"""Impact of one intake note on the spec vault — an OUTPUT of the transform run, not a stage of its own.

BABOK 5.4 "assess requirements changes" over the trace graph the vault already keeps. Seeds are what
the note's signals actually reached: every hub Signal Log row citing ``INT-###`` and its Destination
(``UC-012 S6 · BR-004``) and Status (applied / staged / question / rejected …). From there one fixed
walk, every hit carrying a reason:

    direct      a UC step / flow or a BR the note's rows were routed to (applied, or staged: waiting
                on a question)
    rule        another UC whose § 4 mirrors a BR the note changed — the rule changed under it
    entity      another UC that uses an entity a directly-hit UC uses (review, lower severity)
    sibling     every other feature a hit UC belongs to
    downstream  UX specs, epics and stories built on a hit UC — with ``absorbed`` vs the UC's version
                (current / drifted) and, for a story, which of its sliced steps were hit

Nothing here writes a UC, BR or hub. ``write()`` regenerates one engine-owned ``## Impact`` section on
the INT note (and ``01-Requirements/_impact/INT-###.json``); a rerun with nothing changed writes
nothing. The BA reads it in review — there is no confirmation step and no gate.
"""
import json
import os
import re

from . import model
from .cascade import derive as derive_stale
from .stories import expand_slice, parse_slices
from .util import EngineError, sort_ids, today

MARK = "<!-- engine-owned: `bigin impact` regenerates this section after every transform run — edit nothing here -->"
REF = re.compile(r"\b(UC-\d+)((?:\s+[SAE]\d+(?:\s*[-–]\s*[SAE]?\d+)?)*)|\b(BR-\d+)")


def _dests(text):
    """'UC-012 S6, A2 · BR-004' → ({'UC-012': {'S6','A2'}}, {'BR-004'})."""
    ucs, brs = {}, set()
    for m in REF.finditer(text or ""):
        if m.group(3):
            brs.add(m.group(3))
            continue
        refs = ucs.setdefault(m.group(1), set())
        refs |= model.enforcement_refs(m.group(2) or "") | set(re.findall(r"\b[SAE]\d+\b", m.group(2) or ""))
    tail = re.findall(r"(UC-\d+)[^·;|]*?((?:,\s*[SAE]\d+)+)", text or "")
    for uc, more in tail:
        ucs.setdefault(uc, set()).update(re.findall(r"[SAE]\d+", more))
    return ucs, brs


class Graph:
    def __init__(self, vault):
        self.v = vault
        self.uc, self.br = {}, {}
        for p in vault.uc_paths():
            d = vault.load(p)
            if d.id:
                feats = [f for f in [d.fm_get("primary_feature")] + d.fm_list("features") if f]
                self.uc[d.id] = {"doc": d, "title": model.title_of(d), "status": d.fm_get("status") or "",
                                 "version": str(d.fm_get("version") or ""), "primary": d.fm_get("primary_feature") or "",
                                 "features": list(dict.fromkeys(feats)),
                                 "brs": set(d.fm_list("brs")) | set(model.s4_brs(d)), "entities": set(d.fm_list("entities")),
                                 "order": [s.id for s in model.steps(d) if not s.dropped]}
        for p in vault.br_paths():
            d = vault.load(p)
            if d.id:
                self.br[d.id] = {"doc": d, "title": model.title_of(d), "status": d.fm_get("status") or "",
                                 "version": str(d.fm_get("version") or ""), "feature": d.fm_get("feature") or "",
                                 "ucs": set(d.fm_list("uc"))}
        self.ucs_state = {k: {"version": u["version"], "status": u["status"], "trigger": None} for k, u in self.uc.items()}

    def ucs_citing_br(self, bid):
        out = set(self.br.get(bid, {}).get("ucs", set()))
        out |= {u for u, x in self.uc.items() if bid in x["brs"]}
        return out


def seeds(vault, nid):
    """Every Signal Log row citing ``nid``, across hubs → rows + direct UC/BR targets."""
    rows, ucs, brs = [], {}, set()
    for slug in vault.slugs():
        sd = model.signal_doc(vault, slug)
        for r in model.signal_rows(sd) if sd else []:
            cites = {n for n, _ in model.expand_int_cites(r.source)}
            if nid not in cites and nid not in (r.source or ""):
                continue
            u, b = _dests(r.destination)
            rows.append({"hub": slug, "row": r.num, "signal": r.get("Signal"), "status": r.status,
                         "destination": r.destination, "notes": r.get("Notes")})
            if r.status in ("applied", "staged", "new", "held", "conflict"):
                for k, refs in u.items():
                    ucs.setdefault(k, {"refs": set(), "pending": False})
                    ucs[k]["refs"] |= refs
                    ucs[k]["pending"] = ucs[k]["pending"] or r.status == "staged"
                brs |= b
    return rows, ucs, brs


def walk(vault, nid=None, ucs=None, brs=None, features=None):
    g = Graph(vault)
    rows = []
    if nid:
        rows, ucs, brs = seeds(vault, nid)
    ucs = {k: (v if isinstance(v, dict) else {"refs": set(v or []), "pending": False}) for k, v in (ucs or {}).items()}
    brs = set(brs or [])
    for f in features or []:
        for u, x in g.uc.items():
            if f in x["features"]:
                ucs.setdefault(u, {"refs": set(), "pending": False})
    out_ucs, out_brs = {}, {}

    def hit_uc(uid, reason, steps=(), via=None, pending=False):
        x = g.uc.get(uid)
        if not x:
            return
        e = out_ucs.setdefault(uid, {"id": uid, "title": x["title"], "feature": x["primary"], "status": x["status"],
                                     "version": x["version"], "reason": reason, "steps": set(), "via": set(),
                                     "pending": False})
        rank = ["direct", "rule", "entity"]
        if rank.index(reason) < rank.index(e["reason"]):
            e["reason"] = reason
        e["steps"] |= set(steps)
        if via:
            e["via"].add(via)
        e["pending"] = e["pending"] or pending

    for uid, s in ucs.items():
        hit_uc(uid, "direct", s["refs"], pending=s["pending"])
    for bid in sorted(brs):
        b = g.br.get(bid)
        if not b:
            continue
        out_brs[bid] = {"id": bid, "title": b["title"], "feature": b["feature"], "status": b["status"],
                        "version": b["version"], "ucs": sort_ids(g.ucs_citing_br(bid))}
        for uid in g.ucs_citing_br(bid):
            hit_uc(uid, "rule", via=bid)
    direct = [u for u, e in out_ucs.items() if e["reason"] == "direct"]
    ents = {}
    for uid in direct:
        for en in g.uc[uid]["entities"]:
            ents.setdefault(en, set()).add(uid)
    for uid, x in g.uc.items():
        shared = {en for en in x["entities"] if en in ents} if uid not in direct else set()
        for en in shared:
            hit_uc(uid, "entity", via=en)

    feats = {}
    for uid, e in out_ucs.items():
        x = g.uc[uid]
        for f in x["features"]:
            role = "primary" if f == x["primary"] and e["reason"] == "direct" else "sibling"
            cur = feats.setdefault(f, {"slug": f, "role": role, "via": set()})
            if role == "primary":
                cur["role"] = "primary"
            cur["via"].add(uid)
    for bid, b in out_brs.items():
        if b["feature"]:
            feats.setdefault(b["feature"], {"slug": b["feature"], "role": "primary", "via": set()})["via"].add(bid)

    hit = {u for u, e in out_ucs.items() if e["reason"] in ("direct", "rule")}
    down = {"ux": [], "epics": [], "stories": []}
    for kind, key, p in [("UX", "ux", p) for p in vault.ux_paths()] + [("EP", "epics", p) for p in vault.epic_paths()] + \
            [("US", "stories", p) for p in vault.story_paths()]:
        d = vault.load(p)
        if kind == "UX":
            cited = set(d.fm_list("uc"))
        elif kind == "EP":
            cited = set(d.fm_list("source_ucs"))
        else:
            cited = set()
            steps_hit = set()
            for item in parse_slices(d.fm_list("slice_of") or d.fm_get("slice_of") or ""):
                m = re.match(r"^(UC-\d+)", item.strip())
                uc, ids = expand_slice(item, g.uc.get(m.group(1), {}).get("order", []) if m else [])
                if uc:
                    cited.add(uc)
                    if uc in out_ucs:
                        steps_hit |= {f"{uc} {s}" for s in ids & out_ucs[uc]["steps"]}
        on = sorted(cited & hit)
        if not on:
            continue
        stale = derive_stale(d, kind, {u: {"version": g.uc[u]["version"], "status": g.uc[u]["status"]} for u in g.uc})
        e = {"id": d.id, "title": model.title_of(d), "status": d.fm_get("status") or "", "ucs": on,
             "absorbed": [a for a in d.fm_list("absorbed") if a.split("@")[0] in on],
             "drift": "drifted" if any(s.split("@")[0] in on for s in stale) else
                      ("current" if d.fm_list("absorbed") else "never")}
        if kind == "US":
            e["epic"] = d.fm_get("epic") or ""
            e["hits_steps"] = sorted(steps_hit)
        down[key].append(e)

    questions = []
    for uid in sorted(hit):
        for q in model.open_questions(g.uc[uid]["doc"]):
            questions.append({"where": uid, "question": re.sub(r"\s+", " ", q.text)[:300]})
    for bid in sorted(out_brs):
        for q in model.open_questions(g.br[bid]["doc"]):
            questions.append({"where": bid, "question": re.sub(r"\s+", " ", q.text)[:300]})
    if nid:
        d = vault.load_id(nid)
        s = d.section("Open Questions")
        if s:
            from .vault import questions_in
            for q in questions_in(d, s.start, s.end):
                if not q.checked:
                    questions.append({"where": nid, "question": re.sub(r"\s+", " ", q.text)[:300]})

    def fin(e):
        e = dict(e)
        for k in ("steps", "via"):
            if k in e:
                e[k] = sorted(e[k])
        return e

    order = {"direct": 0, "rule": 1, "entity": 2}
    res = {"$schema_version": 1, "kind": "impact", "int": nid, "generated": today(), "rows": rows,
           "ucs": [fin(e) for e in sorted(out_ucs.values(), key=lambda e: (order[e["reason"]], e["id"]))],
           "brs": [out_brs[b] for b in sorted(out_brs)],
           "features": [fin(f) for f in sorted(feats.values(), key=lambda f: (f["role"] != "primary", f["slug"]))],
           "ux": down["ux"], "epics": down["epics"], "stories": down["stories"], "questions": questions}
    res["summary"] = {
        "signals": len(rows),
        "deferred": sum(1 for r in rows if r["status"] == "rejected"),
        "waiting": sum(1 for r in rows if r["status"] in ("staged", "question", "conflict", "held")),
        "direct_ucs": sum(1 for e in res["ucs"] if e["reason"] == "direct"),
        "rule_ucs": sum(1 for e in res["ucs"] if e["reason"] == "rule"),
        "entity_ucs": sum(1 for e in res["ucs"] if e["reason"] == "entity"),
        "features": len(res["features"]),
        "reopened": sorted(e["id"] for e in res["ucs"] + res["brs"] if e.get("reason", "direct") in ("direct", "rule")
                           and e["status"] in ("draft", "needs-clarification") and _was_approved(g, e["id"])),
        "downstream_stale": sum(1 for k in ("ux", "epics", "stories") for e in res[k] if e["drift"] == "drifted"),
        "open_questions": len(questions),
    }
    return res


def _was_approved(g, ident):
    d = (g.uc.get(ident) or g.br.get(ident) or {}).get("doc")
    return bool(d and d.section("Changelog") and
                any(re.search(r"Status (approved|enriched|consolidated) → draft", x) for x in d.lines[d.section("Changelog").start:d.section("Changelog").end]))


# ---------------------------------------------------------------------------- render

def _t(text, n=110):
    text = re.sub(r"\s+", " ", (text or "").replace("|", "/")).strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def markdown(res):
    s = res["summary"]
    L = [MARK, "",
         f"_{res['generated']}_ · {s['signals']} filed signal row(s) · {s['direct_ucs']} use case(s) changed directly · "
         f"{s['rule_ucs']} through a shared rule · {s['entity_ucs']} to review (shared entity) · {s['features']} feature(s) · "
         f"{s['downstream_stale']} downstream artifact(s) stale · {s['waiting']} waiting · {s['deferred']} deferred · "
         f"{s['open_questions']} open question(s)"]
    if s["reopened"]:
        L.append(f"\n**Re-opened for approval:** {', '.join(s['reopened'])} — an approved spec changed; re-approve via `/approve-uc`.")
    if res["rows"]:
        L += ["", "**Where the signals went**", "", "| Hub row | Signal | Status | Destination |", "|---|---|---|---|"]
        L += [f"| {r['hub']} #{r['row']} | {_t(r['signal'])} | {r['status']} | {_t(r['destination'], 60) or '—'} |" for r in res["rows"]]
    if res["ucs"]:
        L += ["", "**Use cases**", "", "| UC | Feature | Status | Why | Steps / via |", "|---|---|---|---|---|"]
        for e in res["ucs"]:
            why = {"direct": "changed" + (" (waiting on a question)" if e["pending"] else ""),
                   "rule": "a rule it enforces changed", "entity": "shares an entity — review"}[e["reason"]]
            L.append(f"| {e['id']} {_t(e['title'], 50)} | {e['feature'] or '—'} | {e['status']} v{e['version']} | {why} | "
                     f"{', '.join(e['steps'] + e['via']) or '—'} |")
    if res["brs"]:
        L += ["", "**Business rules**", "", "| BR | Feature | Status | Enforced by |", "|---|---|---|---|"]
        L += [f"| {b['id']} {_t(b['title'], 50)} | {b['feature'] or '—'} | {b['status']} v{b['version']} | {', '.join(b['ucs']) or '—'} |"
              for b in res["brs"]]
    if res["features"]:
        L += ["", "**Features touched:** " + ", ".join(
            f"`{f['slug']}`" + (" (sibling via " + ", ".join(f["via"]) + ")" if f["role"] == "sibling" else "")
            for f in res["features"])]
    down = [("UX", e) for e in res["ux"]] + [("Epic", e) for e in res["epics"]] + [("Story", e) for e in res["stories"]]
    if down:
        L += ["", "**Built on these use cases (downstream)**", "", "| Artifact | Status | Built from | Now | Steps hit |", "|---|---|---|---|---|"]
        for kind, e in down:
            L.append(f"| {kind} {e['id']} {_t(e['title'], 40)} | {e['status']} | {', '.join(e['absorbed']) or '—'} | "
                     f"{e['drift']} | {', '.join(e.get('hits_steps') or []) or '—'} |")
    if res["questions"]:
        L += ["", "**Open questions to raise with the other team**", ""]
        L += [f"- {q['where']}: {_t(q['question'], 240)}" for q in res["questions"]]
    return L


def write(vault, nid, dry=False):
    """Regenerate the INT note's ## Impact section and _impact/<INT>.json. Returns (res, written?)."""
    res = walk(vault, nid)
    d = vault.load_id(nid)
    body = [""] + markdown(res) + [""]
    s = d.section("Impact")
    if s is not None:
        def core(lines):
            return [x for x in lines if x.strip() and not x.startswith("_20")]  # the date line alone is no change
        same = core(d.lines[s.start:s.end]) == core(body)
        if same:
            return res, False
        d.replace_body("Impact", body)
    else:
        d.insert_section("Impact", body[1:], after="Open Questions")
    if dry:
        d.verify()
        vault.forget(d.path)
        return res, True
    vault.write(d)
    os.makedirs(vault.impact_dir, exist_ok=True)
    with open(os.path.join(vault.impact_dir, f"{nid}.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return res, True


def notes_touched(vault, since=None):
    """INT notes whose rows a hub Signal Log cites with a status transform writes (applied / staged /
    superseded / held) — the notes a transform run may have moved. ``since`` (YYYY-MM-DD) narrows to
    notes updated or cited by a hub updated on/after that day."""
    out = set()
    for slug in vault.slugs():
        sd = model.signal_doc(vault, slug)
        for r in model.signal_rows(sd) if sd else []:
            if r.status in ("applied", "staged", "superseded", "held", "conflict", "rejected", "question"):
                out |= {n for n, _ in model.expand_int_cites(r.source)}
    return sorted(n for n in out if vault.find(n))


def render(res):
    s = res["summary"]
    head = (f"impact {res.get('int') or '(ad hoc)'}: {s['direct_ucs']} UC direct · {s['rule_ucs']} via rule · "
            f"{s['entity_ucs']} entity-review · {s['features']} feature(s) · {s['downstream_stale']} downstream stale · "
            f"{s['open_questions']} open question(s)")
    lines = [head]
    if s["reopened"]:
        lines.append("  re-opened for approval: " + ", ".join(s["reopened"]))
    for e in res["ucs"]:
        lines.append(f"  {e['reason']:6} {e['id']} [{e['status']}] {', '.join(e['steps'] + e['via'])}")
    for k in ("ux", "epics", "stories"):
        for e in res[k]:
            lines.append(f"  down   {e['id']} [{e['status']}] {e['drift']} {', '.join(e.get('hits_steps') or [])}")
    return "\n".join(lines)


def cli(vault, args):
    if args.int_id == "touched":
        out = []
        for nid in notes_touched(vault):
            res, wrote = write(vault, nid, dry=args.dry) if args.write else (walk(vault, nid), False)
            out.append({"int": nid, "written": wrote, "summary": res["summary"]})
        return out, "\n".join(f"{o['int']}: {'written' if o['written'] else 'unchanged'} · "
                              f"{o['summary']['direct_ucs']} UC direct · {o['summary']['downstream_stale']} downstream stale"
                              for o in out) or "impact: no notes reached a hub"
    if args.int_id:
        if not vault.find(args.int_id):
            raise EngineError(f"{args.int_id}: no such note")
        if args.write:
            res, _ = write(vault, args.int_id, dry=args.dry)
        else:
            res = walk(vault, args.int_id)
        return res, render(res)
    ucs = {u.strip(): set() for u in (args.ucs or "").split(",") if u.strip()}
    res = walk(vault, ucs=ucs, brs=[b.strip() for b in (args.brs or "").split(",") if b.strip()],
               features=[f.strip() for f in (args.features or "").split(",") if f.strip()])
    return res, render(res)
