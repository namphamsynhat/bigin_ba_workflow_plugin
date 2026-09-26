"""Intake-note and filing writers — the engine half of /extract-signal.

``write_signals``  signals.json (signal-extractor) → the note's ## Extracted signals table. Row ids
                   are assigned by the engine and permanent; repairs edit a row in place by #;
                   appends continue after the last #. Feature/Status are never touched here.
``apply_audit``    audit.json (signal-auditor) → appended / edited / flagged rows, same rules.
``file_apply``     filing.json (signal-filer) → note Feature/Status/Notes, themed hub Signal Log rows,
                   registers (PAIN-POINTS / ENTITIES / DESIGN-PRINCIPLES), questions, Step 5b answers,
                   and the note's status — LAST, so a crash never leaves a note looking filed.
"""
import glob
import os
import re

from . import jsonschema_lite, model
from .edit import append_changelog, question_block, same_question, touch_updated
from .ids import fmt, highest, id_lock, instantiate
from .util import EngineError, load_json, norm_ws, sort_ids, today
from .vault import find_tables, questions_in, render_row

NOTE_HEADER = "| # | Type | Signal | Why | Source | Feature | Status | Notes |"
NOTE_SEP = "|---|------|--------|-----|--------|---------|--------|-------|"


def _load(path, kind):
    data = load_json(path)
    errs = jsonschema_lite.check(data, kind)
    if errs:
        raise EngineError(f"{os.path.basename(path)} fails the {kind} schema:\n  " + "\n  ".join(errs[:15]))
    return data


def _note_table(doc):
    t = model.note_table(doc)
    if t is not None:
        return t
    s = doc.section("Extracted signals")
    if s is None:
        doc.insert_section("Extracted signals", ["", NOTE_HEADER, NOTE_SEP, ""], before="Open Questions")
    else:
        pos = s.end
        while pos > s.start and not doc.lines[pos - 1].strip():
            pos -= 1
        doc.splice(pos, pos, ["", NOTE_HEADER, NOTE_SEP])
    return model.note_table(doc)


def _cells_of(r, n):
    return [str(n), r["type"], r["signal"], r.get("why", ""), r["source"], "", "", r.get("notes", "")]


def _append_rows(doc, new_rows):
    t = _note_table(doc)
    have = model.note_rows(doc)
    last = max([int(r.num) for r in have] or [0])
    existing = {(norm_ws(r.get("Signal")), norm_ws(r.source)) for r in have}
    lines, added = [], []
    _append_rows.skipped = 0
    for r in new_rows:
        if (norm_ws(r["signal"]), norm_ws(r["source"])) in existing:
            _append_rows.skipped += 1  # re-run of the same output: reported, never silent
            continue
        last += 1
        lines.append(render_row(_cells_of(r, last)))
        added.append(last)
    if lines:
        t = model.note_table(doc)
        pos = t.row_idxs[-1] + 1 if t.row_idxs else t.sep_idx + 1
        doc.splice(pos, pos, lines)
    return added


def _edit_row(doc, n, patch):
    rows = {int(r.num): r for r in model.note_rows(doc)}
    r = rows.get(int(n))
    if r is None:
        raise EngineError(f"row #{n} does not exist — repairs never invent a row number")
    cells = list(r.cells) + [""] * (8 - len(r.cells))
    for key, col in (("type", 1), ("signal", 2), ("why", 3), ("source", 4)):
        if patch.get(key) is not None and (patch[key] != "" or key == "why"):
            cells[col] = patch[key]  # an explicit "" blanks Why (an inversion repair); other cells never blank
    if patch.get("notes"):
        cells[7] = "; ".join(x for x in (cells[7].strip(), patch["notes"]) if x and patch["notes"] not in cells[7])
    doc.set_row(r.idx, cells)


def write_signals(vault, path, dry=False):
    data = _load(path, "signals")
    doc = vault.load_id(data["int"])
    mode = data.get("mode") or ("append" if model.note_rows(doc) else "fresh")
    res = {"int": data["int"], "mode": mode, "added": [], "edited": []}
    if mode == "fresh" and model.note_rows(doc):
        raise EngineError(f"{data['int']} already has signal rows — use mode append or repair")
    if mode == "repair":
        for r in data["rows"]:
            if not r.get("n"):
                raise EngineError("repair rows need n")
            _edit_row(doc, r["n"], r)
            res["edited"].append(r["n"])
    else:
        res["added"] = _append_rows(doc, data["rows"])
        res["skipped_duplicates"] = _append_rows.skipped
    if data.get("self_audit"):
        res["audit_owed"] = bool(data["self_audit"].get("audit_owed"))
    touch_updated(doc)
    _flush(vault, doc, dry)
    return res


def apply_audit(vault, path, dry=False):
    data = _load(path, "audit")
    doc = vault.load_id(data["int"])
    res = {"int": data["int"], "added": [], "edited": [], "flagged": [], "verdict": data.get("verdict")}
    appends = [r for r in data.get("repairs") or [] if r["action"] == "append"]
    for r in data.get("repairs") or []:
        if r["action"] == "edit":
            _edit_row(doc, r["n"], r)
            res["edited"].append(r["n"])
        elif r["action"] == "flag":
            _edit_row(doc, r["n"], {"notes": "audit: " + (r.get("notes") or "unsupported by the source")})
            res["flagged"].append(r["n"])
    res["added"] = _append_rows(doc, [{"type": r.get("type", "requirement"), "signal": r.get("signal", ""),
                                       "why": r.get("why", ""), "source": r.get("source", ""),
                                       "notes": r.get("notes", "audit: added")} for r in appends])
    touch_updated(doc)
    _flush(vault, doc, dry)
    return res


# ---------------------------------------------------------------------------- filing

def _hub_for(vault, slug, dry):
    hp = vault.hub_path(slug)
    if os.path.exists(hp):
        return vault.load(hp), False
    name, status = slug, "proposed"
    if os.path.exists(vault.features_file):
        fd = vault.load(vault.features_file)
        found = False
        for t in find_tables(fd, fd.body_start, len(fd.lines)):
            sc, nc, stc = t.col("Slug"), t.col("Feature"), t.col("Status")
            for r in t.rows():
                if sc is not None and len(r) > sc and r[sc] == slug:
                    name = r[nc] if nc is not None else slug
                    status = r[stc] if stc is not None else status
                    found = True
        if not found:
            raise EngineError(f"'{slug}' is not a FEATURES.md slug — a new slug is a human's call (3-filing.md § Step 1)")
    text = instantiate(vault, "feature-hub.md", {"type": "feature-hub", "feature": slug, "name": name, "status": status,
                                                 "sources": [], "updated": today()}, name,
                       lambda b: re.sub(r"(## Changelog\n)(?:- .*\n?)*", lambda m: m.group(1) + f"- ({today()}) — hub created\n", b))
    from .vault import Doc
    d = Doc(text, hp)
    split = bool(glob.glob(os.path.join(vault.hub_dir, "*.signals.md"))) or vault.config("signal_log") == "split"
    if not dry:
        vault.create(hp, text)
        d = vault.load(hp)
        if split and d.section("Signal Log"):
            # this vault keeps Signal Logs in companion files (v1.12.0): new hubs follow suit
            from .migrate import split_signal_log
            split_signal_log(vault, only=[slug])
            d = vault.load(hp)
    return d, True


def _add_hub_row(sdoc, hr, nid, cite):
    rows = model.signal_rows(sdoc)
    src = f"{nid} " + ", ".join(f"#{n}" for n in hr["note_rows"]) + (f" — {cite}" if cite else "")
    for r in rows:
        if model.expand_int_cites(r.source) == model.expand_int_cites(src) and norm_ws(r.get("Signal")) == norm_ws(hr["signal"]):
            return r.num, False
    t = model.signal_table(sdoc)
    if t is None:
        s = sdoc.section("Signal Log")
        pos = s.end
        while pos > s.start and not sdoc.lines[pos - 1].strip():
            pos -= 1
        sdoc.splice(pos, pos, ["", "| # | Signal | Type | Source | Status | Destination | Notes |",
                               "|---|--------|------|--------|--------|--------------|-------|"])
        t = model.signal_table(sdoc)
    nums = [int(re.match(r"\d+", r.num).group(0)) for r in rows]
    n = str(max(nums or [0]) + 1)
    pos = t.row_idxs[-1] + 1 if t.row_idxs else t.sep_idx + 1
    sdoc.splice(pos, pos, [render_row([n, hr["signal"], hr["type"], src, hr["status"], "", hr.get("notes", "")])])
    return n, True


def _register_rows(vault, fname):
    p = os.path.join(vault.req, fname)
    if not os.path.exists(p):
        tpl = {"PAIN-POINTS.md": "pain-points-register.md", "ENTITIES.md": "entities-register.md",
               "DESIGN-PRINCIPLES.md": "design-principles-register.md"}[fname]
        with open(vault.template_path(tpl), encoding="utf-8") as f:
            vault.create(p, f.read())
    d = vault.load(p)
    ts = find_tables(d, d.body_start, len(d.lines))
    return d, (ts[0] if ts else None)


def _append_register(d, t, cells):
    pos = t.row_idxs[-1] + 1 if t.row_idxs else t.sep_idx + 1
    d.splice(pos, pos, [render_row(cells)])


def file_apply(vault, path, dry=False):
    data = _load(path, "filing")
    nid = data["int"]
    note = vault.load_id(nid)
    note_rows = {int(r.num): r for r in model.note_rows(note)}
    res = {"int": nid, "rows": 0, "hub_rows": {}, "questions": 0, "pp": [], "en": [], "dp": 0, "answers": 0,
           "hubs_created": [], "status": None}
    # 0 — declared-slug exception (3-filing.md): a slug the HUMAN declared at capture gets a proposed row
    declared = set(note.fm_list("declared_features"))
    for nf in data.get("new_features") or []:
        if nf["slug"] not in declared:
            raise EngineError(f"new feature '{nf['slug']}' was not declared at capture — a new slug is a human's call")
        _add_feature_row(vault, nf, nid, dry)
        res.setdefault("features_added", []).append(nf["slug"])
    # 1 — anchor columns on the note
    for r in data["rows"]:
        nr = note_rows.get(r["n"])
        if nr is None:
            raise EngineError(f"{nid} has no row #{r['n']}")
        cells = list(nr.cells) + [""] * (8 - len(nr.cells))
        cells[5], cells[6] = r["feature"].replace("|", "/"), r["status"]
        if r.get("notes") and r["notes"] not in cells[7]:
            cells[7] = "; ".join(x for x in (cells[7].strip(), r["notes"]) if x)
        note.set_row(nr.idx, cells)
        res["rows"] += 1
    note_rows = {int(r.num): r for r in model.note_rows(note)}
    # 2 — themed hub rows
    hubs = {}
    row_of = {}
    with id_lock(vault):
        for hr in data.get("hub_rows") or []:
            slug = hr["hub"]
            if slug not in hubs:
                d, created = _hub_for(vault, slug, dry)
                hubs[slug] = d
                if created:
                    res["hubs_created"].append(slug)
            hdoc = hubs[slug]
            sdoc = model.signal_doc(vault, slug) if os.path.exists(vault.signals_path(slug)) else hdoc
            first = note_rows.get(hr["note_rows"][0])
            cite = hr.get("cite") or (first.source if first else "")
            n, new = _add_hub_row(sdoc, hr, nid, cite)
            if new:
                res["hub_rows"].setdefault(slug, []).append(n)
            row_of.setdefault(slug, []).append((n, set(hr["note_rows"])))
            if hr.get("conflicts_with"):
                old = {r.num: r for r in model.signal_rows(sdoc)}.get(str(hr["conflicts_with"]))
                if old is not None and old.status not in ("superseded", "rejected"):
                    from .hub import set_row
                    set_row(sdoc, old, "conflict", None, f"conflicts with #{n}")
            if sdoc is not hdoc:
                _flush(vault, sdoc, dry)
            if hdoc.fm and nid not in hdoc.fm_list("sources"):
                hdoc.fm_set("sources", hdoc.fm_list("sources") + [nid])
            touch_updated(hdoc)
        # 3 — registers (per signal, never collapsed)
        regs = {}

        def reg(name):
            if name not in regs:
                regs[name] = _register_rows(vault, name)[0]
            d = regs[name]
            return d, find_tables(d, d.body_start, len(d.lines))[0]
        for pp in data.get("pain_points") or []:
            nr = note_rows.get(pp["n"])
            if pp.get("match"):
                ppid = pp["match"]
                pp_doc, t = reg("PAIN-POINTS.md")
                sc = t.col("Source")
                if sc is not None:
                    for i, r in zip(t.row_idxs, t.rows()):
                        if r and r[0] == pp["match"] and nid not in r[sc]:
                            r = list(r) + [""] * (len(t.header) - len(r))
                            r[sc] = ", ".join(x for x in (r[sc].strip(), f"{nid} #{pp['n']}") if x)
                            pp_doc.set_row(i, r)
                            break
            else:
                pp_doc, t = reg("PAIN-POINTS.md")
                ppid = fmt("PP", max(highest(vault, "PP"), max([int(x) for x in re.findall(r"PP-(\d+)", pp_doc.text)] or [0])) + 1)
                hdr = t.header
                cells = {"PP-###": ppid, "Statement": pp["statement"], "Status": "open",
                         "Proposed solution": pp.get("proposed_solution", ""), "Resolved by": "", "Feature": pp["feature"],
                         "Source": f"{nid} #{pp['n']}"}
                _append_register(pp_doc, t, [cells.get(h, "") for h in hdr])
                hd = hubs.get(pp["feature"]) or _hub_for(vault, pp["feature"], dry)[0]
                hubs[pp["feature"]] = hd
                pt = hd.table("Pain Points")
                if pt is not None:
                    _append_register(hd, pt, [ppid, pp["statement"], "open", pp.get("proposed_solution", ""), ""])
                res["pp"].append(ppid)
                # cite the minted id on the themed hub row(s) that cover this note row (3-filing.md § Step 4)
                for num, members in row_of.get(pp["feature"], []):
                    if pp["n"] in members:
                        sd = model.signal_doc(vault, pp["feature"]) if os.path.exists(vault.signals_path(pp["feature"])) else hd
                        r = {x.num: x for x in model.signal_rows(sd)}.get(num)
                        if r is not None and ppid not in r.get("Notes"):
                            from .hub import set_row
                            set_row(sd, r, note=ppid)
                            if sd is not hd:
                                _flush(vault, sd, dry)
            if nr is not None:
                cells = list(nr.cells) + [""] * (8 - len(nr.cells))
                tag = f"same as {ppid} — not re-minted" if pp.get("match") else ppid
                if ppid not in cells[7]:
                    cells[7] = "; ".join(x for x in (cells[7].strip(), tag) if x)
                    note.set_row(nr.idx, cells)
                    note_rows = {int(r.num): r for r in model.note_rows(note)}
        for en in data.get("entities") or []:
            en_doc, t = reg("ENTITIES.md")
            hdr = t.header
            target = None
            for i, r in zip(t.row_idxs, t.rows()):
                if (en.get("match") and r[0] == en["match"]) or (not en.get("match") and len(r) > 1 and r[1].strip().lower() == en["object"].strip().lower()):
                    target = (i, r)
                    break
            if target:
                i, r = target
                fc, ftc = t.col("Fields"), t.col("Features")
                r = list(r) + [""] * (len(hdr) - len(r))
                if fc is not None:
                    have = [x.strip() for x in r[fc].split(";") if x.strip()]
                    for f in en.get("fields") or []:
                        if f not in have:
                            have.append(f)
                    r[fc] = "; ".join(have)
                if ftc is not None and en["feature"] not in r[ftc]:
                    r[ftc] = ", ".join(x for x in (r[ftc].strip(), en["feature"]) if x)
                en_doc.set_row(i, r)
            else:
                enid = fmt("EN", max(highest(vault, "EN"), max([int(x) for x in re.findall(r"EN-(\d+)", en_doc.text)] or [0])) + 1)
                cells = {"EN-###": enid, "Entity": en["object"], "Status": "proposed",
                         "Fields (so far)": "; ".join(en.get("fields") or []), "Features": en["feature"],
                         "Notes": f"from {nid}" + (f" #{en['n']}" if en.get("n") else "")}
                _append_register(en_doc, t, [cells.get(h, "") for h in hdr])
                res["en"].append(enid)
        for dp in data.get("design_principles") or []:
            dp_doc, t = reg("DESIGN-PRINCIPLES.md")
            if any(len(r) > 1 and norm_ws(r[1]) == norm_ws(dp["principle"]) for r in t.rows()):
                continue
            nums = [int(r[0]) for r in t.rows() if r and r[0].isdigit()]
            cells = {"#": str(max(nums or [0]) + 1), "Principle": dp["principle"], "Why": dp.get("why", "not stated"),
                     "Category": dp.get("category", ""), "Source": dp.get("source", nid), "Status": "active", "Notes": ""}
            _append_register(dp_doc, t, [cells.get(h, "") for h in t.header])
            res["dp"] += 1
        for d in regs.values():
            _flush(vault, d, dry)
    # 4 — questions
    for q in data.get("questions") or []:
        if q["where"] == "note":
            _add_note_question(note, q)
        else:
            hd = hubs.get(q["hub"]) or _hub_for(vault, q["hub"], dry)[0]
            hubs[q["hub"]] = hd
            from .changeset import Outcome, add_question
            try:
                add_question(hd, "HUB", q["text"], q.get("owner"), q.get("ref") or nid)
            except Outcome:
                pass
        res["questions"] += 1
    # 5 — Step 5b answers on other notes
    for a in data.get("answers") or []:
        other = vault.load_id(a["int"])
        s = other.section("Open Questions")
        if s is None:
            continue
        for q in questions_in(other, s.start, s.end):
            if not q.checked and same_question(q.text, a["question"]):
                other.splice(q.start, q.end, question_block(q.text, answer=f"{a['answer']} (answered by {nid})",
                                                           indent=" " * q.indent, checked=True))
                res["answers"] += 1
                break
        _flush(vault, other, dry)
    for slug, hd in hubs.items():
        _flush(vault, hd, dry)
    # 6 — the note's status, LAST
    s = note.section("Open Questions")
    open_q = [q for q in questions_in(note, s.start, s.end) if not q.checked] if s else []
    st = data.get("note_status") or ("needs-clarification" if open_q else "in-review")
    note.fm_set("status", st)
    if data.get("tags"):
        note.fm_set("tags", list(dict.fromkeys(note.fm_list("tags") + data["tags"])))
    touch_updated(note)
    _flush(vault, note, dry)
    res["status"] = st
    return res


def _add_feature_row(vault, nf, nid, dry):
    fd = vault.load(vault.features_file)
    for t in find_tables(fd, fd.body_start, len(fd.lines)):
        sc = t.col("Slug")
        if sc is None:
            continue
        if any(len(r) > sc and r[sc] == nf["slug"] for r in t.rows()):
            return
        hdr = t.header
        cells = {"Slug": nf["slug"], "Feature": nf.get("name", nf["slug"]), "Status": "proposed", "Sources": nid,
                 "Notes": nf.get("scope", "declared at capture")}
        pos = t.row_idxs[-1] + 1 if t.row_idxs else t.sep_idx + 1
        fd.splice(pos, pos, [render_row([cells.get(h, "") for h in hdr])])
        _flush(vault, fd, dry)
        return


def _add_note_question(note, q):
    s = note.section("Open Questions")
    if s is None:
        note.insert_section("Open Questions", [""], before=None)
        s = note.section("Open Questions")
    for x in questions_in(note, s.start, s.end):
        if same_question(x.text, q["text"]):
            return
    text = q["text"]
    if "↦" not in text:
        text += " ↦ —"
    pos = s.end
    while pos > s.start and not note.masked[pos - 1].strip():
        pos -= 1
    note.splice(pos, pos, question_block(text, owner=q.get("owner")))


def _flush(vault, d, dry):
    if not d.changed and os.path.exists(d.path or ""):
        return
    if dry:
        d.verify() if os.path.exists(d.path or "") else None
        vault.forget(d.path)
    elif not os.path.exists(d.path):
        vault.create(d.path, d.text)
    else:
        vault.write(d)


def render(res):
    import json
    return json.dumps(res, ensure_ascii=False)
