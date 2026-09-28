"""Section-aware Markdown I/O for vault artifacts.

Ported from Agoyu ``analysis/ba/vaultlib.py`` but rebuilt around *splicing* instead of
re-rendering, so an unchanged document round-trips byte-identically and an edit touches only
the lines it means to.

Rules this module enforces for every caller:
  * A heading is a heading only at column 0, outside ``<!-- -->`` and fenced code
    (the Agoyu truncation incident: a regex matched ``## Discussion`` inside a comment).
  * Frontmatter keeps key order, inline ``[a, b]`` vs block ``- a`` list style, quoting,
    and every line it was not asked to change.
  * ``Vault.write`` = verify → backup → atomic write → re-read verify → restore on failure.
    Verification refuses a write that drops a heading, changes a section nobody touched,
    or changes a frontmatter key nobody set.
"""
import glob
import os
import re
import shutil

from .util import EngineError, now_stamp, today

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FENCE_RE = re.compile(r"^\s*```")
H2_RE = re.compile(r"^##(?!#)\s+(.*?)\s*$")
SEP_CELL = re.compile(r"^\s*:?-{3,}:?\s*$")
Q_RE = re.compile(r"^(\s*)- \[( |x|X)\] Q:\s?(.*)$")


# ---------------------------------------------------------------------------- masking

def mask_lines(lines):
    """Return a parallel list where text inside HTML comments / fenced code is blanked.

    Line count and per-line length are preserved, so indices map 1:1 onto the source.
    An unterminated comment masks to the end of the document (fail closed)."""
    out = []
    in_comment = False
    in_fence = False
    for line in lines:
        if in_fence:
            out.append(" " * len(line))
            if FENCE_RE.match(line):
                in_fence = False
            continue
        if not in_comment and FENCE_RE.match(line):
            in_fence = True
            out.append(" " * len(line))
            continue
        buf = []
        i = 0
        n = len(line)
        while i < n:
            if in_comment:
                j = line.find("-->", i)
                if j < 0:
                    buf.append(" " * (n - i))
                    i = n
                else:
                    buf.append(" " * (j + 3 - i))
                    i = j + 3
                    in_comment = False
            else:
                j = line.find("<!--", i)
                if j < 0:
                    buf.append(line[i:])
                    i = n
                else:
                    buf.append(line[i:j])
                    i = j
                    in_comment = True
        out.append("".join(buf))
    return out


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text or "", flags=re.S)


# ---------------------------------------------------------------------------- tables

def split_cells(line):
    """Split a Markdown table row on unescaped pipes. Returns raw cell strings (untrimmed),
    without the leading/trailing empty edges."""
    s = line.rstrip("\n")
    parts = []
    buf = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            buf.append("\\|")
            i += 2
            continue
        if c == "|":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
        i += 1
    parts.append("".join(buf))
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return parts


def cell_value(raw):
    return raw.strip().replace("\\|", "|")


def escape_cell(value):
    v = str(value if value is not None else "").replace("\r", "")
    v = re.sub(r"\s*\n\s*", " ", v).strip()
    return re.sub(r"(?<!\\)\|", r"\\|", v)


def render_row(values):
    return "| " + " | ".join(escape_cell(v) for v in values) + " |"


def is_row(line):
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and len(s) > 1


def is_loose_row(line):
    """A data row missing its closing pipe (a known hand-edit defect) still belongs to the table."""
    s = line.strip()
    return s.startswith("|") and s.count("|") >= 3


def is_sep(line):
    cells = split_cells(line)
    return bool(cells) and all(SEP_CELL.match(c) for c in cells)


class Table:
    """A Markdown table located inside a Doc by absolute line indices."""

    def __init__(self, doc, header_idx, sep_idx, row_idxs, end):
        self.doc = doc
        self.header_idx = header_idx
        self.sep_idx = sep_idx
        self.row_idxs = row_idxs
        self.end = end  # one past the last table line (row or header/sep)

    @property
    def header(self):
        return [cell_value(c) for c in split_cells(self.doc.lines[self.header_idx])]

    def rows(self):
        return [[cell_value(c) for c in split_cells(self.doc.lines[i])] for i in self.row_idxs]

    def raw_rows(self):
        return [(i, split_cells(self.doc.lines[i])) for i in self.row_idxs]

    def col(self, name):
        """Index of the first header column whose name contains ``name`` (case-insensitive)."""
        for k, h in enumerate(self.header):
            if name.lower() == h.lower():
                return k
        for k, h in enumerate(self.header):
            if name.lower() in h.lower():
                return k
        return None


def find_tables(doc, start, end, tolerate_split=False):
    """Every table between line ``start`` and ``end`` (exclusive), outside comments/fences.

    ``tolerate_split`` treats blank lines between two data rows as part of one table — the
    known Signal Log defect (Agoyu fix_split_tables) where a blank line cut the table in two."""
    m = doc.masked
    L = doc.lines
    out = []
    i = start
    while i < end:
        if is_row(m[i]) and i + 1 < end and is_row(m[i + 1]) and is_sep(L[i + 1]):
            h, sp = i, i + 1
            rows = []
            j = i + 2
            while j < end:
                if is_row(m[j]) or is_loose_row(m[j]):
                    rows.append(j)
                    j += 1
                    continue
                if tolerate_split and not m[j].strip():
                    k = j
                    while k < end and not m[k].strip():
                        k += 1
                    if k < end and is_row(m[k]) and not (k + 1 < end and is_sep(L[k + 1])) \
                            and re.match(r"^\|\s*\d+[a-z]?\s*\|", m[k]):
                        j = k
                        continue
                break
            out.append(Table(doc, h, sp, rows, j))
            i = j
            continue
        i += 1
    return out


# ---------------------------------------------------------------------------- frontmatter

_NEEDS_QUOTE = re.compile(r"(^[\[\]{}>|*&!%@`'\"#,?-]|: | #|^\s|\s$|^$)")


class Frontmatter:
    """Line-preserving YAML-ish frontmatter (the subset vault artifacts use)."""

    def __init__(self, lines):
        self.lines = list(lines)
        self._index()

    def _index(self):
        self.entries = {}
        self.order = []
        i = 0
        L = self.lines
        while i < len(L):
            m = re.match(r"^([A-Za-z0-9_][A-Za-z0-9_\-]*)\s*:(.*)$", L[i])
            if not m:
                i += 1
                continue
            key = m.group(1)
            j = i + 1
            while j < len(L) and L[j].strip() and (L[j][:1] in (" ", "\t") or re.match(r"^-\s", L[j])):
                j += 1
            if key not in self.entries:
                self.entries[key] = (i, j)
                self.order.append(key)
            i = j

    def keys(self):
        return list(self.order)

    def __contains__(self, key):
        return key in self.entries

    def raw(self, key):
        if key not in self.entries:
            return None
        a, b = self.entries[key]
        return "\n".join(self.lines[a:b])

    @staticmethod
    def _strip_comment(v):
        v = v.strip()
        if v.startswith(('"', "'")):
            q = v[0]
            end = v.find(q, 1)
            while end > 0 and v[end - 1] == "\\":
                end = v.find(q, end + 1)
            return v[: end + 1] if end > 0 else v
        m = re.search(r"\s+#", v)
        return v[: m.start()].strip() if m else v

    @staticmethod
    def _unquote(v):
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            inner = v[1:-1]
            return _yaml_unescape(inner) if v[0] == '"' else inner.replace("''", "'")
        return v

    def get(self, key, default=None):
        if key not in self.entries:
            return default
        a, b = self.entries[key]
        first = self.lines[a].split(":", 1)[1]
        v = self._strip_comment(first)
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            return [self._unquote(x) for x in _split_inline_list(inner)] if inner else []
        if v == "" and b > a + 1:
            items = []
            for line in self.lines[a + 1:b]:
                mm = re.match(r"^\s*-\s+(.*)$", line)
                if mm:
                    items.append(self._unquote(self._strip_comment(mm.group(1))))
            return items
        return self._unquote(v)

    def get_list(self, key):
        v = self.get(key)
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return v
        return [v]

    def style(self, key):
        """'block' | 'inline' | 'scalar' | 'quoted' | None"""
        if key not in self.entries:
            return None
        a, b = self.entries[key]
        v = self._strip_comment(self.lines[a].split(":", 1)[1])
        if v.startswith("["):
            return "inline"
        if v == "" and any(re.match(r"^\s*-\s", x) for x in self.lines[a + 1:b]):
            return "block"
        if v.startswith('"'):
            return "quoted"
        return "scalar"

    def set(self, key, value, after=None):
        """Set ``key``; keeps the list style and quoting the key already had."""
        style = self.style(key)
        if isinstance(value, bool):
            rendered = [f"{key}: {'true' if value else 'false'}"]
        elif isinstance(value, (list, tuple)):
            vals = [str(x) for x in value]
            if style == "block" and vals:
                a, _ = self.entries[key]
                indent = "  "
                for line in self.lines[a + 1:]:
                    mm = re.match(r"^(\s*)-\s", line)
                    if mm:
                        indent = mm.group(1)
                        break
                rendered = [f"{key}:"] + [f"{indent}- {_q(v)}" for v in vals]
            else:
                rendered = [f"{key}: [" + ", ".join(_q_inline(v) for v in vals) + "]"]
        else:
            s = "" if value is None else str(value)
            if style == "quoted" or (s and _NEEDS_QUOTE.search(s)):
                rendered = [f'{key}: "' + _yaml_escape(s) + '"']
            else:
                rendered = [f"{key}: {s}".rstrip()]
        if key in self.entries:
            a, b = self.entries[key]
            if self.lines[a:b] == rendered:
                return False
            self.lines[a:b] = rendered
        else:
            pos = len(self.lines)
            if after and after in self.entries:
                pos = self.entries[after][1]
            self.lines[pos:pos] = rendered
        self._index()
        return True


def _split_inline_list(inner):
    out, buf, q = [], [], None
    for c in inner:
        if q:
            buf.append(c)
            if c == q:
                q = None
            continue
        if c in "\"'":
            q = c
            buf.append(c)
        elif c == ",":
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return [x for x in out if x]


def _yaml_escape(v):
    return v.replace("\\", "\\\\").replace('"', '\\"')


def _yaml_unescape(v):
    """Undo YAML double-quoted escapes for backslash, quote and slash; any other escape is kept verbatim."""
    return re.sub(r'\\(["\\/])', lambda m: m.group(1), v)


def _q(v):
    return '"' + _yaml_escape(v) + '"' if _NEEDS_QUOTE.search(v) and not re.match(r"^[\w./@-]+$", v) else v


def _q_inline(v):
    return '"' + _yaml_escape(v) + '"' if re.search(r"[,\[\]]|^\s|\s$|: ", v) else v


# ---------------------------------------------------------------------------- document

class Section:
    __slots__ = ("title", "occ", "h", "start", "end")

    def __init__(self, title, occ, h, start, end):
        self.title, self.occ, self.h, self.start, self.end = title, occ, h, start, end

    @property
    def key(self):
        return (self.title, self.occ)


class Doc:
    """A vault Markdown file held as lines. Every edit is a splice; ``text`` re-joins them."""

    def __init__(self, text, path=None):
        self.path = path
        self.original_text = text
        self.trailing_nl = text.endswith("\n")
        self.lines = text.split("\n")
        if self.trailing_nl:
            self.lines = self.lines[:-1]
        self.touched = set()      # section keys edited
        self.fm_touched = set()   # frontmatter keys set
        self.allow_heading_change = False
        self._reparse()
        self._orig_sections = self._section_map(self)
        self._orig_titles = [s.key for s in self.sections]
        self._orig_fm = {k: self.fm.raw(k) for k in self.fm.keys()} if self.fm else {}

    @staticmethod
    def _section_map(d):
        m = {s.key: d.lines[s.start:s.end] for s in d.sections}
        first = d.sections[0].h if d.sections else len(d.lines)
        m[("__intro__", 0)] = d.lines[d.body_start:first]
        return m

    # -- parsing
    def _reparse(self):
        self.fm = None
        self.fm_range = None
        body_start = 0
        if self.lines and self.lines[0].strip() == "---":
            for i in range(1, len(self.lines)):
                if self.lines[i].strip() == "---":
                    self.fm = Frontmatter(self.lines[1:i])
                    self.fm_range = (1, i)
                    body_start = i + 1
                    break
        self.body_start = body_start
        self.masked = [" " * len(x) for x in self.lines[:body_start]] + mask_lines(self.lines[body_start:])
        secs = []
        seen = {}
        for i in range(body_start, len(self.lines)):
            m = H2_RE.match(self.masked[i])
            if m and self.lines[i].startswith("##"):
                t = m.group(1).strip()
                seen[t] = seen.get(t, 0) + 1
                secs.append([t, seen[t] - 1, i])
        self.sections = []
        for k, (t, occ, h) in enumerate(secs):
            end = secs[k + 1][2] if k + 1 < len(secs) else len(self.lines)
            self.sections.append(Section(t, occ, h, h + 1, end))

    @property
    def text(self):
        return "\n".join(self.lines) + ("\n" if self.trailing_nl else "")

    @property
    def changed(self):
        return self.text != self.original_text

    # -- sections
    def section(self, key):
        """Find a level-2 section. ``key``: '2' / '2.' → the section titled '2. …';
        otherwise an exact (case-insensitive) title, else a title prefix."""
        k = str(key).strip()
        if k.startswith("## "):
            k = k[3:].strip()
        if re.fullmatch(r"\d+\.?", k):
            n = k.rstrip(".")
            for s in self.sections:
                if re.match(rf"^{n}\.(\s|$)", s.title):
                    return s
            return None
        for s in self.sections:
            if s.title.lower() == k.lower():
                return s
        for s in self.sections:
            if s.title.lower().startswith(k.lower()):
                return s
        return None

    def has(self, key):
        return self.section(key) is not None

    def get(self, key):
        s = self.section(key)
        return None if s is None else "\n".join(self.lines[s.start:s.end])

    def section_masked(self, key):
        s = self.section(key)
        return None if s is None else "\n".join(self.masked[s.start:s.end])

    def _mark(self, start, end):
        # a pure insertion belongs to the section holding the line before it
        lo, hi = (start, end) if end > start else (start - 1, start)
        first = self.sections[0].h if self.sections else len(self.lines)
        if lo < first and hi > self.body_start:
            self.touched.add(("__intro__", 0))
        for s in self.sections:
            if lo < s.end and hi > s.h:
                self.touched.add(s.key)

    def splice(self, start, end, new_lines):
        if self.lines[start:end] == list(new_lines):
            return False
        self._mark(start, end)
        self.lines[start:end] = list(new_lines)
        self._reparse()
        return True

    def replace_body(self, key, new_body_lines):
        s = self.section(key)
        if s is None:
            raise EngineError(f"{self.name}: no section '{key}'")
        body = list(new_body_lines)
        # keep one blank line before the next heading, as the vault writes it
        if s.end < len(self.lines) and (not body or body[-1].strip()):
            body.append("")
        return self.splice(s.start, s.end, body)

    def insert_section(self, title, body_lines, before=None, after=None):
        """Insert ``## title`` before/after another section (default: before Changelog, else end)."""
        pos = len(self.lines)
        ref = None
        if before:
            ref = self.section(before)
            if ref:
                pos = ref.h
        elif after:
            ref = self.section(after)
            if ref:
                pos = ref.end
        else:
            ref = self.section("Changelog")
            if ref:
                pos = ref.h
        block = [f"## {title}"] + list(body_lines)
        if block[-1].strip():
            block.append("")
        if pos > 0 and self.lines[pos - 1].strip():
            block.insert(0, "")
        self.allow_heading_change = True
        self.lines[pos:pos] = block
        self._reparse()
        self.touched.add((title, 0))
        return True

    def tables(self, key, tolerate_split=False):
        s = self.section(key)
        if s is None:
            return []
        return find_tables(self, s.start, s.end, tolerate_split)

    def table(self, key, idx=0, tolerate_split=False):
        t = self.tables(key, tolerate_split)
        return t[idx] if len(t) > idx else None

    def set_row(self, line_idx, values):
        return self.splice(line_idx, line_idx + 1, [render_row(values)])

    def replace_table_rows(self, table, rows_lines):
        return self.splice(table.sep_idx + 1, table.end, list(rows_lines))

    # -- frontmatter
    def fm_get(self, key, default=None):
        return self.fm.get(key, default) if self.fm else default

    def fm_list(self, key):
        return self.fm.get_list(key) if self.fm else []

    def fm_set(self, key, value, after=None):
        if not self.fm:
            raise EngineError(f"{self.name}: no frontmatter")
        before = list(self.fm.lines)
        if not self.fm.set(key, value, after=after):
            return False
        a, b = self.fm_range
        self.lines[a:b] = self.fm.lines
        self.fm_touched.add(key)
        self._reparse()
        return before != self.fm.lines

    @property
    def name(self):
        return os.path.basename(self.path) if self.path else "<doc>"

    @property
    def id(self):
        v = self.fm_get("id")
        if v:
            return v
        m = re.match(r"^((?:UC|BR|INT|EN|UX|PRD)-\d+)", self.name)
        return m.group(1) if m else None

    # -- verification
    def verify(self):
        """Raise EngineError when the pending text drifts outside what was edited."""
        new = Doc(self.text, self.path)
        if self._orig_fm and new.fm is None:
            raise EngineError(f"{self.name}: frontmatter lost")
        for k, raw in self._orig_fm.items():
            if k in self.fm_touched:
                continue
            if new.fm.raw(k) != raw:
                raise EngineError(f"{self.name}: frontmatter key '{k}' changed without being set")
        new_keys = [s.key for s in new.sections]
        if not self.allow_heading_change:
            missing = [k for k in self._orig_titles if k not in new_keys]
            if missing:
                raise EngineError(f"{self.name}: heading(s) lost: {', '.join(t for t, _ in missing)}")
            order = [k for k in new_keys if k in self._orig_titles]
            if order != self._orig_titles:
                raise EngineError(f"{self.name}: heading order changed")
        new_by_key = self._section_map(new)
        for k, lines in self._orig_sections.items():
            if k in self.touched:
                continue
            got = new_by_key.get(k)
            if got is None and self.allow_heading_change:
                continue
            if _strip_trailing_blank(got or []) != _strip_trailing_blank(lines):
                raise EngineError(f"{self.name}: section '{k[0]}' changed without being edited")

        # Guard Changelog heading and history lines
        orig_cl_lines = None
        for (t, occ), lines in self._orig_sections.items():
            if t.lower() == "changelog":
                orig_cl_lines = lines
                break
        if orig_cl_lines is not None:
            new_cl = new.section("Changelog")
            if new_cl is None:
                raise EngineError(f"{self.name}: ## Changelog heading lost")
            def _cl_lines(lines):
                entries = []
                in_comment = False
                for line in lines:
                    s = line.strip()
                    if "<!--" in s:
                        in_comment = True
                    if in_comment:
                        if "-->" in s:
                            in_comment = False
                        continue
                    if s.startswith("- ") or s.startswith("* "):
                        entries.append(s)
                return entries
            orig_entries = _cl_lines(orig_cl_lines)
            new_entries = set(_cl_lines(new.lines[new_cl.start:new_cl.end]))
            for e in orig_entries:
                if e not in new_entries:
                    raise EngineError(f"{self.name}: ## Changelog history line lost: {e}")

        # Guard Open Questions / Gates questions
        orig_gates_lines = None
        for (t, occ), lines in self._orig_sections.items():
            if t.lower() == "open questions / gates":
                orig_gates_lines = lines
                break
        if orig_gates_lines is not None:
            new_gates = new.section("Open Questions / Gates")
            if new_gates is None:
                raise EngineError(f"{self.name}: ## Open Questions / Gates heading lost")
            from .edit import q_core
            orig_doc = Doc(self.original_text, self.path)
            s_orig = orig_doc.section("Open Questions / Gates")
            orig_qs = questions_in(orig_doc, s_orig.start, s_orig.end) if s_orig else []
            new_qs = questions_in(new, new_gates.start, new_gates.end)
            new_cores = {q_core(q.text) for q in new_qs}
            for q in orig_qs:
                qc = q_core(q.text)
                if qc and qc not in new_cores:
                    raise EngineError(f"{self.name}: refused — question in ## Open Questions / Gates disappeared: {q.text}")

        return True


def _strip_trailing_blank(lines):
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    return out


# ---------------------------------------------------------------------------- questions

class Question:
    __slots__ = ("start", "end", "checked", "text", "answer", "indent")

    def __init__(self, start, end, checked, text, answer, indent):
        self.start, self.end, self.checked, self.text, self.answer, self.indent = \
            start, end, checked, text, answer, indent

    @property
    def answered(self):
        return bool(self.answer and self.answer.strip())


def questions_in(doc, start, end):
    """Every ``- [ ] Q:`` / ``- [x] Q:`` item in [start, end), outside comments.
    A question spans its own line plus following indented lines (its ``A:`` and continuations)."""
    out = []
    i = start
    while i < end:
        m = Q_RE.match(doc.masked[i])
        if not m:
            i += 1
            continue
        indent = len(m.group(1))
        j = i + 1
        answer_lines = []
        in_answer = False
        while j < end:
            line = doc.lines[j]
            ml = doc.masked[j]
            if not ml.strip():
                # blank line ends the item unless the next non-blank is still indented continuation of A:
                k = j + 1
                while k < end and not doc.masked[k].strip():
                    k += 1
                if in_answer and k < end and re.match(rf"^\s{{{indent + 2},}}\S", doc.masked[k]) \
                        and not Q_RE.match(doc.masked[k]) and not re.match(r"^\s*A:", doc.masked[k]):
                    j = k
                    continue
                break
            if Q_RE.match(ml) or not re.match(rf"^\s{{{indent + 1},}}\S", line):
                break
            am = re.match(r"^\s*A:\s?(.*)$", line)
            if am and not in_answer:
                in_answer = True
                answer_lines.append(am.group(1))
            elif in_answer:
                answer_lines.append(line.strip())
            j += 1
        out.append(Question(i, j, m.group(2).lower() == "x", m.group(3).strip(),
                            " ".join(x for x in answer_lines if x).strip(), indent))
        i = j
    return out


# ---------------------------------------------------------------------------- vault

class Vault:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.req = os.path.join(self.root, "01-Requirements")
        self.inbox = os.path.join(self.root, "00-Inbox")
        self.uc_dir = os.path.join(self.req, "_ucs")
        self.br_dir = os.path.join(self.req, "_brs")
        self.hub_dir = os.path.join(self.req, "_features")
        self.entity_dir = os.path.join(self.req, "_entities")
        self.ledger_dir = os.path.join(self.req, "_ledger")
        self.runs_dir = os.path.join(self.root, "_runs")
        self.features_file = os.path.join(self.req, "FEATURES.md")
        self._cache = {}
        self._project = None
        self.writes = []
        self.dry = False

    @classmethod
    def discover(cls, start=None):
        env = os.environ.get("BIGIN_VAULT")
        if env:
            return cls(env)
        d = os.path.abspath(start or os.getcwd())
        while True:
            if os.path.exists(os.path.join(d, "_bigin", "system", "project.md")) or \
                    os.path.isdir(os.path.join(d, "01-Requirements")):
                return cls(d)
            parent = os.path.dirname(d)
            if parent == d:
                raise EngineError("no Bigin vault found (no _bigin/system/project.md or 01-Requirements/ "
                                  "above the working directory) — pass --vault <root>")
            d = parent

    # -- config
    def project(self):
        if self._project is None:
            p = os.path.join(self.root, "_bigin", "system", "project.md")
            self._project = self.load(p) if os.path.exists(p) else Doc("", p)
        return self._project

    def config(self, key, default=None):
        v = self.project().fm_get(key)
        return default if v in (None, "", "<unset>", "<unknown>") else v

    def template_path(self, name):
        for base in (os.path.join(self.root, "_bigin", "templates"), os.path.join(PLUGIN_ROOT, "workspace", "templates")):
            p = os.path.join(base, name)
            if os.path.exists(p):
                return p
        raise EngineError(f"template {name} not found in _bigin/templates or the plugin")

    def rel(self, path):
        return os.path.relpath(path, self.root)

    # -- listing
    def uc_paths(self):
        return sorted(glob.glob(os.path.join(self.uc_dir, "UC-*.md")))

    def br_paths(self):
        return sorted(glob.glob(os.path.join(self.br_dir, "BR-*.md")))

    def hub_paths(self):
        return sorted(p for p in glob.glob(os.path.join(self.hub_dir, "*.md")) if not p.endswith(".signals.md"))

    def note_paths(self):
        return sorted(glob.glob(os.path.join(self.inbox, "INT-*.md")))

    def slugs(self):
        return [os.path.basename(p)[:-3] for p in self.hub_paths()]

    def hub_path(self, slug):
        return os.path.join(self.hub_dir, f"{slug}.md")

    def signals_path(self, slug):
        return os.path.join(self.hub_dir, f"{slug}.signals.md")

    def find(self, ident):
        """Path of the artifact with this id, or None."""
        ident = ident.strip()
        kind = ident.split("-")[0]
        d = {"UC": self.uc_dir, "BR": self.br_dir, "INT": self.inbox, "EN": self.entity_dir}.get(kind)
        if not d:
            return None
        for p in glob.glob(os.path.join(d, f"{ident} *.md")) + glob.glob(os.path.join(d, f"{ident}.md")):
            return p
        return None

    def ids(self, kind):
        paths = self.uc_paths() if kind == "UC" else self.br_paths()
        out = set()
        for p in paths:
            m = re.match(rf"^({kind}-\d+)", os.path.basename(p))
            if m:
                out.add(m.group(1))
        return out

    # -- loading / writing
    def load(self, path):
        path = os.path.abspath(path)
        d = self._cache.get(path)
        if d is not None:
            return d
        with open(path, "r", encoding="utf-8") as f:
            d = Doc(f.read(), path)
        self._cache[path] = d
        return d

    def load_id(self, ident):
        p = self.find(ident)
        if not p:
            raise EngineError(f"{ident}: no such file")
        return self.load(p)

    def forget(self, path=None):
        if path is None:
            self._cache.clear()
        else:
            self._cache.pop(os.path.abspath(path), None)

    def backup_dir(self):
        return os.path.join(self.runs_dir, "_backups", today())

    def write(self, doc, new_file=False):
        """Verify, back up, atomically write, and re-read ``doc``. Returns True if written."""
        if not new_file and not doc.changed:
            return False
        if not new_file:
            doc.verify()
        text = doc.text
        if self.dry:
            self.writes.append(doc.path)
            return True
        path = doc.path
        bak = None
        with self.write_lock():
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    on_disk = f.read()
                if new_file:
                    raise EngineError(f"{self.rel(path)} already exists")
                if on_disk != doc.original_text:
                    # someone (a person, another process) wrote it after we read it: never clobber
                    self.forget(path)
                    raise EngineError(f"{self.rel(path)} changed on disk since it was read — re-run the command")
                bdir = self.backup_dir()
                bak = os.path.join(bdir, self.rel(path) + "@" + now_stamp())
                os.makedirs(os.path.dirname(bak), exist_ok=True)
                shutil.copy2(path, bak)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = f"{path}.{os.getpid()}.bigin-tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)
            with open(path, "r", encoding="utf-8") as f:
                back = f.read()
            if back != text:
                if bak:
                    shutil.copy2(bak, path)
                raise EngineError(f"{self.rel(path)}: post-write verification failed — restored from backup")
        self.writes.append(path)
        fresh = Doc(text, path)
        self._cache[os.path.abspath(path)] = fresh
        return True

    def write_lock(self):
        """Exclusive lock held only around check-then-replace of one file."""
        import contextlib

        @contextlib.contextmanager
        def _lock():
            try:
                import fcntl
            except ImportError:  # pragma: no cover
                yield
                return
            os.makedirs(self.req, exist_ok=True)
            with open(os.path.join(self.req, ".write.lock"), "a+") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return _lock()

    def create(self, path, text):
        if os.path.exists(path):
            raise EngineError(f"{self.rel(path)} already exists")
        return self.write(Doc(text, path), new_file=True)
