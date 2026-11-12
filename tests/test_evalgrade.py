"""W6 — golden-set grader arithmetic, case staging, and the passive quality rows."""
import json
import os

from helpers import ROOT, fresh, read, run, write_json

from bigin import evalgrade, metrics

EXP = [{"type": "constraint", "signal": "a", "quote": "Appeals must be filed within 14 days of the rejection"},
       {"type": "requirement", "signal": "b", "quote": "reviewers want to see the previous grants"},
       {"type": "problem", "signal": "c", "quote": "the export only gives me the school name"},
       {"type": "requirement", "signal": "d", "quote": "payments run every Friday"}]
ACT = [{"type": "constraint", "signal": "x", "quote": "Appeals must be filed within 14 days of the rejection."},        # match, same type
       {"type": "decision", "signal": "y", "quote": "reviewers want to see the previous grants"},                       # match, type differs, polarity as-is vs to-be → inversion
       {"type": "requirement", "signal": "z", "quote": "something nobody said at all in this source"}]                  # unmatched (precision)


def test_grade_signals_arithmetic():
    g = evalgrade.grade_signals(EXP, ACT)
    assert g["matched"] == 2 and g["expected"] == 4 and g["actual"] == 3, g
    assert g["recall"] == 0.5 and g["precision"] == 0.667 and g["type_acc"] == 0.5 and g["inversions"] == 1, g
    assert len(g["missed"]) == 2


def test_matching_is_one_to_one_and_ignores_case_and_punctuation():
    exp = [{"type": "requirement", "signal": "s", "quote": "Appeals must be FILED within 14 days"}]
    act = [{"type": "requirement", "signal": "s1", "quote": "appeals must be filed, within 14 days!"},
           {"type": "requirement", "signal": "s2", "quote": "appeals must be filed within 14 days"}]
    g = evalgrade.grade_signals(exp, act)
    assert g["matched"] == 1 and g["precision"] == 0.5, g


def test_grade_routing_lane_and_target_accuracy():
    exp = [{"row": 1, "lane": "uc", "target": "UC-003"}, {"row": 2, "lane": "br", "target": "new:rule"},
           {"row": 3, "lane": "question", "target": "none"}, {"row": 4, "lane": "uc", "target": "UC-001"}]
    act = [{"row": 1, "lane": "uc", "target": "UC-003"}, {"row": "2", "lane": "br", "target": "new:other"},
           {"row": 3, "lane": "hold", "target": "none"}, {"row": 4, "lane": "uc", "target": "UC-002"}]
    g = evalgrade.grade_routing(exp, act)
    assert g == {"expected": 4, "lane_acc": 0.75, "target_acc": 0.5}, g


def test_prepare_then_grade_the_seed_case_end_to_end():
    root, v = fresh("comm-vault")
    rid = json.loads(run(root, "--json", "run", "new", "--stage", "eval")[1])["id"]
    cases = os.path.join(ROOT, "tests", "evals")
    prep = json.loads(run(root, "--json", "eval", "prepare", rid, "--cases", cases)[1])
    assert prep[0]["case"] == "appeals-email", prep
    w = json.load(open(os.path.join(root, prep[0]["extract_in"]), encoding="utf-8"))
    assert os.path.exists(os.path.join(root, w["path"])) and "evals/appeals-email" in w["path"].replace("\\", "/"), w
    # the extractor's output for the case (as the real agent would write it) → graded against the expected rows
    write_json(root, f"_runs/{rid}/tasks/appeals-email.signals.out.json", {"kind": "signals", "int": "INT-003", "rows": [
        {"type": "constraint", "signal": "Appeals within 14 days", "source": "s", "quote": "Appeals must be filed within 14 days of the rejection"},
        {"type": "requirement", "signal": "See previous grants", "source": "s", "quote": "reviewers want to see the applicant's previous grants when reviewing"}]})
    code, out = run(root, "--json", "eval", "grade", rid, "--cases", cases)
    res = json.loads(out)
    assert code == 0 and res["aggregate"]["recall"] == 1.0 and res["aggregate"]["precision"] == 1.0 and res["aggregate"]["inversions"] == 0, res
    code, out = run(root, "eval", "grade", rid, "--cases", cases)
    assert "recall" in out and "appeals-email" in out


def test_quality_rows_are_written_by_the_engine_and_reported():
    root, v = fresh("comm-vault")
    rid = json.loads(run(root, "--json", "run", "new", "--stage", "extract")[1])["id"]
    sig = write_json(root, "s.json", {"kind": "signals", "int": "INT-003", "rows": [
        {"type": "constraint", "signal": "Appeals in 14 days", "source": "s", "quote": "Appeals must be filed within 14 days of the rejection"},
        {"type": "requirement", "signal": "Invented", "source": "s", "quote": "never said"}]})
    assert run(root, "note", "write-signals", sig, "--run", rid)[0] == 0
    aud = write_json(root, "a.json", {"kind": "audit", "int": "INT-003", "verdict": "repaired",
                                      "findings": [{"kind": "missed", "n": 1}, {"kind": "missed"}, {"kind": "inverted", "n": 2}], "repairs": []})
    assert run(root, "note", "audit-apply", aud, "--run", rid)[0] == 0
    assert run(root, "metrics", "quality-add", "--run", rid, "--kind", "repair_round:schema", "--task", "INT-003")[0] == 0
    q = json.loads(run(root, "--json", "metrics", "report", "--quality", "--run", rid)[1])
    r = q["runs"][rid]
    assert r["unverified_rate"]["mean"] == 0.5 and r["audit_finding:missed"]["n"] == 2 and r["repair_round:schema"]["n"] == 1, r
    assert "uncovered_pct" in r
    # a hand-run command (no run) records nothing and costs nothing
    assert metrics.quality_add(v, None, "x") is None


def test_question_latency_runs_from_asked_to_answered():
    root, v = fresh("comm-vault")
    import re
    p = os.path.join(root, "00-Inbox/INT-001.md")
    s = read(root, "00-Inbox/INT-001.md")
    s = re.sub(r"(## Open Questions\n)", r"\1\n- [x] Q: Is it due? (owner: client) (asked: 2026-09-20) (answered: 2026-09-27)\n  A: yes\n", s, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    q = json.loads(run(root, "--json", "metrics", "report", "--quality")[1])
    assert q["question_latency_days"]["n"] == 1 and q["question_latency_days"]["median"] == 7, q
