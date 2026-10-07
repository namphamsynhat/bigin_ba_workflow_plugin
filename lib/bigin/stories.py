"""Epics and user stories (03-Epics-Stories/) — the shared parsing behind lint, coverage, and mint.

Layout (paths.md): ``03-Epics-Stories/EP-<NNN> <Feature>/EP-<NNN> <Feature>.md`` with its stories
``US-<NNN> <Title>.md`` beside it and frozen prototype captures under ``_snapshot/<YYYY-MM-DD>-v<N>/``.
A story is a use-case slice: ``slice_of`` names the UC and the step/flow ids it delivers
(``UC-003 S1–S6``, ``UC-003 A2``), and each acceptance-criteria scenario is tagged with the ids it
proves (``[S3]``, ``[E1]``, ``[BR-004]``). Coverage is "every live S#/A#/E# of every source UC is
sliced or tagged by some story of its epic".

The lint-facing helpers take plain strings — lint.py reads frontmatter without a Vault.
"""
import os
import re

# Hard rule S1: business language only. Acronyms match case-sensitively (so "rest of the form" is
# fine); words match case-insensitively, singular or plural. One list — extend it here, nowhere else.
TECH_ACRONYMS = ["API", "SQL", "JSON", "HTTP", "HTTPS", "REST", "UUID", "GraphQL"]
TECH_WORDS = ["endpoint", "database", "schema", "microservice", "backend", "back-end", "frontend",
              "front-end", "payload", "query string", "foreign key", "primary key", "webhook", "cron"]
TECH_TERMS = TECH_ACRONYMS + TECH_WORDS

_ACRONYM_RX = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, TECH_ACRONYMS)) + r")s?(?![\w-])")
_WORD_RX = re.compile(r"(?<![\w-])(" + "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in TECH_WORDS)
                      + r")s?(?![\w-])", re.I)

MERMAID_KINDS = ("flowchart", "graph", "stateDiagram", "stateDiagram-v2", "sequenceDiagram")
FENCE = re.compile(r"^\s*(```+|~~~+)\s*([\w-]*)")
SNAPSHOT_RX = re.compile(r"^\d{4}-\d{2}-\d{2}-v\d+$")

LIST_KEYS = {"epic": ("source_ucs", "absorbed", "stories", "after"),
             "story": ("rules", "screens", "entities", "after", "absorbed")}

_ID_TOKEN = re.compile(r"^(?:(UC-\d+)\s+)?([SAE]\d+)$")
_RANGE = re.compile(r"^([SAE]\d+)\s*[–-]\s*([SAE]\d+)$")


def kind_of(path):
    """'epic' | 'story' | None for a path under 03-Epics-Stories (never a _snapshot/ capture)."""
    norm = os.path.normpath(path)
    if os.sep + "_snapshot" + os.sep in norm or os.sep + "03-Epics-Stories" + os.sep not in norm:
        return None
    base = os.path.basename(norm)
    return "epic" if base.startswith("EP-") else "story" if base.startswith("US-") else None


# ---------------------------------------------------------------------------- frontmatter

def _split_list(raw):
    raw = (raw or "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [x.strip().strip("'\"") for x in raw.split(",") if x.strip()]


def parse_slices(raw):
    """``slice_of`` → ['UC-003 S1–S6', 'UC-003 A2', …]. A scalar or a list; a comma inside one UC's
    slice ('UC-003 S1-S3, E1') continues that slice rather than starting a new one."""
    if isinstance(raw, list):
        raw = ", ".join(raw)
    out = []
    for item in _split_list(raw):
        if item.startswith("UC-") or not out:
            out.append(item)
        else:
            out[-1] += ", " + item
    return out


def normalize(fm, kind):
    """Raw frontmatter strings → the shape schema/{epic,story}.json validates."""
    d = {}
    for k, v in fm.items():
        if k in LIST_KEYS[kind]:
            d[k] = _split_list(v)
        elif k == "slice_of":
            d[k] = parse_slices(v)
        elif k in ("updated", "owner"):
            continue
        else:
            d[k] = "" if v is None else str(v).strip().strip("'\"")
    return d


def schema_errors(fm, kind):
    from . import jsonschema_lite
    return jsonschema_lite.check(normalize(fm, kind), kind)


# ---------------------------------------------------------------------------- body checks

def _mask(lines):
    """Blank out HTML comments (template guidance is not content)."""
    out, inside = [], False
    for line in lines:
        buf, i = "", 0
        while i < len(line):
            if inside:
                j = line.find("-->", i)
                if j < 0:
                    i = len(line)
                else:
                    i, inside = j + 3, False
            else:
                j = line.find("<!--", i)
                if j < 0:
                    buf += line[i:]
                    i = len(line)
                else:
                    buf += line[i:j]
                    i, inside = j, True
        out.append(buf)
    return out


def _body_lines(text):
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    return start, _mask(lines[start:])


def technical_terms(text):
    """[(line number, term)] for S1 violations: body text and mermaid blocks, never other code fences."""
    start, lines = _body_lines(text)
    hits, fence = [], None
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if m:
            fence = (m.group(2) or "code") if fence is None else None
            continue
        if fence is not None and fence != "mermaid":
            continue
        for rx in (_ACRONYM_RX, _WORD_RX):
            for t in rx.finditer(line):
                hits.append((start + i + 1, t.group(0)))
    return hits


def mermaid_errors(text):
    """[(line number, message)] — every ```mermaid block opens with a known diagram type and closes."""
    start, lines = _body_lines(text)
    errs, fence, opened, first = [], None, 0, None
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if m and fence is None:
            fence, opened, first = (m.group(2) or "code"), i, None
            continue
        if m and fence is not None:
            if fence == "mermaid" and first is None:
                errs.append((start + opened + 1, "empty mermaid block"))
            fence = None
            continue
        if fence == "mermaid" and first is None and line.strip() and not line.strip().startswith("%%"):
            first = line.strip()
            head = first.split()[0]
            if head not in MERMAID_KINDS:
                errs.append((start + i + 1, f"mermaid block starts with `{head}` "
                                            f"(expected one of {', '.join(MERMAID_KINDS)})"))
    if fence is not None:
        errs.append((start + opened + 1, f"unclosed ```{fence} block"))
    return errs


def section(text, number):
    """Lines of the '## <number>.' section (comments masked)."""
    lines = _mask(text.splitlines())
    rx = re.compile(rf"^##\s+{number}\.")
    out, inside = [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = bool(rx.match(line))
            continue
        if inside:
            out.append(line)
    return out


def ac_tags(text):
    """{(uc or None, id)} named by the acceptance-criteria tags in § 6 — ``[S3]``, ``[E1, BR-004]``,
    ``[UC-003 E2]``. Markdown links and anything that isn't an id are ignored."""
    tags = set()
    for line in section(text, 6):
        for inner in re.findall(r"\[([^\]]+)\](?!\()", line):
            uc = None
            for tok in re.split(r"[,;·]", inner):
                tok = tok.strip()
                u = re.match(r"^(UC-\d+)\b\s*(.*)$", tok)
                if u:
                    uc, tok = u.group(1), u.group(2).strip()
                if _ID_TOKEN.match(tok):
                    tags.add((uc, _ID_TOKEN.match(tok).group(2)))
    return tags


# ---------------------------------------------------------------------------- coverage

def expand_slice(item, order):
    """'UC-003 S1–S4, E1' → ('UC-003', {'S1','S2','S3','S4','E1'}). Ranges follow the UC's ROW order
    (step ids are permanent, not sequential), falling back to numbers when an end is unknown."""
    m = re.match(r"^(UC-\d+)\s+(.*)$", item.strip())
    if not m:
        return None, set()
    uc, rest = m.group(1), m.group(2)
    ids = set()
    for tok in re.split(r"\s*,\s*", rest):
        r = _RANGE.match(tok)
        if r:
            a, b = r.group(1), r.group(2)
            if a in order and b in order and order.index(a) <= order.index(b):
                ids.update(order[order.index(a):order.index(b) + 1])
            elif a[0] == b[0]:
                ids.update(f"{a[0]}{n}" for n in range(int(a[1:]), int(b[1:]) + 1))
        elif re.match(r"^[SAE]\d+$", tok):
            ids.add(tok)
    return uc, ids


def coverage(vault):
    """Per epic: every live S#/A#/E# of each source UC that no story slices or tags."""
    from . import model
    res = {"epics": 0, "stories": 0, "units": 0, "covered": 0, "missing": []}
    stories = [vault.load(p) for p in vault.story_paths()]
    for ep_path in vault.epic_paths():
        ep = vault.load(ep_path)
        res["epics"] += 1
        mine = [s for s in stories if (s.fm_get("epic") or "").strip() == ep.id]
        res["stories"] += len(mine)
        for uc_id in ep.fm_list("source_ucs"):
            uc_path = vault.find(uc_id)
            if not uc_path:
                res["missing"].append(f"{ep.id} {uc_id} (no such UC)")
                continue
            uc = vault.load(uc_path)
            order = [s.id for s in model.steps(uc) if not s.dropped]
            live = order + [f.id for f in model.flows(uc) if not f.dropped]
            got = set()
            for s in mine:
                slices = parse_slices(s.fm_get("slice_of") or "")
                story_ucs = set()
                for item in slices:
                    u, ids = expand_slice(item, order)
                    story_ucs.add(u)
                    if u == uc_id:
                        got |= ids
                for u, sid in ac_tags(s.text):
                    if u == uc_id or (u is None and uc_id in story_ucs):
                        got.add(sid)
            res["units"] += len(live)
            res["covered"] += sum(1 for x in live if x in got)
            res["missing"] += [f"{ep.id} {uc_id} {x}" for x in live if x not in got]
    return res


def report(res, list_all=False):
    lines = [f"epics: {res['epics']} · stories: {res['stories']}",
             f"  UC steps/flows {res['units']:>6}  in the epics' source UCs",
             f"  covered        {res['covered']:>6}  sliced (slice_of) or tagged in a story's § 6",
             f"stage checked: stories — missing {len(res['missing'])}"]
    if res["missing"]:
        shown = res["missing"] if list_all else res["missing"][:20]
        lines.append("  " + ", ".join(shown) + ("" if list_all or len(res["missing"]) <= 20
                                                 else f" … (+{len(res['missing']) - 20}, --list for all)"))
    return "\n".join(lines)
