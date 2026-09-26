"""Traceability coverage — generalised from Agoyu ``check_xr_coverage.py``.

Two traced units:
  * id mode (``--id-pattern``, e.g. ``XR-[A-Z]+-\\d+`` for codebase intake): every id in the universe
    must survive extract → file → transform.
  * row mode (default, communication intake): every intake-note signal row is the unit.

Stages:
  extract    the unit is in an ## Extracted signals row
  file       … and that row is cited by a hub Signal Log row (``INT-### #n``), or the id is named on a hub
  transform  … and the unit reaches a BR/UC: named in one directly, or via note row → hub row → an
             existing Destination id. Filed units whose every hub row is question/conflict/held are
             ``parked`` (awaiting a human) — reported, not failed.
Read-only.
"""
import json
import os
import re

from . import model
from .util import load_json


def _note_ids(vault, notes=None):
    out = []
    for p in vault.note_paths():
        nid = os.path.basename(p)[:-3]
        if notes and nid not in notes:
            continue
        out.append((nid, vault.load(p)))
    return out


def _hub_index(vault, ids):
    """(row_dest, row_state, hub_named_text) over every hub Signal Log."""
    row_dest, row_state, cited, named = {}, {}, set(), []
    for slug in vault.slugs():
        doc = model.signal_doc(vault, slug)
        for r in model.signal_rows(doc):
            dests = {d for d in re.findall(r"\b(?:UC|BR)-\d+\b", r.destination) if d in ids}
            named.append(" ".join(r.cells))
            for key in model.expand_int_cites(r.source):
                cited.add(key)
                row_dest.setdefault(key, set()).update(dests)
                row_state.setdefault(key, set()).add(r.status)
    return row_dest, row_state, cited, "\n".join(named)


def _universe(vault, pattern, universe_file, notes):
    rx = re.compile(pattern)
    if universe_file:
        data = load_json(universe_file) if universe_file.endswith(".json") else open(universe_file).read()
        if isinstance(data, dict) and "rules" in data:
            vals = [r.get("_xr") or r.get("id") or k for k, r in data["rules"].items()]
        elif isinstance(data, dict):
            vals = list(data.keys())
        elif isinstance(data, list):
            vals = [x if isinstance(x, str) else (x.get("id") or x.get("_xr")) for x in data]
        else:
            vals = rx.findall(data)
        return sorted({v for v in vals if v and rx.fullmatch(v)})
    found = set()
    for nid, d in _note_ids(vault, notes):
        found |= set(rx.findall(d.text))
        for a in d.fm_list("attachments"):
            p = os.path.join(vault.root, a)
            if os.path.exists(p) and os.path.getsize(p) < 20_000_000:
                try:
                    found |= set(rx.findall(open(p, encoding="utf-8", errors="ignore").read()))
                except OSError:
                    pass
    return sorted(found)


def run(vault, stage=None, id_pattern=None, universe_file=None, notes=None):
    ids = vault.ids("UC") | vault.ids("BR")
    row_dest, row_state, cited, hub_text = _hub_index(vault, ids)
    art_text = {}
    for p in vault.uc_paths() + vault.br_paths():
        d = vault.load(p)
        art_text[d.id] = d.text
    res = {"mode": "id" if id_pattern else "row"}

    if id_pattern:
        rx = re.compile(id_pattern)
        universe = _universe(vault, id_pattern, universe_file, notes)
        rows = {}
        for nid, d in _note_ids(vault, notes):
            for r in model.note_rows(d):
                for x in set(rx.findall(" ".join(r.cells))):
                    rows.setdefault(x, []).append((nid, int(r.num)))
        extracted = set(rows)
        hub_named = set(rx.findall(hub_text))
        filed = {x for x in extracted if x in hub_named or any(k in cited for k in rows[x])}
        reach = {}
        for aid, t in art_text.items():
            for x in set(rx.findall(t)):
                reach.setdefault(x, set()).add(aid[:2])
        for x, rs in rows.items():
            for k in rs:
                for d in row_dest.get(k, ()):
                    reach.setdefault(x, set()).add(d[:2])
        transformed = set(reach)
        parked = {x for x in filed - transformed
                  if all(row_state.get(k) and row_state[k] <= model.PARKED for k in rows[x])}
        res.update(universe=len(universe), extracted=len(extracted & set(universe) or extracted),
                   filed=len(filed), transformed=len(transformed), parked=len(parked),
                   br=sum(1 for v in reach.values() if "BR" in v), uc=sum(1 for v in reach.values() if "UC" in v))
        sets = {"extract": extracted, "file": filed, "transform": transformed | parked}
        stage = stage or ("transform" if transformed else "file" if filed else "extract")
        miss = [x for x in universe if x not in sets[stage]]
    else:
        units, unit_status, empty_notes = [], {}, []
        for nid, d in _note_ids(vault, notes):
            if (d.fm_get("kind") or "requirement") == "info":
                continue
            rs = model.note_rows(d)
            if not rs:
                if (d.fm_get("status") or "raw") != "raw" or d.section("Extracted signals"):
                    empty_notes.append(nid)
                continue
            for r in rs:
                units.append((nid, int(r.num)))
                unit_status[(nid, int(r.num))] = (r.get("Status") or "").strip().lower()
        extracted = set(units)
        filed = {u for u in units if u in cited or unit_status[u] == "rejected"}
        transformed = {u for u in filed if unit_status[u] == "rejected" or
                       (row_dest.get(u) and (row_state.get(u, set()) & model.PROCESSED))}
        parked = {u for u in filed - transformed if row_state.get(u) and row_state[u] <= model.PARKED | model.PROCESSED}
        parked |= {u for u in extracted - filed if unit_status[u] in ("question", "conflict")}
        res.update(notes_without_table=empty_notes, units=len(units), extracted=len(extracted), filed=len(filed),
                   transformed=len(transformed), parked=len(parked))
        stage = stage or ("transform" if transformed else "file" if filed else "extract")
        need = {"extract": extracted, "file": filed | parked, "transform": transformed | parked}[stage]
        miss = [f"{n} #{r}" for n, r in sorted(units) if (n, r) not in need]
        if stage == "extract":
            miss = empty_notes + miss
    res["stage"] = stage
    res["missing"] = miss
    return res


def report(res, list_all=False):
    lines = []
    if res["mode"] == "id":
        lines.append(f"ids: {res['universe']}")
        lines.append(f"  extract   {res['extracted']:>6}  in a signal row")
        lines.append(f"  file      {res['filed']:>6}  cited by a hub Signal Log row")
        lines.append(f"  transform {res['transformed']:>6}  reached a BR or UC (BR {res['br']} · UC {res['uc']})")
    else:
        lines.append(f"signal rows: {res['units']}")
        lines.append(f"  extract   {res['extracted']:>6}  rows in ## Extracted signals")
        lines.append(f"  file      {res['filed']:>6}  cited by a hub Signal Log row (or rejected)")
        lines.append(f"  transform {res['transformed']:>6}  reached an applied UC/BR (or rejected)")
        if res.get("notes_without_table"):
            lines.append(f"  notes past raw with no signal table: {', '.join(res['notes_without_table'])}")
    lines.append(f"  parked    {res['parked']:>6}  awaiting a human answer (question/conflict/held)")
    lines.append(f"stage checked: {res['stage']} — missing {len(res['missing'])}")
    if res["missing"]:
        shown = res["missing"] if list_all else res["missing"][:20]
        lines.append("  " + ", ".join(shown) + ("" if list_all or len(res["missing"]) <= 20 else f" … (+{len(res['missing']) - 20}, --list for all)"))
    return "\n".join(lines)


def as_json(res):
    return json.dumps(res, indent=2)
