"""The ledger — change sets gated on a question (restructure plan § B.2/B.3).

One JSONL file per feature: ``01-Requirements/_ledger/<slug>.jsonl``; one line per gated change set:
``{"id", "state": open|released|superseded|needs-judgement, "artifact", "question", "changeset",
"added", "updated", "reason"}``. Replaces staged ``## Discussion`` entries for new work.

``render``   writes a read-only ``## Pending changes`` block into each affected UC/BR so a reviewer
             (and /approve-uc) still sees exactly what is waiting and on which question.
``release``  re-checks each open set: when its question is ticked with a filled ``A:`` (or moved to
             the Decision log) the set is applied. An answer that reads as a refusal ("no", "reject",
             "out of scope" …) is never applied blindly: it is marked needs-judgement for a judging
             agent, whose verdicts file (apply | supersede | revise) settles it.
"""
import os
import re

from . import model
from .edit import same_question
from .util import EngineError, dump_json, load_json, today
from .vault import Doc, questions_in

NEGATIVE = re.compile(r"^\s*(no\b|not\b|reject|decline|out of scope|won'?t|do not|don'?t|never|superseded|n/a\b)", re.I)
BLOCK = "Pending changes"
MARK = "<!-- bigin ledger render — read-only, regenerated from 01-Requirements/_ledger. Answer the question; do not edit this block. -->"


def _path(vault, slug):
    return os.path.join(vault.ledger_dir, f"{slug or '_vault'}.jsonl")


def _read(path):
    out = []
    if os.path.exists(path):
        import json
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    return out


def _write(path, items):
    import json
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for e in items:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def entries(vault, state=None):
    out = []
    if not os.path.isdir(vault.ledger_dir):
        return out
    for fn in sorted(os.listdir(vault.ledger_dir)):
        if fn.endswith(".jsonl"):
            for e in _read(os.path.join(vault.ledger_dir, fn)):
                e["_file"] = fn
                if state is None or e.get("state") == state:
                    out.append(e)
    return out


def open_counts(vault):
    counts = {}
    for e in entries(vault, "open"):
        counts[e["artifact"]] = counts.get(e["artifact"], 0) + 1
    return counts


def _slug_for(vault, cs, artifact):
    tr = cs.get("trace") or {}
    if tr.get("hub"):
        return tr["hub"]
    p = vault.find(artifact) if artifact[:2] in ("UC", "BR") else None
    if p:
        d = vault.load(p)
        return d.fm_get("primary_feature") or d.fm_get("feature") or "_vault"
    return artifact if re.match(r"^[a-z0-9-]+$", artifact) else "_vault"


def add(vault, cs, artifact):
    slug = _slug_for(vault, cs, artifact)
    path = _path(vault, slug)
    items = _read(path)
    for e in items:
        if e["id"] == cs["id"]:
            return e  # idempotent
    e = {"id": cs["id"], "state": "open", "artifact": artifact, "question": (cs.get("gate") or {}).get("question", ""),
         "changeset": cs, "added": today(), "updated": today(), "reason": ""}
    items.append(e)
    _write(path, items)
    return e


def _set_state(vault, ids, state, reason=""):
    changed = []
    for fn in (os.listdir(vault.ledger_dir) if os.path.isdir(vault.ledger_dir) else []):
        if not fn.endswith(".jsonl"):
            continue
        p = os.path.join(vault.ledger_dir, fn)
        items = _read(p)
        dirty = False
        for e in items:
            if e["id"] in ids and e["state"] != state:
                e["state"], e["updated"] = state, today()
                if reason:
                    e["reason"] = reason
                dirty = True
                changed.append(e["id"])
        if dirty:
            _write(p, items)
    return changed


def supersede(vault, ids, reason, dry=False):
    if dry:
        return [e["id"] for e in entries(vault, "open") if e["id"] in ids]
    out = _set_state(vault, set(ids), "superseded", reason)
    render_blocks(vault)
    return out


def _answer_for(vault, e):
    """(answered, answer text) for the entry's gate question on its artifact."""
    p = vault.find(e["artifact"]) if e["artifact"][:2] in ("UC", "BR") else vault.hub_path(e["artifact"])
    if not p or not os.path.exists(p):
        return False, ""
    d = vault.load(p)
    q = e["question"]
    for x in model.artifact_questions(d) if e["artifact"][:2] in ("UC", "BR") else []:
        if same_question(x.text, q):
            return (x.checked and x.answered), x.answer
    if e["artifact"].startswith("UC"):
        t = model.decision_table(d)
        if t is not None:
            for r in t.rows():
                if len(r) >= 4 and same_question(r[1], q):
                    return True, r[3]
    return False, ""


def release(vault, verdicts=None, dry=False, run=None):
    """Apply every open change set whose question is answered. Returns a report dict."""
    from . import changeset
    vmap = {}
    if verdicts:
        data = load_json(verdicts)
        for v in data.get("verdicts") or []:
            vmap[v["id"]] = v
    report = {"released": [], "superseded": [], "needs_judgement": [], "waiting": [], "apply": None}
    to_apply = []
    for e in entries(vault, None):
        if e["state"] not in ("open", "needs-judgement"):
            continue
        answered, answer = _answer_for(vault, e)
        v = vmap.get(e["id"])
        if v:
            if v["verdict"] == "supersede":
                report["superseded"].append(e["id"])
                if not dry:
                    _set_state(vault, {e["id"]}, "superseded", v.get("reason", "the answer contradicts it"))
                continue
            cs = v.get("changeset") if v["verdict"] == "revise" and v.get("changeset") else e["changeset"]
            to_apply.append((e, cs))
            continue
        if not answered:
            report["waiting"].append(e["id"])
            continue
        if NEGATIVE.search(answer or ""):
            report["needs_judgement"].append({"id": e["id"], "question": e["question"], "answer": answer})
            if not dry and e["state"] != "needs-judgement":
                _set_state(vault, {e["id"]}, "needs-judgement", "answer reads as a refusal — judge before applying")
            continue
        to_apply.append((e, e["changeset"]))
    if to_apply:
        sets = []
        for e, cs in to_apply:
            cs = dict(cs)
            cs.pop("gate", None)
            sets.append(cs)
        ids = {e["id"] for e, _ in to_apply}
        res = changeset.apply(vault, sets, run=run, dry=dry, release_ids=ids)
        report["apply"] = res
        landed = {x["id"] for x in res["applied"] + res["already"]}
        report["released"] = sorted(landed & ids)
        if not dry:
            _set_state(vault, landed & ids, "released", "question answered")
            # the gate question is settled and its change folded in → Decision log (use-case.md § 5)
            from .edit import append_changelog
            for aid in sorted({e["artifact"] for e, _ in to_apply if e["id"] in landed and e["artifact"].startswith("UC")}):
                d = vault.load(vault.find(aid))
                n = changeset.settle_answered(d)
                if n:
                    append_changelog(d, f"- {today()} — bigin ledger release: {n} answered question(s) moved to the Decision log")
                    vault.write(d)
            render_blocks(vault)
    return report


def render_blocks(vault, dry=False):
    """Write/refresh/remove the read-only ## Pending changes block on every UC/BR."""
    by_art = {}
    for e in entries(vault, None):
        if e["state"] in ("open", "needs-judgement"):
            by_art.setdefault(e["artifact"], []).append(e)
    changed = []
    for p in vault.uc_paths() + vault.br_paths():
        d = vault.load(p)
        want = by_art.get(d.id)
        has = d.section(BLOCK)
        if not want and not has:
            continue
        if want:
            body = ["", MARK, ""]
            for e in want:
                cs = e["changeset"]
                anchor = (cs.get("anchor") or {}).get("ref")
                what = cs.get("text") or (cs.get("cells") and f"{cs['cells']['actor']} → {cs['cells']['system']}") \
                    or (cs.get("flow") and f"{cs['flow'].get('name')}: {cs['flow'].get('body')}") or ""
                what = re.sub(r"\s+", " ", what).strip()
                flag = " — **answer reads as a refusal; awaiting judgement**" if e["state"] == "needs-judgement" else ""
                body.append(f"- **{e['id']}** `{cs['op']}`{(' at ' + anchor) if anchor else ''} — waiting on: "
                            f"“{e['question']}”{flag}")
                if what:
                    body.append(f"  → “{what[:600]}”")
            body.append("")
            if has:
                d.replace_body(BLOCK, body)
            else:
                before = "Discussion" if d.section("Discussion") else "Changelog"
                d.insert_section(BLOCK, body, before=before)
        else:
            s = d.section(BLOCK)
            d.allow_heading_change = True
            d.splice(s.h, s.end, [])
        if d.changed:
            changed.append(d.id)
            if dry:
                vault.forget(p)
            else:
                vault.write(d)
    return changed


def render_list(items):
    if not items:
        return "ledger: empty"
    lines = []
    for e in items:
        lines.append(f"{e['id']:<28} {e['state']:<16} {e['artifact']:<9} {e['question'][:90]}")
    return "\n".join(lines)


def render_release(rep):
    lines = [f"ledger release: {len(rep['released'])} released · {len(rep['superseded'])} superseded · "
             f"{len(rep['needs_judgement'])} need judgement · {len(rep['waiting'])} still waiting"]
    for x in rep["needs_judgement"][:10]:
        lines.append(f"  judge: {x['id']} — A: {x['answer'][:100]}")
    if rep.get("apply"):
        from .changeset import render_result
        lines.append(render_result(rep["apply"]))
    return "\n".join(lines)
