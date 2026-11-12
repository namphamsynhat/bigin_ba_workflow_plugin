"""Open-question tracking and the outbox.

Every ``- [ ] Q:`` in the vault carries (or gains) ``(asked: date)``; a pack hands the BA a paste-ready file per
recipient and ``questions sent`` stamps ``(sent: date via target)``. Nothing is posted anywhere — the BA pastes.

``collect``   one record per DISTINCT open question (the same question mirrored on a note, a hub and a UC is one)
``listing``   those records aged and ranked by what they block
``pack``      writes ``06-Outbox/<date>-<target>.md``, one file per Jira key, else per owner
``sent``      stamps ``(sent: …)`` on every question named in a pack
``prematch``  intake hook: a new source block quoting ``[q:xxxxxx]`` is recorded as that question's answer
"""
import datetime
import os
import re

from . import ledger
from .edit import same_question
from .util import EngineError, today
from .vault import q_clean, q_tag, questions_in

OUTBOX = "06-Outbox"
TAG_RE = re.compile(r"\\?\[?\bq:([0-9a-f]{6})\b\\?\]?", re.I)   # also the `\[q:…\]` Markdown/ADF conversion leaves
OWNERS = ("client", "dev", "team")


def _docs(vault):
    for p in vault.note_paths():
        yield vault.load(p)
    for p in vault.hub_paths():
        yield vault.load(p)
    for p in vault.uc_paths() + vault.br_paths():
        yield vault.load(p)


def _age(asked):
    try:
        return (datetime.date.fromisoformat(today()) - datetime.date.fromisoformat(asked)).days if asked else None
    except ValueError:
        return None


def collect(vault, owner=None, feature=None):
    """Open questions, de-duplicated by tag. Each: tag, text, owner, ref, asked, sent, where[], blocks[]."""
    out = {}
    for doc in _docs(vault):
        feats = _features_of(doc)
        for q in questions_in(doc, 0, len(doc.lines)):
            if q.checked or q.answered:
                continue
            anchor = _anchor(doc, q)
            key = q.tag
            # the same words on two UCs/BRs with nothing in common are two questions, not one mirrored
            if key in out and anchor and out[key]["anchor"] and not (anchor & out[key]["anchor"]):
                key = q_tag(q.text + "|" + sorted(anchor)[0])
            rec = out.setdefault(key, {"tag": key, "text": q_clean(q.text), "owner": q.owner, "ref": q.ref,
                                       "asked": None, "sent": None, "where": [], "ids": set(), "features": set(),
                                       "anchor": set()})
            rec["features"] |= feats
            rec["anchor"] |= anchor
            rec["owner"] = rec["owner"] or q.owner
            rec["ref"] = rec["ref"] or q.ref
            if q.asked and (not rec["asked"] or q.asked < rec["asked"]):
                rec["asked"] = q.asked
            rec["sent"] = rec["sent"] or q.sent
            rec["where"].append(vault.rel(doc.path))
            if doc.id:
                rec["ids"].add(doc.id)
    items = list(out.values())
    if feature:
        items = [r for r in items if _in_feature(vault, r, feature)]
    if owner:
        items = [r for r in items if (r["owner"] or "team") == owner]
    open_cs = [e for e in ledger.entries(vault, "open")]
    for r in items:
        blocks = {e["id"] for e in open_cs if e.get("question") and same_question(e["question"], r["text"])}
        for i in set(r["ids"]) | set(re.findall(r"\bUC-\d+\b", r["ref"] or "")):
            if not i.startswith("UC-"):
                continue
            p = vault.find(i)
            if p and (vault.load(p).fm_get("status") or "") == "needs-clarification":
                blocks.add(i)
        r["features"] = sorted(r["features"])
        r["anchor"] = sorted(r["anchor"])
        r["blocks"] = sorted(blocks)
        r["age"] = _age(r["asked"])
        r["ids"] = sorted(r["ids"])
    return items


def _features_of(doc):
    """Feature slugs a doc belongs to, from its front matter (never from its path)."""
    kind = (doc.id or "")[:2]
    if kind in ("UC", "BR"):
        vals = [doc.fm_get("primary_feature"), doc.fm_get("feature")] + doc.fm_list("features")
    elif kind == "IN":
        vals = [doc.fm_get("feature")] + doc.fm_list("declared_features")
    else:
        vals = [os.path.basename(doc.path or "")[:-3]]
    return {str(v).strip() for v in vals if v and str(v).strip()}


def _anchor(doc, q):
    """UC/BR ids this question is about — used only to tell identical wording on unrelated artifacts apart."""
    if (doc.id or "")[:2] in ("UC", "BR"):
        return {doc.id}
    return set(re.findall(r"\b(?:UC|BR)-\d+\b", q.ref or ""))


def _in_feature(vault, r, feature):
    return feature in r["features"]


def listing(vault, owner=None, feature=None):
    items = collect(vault, owner, feature)
    items.sort(key=lambda r: (-len(r["blocks"]), -(r["age"] if r["age"] is not None else -1), r["text"]))
    return items


def _jira_keys(vault, r):
    """Jira keys this question belongs to: the note it sits on or cites, or the notes behind a UC it names."""
    from .cascade import trace_of
    ints = {i for i in list(r["ids"]) + re.findall(r"\bINT-\d+\b", r["ref"] or "") if i.startswith("INT-")}
    ucs = [i for i in list(r["ids"]) + re.findall(r"\bUC-\d+\b", r["ref"] or "") if i.startswith("UC-")]
    if ucs:
        got_ints, _ = trace_of(vault, ", ".join(sorted(set(ucs))))
        ints |= set(got_ints)
    keys = set()
    for nid in ints:
        p = vault.find(nid)
        if p:
            k = (vault.load(p).fm_get("jira_key") or "").strip()
            if k:
                keys.add(k)
    return sorted(keys)


def _slug(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-") or "pack"


def pack(vault, owner=None, dry=False):
    """Write one pack per Jira key (else per owner) holding the not-yet-sent questions. Returns the packs."""
    wanted = [owner] if owner else ["client", "dev"]
    groups = {}
    for r in listing(vault):
        o = r["owner"] or "team"
        if o not in wanted or r["sent"]:
            continue
        keys = _jira_keys(vault, r)
        for target in (keys or [o]):
            groups.setdefault((o, target), []).append(r)      # a dev question never rides in a client pack
    res = []
    for (o, target), rs in sorted(groups.items()):
        rel = f"{OUTBOX}/{today()}-{o}-{_slug(target)}.md"
        body = [f"# Questions for {target}", "",
                "Paste as is. Keep each `[q:…]` tag in the reply so the answer finds its question.", ""]
        body += [f"- [q:{r['tag']}] {r['text']}" for r in rs]
        text = "\n".join(body) + "\n"
        if not dry:
            path = os.path.join(vault.root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        res.append({"pack": rel, "target": target, "owner": o, "questions": [r["tag"] for r in rs]})
    return res


def sent(vault, pack_path, dry=False):
    """Stamp ``(sent: date via target)`` on every question the pack names."""
    path = pack_path if os.path.isabs(pack_path) else os.path.join(vault.root, pack_path)
    if not os.path.exists(path):
        raise EngineError(f"no such pack: {pack_path}")
    with open(path, encoding="utf-8") as f:
        tags = set(TAG_RE.findall(f.read()))
    base = os.path.basename(path)[:-3] if path.endswith(".md") else os.path.basename(path)
    target = re.sub(r"^(?:client|dev|team)-", "", re.sub(r"^\d{4}-\d{2}-\d{2}-", "", base))
    stamped = 0
    for doc in _docs(vault):
        hit = False
        for q in reversed(questions_in(doc, 0, len(doc.lines))):
            if (q.tag in tags or any(t in tags for t in [q_tag(q.text + "|" + a) for a in _anchor(doc, q)])) \
                    and not q.sent and not q.checked:
                doc.splice(q.start, q.start + 1, [doc.lines[q.start].rstrip() + f" (sent: {today()} via {target})"])
                hit = True
                stamped += 1
        if hit:
            if not dry:
                vault.write(doc)
            else:
                vault.forget(doc.path)
    return {"pack": pack_path, "target": target, "stamped": stamped, "questions": sorted(tags)}


def prematch(vault, doc, blocks):
    """Intake hook. ``blocks`` = [(src_label, text)]. A block quoting ``[q:xxxxxx]`` of a question that is still
    open anywhere in the vault is recorded on the note as ``q:xxxxxx @ SRC-n`` (``prematched_answers``), so the
    filer confirms that answer instead of searching for the question. Untagged replies are not touched."""
    wanted = {}
    for src, text in blocks:
        for t in TAG_RE.findall(text or ""):
            wanted.setdefault(t, src)
    if not wanted:
        return []
    open_tags = {r["tag"] for r in collect(vault)}
    have = doc.fm_list("prematched_answers")
    new = [f"q:{t} @ {src}" for t, src in sorted(wanted.items()) if t in open_tags and f"q:{t} @ {src}" not in have]
    if new:
        doc.fm_set("prematched_answers", have + new)
    return new


def prematched(vault, doc):
    """The note's pre-matched answers resolved to the question text and where it sits — for the file worklist."""
    by_tag = {r["tag"]: r for r in collect(vault)}
    out = []
    for item in doc.fm_list("prematched_answers"):
        m = re.match(r"^q:([0-9a-f]{6}) @ (SRC-\d+)$", str(item).strip().strip('"'))
        if m and m.group(1) in by_tag:
            r = by_tag[m.group(1)]
            out.append({"tag": m.group(1), "src": m.group(2), "question": r["text"], "where": r["where"]})
    return out


def render_list(items):
    if not items:
        return "no open questions"
    out = []
    for r in items:
        age = "—" if r["age"] is None else f"{r['age']}d"
        blk = f" blocks {', '.join(r['blocks'])}" if r["blocks"] else ""
        snt = f" sent {r['sent'][0]} via {r['sent'][1]}" if r["sent"] else ""
        out.append(f"[q:{r['tag']}] {r['owner'] or 'team':<6} {age:>5}{blk}{snt}\n    {r['text'][:200]}")
    return "\n".join(out)
