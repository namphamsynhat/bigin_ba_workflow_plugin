"""Stage 2 qualification — the part that is bookkeeping (``2-qualification.md``).

Three of the four gates are mostly lookups: is a question still open against this row (gate 1), is every
attachment on disk (gate 2), does every cited note row exist (gate 3). ``bigin qualify <slug>`` answers
those from the files, so the orchestrator no longer loads each intake note to find out, and returns three
lists:

- ``pass``  — nothing on record blocks the row; it goes to routing (subject to gate 4, below)
- ``held``  — a gate failed on a fact; ``--apply`` flips the row to ``held`` with the stage file's note
- ``check`` — a fact was found that only a reader can weigh (an open question that names no row, a note
              row corrected after filing, an e-mail thread that may still be waiting on a reply); each
              entry carries exactly the text needed to decide, and nothing else

Gate 4 (duplicate / already covered / supersession) is judgement about meaning and is NOT decided here.
"""
import os
import re

from . import model
from .util import EngineError
from .vault import questions_in

STATUSES = ("new", "held")


def _words(text, n=5):
    return " ".join(re.sub(r"\s+", " ", text or "").strip().split()[:n])


def _open_note_questions(note):
    s = note.section("Open Questions")
    return [q for q in questions_in(note, s.start, s.end) if not q.checked] if s else []


_ROW_LIST = re.compile(r"\brows?\s*:?\s+((?:#?\d+(?:\s*[-–]\s*#?\d+)?(?:\s*,\s*(?:and\s+)?|\s+and\s+|\s*&\s*)?)+)", re.I)


def rows_named(q_text):
    """Note row numbers a question names: '#7', 'row 34', 'rows 7, 10 and 14', 'Rows 6, 25 (…) and 28-33'.
    Read with and without parentheticals, so a list interrupted by a gloss is still one list."""
    text = q_text or ""
    out = {int(m) for m in re.findall(r"(?<![\w-])#(\d+)(?!\d)", text)}
    for variant in (text, re.sub(r"\([^)]*\)", " ", text)):
        for chunk in _ROW_LIST.findall(variant):
            for a, b in re.findall(r"#?(\d+)(?:\s*[-–]\s*#?(\d+))?", chunk):
                lo, hi = int(a), int(b or a)
                out |= set(range(lo, min(hi, lo + 500) + 1))
    return out


def _missing_attachments(vault, note):
    out = []
    for a in note.fm_list("attachments") or []:
        a = (a or "").strip().strip("\"'")
        if not a or re.match(r"^[a-z]+://", a):
            continue
        if not os.path.exists(os.path.join(vault.root, a)):
            out.append(a)
    return out


def _judge_row(vault, row):
    """(verdict, gate, note, why[]) for one Signal Log row."""
    cites = sorted(model.expand_int_cites(row.source))
    if not cites:
        return "check", 3, None, ["Source cite names no intake note row — gate 3: is it specific enough to draft from?"]
    why = []
    for nid, n in cites:
        path = vault.find(nid)
        if not path:
            return "held", 3, f"hub cite {nid} #{n} does not resolve — re-run /extract-signal verification", []
        note = vault.load(path)
        nrows = {int(r.num): r for r in model.note_rows(note)}
        if n not in nrows:
            return "held", 3, f"hub cite {nid} #{n} does not resolve — re-run /extract-signal verification", []
        missing = _missing_attachments(vault, note)
        if missing:
            return "held", 2, (f"source incomplete — {missing[0]} is not on disk; "
                               "re-run /bigin-intake then /extract-signal"), []
        notes_cell = nrows[n].get("Notes") or ""
        open_qs = _open_note_questions(note)
        named = [(q, rows_named(q.text)) for q in open_qs]
        naming = [q for q, ns in named if n in ns]
        if naming:
            return "held", 1, f"awaiting {nid} — {_words(naming[0].text)}", []
        # a question that names OTHER rows is about those rows; only one that names no row at all can
        # be about this one by subject, and that is a reader's call
        loose = [q for q, ns in named if not ns]
        if "rationale: in question" in notes_cell and loose:
            why.append(f"{nid} #{n} is marked `rationale: in question` and the note has an open question "
                       "that names no row — gate 1: is that the rationale question?")
        for q in loose:
            why.append(f"{nid} open question (names no row) — gate 1, same subject as this row?: {q.text[:200]}")
        if re.search(r"\bcorrected:|added by source audit", notes_cell):
            why.append(f"{nid} #{n} was corrected after extraction ({notes_cell[:120]}) — gate 3: does the hub "
                       f"clause still say what the note row says? Note row: {(nrows[n].get('Signal') or '')[:200]}")
        if (note.fm_get("source") or "") == "email" and (note.fm_get("status") or "") == "needs-clarification":
            why.append(f"{nid} is an e-mail note awaiting clarification — gate 2: is the thread still waiting on a reply?")
    seen, uniq = set(), []
    for w in why:
        if w not in seen:
            seen.add(w)
            uniq.append(w)
    return ("check", None, None, uniq) if uniq else ("pass", None, None, [])


def qualify(vault, slug, apply=False, dry=False):
    doc = model.signal_doc(vault, slug)
    if doc is None:
        raise EngineError(f"no hub '{slug}'")
    res = {"slug": slug, "pass": [], "held": [], "check": [], "retract": [], "flipped": [],
           "not_checked": "gate 4 (duplicate / already covered / supersession) — judgement, not decided here"}
    for row in model.signal_rows(doc):
        if row.status == "retract":
            res["retract"].append(row.num)          # never qualified: routed as-is (4-analysis.md)
            continue
        if row.status not in STATUSES:
            continue
        verdict, gate, note, why = _judge_row(vault, row)
        if verdict == "pass":
            res["pass"].append(row.num)
        elif verdict == "held":
            res["held"].append({"row": row.num, "gate": gate, "note": note, "was": row.status})
        else:
            res["check"].append({"row": row.num, "signal": (row.get("Signal") or "")[:200], "why": why})
    if apply and res["held"] and not dry:
        from . import hub
        specs = [f"{h['row']}=held@{h['note']}" for h in res["held"]]
        hub.flip(vault, slug, specs)
        res["flipped"] = [h["row"] for h in res["held"]]
    res["rows_arg"] = ",".join(res["pass"] + res["retract"])
    return res


def render(res):
    lines = [f"qualify {res['slug']}: {len(res['pass'])} pass · {len(res['held'])} held · "
             f"{len(res['check'])} need a reader · {len(res['retract'])} retract"]
    for h in res["held"]:
        lines.append(f"  held #{h['row']} (gate {h['gate']}): {h['note']}")
    for c in res["check"]:
        lines.append(f"  check #{c['row']}: {c['signal'][:80]}")
        for w in c["why"][:4]:
            lines.append(f"      {w}")
    if res["rows_arg"]:
        lines.append(f"  → bigin worklist route {res['slug']} --rows {res['rows_arg']}   (add the checked rows that pass)")
    lines.append(f"  not checked: {res['not_checked']}")
    return "\n".join(lines)
