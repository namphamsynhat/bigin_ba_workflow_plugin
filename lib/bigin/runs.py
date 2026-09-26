"""Run ledger under ``_runs/<run-id>/``: plan.json, tasks/*.json (agent inputs/outputs),
results.jsonl, metrics.jsonl, report.md. Machine-readable, resumable, never re-read by agents.
The orchestrator reads ``bigin run summary`` (≤ 20 lines) between steps — never transcripts."""
import datetime
import os
import re
import shutil

from . import jsonschema_lite
from .util import EngineError, append_jsonl, dump_json, load_json, load_jsonl, today

KINDS = ("changesets", "route", "signals", "audit", "filing", "adjudication", "verdicts")


def run_dir(vault, run):
    if not run or not re.match(r"^[A-Za-z0-9._-]+$", run):
        raise EngineError(f"bad run id '{run}'")
    return os.path.join(vault.runs_dir, run)


def new_run(vault, stage, scope=None):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    rid = f"{stamp}-{stage or 'run'}" + (f"-{re.sub(r'[^A-Za-z0-9-]', '-', scope)}" if scope else "")
    d = run_dir(vault, rid)
    os.makedirs(os.path.join(d, "tasks"), exist_ok=True)
    plan = {"id": rid, "stage": stage, "scope": scope, "created": today(), "tasks": []}
    dump_json(plan, os.path.join(d, "plan.json"))
    return plan


def record(vault, run, task, status, note=None):
    e = {"task": task, "status": status, "note": note or "", "at": datetime.datetime.now().isoformat(timespec="seconds")}
    append_jsonl(os.path.join(run_dir(vault, run), "results.jsonl"), e)
    return e


def done_tasks(vault, run):
    return {e["task"] for e in load_jsonl(os.path.join(run_dir(vault, run), "results.jsonl"))
            if e.get("status") in ("ok", "applied", "already", "skipped")}


def _kind_of(path, data, kind):
    if kind:
        return kind
    if isinstance(data, dict) and data.get("kind") in KINDS:
        return data["kind"]
    for k in KINDS:
        if k in os.path.basename(path):
            return k
    raise EngineError(f"{path}: cannot tell the schema — pass --kind")


def ingest(vault, path, kind=None, run=None):
    """Validate an agent's output file; store it under the run. Errors go back to the same agent."""
    try:
        data = load_json(path)
    except ValueError as e:
        return {"ok": False, "path": path, "errors": [f"not valid JSON: {e}"]}
    kind = _kind_of(path, data, kind)
    errs = jsonschema_lite.check(data, kind)
    res = {"ok": not errs, "path": path, "kind": kind, "errors": errs[:20]}
    if run:
        d = os.path.join(run_dir(vault, run), "tasks")
        os.makedirs(d, exist_ok=True)
        if os.path.abspath(os.path.dirname(path)) != os.path.abspath(d):
            shutil.copy2(path, os.path.join(d, os.path.basename(path)))
        record(vault, run, os.path.basename(path), "ok" if not errs else "failed",
               f"{kind}: {len(errs)} schema error(s)" if errs else kind)
    return res


def render_ingest(res):
    if res["ok"]:
        return f"OK {os.path.basename(res['path'])} ({res['kind']})"
    return f"INVALID {os.path.basename(res['path'])}:\n  " + "\n  ".join(res["errors"])


def summary(vault, run):
    d = run_dir(vault, run)
    if not os.path.isdir(d):
        raise EngineError(f"no run {run}")
    plan = load_json(os.path.join(d, "plan.json")) if os.path.exists(os.path.join(d, "plan.json")) else {}
    results = load_jsonl(os.path.join(d, "results.jsonl"))
    counts = {}
    for e in results:
        counts[e.get("status")] = counts.get(e.get("status"), 0) + 1
    metrics = load_jsonl(os.path.join(d, "metrics.jsonl"))
    tokens = sum(int(m.get("tokens") or 0) for m in metrics)
    problems = [e for e in results if e.get("status") in ("failed", "blocked", "drift", "invalid")]
    return {"id": run, "stage": plan.get("stage"), "scope": plan.get("scope"), "counts": counts,
            "agents": len(metrics), "tokens": tokens, "problems": problems[-10:]}


def render_summary(s):
    lines = [f"run {s['id']} — {s.get('stage') or '?'} {s.get('scope') or ''}".rstrip(),
             "results: " + (", ".join(f"{k} {v}" for k, v in sorted(s["counts"].items())) or "none"),
             f"agents: {s['agents']} · tokens: {s['tokens']:,}"]
    for p in s["problems"]:
        lines.append(f"  {p.get('status')}: {p.get('task')} {p.get('target') or ''} {p.get('note') or ''}".rstrip())
    return "\n".join(lines[:20])
