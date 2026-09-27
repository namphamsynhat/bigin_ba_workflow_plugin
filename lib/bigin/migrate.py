"""Vault migrations between plugin versions (docs/MIGRATION.md).

    bigin migrate snapshot                      tar czf _runs/migrate-<stamp>.tgz 01-Requirements 00-Inbox
    bigin migrate plan --from 1.8.12 --to 1.12.0
    bigin migrate all  --from 1.8.12 --to 1.12.0 [--dry]
    bigin migrate discussion-to-ledger [--dry]  (v1.10.0)
    bigin migrate strip-guidance [--dry]        (v1.12.0)
    bigin migrate split-signal-log [--dry]      (v1.12.0)

Every real run snapshots first (vaults are often untracked by git) and prints a summary.
"""
import difflib
import glob
import os
import re
import tarfile

from . import model
from .util import EngineError, dump_json, now_stamp, sort_ids, today
from .vault import PLUGIN_ROOT, Doc, strip_comments

LEGACY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legacy_templates")
STEPS = [("1.9.0", []), ("1.10.0", ["discussion-to-ledger"]), ("1.12.0", ["strip-guidance", "split-signal-log"]), ("1.12.1", [])]


def _v(s):
    return tuple(int(x) for x in re.findall(r"\d+", s or "0")[:3]) + (0,) * (3 - len(re.findall(r"\d+", s or "0")[:3]))


# ---------------------------------------------------------------------------- snapshot

def snapshot(vault, label="migrate"):
    os.makedirs(vault.runs_dir, exist_ok=True)
    path = os.path.join(vault.runs_dir, f"{label}-{now_stamp()}.tgz")
    with tarfile.open(path, "w:gz") as tar:
        for d in ("01-Requirements", "00-Inbox"):
            p = os.path.join(vault.root, d)
            if os.path.exists(p):
                tar.add(p, arcname=d)
    return path


# ---------------------------------------------------------------------------- discussion → ledger

ENTRY_HEAD = re.compile(r"^- \*\*((?:INT-\d+)(?:\s*,\s*INT-\d+)*)\*\*")
TAIL = re.compile(r"\s*—\s*rationale not stated at capture.*$", re.I | re.S)


def parse_entries(doc):
    """Staged entries in ## Discussion: [{start, end, raw, ints, hub_rows, proposal}]"""
    s = doc.section("Discussion")
    if not s:
        return []
    heads = [i for i in range(s.start, s.end) if ENTRY_HEAD.match(doc.masked[i])]
    out = []
    for k, i in enumerate(heads):
        j = heads[k + 1] if k + 1 < len(heads) else s.end
        while j > i + 1 and not doc.masked[j - 1].strip():
            j -= 1
        raw = "\n".join(doc.lines[i:j])
        head, _, prop = raw.partition("→ proposed")
        ints = sort_ids(re.findall(r"INT-\d+", ENTRY_HEAD.match(doc.lines[i]).group(1)))
        rows = sorted(model.hub_row_cites(head), key=lambda x: (x[0], int(re.match(r"\d+", x[1]).group(0))))
        out.append({"start": i, "end": j, "raw": raw, "ints": ints, "hub_rows": rows,
                    "proposal": prop, "xr": sorted(set(re.findall(r"XR-[A-Z]+-\d+", raw)))})
    return out


def _clauses(prop):
    """Split '→ proposed…' text into destination clauses."""
    prop = prop.strip()
    m = re.match(r"^(rule(?:\s*\(addition\))?|correction[^:]*)\s*:\s*", prop, re.I)
    if m:
        return [(m.group(1).lower(), prop[m.end():])]
    prop = re.sub(r"^:\s*", "", prop)
    lines = prop.split("\n")
    subs = [x for x in lines if re.match(r"^\s{0,4}- ", x)]
    if subs:
        out, cur = [], None
        for x in lines:
            if re.match(r"^\s{0,4}- ", x):
                if cur:
                    out.append(cur)
                cur = re.sub(r"^\s*- ", "", x)
            elif cur is not None and x.strip() and not x.strip().startswith("—"):
                cur += "\n" + x.strip()
        if cur:
            out.append(cur)
        return [("", TAIL.sub("", c).strip()) for c in out]
    return [("", TAIL.sub("", prop).strip())]


def _cells(text):
    if "||" in text:
        a, b = text.split("||", 1)
        return {"actor": a.strip(), "system": b.strip()}
    m = re.search(r"(?<=[.;])\s+(?=(?:The )?System\b)", text)
    if m:
        return {"actor": text[:m.start()].strip(), "system": text[m.end():].strip()}
    return {"actor": text.strip(), "system": "—"}


def clause_to_changesets(kind, prefix, clause, target_id):
    """Map one legacy destination clause to change-set bodies (no id/trace). [] = unparseable."""
    c = clause.strip()
    if prefix.startswith("rule"):
        op = "append_rule_clause" if "addition" in prefix else "set_rule"
        return [{"target": {"kind": "BR", "id": target_id}, "op": op, "text": c}] if kind == "BR" else []
    if prefix.startswith("correction"):
        return []
    m = re.match(r"^rule becomes:\s*(.+)$", c, re.I | re.S)
    if m and kind == "BR":
        return [{"target": {"kind": "BR", "id": target_id}, "op": "set_rule", "text": m.group(1).strip()}]
    m = re.match(r"^(?:rule )?(?:adds?|clause):\s*(.+)$", c, re.I | re.S)
    if m and kind == "BR":
        return [{"target": {"kind": "BR", "id": target_id}, "op": "append_rule_clause", "text": m.group(1).strip()}]
    m = re.match(r"^§\s*1\s+(.+?)\s+becomes:\s*(.+)$", c, re.S)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "1", "field": m.group(1).strip()},
                 "op": "set_field", "text": m.group(2).strip()}]
    m = re.match(r"^§\s*1\s+(.+?)\s*(?:—|-|:)?\s*adds?:\s*(.+)$", c, re.S)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "1", "field": m.group(1).strip()},
                 "op": "append_note", "text": m.group(2).strip()}]
    m = re.match(r"^§\s*4:?\s*(.+)$", c, re.S)
    if m:
        out = []
        for part in re.split(r"\s+·\s+|;\s+(?=add )", m.group(1)):
            mm = re.search(r"(?:add|mirror(?: of)?)\s+(BR-\d+)\b.*?(?:enforced\s+at|\bat)\s+(.+?)\.?$", part.strip(), re.S)
            if not mm:
                return []
            out.append({"target": {"kind": "UC", "id": target_id, "section": "4"}, "op": "mirror_br",
                        "br": mm.group(1), "enforced_at": mm.group(2).strip()})
        return out
    m = re.match(r"^§\s*6:?\s*(?:becomes:|adds?:)?\s*(.+)$", c, re.S)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "6"}, "op": "append_note", "text": m.group(1).strip()}]
    m = re.match(r"^§\s*5:?\s*(?:add\s+)?(?:question:?|Q:)\s*(.+)$", c, re.S | re.I)
    if m:
        return [{"target": {"kind": kind, "id": target_id}, "op": "add_question", "text": m.group(1).strip()}]
    m = re.match(r"^new step(?: after (S\d+|start|end))?:\s*(.+)$", c, re.S | re.I)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "2"}, "op": "new_step_after",
                 "anchor": {"ref": m.group(1) or "end"}, "cells": _cells(m.group(2))}]
    m = re.match(r"^(S\d+) becomes:\s*(.+)$", c, re.S)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "2"}, "op": "replace_step",
                 "anchor": {"ref": m.group(1)}, "cells": _cells(m.group(2))}]
    m = re.match(r"^(S\d+) is removed because\s*(.+)$", c, re.S)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "2"}, "op": "drop_step",
                 "anchor": {"ref": m.group(1)}, "reason": m.group(2).strip()}]
    m = re.match(r"^new flow\s*([AE])?\d*:?\s*(.+)$", c, re.S | re.I)
    if m:
        name, _, body = m.group(2).partition("\n")
        return [{"target": {"kind": "UC", "id": target_id, "section": "3"}, "op": "new_flow",
                 "flow": {"kind": (m.group(1) or "E").upper(), "name": name.strip().rstrip("."), "body": body.strip() or name.strip()}}]
    m = re.match(r"^([AE]\d+) becomes:\s*(.+)$", c, re.S)
    if m:
        name, _, body = m.group(2).partition("\n")
        return [{"target": {"kind": "UC", "id": target_id, "section": "3"}, "op": "replace_flow",
                 "anchor": {"ref": m.group(1)}, "flow": {"name": name.strip(), "body": body.strip() or name.strip()}}]
    m = re.match(r"^([AE]\d+) is removed because\s*(.+)$", c, re.S)
    if m:
        return [{"target": {"kind": "UC", "id": target_id, "section": "3"}, "op": "drop_flow",
                 "anchor": {"ref": m.group(1)}, "reason": m.group(2).strip()}]
    return []


MECHANICAL = {"new_step_after", "replace_step", "drop_step", "new_flow", "replace_flow", "drop_flow", "mirror_br"}


def discussion_to_ledger(vault, dry=False):
    from . import changeset
    from .edit import q_core
    plan, sets, unparsed = [], [], []
    per_art = {}
    for p in vault.uc_paths() + vault.br_paths():
        d = vault.load(p)
        kind = d.id[:2]
        entries = parse_entries(d)
        if not entries:
            continue
        open_qs = model.open_questions(d)
        for k, e in enumerate(entries):
            bodies = []
            ok = True
            for prefix, cl in _clauses(e["proposal"]):
                got = clause_to_changesets(kind, prefix, cl, d.id)
                if not got:
                    ok = False
                    break
                bodies += got
            if not ok or not bodies:
                unparsed.append({"artifact": d.id, "entry": e["raw"][:300]})
                continue
            hub_rows = {}
            for slug, row in e["hub_rows"]:
                hub_rows.setdefault(slug, []).append(row)
            gate_q = None
            if any(b["op"] not in MECHANICAL for b in bodies) and open_qs:
                # a prose entry waits only on an open question that traces to the SAME hub row or the
                # same note rows (1-foldin.md: each staged entry is folded once its question is answered)
                mine_rows = set(e["hub_rows"])
                mine_notes = model.expand_int_cites(e["raw"].split("→ proposed")[0])
                for q in open_qs:
                    if (model.hub_row_cites(q.text) & mine_rows) or (model.expand_int_cites(q.text) & mine_notes) \
                            or "(gated" in e["raw"]:
                        gate_q = q.text
                        break
            for j, b in enumerate(bodies):
                slug = next(iter(hub_rows), None)
                tr = {"ints": e["ints"]}
                if slug:
                    tr["hub"] = slug
                    tr["hub_rows"] = hub_rows[slug]
                if e["xr"]:
                    tr["xr"] = e["xr"]
                cs = {"id": f"cs-mig-{d.id}-{k + 1}-{j + 1}", "trace": tr, **b}
                if gate_q and b["op"] not in MECHANICAL:
                    cs["gate"] = {"question": re.sub(r"\s*\((owner|ref):[^)]*\)", "", gate_q).strip(), "blocks": True}
                sets.append(cs)
            per_art.setdefault(d.id, []).append((e, [f"cs-mig-{d.id}-{k + 1}-{j + 1}" for j in range(len(bodies))]))
            plan.append({"artifact": d.id, "entry": k + 1, "changesets": len(bodies), "gated": bool(gate_q)})
    res = {"converted": len(plan), "changesets": len(sets), "unparsed": unparsed, "removed": 0}
    if dry or not sets:
        res["plan"] = plan[:50]
        return res
    out_dir = os.path.join(vault.runs_dir, f"migrate-discussion-{now_stamp()}")
    dump_json({"kind": "changesets", "task": "migrate discussion-to-ledger", "changesets": sets},
              os.path.join(out_dir, "changesets.json"))
    applied = changeset.apply(vault, sets, run=None)
    res["apply"] = {k: len(v) if isinstance(v, list) else v for k, v in applied.items() if k in ("applied", "already", "gated", "drift", "invalid", "rejected")}
    landed = {x["id"] for b in ("applied", "already", "gated", "drift") for x in applied[b]}
    # remove every entry whose change sets all landed somewhere (applied, ledger, or a drift question)
    for aid, items in per_art.items():
        d = vault.load(vault.find(aid))
        drop = []
        for e, ids in items:
            if all(i in landed for i in ids):
                raw = e["raw"]
                for q in parse_entries(d):
                    if q["raw"] == raw:
                        drop.append((q["start"], q["end"]))
        for a, b in sorted(drop, reverse=True):
            d.splice(a, b, [])
            res["removed"] += 1
        if d.changed:
            vault.write(d)
    # rows whose entries carried no hub-row trace: nothing cites them any more → applied
    from . import hub
    res["swept"] = {k: len(v) for k, v in hub.sweep(vault).items()}
    res["invalid"] = [{"id": x["id"], "detail": x["detail"]} for x in applied["invalid"]][:30]
    res["saved"] = vault.rel(os.path.join(out_dir, "changesets.json"))
    return res


# ---------------------------------------------------------------------------- strip guidance

def _norm_comment(c):
    return re.sub(r"\s+", " ", c.replace("`", "")).strip()


def _known_blocks():
    blocks = set()
    for p in glob.glob(os.path.join(LEGACY_DIR, "*.md")) + glob.glob(os.path.join(PLUGIN_ROOT, "workspace", "templates", "*.md")):
        text = open(p, encoding="utf-8").read()
        for m in re.finditer(r"<!--.*?-->", text, re.S):
            if "guide:" not in m.group(0):
                blocks.add(_norm_comment(m.group(0)))
    return blocks


GUIDE = {"UC": "<!-- guide: _bigin/templates/use-case.guide.md -->",
         "BR": "<!-- guide: _bigin/templates/br.guide.md -->",
         "HUB": "<!-- guide: _bigin/templates/feature-hub.guide.md -->"}


def strip_guidance_doc(doc, kind, known):
    text = doc.text
    spans = []
    for m in re.finditer(r"<!--.*?-->", text, re.S):
        if _norm_comment(m.group(0)) in known:
            spans.append((m.start(), m.end()))
    if not spans:
        return 0
    out, last = [], 0
    for a, b in spans:
        # take the whole line(s) when the comment is alone on them
        la = text.rfind("\n", 0, a) + 1
        lb = text.find("\n", b)
        lb = len(text) if lb < 0 else lb
        if not text[la:a].strip() and not text[b:lb].strip():
            a, b = la, min(lb + 1, len(text))
        out.append(text[last:a])
        last = b
    out.append(text[last:])
    new = "".join(out)
    new = re.sub(r"\n{3,}", "\n\n", new)
    guide = GUIDE.get(kind)
    if guide and guide not in new:
        new = re.sub(r"^(# [^\n]*)$", lambda m: m.group(1) + "\n" + guide, new, count=1, flags=re.M)
    d2 = Doc(new, doc.path)
    # heading set must be identical — strip-guidance only ever removes comments
    if [s.title for s in d2.sections] != [s.title for s in doc.sections]:
        raise EngineError(f"{doc.name}: strip-guidance would change headings — refused")
    if model.h2_titles(strip_comments(new)) != model.h2_titles(strip_comments(doc.text)):
        raise EngineError(f"{doc.name}: strip-guidance changed visible content — refused")
    doc.lines = d2.lines
    doc.trailing_nl = d2.trailing_nl
    doc.allow_heading_change = False
    doc.touched |= {s.key for s in doc.sections} | {("__intro__", 0)}
    doc._reparse()
    return len(spans)


def strip_guidance(vault, dry=False):
    known = _known_blocks()
    res = {"files": 0, "blocks": 0, "bytes_before": 0, "bytes_after": 0}
    targets = [(p, "UC") for p in vault.uc_paths()] + [(p, "BR") for p in vault.br_paths()] + \
              [(p, "HUB") for p in vault.hub_paths()]
    for p, kind in targets:
        d = vault.load(p)
        before = len(d.text.encode("utf-8"))
        n = strip_guidance_doc(d, kind, known)
        res["bytes_before"] += before
        res["bytes_after"] += len(d.text.encode("utf-8"))
        if n:
            res["files"] += 1
            res["blocks"] += n
            if dry:
                d.verify()
                vault.forget(p)
            else:
                vault.write(d)
    return res


# ---------------------------------------------------------------------------- split signal log

POINTER = "Rows: `{slug}.signals.md` — agents read them via `bigin worklist`."


def split_signal_log(vault, dry=False, only=None):
    res = {"hubs": 0, "bytes_moved": 0}
    for hp in vault.hub_paths():
        slug = os.path.basename(hp)[:-3]
        if only and slug not in only:
            continue
        sp = vault.signals_path(slug)
        if os.path.exists(sp):
            continue
        d = vault.load(hp)
        s = d.section("Signal Log")
        if s is None:
            continue
        body = d.lines[s.start:s.end]
        while body and not body[-1].strip():
            body.pop()
        name = d.fm_get("name") or slug
        comp = ["---", "type: signal-log", f"feature: {slug}", f"updated: {today()}", "---", "",
                f"# Signal Log — {name}", "", f"Companion of `{slug}.md`. Append-only; `#` is permanent.", "",
                "## Signal Log"] + body + [""]
        text = "\n".join(comp)
        res["bytes_moved"] += len("\n".join(body).encode("utf-8"))
        d.replace_body("Signal Log", ["", POINTER.format(slug=slug), ""])
        res["hubs"] += 1
        if dry:
            d.verify()
            vault.forget(hp)
            continue
        vault.create(sp, text)
        vault.write(d)
    return res


# ---------------------------------------------------------------------------- orchestration

def plan_steps(from_v, to_v):
    out = []
    for ver, steps in STEPS:
        if _v(from_v) < _v(ver) <= _v(to_v):
            out += [(ver, s) for s in steps]
    return out


def run(vault, step, args, dry=False):
    if step == "snapshot":
        return {"snapshot": vault.rel(snapshot(vault))}
    if step == "plan":
        f = args.from_v or vault.config("workspace_version", "1.8.12")
        return {"from": f, "to": args.to_v, "steps": plan_steps(f, args.to_v or "99")}
    if step == "all":
        f = args.from_v or vault.config("workspace_version", "1.8.12")
        t = args.to_v
        if not t:
            from . import __version__
            t = __version__
        res = {"from": f, "to": t, "steps": []}
        if not dry:
            res["snapshot"] = vault.rel(snapshot(vault, f"migrate-{t}"))
        args._no_snapshot = True
        for ver, s in plan_steps(f, t):
            res["steps"].append({"version": ver, "step": s, "result": run(vault, s, args, dry)})
        if not dry:
            from . import hub, mirror, status
            mirror.sync_links(vault)
            hub.refresh_many(vault)
            status.recount(vault)
            proj = vault.project()
            if proj.fm and "workspace_version" in proj.fm:
                proj.fm_set("workspace_version", t)
                vault.write(proj)
        return res
    if not dry and step in ("discussion-to-ledger", "strip-guidance", "split-signal-log") and not getattr(args, "_no_snapshot", False):
        snap = snapshot(vault, f"migrate-{step}")
    else:
        snap = None
    fn = {"discussion-to-ledger": discussion_to_ledger, "strip-guidance": strip_guidance,
          "split-signal-log": split_signal_log}[step]
    r = fn(vault, dry=dry)
    if snap:
        r["snapshot"] = vault.rel(snap)
    return r


def render(res):
    import json
    return json.dumps(res, indent=2, ensure_ascii=False, default=str)
