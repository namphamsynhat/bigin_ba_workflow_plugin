"""Change sets — the one contract between agents and the engine (restructure plan § B.3).

``bigin apply <file|dir>`` is the ONLY writer of UC/BR/hub content for new work:

* validate every set against ``schema/changeset.json``; mint ids for ``create_*`` sets (locked)
  and resolve ``new:<key>`` references;
* per artifact, apply its sets in a fixed order (structure → § 1/§ 6 → rule → § 4 mirrors →
  questions) and write the file ONCE: version bump, one Changelog line carrying the trace and
  every change-set id (so re-applying is a no-op), review flag when § 2 changed, status untouched;
* an anchor whose ``sha`` no longer matches is DRIFT: nothing is overwritten, ONE question naming
  both wordings is raised instead (1-foldin.md § the human may have edited the section first);
  text already matching the proposal counts as applied (a hand-applied change);
* a ``gate`` with ``blocks: true`` goes to the ledger, its question to the artifact;
* afterwards: hub Signal Log rows flip (applied / staged), links sync, hubs refresh, statuses
  recount. No agent does any of this.
"""
import glob
import json
import os
import re

from . import jsonschema_lite, model
from .edit import (append_changelog, bump_version, changelog_has, q_core, question_block,
                   same_question, touch_updated)
from .util import EngineError, append_jsonl, load_json, norm_ws, sha, sort_ids, today
from .vault import cell_value, find_tables, questions_in, render_row, split_cells

ORDER = {
    "create_uc": 0, "create_br": 0,
    "new_step_after": 1, "replace_step": 1, "drop_step": 1,
    "new_flow": 2, "replace_flow": 2, "drop_flow": 2,
    "set_field": 3, "append_note": 3, "link": 3,
    "set_rule": 4, "append_rule_clause": 4,
    "mirror_br": 5, "unmirror_br": 5, "add_directive": 5,
    "add_question": 6, "answer_question": 7,
}
S2_OPS = {"new_step_after", "replace_step", "drop_step"}
LIST_FIELDS = {"pre-conditions", "post-conditions (success)", "post-conditions (failure)"}


class Outcome(Exception):
    """Raised inside an op to report a non-applied outcome (already / drift / invalid)."""

    def __init__(self, kind, detail="", current=None):
        super().__init__(detail)
        self.kind, self.detail, self.current = kind, detail, current


# ---------------------------------------------------------------------------- loading

def load_changesets(paths):
    """Change sets from files or directories: an envelope {kind: changesets}, a list, or one set.
    An adjudication file contributes the change sets nested in its verdicts."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "*.json")))
        else:
            files.append(p)
    out = []
    for f in files:
        data = load_json(f)
        if isinstance(data, list):
            out += data
        elif isinstance(data, dict) and data.get("kind") == "changesets":
            out += data.get("changesets") or []
        elif isinstance(data, dict) and data.get("kind") == "adjudication":
            for v in data.get("verdicts") or []:
                out += v.get("changesets") or []
        elif isinstance(data, dict) and "op" in data:
            out.append(data)
        elif isinstance(data, dict) and data.get("kind") in ("route", "filing", "signals", "audit"):
            continue
        else:
            raise EngineError(f"{f}: not a change-set file")
    return out


# ---------------------------------------------------------------------------- UC § 1 fields

def _field_line(doc, section, field):
    """(line index, is_list) of '* **Field:**' in a section, matching a field-name prefix."""
    s = doc.section(section)
    if not s:
        return None, False
    f = field.strip().rstrip(":").lower()
    for i in range(s.start, s.end):
        m = re.match(r"^\*\s+\*\*(.+?):\*\*(.*)$", doc.masked[i])
        if m and (m.group(1).strip().lower() == f or m.group(1).strip().lower().startswith(f)):
            rest = m.group(2).strip()
            return i, (not rest or m.group(1).strip().lower() in LIST_FIELDS)
    return None, False


def _field_children(doc, i, section):
    """Indices of the '  * …' sub-bullets under a list field (and their indented continuations)."""
    s = doc.section(section)
    j = i + 1
    kids = []
    while j < s.end:
        ml = doc.masked[j]
        if re.match(r"^\s{2,}\*\s", ml):
            kids.append(j)
            j += 1
            continue
        if ml.strip() == "" and doc.lines[j].strip().startswith("<!--"):
            j += 1
            continue
        if re.match(r"^\s{4,}\S", doc.lines[j]) and kids:
            j += 1
            continue
        if not doc.lines[j].strip():
            # a comment-only line inside the list is masked blank; keep scanning if more kids follow
            k = j + 1
            if k < s.end and re.match(r"^\s{2,}\*\s", doc.masked[k]):
                j += 1
                continue
        break
    return kids, j


def _is_placeholder_text(t):
    t = t.strip()
    return not t or t.startswith("`<") or t in ("`not stated`",)


def field_value(doc, section, field):
    i, is_list = _field_line(doc, section, field)
    if i is None:
        return None
    if is_list:
        kids, _ = _field_children(doc, i, section)
        vals = [re.sub(r"^\s*\*\s+", "", doc.lines[k]).strip() for k in kids]
        return "\n".join(v for v in vals if not _is_placeholder_text(v))
    v = re.sub(r"^\*\s+\*\*.+?:\*\*", "", doc.lines[i]).strip()
    return "" if _is_placeholder_text(v) else v


def op_set_field(doc, cs, append=False):
    sec = str(cs["target"].get("section") or "1")
    field = cs["target"].get("field") or (cs.get("anchor") or {}).get("ref")
    text = cs["text"].strip()
    if not field:
        # a whole-section note (§ 6, or § 1 without a field): append a paragraph
        s = doc.section(sec)
        if s is None:
            raise Outcome("invalid", f"no section {sec}")
        if norm_ws(text) in norm_ws("\n".join(doc.lines[s.start:s.end])):
            raise Outcome("already", "text already present")
        pos = s.end
        while pos > s.start and not doc.masked[pos - 1].strip():
            pos -= 1
        block = ([""] if pos > s.start and doc.lines[pos - 1].strip() else []) + text.split("\n")
        doc.splice(pos, pos, block)
        return f"§ {sec}"
    cur = field_value(doc, sec, field)
    i, is_list = _field_line(doc, sec, field)
    if i is None:
        s = doc.section(sec)
        if s is None:
            raise Outcome("invalid", f"no section {sec}")
        pos = s.end
        while pos > s.start and not doc.masked[pos - 1].strip():
            pos -= 1
        doc.splice(pos, pos, [f"* **{field}:** {text}"])
        return f"§ {sec} {field}"
    _check_anchor(cs, cur or "", text)
    if is_list:
        kids, end = _field_children(doc, i, sec)
        items = [x.strip().lstrip("*").strip() for x in text.split("\n") if x.strip()]
        new = [f"  * {x}" for x in items]
        if append:
            live = [k for k in kids if not _is_placeholder_text(re.sub(r"^\s*\*\s+", "", doc.lines[k]))]
            if all(norm_ws(x) in norm_ws(cur or "") for x in items):
                raise Outcome("already", "items already present")
            if live:
                doc.splice(live[-1] + 1, live[-1] + 1, new)
            else:
                start = kids[0] if kids else i + 1
                stop = (kids[-1] + 1) if kids else i + 1
                doc.splice(start, stop, new)
        else:
            if norm_ws(cur or "") == norm_ws("\n".join(items)):
                raise Outcome("already", "field already reads this way")
            start = kids[0] if kids else i + 1
            stop = (kids[-1] + 1) if kids else i + 1
            doc.splice(start, stop, new)
    else:
        head = re.match(r"^(\*\s+\*\*.+?:\*\*)", doc.lines[i]).group(1)
        if append and cur:
            if norm_ws(text) in norm_ws(cur):
                raise Outcome("already", "text already present")
            doc.splice(i, i + 1, [f"{head} {cur} {text}"])
        else:
            if norm_ws(cur or "") == norm_ws(text):
                raise Outcome("already", "field already reads this way")
            doc.splice(i, i + 1, [f"{head} {text}"])
    return f"§ {sec} {field}"


def _check_anchor(cs, current, proposed):
    """Drift rule: a given anchor sha must match the current text — unless the current text
    already IS the proposal (hand-applied), which the caller then reports as already."""
    a = cs.get("anchor") or {}
    want = a.get("sha")
    if not want:
        return
    if sha(current) == want or norm_ws(current) == norm_ws(proposed):
        return
    raise Outcome("drift", "anchor text changed since the change set was written", current)


# ---------------------------------------------------------------------------- § 2 steps

def _step_cells(cs):
    if cs.get("cells"):
        return cs["cells"]["actor"].strip(), cs["cells"]["system"].strip()
    t = cs.get("text", "")
    if "||" in t:
        a, b = t.split("||", 1)
        return a.strip(), b.strip()
    return t.strip(), "—"


def op_new_step(doc, cs):
    actor, system = _step_cells(cs)
    t = model.steps_table(doc)
    if t is None:
        raise Outcome("invalid", "§ 2 has no step table")
    sts = model.steps(doc)
    for st in sts:
        if norm_ws(st.actor) == norm_ws(actor) and norm_ws(st.system) == norm_ws(system):
            raise Outcome("already", f"already present as {st.id}")
    if model.is_placeholder(doc):
        doc.set_row(sts[0].idx, ["**S1**", actor, system])
        return "S1"
    ref = ((cs.get("anchor") or {}).get("ref") or "end").strip()
    new_id = model.next_id({x.id for x in sts}, "S")
    row = render_row([f"**{new_id}**", actor, system])
    if ref.lower() == "end":
        pos = sts[-1].idx + 1 if sts else t.sep_idx + 1
    elif ref.lower() == "start":
        pos = t.sep_idx + 1
    else:
        hit = next((x for x in sts if x.id == ref), None)
        if hit is None:
            raise Outcome("drift", f"anchor {ref} no longer exists in § 2", "")
        _check_anchor(cs, hit.text, f"{actor} || {system}")
        pos = hit.idx + 1
    doc.splice(pos, pos, [row])
    return new_id


def op_replace_step(doc, cs):
    ref = cs["anchor"]["ref"]
    hit = next((x for x in model.steps(doc) if x.id == ref), None)
    if hit is None:
        raise Outcome("drift", f"{ref} no longer exists in § 2", "")
    actor, system = _step_cells(cs)
    if norm_ws(hit.actor) == norm_ws(actor) and norm_ws(hit.system) == norm_ws(system):
        raise Outcome("already", f"{ref} already reads this way")
    _check_anchor(cs, hit.text, f"{actor} || {system}")
    doc.set_row(hit.idx, [f"**{ref}**", actor, system])
    return ref


def op_drop_step(doc, cs):
    ref = cs["anchor"]["ref"]
    hit = next((x for x in model.steps(doc) if x.id == ref), None)
    if hit is None:
        raise Outcome("drift", f"{ref} no longer exists in § 2", "")
    if hit.dropped:
        raise Outcome("already", f"{ref} is already dropped")
    _check_anchor(cs, hit.text, hit.text)
    doc.set_row(hit.idx, [f"**{ref}**", f"Dropped — {cs['reason'].strip()}", "—"])
    return ref


# ---------------------------------------------------------------------------- § 3 flows

def _ensure_s3(doc):
    if doc.section("3") is None:
        doc.insert_section("3. Alternative & Exception Flows", [""], before="4")
    return doc.section("3")


def _flow_kind(cs):
    k = (cs.get("flow") or {}).get("kind")
    if k:
        return k
    ref = (cs.get("anchor") or {}).get("ref") or ""
    return ref[:1] if ref[:1] in "AE" else "E"


def op_new_flow(doc, cs):
    fl = cs["flow"]
    kind = _flow_kind(cs)
    s = _ensure_s3(doc)
    fls = model.flows(doc)
    for f in fls:
        if norm_ws(f.name).lower() == norm_ws(fl["name"]).lower():
            raise Outcome("already", f"already present as {f.id}")
    new_id = model.next_id({f.id for f in fls}, kind)
    block = [f"### {new_id}: {fl['name'].strip()}"] + fl["body"].rstrip().split("\n")
    same = [f for f in fls if f.kind == kind]
    if same:
        pos = _flow_end(doc, same[-1])
    elif kind == "A" and fls:
        pos = fls[0].h
    elif fls:
        pos = _flow_end(doc, fls[-1])
    else:
        pos = s.end
        while pos > s.start and not doc.masked[pos - 1].strip():
            pos -= 1
    lead = [""] if pos > 0 and doc.lines[pos - 1].strip() else []
    tail = [""] if pos < len(doc.lines) and doc.lines[pos].strip() else []
    doc.splice(pos, pos, lead + block + tail)
    return new_id


def _flow_end(doc, f):
    end = f.end
    while end > f.h + 1 and not doc.lines[end - 1].strip():
        end -= 1
    return end


def op_replace_flow(doc, cs):
    ref = cs["anchor"]["ref"]
    hit = next((f for f in model.flows(doc) if f.id == ref), None)
    if hit is None:
        raise Outcome("drift", f"{ref} no longer exists in § 3", "")
    fl = cs["flow"]
    name = (fl.get("name") or hit.name).strip()
    proposed = f"{name}\n{fl['body']}".strip()
    if norm_ws(hit.text) == norm_ws(proposed):
        raise Outcome("already", f"{ref} already reads this way")
    _check_anchor(cs, hit.text, proposed)
    doc.splice(hit.h, _flow_end(doc, hit), [f"### {ref}: {name}"] + fl["body"].rstrip().split("\n"))
    return ref


def op_drop_flow(doc, cs):
    ref = cs["anchor"]["ref"]
    hit = next((f for f in model.flows(doc) if f.id == ref), None)
    if hit is None:
        raise Outcome("drift", f"{ref} no longer exists in § 3", "")
    if hit.dropped:
        raise Outcome("already", f"{ref} is already dropped")
    _check_anchor(cs, hit.text, hit.text)
    doc.splice(hit.h, _flow_end(doc, hit), [f"### {ref}: {hit.name} (dropped)", f"Dropped — {cs['reason'].strip()}"])
    return ref


# ---------------------------------------------------------------------------- § 4 / BR rule

def op_mirror_br(vault, doc, cs):
    from .mirror import check_enforcement
    bid = cs["br"]
    p = vault.find(bid)
    if not p:
        raise Outcome("invalid", f"{bid} has no file")
    stmt = model.br_statement(vault.load(p))
    if not stmt or model.is_placeholder_statement(stmt):
        raise Outcome("invalid", f"{bid} has no settled rule statement to mirror")
    at = cs["enforced_at"].strip()
    why = check_enforcement(doc, at)
    if why:
        raise Outcome("invalid", why)
    t = model.s4_table(doc)
    if t is None:
        s = doc.section("4")
        if s is None:
            raise Outcome("invalid", "UC has no § 4")
        pos = s.end
        while pos > s.start and not doc.masked[pos - 1].strip():
            pos -= 1
        doc.splice(pos, pos, ["", "| Rule | Statement (short) | Enforced at |", "| :--- | :--- | :--- |"])
        t = model.s4_table(doc)
    for idx, cells in model.s4_rows(doc):
        if cells[0] == bid:
            if cell_value(cells[2] if len(cells) > 2 else "") == at and norm_ws(cells[1]) == norm_ws(stmt):
                raise Outcome("already", f"{bid} already mirrored at {at}")
            doc.set_row(idx, [bid, stmt, at])
            break
    else:
        rows = model.s4_rows(doc)
        pos = rows[-1][0] + 1 if rows else t.sep_idx + 1
        doc.splice(pos, pos, [render_row([bid, stmt, at])])
    if doc.fm and "brs" in doc.fm:
        doc.fm_set("brs", model.s4_brs(doc))
    return f"§ 4 {bid}"


def op_unmirror_br(vault, doc, cs):
    """Remove a § 4 row (a rule moved to another UC by a split, or mis-attached) and drop this UC
    from the BR's uc: list. The only engine path that removes a link — explicit, with a reason."""
    bid = cs["br"]
    for idx, cells in model.s4_rows(doc):
        if cells[0] == bid:
            doc.splice(idx, idx + 1, [])
            break
    else:
        raise Outcome("already", f"{bid} is not mirrored here")
    if doc.fm and "brs" in doc.fm:
        doc.fm_set("brs", model.s4_brs(doc))
    p = vault.find(bid)
    if p:
        b = vault.load(p)
        if doc.id in b.fm_list("uc"):
            b.fm_set("uc", [x for x in b.fm_list("uc") if x != doc.id])
            append_changelog(b, f"- {today()} — bigin apply: no longer governs {doc.id} ({cs['reason'].strip()}). cs: {cs['id']}.")
            vault.write(b)
    return f"§ 4 −{bid}"


def op_set_rule(doc, cs, append=False):
    r = model.br_statement_range(doc)
    cur = model.br_statement(doc)
    text = cs["text"].strip()
    if append:
        if norm_ws(text) in norm_ws(cur):
            raise Outcome("already", "clause already in the rule")
        new = (cur + " " + text).strip() if not model.is_placeholder_statement(cur) else text
    else:
        if norm_ws(cur) == norm_ws(text):
            raise Outcome("already", "rule already reads this way")
        if not model.is_placeholder_statement(cur):
            _check_anchor(cs, cur, text)
        new = text
    if r is None:
        # no statement paragraph yet: place it after the H1
        first_h2 = doc.sections[0].h if doc.sections else len(doc.lines)
        h1 = next((i for i in range(doc.body_start, first_h2) if doc.lines[i].startswith("# ")), doc.body_start)
        doc.splice(h1 + 1, h1 + 1, ["", new])
    else:
        doc.splice(r[0], r[1], [new])
    return "rule"


# ---------------------------------------------------------------------------- questions

def _question_area(doc, kind):
    """(start, end) where new questions go for this artifact kind."""
    if kind == "UC":
        r = model.uc_still_open_range(doc)
        if r is None:
            raise Outcome("invalid", "UC has no § 5")
        return r
    key = "Open Questions / Gates" if kind == "HUB" else "Open Questions"
    s = doc.section(key)
    if s is None:
        doc.insert_section(key, [""], before="Changelog")
        s = doc.section(key)
    return s.start, s.end


def add_question(doc, kind, text, owner=None, ref=None):
    start, end = _question_area(doc, kind)
    for q in questions_in(doc, start, end):
        if same_question(q.text, text):
            raise Outcome("already", "the same question is already open")
    pos = end
    while pos > start and not doc.masked[pos - 1].strip():
        pos -= 1
    block = question_block(text, owner=owner, ref=ref)
    if pos > 0 and doc.lines[pos - 1].strip() and not re.match(r"^\s*(- \[|A:)", doc.lines[pos - 1].strip()) \
            and not re.match(r"^\s+A:", doc.lines[pos - 1]):
        block = [""] + block
    doc.splice(pos, pos, block)
    return "§ 5" if kind == "UC" else "questions"


def op_answer_question(doc, kind, cs):
    anchor = cs["anchor"].get("ref") or ""
    start, end = _question_area(doc, kind)
    qs = questions_in(doc, start, end)
    hit = None
    for q in qs:
        if (cs["anchor"].get("sha") and sha(q.text) == cs["anchor"]["sha"]) or \
                (anchor and q_core(q.text).startswith(q_core(anchor)[:80])):
            hit = q
            break
    if hit is None:
        raise Outcome("drift", "question not found (reworded or already settled)", "")
    if hit.checked and hit.answered and kind != "UC":
        raise Outcome("already", "question already answered")
    # an orphan answer (ticked by a human, never folded) settles with the human's own words
    answer = hit.answer if (hit.checked and hit.answered) else cs["text"].strip()
    if kind == "UC":
        # settled → move to the Decision log (use-case.md § 5); the Still-open line leaves
        t = model.decision_table(doc)
        m = re.search(r"\(ref:\s*([^)]*)\)", hit.text)
        o = re.search(r"\(owner:\s*([^)]*)\)", hit.text)
        topic = re.sub(r"\((owner|ref):[^)]*\)", "", hit.text).strip()
        raised = "; ".join(x for x in ((o.group(1) if o else ""), (m.group(1) if m else "")) if x) or "not stated"
        doc.splice(hit.start, hit.end, [])
        t = model.decision_table(doc)
        if t is None:
            raise Outcome("invalid", "UC § 5 has no Decision log table")
        nums = [int(r[0]) for r in t.rows() if r and r[0].strip().isdigit()]
        row = render_row([str(max(nums or [0]) + 1), topic, raised, answer, today()])
        doc.splice(t.end, t.end, [row])
    else:
        doc.splice(hit.start, hit.end, question_block(hit.text, answer=answer, indent=" " * hit.indent, checked=True))
    return "§ 5 decision" if kind == "UC" else "questions"


# ---------------------------------------------------------------------------- hub / design

def settle_answered(doc):
    """Move every ticked-and-answered § 5 Still-open question to the Decision log (UC only).
    Returns how many moved. Unanswered or unticked questions never move (questions are add-only)."""
    r = model.uc_still_open_range(doc)
    if r is None:
        return 0
    moved = 0
    for q in reversed(questions_in(doc, *r)):
        if not (q.checked and q.answered):
            continue
        m = re.search(r"\(ref:\s*([^)]*)\)", q.text)
        o = re.search(r"\(owner:\s*([^)]*)\)", q.text)
        topic = re.sub(r"\((owner|ref):[^)]*\)", "", q.text).strip()
        raised = "; ".join(x for x in ((o.group(1) if o else ""), (m.group(1) if m else "")) if x) or "not stated"
        doc.splice(q.start, q.end, [])
        t = model.decision_table(doc)
        if t is None:
            return moved
        nums = [int(x[0]) for x in t.rows() if x and x[0].strip().isdigit()]
        doc.splice(t.end, t.end, [render_row([str(max(nums or [0]) + 1), topic, raised, q.answer, today()])])
        moved += 1
    return moved


def op_add_directive(doc, cs):
    t = doc.table("Design Directives")
    if t is None:
        s = doc.section("Design Directives")
        if s is None:
            doc.insert_section("Design Directives", [""], before="Changelog")
            s = doc.section("Design Directives")
        doc.splice(s.end if not doc.lines[s.end - 1].strip() else s.end, s.end,
                   ["| # | Directive | Source | Status | Notes |", "|---|-----------|--------|--------|-------|", ""])
        t = doc.table("Design Directives")
    for r in t.rows():
        if len(r) > 1 and norm_ws(r[1]) == norm_ws(cs["text"]):
            raise Outcome("already", f"directive already present as #{r[0]}")
    nums = [int(r[0]) for r in t.rows() if r and r[0].isdigit()]
    n = max(nums or [0]) + 1
    tr = cs.get("trace") or {}
    src = _trace_text(tr) or "not stated"
    pos = t.row_idxs[-1] + 1 if t.row_idxs else t.sep_idx + 1
    doc.splice(pos, pos, [render_row([n, cs["text"].strip(), src, "open", ""])])
    return f"Design Directives #{n}"


def op_flag_conflict(doc, cs):
    """Signal Log rows in trace.hub_rows → `conflict`, and ONE question on the hub naming both sides
    (4-sync.md § Part 3: never auto-resolve)."""
    tr = cs.get("trace") or {}
    add_question(doc, "HUB", cs["text"], cs.get("owner", "team"), _trace_text(tr) or None)
    return "conflict question"


def op_add_principle(vault, cs):
    from .notes import _register_rows
    d, t = _register_rows(vault, "DESIGN-PRINCIPLES.md")
    if t is None:
        raise Outcome("invalid", "DESIGN-PRINCIPLES.md has no table")
    for r in t.rows():
        if len(r) > 1 and norm_ws(r[1]) == norm_ws(cs["text"]):
            raise Outcome("already", f"principle already present as #{r[0]}")
    nums = [int(r[0]) for r in t.rows() if r and r[0].isdigit()]
    cells = {"#": str(max(nums or [0]) + 1), "Principle": cs["text"].strip(), "Why": cs.get("reason", "not stated"),
             "Category": cs["target"].get("field", ""), "Source": _trace_text(cs.get("trace") or {}) or "not stated",
             "Status": "active", "Notes": ""}
    pos = t.row_idxs[-1] + 1 if t.row_idxs else t.sep_idx + 1
    d.splice(pos, pos, [render_row([cells.get(h, "") for h in t.header])])
    vault.write(d)
    return f"DESIGN-PRINCIPLES #{cells['#']}"


def op_link(doc, cs):
    field = cs["field"]
    if not doc.fm or field not in doc.fm:
        raise Outcome("invalid", f"no frontmatter list '{field}'")
    cur = doc.fm_list(field)
    add = [x for x in cs["ids"] if x not in cur]
    if not add:
        raise Outcome("already", f"{field} already lists them")
    new = cur + add
    if field in ("brs", "uc", "sources", "entities", "pain_points"):
        new = sort_ids(new)
    doc.fm_set(field, new)
    return f"{field}:"


# ---------------------------------------------------------------------------- engine

def _trace_text(tr):
    parts = []
    ints = sort_ids(([tr["int"]] if tr.get("int") else []) + list(tr.get("ints") or []))
    if ints:
        parts.append(", ".join(ints))
    if tr.get("hub") and tr.get("hub_rows"):
        parts.append(f"{tr['hub']} hub row{'s' if len(tr['hub_rows']) > 1 else ''} "
                     + ", ".join(f"#{r}" for r in tr["hub_rows"]))
    if tr.get("xr"):
        parts.append("XR: " + ", ".join(tr["xr"]))
    return "; ".join(parts)


def _drift_question(target_id, ref, current, proposed, tr):
    where = f"{ref}" if ref else "this text"
    ref_tag = _trace_text(tr) or None
    return (f"{where} of {target_id} was reworded after this change was proposed. It now reads: "
            f"“{norm_ws(current)[:400]}”. The proposed wording is: “{norm_ws(proposed)[:400]}”. Which wording is right?"), ref_tag


def _proposed_text(cs):
    if cs.get("cells"):
        return f"{cs['cells']['actor']} || {cs['cells']['system']}"
    if cs.get("flow"):
        return f"{cs['flow'].get('name', '')}: {cs['flow'].get('body', '')}"
    return cs.get("text", "")


def _kind(cs):
    k = cs["target"]["kind"]
    if k == "ENTITY_REF":
        return "UC" if cs["target"]["id"].startswith("UC") else "BR"
    if k == "DESIGN":
        return "HUB"
    return k


def _doc_for(vault, cs):
    kind, tid = _kind(cs), cs["target"]["id"]
    if kind == "HUB":
        p = vault.hub_path(tid)
        if not os.path.exists(p):
            raise Outcome("invalid", f"no hub '{tid}'")
        return vault.load(p)
    p = vault.find(tid)
    if not p:
        raise Outcome("invalid", f"{tid} has no file")
    return vault.load(p)


def _dispatch(vault, doc, cs):
    op = cs["op"]
    kind = _kind(cs)
    sec = str(cs["target"].get("section") or "")
    if op in ("set_field", "append_note"):
        if kind == "HUB":
            if op == "append_note":
                s = doc.section("Notes / History")
                if s is None:
                    raise Outcome("invalid", "hub has no Notes / History")
                pos = s.end
                while pos > s.start and not doc.masked[pos - 1].strip():
                    pos -= 1
                doc.splice(pos, pos, [f"- {today()} — {cs['text'].strip()}"])
                return "Notes / History"
            raise Outcome("invalid", "set_field is not a hub op")
        if kind == "BR":
            return op_set_rule(doc, cs, append=(op == "append_note"))
        return op_set_field(doc, cs, append=(op == "append_note"))
    if op == "new_step_after":
        return op_new_step(doc, cs)
    if op == "replace_step":
        return op_replace_step(doc, cs)
    if op == "drop_step":
        return op_drop_step(doc, cs)
    if op == "new_flow":
        return op_new_flow(doc, cs)
    if op == "replace_flow":
        return op_replace_flow(doc, cs)
    if op == "drop_flow":
        return op_drop_flow(doc, cs)
    if op == "mirror_br":
        return op_mirror_br(vault, doc, cs)
    if op == "unmirror_br":
        return op_unmirror_br(vault, doc, cs)
    if op in ("set_rule", "append_rule_clause"):
        if kind != "BR":
            raise Outcome("invalid", f"{op} targets a BR")
        return op_set_rule(doc, cs, append=(op == "append_rule_clause"))
    if op == "add_question":
        tr = cs.get("trace") or {}
        return add_question(doc, kind, cs["text"], cs.get("owner"), cs.get("ref") or _trace_text(tr) or None)
    if op == "answer_question":
        return op_answer_question(doc, kind, cs)
    if op == "link":
        return op_link(doc, cs)
    if op == "add_directive":
        return op_add_directive(doc, cs)
    if op == "flag_conflict":
        if kind != "HUB":
            raise Outcome("invalid", "flag_conflict targets a HUB")
        return op_flag_conflict(doc, cs)
    raise Outcome("invalid", f"op {op} not handled here")


def _resolve(cs, keymap):
    """Replace new:<key> references with minted ids."""
    t = cs["target"]["id"]
    if t.startswith("new:"):
        if t[4:] not in keymap:
            raise Outcome("invalid", f"{t} was not created in this batch")
        cs["target"]["id"] = keymap[t[4:]]
    if str(cs.get("br", "")).startswith("new:"):
        k = cs["br"][4:]
        if k not in keymap:
            raise Outcome("invalid", f"{cs['br']} was not created in this batch")
        cs["br"] = keymap[k]
    if cs.get("ids"):
        cs["ids"] = [keymap.get(x[4:], x) if x.startswith("new:") else x for x in cs["ids"]]

    def sub(t):
        return re.sub(r"\bnew:([A-Za-z0-9_-]+)", lambda m: keymap.get(m.group(1), m.group(0)), t) if isinstance(t, str) else t
    for k in ("text", "reason", "enforced_at"):
        if k in cs:
            cs[k] = sub(cs[k])
    for k in ("cells", "flow"):
        if isinstance(cs.get(k), dict):
            cs[k] = {kk: sub(vv) for kk, vv in cs[k].items()}


def _create(vault, cs, dry, keymap):
    from . import ids
    c = dict(cs["create"])
    tr = cs.get("trace") or {}
    srcs = sort_ids(list(c.get("sources") or []) + ([tr["int"]] if tr.get("int") else []) + list(tr.get("ints") or []))
    c["sources"] = srcs
    if dry:
        n = len(keymap) + 1
        keymap[cs["key"]] = f"{'UC' if cs['op'] == 'create_uc' else 'BR'}-NEW{n}"
        return keymap[cs["key"]]
    if cs["op"] == "create_uc":
        for p in vault.uc_paths():
            d = vault.load(p)
            if norm_ws(d.fm_get("title") or "").lower() == norm_ws(c.get("title", "")).lower() \
                    and changelog_has(d, f"created by {cs['id']}"):
                keymap[cs["key"]] = d.id
                raise Outcome("already", f"created earlier as {d.id}")
        uid, _ = ids.mint_uc(vault, c, refresh=False)
    else:
        c["uc"] = [keymap.get(x[4:], x) if str(x).startswith("new:") else x for x in c.get("uc") or []]
        for p in vault.br_paths():
            d = vault.load(p)
            if changelog_has(d, f"created by {cs['id']}"):
                keymap[cs["key"]] = d.id
                raise Outcome("already", f"created earlier as {d.id}")
        uid, _ = ids.mint_br(vault, c, refresh=False)
        hp = vault.hub_path(c["feature"])
        if os.path.exists(hp):
            h = vault.load(hp)
            if uid not in h.fm_list("br"):
                h.fm_set("br", sort_ids(h.fm_list("br") + [uid]))
                vault.write(h)
    keymap[cs["key"]] = uid
    d = vault.load(vault.find(uid))
    append_changelog(d, f"- {today()} — bigin apply: created by {cs['id']}" + (f" ({_trace_text(tr)})" if _trace_text(tr) else ""))
    vault.write(d)
    return uid


def apply(vault, changesets, run=None, dry=False, release_ids=None):
    """Apply a batch. Returns a result dict (see render_result)."""
    from . import hub as hubmod
    from . import ledger, mirror, status
    prev_batch = os.environ.get("BIGIN_BATCH")
    os.environ["BIGIN_BATCH"] = "1"
    res = {"run": run, "applied": [], "already": [], "gated": [], "drift": [], "invalid": [], "rejected": [],
           "created": {}, "written": [], "hubs_refreshed": [], "rows": {}, "review": []}
    try:
        schema = jsonschema_lite.load("changeset")
        valid = []
        seen = set()
        for cs in changesets:
            errs = jsonschema_lite.validate(cs, schema)
            if not errs and cs["id"] in seen:
                errs = [f"duplicate change-set id {cs['id']}"]
            if errs:
                res["rejected"].append({"id": cs.get("id"), "errors": errs[:6]})
                continue
            seen.add(cs["id"])
            valid.append(json.loads(json.dumps(cs)))
        keymap = {}
        row_outcomes_pre = {}
        # 1 — creates, serially under the id lock
        for cs in [c for c in valid if c["op"] in ("create_uc", "create_br")]:
            try:
                uid = _create(vault, cs, dry, keymap)
                res["created"][cs["key"]] = uid
                res["applied"].append(_entry(cs, uid))
            except Outcome as o:
                if o.kind == "already":
                    res["created"][cs["key"]] = keymap.get(cs["key"])
                    res["already"].append(_entry(cs, o.detail))
                else:
                    res["invalid"].append(_entry(cs, o.detail))
        for cs in [c for c in valid if c["op"] == "add_principle"]:
            try:
                where = op_add_principle(vault, cs) if not dry else "DESIGN-PRINCIPLES (dry)"
                res["applied"].append(_entry(cs, where))
                _note_row(row_outcomes_pre, cs.get("trace") or {}, "applied", "DESIGN-PRINCIPLES")
            except Outcome as o:
                res["already" if o.kind == "already" else "invalid"].append(_entry(cs, o.detail))
        rest = [c for c in valid if c["op"] not in ("create_uc", "create_br", "add_principle")]
        groups = {}
        for cs in rest:
            try:
                _resolve(cs, keymap)
            except Outcome as o:
                res["invalid"].append(_entry(cs, o.detail))
                continue
            key = (_kind(cs), cs["target"]["id"])
            groups.setdefault(key, []).append(cs)
        touched_hubs, touched_ids = set(), set()
        row_outcomes = dict(row_outcomes_pre)  # (hub, row) -> list of (outcome, dest)
        for (kind, tid), sets in groups.items():
            try:
                doc = _doc_for(vault, sets[0])
            except Outcome as o:
                for cs in sets:
                    res["invalid"].append(_entry(cs, o.detail))
                continue
            sets.sort(key=lambda c: ORDER.get(c["op"], 9))
            did, dests, s2 = [], [], False
            gated_ids, drift_ids = [], []
            done_ids = applied_ids(doc)
            for cs in sets:
                tr = cs.get("trace") or {}
                if cs["id"] in done_ids:
                    res["already"].append(_entry(cs, "already applied (Changelog cites it)"))
                    _note_row(row_outcomes, tr, "applied", None)
                    continue
                gate = cs.get("gate") or {}
                if gate.get("blocks") and cs["id"] not in (release_ids or set()):
                    try:
                        add_question(doc, kind, gate["question"], gate.get("owner"), _trace_text(tr) or None)
                        gated_ids.append(cs["id"])
                    except Outcome:
                        pass  # the question is already open — gate on it all the same
                    if not dry:
                        ledger.add(vault, cs, tid)
                    res["gated"].append(_entry(cs, gate["question"]))
                    _note_row(row_outcomes, tr, "gated", _dest(tid, "pending"))
                    continue
                try:
                    where = _dispatch(vault, doc, cs)
                    did.append(cs)
                    dests.append(where)
                    s2 = s2 or cs["op"] in S2_OPS or bool((cs.get("flags") or {}).get("review"))
                    res["applied"].append(_entry(cs, f"{tid} {where}"))
                    _note_row(row_outcomes, tr, "conflict" if cs["op"] == "flag_conflict" else "applied", _dest(tid, where))
                except Outcome as o:
                    if o.kind == "already":
                        res["already"].append(_entry(cs, o.detail))
                        _note_row(row_outcomes, tr, "applied", _dest(tid, (cs.get("anchor") or {}).get("ref") or ""))
                    elif o.kind == "drift":
                        ref = (cs.get("anchor") or {}).get("ref")
                        q, reftag = _drift_question(tid, ref, o.current or "", _proposed_text(cs), tr)
                        try:
                            add_question(doc, "UC" if kind == "UC" else kind, q, "team", reftag)
                            drift_ids.append(cs["id"])
                        except Outcome:
                            pass
                        res["drift"].append(_entry(cs, o.detail))
                        _note_row(row_outcomes, tr, "drift", _dest(tid, "drift question"))
                    else:
                        res["invalid"].append(_entry(cs, o.detail))
                        _note_row(row_outcomes, tr, "invalid", None)
            if not doc.changed:
                continue
            if kind in ("UC", "BR"):
                ver = bump_version(doc)
                touch_updated(doc)
                trace = _merge_trace([c.get("trace") or {} for c in sets if c in did or c["id"] in gated_ids + drift_ids])
                what = _summarise(did, dests) if did else "no content change"
                line = f"- {ver} ({today()}) — bigin apply: {what}"
                if gated_ids:
                    line += f"; {len(gated_ids)} change(s) waiting on a question (gated: {', '.join(gated_ids)})"
                if drift_ids:
                    line += f"; {len(drift_ids)} not applied — the text was reworded, question raised (drift: {', '.join(drift_ids)})"
                if trace:
                    line += f" — from {trace}"
                if did:
                    line += f". cs: {', '.join(c['id'] for c in did)}."
                else:
                    line += "."
                if s2:
                    line += " § 2 changed — flagged for review."
                    res["review"].append(tid)
                append_changelog(doc, line)
                touched_ids.add(tid)
                for f in [doc.fm_get("primary_feature") or doc.fm_get("feature")] + doc.fm_list("features"):
                    if f:
                        touched_hubs.add(f)
            else:
                touch_updated(doc)
                append_changelog(doc, f"- {today()} — bigin apply: {_summarise(did, dests)}"
                                      + (f". cs: {', '.join(c['id'] for c in did)}." if did else "."))
                touched_hubs.add(tid)
            if dry:
                doc.verify()
                vault.forget(doc.path)
            else:
                vault.write(doc)
                res["written"].append(vault.rel(doc.path))
        # 2 — hub Signal Log rows
        res["rows"] = _flip_rows(vault, row_outcomes, dry, release_ids)
        touched_hubs |= {h for h, _ in row_outcomes}
        if not dry and (touched_ids or res["created"]):
            # a restated rule refreshes every UC § 4 row that mirrors it (never a hand edit, never an agent)
            ruled = {e["target"] for e in res["applied"] if e["op"] in ("set_rule", "append_rule_clause")}
            if ruled:
                ucs = {vault.load(p).id for p in vault.uc_paths()
                       if set(model.s4_brs(vault.load(p))) & ruled}
                if ucs:
                    mirror.mirror_brs(vault, ucs)
                    touched_ids |= ucs
            mirror.sync_links(vault)
            ix = hubmod.Index(vault)
            for slug in sorted(touched_hubs):
                if os.path.exists(vault.hub_path(slug)):
                    if hubmod.refresh(vault, slug, ix):
                        res["hubs_refreshed"].append(slug)
            status.recount(vault, touched_ids | set(res["created"].values()))
            ledger.render_blocks(vault)
        if run and not dry:
            for bucket in ("applied", "already", "gated", "drift", "invalid"):
                for e in res[bucket]:
                    append_jsonl(os.path.join(vault.runs_dir, run, "results.jsonl"),
                                 {"task": e["id"], "status": bucket, "target": e.get("target"), "at": today()})
    finally:
        if prev_batch is None:
            os.environ.pop("BIGIN_BATCH", None)
        else:
            os.environ["BIGIN_BATCH"] = prev_batch
    return res


CS_LIST = re.compile(r"\bcs: ([^\n]*?)\.?\s*(?:§ 2 changed|$)")


def applied_ids(doc):
    """Change-set ids a Changelog line records as APPLIED ('cs: a, b.'). Gated and drifted ids are
    recorded under 'gated:' / 'drift:' and do not count."""
    s = doc.section("Changelog")
    out = set()
    if not s:
        return out
    for line in doc.lines[s.start:s.end]:
        for m in CS_LIST.finditer(line):
            out |= {x.strip().rstrip(".") for x in m.group(1).split(",") if x.strip().startswith("cs-")}
    return out


def _entry(cs, detail):
    return {"id": cs.get("id"), "op": cs.get("op"), "target": (cs.get("target") or {}).get("id"), "detail": detail}


def _dest(tid, where):
    where = (where or "").strip()
    if not where:
        return tid
    if where.startswith(tid):
        return where
    return f"{tid} {where}".strip()


def _note_row(acc, tr, outcome, dest):
    hub = tr.get("hub")
    for r in tr.get("hub_rows") or []:
        acc.setdefault((hub, str(r)), []).append((outcome, dest))


def _flip_rows(vault, acc, dry, release_ids=None):
    """applied when every set tracing the row landed and no open ledger entry cites it;
    staged when any is gated or drifted. Invalid-only rows are left alone."""
    from . import hub as hubmod
    from . import ledger
    open_rows = set()
    for e in ledger.entries(vault, state="open"):
        if release_ids and e["id"] in release_ids:
            continue
        tr = e["changeset"].get("trace") or {}
        for r in tr.get("hub_rows") or []:
            open_rows.add((tr.get("hub"), str(r)))
    by_hub = {}
    for (hub, row), outs in acc.items():
        if not hub:
            continue
        kinds = {o for o, _ in outs}
        dests = [d for _, d in outs if d]
        if kinds <= {"invalid"}:
            continue
        if "conflict" in kinds:
            st = "conflict"
        elif "gated" in kinds or "drift" in kinds or (hub, row) in open_rows:
            st = "staged"
        elif "applied" in kinds:
            st = "applied"
        else:
            continue
        by_hub.setdefault(hub, []).append((row, st, " · ".join(dict.fromkeys(dests))))
    report = {}
    for hub, items in by_hub.items():
        doc = model.signal_doc(vault, hub)
        if doc is None:
            continue
        rows = {r.num: r for r in model.signal_rows(doc)}
        for row, st, dest in items:
            r = rows.get(row)
            if r is None:
                continue
            if r.status in ("superseded", "rejected"):
                continue
            if st == "applied":
                # a destination written while the change waited no longer describes it
                keep = [x.strip() for x in r.destination.split("·")
                        if x.strip() and not re.search(r"\b(pending|drift question)$", x.strip())]
                if keep != [x.strip() for x in r.destination.split("·") if x.strip()]:
                    cells = list(r.cells)
                    k = [h.lower() for h in r.header].index("destination")
                    cells[k] = " · ".join(keep)
                    doc.set_row(r.idx, cells)
                    r = {x.num: x for x in model.signal_rows(doc)}[row]
                dest = " · ".join(x for x in dest.split(" · ") if not re.search(r"\b(pending|drift question)$", x)) if dest else dest
            hubmod.set_row(doc, r, st, dest or None, add_dest=True)
            rows = {x.num: x for x in model.signal_rows(doc)}
            report.setdefault(hub, []).append(f"#{row}→{st}")
        if dry:
            vault.forget(doc.path)
        else:
            vault.write(doc)
    return report


def _merge_trace(trs):
    ints, rows, xr = set(), {}, []
    for tr in trs:
        if tr.get("int"):
            ints.add(tr["int"])
        ints |= set(tr.get("ints") or [])
        if tr.get("hub"):
            rows.setdefault(tr["hub"], [])
            rows[tr["hub"]] += [str(r) for r in tr.get("hub_rows") or []]
        xr += tr.get("xr") or []
    parts = []
    if ints:
        parts.append(", ".join(sort_ids(ints)))
    for h, rs in rows.items():
        if rs:
            parts.append(f"{h} hub rows " + ", ".join(f"#{r}" for r in dict.fromkeys(rs)))
    if xr:
        parts.append("XR: " + ", ".join(dict.fromkeys(xr)))
    return "; ".join(parts)


def _summarise(sets, dests):
    counts = {}
    for c in sets:
        counts[c["op"]] = counts.get(c["op"], 0) + 1
    label = {"new_step_after": "step(s) added", "replace_step": "step(s) changed", "drop_step": "step(s) dropped",
             "new_flow": "flow(s) added", "replace_flow": "flow(s) changed", "drop_flow": "flow(s) dropped",
             "set_field": "field(s) set", "append_note": "note(s) appended", "mirror_br": "rule mirror(s)",
             "add_question": "question(s) raised", "answer_question": "question(s) settled",
             "set_rule": "rule restated", "unmirror_br": "rule mirror(s) removed", "append_rule_clause": "rule clause(s) added", "link": "link(s)",
             "add_directive": "directive(s) added", "flag_conflict": "conflict(s) flagged"}
    parts = [f"{n} {label.get(op, op)}" for op, n in counts.items()]
    where = ", ".join(dict.fromkeys(d for d in dests if d))
    return "; ".join(parts) + (f" ({where})" if where else "")


def apply_paths(vault, paths, run=None, dry=False):
    return apply(vault, load_changesets(paths), run=run, dry=dry)


def render_result(res):
    lines = [f"apply{' (dry)' if not res['written'] and res['applied'] else ''}: "
             f"{len(res['applied'])} applied · {len(res['already'])} already · {len(res['gated'])} gated · "
             f"{len(res['drift'])} drift · {len(res['invalid'])} invalid · {len(res['rejected'])} rejected"]
    if res["created"]:
        lines.append("created: " + ", ".join(f"{k}={v}" for k, v in res["created"].items()))
    for bucket in ("drift", "invalid"):
        for e in res[bucket][:10]:
            lines.append(f"  {bucket}: {e['id']} {e['target']} — {e['detail']}")
    for e in res["rejected"][:10]:
        lines.append(f"  rejected: {e['id']} — {'; '.join(e['errors'])}")
    if res["rows"]:
        lines.append("rows: " + "; ".join(f"{h} {' '.join(v)}" for h, v in res["rows"].items()))
    if res["review"]:
        lines.append("flagged for review (§ 2 changed): " + ", ".join(sorted(set(res["review"]))))
    return "\n".join(lines)
