"""Golden-set grading — code only, no LLM. ``bigin eval grade <run>``.

A case is a folder ``tests/evals/<case>/``:

  note.md                  the source note (an intake note with ## Raw), as the extractor reads it
  extract.in.json          the extractor's task input for it (worklist shape; ``path`` points at note.md)
  signals.expected.json    the BA-corrected rows: [{"type", "signal", "quote", "polarity"?}]
  route.in.json            (optional) the router's Phase A worklist
  routing.expected.json    (optional) [{"row": <n>, "lane", "target"}]

``workflows/eval.js`` runs the real extractor (and router) on each case and writes
``_runs/<run>/tasks/<case>.signals.out.json`` / ``<case>.route.out.json``; this module grades those files.

Rows are matched by quote overlap (token Jaccard of the quote, else of the signal text), greedily, best first.
  recall      matched expected / expected          precision   matched actual / actual
  type_acc    matched pairs with the same type     inversions  matched pairs whose polarity is opposite
  lane_acc    expected routes whose lane matches   target_acc  … whose target matches (new:* ≡ new:*)
"""
import os
import re

from .quotes import norm
from .util import EngineError, load_json

MATCH_AT = 0.5
AS_IS = {"problem", "pain-point", "decision", "constraint"}
TO_BE = {"requirement", "commitment"}


def _tokens(row):
    t = norm(row.get("quote") or row.get("signal") or "")
    return set(re.findall(r"[a-z0-9]+", t))


def _jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def polarity(row):
    p = row.get("polarity")
    if p in ("as-is", "to-be"):
        return p
    t = row.get("type")
    return "as-is" if t in AS_IS else "to-be" if t in TO_BE else None


def match(expected, actual):
    """[(i_expected, j_actual)] — greedy, best overlap first, each row used once, overlap ≥ MATCH_AT."""
    te, ta = [_tokens(r) for r in expected], [_tokens(r) for r in actual]
    scored = sorted(((_jaccard(te[i], ta[j]), i, j) for i in range(len(te)) for j in range(len(ta))), reverse=True)
    used_e, used_a, out = set(), set(), []
    for s, i, j in scored:
        if s < MATCH_AT:
            break
        if i in used_e or j in used_a:
            continue
        used_e.add(i)
        used_a.add(j)
        out.append((i, j))
    return sorted(out)


def grade_signals(expected, actual):
    pairs = match(expected, actual)
    same_type = sum(1 for i, j in pairs if expected[i].get("type") == actual[j].get("type"))
    inv = sum(1 for i, j in pairs if polarity(expected[i]) and polarity(actual[j]) and polarity(expected[i]) != polarity(actual[j]))
    return {"expected": len(expected), "actual": len(actual), "matched": len(pairs),
            "recall": round(len(pairs) / len(expected), 3) if expected else None,
            "precision": round(len(pairs) / len(actual), 3) if actual else None,
            "type_acc": round(same_type / len(pairs), 3) if pairs else None, "inversions": inv,
            "missed": [expected[i].get("signal", "")[:80] for i in range(len(expected)) if i not in {p[0] for p in pairs}]}


def grade_routing(expected, actual):
    by_row = {}
    for r in actual:
        by_row.setdefault(str(r.get("row")), []).append(r)

    def tgt(x):
        return "new" if str(x).startswith("new:") else str(x)

    lane = target = 0
    for e in expected:
        got = by_row.get(str(e["row"]), [])
        if any(g.get("lane") == e.get("lane") for g in got):
            lane += 1
            if any(g.get("lane") == e.get("lane") and tgt(g.get("target")) == tgt(e.get("target")) for g in got):
                target += 1
    n = len(expected)
    return {"expected": n, "lane_acc": round(lane / n, 3) if n else None, "target_acc": round(target / n, 3) if n else None}


def _rows(path):
    d = load_json(path)
    return d["rows"] if isinstance(d, dict) and "rows" in d else d


def grade_case(case_dir, tasks_dir):
    case = os.path.basename(case_dir.rstrip("/"))
    out = {"case": case}
    sig = os.path.join(tasks_dir, f"{case}.signals.out.json")
    if os.path.exists(sig):
        out["signals"] = grade_signals(_rows(os.path.join(case_dir, "signals.expected.json")), _rows(sig))
    else:
        out["signals"] = None
    rte, rout = os.path.join(case_dir, "routing.expected.json"), os.path.join(tasks_dir, f"{case}.route.out.json")
    if os.path.exists(rte) and os.path.exists(rout):
        d = load_json(rout)
        out["routing"] = grade_routing(load_json(rte), d.get("routes") if isinstance(d, dict) else d)
    return out


def cases_in(cases_dir):
    if not os.path.isdir(cases_dir):
        raise EngineError(f"no cases at {cases_dir}")
    return [c for c in sorted(os.listdir(cases_dir)) if os.path.isfile(os.path.join(cases_dir, c, "signals.expected.json"))]


def prepare(vault, run, cases_dir):
    """Stage each case under the run so the extractor / router read it like a vault file: copy the case to
    ``_runs/<run>/evals/<case>/`` and write ``tasks/<case>.extract.in.json`` (and ``.route.in.json``) with
    ``path`` pointing at the copy. Returns [{case, extract_in, route_in|None}]."""
    import json
    import shutil
    base = os.path.join(vault.runs_dir, run)
    if not os.path.isdir(base):
        raise EngineError(f"no run {run} — `bigin run new --stage eval` first")
    tasks = os.path.join(base, "tasks")
    os.makedirs(tasks, exist_ok=True)
    out = []
    for c in cases_in(cases_dir):
        dst = os.path.join(base, "evals", c)
        shutil.copytree(os.path.join(cases_dir, c), dst, dirs_exist_ok=True)
        entry = {"case": c, "route_in": None}
        for kind in ("extract", "route"):
            src = os.path.join(dst, f"{kind}.in.json")
            if not os.path.exists(src):
                continue
            w = load_json(src)
            if "path" in w:
                w["path"] = os.path.relpath(os.path.join(dst, "note.md"), vault.root)
            target = os.path.join(tasks, f"{c}.{kind}.in.json")
            with open(target, "w", encoding="utf-8", newline="\n") as f:
                json.dump(w, f, indent=2, ensure_ascii=False)
            entry[f"{kind}_in" if kind == "route" else "extract_in"] = os.path.relpath(target, vault.root)
        out.append(entry)
    return out


def grade(vault, run, cases_dir):
    tasks = os.path.join(vault.runs_dir, run, "tasks")
    if not os.path.isdir(tasks):
        raise EngineError(f"no run {run} (no {tasks})")
    cases = [grade_case(os.path.join(cases_dir, c), tasks) for c in cases_in(cases_dir)]
    graded = [c["signals"] for c in cases if c["signals"]]
    tot = lambda k: sum(g[k] for g in graded)  # noqa: E731
    agg = {"cases": len(cases), "graded": len(graded)}
    if graded:
        agg.update(recall=round(tot("matched") / tot("expected"), 3) if tot("expected") else None,
                   precision=round(tot("matched") / tot("actual"), 3) if tot("actual") else None,
                   type_acc=round(sum(g["type_acc"] * g["matched"] for g in graded if g["type_acc"] is not None) / tot("matched"), 3)
                   if tot("matched") else None, inversions=tot("inversions"))
    rt = [c["routing"] for c in cases if c.get("routing")]
    if rt:
        n = sum(r["expected"] for r in rt)
        agg.update(lane_acc=round(sum(r["lane_acc"] * r["expected"] for r in rt) / n, 3),
                   target_acc=round(sum(r["target_acc"] * r["expected"] for r in rt) / n, 3))
    return {"run": run, "aggregate": agg, "cases": cases}


def render(res):
    a = res["aggregate"]
    lines = [f"eval {res['run']}: {a['graded']}/{a['cases']} case(s) graded"]
    for k in ("recall", "precision", "type_acc", "inversions", "lane_acc", "target_acc"):
        if k in a and a[k] is not None:
            lines.append(f"  {k:<10} {a[k]}")
    for c in res["cases"]:
        s = c.get("signals")
        lines.append(f"  {c['case']}: " + (f"recall {s['recall']} precision {s['precision']} type {s['type_acc']} inversions {s['inversions']}"
                                           if s else "no extractor output"))
        for m in (s or {}).get("missed", [])[:3]:
            lines.append(f"      missed: {m}")
    return "\n".join(lines)
