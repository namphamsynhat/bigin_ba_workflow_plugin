"""Read-side model of vault artifacts: UC steps/flows/§ 4/questions, BR statement, hub Signal Log,
intake note signal table. Every function takes a ``Doc`` and never writes."""
import os
import re

from .util import sort_ids
from .vault import H2_RE, cell_value, find_tables, questions_in, split_cells

STEP_CELL = re.compile(r"^\**\s*(S\d+)\s*\**$")
FLOW_H = re.compile(r"^###\s+\**([AE]\d+)\**\s*:\s*(.*)$")
INT_CITE = re.compile(r"(INT-\d+)((?:\s*,?\s*#\d+[a-z]?(?:\s*[-–…]\s*#?\d+)?)+)")
HUB_ROW_CITE = re.compile(r"([a-z0-9][a-z0-9-]*)\s+hub\s+rows?\s*((?:#?\d+[a-z]?(?:\s*[-–]\s*#?\d+)?[\s,]*(?:and\s+)?)+)")
STAGED_ENTRY = re.compile(r"^- \*\*INT-\d+", re.M)

PROCESSED = {"applied", "superseded", "rejected"}
PARKED = {"question", "conflict", "held"}
SIGNAL_STATUSES = {"new", "held", "staged", "applied", "question", "conflict", "superseded", "rejected"}
DROP_MARK = re.compile(r"^\s*(Dropped|Removed)\b", re.I)


def kind_of(ident):
    return (ident or "").split("-")[0]


# ---------------------------------------------------------------------------- UC

def uc_still_open_range(doc):
    """(start, end) line range of § 5's **Still open** list."""
    s = doc.section("5")
    if s is None:
        return None
    start, end = s.start, s.end
    for i in range(s.start, s.end):
        if "**Still open**" in doc.masked[i]:
            start = i + 1
        if "**Decision log**" in doc.masked[i]:
            end = i
            break
    return start, end


def uc_questions(doc):
    r = uc_still_open_range(doc)
    return questions_in(doc, *r) if r else []


def br_questions(doc):
    s = doc.section("Open Questions")
    return questions_in(doc, s.start, s.end) if s else []


def artifact_questions(doc):
    return uc_questions(doc) if kind_of(doc.id) == "UC" else br_questions(doc)


def open_questions(doc):
    return [q for q in artifact_questions(doc) if not q.checked]


def decision_table(doc):
    s = doc.section("5")
    if not s:
        return None
    ts = find_tables(doc, s.start, s.end)
    return ts[-1] if ts else None


class Step:
    __slots__ = ("id", "idx", "actor", "system", "dropped")

    def __init__(self, id, idx, actor, system):
        self.id, self.idx, self.actor, self.system = id, idx, actor, system
        self.dropped = bool(DROP_MARK.match(actor or "") or DROP_MARK.match(system or ""))

    @property
    def text(self):
        return f"{self.actor} || {self.system}"


def steps_table(doc):
    s = doc.section("2")
    if not s:
        return None
    for t in find_tables(doc, s.start, s.end):
        if t.header and t.header[0].lower().startswith("step"):
            return t
    return None


def steps(doc):
    t = steps_table(doc)
    if not t:
        return []
    out = []
    for i in t.row_idxs:
        c = [cell_value(x) for x in split_cells(doc.lines[i])]
        m = STEP_CELL.match(c[0]) if c else None
        if m:
            out.append(Step(m.group(1), i, c[1] if len(c) > 1 else "", c[2] if len(c) > 2 else ""))
    return out


def is_placeholder(doc):
    st = steps(doc)
    return len(st) == 1 and st[0].id == "S1" and not st[0].actor.strip() and not st[0].system.strip()


class Flow:
    __slots__ = ("id", "name", "h", "end", "body")

    def __init__(self, id, name, h, end, body):
        self.id, self.name, self.h, self.end, self.body = id, name, h, end, body

    @property
    def kind(self):
        return self.id[0]

    @property
    def dropped(self):
        return bool(re.search(r"\bDropped\b", self.name) or DROP_MARK.match(self.body.strip() or ""))

    @property
    def text(self):
        return f"{self.name}\n{self.body}".strip()


def flows(doc):
    s = doc.section("3")
    if not s:
        return []
    heads = []
    for i in range(s.start, s.end):
        m = FLOW_H.match(doc.masked[i])
        if m and doc.lines[i].startswith("###"):
            heads.append((i, m.group(1), m.group(2).strip()))
    out = []
    for k, (i, fid, name) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else s.end
        body_lines = doc.lines[i + 1:end]
        while body_lines and not body_lines[-1].strip():
            body_lines = body_lines[:-1]
        out.append(Flow(fid, name.strip("` "), i, end, "\n".join(body_lines)))
    return out


def live_refs(doc):
    """Step and flow ids that exist and are not dropped."""
    return {x.id for x in steps(doc) if not x.dropped} | {f.id for f in flows(doc) if not f.dropped}


def all_refs(doc):
    return {x.id for x in steps(doc)} | {f.id for f in flows(doc)}


def next_id(existing, prefix):
    n = max([int(x[1:]) for x in existing if x.startswith(prefix) and x[1:].isdigit()] or [0])
    return f"{prefix}{n + 1}"


def s4_table(doc):
    s = doc.section("4")
    if not s:
        return None
    ts = find_tables(doc, s.start, s.end)
    return ts[0] if ts else None


def s4_rows(doc):
    t = s4_table(doc)
    if not t:
        return []
    out = []
    for i in t.row_idxs:
        c = [cell_value(x) for x in split_cells(doc.lines[i])]
        if c and re.match(r"^BR-\d+$", c[0]):
            out.append((i, c))
    return out


def s4_brs(doc):
    return sort_ids(c[0] for _, c in s4_rows(doc))


ENFORCE_WORDS = re.compile(r"\b(pre-?condition|post-?condition|trigger|throughout|all steps|every step)\b", re.I)


def enforcement_refs(cell):
    """Step/flow ids an 'Enforced at' cell cites, expanding 'S1-S4' ranges."""
    refs = set()
    for a, b in re.findall(r"\b([SAE]\d+)\s*[-–]\s*([SAE]?\d+)\b", cell):
        p = a[0]
        lo, hi = int(a[1:]), int(b.lstrip("SAE"))
        if hi >= lo and hi - lo < 60:
            refs |= {f"{p}{n}" for n in range(lo, hi + 1)}
    refs |= set(re.findall(r"\b([SAE]\d+)\b", cell))
    return refs


def discussion_text(doc):
    s = doc.section("Discussion")
    return "" if not s else "\n".join(doc.masked[s.start:s.end])


def has_staged(doc):
    return bool(STAGED_ENTRY.search(discussion_text(doc)))


# ---------------------------------------------------------------------------- BR

def br_statement_range(doc):
    """(start, end) of the rule statement: the first paragraph after the H1, before any ## heading."""
    first_h2 = doc.sections[0].h if doc.sections else len(doc.lines)
    i = doc.body_start
    while i < first_h2 and not doc.lines[i].startswith("# "):
        i += 1
    i += 1
    while i < first_h2 and not doc.masked[i].strip():
        i += 1
    j = i
    while j < first_h2 and doc.masked[j].strip():
        j += 1
    return (i, j) if j > i else None


def br_statement(doc):
    r = br_statement_range(doc)
    return "" if not r else re.sub(r"^[-*]\s+", "", " ".join(x.strip() for x in doc.lines[r[0]:r[1]]).strip())


PLACEHOLDER_STMT = re.compile(r"^`?<|pending the review gate|staged in ## Discussion|^_?rule statement pending|^`?not stated`?$", re.I)


def is_placeholder_statement(stmt):
    return bool(PLACEHOLDER_STMT.search((stmt or "").strip()))


def title_of(doc):
    t = doc.fm_get("title") or ""
    if t:
        return t
    m = re.match(r"^[A-Z]+-\d+\s+(.*)\.md$", doc.name)
    return m.group(1) if m else doc.name


# ---------------------------------------------------------------------------- hub Signal Log

class SignalRow:
    __slots__ = ("num", "idx", "cells", "header")

    def __init__(self, num, idx, cells, header):
        self.num, self.idx, self.cells, self.header = num, idx, cells, header

    def get(self, name):
        for k, h in enumerate(self.header):
            if h.lower() == name.lower():
                return self.cells[k] if k < len(self.cells) else ""
        return ""

    @property
    def status(self):
        return self.get("Status").strip()

    @property
    def destination(self):
        return self.get("Destination")

    @property
    def source(self):
        return self.get("Source")


def signal_doc(vault, slug):
    """The Doc holding ``slug``'s Signal Log: ``<slug>.signals.md`` once split, else the hub."""
    sp = vault.signals_path(slug)
    if os.path.exists(sp):
        return vault.load(sp)
    hp = vault.hub_path(slug)
    return vault.load(hp) if os.path.exists(hp) else None


def signal_table(doc):
    return doc.table("Signal Log", tolerate_split=True) if doc else None


def signal_rows(doc):
    t = signal_table(doc)
    if not t:
        return []
    hdr = t.header
    out = []
    for i in t.row_idxs:
        c = [cell_value(x) for x in split_cells(doc.lines[i])]
        if c and re.match(r"^\d+[a-z]?$", c[0]):
            out.append(SignalRow(c[0], i, c, hdr))
    return out


def expand_int_cites(text):
    """{(INT-###, n)} for every 'INT-014 #3, #5-#7' citation in ``text``."""
    out = set()
    for nid, nums in INT_CITE.findall(text or ""):
        for a, b in re.findall(r"#(\d+)[a-z]?(?:\s*[-–…]\s*#?(\d+))?", nums):
            lo, hi = int(a), int(b or a)
            if hi - lo > 2000:
                hi = lo
            for n in range(lo, hi + 1):
                out.add((nid, n))
    return out


def hub_row_cites(text):
    """{(slug, row)} for every 'mover-rates hub rows #17, #18' citation in ``text``."""
    out = set()
    for slug, nums in HUB_ROW_CITE.findall(text or ""):
        for a, b in re.findall(r"#?(\d+)[a-z]?(?:\s*[-–]\s*#?(\d+))?", nums):
            lo, hi = int(a), int(b or a)
            for n in range(lo, min(hi, lo + 500) + 1):
                out.add((slug, str(n)))
    return out


# ---------------------------------------------------------------------------- intake note

NOTE_COLS = ["#", "Type", "Signal", "Why", "Source", "Feature", "Status", "Notes"]


def note_table(doc):
    return doc.table("Extracted signals", tolerate_split=True)


def note_rows(doc):
    t = note_table(doc)
    if not t:
        return []
    hdr = t.header
    out = []
    for i in t.row_idxs:
        c = [cell_value(x) for x in split_cells(doc.lines[i])]
        if c and re.match(r"^\d+$", c[0]):
            out.append(SignalRow(c[0], i, c, hdr))
    return out


def h2_titles(text):
    return [m.group(1) for m in (H2_RE.match(x) for x in text.split("\n")) if m]
