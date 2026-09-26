"""Codebase-mode intake — rule cards become INT notes and hub rows with no LLM call.

    bigin intake codebase --cards <path> [--assignment <map.json>] [--group-by capability]
                          [--unmapped-out <task.in.json>]

Accepted card formats (docs/CODEBASE-INTAKE.md):
  * ``code-modernization:modernize-extract-rules`` output — ``analysis/_rules-store.json``:
    ``{"rules": {<key>: {name, category, priority, source, plainEnglish, given, when, then,
    suspectedDefect?, smeQuestion?, _xr?}}}``; the card id is ``_xr`` when present, else the key.
  * a JSON list of generic cards (``schema/rule-card.json``: id, plainEnglish, …).
  * a CSV with a header row using the same field names.

Per group (capability, feature, group, or none): one INT note (``source: codebase``, provenance
header, the asymmetry warning), the rule pack as its attachment, and ``## Extracted signals`` written
directly — one ``decision`` row per card with its id verbatim and the citation as Source, plus a
separate ``problem`` row per suspected defect and a ``question`` row per SME question. Filing groups
rows by (feature, card theme) deterministically and writes them through the same engine path as a
signal-filer's filing.json. Only rows with no feature (or an ambiguous one) are left for the LLM —
written to ``--unmapped-out`` as one filer task.
"""
import csv
import json
import os
import re

from .. import jsonschema_lite, model
from ..ids import mint_int
from ..notes import file_apply
from ..util import EngineError, dump_json, load_json, today
from ..vault import find_tables

WARNING = ("**As-built, from code.** Each card below was mined from the repositories and cites the code it "
           "describes. A card records what the code does today — never what it should do. A `Suspected defect` "
           "is an observation, not a change request; an `SME question` stays a question. **Asymmetry warning:** "
           "the same rule can differ per surface (web, mobile, API, console); a card speaks only for the surface "
           "it cites — never merge two surfaces into one statement.")


def load_cards(path):
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8") as f:
            cards = [dict(r) for r in csv.DictReader(f)]
    else:
        data = load_json(path)
        if isinstance(data, dict) and "rules" in data:
            cards = []
            for k, r in data["rules"].items():
                c = dict(r)
                c["id"] = r.get("_xr") or r.get("id") or k
                cards.append(c)
        elif isinstance(data, list):
            cards = data
        else:
            raise EngineError(f"{path}: not a rule-card file (want a rules-store, a list, or a CSV)")
    schema = jsonschema_lite.load("rule-card")
    bad = []
    for c in cards:
        errs = jsonschema_lite.validate({k: v for k, v in c.items() if k in schema["properties"] and v not in (None,)}, schema)
        if errs:
            bad.append(f"{c.get('id', '?')}: {errs[0]}")
    if bad:
        raise EngineError("rule cards fail schema/rule-card.json:\n  " + "\n  ".join(bad[:10]))
    return sorted(cards, key=lambda c: str(c["id"]))


def _features(vault):
    out = []
    if os.path.exists(vault.features_file):
        fd = vault.load(vault.features_file)
        for t in find_tables(fd, fd.body_start, len(fd.lines)):
            sc, nc, notes = t.col("Slug"), t.col("Feature"), t.col("Notes")
            if sc is None:
                continue
            for r in t.rows():
                if len(r) > sc:
                    out.append({"slug": r[sc], "name": r[nc] if nc is not None and len(r) > nc else "",
                                "notes": r[notes] if notes is not None and len(r) > notes else "",
                                "caps": re.findall(r"\bC\d+(?:\.\d+)?\b", " ".join(r))})
    return out


def map_feature(card, assignment, feats):
    """(slug | None, basis). Assignment first, then the card's own feature/capability, then path heuristics."""
    slugs = {f["slug"] for f in feats}
    a = (assignment or {}).get(card["id"])
    if a:
        slug = a.get("slug") if isinstance(a, dict) else a
        if a.get("alt") if isinstance(a, dict) else False:
            return None, "ambiguous (assignment lists an alternative)"
        if slug in slugs:
            return slug, "assignment"
    if card.get("feature") in slugs:
        return card["feature"], "card"
    cap = card.get("capability") or card.get("cap")
    if cap:
        hits = [f["slug"] for f in feats if cap in f["caps"]]
        if len(hits) == 1:
            return hits[0], "capability"
    src = (card.get("source") or "").lower()
    words = set(re.findall(r"[a-z]+", src))
    hits = [f["slug"] for f in feats if set(f["slug"].split("-")) <= words or f["slug"].replace("-", "") in src.replace("_", "")]
    if len(hits) == 1:
        return hits[0], "path"
    return None, "unmapped" if not hits else f"ambiguous ({' / '.join(hits)})"


def _theme(card):
    return (card.get("capability") or card.get("cap") or "") + " · " + (card.get("category") or "rule")


def _pack(cards, title):
    lines = [f"# {title}", "", WARNING, ""]
    for c in cards:
        lines += [f"### `{c['id']}` · {c.get('name', '')}".rstrip(), "",
                  f"- {c.get('priority', '')} · {c.get('category', '')} · confidence {c.get('confidence', 'not stated')}".strip(),
                  f"- Cites: `{c.get('source', 'not stated')}`", "", c.get("plainEnglish", "")]
        for k in ("given", "when", "then"):
            if c.get(k):
                lines.append(f"- **{k.capitalize()}** {c[k]}")
        if c.get("suspectedDefect"):
            lines.append(f"- **Suspected defect:** {c['suspectedDefect']}")
        if c.get("smeQuestion"):
            lines.append(f"- **SME question:** {c['smeQuestion']}")
        lines.append("")
    return "\n".join(lines)


def intake(vault, cards_path, assignment=None, group_by="capability", title=None, dry=False, unmapped_out=None):
    cards = load_cards(cards_path)
    asg = load_json(assignment) if assignment else {}
    feats = _features(vault)
    for c in cards:
        a = asg.get(c["id"]) if isinstance(asg.get(c["id"]), dict) else {}
        c.setdefault("capability", a.get("cap") or a.get("capability") or c.get("capability"))
        c["_slug"], c["_basis"] = map_feature(c, asg, feats)
    # skip cards already imported (idempotent re-run): their id is in some note's signal table
    seen = set()
    for p in vault.note_paths():
        d = vault.load(p)
        for r in model.note_rows(d):
            seen |= set(re.findall(r"`([^`]+)`", r.get("Signal"))[:1])
    fresh = [c for c in cards if c["id"] not in seen]
    groups = {}
    for c in fresh:
        key = {"capability": c.get("capability") or c["_slug"] or "unmapped", "feature": c["_slug"] or "unmapped",
               "group": (asg.get(c["id"]) or {}).get("group") if isinstance(asg.get(c["id"]), dict) else "all",
               "none": "all"}[group_by] or "all"
        groups.setdefault(key, []).append(c)
    res = {"cards": len(cards), "skipped_already_imported": len(cards) - len(fresh), "notes": [], "hub_rows": 0,
           "unmapped": 0, "llm_rows": 0}
    unmapped_rows = []
    for key, cs in sorted(groups.items()):
        t = title or f"{key} · mined business rules ({len(cs)}), as-built from the codebase"
        slugs = sorted({c["_slug"] for c in cs if c["_slug"]})
        if dry:
            res["notes"].append({"id": "INT-(next)", "group": key, "cards": len(cs), "features": slugs})
            res["unmapped"] += sum(1 for c in cs if not c["_slug"])
            continue
        spec = {"title": t, "kind": "requirement", "source": "codebase", "status": "raw",
                "source_ref": f"{os.path.basename(cards_path)} — group {key}, imported {today()}",
                "declared_features": slugs, "fm": {"grounding": "codebase"},
                "blocks": [{"kind": "attachment", "ref": "rule pack (see attachments)", "text": WARNING}]}
        nid, npath = mint_int(vault, spec)
        att_rel = f"00-Inbox/_attachments/{nid}/rule-pack.md"
        att = os.path.join(vault.root, att_rel)
        os.makedirs(os.path.dirname(att), exist_ok=True)
        with open(att, "w", encoding="utf-8") as f:
            f.write(_pack(cs, t) + "\n")
        note = vault.load(npath)
        note.fm_set("attachments", [att_rel])
        note.fm_set("raw_sources", [f'"SRC-1 · attachment · {att_rel}"'])
        rows, meta = [], []
        for c in cs:
            cite = f"SRC-1 · rule pack · `{c.get('source', 'not stated')}`"
            feat = c["_slug"] or ("unresolved — none found" if c["_basis"] == "unmapped" else
                                  "unresolved — candidates: " + c["_basis"].split("(", 1)[-1].rstrip(")"))
            rows.append(["decision", f"`{c['id']}` — {c.get('plainEnglish', '').strip()}", "", cite, c, "decision"])
            if c.get("suspectedDefect"):
                rows.append(["problem", f"`{c['id']}` — suspected defect: {c['suspectedDefect'].strip()}", "", cite, c, "problem"])
            if c.get("smeQuestion"):
                rows.append(["question", f"`{c['id']}` — SME question: {c['smeQuestion'].strip()}", "", cite, c, "question"])
        from ..notes import _append_rows
        added = _append_rows(note, [{"type": r[0], "signal": r[1], "why": r[2], "source": r[3]} for r in rows])
        vault.write(note)
        # deterministic filing: (feature, theme) → one hub row; question rows file alone
        filing = {"$schema_version": 1, "kind": "filing", "int": nid, "rows": [], "hub_rows": [], "questions": []}
        themes = {}
        for n, r in zip(added, rows):
            c = r[4]
            if not c["_slug"]:
                filing["rows"].append({"n": n, "feature": ("unresolved — none found" if c["_basis"] == "unmapped"
                                                           else "unresolved — candidates: " + c["_basis"].split("(", 1)[-1].rstrip(")")),
                                       "status": "question", "notes": f"codebase intake: {c['_basis']}"})
                unmapped_rows.append({"int": nid, "n": n, "id": c["id"], "signal": r[1], "source": r[3], "basis": c["_basis"]})
                res["unmapped"] += 1
                continue
            status = "question" if r[5] == "question" else "new"
            filing["rows"].append({"n": n, "feature": c["_slug"], "status": status})
            if status == "question":
                filing["hub_rows"].append({"hub": c["_slug"], "signal": r[1], "type": "question", "note_rows": [n],
                                           "cite": "SRC-1 rule pack", "status": "question"})
                filing["questions"].append({"where": "hub", "hub": c["_slug"], "owner": "team",
                                            "text": re.sub(r"^`[^`]+` — SME question:\s*", "", r[1]) + f" ({c['id']})",
                                            "ref": f"{nid} #{n}"})
                continue
            themes.setdefault((c["_slug"], _theme(c), r[5]), []).append((n, r))
        for (slug, theme, typ), members in themes.items():
            if len(members) == 1:
                sig = members[0][1][1]
            else:
                label = theme.strip(" ·") or "Rules"
                sig = f"**{label}{' — suspected defects' if typ == 'problem' else ''}** — " + "; ".join(m[1][1] for m in members)
            filing["hub_rows"].append({"hub": slug, "signal": sig, "type": typ, "note_rows": [m[0] for m in members],
                                       "cite": "SRC-1 rule pack", "status": "new"})
        tmp = os.path.join(vault.runs_dir, "_intake", f"{nid}.filing.json")
        dump_json(filing, tmp)
        fres = file_apply(vault, tmp)
        res["hub_rows"] += sum(len(v) for v in fres["hub_rows"].values())
        res["notes"].append({"id": nid, "group": key, "cards": len(cs), "rows": len(added), "features": slugs,
                             "status": fres["status"]})
    if unmapped_out and unmapped_rows:
        dump_json({"$schema_version": 1, "kind": "worklist", "stage": "file", "rows": unmapped_rows,
                   "features": [{"slug": f["slug"], "name": f["name"]} for f in feats], "output": "filing",
                   "note": "codebase intake left these rows unmapped; the filer anchors them — nothing else"}, unmapped_out)
        res["llm_rows"] = len(unmapped_rows)
    return res


def render(res):
    lines = [f"codebase intake: {res['cards']} card(s), {res['skipped_already_imported']} already imported"]
    for n in res["notes"]:
        lines.append(f"  {n['id']} [{n['group']}] {n['cards']} card(s) → {', '.join(n['features']) or 'no feature'}"
                     + (f" · status {n['status']}" if n.get("status") else ""))
    lines.append(f"hub rows filed: {res['hub_rows']} · unmapped rows left for the filer: {res['unmapped']}")
    return "\n".join(lines)
