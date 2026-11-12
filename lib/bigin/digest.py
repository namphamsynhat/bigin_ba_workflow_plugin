"""One digest, three audiences — the same vault facts for the BA, the client and the dev team. No LLM call.

Sections (each built from data the engine already keeps), in order:
  Came in · Changed · Decided · Waiting · Ready to approve · Stale downstream · Dev feedback · Spend

``--for ba``      everything.
``--for client``  Decided, Changed and Waiting on the client, with every id moved into a trailing ``(ref: …)``
                  (questions.md client register: no vault vocabulary in the words themselves).
``--for dev``     Changed (approved scope only), Stale downstream, new delta stories, Waiting on dev.
Empty sections are omitted. ``--since`` is a date or a run id; the default is the newest run that began before today.
"""
import os
import re

from . import cascade, ledger, model, questions
from .util import EngineError, load_json, today

AUDIENCES = ("ba", "client", "dev")
ID_RE = re.compile(r"\b(?:UC|BR|INT|EN|PP|US|EP|UX|DP)-\d+\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _runs(vault):
    """[(created date, run id)] oldest first."""
    out = []
    if os.path.isdir(vault.runs_dir):
        for rid in sorted(os.listdir(vault.runs_dir)):
            plan = os.path.join(vault.runs_dir, rid, "plan.json")
            if os.path.exists(plan):
                try:
                    out.append((load_json(plan).get("created") or "", rid))
                except (OSError, ValueError):
                    pass
    return out


def resolve_since(vault, since=None):
    if since and DATE_RE.match(since):
        return since
    runs = _runs(vault)
    if since:
        for created, rid in runs:
            if rid == since:
                return created or "0000-00-00"
        raise EngineError(f"--since: '{since}' is neither a date (YYYY-MM-DD) nor a run in _runs/")
    # default: the PREVIOUS run — the newest one that began before today (the run that just finished is "now")
    before = [c for c, _ in runs if c and c < today()]
    if before:
        return before[-1]
    return runs[-2][0] if len(runs) >= 2 and runs[-2][0] else "0000-00-00"


def _capture_events(vault, since):
    """(INT id, title, date, text) for every Capture history line dated on or after ``since``."""
    out = []
    for p in vault.note_paths():
        d = vault.load(p)
        s = d.section("Capture history")
        if not s:
            continue
        for ln in d.lines[s.start:s.end]:
            m = re.match(r"^-\s+(\d{4}-\d{2}-\d{2})\b[^—]*—\s*(.*)$", ln)
            if m and m.group(1) >= since:
                out.append((d.id, model.title_of(d), m.group(1), m.group(2).strip()))
    return out


def _artifacts(vault):
    for p in vault.uc_paths():
        yield "UC", vault.load(p)
    for p in vault.br_paths():
        yield "BR", vault.load(p)


def build(vault, since=None):
    """Every section as data; ``render`` decides who sees what."""
    since = resolve_since(vault, since)
    ev = _capture_events(vault, since)
    came, seen = [], set()
    for nid, title, date, text in ev:
        if "dev feedback" in text:
            continue
        if nid not in seen:
            seen.add(nid)
            came.append({"id": nid, "title": title, "date": date, "what": text})
    ba = {nid: bool(vault.load_id(nid).section("Before / After")) for nid in seen}
    for c in came:
        c["before_after"] = ba.get(c["id"], False)

    changed, decided = [], []
    for kind, d in _artifacts(vault):
        st = (d.fm_get("status") or "").strip()
        upd = str(d.fm_get("updated") or "")
        if upd >= since and st not in ("removed", "consolidated"):
            changed.append({"id": d.id, "kind": kind, "title": model.title_of(d), "status": st,
                            "version": str(d.fm_get("version") or ""), "date": upd,
                            "approved": st in ("approved", "enriched")})
        t = model.decision_table(d) if kind == "UC" else None
        if t is not None:
            ti, di, dd = t.col("Topic"), t.col("Decision"), t.col("Date")
            for r in t.rows():
                if dd is not None and len(r) > max(ti, di, dd) and DATE_RE.match(r[dd].strip()) and r[dd].strip() >= since:
                    decided.append({"id": d.id, "topic": r[ti].strip(), "decision": r[di].strip(), "date": r[dd].strip()})
    for e in ledger.entries(vault, "released"):
        if (e.get("updated") or "") >= since:
            decided.append({"id": e.get("artifact") or "", "topic": e.get("question") or "(change released)",
                            "decision": "released — its question was answered", "date": e.get("updated")})

    waiting = questions.listing(vault)
    open_cs = {}
    for e in ledger.entries(vault):
        if e.get("state") in ("open", "needs-judgement"):
            open_cs.setdefault(e.get("artifact") or "", []).append(e["id"])
    from .intake import jira
    ready = []
    for kind, d in _artifacts(vault):
        if kind != "UC" or (d.fm_get("status") or "").strip() != "draft":
            continue
        if open_cs.get(d.id) or model.open_questions(d):
            continue
        if not jira.approval_gate(vault, d.id)["ok"]:
            continue
        ready.append({"id": d.id, "title": model.title_of(d)})

    stale = []
    for kind, p in cascade.artifacts(vault):
        d = vault.load(p)
        s = [str(x).strip() for x in d.fm_list("stale")]
        if s:
            stale.append({"id": d.id, "title": model.title_of(d), "stale": s})
    delta = []
    for p in vault.story_paths():
        d = vault.load(p)
        if (d.fm_get("delta_of") or "") and str(d.fm_get("updated") or d.fm_get("created") or "") >= since:
            delta.append({"id": d.id, "title": model.title_of(d), "delta_of": str(d.fm_get("delta_of"))})

    feedback = []
    for nid, title, date, text in ev:
        if "dev feedback" in text:
            from .intake.jira import ucs_from
            feedback.append({"id": nid, "title": title, "date": date, "ucs": [u for u, _, _ in ucs_from(vault, nid)]})

    from . import metrics
    total, over, runs = 0, [], 0
    for created, rid in _runs(vault):
        if created >= since:
            r = metrics.report(vault, rid)
            total += r["total"]
            over += r["overruns"]
            runs += 1
    return {"since": since, "came": came, "changed": changed, "decided": decided, "waiting": waiting,
            "ready": ready, "stale": stale, "delta_stories": delta, "dev_feedback": feedback,
            "spend": {"tokens": total, "runs": runs, "overruns": over} if runs else None}


# ---------------------------------------------------------------------------- rendering

def _ref(ids):
    ids = sorted({i for i in ids if i})
    return f" (ref: {', '.join(ids)})" if ids else ""


def _plain(text):
    """The words with every vault id removed (the ids go into the trailing ref)."""
    t = ID_RE.sub("", text or "")
    t = re.sub(r"\(\s*[,;·]*\s*\)|\[\s*\]", "", t)
    return re.sub(r"\s+", " ", t).strip(" ,;·:-—")


def _lines(aud, data):
    """[(section title, [line, …])] for one audience, empty sections already dropped."""
    client, dev = aud == "client", aud == "dev"
    secs = []

    def line(text, *ids):
        return f"- {_plain(text)}{_ref(ids)}" if client else f"- {text}"

    if aud == "ba" and data["came"]:
        secs.append(("Came in", [f"- {c['id']} {c['title']} — {c['what']}" + (f" (see `{c['id']}` ## Before / After)" if c["before_after"] else "")
                                 for c in data["came"]]))
    ch = [c for c in data["changed"] if (c["approved"] or not dev)]
    if ch:
        secs.append(("Changed", [line(f"{c['id']} {c['title']} — now v{c['version']}, {c['status']}" if not client
                                      else f"{c['title']} — updated {c['date']}", c["id"]) for c in ch]))
    if not dev and data["decided"]:
        secs.append(("Decided", [line(f"{d['topic']} → {d['decision']}" if not client else f"{d['topic']}: {d['decision']}", d["id"])
                                 for d in data["decided"]]))
    w = [r for r in data["waiting"] if (not client or (r["owner"] or "team") == "client") and (not dev or (r["owner"] or "team") == "dev")]
    if w:
        out = []
        for r in w:
            age = "" if r["age"] is None else f" — waiting {r['age']} day(s)"
            who = "" if (client or dev) else f"[{r['owner'] or 'team'}] "
            out.append(line(f"{who}{r['text']}{age}", *r["blocks"]))
        secs.append(("Waiting", out))
    if aud == "ba" and data["ready"]:
        secs.append(("Ready to approve", [f"- {r['id']} {r['title']}" for r in data["ready"]]))
    if aud in ("ba", "dev"):
        st = [f"- {s['id']} {s['title']} — built on an older {', '.join(s['stale'])}" for s in data["stale"]]
        if st:
            secs.append(("Stale downstream", st))
    if dev and data["delta_stories"]:
        secs.append(("New delta stories", [f"- {s['id']} {s['title']} (changes {s['delta_of']})" for s in data["delta_stories"]]))
    if aud == "ba" and data["dev_feedback"]:
        secs.append(("Dev feedback", [f"- {f['id']} {f['title']} — build-team comment on {', '.join(f['ucs']) or 'no use case yet'} ({f['date']})"
                                      for f in data["dev_feedback"]]))
    if aud == "ba" and data["spend"]:
        sp = data["spend"]
        secs.append(("Spend", [f"- {sp['tokens']:,} tokens across {sp['runs']} run(s)"] + [f"- OVER BUDGET: {o}" for o in sp["overruns"]]))
    return secs


def render(data, aud):
    secs = _lines(aud, data)
    head = f"# Digest — {aud} — since {data['since']}"
    if not secs:
        return head + "\n\nNothing new."
    return head + "\n\n" + "\n\n".join(f"## {t}\n" + "\n".join(ls) for t, ls in secs) + "\n"


def write(vault, text, aud):
    rel = f"06-Outbox/digest-{today()}-{aud}.md"
    path = os.path.join(vault.root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    return rel
