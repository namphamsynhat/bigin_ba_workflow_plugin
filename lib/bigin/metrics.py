"""Token / agent accounting per run (``_runs/<id>/metrics.jsonl``) and budget checks.

Two kinds of row, never added together:

- **estimated** (``est: true``) — written by ``bigin ingest`` for every agent output, with no agent or
  orchestrator involved: (card + task input + the source lines it names + output) bytes / 4. A lower
  bound — it leaves out the harness prompt and any re-read — but it is always there, so a run always
  has a cost figure and the budgets always have something to check.
- **measured** — ``bigin metrics add --usage "<usage block>"`` from a task notification, when the
  orchestrator has one.

``bigin metrics report <run>`` prints both per stage / feature / agent and flags budget overruns
declared in project.md (``budgets: {transform_per_feature_tokens: 600000, extract_per_note_tokens: 150000}``).
"""
import os
import re

from .util import EngineError, append_jsonl, load_json, load_jsonl, today
from .vault import PLUGIN_ROOT

# output kind → (stage, agent, card, task-input suffixes tried in order)
TASK_OF = {
    "signals": ("extract", "signal-extractor", "extractor.md", ("extract",)),
    "audit": ("extract", "signal-auditor", "auditor.md", ("audit",)),
    "filing": ("extract", "signal-filer", "filer.md", ("file",)),
    "analysis": ("extract", "intake-analyst", "analyst.md", ("analyze",)),
    "route": ("transform", "uc-router", "router.md", ("route",)),
    "changesets": ("transform", "uc-router", "router.md", ("draft", "route", "split")),
    "adjudication": ("transform", "code-adjudicator", "adjudicator.md", ("adjudicate",)),
}


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def _source_bytes(vault, task_in):
    """Bytes of the note line ranges an extract/audit task input tells the agent to read."""
    try:
        w = load_json(task_in)
        if not isinstance(w, dict) or not w.get("src_blocks") or not w.get("path"):
            return 0
        with open(os.path.join(vault.root, w["path"]), encoding="utf-8") as f:
            lines = f.read().split("\n")
        new_only = any(b.get("new") for b in w["src_blocks"])
        n = 0
        for b in w["src_blocks"]:
            if new_only and not b.get("new"):
                continue
            first, last = (b.get("lines") or [0, 0])[:2]
            n += sum(len(x.encode("utf-8")) + 1 for x in lines[max(first - 1, 0):last])
        return n
    except (OSError, ValueError, TypeError, IndexError):
        return 0


def estimate(vault, run, out_path, kind):
    """Record what one agent task must have read and written, from the files alone (see module doc)."""
    if kind not in TASK_OF or not run:
        return None
    stage, agent, card, suffixes = TASK_OF[kind]
    tasks = os.path.join(vault.runs_dir, run, "tasks")
    base = re.sub(r"\.out\.json$", "", os.path.basename(out_path))
    stem = re.sub(r"\.[a-z]+\d*$", "", base)                      # INT-003.signals → INT-003
    names = [f"{stem}.{sfx}.in.json" for sfx in suffixes] + [f"{base}.in.json"]
    task_in = next((os.path.join(tasks, n) for n in names if os.path.exists(os.path.join(tasks, n))), None)
    b = {"card": _size(os.path.join(PLUGIN_ROOT, "cards", card)), "in": _size(task_in) if task_in else 0,
         "source": _source_bytes(vault, task_in) if task_in else 0, "out": _size(out_path)}
    if kind == "changesets" and task_in:   # Phase B also reads its own Phase A routing
        b["in"] += _size(os.path.join(tasks, f"{stem}.route.out.json"))
    e = {"stage": stage, "task": stem, "agent": agent, "feature": stem if stage == "transform" else None,
         "tokens": sum(b.values()) // 4, "est": True, "kind": kind, "bytes": b, "at": today()}
    append_jsonl(os.path.join(vault.runs_dir, run, "metrics.jsonl"), e)
    return e


def estimate_design(vault, run, slug, spec_path):
    """The screens worker's lower bound: its card, its worklist, the stage guide it is told to read, and
    the spec it wrote. Recorded at `bigin design close`; a measured row replaces nothing, as elsewhere."""
    tasks = os.path.join(vault.runs_dir, run, "tasks")
    guide = os.path.join(vault.root, "_bigin", "stages", "design", "3-screens.md")
    if not os.path.exists(guide):
        guide = os.path.join(PLUGIN_ROOT, "workspace", "stages", "design", "3-screens.md")
    b = {"card": _size(os.path.join(PLUGIN_ROOT, "cards", "design-screens.md")),
         "in": _size(os.path.join(tasks, f"{slug}.design.in.json")), "source": _size(guide), "out": _size(spec_path)}
    e = {"stage": "design", "task": slug, "agent": "design-screens", "feature": slug,
         "tokens": sum(b.values()) // 4, "est": True, "kind": "design", "bytes": b, "at": today()}
    append_jsonl(os.path.join(vault.runs_dir, run, "metrics.jsonl"), e)
    return e


def parse_usage(text):
    out = {}
    for key in ("total_tokens", "tool_uses", "duration_ms"):
        m = re.search(rf"{key}\s*[:=]\s*(\d+)", text or "")
        if m:
            out[key] = int(m.group(1))
    return out


def add(vault, run, stage, task, agent, tokens=0, feature=None, tool_uses=0, duration_ms=0, usage=None):
    if not run:
        raise EngineError("metrics add needs --run")
    u = parse_usage(usage) if usage else {}
    e = {"stage": stage, "task": task, "agent": agent, "feature": feature,
         "tokens": int(u.get("total_tokens", tokens) or 0), "tool_uses": int(u.get("tool_uses", tool_uses) or 0),
         "duration_ms": int(u.get("duration_ms", duration_ms) or 0), "at": today()}
    append_jsonl(os.path.join(vault.runs_dir, run, "metrics.jsonl"), e)
    return e


# ---------------------------------------------------------------------------- quality (passive, no LLM)
#
# ``_runs/<id>/quality.jsonl`` rows {kind, value, ref, feature, at}, written by the engine at ingest / apply time:
#   unverified_rate · uncovered_pct   per note (write-signals; ref = INT)
#   audit_finding:<kind>              one row per auditor finding (audit-apply)
#   repair_round:<what>               a schema / quote / why repair round the workflow had to spend
#   approved_flip                     an approved UC/BR knocked back to draft by a change (apply; ref = id)
# Question latency is not stored: a ticked question keeps ``(asked:)`` and gains ``(answered:)``.

def quality_add(vault, run, kind, value=1, ref=None, feature=None):
    """Append one quality row to the run; silent when there is no run (a hand-run command costs nothing)."""
    if not run or not os.path.isdir(os.path.join(vault.runs_dir, run)):
        return None
    e = {"kind": kind, "value": value, "ref": ref, "feature": feature, "at": today()}
    append_jsonl(os.path.join(vault.runs_dir, run, "quality.jsonl"), e)
    return e


def question_latency(vault):
    """Days from ``(asked:)`` to ``(answered:)`` for every question the vault has seen answered."""
    import datetime

    from .vault import questions_in
    days = []
    docs = [vault.load(p) for p in vault.note_paths() + vault.hub_paths() + vault.uc_paths() + vault.br_paths()]
    for d in docs:
        for q in questions_in(d, 0, len(d.lines)):
            a = re.search(r"\(asked:\s*(\d{4}-\d{2}-\d{2})\)", q.text)
            b = re.search(r"\(answered:\s*(\d{4}-\d{2}-\d{2})\)", q.text)
            if q.checked and a and b:
                try:
                    days.append((datetime.date.fromisoformat(b.group(1)) - datetime.date.fromisoformat(a.group(1))).days)
                except ValueError:
                    pass
    return sorted(days)


def quality_report(vault, run=None):
    """Per run (or every run) and per feature aggregates of the quality rows, plus vault-wide question latency."""
    runs = [run] if run else (sorted(os.listdir(vault.runs_dir)) if os.path.isdir(vault.runs_dir) else [])
    per_run, per_feature = {}, {}
    for rid in runs:
        rows = load_jsonl(os.path.join(vault.runs_dir, rid, "quality.jsonl"))
        if not rows:
            continue
        agg = {}
        for r in rows:
            k = r["kind"]
            a = agg.setdefault(k, {"n": 0, "sum": 0.0})
            a["n"] += 1
            a["sum"] += float(r.get("value") or 0)
            if r.get("feature"):
                f = per_feature.setdefault(r["feature"], {})
                f[k] = f.get(k, 0) + 1
        per_run[rid] = {k: ({"n": a["n"], "mean": round(a["sum"] / a["n"], 3)} if k in ("unverified_rate", "uncovered_pct")
                            else {"n": a["n"]}) for k, a in agg.items()}
    lat = question_latency(vault)
    return {"runs": per_run, "features": per_feature,
            "question_latency_days": {"n": len(lat), "median": lat[len(lat) // 2] if lat else None,
                                      "max": lat[-1] if lat else None}}


def render_quality(q):
    lines = []
    for rid, agg in sorted(q["runs"].items()):
        lines.append(f"run {rid}: " + ", ".join(f"{k} {v['mean'] if 'mean' in v else v['n']}" + (f" (n={v['n']})" if 'mean' in v else "")
                                                 for k, v in sorted(agg.items())))
    for f, agg in sorted(q["features"].items()):
        lines.append(f"feature {f}: " + ", ".join(f"{k} ×{n}" for k, n in sorted(agg.items())))
    ql = q["question_latency_days"]
    lines.append("question latency: " + (f"{ql['n']} answered, median {ql['median']}d, max {ql['max']}d" if ql["n"] else "no answered question yet"))
    return "\n".join(lines) if lines else "no quality rows yet"


def budgets(vault):
    raw = vault.project().fm_get("budgets")
    out = {}
    if isinstance(raw, str):
        for k, v in re.findall(r"([a-z_]+)\s*:\s*(\d+)", raw):
            out[k] = int(v)
    for k in (vault.project().fm.keys() if vault.project().fm else []):
        if k.startswith("budget_"):
            try:
                out[k[len("budget_"):]] = int(vault.project().fm_get(k))
            except (TypeError, ValueError):
                pass
    return out


def _agg(rows):
    agg = {"total": 0, "agents": len(rows), "by_stage": {}, "by_feature": {}, "by_agent": {}}
    for r in rows:
        t = r.get("tokens") or 0
        agg["total"] += t
        for key, col in (("by_stage", "stage"), ("by_feature", "feature"), ("by_agent", "agent")):
            k = r.get(col) or "—"
            agg[key][k] = agg[key].get(k, 0) + t
    return agg


def _overruns(rows, b, label=""):
    over = []
    for k, limit in b.items():
        m = re.match(r"^([a-z]+)_per_(feature|note|agent)_tokens$", k)
        if not m:
            continue
        stage, unit = m.groups()
        per = {}
        for r in rows:
            if (r.get("stage") or "").startswith(stage):
                key = r.get("feature") if unit == "feature" else (r.get("task") if unit == "note" else r.get("agent"))
                per[key or "—"] = per.get(key or "—", 0) + (r.get("tokens") or 0)
        for key, t in per.items():
            if t > limit:
                over.append(f"{stage} {unit} {key}: {t:,}{label} > budget {limit:,}")
    return over


def report(vault, run):
    rows = load_jsonl(os.path.join(vault.runs_dir, run or "", "metrics.jsonl")) if run else []
    if run and not rows and not os.path.isdir(os.path.join(vault.runs_dir, run)):
        raise EngineError(f"no run {run}")
    measured = [r for r in rows if not r.get("est")]
    est = [r for r in rows if r.get("est")]
    agg = _agg(measured)
    agg["estimated"] = _agg(est)
    b = budgets(vault)
    # a measured figure is the truth where there is one; the estimate (a lower bound) covers the rest
    agg["overruns"] = _overruns(measured, b) or _overruns(est, b, " (estimated, lower bound)")
    return agg


def render(a):
    lines = [f"tokens {a['total']:,} across {a['agents']} agent run(s)"]
    e = a.get("estimated") or {}
    if e.get("agents"):
        lines.append(f"estimated ≥ {e['total']:,} across {e['agents']} task(s) — from task files, a lower bound")
    for src, tag in ((a, ""), (e, "est. ")):
        for key in ("by_stage", "by_feature", "by_agent"):
            if src.get(key):
                top = sorted(src[key].items(), key=lambda x: -x[1])[:8]
                lines.append(f"{tag}{key[3:]}: " + ", ".join(f"{k} {v:,}" for k, v in top))
    for o in a["overruns"]:
        lines.append(f"OVER BUDGET: {o}")
    return "\n".join(lines)
