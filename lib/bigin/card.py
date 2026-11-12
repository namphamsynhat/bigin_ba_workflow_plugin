"""Dev cards: one short page per screen (and per back-end process with no screen) that a human can read,
check and justify. A rendered view of what the vault already holds. No LLM call.

    bigin card <EP-###|US-###> [--write]

Each row either cites where it came from (an intake signal, a BR, a UC step) or is listed under
**AI assumed**. That list is the review surface: the places where AI judgement entered instead of the
client's words.

Card stack for one epic (or the cards one story touches):
  screen cards   one per UX spec § 2 inventory row whose ``Serves`` meets a story's slice / AC tags
  process cards  one per use case for the sliced steps no screen serves (system-only work)

Per card: purpose · stories · Before → After (from the source notes' ``_snapshots/<INT>/changes.json``)
· rules · unchanged but affected (other screens serving a changed step) · out of scope (story § 7)
· AI assumed · open questions · acceptance titles · size inputs (counted, never hours).

AI assumed, deterministic sources:
  design        a UX element / state whose ``Grounded by`` names no UC step, BR or EN field
  no signal     a sliced UC step no Signal Log row names as its destination
  not client    a step named only by Signal Log rows that cite no intake note (research, inference)
  declared      the story's § 8 Assumptions
Prototype copy that contradicts a BR is not detected here — it needs a reader.

``--write`` saves ``03-Epics-Stories/EP-### …/_cards.md``. The command works on demand in any project;
``dev_card: on`` in project.md asks the stories stage to write it at close as well.
"""
import json
import os
import re

from . import design, impact, model, stories
from .util import EngineError

UNIT = re.compile(r"^[SAE]\d+$")
GROUNDED = re.compile(r"\bUC-\d+\b|\b[SAE]\d+\b|\bBR-\d+\b|\bEN-\d+")
STEP_IN_LINE = re.compile(r"\*\*([SAE]\d+)\*\*|^###\s+\**([AE]\d+)\b")
MAX_CELL = 90
FILE_NAME = "_cards.md"


def _short(text, n=MAX_CELL):
    t = re.sub(r"\s+", " ", (text or "").replace("|", "/")).strip()
    t = re.sub(r"<br>", " · ", t)
    return t if len(t) <= n else t[: n - 1] + "…"


def _lines_text(lines, n=70):
    """Changed lines → readable text: table rows lose their pipes and the bold step id."""
    out = []
    for x in lines:
        x = x.strip()
        if x.startswith("|"):
            cells = [c.strip() for c in x.strip("|").split("|")]
            x = " / ".join(c for c in cells if c and not re.match(r"^\**[SAE]\d+\**$", c) and not re.match(r"^:?-+:?$", c))
        out.append(x.lstrip("#").strip())
    return _short(" · ".join(o for o in out if o), n)


def _bullets(lines):
    out = []
    for x in lines:
        m = re.match(r"^\s*[*-]\s+(?:\[[ xX]\]\s+)?(.*\S)\s*$", x)
        if m and not m.group(1).startswith("`<"):
            out.append(m.group(1).strip("`"))
    return out


def _notes_part(text, label):
    """Bullets under ``**<label>**`` in story § 8 (Still open / Decisions / Assumptions)."""
    out, inside = [], False
    for x in stories.section(text, 8):
        m = re.match(r"^\s*\*\*(.+?)\*\*\s*$", x)
        if m:
            inside = m.group(1).strip().lower() == label.lower()
            continue
        if inside:
            out.append(x)
    return _bullets(out)


def _scenarios(text):
    """[(title, {step ids}, {BR ids})] from story § 6."""
    out = []
    for x in stories.section(text, 6):
        m = re.match(r"^\s*(?:[-*]\s*)?(?:\*\*)?Scenario(?: Outline)?:\s*(.*?)(?:\*\*)?\s*$", x)
        if not m:
            continue
        raw = m.group(1)
        tags = " ".join(re.findall(r"\[([^\]]+)\](?!\()", raw))
        title = re.sub(r"\s*\[[^\]]+\](?!\()", "", raw).replace("**", "").strip()
        out.append((title, set(re.findall(r"\b[SAE]\d+\b", tags)), set(re.findall(r"\bBR-\d+\b", tags))))
    return out


# ---------------------------------------------------------------------------- reading the vault

class _Ctx:
    def __init__(self, vault, epic):
        self.v, self.epic = vault, epic
        self.slug = (epic.fm_get("feature") or "").strip()
        self.ucs, self.brs = {}, {}
        self.spec = design.spec_of(vault, self.slug) if self.slug else None
        self.parsed = design.parse(self.spec) if self.spec else None
        self.signals = self._signals()

    def uc(self, uid):
        if uid not in self.ucs:
            p = self.v.find(uid)
            self.ucs[uid] = self.v.load(p) if p else None
        return self.ucs[uid]

    def br_title(self, bid):
        if bid not in self.brs:
            p = self.v.find(bid)
            self.brs[bid] = model.title_of(self.v.load(p)) if p else ""
        return self.brs[bid]

    def _signals(self):
        """{(uc, step) or (uc, None) or (BR, None): [(cite or None, row #, slug)]} from every Signal Log."""
        out = {}
        for slug in self.v.slugs():
            sd = model.signal_doc(self.v, slug)
            for r in model.signal_rows(sd) if sd else []:
                if r.status in ("rejected", "superseded", "withdrawn"):
                    continue
                cites = sorted(model.expand_int_cites(r.source))
                cite = ", ".join(f"{n} #{k}" for n, k in cites[:3]) if cites else None
                ucs, brs = impact._dests(r.destination)
                for u, refs in ucs.items():
                    for ref in (refs or {None}):
                        out.setdefault((u, ref), []).append((cite, r.num, slug))
                for b in brs:
                    out.setdefault((b, None), []).append((cite, r.num, slug))
        return out

    def sourcing(self, uid, sid):
        """'client' | 'not client' | 'none' for one UC step. A row naming the whole UC counts for every step."""
        rows = self.signals.get((uid, sid), []) + self.signals.get((uid, None), [])
        if not rows:
            return "none", []
        cites = [c for c, _, _ in rows if c]
        return ("client" if cites else "not client"), rows

    def cite_for(self, key, ref, nid):
        """The Signal Log cite of ``nid`` that names this step or rule (``INT-002 #4``), else the note id."""
        rows = self.signals.get((key, ref), []) + self.signals.get((key, None), [])
        cites = [c for c, _, _ in rows if c and c.startswith(nid + " ")]
        return cites[0] if cites else nid


def _story_units(ctx, s):
    """{(uc, step id)} a story slices or tags."""
    units, story_ucs = set(), []
    for item in stories.parse_slices(s.fm_get("slice_of") or ""):
        m = re.match(r"^(UC-\d+)", item.strip())
        d = ctx.uc(m.group(1)) if m else None
        order = [x.id for x in model.steps(d) if not x.dropped] if d else []
        u, ids = stories.expand_slice(item, order)
        if u:
            story_ucs.append(u)
            units |= {(u, i) for i in ids}
    for u, sid in stories.ac_tags(s.text):
        u = u or (story_ucs[0] if len(story_ucs) == 1 else None)
        if u:
            units.add((u, sid))
    return units


def _changes(ctx):
    """[{target, ref, units, removed, added, int}] — every change any intake note recorded (``bigin apply``'s
    Before / After log). The cards keep only the ones on their own steps and rules."""
    out = []
    base = os.path.join(ctx.v.inbox, "_snapshots")
    for nid in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        p = os.path.join(ctx.v.inbox, "_snapshots", nid, "changes.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            log = json.load(f)
        for tid, e in log.items():
            for c in e.get("changes", []):
                ref = (c.get("ref") or "").strip()
                units = {ref} if UNIT.match(ref) else set()
                for line in (c.get("removed") or []) + (c.get("added") or []):
                    for a, b in STEP_IN_LINE.findall(line):
                        units.add(a or b)
                out.append({"target": tid, "ref": ref, "units": units, "created": bool(e.get("created")),
                            "removed": c.get("removed") or [], "added": c.get("added") or [], "int": nid})
    return out


def _block_tables(doc, start, end):
    """{'elements': [...], 'states': [...], 'interactions': [...]} dict rows of one § 3 screen block."""
    from .vault import find_tables
    out = {"elements": [], "states": [], "interactions": []}
    for t in find_tables(doc, start, end):
        hdr = [h.strip() for h in t.header]
        key = {"Element": "elements", "State": "states", "Control": "interactions"}.get(hdr[0] if hdr else "")
        if key:
            out[key] += [dict(zip(hdr, [c.strip() for c in r])) for r in t.rows()]
    return out


# ---------------------------------------------------------------------------- building cards

def build(vault, ident):
    path = vault.find(ident)
    if not path:
        raise EngineError(f"{ident}: no such epic or story")
    doc = vault.load(path)
    only = None
    if ident.startswith("US-"):
        only = doc.id
        ep_path = vault.find((doc.fm_get("epic") or "").strip())
        if not ep_path:
            raise EngineError(f"{ident} names epic `{doc.fm_get('epic')}`, which has no file")
        epic = vault.load(ep_path)
    elif ident.startswith("EP-"):
        epic = doc
    else:
        raise EngineError("bigin card takes an EP-### or a US-###")
    ctx = _Ctx(vault, epic)
    all_stories = [vault.load(p) for p in vault.story_paths()]
    mine = [s for s in all_stories if (s.fm_get("epic") or "").strip() == epic.id]
    if only:
        mine = [s for s in mine if s.id == only]
    units = {s.id: _story_units(ctx, s) for s in mine}
    changes = _changes(ctx)
    sources = sorted({n for s in mine for n in s.fm_list("sources")} | {c["int"] for c in changes
                     if c["target"] in set(epic.fm_list("source_ucs"))})
    cr = bool(str(epic.fm_get("cr") or "").lower() in ("true", "yes")) or any(s.fm_get("delta_of") for s in mine)

    screens, served_all = [], set()
    inv = ctx.parsed["inventory"] if ctx.parsed else []
    for row in inv:
        serves = design.serves(row.get("Serves", ""))
        served_all |= serves
        names = {design._name(row.get("Screen", "")), design._name(row.get("View ID", ""))}
        on = [s for s in mine if units[s.id] & serves or names & set(s.fm_list("screens"))]
        if on:
            screens.append((row, serves, on))

    cards = [_screen_card(ctx, row, serves, on, units, changes, cr, inv) for row, serves, on in screens]
    rest = {}
    for s in mine:
        for u, sid in sorted(units[s.id] - served_all):
            rest.setdefault(u, {}).setdefault(sid, set()).add(s.id)
    for uid in sorted(rest):
        cards.append(_process_card(ctx, uid, rest[uid], mine, units, changes, cr))
    seen = set()
    for c in cards:
        keep = []
        for a in c["assumed"]:
            if a["why"].startswith("declared"):
                if a["what"] in seen:
                    continue
                seen.add(a["what"])
            keep.append(a)
        c["assumed"] = keep
    affected = _affected(vault, sources, {c["id"] for c in cards}, epic)
    return {"kind": "card", "epic": epic.id, "title": model.title_of(epic), "feature": ctx.slug,
            "story": only, "variant": "CR" if cr else "New", "sources": sources,
            "ux": ctx.spec.id if ctx.spec else None, "snapshot": (epic.fm_get("snapshot") or "none").strip(),
            "cards": cards, "affected": affected, "folder": os.path.dirname(epic.path)}


def _common(ctx, on, my_units, changes, rule_ids):
    """The parts a screen card and a process card share."""
    rules = sorted(rule_ids | {b for s in on for b in s.fm_list("rules")}
                   | {b for s in on for _, _, brs in _scenarios(s.text) for b in brs})
    rows = []
    for c in changes:
        if c["target"].startswith("UC-"):
            hit = {(c["target"], u) for u in c["units"]} & my_units
            if not hit and not (c["created"] and any(u == c["target"] for u, _ in my_units)):
                continue
            where = f"{c['target']} {' '.join(sorted(x for _, x in hit))}".strip()
        elif c["target"] in rules:
            where = c["target"]
        else:
            continue
        before = "(none)" if c["created"] or not c["removed"] else _lines_text(c["removed"])
        after = _lines_text(c["added"]) or "(removed)"
        ref = next(iter(sorted(c["units"])), None)
        cite = ctx.cite_for(c["target"], ref, c["int"])
        rows.append({"where": where, "before": before, "after": after, "cite": cite})
    out_scope = list(dict.fromkeys(b for s in on for b in _bullets(stories.section(s.text, 7))))
    assumed = []
    for uid, sid in sorted(my_units):
        kind, srows = ctx.sourcing(uid, sid)
        if kind == "client":
            continue
        d = ctx.uc(uid)
        st = next((x for x in model.steps(d) if x.id == sid), None) if d else None
        fl = next((x for x in model.flows(d) if x.id == sid), None) if d and not st else None
        what = _short(st.actor or st.system, 60) if st else (_short(fl.name, 60) if fl else "")
        why = "no client signal" if kind == "none" else \
            "signal cites no intake note (hub rows " + ", ".join(f"#{n}" for _, n, _ in srows[:3]) + ")"
        assumed.append({"what": f"{uid} {sid} {what}".strip(), "why": why})
    for s in on:
        for a in _notes_part(s.text, "Assumptions"):
            assumed.append({"what": _short(a, 70), "why": f"declared in {s.id} § 8"})
    questions = []
    for s in on:
        questions += [f"{s.id}: {_short(q, 70)}" for q in _notes_part(s.text, "Still open")]
    for uid in sorted({u for u, _ in my_units}):
        d = ctx.uc(uid)
        questions += [f"{uid}: {_short(q.text, 70)}" for q in (model.open_questions(d) if d else [])]
    acs = []
    for s in on:
        for title, steps_, brs in _scenarios(s.text):
            if {(u, x) for u, x in my_units if x in steps_} or (not steps_ and (not brs or brs & set(rules))):
                acs.append(f"{s.id} {title}")
    return {"rules": [{"id": b, "title": ctx.br_title(b)} for b in rules], "changes": rows,
            "out_of_scope": out_scope, "assumed": assumed, "questions": list(dict.fromkeys(questions)),
            "acceptance": acs}


def _screen_card(ctx, row, serves, on, units, changes, cr, inv):
    view = design._name(row.get("View ID", "")) or design.kebab(row.get("Screen", ""))
    name = design._name(row.get("Screen", ""))
    my_units = serves & set().union(*(units[s.id] for s in on)) or serves
    block = ctx.parsed["blocks"].get(name)
    tables = _block_tables(ctx.spec, *block) if block else {"elements": [], "states": [], "interactions": []}
    rule_ids = set()
    for r in tables["elements"] + tables["states"]:
        rule_ids |= set(re.findall(r"\bBR-\d+\b", r.get("Grounded by", "")))
    part = _common(ctx, on, my_units, changes, rule_ids)
    for r in tables["elements"] + tables["states"]:
        g = r.get("Grounded by", "")
        if not GROUNDED.search(g):
            label = r.get("Element") or r.get("State") or "?"
            part["assumed"].insert(0, {"what": _short(f"{label} — {r.get('Content / copy') or r.get('What the user sees') or ''}", 70),
                                       "why": f"design only ({_short(g, 30) or 'no ground'})"})
    changed_units = {(c["target"], u) for c in changes for u in c["units"]} & my_units
    others = []
    for r in inv:
        v2 = design._name(r.get("View ID", ""))
        if v2 != view and design.serves(r.get("Serves", "")) & changed_units:
            others.append(v2 or design._name(r.get("Screen", "")))
    ents = [e for e in re.findall(r"\bEN-\d+\b", row.get("Entities", ""))]
    return dict(part, type="screen", id=view, name=name, purpose=_short(row.get("Purpose", ""), 100),
                actor=_short(row.get("Actor", ""), 40), stories=[s.id for s in on],
                variant="CR" if cr else "New", regression=others,
                size={"elements": len(tables["elements"]), "states": len(tables["states"]),
                      "actions": len(tables["interactions"]), "rules": len(part["rules"]), "entities": len(ents)})


def _process_card(ctx, uid, steps_, mine, units, changes, cr):
    from .changeset import field_value
    d = ctx.uc(uid)
    on = [s for s in mine if any(s.id in v for v in steps_.values())]
    my_units = {(uid, sid) for sid in steps_}
    part = _common(ctx, on, my_units, changes, set())
    flow = []
    order = {x.id: i for i, x in enumerate(model.steps(d))} if d else {}
    for sid in sorted(steps_, key=lambda x: (x[0] != "S", order.get(x, 999), x)):
        st = next((x for x in model.steps(d) if x.id == sid), None) if d else None
        fl = next((x for x in model.flows(d) if x.id == sid), None) if d and not st else None
        flow.append(f"{sid} " + _short(st.system or st.actor if st else (fl.name if fl else ""), 80))
    title = model.title_of(d) if d else uid
    return dict(part, type="process", id=f"{uid}-process", name=f"{uid} {title}",
                purpose=_short(field_value(d, "1", "Business Need / Goal") if d else "", 100),
                trigger=_short(field_value(d, "1", "Trigger") if d else "", 80), steps=flow,
                stories=[s.id for s in on], variant="CR" if cr else "New", regression=[],
                size={"steps": len(flow), "rules": len(part["rules"])})


def _affected(vault, sources, card_ids, epic):
    """Use cases and rules a source note reaches indirectly (shared rule or entity), outside this epic."""
    own = set(epic.fm_list("source_ucs"))
    out = {}
    for nid in sources:
        try:
            res = impact.walk(vault, nid)
        except EngineError:
            continue
        for e in res["ucs"]:
            if e["reason"] != "direct" and e["id"] not in own:
                out.setdefault(e["id"], f"{e['id']} {e['title']} (via {', '.join(e.get('via') or []) or e['reason']})")
    return [out[k] for k in sorted(out)]


# ---------------------------------------------------------------------------- rendering

def render(res):
    head = f"# Dev cards — {res['epic']} {res['title']}" + (f" · {res['story']}" if res["story"] else "")
    lines = [head, "",
             f"<!-- engine-owned: `scripts/bigin card {res['story'] or res['epic']}` regenerates this file. Edit the story, "
             f"UC or UX spec instead — never this page. -->", "",
             f"{res['variant']} · feature `{res['feature'] or '—'}` · design {res['ux'] or 'none'} · snapshot {res['snapshot']}"
             + (f" · from {', '.join(res['sources'])}" if res["sources"] else ""), ""]
    if not res["cards"]:
        lines += ["_No card: this epic has no story slices yet._"]
    total_assumed = sum(len(c["assumed"]) for c in res["cards"])
    lines += [f"**{len(res['cards'])} card(s) · {total_assumed} AI-assumed line(s) to check**", ""]
    for c in res["cards"]:
        lines += _render_card(c) + [""]
    if res["affected"]:
        lines += ["## Unchanged but affected (regression)", ""] + [f"- {a}" for a in res["affected"]] + [""]
    return "\n".join(lines).rstrip() + "\n"


def _render_card(c):
    if c["type"] == "screen":
        out = [f"## {c['id']} · {c['name']}   [{c['variant']}]",
               f"Purpose: {c['purpose'] or '—'}" + (f" · Actor: {c['actor']}" if c["actor"] else ""),
               f"Stories: {', '.join(c['stories'])}"]
    else:
        out = [f"## {c['name']} — back-end process   [{c['variant']}]",
               f"Purpose: {c['purpose'] or '—'}",
               f"Trigger: {c['trigger'] or '—'}",
               f"Stories: {', '.join(c['stories']) or '—'}",
               "Steps: " + (" → ".join(c["steps"]) or "—")]
    if c["changes"]:
        out += ["Change (Before → After):", "", "| Where | Before | After | Source |", "|---|---|---|---|"]
        out += [f"| {r['where']} | {r['before']} | {r['after']} | {r['cite']} |" for r in c["changes"]]
        out.append("")
    elif c["variant"] == "New":
        out.append("Change: new — nothing existed before")
    else:
        out.append("Change: none recorded on this card")
    if c["rules"]:
        out.append("Rules: " + " · ".join(f"{r['id']} {_short(r['title'], 50)}".strip() for r in c["rules"]))
    if c["regression"]:
        out.append("Unchanged but affected: " + ", ".join(c["regression"]))
    if c["out_of_scope"]:
        out.append("Out of scope: " + " · ".join(_short(x, 60) for x in c["out_of_scope"]))
    if c["assumed"]:
        out.append("AI assumed (check these!):")
        out += [f"  - {a['what']} — {a['why']}" for a in c["assumed"]]
    else:
        out.append("AI assumed: none found")
    out.append("Open questions: " + ("; ".join(c["questions"]) if c["questions"] else "none"))
    out.append("Acceptance: " + (" · ".join(c["acceptance"]) if c["acceptance"] else "none"))
    out.append("Size inputs: " + " · ".join(f"{k} {v}" for k, v in c["size"].items()))
    return out


def write(vault, res, text):
    p = os.path.join(res["folder"], FILE_NAME)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return vault.rel(p)
