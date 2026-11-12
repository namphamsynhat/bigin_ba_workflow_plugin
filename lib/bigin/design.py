"""The design stage's bookkeeping, done by the engine instead of by a model re-reading 40–110 KB specs.

    bigin design scope [slug|UC-###] [--run R]   Stage 1: NEW / CHANGED / CURRENT per use case, the gates,
                                                 the platform, the mode — and what a dead run left behind
    bigin worklist design <slug>                 Stage 3: the screens worker's whole requirement input
    bigin design items <slug>                    Stage 5: every requirement item, matched forward BY ID
    bigin design check <slug> [--phase wave]     Stage 3 wave check / Stage 6 Part 5: the lookup checks
    bigin design close <slug> [--run R]          Stage 6 Parts 1, 2, 3 (pointer, questions) and 4

What stays with a reader is what needs one: whether an unmatched item is really on a screen, whether a
directive is implemented, whether a journey is sound. Everything here is a lookup, and a lookup done by
a model is both the expensive way to do it and the one that gets it wrong quietly.
"""
import os
import re

from . import model
from .edit import append_changelog, q_core
from .util import EngineError, today
from .vault import cell_value, find_tables, split_cells

ROLES = {"primary action", "secondary action", "destructive", "danger", "warning", "success", "info",
         "emphasis", "muted"}
SCREEN_TYPES = {"Primary", "Drill-down", "Wizard", "Tab"}
REGIONS = {"web": {"header", "nav", "main", "aside", "footer"},
           "mobile": {"header", "content", "tab-bar", "sheet", "fab"}}
SPEC_Q = re.compile(r"^- \[( |x|X)\] Q(\d*):\s?(.*)$")
H3 = re.compile(r"^###(?!#)\s+(.*?)\s*$")
VERDICT = re.compile(r"^(covered|gap\s*→\s*##\s*6\s*Q(\d+)|out of scope\s*[—-]\s*\S.*)$")
CAPABILITY = re.compile(r"\b(bulk|select all|export|saved view|subscri\w+)\b", re.I)
FIND = re.compile(r"\b(search|filter|sort)", re.I)
RESOLVED = ("resolved", "rejected", "addressed")


# ---------------------------------------------------------------------------- reading a spec

def kebab(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def _name(text):
    return (text or "").strip().strip("`").strip()


def nav_map_path(vault):
    return os.path.join(vault.ux_dir, "_ux", "navigation-map.md")


def spec_of(vault, slug):
    """The UX spec that owns ``slug`` (its ``feature:``), or None."""
    for p in vault.ux_paths():
        d = vault.load(p)
        if (d.fm_get("feature") or "").strip() == slug:
            return d
    return None


def _table_dicts(doc, start, end):
    out = []
    for t in find_tables(doc, start, end):
        hdr = [h.strip() for h in t.header]
        for r in t.rows():
            out.append(dict(zip(hdr, [c.strip() for c in r])))
        if out:
            break
    return out


def _subsections(doc, sec):
    """[(title, start, end)] for each ``###`` inside a level-2 section."""
    if not sec:
        return []
    heads = [(i, H3.match(doc.masked[i]).group(1)) for i in range(sec.start, sec.end)
             if H3.match(doc.masked[i]) and doc.lines[i].startswith("###")]
    return [(_name(t), i + 1, heads[k + 1][0] if k + 1 < len(heads) else sec.end) for k, (i, t) in enumerate(heads)]


def _bullets(doc, start, end):
    """``* **Key:** value`` lines of a block → {key: value}."""
    out = {}
    for i in range(start, end):
        m = re.match(r"^\s*[*-]\s+\*\*(.+?):\*\*\s*(.*)$", doc.lines[i])
        if m:
            out.setdefault(m.group(1).strip(), m.group(2).strip())
    return out


def serves(cell):
    """``UC-008 S1, S2, A1.2 · UC-009 E2 (entry)`` → {("UC-008","S1"), ("UC-008","S2"), ("UC-008","A1"), …}.
    Parentheticals are commentary; a sub-step (A1.2) counts for its flow (A1); ``S1–S4`` is a range."""
    out, uc = set(), None
    text = re.sub(r"\([^)]*\)", " ", cell or "")
    for m in re.finditer(r"(UC-\d+)|\b([SAE])(\d+)(?:\.\d+)*(?:\s*[–-]\s*\2?(\d+)\b)?", text):
        if m.group(1):
            uc = m.group(1)
        elif uc:
            a, b = int(m.group(3)), int(m.group(4) or m.group(3))
            for n in range(a, (b if a <= b <= a + 50 else a) + 1):
                out.add((uc, f"{m.group(2)}{n}"))
    return out


def parse(doc):
    """One UX spec, as the lookups need it. Never raises on a missing section — a check reports it."""
    s2, s3, s4, s5, s6 = (doc.section(k) for k in ("2", "3", "4", "5", "6"))
    inv = _table_dicts(doc, s2.start, s2.end) if s2 else []
    blocks = {t: (a, b) for t, a, b in _subsections(doc, s3)}
    flows, coverage, review = [], None, None
    for t, a, b in _subsections(doc, s4):
        if t.lower() == "coverage":
            coverage = _table_dicts(doc, a, b)
        else:
            flows.append({"name": t, **_bullets(doc, a, b)})
    for t, a, b in _subsections(doc, s5):
        if t.lower() == "flow review":
            review = _table_dicts(doc, a, b)
    qs = []
    if s6:
        for i in range(s6.start, s6.end):
            m = SPEC_Q.match(doc.masked[i])
            if m:
                qs.append({"n": m.group(2), "open": m.group(1) == " ", "text": m.group(3).strip(), "line": i})
    s1 = doc.section("1")
    scope_rows = []
    if s1:
        for t in find_tables(doc, s1.start, s1.end):
            if t.header and t.header[0].strip().lower() == "actor":
                scope_rows = [dict(zip([h.strip() for h in t.header], [c.strip() for c in r])) for r in t.rows()]
    return {"inventory": inv, "blocks": blocks, "flows": flows, "coverage": coverage, "review": review,
            "questions": qs, "actor_scope": scope_rows, "brief": _bullets(doc, s1.start, s1.end) if s1 else {}}


def _served(spec):
    out = set()
    for r in spec["inventory"]:
        out |= serves(r.get("Serves", ""))
    return out


# ---------------------------------------------------------------------------- hub rows

def _hub_rows(hub, key):
    s = hub.section(key)
    return _table_dicts(hub, s.start, s.end) if s else []


def open_pain_points(hub):
    return [{"id": r.get("PP-###", ""), "statement": r.get("Statement", ""), "status": r.get("Status", "")}
            for r in _hub_rows(hub, "Pain Points")
            if re.match(r"^PP-\d+$", r.get("PP-###", "")) and r.get("Status", "").lower() not in RESOLVED]


def open_directives(hub):
    return [{"n": r.get("#", ""), "directive": r.get("Directive", ""), "source": r.get("Source", "")}
            for r in _hub_rows(hub, "Design Directives")
            if r.get("#", "").strip() and r.get("Status", "").strip().lower() == "open"]


def active_principles(vault):
    p = os.path.join(vault.req, "DESIGN-PRINCIPLES.md")
    if not os.path.exists(p):
        return []
    d = vault.load(p)
    return [{"n": r.get("#", ""), "principle": r.get("Principle", ""), "category": r.get("Category", "")}
            for r in _table_dicts(d, d.body_start, len(d.lines))
            if r.get("#", "").strip() and r.get("Status", "").strip().lower() == "active"]


def nav_rows(vault):
    """{section title: [row dict]} for each ``## Structure…`` section of the navigation map."""
    p = nav_map_path(vault)
    if not os.path.exists(p):
        return None, {}
    d = vault.load(p)
    out = {}
    for s in d.sections:
        if s.title.lower().startswith("structure"):
            out[s.title] = _table_dicts(d, s.start, s.end)
    return d, out


# ---------------------------------------------------------------------------- Stage 1: scope

def _uc_state(vault, slug, uid, absorbed, served_ucs):
    p = vault.find(uid)
    if not p:
        return {"id": uid, "state": "SKIP", "why": "no such use case file"}
    d = vault.load(p)
    live = str(d.fm_get("version") or "").strip()
    row = {"id": uid, "title": model.title_of(d), "version": live, "status": (d.fm_get("status") or "").strip()}
    owner = (d.fm_get("primary_feature") or "").strip()
    if row["status"] == "removed":
        return {**row, "state": "SKIP", "why": "removed", "silent": True}
    if not [s for s in model.steps(d) if not s.dropped] or model.is_placeholder(d):
        return {**row, "state": "SKIP", "why": "no main flow yet → /bigin-transform-signal"}
    if not row["title"] or (d.fm_get("level") or "").strip() == "summary":
        return {**row, "state": "SKIP", "why": "summary-level or untitled — design the use cases it groups"}
    if owner and owner != slug:
        return {**row, "state": "SKIP", "why": f"owned by {owner}", "owner": owner}
    if uid not in absorbed:
        # screens on disk for a UC that was never stamped: a run died between Stage 3 and Stage 6
        return {**row, "state": "DRAFTED" if uid in served_ucs else "NEW"}
    if absorbed[uid] != live:
        return {**row, "state": "CHANGED", "from": absorbed[uid]}
    return {**row, "state": "CURRENT"}


def scope(vault, arg=None, run=None):
    """Stage 1 (1-scope.md), whole: which use cases have no current design, and why the others are skipped."""
    slugs = vault.slugs()
    if arg and re.match(r"^UC-\d+$", arg):
        p = vault.find(arg)
        if not p:
            raise EngineError(f"no use case {arg}")
        slugs = [(vault.load(p).fm_get("primary_feature") or "").strip()]
    elif arg:
        if arg not in slugs:
            raise EngineError(f"no hub '{arg}'")
        slugs = [arg]
    done = set()
    if run:
        from .runs import done_tasks
        done = done_tasks(vault, run)
    raw = vault.project().fm_get("platform")
    platform = raw if raw in ("web", "mobile", "both") else "web"
    nav, _ = nav_rows(vault)
    feats = []
    for slug in slugs:
        hub = vault.load(vault.hub_path(slug))
        d = spec_of(vault, slug)
        absorbed = dict(a.split("@", 1) for a in (d.fm_list("absorbed") if d else []) if "@" in a)
        served_ucs = {u for u, _ in _served(parse(d))} if d else set()
        ucs = [_uc_state(vault, slug, u, absorbed, served_ucs) for u in hub.fm_list("uc")]
        work = [u for u in ucs if u["state"] in ("NEW", "CHANGED", "DRAFTED")]
        dirs = open_directives(hub)
        f = {"feature": slug, "ux": d.id if d else None, "ux_path": vault.rel(d.path) if d else None,
             "platform": platform, "pain_points_open": len(open_pain_points(hub)), "open_directives": len(dirs),
             "ucs": ucs, "design_only": not hub.fm_list("uc") and bool(dirs)}
        if f"designed:{slug}" in done:
            f["resume"] = "done"
        elif f"screens:{slug}" in done or (work and all(u["state"] == "DRAFTED" for u in work)):
            f["resume"] = "review"     # the screens are on disk: resume at Stage 4, never redesign
        f["in_scope"] = (bool(work) or f["design_only"]) and f.get("resume") != "done"
        feats.append(f)
    return {"mode": "extend" if nav else "bootstrap", "nav_map": str(nav.fm_get("version") or "") if nav else None,
            "platform": platform, "platform_source": "stated" if raw in ("web", "mobile", "both") else "defaulted",
            **({"platform_bad_value": raw} if raw and raw not in ("web", "mobile", "both") else {}),
            "features": feats, "new_ids_needed": sum(1 for f in feats if f["in_scope"] and not f["ux"])}


def render_scope(res):
    L = ["work-list:"]
    skipped = []
    for f in res["features"]:
        bits = []
        for u in f["ucs"]:
            if u["state"] == "SKIP":
                if not u.get("silent") and not u.get("owner"):
                    skipped.append(f"  skipped {f['feature']}/{u['id']} — {u['why']}")
            elif u["state"] == "CHANGED":
                bits.append(f"{u['id']} CHANGED ({u['from']} → {u['version']})")
            else:
                bits.append(f"{u['id']} {u['state']}")
        if not f["in_scope"] and not bits:
            continue
        head = f"  {f['feature']}  " + ("design-only" if f["design_only"] else f"{f['ux'] or 'UX new'}")
        tail = ", ".join(bits) or f"{f['open_directives']} open directive(s)"
        note = {"review": "  [screens on disk — resume at Stage 4]", "done": "  [closed in this run]"}.get(f.get("resume"), "")
        elsewhere = sum(1 for u in f["ucs"] if u.get("owner"))
        L.append(f"{head}  platform: {f['platform']}  pp: {f['pain_points_open']} open  — {tail}{note}"
                 + ("" if f["in_scope"] else "  (nothing to redesign)")
                 + (f"  · {elsewhere} designed in their owner's spec" if elsewhere else ""))
    L += skipped
    L.append(f"mode: {res['mode']}" + (f" (navigation map v{res['nav_map']})" if res["nav_map"] else ""))
    L.append(f"platform: {res['platform']} ({res['platform_source']})"
             + (f" — bad value '{res['platform_bad_value']}' in project.md" if res.get("platform_bad_value") else ""))
    L.append(f"new UX ids needed: {res['new_ids_needed']}")
    return "\n".join(L)


# ---------------------------------------------------------------------------- Stage 3: the worker's input

def _uc_full(vault, d, state):
    from .changeset import field_value
    fields = ("Primary Actor", "Secondary Actor(s)", "Business Need / Goal", "Trigger", "Pre-conditions",
              "Post-conditions (success)", "Post-conditions (failure)")
    return {"id": d.id, "title": model.title_of(d), "version": str(d.fm_get("version") or ""),
            "status": d.fm_get("status"), "state": state["state"], **({"was": state["from"]} if state.get("from") else {}),
            "summary": {f: field_value(d, "1", f) for f in fields if field_value(d, "1", f)},
            "steps": [{"id": s.id, "actor": s.actor, "system": s.system} for s in model.steps(d) if not s.dropped],
            "flows": [{"id": f.id, "name": f.name, "body": f.body} for f in model.flows(d) if not f.dropped],
            "rules": [{"br": c[0], "enforced_at": c[2] if len(c) > 2 else ""} for _, c in model.s4_rows(d)],
            "known_gaps": [q.text for q in model.open_questions(d)],
            "entities": d.fm_list("entities"), "pain_points": d.fm_list("pain_points")}


def _entity(vault, eid):
    p = vault.find(eid)
    if not p:
        return {"id": eid, "missing": True}
    d = vault.load(p)
    s = d.section("Fields")
    rel = d.section("Relationships")
    return {"id": eid, "title": model.title_of(d),
            "fields": [{k: v for k, v in r.items() if v} for r in (_table_dicts(d, s.start, s.end) if s else [])],
            "relationships": "\n".join(x for x in d.lines[rel.start:rel.end] if x.strip()) if rel else ""}


def worklist(vault, slug, args=None):
    """The screens worker's requirement input (3-screens.md Part 1), compact: it reads this and its card,
    and opens a UC, BR or entity file only to confirm one detail."""
    sc = scope(vault, slug)
    f = sc["features"][0]
    hub = vault.load(vault.hub_path(slug))
    spec = spec_of(vault, slug)
    ucs, others, brs, ents = [], [], {}, {}
    for u in f["ucs"]:
        if u["state"] in ("NEW", "CHANGED", "DRAFTED"):
            d = vault.load(vault.find(u["id"]))
            card = _uc_full(vault, d, u)
            ucs.append(card)
            for r in card["rules"]:
                brs.setdefault(r["br"], None)
            for e in card["entities"]:
                ents.setdefault(e, None)
        elif u["state"] == "CURRENT":
            others.append({"id": u["id"], "title": u["title"], "note": "CURRENT — already designed, do not redesign"})
        elif u.get("owner"):
            others.append({"id": u["id"], "title": u["title"], "note": f"NOT YOURS — designed in {u['owner']}'s spec"})
    for b in list(brs):
        p = vault.find(b)
        if p:
            d = vault.load(p)
            brs[b] = {"id": b, "title": model.title_of(d), "statement": model.br_statement(d)}
    _, nav = nav_rows(vault)
    siblings = []
    for p in vault.ux_paths():
        d = vault.load(p)
        if spec is not None and d.path == spec.path:
            continue
        siblings.append({"ux": d.id, "feature": d.fm_get("feature"),
                         "screens": [f"{_name(r.get('Screen'))} ({r.get('Screen Type', '?')})" for r in parse(d)["inventory"]]})
    existing = None
    if spec is not None:
        existing = {"id": spec.id, "path": vault.rel(spec.path), "version": str(spec.fm_get("version") or ""),
                    "screens": [{k: r.get(k, "") for k in ("Screen", "View ID", "Screen Type", "Actor", "Volume", "Serves")}
                                for r in parse(spec)["inventory"]]}
    return {"$schema_version": 1, "kind": "worklist", "stage": "design", "feature": slug,
            "hub": {"name": hub.fm_get("name"), "description": hub.fm_get("description")},
            "ux": existing or {"id": None, "note": "new — the dispatch names the UX-### minted for you"},
            "platform_default": sc["platform"], "nav_map": {"version": sc["nav_map"], "structure": {
                k: [{c: r.get(c, "") for c in ("id", "Label", "Points to (screen)")} for r in rows]
                for k, rows in nav.items()}},
            "use_cases": ucs, "other_use_cases": others,
            "rules": [b for b in brs.values() if b], "entities": [_entity(vault, e) for e in ents],
            "pain_points": open_pain_points(hub), "directives": open_directives(hub),
            "principles": active_principles(vault), "sibling_screens": siblings,
            "read": "this is your whole requirement input. Open a UC, BR or EN file only to confirm one detail "
                    "this summarised; open ONE sibling spec only when you reuse a pattern named in sibling_screens."}


# ---------------------------------------------------------------------------- Stage 5: forward items

def _in_scope_ucs(vault, slug, spec_doc):
    """UCs whose coverage this run answers for: owned here, with a flow, and on the spec or not yet stamped."""
    f = scope(vault, slug)["features"][0]
    return [u for u in f["ucs"] if u["state"] in ("NEW", "CHANGED", "DRAFTED")]


def items(vault, slug):
    """Every requirement item of the in-scope use cases, matched FORWARD by id (5-verify.md Parts 1–2).
    ``covered_by`` is what an id match found; an empty one is ``unmatched`` and is the reader's to settle."""
    d = spec_of(vault, slug)
    if d is None:
        raise EngineError(f"no UX spec for '{slug}'")
    spec = parse(d)
    hub = vault.load(vault.hub_path(slug))
    by_item = {}
    for r in spec["inventory"]:
        for key in serves(r.get("Serves", "")):
            by_item.setdefault(key, []).append(_name(r.get("Screen")))
    text = {t: "\n".join(d.lines[a:b]) for t, (a, b) in spec["blocks"].items()}
    out, brs = [], {}
    for u in _in_scope_ucs(vault, slug, d):
        ud = vault.load(vault.find(u["id"]))
        for s in model.steps(ud):
            if not s.dropped:
                out.append({"item": f"{u['id']} {s.id}", "kind": "step", "covered_by": by_item.get((u["id"], s.id), [])})
        for fl in model.flows(ud):
            if not fl.dropped:
                out.append({"item": f"{u['id']} {fl.id}", "kind": "alternative" if fl.kind == "A" else "exception",
                            "covered_by": by_item.get((u["id"], fl.id), [])})
        for b in model.s4_brs(ud):
            brs.setdefault(b, None)
    for b in brs:
        out.append({"item": b, "kind": "rule", "covered_by": [t for t, body in text.items() if re.search(rf"\b{b}\b", body)],
                    "note": "a back-office rule that constrains no screen is `out of scope` — say so once"})
    for pp in open_pain_points(hub):
        hit = [fl["name"] for fl in spec["flows"] if re.search(rf"\b{pp['id']}\b", fl.get("Resolves", ""))]
        out.append({"item": pp["id"], "kind": "pain point", "covered_by": hit, "statement": pp["statement"],
                    "note": "matches ONLY on a flow's Resolves cell — never repaired by writing the id in"})
    whole = d.text
    for x in open_directives(hub):
        out.append({"item": f"directive #{x['n']}", "kind": "directive", "text": x["directive"],
                    "covered_by": ["cited in the spec"] if re.search(rf"[Dd]irective[s]?\s+#?{re.escape(x['n'])}\b", whole) else []})
    for x in active_principles(vault):
        out.append({"item": f"principle #{x['n']}", "kind": "principle", "text": x["principle"][:200],
                    "covered_by": ["cited in the spec"] if re.search(rf"(PRINCIPLES|principle)\s+#?{re.escape(x['n'])}\b", whole) else []})
    unmatched = [i for i in out if not i["covered_by"]]
    return {"feature": slug, "ux": d.id, "items": out, "unmatched": [i["item"] for i in unmatched],
            "counts": {"items": len(out), "matched": len(out) - len(unmatched), "unmatched": len(unmatched)},
            "not_listed": "entity FIELDS a step reads or writes are not derivable by id — check those against the "
                          "element tables of the screens that serve the step",
            "read": "matched = an id match only: name the STATE in `Covered by` from that one screen block. "
                    "unmatched = not designed, unless you can point at the element or state that carries it."}


def render_items(res):
    c = res["counts"]
    L = [f"{res['feature']} {res['ux']} — {c['items']} item(s): {c['matched']} matched by id, {c['unmatched']} unmatched"]
    L += [f"  unmatched: {i['item']} ({i['kind']})" for i in res["items"] if not i["covered_by"]]
    return "\n".join(L)


# ---------------------------------------------------------------------------- the lookup checks

def _on_hub(hub, ux_id, q):
    """Is this ## 6 question on the hub? ``open`` / ``answered`` / None. Matched on its ``(ref: UX-### § 6
    Q<n>)`` tag first — the two copies get reworded apart — then on the sentence."""
    s = hub.section("Open Questions / Gates")
    if not s:
        return None
    ref = re.compile(rf"{ux_id} § 6 Q{q['n']}\b") if q["n"] else None
    core = q_core(q["text"])[:80]
    for i in range(s.start, s.end):
        m = re.match(r"^\s*- \[( |x|X)\] Q:\s?(.*)$", hub.lines[i])
        if m and ((ref and ref.search(m.group(2))) or (core and q_core(m.group(2)).startswith(core))):
            return "open" if m.group(1) == " " else "answered"
    return None


def _f(check, where, msg, level="block"):
    return {"check": check, "level": level, "where": where, "msg": msg}


def _all_view_ids(vault):
    out = {}
    for p in vault.ux_paths():
        d = vault.load(p)
        for r in parse(d)["inventory"]:
            v = _name(r.get("View ID"))
            if v:
                out.setdefault(v, []).append(f"{d.id} {_name(r.get('Screen'))}")
    return out


def check(vault, slug, phase="close"):
    """The lookup half of 6-close.md Part 5 (``phase='close'``) and of the wave check in
    references/agent-dispatch.md (``phase='wave'``). ``block`` findings are mismatches; ``confirm`` ones are
    heuristics a reader settles by opening only the block named."""
    d = spec_of(vault, slug)
    if d is None:
        return {"feature": slug, "ux": None, "findings": [_f(0, slug, "no UX spec on disk for this feature")], "ok": False}
    spec, F = parse(d), []
    inv, blocks = spec["inventory"], spec["blocks"]
    platform = (d.fm_get("platform") or "web").strip()
    served = _served(spec)
    # 1 — absorbed names only designed use cases
    absorbed = [a.split("@")[0] for a in d.fm_list("absorbed")]
    if phase == "close":
        for u in absorbed:
            if u not in {x for x, _ in served}:
                F.append(_f(1, u, "is on absorbed: but no ## 2 row serves it"))
    # 2 — every served step exists and is live
    live = {}
    for uc, sid in sorted(served):
        if uc not in live:
            p = vault.find(uc)
            ud = vault.load(p) if p else None
            live[uc] = None if ud is None else ({s.id for s in model.steps(ud) if not s.dropped} |
                                                {f.id for f in model.flows(ud) if not f.dropped})
        if live[uc] is None:
            F.append(_f(2, uc, "a ## 2 row serves a use case that does not exist"))
        elif sid not in live[uc]:
            F.append(_f(2, f"{uc} {sid}", "a ## 2 row serves a step or flow that does not exist or was removed"))
    # 3 / 4 / 13 / 15 / 16 — per screen block
    for name, (a, b) in blocks.items():
        primaries = 0
        for t in find_tables(d, a, b):
            ci = t.col("Role")
            if ci is None:
                continue
            for r in t.rows():
                cell = cell_value(r[ci]).lower() if len(r) > ci else ""
                # a cell may name one role per state: `warning (draft) · success (signed)`
                parts = [x.strip(" `") for x in re.split(r"[·/,;|]|\bor\b", re.sub(r"\([^)]*\)", " ", cell))]
                for role in [x for x in parts if x and x not in ("blank", "—", "-")]:
                    if role not in ROLES:
                        F.append(_f(3, name, f"role '{role}' is not on the closed list"))
                primaries += "primary action" in parts
        if primaries > 1 and platform != "both":
            F.append(_f(3, name, f"{primaries} `primary action` elements on one screen"))
        elif primaries > 2:
            F.append(_f(3, name, f"{primaries} `primary action` elements — more than one per layout?", "confirm"))
        body = d.masked[a:b]
        for line in body:
            for m in re.finditer(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", line):
                if re.search(r"[a-fA-F]", m.group(0)) or len(m.group(0)) == 7:
                    F.append(_f(4, name, f"raw colour {m.group(0)}"))
            for m in re.finditer(r"\b(\d+(?:\.\d+)?)px\b", line):
                if m.group(1) != "390":
                    F.append(_f(4, name, f"raw size {m.group(0)}"))
            for m in re.finditer(r"(?<![\w-])--[a-z][a-z0-9-]*", line):
                F.append(_f(4, name, f"token id {m.group(0)}"))
            if re.search(r"\bfont-family\b|\bsans-serif\b|\bHelvetica\b|\bArial\b|\bRoboto\b", line):
                F.append(_f(4, name, "a font name"))
            if CAPABILITY.search(line) and not re.search(r"\b(UC-\d+|BR-\d+)\b", line):
                F.append(_f(16, name, f"'{CAPABILITY.search(line).group(0)}' with no UC step or BR on the line: "
                            + line.strip()[:120], "confirm"))
        fields = _bullets(d, a, b)
        for key, val in fields.items():
            want = "web" if key.endswith("Web") else "mobile" if key.endswith("Mobile") else None
            if key == "Regions" and platform in REGIONS:
                want = platform
            if want and (key == "Regions" or key.startswith("Layout")):
                lead = re.match(r"^`([^`]*)`", val)
                words = set(re.findall(r"[a-z-]+", (lead.group(1) if lead else val.split(".")[0]).lower()))
                wrong = words & (REGIONS["mobile" if want == "web" else "web"] - REGIONS[want])
                if wrong:
                    F.append(_f(13, name, f"{key} uses the other platform's region(s): {', '.join(sorted(wrong))}"))
        if not fields.get("Actor"):
            F.append(_f(15, name, "screen block carries no Actor line"))
    # 2 (structure) / 15 / 18 / 19 — per inventory row
    ids = _all_view_ids(vault)
    _, nav = nav_rows(vault)
    landing, drill = set(), set()
    for rows in nav.values():
        for r in rows:
            for part in re.split(r",\s*(?![^()]*\))", r.get("Points to (screen)", "")):
                m = re.match(r"^(.*?)\s*\((Landing|Drill-down)\)\s*$", part.strip())
                if m:
                    (landing if m.group(2) == "Landing" else drill).add(_name(m.group(1)))
    names = {_name(r.get("Screen")) for r in inv}
    for r in inv:
        name = _name(r.get("Screen"))
        if name not in blocks:
            F.append(_f(2, name, "is in the ## 2 inventory but has no ## 3 spec block"))
        vid, stype = _name(r.get("View ID")), _name(r.get("Screen Type"))
        if not vid:
            F.append(_f(18, name, "no View ID"))
        else:
            if vid != f"{slug}-{kebab(name)}":
                F.append(_f(18, name, f"View ID '{vid}' is not '{slug}-{kebab(name)}' — renamed without re-minting?", "confirm"))
            if len(ids.get(vid, [])) > 1:
                F.append(_f(18, name, f"View ID '{vid}' is shared by: {'; '.join(ids[vid])}"))
        if stype not in SCREEN_TYPES:
            F.append(_f(19, name, f"Screen Type '{stype}' is not one of {', '.join(sorted(SCREEN_TYPES))}"))
        elif name in landing and stype != "Primary":
            F.append(_f(19, name, f"the nav map opens it as (Landing) but it is typed {stype}", "confirm"))
        elif name in drill and name not in landing and stype in ("Wizard", "Tab"):
            F.append(_f(19, name, f"the nav map lists it as (Drill-down) but it is typed {stype}"))
        if not r.get("Actor", "").strip() or not r.get("Volume", "").strip():
            F.append(_f(15, name, "## 2 row carries no Actor or no Volume"))
        vol = r.get("Volume", "").strip().lower()
        if name in blocks:
            body = "\n".join(d.lines[slice(*blocks[name])])
            if vol.startswith("many"):
                if not FIND.search(body):
                    F.append(_f(15, name, "volume `many` with no search, filter or sort"))
                missing = [s for s in ("empty", "few", "many", "loading", "error") if not re.search(rf"\b{s}\b", body, re.I)]
                if missing:
                    F.append(_f(15, name, f"volume `many` but no state named: {', '.join(missing)}", "confirm"))
                if not re.search(r"\d[\d,]{2,}", body):
                    F.append(_f(15, name, "volume `many` but the real scale is never a number", "confirm"))
    for name in blocks:
        if name not in names:
            F.append(_f(2, name, "has a ## 3 spec block but no ## 2 inventory row"))
    # 7 — no prompt blocks
    if any(s.title.lower().startswith("prototype prompt") for s in d.sections):
        F.append(_f(7, d.id, "a ## Prototype Prompt heading remains — delete the block"))
    # 9 — relationship model matches ## 7 on disk
    s7 = d.section("7")
    rows7 = sum(len(t.rows()) for t in find_tables(d, s7.start, s7.end)) if s7 else 0
    rm = (d.fm_get("relationship_model") or "none").strip()
    if rm == "modelled" and not rows7:
        F.append(_f(9, d.id, "relationship_model: modelled but ## 7 is absent or has no rows"))
    if rm != "modelled" and s7:
        F.append(_f(9, d.id, "relationship_model is not `modelled` but ## 7 is still in the file — delete it"))
    # 12 — platform stated twice, the same
    said = re.match(r"^`?(web|mobile|both)\b", spec["brief"].get("Platform", "").lower())
    if not said or said.group(1) != platform:
        F.append(_f(12, d.id, f"frontmatter platform: {platform} but ## 1's Platform line says "
                    f"'{spec['brief'].get('Platform', '')[:40] or 'nothing'}'"))
    # 14 — actors: frontmatter and table agree
    fm_roles = [str(a).split(":")[0].strip() for a in d.fm_list("actors")]
    tb_roles = [r.get("Actor", "").strip() for r in spec["actor_scope"]]
    if fm_roles != tb_roles:
        F.append(_f(14, d.id, f"actors: lists {fm_roles or 'nothing'}; the Actor & Scope table lists {tb_roles or 'nothing'}"))
    for r in spec["actor_scope"]:
        if not r.get("Grounded by", "").strip():
            F.append(_f(14, r.get("Actor", "?"), "Actor & Scope row carries no ground"))
    # 5e — flows walk real screens
    known = set(ids) | {x.split(" ", 1)[1] for v in ids.values() for x in v} | \
        {r.get("id", "") for rows in nav.values() for r in rows}
    for p in vault.ux_paths():
        known |= {_name(r.get("Screen")) for r in parse(vault.load(p))["inventory"]}
    for fl in spec["flows"]:
        for n in re.findall(r"`([^`]+)`", fl.get("Path", "")):
            if n not in known and not re.match(r"^(header|main|aside|nav|footer|content|tab-bar|sheet|fab)\b", n):
                F.append(_f(17, fl["name"], f"Path names `{n}`, which is no screen of any spec", "confirm"))
    seen = set()
    F = [x for x in F if (k := (x["check"], x["where"], x["msg"])) not in seen and not seen.add(k)]
    if phase == "wave":
        if spec["review"]:
            F.append(_f(17, d.id, "### Flow Review has rows — fine on a spec being UPDATED (earlier runs' verdicts); "
                        "on a new spec the worker graded its own journeys", "confirm"))
        open_q = [q for q in spec["questions"] if q["open"]]
        return {"feature": slug, "ux": d.id, "phase": phase, "screens": len(inv), "flows": len(spec["flows"]),
                "open_questions": len(open_q), "findings": F, "ok": not [x for x in F if x["level"] == "block"]}
    # 6 — status from the live count
    open_q = [q for q in spec["questions"] if q["open"]]
    status = (d.fm_get("status") or "").strip()
    if status in ("draft", "needs-clarification") and status != ("needs-clarification" if open_q else "draft"):
        F.append(_f(6, d.id, f"status: {status} with {len(open_q)} open question(s)"))
    # 5 — every open question is on the hub, same sentence
    hub = vault.load(vault.hub_path(slug))
    for q in open_q:
        hit = _on_hub(hub, d.id, q)
        if hit is None:
            F.append(_f(5, f"Q{q['n']}", "open in ## 6 but not mirrored on the hub's Open Questions / Gates"))
        elif hit == "answered":
            F.append(_f(5, f"Q{q['n']}", "answered on the hub but still open in ## 6 — fold the answer into the spec", "confirm"))
    # 17 — Coverage and Flow Review are whole
    cov = spec["coverage"]
    if cov is None:
        F.append(_f(17, d.id, "no ### Coverage table under ## 4"))
    else:
        open_n = {q["n"] for q in open_q}
        rows = {r.get("Item", "").strip(): r for r in cov}
        for item, r in rows.items():
            v = r.get("Verdict", "").strip()
            m = VERDICT.match(v)
            if not m:
                F.append(_f(17, item, f"verdict '{v[:40]}' is not covered | gap → ## 6 Q<n> | out of scope — <reason>"))
            elif v == "covered" and r.get("Covered by", "").strip() in ("", "—", "-"):
                F.append(_f(17, item, "`covered` over an empty Covered by"))
            elif m.group(2) and m.group(2) not in open_n:
                F.append(_f(17, item, f"gap points at Q{m.group(2)}, which is not an open ## 6 question"))
        for i in items(vault, slug)["items"]:
            if i["kind"] in ("step", "alternative", "exception", "pain point", "rule") and i["item"] not in rows:
                F.append(_f(17, i["item"], f"{i['kind']} has no row in ### Coverage"))
            elif i["kind"] == "pain point" and rows[i["item"]].get("Verdict", "").strip() == "covered" and not i["covered_by"]:
                F.append(_f(17, i["item"], "Coverage says covered but no flow's Resolves names it"))
    if spec["flows"]:
        reviewed = {_name(r.get("Flow")) for r in (spec["review"] or [])}
        for fl in spec["flows"]:
            if fl["name"] not in reviewed:
                F.append(_f(17, fl["name"], "flow has no row in ### Flow Review", "block" if not spec["review"] else "confirm"))
    return {"feature": slug, "ux": d.id, "phase": phase, "screens": len(inv), "flows": len(spec["flows"]),
            "open_questions": len(open_q), "findings": F, "ok": not [x for x in F if x["level"] == "block"],
            "not_checked": "8 (nav map lost nothing — `git diff` it), 10 and 11 (## 7 rows against real EN fields and "
                           "BRs), the grounds behind 14, and whether each `confirm` finding is real"}


def render_check(res):
    blk = [x for x in res["findings"] if x["level"] == "block"]
    cnf = [x for x in res["findings"] if x["level"] == "confirm"]
    L = [f"{res['feature']} {res.get('ux') or '—'} [{res.get('phase', 'close')}]: "
         + ("OK" if res["ok"] else f"{len(blk)} BLOCKING") + (f", {len(cnf)} to confirm" if cnf else "")]
    L += [f"  BLOCK   check {x['check']:>2}  {x['where']}: {x['msg']}" for x in blk]
    L += [f"  confirm check {x['check']:>2}  {x['where']}: {x['msg']}" for x in cnf]
    if res.get("not_checked"):
        L.append(f"  still yours: {res['not_checked']}")
    return "\n".join(L)


# ---------------------------------------------------------------------------- Stage 6: close

def _pointer(spec_doc, n_screens, status, role):
    title = re.sub(r"\.md$", "", os.path.basename(spec_doc.path))
    return f"- [[{title}]] — {status} — {n_screens} screens — updated {today()} ({role})"


def _upsert_pointer(hub, ux_id, line):
    s = hub.section("UX Spec")
    if s is None:
        hub.insert_section("UX Spec", ["", line], before="Open Questions / Gates")
        return True
    for i in range(s.start, s.end):
        if re.match(rf"^- \[\[{ux_id}\b", hub.lines[i]):
            # same facts, a different day: leave the line (and its date) alone
            if re.sub(r"updated \S+", "", hub.lines[i]) == re.sub(r"updated \S+", "", line):
                return False
            return hub.splice(i, i + 1, [line])
    end = s.end
    while end > s.start and not hub.lines[end - 1].strip():
        end -= 1
    if end == s.start:
        return hub.splice(end, end, ["", line])
    return hub.splice(end, end, [line])


def close(vault, slug, run=None, dry=False):
    """Stage 6 Parts 1, 2, 4 and the pointer/question half of Part 3, from the file on disk — never from
    a worker's report. Idempotent. Directive rows, ``sources:`` and the report stay with the orchestrator."""
    from .changeset import Outcome, add_question
    d = spec_of(vault, slug)
    if d is None:
        raise EngineError(f"no UX spec for '{slug}'")
    spec = parse(d)
    served_ucs = {u for u, _ in _served(spec)}
    f = scope(vault, slug)["features"][0]
    # check 17 keys on what is NEW / CHANGED, which the stamp below is about to make CURRENT: read it first
    pre17 = [x for x in check(vault, slug, "close")["findings"] if x["check"] == 17]
    # Part 1 — absorbed: every owned use case that really has a screen row, at its live version
    designed = [u for u in f["ucs"] if u["state"] != "SKIP" and u["id"] in served_ucs]
    not_designed = [u["id"] for u in f["ucs"] if u["state"] in ("NEW", "CHANGED") and u["id"] not in served_ucs]
    stamp = [f"{u['id']}@{u['version']}" for u in designed]
    was = d.fm_list("absorbed")
    newly = [u for u in designed if f"{u['id']}@{u['version']}" not in was]
    changed = []
    if stamp != was:
        d.fm_set("absorbed", stamp)
        changed.append("absorbed")
    # Part 2 — status from the live count
    open_q = [q for q in spec["questions"] if q["open"]]
    status = (d.fm_get("status") or "draft").strip()
    if status not in ("accepted", "superseded"):
        want = "needs-clarification" if (open_q or not_designed) else "draft"
        if want != status:
            d.fm_set("status", want)
            changed.append("status")
            status = want
    nav, _ = nav_rows(vault)
    if nav is not None and str(d.fm_get("nav_map") or "") != str(nav.fm_get("version") or ""):
        d.fm_set("nav_map", str(nav.fm_get("version") or ""))
        changed.append("nav_map")
    s7 = d.section("7")
    rows7 = sum(len(t.rows()) for t in find_tables(d, s7.start, s7.end)) if s7 else 0
    if (d.fm_get("relationship_model") or "none").strip() == "modelled" and not rows7:
        d.fm_set("relationship_model", "none")
        changed.append("relationship_model")
    if changed:
        if "updated" in d.fm:
            d.fm_set("updated", today())
        append_changelog(d, f"- {today()} — closed: absorbed {', '.join(stamp) or 'nothing'}; status {status} "
                            f"({len(open_q)} open question(s))")
    wrote = []
    if changed and not dry and vault.write(d):
        wrote.append(vault.rel(d.path))
    # Part 3 — the pointer on every hub these screens touch, and the questions on the owner's
    n = len(spec["inventory"])
    mirrored = 0
    for s in [slug] + [x for x in d.fm_list("features") if x != slug]:
        hp = vault.hub_path(s)
        if not os.path.exists(hp):
            continue
        hub = vault.load(hp)
        did = _upsert_pointer(hub, d.id, _pointer(d, n, status, "owner" if s == slug else f"participant — designed in {slug}"))
        have = hub.fm_list("uiux")
        if d.id not in have:
            hub.fm_set("uiux", have + [d.id])
            did = True
        if s == slug:
            for q in open_q:
                if _on_hub(hub, d.id, q):
                    continue
                try:
                    add_question(hub, "HUB", re.sub(r"\s*\(ref:[^)]*\)", "", q["text"]),
                                 ref=f"{d.id} § 6 Q{q['n']}" if q["n"] else d.id)
                    mirrored += 1
                    did = True
                except Outcome:
                    pass
            if newly:
                ns = hub.section("Notes / History")
                line = (f"- {today()} — /bigin-generate-design: {d.id} designed from "
                        f"{', '.join(u['id'] + '@' + u['version'] for u in newly)} ({n} screens); "
                        f"{len(open_q)} design question(s) open.")
                if ns:
                    hub.splice(ns.start, ns.start, [line])
                    did = True
        if did:
            if "updated" in hub.fm:
                hub.fm_set("updated", today())
            if not dry and vault.write(hub):
                wrote.append(vault.rel(hp))
    # Part 4 — the one line back to a use case that is not approved yet
    title = re.sub(r"\.md$", "", os.path.basename(d.path))
    for u in newly:
        if u["status"] == "approved":
            continue
        ud = vault.load(vault.find(u["id"]))
        ds = ud.section("Discussion")
        if ds is None or any(f"**{d.id}** ({today()})" in x for x in ud.lines[ds.start:ds.end]):
            continue
        end = ds.end
        while end > ds.start and not ud.lines[end - 1].strip():
            end -= 1
        ud.splice(end, end, [f"- **{d.id}** ({today()}): screens for this flow are drafted — {n} screens, see "
                             f"04-UIUX/{title}.md. Supporting evidence, no requirement change proposed."])
        if not dry and vault.write(ud):
            wrote.append(vault.rel(ud.path))
    if not dry:
        from . import cascade
        cascade.run(vault)
        if run:
            from .runs import record
            record(vault, run, f"designed:{slug}", "ok", f"{d.id} {status}")
            from . import metrics
            metrics.estimate_design(vault, run, slug, d.path)
    post = [] if dry else [x for x in check(vault, slug, "close")["findings"] if x["check"] != 17]
    res = {"findings": pre17 + post}
    res["ok"] = not [x for x in res["findings"] if x["level"] == "block"]
    return {"feature": slug, "ux": d.id, "status": status, "absorbed": stamp, "not_designed": not_designed,
            "open_questions": len(open_q), "questions_mirrored": mirrored, "screens": n, "set": changed,
            "wrote": wrote, "dry": dry, "ok": res["ok"], "findings": res["findings"],
            "left_to_you": "flip a hub ## Design Directives row to `reflected` only where a screen implements it; "
                           "keep sources: and features: current; the run report (6-close.md Part 6)"}


def render_close(res):
    L = [f"{res['feature']} {res['ux']} — status {res['status']}, {res['screens']} screens, "
         f"{res['open_questions']} open question(s), absorbed [{', '.join(res['absorbed'])}]"
         + (" (dry run)" if res["dry"] else "")]
    if res["not_designed"]:
        L.append(f"  NOT designed, stays off absorbed: {', '.join(res['not_designed'])}")
    if res["wrote"]:
        L.append("  wrote: " + ", ".join(res["wrote"]))
    L.append(render_check({**res, "phase": "close"}))
    L.append(f"  left to you: {res['left_to_you']}")
    return "\n".join(L)
