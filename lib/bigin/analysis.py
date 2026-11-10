"""Intake analysis and withdrawal — the business-analyst half of /extract-signal.

``worklist``   ``bigin worklist analyze <INT>`` — the filed note's rows and hub rows, read against the
               current requirements of every feature it anchored to: compact UC cards, BR statements,
               the questions already open there, and the pending (not yet drafted) rows of those hubs.
``apply``      analysis.json (intake-analyst) → the note's engine-owned ``## Analysis`` section: what the
               request asks, the flow as understood, the features / use cases / rules it will change
               (with what is built on them downstream), the conflicts with current requirements, and the
               questions where the request is unclear against them. Questions land on the note's
               ``## Open Questions`` (add-only); a BLOCKING conflict flips the note row and its hub row to
               ``conflict`` so transform waits for the decision instead of drafting over the current spec.
``withdraw``   ``bigin note withdraw <INT> --reason`` — the client removed the request (a deleted or
               cancelled ticket, a retracted email). The note keeps everything it said (history) and is
               marked ``status: withdrawn``; every hub row it filed is closed so the source of truth never
               carries a requirement nobody asked for any more:
                   new / held / question / conflict  → withdrawn
                   staged                            → its ledger change sets superseded, row withdrawn
                   applied                           → retract: transform (uc-router) drafts the change
                                                       sets that take it back out; ``bigin apply`` flips
                                                       the row to withdrawn and the UC Changelog says why
               Questions this note alone raised on a UC/BR are ticked "not needed — withdrawn".

Nothing here drafts UC or BR content; the analyst only reads, and retraction goes through change sets.
"""
import json
import os
import re

from . import jsonschema_lite, model
from .edit import append_changelog, question_block, same_question, touch_updated
from .util import EngineError, load_json, sha, today
from .vault import questions_in

MARK = "<!-- engine-owned: `bigin note analysis-apply` rewrites this section on every extract run — edit nothing here; answer questions in ## Open Questions -->"
WMARK = "<!-- engine-owned: written by `bigin note withdraw` — the request was removed; nothing below is a live requirement -->"
UNPROCESSED = ("new", "held", "question", "conflict")


def _t(text, n=140):
    text = re.sub(r"\s+", " ", (text or "").replace("|", "/")).strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def _cites(r):
    return {n for n, _ in model.expand_int_cites(r.source)} | set(re.findall(r"\bINT-\d+\b", r.source or ""))


def _note_hub_rows(vault, nid):
    """[(slug, signal_doc, row)] for every Signal Log row citing ``nid``."""
    out = []
    for slug in vault.slugs():
        sd = model.signal_doc(vault, slug)
        for r in model.signal_rows(sd) if sd else []:
            if nid in _cites(r):
                out.append((slug, sd, r))
    return out


def _row_nums(r, nid):
    return {int(n) for x, n in model.expand_int_cites(r.source) if x == nid and str(n).isdigit()}


# ---------------------------------------------------------------------------- worklist

def worklist(vault, nid, args=None):
    from .worklist import uc_card
    d = vault.load_id(nid)
    rows = model.note_rows(d)
    if not rows:
        raise EngineError(f"{nid} has no extracted signals — analysis runs after filing")
    if (d.fm_get("status") or "") == "withdrawn":
        raise EngineError(f"{nid} is withdrawn — nothing to analyse")
    feats = []
    for r in rows:
        for f in re.split(r"\s*/\s*", r.get("Feature") or ""):
            f = f.strip()
            if f and not f.startswith("unresolved") and f not in feats and os.path.exists(vault.hub_path(f)):
                feats.append(f)
    for f in d.fm_list("declared_features"):
        if f not in feats and os.path.exists(vault.hub_path(f)):
            feats.append(f)
    ucs, index = [], []
    for p in vault.uc_paths():
        u = vault.load(p)
        st = u.fm_get("status") or ""
        index.append(f"{u.id} {model.title_of(u)} [{u.fm_get('primary_feature')}] {st}")
        if st in ("removed", "consolidated"):
            continue
        if set([u.fm_get("primary_feature")] + u.fm_list("features")) & set(feats):
            c = uc_card(vault, u, full=True)
            c["version"] = str(u.fm_get("version") or "")
            ucs.append(c)
    brs, seen = [], set()
    for f in feats:
        for b in vault.load(vault.hub_path(f)).fm_list("br"):
            p = vault.find(b)
            if not p or b in seen:
                continue
            seen.add(b)
            bd = vault.load(p)
            stmt = model.br_statement(bd)
            brs.append({"id": bd.id, "title": model.title_of(bd), "status": bd.fm_get("status") or "",
                        "uc": bd.fm_list("uc"), "statement": stmt[:600] + ("…" if len(stmt) > 600 else ""),
                        "sha": sha(stmt), "open_questions": [q.text[:200] for q in model.open_questions(bd)]})
    mine, pending = [], []
    for f in feats:
        sd = model.signal_doc(vault, f)
        for r in model.signal_rows(sd) if sd else []:
            item = {"hub": f, "row": r.num, "signal": _t(r.get("Signal"), 300), "type": r.get("Type"),
                    "status": r.status, "destination": r.destination, "source": _t(r.source, 80)}
            if nid in _cites(r):
                mine.append(item)
            elif r.status in ("new", "held", "staged", "question", "conflict"):
                pending.append(item)
    s = d.section("Open Questions")
    note_qs = [q.text[:200] for q in questions_in(d, s.start, s.end) if not q.checked] if s else []
    jira = {k: d.fm_get(f"jira_{k}") for k in ("key", "type", "status", "phase") if d.fm_get(f"jira_{k}")}
    return {"$schema_version": 1, "kind": "worklist", "stage": "analyze", "int": nid,
            "title": d.fm_get("title") or "", "source": d.fm_get("source") or "", **({"jira": jira} if jira else {}),
            "rows": [{"n": int(r.num), "type": r.get("Type"), "signal": r.get("Signal"), "why": r.get("Why"),
                      "feature": r.get("Feature"), "status": r.get("Status"), "notes": r.get("Notes")} for r in rows],
            "hub_rows": mine, "features": feats, "candidates": ucs, "brs": brs, "pending": pending[-60:],
            "note_questions": note_qs, "uc_index": index, "output": "analysis"}


# ---------------------------------------------------------------------------- apply

def _render(vault, data, nid, feats, n_ucs, n_brs, down):
    L = [MARK, "", f"_{today()}_ · read against {n_ucs} use case(s) and {n_brs} rule(s) on "
         + (", ".join(f"`{f}`" for f in feats) or "no anchored feature yet"), "",
         "**What the request asks**", "", data["summary"].strip()]
    if data.get("flow"):
        L += ["", "**Requested flow, as understood**", ""] + [f"{i}. {s.strip()}" for i, s in enumerate(data["flow"], 1)]
    L += ["", "**Features and use cases this changes**", ""]
    if data["affected"]:
        L += ["| Target | Feature | Change | Where | Rows | Why |", "|---|---|---|---|---|---|"]
        for a in data["affected"]:
            tgt = a["target"]
            if tgt == "new":
                tgt = f"new: {_t(a.get('title') or '(untitled goal)', 60)}"
            else:
                p = vault.find(tgt)
                if p:
                    x = vault.load(p)
                    tgt = f"{tgt} {_t(model.title_of(x), 50)} ({x.fm_get('status') or '?'})"
            L.append(f"| {tgt} | {a.get('feature') or '—'} | {a['change']} | {', '.join(a.get('refs') or []) or '—'} | "
                     f"{', '.join('#%d' % n for n in a['note_rows']) or '—'} | {_t(a['why'], 160)} |")
    else:
        L.append("_No current use case or rule changes — the request is new ground or information only._")
    if down:
        L += ["", "**Already built on those use cases** (review once the change lands)", ""]
        L += [f"- {k} {e['id']} {_t(e['title'], 60)} — {e['status']}" + (f", built from {', '.join(e['absorbed'])}" if e.get("absorbed") else "")
              for k, e in down]
    L += ["", "**Conflicts with current requirements**", ""]
    if data["conflicts"]:
        L += ["| Rows | Conflicts with | Current requirement | This request | Severity |", "|---|---|---|---|---|"]
        for c in data["conflicts"]:
            L.append(f"| {', '.join('#%d' % n for n in c['note_rows'])} | {c['with']} | {_t(c['existing'], 160)} | "
                     f"{_t(c['incoming'], 160)} | {c['severity']} |")
        L += ["", "_A blocking conflict holds its hub row at `conflict` — transform drafts nothing from it until the "
                  "question in ## Open Questions is answered._"]
    else:
        L.append("_None found._")
    L += ["", "**Unclear against current requirements, and gaps implementation will need**", ""]
    if data["questions"]:
        label = {"unclear": "unclear", "gap": "gap", "impact": "impact"}
        L += [f"- [{label[q['kind']]}] {_t(q['text'], 300)}" + (f" — about {q['about']}" if q.get("about") else "")
              + f" ({q.get('owner') or 'client'})" for q in data["questions"]]
        L += ["", "_Each is tracked as a question in ## Open Questions — answer it there._"]
    else:
        L.append("_None._")
    return L


def apply(vault, path, dry=False):
    data = load_json(path)
    errs = jsonschema_lite.check(data, "analysis")
    if errs:
        raise EngineError(f"{os.path.basename(path)} fails the analysis schema:\n  " + "\n  ".join(errs[:15]))
    nid = data["int"]
    note = vault.load_id(nid)
    if (note.fm_get("status") or "") == "withdrawn":
        raise EngineError(f"{nid} is withdrawn — its analysis is closed")
    have = {int(r.num): r for r in model.note_rows(note)}
    for grp in [a["note_rows"] for a in data["affected"]] + [c["note_rows"] for c in data["conflicts"]] + \
               [q.get("note_rows") or [] for q in data["questions"]]:
        bad = [n for n in grp if n not in have]
        if bad:
            raise EngineError(f"{nid} has no row #{bad[0]} — the analysis cites only rows on the note")
    for a in data["affected"]:
        if a["target"] != "new" and not vault.find(a["target"]):
            raise EngineError(f"affected target {a['target']} does not exist — a new goal is target 'new'")
    for c in data["conflicts"]:
        ref = c["with"].split()[0]
        if re.match(r"^(UC|BR|INT)-\d+$", ref) and not vault.find(ref):
            raise EngineError(f"conflict with {ref}: no such artifact")
    res = {"int": nid, "affected": len(data["affected"]), "conflicts": len(data["conflicts"]),
           "blocking": 0, "questions_added": 0, "rows_flagged": [], "status": None}

    # questions → ## Open Questions (add-only, de-duplicated against what is already there)
    from .notes import _add_note_question
    s = note.section("Open Questions")
    before = len(questions_in(note, s.start, s.end)) if s else 0
    for c in data["conflicts"]:
        rows = ", ".join(f"#{n}" for n in c["note_rows"])
        _add_note_question(note, {"text": f"{c['question'].strip()} (conflict: {nid} {rows} vs {c['with']})",
                                  "owner": c.get("owner") or "client"})
    for q in data["questions"]:
        tag = f" ({q['kind']}: {q['about']})" if q.get("about") else ""
        _add_note_question(note, {"text": q["text"].strip() + tag, "owner": q.get("owner") or "client"})
    s = note.section("Open Questions")
    res["questions_added"] = (len(questions_in(note, s.start, s.end)) if s else 0) - before

    # blocking conflicts hold the note row and its hub row(s)
    from .hub import set_row
    hubs = {}
    for c in data["conflicts"]:
        if c["severity"] != "blocking":
            continue
        res["blocking"] += 1
        flag = f"conflicts with {c['with']} — see {nid} ## Analysis"
        for n in c["note_rows"]:
            r = {int(x.num): x for x in model.note_rows(note)}[n]
            if (r.get("Status") or "") in ("new", "question", ""):
                cells = list(r.cells) + [""] * (8 - len(r.cells))
                cells[6] = "conflict"
                cells[7] = "; ".join(x for x in (cells[7].strip(), flag) if x and flag not in cells[7])
                note.set_row(r.idx, cells)
        for slug, sd, hr in _note_hub_rows(vault, nid):
            if not (_row_nums(hr, nid) & set(c["note_rows"])):
                continue
            sd = hubs.setdefault(slug, sd)
            hr = {x.num: x for x in model.signal_rows(sd)}[hr.num]
            if hr.status in ("new", "held"):
                set_row(sd, hr, "conflict", None, flag)
                res["rows_flagged"].append(f"{slug} #{hr.num}")
    for sd in hubs.values():
        if dry:
            vault.forget(sd.path)
        else:
            vault.write(sd)

    # ## Analysis — regenerated whole, with the downstream artifacts built on the directly hit UCs
    from . import impact
    direct = {a["target"]: set(a.get("refs") or []) for a in data["affected"] if a["target"].startswith("UC-")}
    brs = [a["target"] for a in data["affected"] if a["target"].startswith("BR-")]
    down = []
    if direct or brs:
        w = impact.walk(vault, ucs=direct, brs=brs)
        down = [("UX", e) for e in w["ux"]] + [("Epic", e) for e in w["epics"]] + [("Story", e) for e in w["stories"]]
    feats = list(dict.fromkeys([a["feature"] for a in data["affected"] if a.get("feature")] +
                               [f for r in have.values() for f in re.split(r"\s*/\s*", r.get("Feature") or "")
                                if f and not f.startswith("unresolved") and os.path.exists(vault.hub_path(f))]))
    n_ucs = sum(1 for p in vault.uc_paths() if set([vault.load(p).fm_get("primary_feature")] + vault.load(p).fm_list("features")) & set(feats))
    n_brs = len({b for f in feats for b in vault.load(vault.hub_path(f)).fm_list("br")})
    body = [""] + _render(vault, data, nid, feats, n_ucs, n_brs, down) + [""]
    if note.section("Analysis") is not None:
        note.replace_body("Analysis", body)
    elif note.section("Impact") is not None:
        note.insert_section("Analysis", body[1:], before="Impact")
    else:
        note.insert_section("Analysis", body[1:], after="Open Questions")
    note.fm_set("analysed", today())

    # status: a new open question parks the note, exactly like a filer question
    s = note.section("Open Questions")
    open_q = [q for q in questions_in(note, s.start, s.end) if not q.checked] if s else []
    st = note.fm_get("status") or "in-review"
    if open_q and st == "in-review":
        st = "needs-clarification"
        note.fm_set("status", st)
    res["status"] = st
    touch_updated(note)
    if dry:
        note.verify()
        vault.forget(note.path)
    else:
        vault.write(note)
        os.makedirs(vault.impact_dir, exist_ok=True)
        with open(os.path.join(vault.impact_dir, f"{nid}.analysis.json"), "w", encoding="utf-8") as f:
            json.dump(dict(data, generated=today()), f, indent=2, ensure_ascii=False)
            f.write("\n")
    return res


# ---------------------------------------------------------------------------- withdraw

def _only_this_note(text, nid):
    ints = set(re.findall(r"\bINT-\d+\b", text))
    return ints == {nid}


def withdraw(vault, nid, reason, by=None, dry=False):
    from . import ledger
    from .hub import set_row
    from .impact import _dests
    from .notes import _tick
    reason = (reason or "").strip()
    if not reason:
        raise EngineError("note withdraw: --reason is required — the team must be able to read why it was removed")
    note = vault.load_id(nid)
    if (note.fm_get("type") or "") != "intake":
        raise EngineError(f"{nid} is not an intake note")
    if (note.fm_get("source") or "") != "jira":
        raise EngineError(f"{nid} is a {note.fm_get('source') or 'non-ticket'} note — only a ticket is withdrawn whole. "
                          "A meeting or email covers many things: to drop a feature the client no longer wants, run "
                          "`bigin feature withdraw <slug> --reason …`; a single dropped point is a new signal "
                          "that transform supersedes")
    when = today()
    if (note.fm_get("status") or "") == "withdrawn":
        return {"int": nid, "already": True, "withdrawn": note.fm_get("withdrawn") or "", "rows": {}}
    tag = f"{nid} withdrawn {when}: {_t(reason, 120)}"
    res = {"int": nid, "reason": reason, "date": when, "rows": {"withdrawn": [], "retract": [], "mixed": [],
           "kept": []}, "changesets_superseded": [], "questions_closed": [], "retract_ucs": []}

    # 1 — staged change sets in the ledger: superseded, never applied
    open_sets = [e for e in ledger.entries(vault, state="open")
                 if ((e["changeset"].get("trace") or {}).get("int") == nid
                     or nid in ((e["changeset"].get("trace") or {}).get("ints") or []))]
    if open_sets:
        res["changesets_superseded"] = [e["id"] for e in open_sets]
        if not dry:
            ledger.supersede(vault, res["changesets_superseded"], f"source {tag}")

    # 2 — hub rows
    by_hub = {}
    for slug, sd, r in _note_hub_rows(vault, nid):
        by_hub.setdefault(slug, sd)
    for slug, sd in by_hub.items():
        for r in [x for x in model.signal_rows(sd) if nid in _cites(x)]:
            r = {x.num: x for x in model.signal_rows(sd)}[r.num]
            key = f"{slug} #{r.num}"
            if _cites(r) - {nid}:
                set_row(sd, r, None, None, f"partly withdrawn — {tag}; review the rest")
                res["rows"]["mixed"].append(key)
            elif r.status in UNPROCESSED or r.status == "staged":
                set_row(sd, r, "withdrawn", None, f"withdrawn — {tag}")
                res["rows"]["withdrawn"].append(key)
            elif r.status == "applied":
                set_row(sd, r, "retract", None, f"retract — {tag}; take it out of {r.destination or 'its destination'}")
                res["rows"]["retract"].append(key)
                ucs, brs = _dests(r.destination)
                res["retract_ucs"] += [u for u in list(ucs) + sorted(brs) if u not in res["retract_ucs"]]
            else:
                res["rows"]["kept"].append(f"{key} ({r.status})")
        if dry:
            vault.forget(sd.path)
        else:
            vault.write(sd)

    # 3 — questions this note alone raised on a UC / BR are no longer needed
    for p in list(vault.uc_paths()) + list(vault.br_paths()):
        d = vault.load(p)
        closed = []
        for q in model.open_questions(d):
            if nid in q.text and _only_this_note(q.text, nid):
                if _tick(d, q.text, f"Not needed — {tag}"):
                    closed.append(d.id)
        if closed:
            append_changelog(d, f"- {when} — bigin note withdraw: {len(closed)} open question(s) raised by {nid} closed "
                                f"(source withdrawn: {_t(reason, 120)})")
            touch_updated(d)
            res["questions_closed"] += closed
            if dry:
                d.verify()
                vault.forget(d.path)
            else:
                vault.write(d)

    # 4 — the note itself: rows, status, the ## Withdrawal record (history kept, nothing deleted)
    for r in model.note_rows(note):
        if (r.get("Status") or "") in ("", "new", "question", "conflict"):
            cells = list(r.cells) + [""] * (8 - len(r.cells))
            cells[6] = "withdrawn"
            note.set_row(r.idx, cells)
    rr = res["rows"]
    body = [WMARK, "", f"**Withdrawn {when}**" + (f" by {by}" if by else "") + f" — {reason}", "",
            f"- hub rows closed: {', '.join(rr['withdrawn']) or 'none'}",
            f"- applied to the spec, to be retracted by the next transform run: {', '.join(rr['retract']) or 'none'}"
            + (f" (on {', '.join(res['retract_ucs'])})" if res["retract_ucs"] else ""),
            f"- staged change sets superseded: {', '.join(res['changesets_superseded']) or 'none'}",
            f"- open questions closed: {', '.join(sorted(set(res['questions_closed']))) or 'none'}"]
    if rr["mixed"]:
        body.append(f"- rows that also cite another note — review by hand: {', '.join(rr['mixed'])}")
    body.append("")
    if note.section("Withdrawal") is not None:
        note.replace_body("Withdrawal", [""] + body)
    else:
        note.insert_section("Withdrawal", body, before="Raw")
    note.fm_set("status", "withdrawn")
    note.fm_set("withdrawn", when)
    note.fm_set("withdrawn_reason", reason)
    touch_updated(note)
    if dry:
        note.verify()
        vault.forget(note.path)
    else:
        vault.write(note)
        if by_hub:
            from . import hub as hubmod
            ix = hubmod.Index(vault)
            for slug in by_hub:
                hubmod.refresh(vault, slug, ix)
    return res


def render_withdraw(res):
    if res.get("already"):
        return f"{res['int']}: already withdrawn ({res['withdrawn']})"
    r = res["rows"]
    lines = [f"{res['int']} withdrawn {res['date']}: {len(r['withdrawn'])} hub row(s) closed · "
             f"{len(r['retract'])} to retract · {len(res['changesets_superseded'])} staged change set(s) superseded · "
             f"{len(res['questions_closed'])} question(s) closed"]
    if r["retract"]:
        lines.append(f"  retract (next /bigin-transform-signal): {', '.join(r['retract'])} — on {', '.join(res['retract_ucs'])}")
    if r["mixed"]:
        lines.append(f"  review by hand (cite another note too): {', '.join(r['mixed'])}")
    return "\n".join(lines)


def render(res):
    return (f"{res['int']}: analysis written · {res['affected']} affected · {res['conflicts']} conflict(s) "
            f"({res['blocking']} blocking{', held: ' + ', '.join(res['rows_flagged']) if res['rows_flagged'] else ''}) · "
            f"{res['questions_added']} question(s) added · status {res['status']}")


# ---------------------------------------------------------------------------- withdraw a whole feature

FMARK = "<!-- engine-owned: written by `bigin feature withdraw` — the client removed this feature; nothing below is a live requirement -->"


def _cells(line):
    from .vault import cell_value, split_cells
    return [cell_value(x) for x in split_cells(line)]


def _features_table(vault):
    from .vault import find_tables
    fd = vault.load(vault.features_file)
    for t in find_tables(fd, fd.body_start, len(fd.lines)):
        if t.col("Slug") is not None and t.col("Status") is not None:
            return fd, t
    raise EngineError("FEATURES.md has no Slug | Status table")


def _remove_artifact(vault, d, tag, by, dry):
    """status → removed (human-gated: the human ran the command), version bumped so everything built on it
    goes stale, open questions closed, and the reason on the Changelog."""
    from .edit import bump_version
    from .notes import _tick
    was = d.fm_get("status") or "draft"
    for q in model.open_questions(d):
        _tick(d, q.text, f"Not needed — {tag}")
    ver = bump_version(d)
    d.fm_set("status", "removed")
    append_changelog(d, f"- {ver} ({today()}) — bigin feature withdraw: Status {was} → removed — {tag}"
                        + (f" (by {by})" if by else "") + ". Not deleted: reinstate by setting it back to draft.")
    touch_updated(d)
    if dry:
        d.verify()
        vault.forget(d.path)
    else:
        vault.write(d)


def withdraw_feature(vault, slug, reason, by=None, dry=False):
    """The client dropped a whole feature (too costly, no longer fits the market). FEATURES.md → out-of-scope;
    every UC it owns and every BR it governs → removed, unless another live feature still uses it (then only
    this feature's content is retracted); its Signal Log rows closed (withdrawn) or, where they put content
    into a UC that stays, retract; its staged change sets superseded; every UX spec / epic / story built on a
    removed UC flagged stale by the cascade. Future intake for the slug is rejected by the filer
    (out-of-scope — skipped). Nothing is deleted."""
    from . import cascade, ledger
    from . import hub as hubmod
    from .hub import set_row
    from .impact import _dests
    reason = (reason or "").strip()
    if not reason:
        raise EngineError("feature withdraw: --reason is required — the team must be able to read why it was removed")
    fd, t = _features_table(vault)
    sc, stc, nc = t.col("Slug"), t.col("Status"), t.col("Notes")
    row_cells = {i: _cells(fd.lines[i]) for i in t.row_idxs}
    frow = next((i for i, c in row_cells.items() if len(c) > sc and c[sc] == slug), None)
    if frow is None:
        raise EngineError(f"'{slug}' is not a FEATURES.md slug")
    cells = list(row_cells[frow])
    when = today()
    hub_exists = os.path.exists(vault.hub_path(slug))
    hdoc = vault.load(vault.hub_path(slug)) if hub_exists else None
    if cells[stc] == "out-of-scope" and (hdoc is None or hdoc.fm_get("withdrawn")):
        return {"feature": slug, "already": True, "withdrawn": hdoc.fm_get("withdrawn") if hdoc else ""}
    tag = f"feature {slug} withdrawn {when}: {_t(reason, 120)}"
    res = {"feature": slug, "reason": reason, "date": when, "removed": [], "kept": [], "changesets_superseded": [],
           "rows": {"withdrawn": [], "retract": []}, "note_rows": [], "stale": []}

    live = {c[sc] for c in row_cells.values() if len(c) > max(sc, stc) and c[sc] != slug and c[stc] != "out-of-scope"}

    # 1 — use cases this feature owns
    removed = set()
    ucs = {}
    for p in vault.uc_paths():
        u = vault.load(p)
        if u.id:
            ucs[u.id] = u
    for uid, u in sorted(ucs.items()):
        if u.fm_get("primary_feature") != slug or (u.fm_get("status") or "") in ("removed", "consolidated"):
            continue
        others = sorted(f for f in u.fm_list("features") if f != slug and f in live)
        if others:
            res["kept"].append(f"{uid} (also serves {', '.join(others)} — only {slug}'s content is retracted)")
            continue
        _remove_artifact(vault, u, tag, by, dry)
        removed.add(uid)
    # 2 — rules it governs, unless a use case that stays still enforces them
    for p in vault.br_paths():
        b = vault.load(p)
        if not b.id or b.fm_get("feature") != slug or (b.fm_get("status") or "") == "removed":
            continue
        users = {x for x, u in ucs.items() if (b.id in u.fm_list("brs") or b.id in model.s4_brs(u))
                 and x not in removed and (u.fm_get("status") or "") != "removed"} | \
                ({x for x in b.fm_list("uc") if x in ucs and x not in removed and (ucs[x].fm_get("status") or "") != "removed"})
        if users:
            res["kept"].append(f"{b.id} (still enforced by {', '.join(sorted(users))})")
            continue
        _remove_artifact(vault, b, tag, by, dry)
        removed.add(b.id)
    res["removed"] = sorted(removed)

    # 3 — change sets waiting in the ledger: from this hub, or onto a removed artifact
    open_sets = [e for e in ledger.entries(vault, state="open")
                 if (e["changeset"].get("trace") or {}).get("hub") == slug or e.get("artifact") in removed]
    if open_sets:
        res["changesets_superseded"] = [e["id"] for e in open_sets]
        if not dry:
            ledger.supersede(vault, res["changesets_superseded"], tag)

    # 4 — the feature's Signal Log
    ints = set()
    sd = model.signal_doc(vault, slug) if hub_exists else None
    for r in [x for x in model.signal_rows(sd)] if sd else []:
        r = {x.num: x for x in model.signal_rows(sd)}[r.num]
        ints |= _cites(r)
        if r.status in UNPROCESSED or r.status == "staged":
            set_row(sd, r, "withdrawn", None, f"withdrawn — {tag}")
            res["rows"]["withdrawn"].append(f"#{r.num}")
        elif r.status in ("applied", "retract"):
            u, b = _dests(r.destination)
            targets = set(u) | set(b)
            if targets and targets <= removed:
                set_row(sd, r, "withdrawn", None, f"withdrawn — removed with {', '.join(sorted(targets))}; {tag}")
                res["rows"]["withdrawn"].append(f"#{r.num}")
            elif r.status == "applied":
                set_row(sd, r, "retract", None, f"retract — {tag}; take it out of {r.destination or 'its destination'}")
                res["rows"]["retract"].append(f"#{r.num}")
    if sd is not None and sd is not hdoc:
        if dry:
            vault.forget(sd.path)
        else:
            vault.write(sd)

    # 5 — the intake notes' raw records: rows filed to this feature are closed (the notes themselves stay live)
    for nid in sorted(ints):
        if not vault.find(nid):
            continue
        n = vault.load_id(nid)
        hit = False
        for r in model.note_rows(n):
            if (r.get("Feature") or "").strip() == slug and (r.get("Status") or "") in ("", "new", "question", "conflict"):
                c = list(r.cells) + [""] * (8 - len(r.cells))
                c[6] = "withdrawn"
                c[7] = "; ".join(x for x in (c[7].strip(), f"feature {slug} withdrawn {when}") if x)
                n.set_row(r.idx, c)
                res["note_rows"].append(f"{nid} #{r.num}")
                hit = True
        if hit:
            touch_updated(n)
            if dry:
                n.verify()
                vault.forget(n.path)
            else:
                vault.write(n)

    # 6 — FEATURES.md and the hub
    if nc is not None:
        while len(cells) <= max(stc, nc):
            cells.append("")
        cells[nc] = "; ".join(x for x in (cells[nc], f"withdrawn {when}: {_t(reason, 120)}") if x)
    cells[stc] = "out-of-scope"
    from .vault import render_row
    fd.splice(frow, frow + 1, [render_row(cells)])
    if dry:
        fd.verify()
        vault.forget(fd.path)
    else:
        vault.write(fd)
    if hdoc is not None:
        hdoc.fm_set("status", "out-of-scope")
        hdoc.fm_set("withdrawn", when)
        hdoc.fm_set("withdrawn_reason", reason)
        r = res["rows"]
        body = [FMARK, "", f"**Withdrawn {when}**" + (f" by {by}" if by else "") + f" — {reason}", "",
                f"- removed: {', '.join(res['removed']) or 'none'}",
                f"- kept (another live feature uses it): {'; '.join(res['kept']) or 'none'}",
                f"- Signal Log rows closed: {', '.join(r['withdrawn']) or 'none'} · to retract by the next "
                f"transform run: {', '.join(r['retract']) or 'none'}",
                f"- staged change sets superseded: {', '.join(res['changesets_superseded']) or 'none'}",
                "- new intake for this feature is rejected at filing (`out-of-scope — skipped`); reinstate by setting "
                "FEATURES.md back to committed and each removed UC/BR back to draft", ""]
        if hdoc.section("Withdrawal") is not None:
            hdoc.replace_body("Withdrawal", [""] + body)
        else:
            hdoc.insert_section("Withdrawal", body, before="Notes / History" if hdoc.section("Notes / History") else None)
        touch_updated(hdoc)
        if dry:
            hdoc.verify()
            vault.forget(hdoc.path)
        else:
            vault.write(hdoc)
    if not dry:
        if hub_exists:
            hubmod.refresh(vault, slug, hubmod.Index(vault))
        res["stale"] = [c["id"] for c in cascade.run(vault)]
    return res


def render_withdraw_feature(res):
    if res.get("already"):
        return f"{res['feature']}: already withdrawn ({res['withdrawn']})"
    r = res["rows"]
    lines = [f"feature {res['feature']} withdrawn {res['date']}: removed {', '.join(res['removed']) or 'nothing'} · "
             f"{len(r['withdrawn'])} row(s) closed · {len(r['retract'])} to retract · "
             f"{len(res['changesets_superseded'])} staged change set(s) superseded · {len(res['note_rows'])} note row(s) closed"]
    if res["kept"]:
        lines.append("  kept (still used elsewhere): " + "; ".join(res["kept"]))
    if r["retract"]:
        lines.append(f"  retract (next /bigin-transform-signal): {res['feature']} {', '.join(r['retract'])}")
    if res["stale"]:
        lines.append("  now stale (built on a removed use case): " + ", ".join(res["stale"]))
    return "\n".join(lines)
