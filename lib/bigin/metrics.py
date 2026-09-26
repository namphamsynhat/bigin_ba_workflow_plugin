"""Token / agent accounting per run (``_runs/<id>/metrics.jsonl``) and budget checks.

Skills call ``bigin metrics add`` with each task notification's <usage> block; ``bigin metrics
report <run>`` prints tokens per stage / feature / agent and flags budget overruns declared in
project.md (``budgets: {transform_per_feature_tokens: 600000, extract_per_note_tokens: 150000}``).
"""
import os
import re

from .util import EngineError, append_jsonl, load_jsonl, today


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


def report(vault, run):
    rows = load_jsonl(os.path.join(vault.runs_dir, run or "", "metrics.jsonl")) if run else []
    if run and not rows and not os.path.isdir(os.path.join(vault.runs_dir, run)):
        raise EngineError(f"no run {run}")
    agg = {"total": 0, "agents": len(rows), "by_stage": {}, "by_feature": {}, "by_agent": {}}
    for r in rows:
        t = r.get("tokens") or 0
        agg["total"] += t
        for key, col in (("by_stage", "stage"), ("by_feature", "feature"), ("by_agent", "agent")):
            k = r.get(col) or "—"
            agg[key][k] = agg[key].get(k, 0) + t
    over = []
    b = budgets(vault)
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
                over.append(f"{stage} {unit} {key}: {t:,} > budget {limit:,}")
    agg["overruns"] = over
    return agg


def render(a):
    lines = [f"tokens {a['total']:,} across {a['agents']} agent run(s)"]
    for key in ("by_stage", "by_feature", "by_agent"):
        if a[key]:
            top = sorted(a[key].items(), key=lambda x: -x[1])[:8]
            lines.append(f"{key[3:]}: " + ", ".join(f"{k} {v:,}" for k, v in top))
    for o in a["overruns"]:
        lines.append(f"OVER BUDGET: {o}")
    return "\n".join(lines)
