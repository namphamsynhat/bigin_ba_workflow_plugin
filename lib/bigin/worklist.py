"""Worklists — compact JSON task inputs, so an agent reads what its task needs and nothing else
(restructure plan § B.5). Whole files are never handed to an agent: rows, anchor texts with their
``sha``, section excerpts, candidate ids and titles.
"""
import os
import re

from . import model
from .util import EngineError, sha
from .vault import strip_comments

SUMMARY_FIELDS = ("Primary Actor", "Secondary Actor(s)", "Business Need / Goal", "Trigger")


def _clean(text):
    t = strip_comments(text or "")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _fm(d, keys):
    return {k: d.fm_get(k) for k in keys if d.fm and k in d.fm}


def uc_card(vault, d, full=False):
    from .changeset import field_value
    card = {"id": d.id, "title": model.title_of(d), **_fm(d, ("status", "primary_feature", "features", "level"))}
    card["summary"] = {f: field_value(d, "1", f) for f in SUMMARY_FIELDS if field_value(d, "1", f) is not None}
    card["steps"] = [{"id": s.id, "actor": s.actor, "system": s.system, "sha": sha(s.text), **({"dropped": True} if s.dropped else {})}
                     for s in model.steps(d)]
    card["flows"] = [{"id": f.id, "name": f.name, "sha": sha(f.text), **({"dropped": True} if f.dropped else {}),
                      **({"body": f.body} if full else {})} for f in model.flows(d)]
    card["brs"] = model.s4_brs(d)
    qs = [q.text for q in model.open_questions(d)]
    card["open_questions"] = qs if full else [q[:200] + ("…" if len(q) > 200 else "") for q in qs]
    if full:
        for f in ("Pre-conditions", "Post-conditions (success)", "Post-conditions (failure)"):
            v = field_value(d, "1", f)
            if v is not None:
                card["summary"][f] = v
        card["s4"] = [{"br": c[0], "enforced_at": c[2] if len(c) > 2 else ""} for _, c in model.s4_rows(d)]
    return card


def br_card(d, full=False):
    stmt = model.br_statement(d)
    return {"id": d.id, "title": model.title_of(d), **_fm(d, ("status", "feature", "uc")),
            "statement": stmt if full else (stmt[:400] + ("…" if len(stmt) > 400 else "")), "sha": sha(stmt),
            "open_questions": [q.text for q in model.open_questions(d)]}


def context(vault, ident, sections=None):
    """A compact slice of one artifact: frontmatter essentials + chosen sections, comments stripped."""
    p = vault.find(ident) if re.match(r"^(UC|BR|INT|EN)-\d+$", ident) else vault.hub_path(ident)
    if not p or not os.path.exists(p):
        raise EngineError(f"{ident}: no such artifact")
    d = vault.load(p)
    out = {"id": ident, "path": vault.rel(p)}
    if ident.startswith("UC"):
        out["card"] = uc_card(vault, d, full=True)
    elif ident.startswith("BR"):
        out["card"] = br_card(d, full=True)
    for key in sections or []:
        body = d.get(key.strip())
        if body is not None:
            out.setdefault("sections", {})[key.strip()] = _clean(body)
    return out


def render_context(res):
    import json
    return json.dumps(res, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------- stages

def _rows(vault, slug, statuses, only=None):
    doc = model.signal_doc(vault, slug)
    if doc is None:
        raise EngineError(f"no hub '{slug}'")
    out = []
    for r in model.signal_rows(doc):
        if only and r.num not in only:
            continue
        if not only and r.status not in statuses:
            continue
        out.append({"row": r.num, "signal": r.get("Signal"), "type": r.get("Type"), "source": r.source,
                    "status": r.status, "destination": r.destination, "notes": r.get("Notes")})
    return out


def route(vault, slug, args=None):
    only = set(args.rows.split(",")) if args is not None and getattr(args, "rows", None) else None
    rows = _rows(vault, slug, {"new", "held"}, only)
    hub = vault.load(vault.hub_path(slug))
    extra = set(args.uc.split(",")) if args is not None and getattr(args, "uc", None) else set()
    cands, index = [], []
    for p in vault.uc_paths():
        d = vault.load(p)
        feats = [d.fm_get("primary_feature")] + d.fm_list("features")
        if slug in feats or d.id in extra:
            cands.append(uc_card(vault, d))
        index.append(f"{d.id} {model.title_of(d)} [{d.fm_get('primary_feature')}]")
    brs = []
    for b in hub.fm_list("br"):
        p = vault.find(b)
        if p:
            d = vault.load(p)
            stmt = model.br_statement(d)
            # compact: the router greps a BR file only when it needs the full statement
            brs.append({"id": d.id, "title": model.title_of(d), "uc": d.fm_list("uc"), "sha": sha(stmt),
                        "statement": stmt[:160] + ("…" if len(stmt) > 160 else "")})
    return {"$schema_version": 1, "kind": "worklist", "stage": "route", "feature": slug,
            "hub": {"name": hub.fm_get("name"), "status": hub.fm_get("status")},
            "rows": rows, "candidates": cands, "brs": brs, "uc_index": index,
            "output": {"phase_a": "route", "phase_b": "changesets"}}


def adjudicate(vault, slug, args=None):
    rows = _rows(vault, slug, {"conflict", "held"})
    doc = model.signal_doc(vault, slug)
    allrows = {r.num: r for r in model.signal_rows(doc)}
    for r in rows:
        refs = sorted(set(re.findall(r"#(\d+[a-z]?)", r["notes"] or "")) & set(allrows))
        r["related"] = [{"row": n, "signal": allrows[n].get("Signal"), "status": allrows[n].status} for n in refs if n != r["row"]]
    repos = vault.project().fm_list("repos") or ([vault.config("codebase_path")] if vault.config("codebase_path") else [])
    return {"$schema_version": 1, "kind": "worklist", "stage": "adjudicate", "feature": slug, "rows": rows,
            "repos": repos, "conflict_policy": vault.config("conflict_policy", "ask"), "output": "adjudication"}


def _src_blocks(d):
    s = d.section("Raw")
    if not s:
        return []
    heads = [i for i in range(s.start, s.end) if re.match(r"^###\s+SRC-\d+", d.masked[i])]
    out = []
    for k, i in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else s.end
        m = re.match(r"^###\s+(SRC-\d+)\s*·\s*`?([^`·]*)`?\s*·\s*(.*)$", d.lines[i])
        out.append({"src": m.group(1) if m else f"SRC-{k + 1}", "kind": (m.group(2).strip() if m else ""),
                    "ref": (m.group(3).strip() if m else ""), "lines": [i + 1, end], "chars": sum(len(x) for x in d.lines[i:end])})
    return out


def _answered(d):
    """Fold-in input: this note's questions a human has answered (2-extraction.md § Fold-in runs)."""
    s = d.section("Open Questions")
    if not s:
        return []
    from .vault import questions_in
    return [{"question": q.text, "answer": q.answer} for q in questions_in(d, s.start, s.end) if q.answered]


def extract(vault, nid, args=None):
    d = vault.load_id(nid)
    rows = model.note_rows(d)
    return {"$schema_version": 1, "kind": "worklist", "stage": "extract", "int": nid, "path": vault.rel(d.path),
            "note": _fm(d, ("kind", "source", "source_ref", "declared_features", "attachments")),
            "src_blocks": _src_blocks(d), "mode": "append" if rows else "fresh",
            "answered_questions": _answered(d),
            "last_row": max([int(r.num) for r in rows] or [0]), "output": "signals",
            "read": "read ONLY the listed line ranges of the note (and attachments named in a block); never the whole note"}


def audit(vault, nid, args=None):
    d = vault.load_id(nid)
    w = extract(vault, nid)
    w["stage"] = "audit"
    w["rows"] = [{"n": int(r.num), "type": r.get("Type"), "signal": r.get("Signal"), "why": r.get("Why"),
                  "source": r.source} for r in model.note_rows(d)]
    w["output"] = "audit"
    return w


def file_(vault, nid, args=None):
    d = vault.load_id(nid)
    rows = [{"n": int(r.num), "type": r.get("Type"), "signal": r.get("Signal"), "why": r.get("Why"), "source": r.source,
             "feature": r.get("Feature"), "status": r.get("Status")} for r in model.note_rows(d)
            if not r.get("Feature").strip() or not r.get("Status").strip()]
    feats = []
    if os.path.exists(vault.features_file):
        fd = vault.load(vault.features_file)
        from .vault import find_tables
        for t in find_tables(fd, fd.body_start, len(fd.lines)):
            sc, nc, stc = t.col("Slug"), t.col("Feature"), t.col("Status")
            if sc is None:
                continue
            for r in t.rows():
                if len(r) > max(sc, nc or 0):
                    feats.append({"slug": r[sc], "name": r[nc] if nc is not None else "", "status": r[stc] if stc is not None else ""})
    hubs = {}
    for f in d.fm_list("declared_features") or []:
        sd = model.signal_doc(vault, f)
        if sd:
            rs = model.signal_rows(sd)
            hubs[f] = {"last_row": rs[-1].num if rs else "0",
                       "recent": [f"#{r.num} [{r.status}] {r.get('Signal')[:140]}" for r in rs[-25:]]}
    # Step 5b input: questions still open elsewhere that a row of this note might answer
    open_elsewhere = []
    for p in vault.note_paths():
        o = vault.load(p)
        if o.id == nid or not o.section("Open Questions"):
            continue
        s_ = o.section("Open Questions")
        from .vault import questions_in
        for q in questions_in(o, s_.start, s_.end):
            if not q.checked:
                open_elsewhere.append({"int": o.id, "question": q.text[:300]})
    for f in d.fm_list("declared_features") or []:
        hp = vault.hub_path(f)
        if os.path.exists(hp):
            hd = vault.load(hp)
            s_ = hd.section("Open Questions / Gates")
            if s_:
                from .vault import questions_in
                for q in questions_in(hd, s_.start, s_.end):
                    if not q.checked:
                        open_elsewhere.append({"hub": f, "question": q.text[:300]})
    return {"$schema_version": 1, "kind": "worklist", "stage": "file", "int": nid, "rows": rows, "features": feats,
            "declared_features": d.fm_list("declared_features"), "hubs": hubs,
            "open_questions_elsewhere": open_elsewhere[:80], "output": "filing"}


def release(vault, scope, args=None):
    from . import ledger
    items = [e for e in ledger.entries(vault, "needs-judgement")]
    out = []
    for e in items:
        ans = ledger._answer_for(vault, e)[1]
        out.append({"id": e["id"], "artifact": e["artifact"], "question": e["question"], "answer": ans,
                    "changeset": e["changeset"]})
    return {"$schema_version": 1, "kind": "worklist", "stage": "release", "items": out, "output": "verdicts"}


def split(vault, uid, args=None):
    d = vault.load_id(uid)
    return {"$schema_version": 1, "kind": "worklist", "stage": "split", "uc": uc_card(vault, d, full=True),
            "output": "changesets"}


def build(vault, stage, scope, args=None):
    fn = {"route": route, "adjudicate": adjudicate, "extract": extract, "audit": audit, "file": file_,
          "release": release, "split": split}.get(stage)
    if not fn:
        raise EngineError(f"no worklist for stage '{stage}'")
    return fn(vault, scope, args)


def summary(res):
    bits = []
    for k in ("rows", "candidates", "brs", "src_blocks", "items"):
        if k in res:
            bits.append(f"{len(res[k])} {k}")
    return ", ".join(bits) or "ok"
