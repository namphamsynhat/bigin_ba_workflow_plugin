"""Dev handoff beyond the cards: the build pack (for the coding agent), the estimate sheet (for the dev to fill
and the BA to check), and paste-ready Jira text. All rendered from the vault; no LLM call.

    bigin card US-###|EP-### --for agent [--write]   build pack: one self-contained file per story
    bigin card EP-### --estimate                      write / refresh EP-### …/_estimate.md
    bigin card EP-###|US-### --for jira [--write]     copy-and-paste text for Jira (a human posts it; nothing is sent)

Build pack (``_build/US-###.md`` in the epic folder): the story as written, the UC steps / flows it slices,
the full text of every BR it cites, the fields of every entity it cites, the prototype files for its screens,
a ``US-###@version`` stamp, and the rules the agent follows (test names carry the AC, stop and ask on a gap).

Estimate sheet (``_estimate.md``): one section per card; one row per scope item (a Before → After row or an
acceptance criterion), keyed by a stable id ``<card> · <item>``. The dev fills Task / Hours (with AI) / Notes
and may add more task lines under a key by leaving the Key cell blank. Refreshing keeps every dev line, adds
new keys, and marks a key whose source is gone ``source removed`` (never deletes it). Totals are recomputed.
"""
import os
import re

from . import card as cardmod
from . import design, model, stories
from .util import EngineError, today

PACK_DIR = "_build"
ESTIMATE = "_estimate.md"
INLINE_MAX = 40_000
EST_HEAD = "| Key | Scope item | Task | Hours (with AI) | Notes |"
EST_SEP = "|---|---|---|---|---|"


# ---------------------------------------------------------------------------- build pack

def _story_body(doc):
    out, skip = [], False
    for x in stories._mask(doc.lines[doc.body_start:]):
        if x.startswith("## "):
            skip = x[3:].strip().lower().startswith("changelog")
        if not skip:
            out.append(x.rstrip())
    while out and not out[-1].strip():
        out.pop()
    return out


def _snapshot_files(folder, snap, screen_names):
    """[(label, path, inline text or None)] prototype files for these screens."""
    if not snap or snap == "none":
        return []
    base = os.path.join(folder, "_snapshot", snap)
    if not os.path.isdir(base):
        return []
    slugs = {design.kebab(n) for n in screen_names if n}
    out = []
    for dp, _dn, fns in os.walk(base):
        for fn in sorted(fns):
            low = fn.lower()
            if not (low.endswith(".html") or low.endswith(".png")):
                continue
            stem = design.kebab(os.path.splitext(fn)[0])
            hit = any(s and s in stem for s in slugs) or fn == "index.html"
            if not hit:
                continue
            p = os.path.join(dp, fn)
            text = None
            if low.endswith(".html") and os.path.getsize(p) <= INLINE_MAX:
                with open(p, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            out.append((fn, os.path.relpath(p, folder), text))
    return out


def build_pack(vault, sid):
    path = vault.find(sid)
    if not path:
        raise EngineError(f"{sid}: no such story")
    s = vault.load(path)
    folder = os.path.dirname(path)
    ver = str(s.fm_get("version") or "")
    lines = [f"# Build pack — {s.id}@{ver} {model.title_of(s)}", "",
             f"<!-- engine-owned: `scripts/bigin card {s.id} --for agent --write` regenerates this file from the vault. -->", "",
             f"- Story: `{s.id}@{ver}` · status {s.fm_get('status') or '—'} · epic {s.fm_get('epic') or '—'}",
             f"- Built from: {', '.join(s.fm_list('absorbed')) or '—'}"
             + (f" · STALE: {', '.join(s.fm_list('stale'))}" if s.fm_list("stale") else ""),
             f"- Delta of: {s.fm_get('delta_of')}" if s.fm_get("delta_of") else "- Delta of: —",
             f"- Intake: {', '.join(s.fm_list('sources')) or '—'} · Jira: {', '.join(s.fm_list('jira')) or '—'}", ""]
    if (s.fm_get("status") or "") != "approved":
        lines += ["> **Not approved yet.** Build only after `/approve-story`; this pack may still change.", ""]
    body = [("#" + x if x.startswith("## ") else x) for x in _story_body(s) if not x.startswith("# ")]
    while body and not body[0].strip():
        body.pop(0)
    lines += ["## Story", ""] + body + [""]

    lines += ["## Use case steps this story delivers", ""]
    brs, ents = set(s.fm_list("rules")), set(s.fm_list("entities"))
    for item in stories.parse_slices(s.fm_get("slice_of") or ""):
        m = re.match(r"^(UC-\d+)", item.strip())
        p = vault.find(m.group(1)) if m else None
        if not p:
            lines += [f"- {item}: use case not found", ""]
            continue
        d = vault.load(p)
        order = [x.id for x in model.steps(d) if not x.dropped]
        _, ids = stories.expand_slice(item, order)
        brs |= set(model.s4_brs(d))
        ents |= set(d.fm_list("entities"))
        lines += [f"### {d.id}@{d.fm_get('version') or ''} {model.title_of(d)} — {item}", "",
                  "| Step | Actor | System |", "|---|---|---|"]
        lines += [f"| {x.id} | {x.actor} | {x.system} |" for x in model.steps(d) if x.id in ids and not x.dropped]
        for f in model.flows(d):
            if f.id in ids and not f.dropped:
                lines += ["", f"**{f.id}: {f.name}** {re.sub(r'\s+', ' ', f.body or '').strip()}"]
        lines.append("")
    brs |= set(re.findall(r"\bBR-\d+\b", " ".join(stories.section(s.text, 6))))

    lines += ["## Business rules (full text)", ""]
    for b in sorted(brs):
        p = vault.find(b)
        if not p:
            lines.append(f"- **{b}** — not found")
            continue
        d = vault.load(p)
        lines.append(f"- **{b}@{d.fm_get('version') or ''} {model.title_of(d)}** — {model.br_statement(d) or '(no statement)'}")
    lines.append("" if brs else "- none")
    if not brs:
        lines.append("")

    lines += ["## Entities", ""]
    for e in sorted(ents):
        info = design._entity(vault, e)
        if info.get("missing"):
            lines.append(f"- **{e}** — not found")
            continue
        lines += [f"### {e} {info['title']}", ""]
        fields = info.get("fields") or []
        if fields:
            keys = list(dict.fromkeys(k for f in fields for k in f))[:6]
            lines += ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
            lines += ["| " + " | ".join(f.get(k, "") for k in keys) + " |" for f in fields]
        lines.append("")
    if not ents:
        lines += ["- none", ""]

    lines += ["## Prototype", ""]
    snap = (s.fm_get("snapshot") or "none").strip()
    files = _snapshot_files(folder, snap, s.fm_list("screens"))
    if not files:
        lines += [f"- snapshot: {snap} — no prototype files found for this story's screens", ""]
    for name, rel, text in files:
        lines.append(f"- `{rel}`")
    lines.append("")
    for name, rel, text in files:
        if text is not None:
            lines += [f"### {name}", "", "```html", text.rstrip(), "```", ""]

    lines += ["## Rules for the coding agent", "",
              f"1. Build exactly this story ({s.id}@{ver}). Put `{s.id}@{ver}` in the PR title or description.",
              f"2. Name each test after the acceptance criterion it proves, e.g. `{s.id} AC1 — <title>`. Every AC needs a test.",
              "3. Business rules above are the source of truth. If the prototype disagrees with a rule, follow the rule and say so in the PR.",
              "4. If this pack does not answer something, stop and ask. Do not guess. Write the question in the PR "
              "so the BA can add it to the story § 8.",
              "5. Do not change behaviour listed under § 7 Boundaries.", ""]
    return {"id": s.id, "version": ver, "folder": folder, "text": "\n".join(lines).rstrip() + "\n"}


def write_pack(vault, pack):
    d = os.path.join(pack["folder"], PACK_DIR)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{pack['id']}.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(pack["text"])
    return vault.rel(p)


def packs(vault, ident):
    if ident.startswith("US-"):
        return [build_pack(vault, ident)]
    path = vault.find(ident)
    if not path or not ident.startswith("EP-"):
        raise EngineError(f"{ident}: no such epic or story")
    ep = vault.load(path)
    mine = [vault.load(p) for p in vault.story_paths()]
    return [build_pack(vault, s.id) for s in mine if (s.fm_get("epic") or "").strip() == ep.id]


# ---------------------------------------------------------------------------- estimate sheet

def _scope_rows(res):
    """[(card label, [(key, item)])] the sheet's sections, from the card stack."""
    out = []
    for c in res["cards"]:
        cid = c["id"]
        items = [(f"{cid} · {r['where']}", f"Change: {r['before']} → {r['after']}") for r in c["changes"]]
        items += [(f"{cid} · {a}", f"AC: {a}") for a in c["acceptance"]]
        if not items:
            items = [(f"{cid} · build", "Build this card")]
        label = c["name"] if c["type"] == "process" else f"{c['id']} · {c['name']}"
        out.append((label, items))
    return out


def _parse_sheet(text):
    """{key: [row cells]} (continuation rows ride on the key above) + the free Assumptions lines."""
    rows, last, assumptions, in_assume = {}, None, [], False
    for line in text.splitlines():
        if line.startswith("## "):
            in_assume = line[3:].strip().lower().startswith("dev assumptions")
            continue
        if in_assume:
            assumptions.append(line)
            continue
        if not line.startswith("|") or line.startswith(EST_HEAD) or line.startswith(EST_SEP) or line.startswith("| **Total"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cells += [""] * (5 - len(cells))
        key = cells[0]
        if key:
            last = key
            rows.setdefault(key, []).append(cells[:5])
        elif last:
            rows[last].append(cells[:5])
    while assumptions and not assumptions[-1].strip():
        assumptions.pop()
    return rows, assumptions


def _hours(cell):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)", cell or "")
    return float(m.group(1)) if m else 0.0


def estimate(vault, ident, dry=False):
    res = cardmod.build(vault, ident)
    p = os.path.join(res["folder"], ESTIMATE)
    old, assumptions = ({}, [])
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            old, assumptions = _parse_sheet(f.read())
    sections = _scope_rows(res)
    live = {k for _, items in sections for k, _ in items}
    lines = [f"# Estimate — {res['epic']} {res['title']}", "",
             "<!-- Dev: fill Task, Hours (with AI) and Notes. Add more task lines under a key by leaving Key blank. "
             f"`scripts/bigin card {res['epic']} --estimate` refreshes the scope rows and totals and keeps your lines. -->", "",
             f"{res['variant']} · refreshed {today()} · cards: `_cards.md`", "", ""]
    grand, added, removed = 0.0, 0, 0
    for label, items in sections:
        lines += [f"## {label}", "", EST_HEAD, EST_SEP]
        sub = 0.0
        for key, item in items:
            prev = old.get(key)
            if not prev:
                added += 1
                prev = [[key, item, "", "", ""]]
            for i, cells in enumerate(prev):
                cells = list(cells)
                if i == 0:
                    cells[0], cells[1] = key, cardmod._short(item, 110)
                sub += _hours(cells[3])
                lines.append("| " + " | ".join(cells) + " |")
        lines += [f"| **Total** | | | **{sub:g}** | |", ""]
        grand += sub
    gone = [k for k in old if k not in live]
    if gone:
        lines += ["## Source removed", "", "<!-- scope items no card shows any more — the dev's lines are kept; "
                  "delete them once the BA agrees -->", "", EST_HEAD, EST_SEP]
        for k in gone:
            for cells in old[k]:
                cells = list(cells)
                if "source removed" not in cells[4]:
                    cells[4] = (cells[4] + " · source removed").strip(" ·") if cells[0] else cells[4]
                lines.append("| " + " | ".join(cells) + " |")
        removed = len(gone)
        lines.append("")
    lines += ["## Dev assumptions", ""] + (assumptions or ["- "]) + [""]
    lines.insert(6, f"**Total: {grand:g} h (with AI)**")
    text = "\n".join(lines).rstrip() + "\n"
    if not dry:
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    return {"path": vault.rel(p), "total": grand, "added": added, "source_removed": removed,
            "sections": len(sections), "text": text}


# ---------------------------------------------------------------------------- Jira paste text

JIRA_FILE = "_jira.md"


def jira_text(vault, ident):
    """Copy-and-paste text for Jira, written for a human to post: the epic, then one block per story with a
    Summary line and a Description (the story's cards + its acceptance criteria). Nothing is sent anywhere."""
    if not ident.startswith(("EP-", "US-")):
        raise EngineError("--for jira takes an EP-### or a US-###")
    res = cardmod.build(vault, ident)
    ep = vault.load(vault.find(res["epic"]))
    only = res["story"]
    lines = [f"# Jira paste text — {ep.id} {model.title_of(ep)}", "",
             "<!-- engine-owned: `scripts/bigin card " + (only or ep.id) + " --for jira --write` regenerates this file. "
             "Copy each block into Jira by hand. -->", ""]
    if not only:
        lines += [f"## Epic — {ep.id}", "", f"**Summary:** {ep.id} {model.title_of(ep)}", "", "**Description:**", "",
                  f"Feature `{res['feature'] or '—'}` · {res['variant']} · {len(res['cards'])} card(s): "
                  + ", ".join(c["id"] for c in res["cards"]), ""]
    for p in vault.story_paths():
        s = vault.load(p)
        if (s.fm_get("epic") or "").strip() != ep.id or (only and s.id != only):
            continue
        intake = ", ".join(s.fm_list("jira"))
        lines += [f"## Story — {s.id}", "", f"**Summary:** {s.id}@{s.fm_get('version') or ''} {model.title_of(s)}", "",
                  f"**Links:** epic {ep.id}" + (f" · intake tickets {intake}" if intake else "")
                  + f" · status {s.fm_get('status') or '—'}", "", "**Description:**", ""]
        lines += [x for x in stories.section(s.text, 1) if x.strip()][:6] + [""]
        for c in res["cards"]:
            if s.id in c["stories"]:
                lines += cardmod._render_card(c) + [""]
        acs = [x.rstrip() for x in stories.section(s.text, 6) if x.strip()]
        lines += ["**Acceptance criteria:**", ""] + (acs or ["none"]) + [""]
    return {"folder": res["folder"], "text": "\n".join(lines).rstrip() + "\n"}


def write_jira(vault, res):
    p = os.path.join(res["folder"], JIRA_FILE)
    with open(p, "w", encoding="utf-8") as f:
        f.write(res["text"])
    return vault.rel(p)
