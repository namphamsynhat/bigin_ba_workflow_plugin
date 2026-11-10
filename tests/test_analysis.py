"""Extract-time analysis (`worklist analyze` → `note analysis-apply`) and withdrawal of a removed request
(`note withdraw`, the Jira `withdrawn` phase, retraction through `bigin apply`)."""
import json
import os

from helpers import fresh, read, run, write_json

from bigin import model
from bigin.vault import Doc, Vault

import test_jira_intake as tj

HUB = "01-Requirements/_features/payments.md"
NOTE = "00-Inbox/INT-002.md"


def _json(root, *args):
    code, out = run(root, "--json", *args)
    assert code == 0, out
    return json.loads(out)


def _hub_rows(root, slug="payments"):
    v = Vault(root)
    return {r.num: r for r in model.signal_rows(model.signal_doc(v, slug))}


def _analysis(**kw):
    a = {"kind": "analysis", "int": "INT-002",
         "summary": "Finance wants grants paid within 10 days, bank details confirmed first, and sign-off over $10,000.",
         "flow": ["Finance officer opens an approved grant", "Applicant confirms bank details",
                  "Finance officer releases the payment"],
         "affected": [{"target": "UC-003", "feature": "payments", "refs": ["S2"], "change": "modify",
                       "note_rows": [2], "why": "payment deadline lands on the transfer step"},
                      {"target": "new", "feature": "payments", "title": "Confirm bank details", "change": "new-goal",
                       "note_rows": [6], "why": "no UC covers the applicant confirming bank details"}],
         "conflicts": [{"note_rows": [6], "with": "BR-006", "existing": "Finance confirms the bank details",
                        "incoming": "The applicant confirms their bank details", "severity": "blocking",
                        "question": "Who confirms the bank details before payment — the applicant or finance?",
                        "owner": "client"}],
         "questions": [{"text": "What happens if the 10-day deadline falls on a bank holiday?", "kind": "gap",
                        "about": "UC-003 S2", "owner": "client", "note_rows": [2]}]}
    a.update(kw)
    return a


def test_worklist_analyze_reads_current_requirements():
    root, _ = fresh("comm-vault")
    w = _json(root, "worklist", "analyze", "INT-002")
    assert w["stage"] == "analyze" and set(w["features"]) >= {"payments", "grant-intake"}
    assert any(c["id"] == "UC-003" for c in w["candidates"]) and any(b["id"] == "BR-006" for b in w["brs"])
    assert {h["row"] for h in w["hub_rows"] if h["hub"] == "payments"} == {"1", "2", "3", "4"}
    assert len(w["rows"]) == 6 and w["output"] == "analysis"


def test_analysis_apply_writes_section_questions_and_holds_conflict():
    root, _ = fresh("comm-vault")
    p = write_json(root, "a.json", _analysis())
    res = _json(root, "note", "analysis-apply", p)
    assert res["blocking"] == 1 and res["questions_added"] == 2 and res["status"] == "needs-clarification", res
    assert res["rows_flagged"] == ["payments #4"]
    d = Doc(read(root, NOTE))
    body = d.get("Analysis")
    assert "engine-owned" in body and "UC-003" in body and "new: Confirm bank details" in body
    assert "BR-006" in body and "blocking" in body and "[gap]" in body and "Requested flow" in body
    oq = d.get("Open Questions")
    assert "Who confirms the bank details" in oq and "(conflict: INT-002 #6 vs BR-006)" in oq and "bank holiday" in oq
    assert {int(r.num): r.get("Status") for r in model.note_rows(d)}[6] == "conflict"
    assert _hub_rows(root)["4"].status == "conflict" and "INT-002 ## Analysis" in _hub_rows(root)["4"].get("Notes")
    assert os.path.exists(os.path.join(root, "01-Requirements", "_impact", "INT-002.analysis.json"))
    # a re-run replaces the section and never duplicates a question
    res2 = _json(root, "note", "analysis-apply", p)
    assert res2["questions_added"] == 0
    import re
    assert len(re.findall(r"^## Analysis$", read(root, NOTE), re.M)) == 1


def test_analysis_apply_rejects_unknown_rows_and_targets():
    root, _ = fresh("comm-vault")
    bad = write_json(root, "b.json", _analysis(conflicts=[], questions=[], affected=[
        {"target": "UC-099", "change": "modify", "note_rows": [2], "why": "x"}]))
    code, out = run(root, "note", "analysis-apply", bad)
    assert code != 0 and "UC-099" in out
    bad = write_json(root, "c.json", _analysis(conflicts=[], questions=[], affected=[
        {"target": "UC-003", "change": "modify", "note_rows": [42], "why": "x"}]))
    code, out = run(root, "note", "analysis-apply", bad)
    assert code != 0 and "#42" in out


def _as_ticket(root):
    p = os.path.join(root, NOTE)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("source: meeting", "source: jira\njira_key: ACME-7", 1))


def test_withdraw_refuses_a_meeting_note():
    root, _ = fresh("comm-vault")
    code, out = run(root, "note", "withdraw", "INT-002", "--reason", "x")
    assert code != 0 and "feature withdraw" in out, out


def test_withdraw_closes_rows_and_queues_retraction():
    root, _ = fresh("comm-vault")
    _as_ticket(root)
    code, out = run(root, "note", "withdraw", "INT-002")
    assert code != 0 and "--reason" in out
    res = _json(root, "note", "withdraw", "INT-002", "--reason", "client cancelled the payment change",
                "--by", "client email 2026-09-27")
    rows = _hub_rows(root)
    assert rows["1"].status == "retract" and "take it out of UC-003 S2 · BR-004" in rows["1"].get("Notes")
    assert rows["2"].status == "withdrawn" and rows["3"].status == "withdrawn" and rows["4"].status == "withdrawn"
    assert "payments #1" in res["rows"]["retract"] and set(res["retract_ucs"]) >= {"UC-003", "BR-004"}
    d = Doc(read(root, NOTE))
    assert d.fm_get("status") == "withdrawn" and d.fm_get("withdrawn_reason") == "client cancelled the payment change"
    w = d.get("Withdrawal")
    assert "client cancelled the payment change" in w and "client email 2026-09-27" in w
    assert all(r.get("Status") in ("withdrawn",) for r in model.note_rows(d))
    # idempotent, and lint accepts the new vocabulary
    assert _json(root, "note", "withdraw", "INT-002", "--reason", "again")["already"]
    code, out = run(root, "lint", "--full")
    assert "illegal Signal Log status" not in out and "illegal note status" not in out, out
    # the route worklist hands the retract row to the router, with what to take out and why
    w = _json(root, "worklist", "route", "payments")
    r1 = next(r for r in w["rows"] if r["row"] == "1")
    assert r1["status"] == "retract" and "client cancelled" in r1["retract"]["reason"]
    assert "UC-003 S2" in r1["retract"]["remove_from"] and any(c["id"] == "UC-003" for c in w["candidates"])
    w = _json(root, "worklist", "route", "payments", "--rows", "4")
    assert {r["row"] for r in w["rows"]} == {"1", "4"}, "a retract row rides along with Stage 2's qualified rows"
    # analysis is closed on a withdrawn note
    code, out = run(root, "worklist", "analyze", "INT-002")
    assert code != 0 and "withdrawn" in out


def test_retraction_change_set_flips_row_and_records_why():
    root, v = fresh("comm-vault")
    _as_ticket(root)
    _json(root, "note", "withdraw", "INT-002", "--reason", "client cancelled the payment change")
    w = _json(root, "worklist", "route", "payments")
    uc = next(c for c in w["candidates"] if c["id"] == "UC-003")
    s2 = next(s for s in uc["steps"] if s["id"] == "S2")
    cs = {"id": "cs-payments-1r", "trace": {"int": "INT-002", "note_rows": [2], "hub": "payments", "hub_rows": ["1"]},
          "target": {"kind": "UC", "id": "UC-003", "section": "2"}, "op": "drop_step",
          "anchor": {"ref": "S2", "sha": s2["sha"]}, "reason": "removed — INT-002 withdrawn: client cancelled the payment change"}
    p = write_json(root, "r.json", {"kind": "changesets", "changesets": [cs]})
    res = _json(root, "apply", p)
    assert res["applied"], res
    row = _hub_rows(root)["1"]
    assert row.status == "withdrawn" and "retracted from UC-003 S2" in row.get("Notes")
    from helpers import find
    text = read(root, find(root, "01-Requirements/_ucs", "UC-003"))
    assert "Dropped — removed — INT-002 withdrawn" in text
    assert "retracts withdrawn INT-002 (2026-09-27: client cancelled the payment change)" in text


def test_jira_withdrawn_phase_withdraws_the_note():
    root = tj.setup()
    p = os.path.join(root, "_bigin", "system", "project.md")
    with open(p, "a", encoding="utf-8") as f:
        f.write("| ACME | * | Cancelled | withdrawn |\n")
    res = tj.capture(root, tj.day1())
    nid = res["id"]
    d = tj.day1()
    d["issue"]["fields"]["status"] = {"name": "Cancelled"}
    d["issue"]["fields"]["updated"] = "2026-10-04T09:00:00.000+0700"
    res = tj.capture(root, d)
    assert res["action"] == "withdrawn" and res["id"] == nid, res
    doc = Doc(read(root, res["path"]))
    assert doc.fm_get("status") == "withdrawn" and "Cancelled" in doc.fm_get("withdrawn_reason")
    # new activity on a withdrawn ticket is captured but never re-opens the note
    d["issue"]["fields"]["status"] = {"name": "To Do"}
    d["issue"]["fields"]["updated"] = "2026-10-06T09:00:00.000+0700"
    d["comments"] = [{"id": "999", "author": tj.ONSHORE, "created": "2026-10-06T09:00:00.000+0700",
                      "updated": "2026-10-06T09:00:00.000+0700", "body": "Actually we may want this later."}]
    res = tj.capture(root, d)
    assert Doc(read(root, res["path"])).fm_get("status") == "withdrawn"
    assert any("withdrawn" in w for w in res["warnings"]), res


def test_feature_withdraw_removes_what_only_it_uses():
    root, _ = fresh("comm-vault")
    code, out = run(root, "feature", "withdraw", "payments")
    assert code != 0 and "--reason" in out
    res = _json(root, "feature", "withdraw", "payments", "--reason", "too costly; no longer fits the market",
                "--by", "client steering meeting 2026-09-27")
    # UC-003 also serves grant-intake (live) → kept; UC-004 only payments → removed
    assert res["removed"] == ["BR-006", "UC-004"], res
    assert any(k.startswith("UC-003") for k in res["kept"]) and any(k.startswith("BR-004") for k in res["kept"])
    from helpers import find
    uc4 = Doc(read(root, find(root, "01-Requirements/_ucs", "UC-004")))
    assert uc4.fm_get("status") == "removed" and uc4.fm_get("version") != "1.0"
    assert "feature payments withdrawn 2026-09-27: too costly" in uc4.get("Changelog")
    assert Doc(read(root, find(root, "01-Requirements/_brs", "BR-006"))).fm_get("status") == "removed"
    assert Doc(read(root, find(root, "01-Requirements/_ucs", "UC-003"))).fm_get("status") == "draft"
    rows = _hub_rows(root)
    assert rows["1"].status == "retract"  # applied into UC-003, which stays
    assert rows["2"].status == rows["3"].status == rows["4"].status == "withdrawn"
    hub = Doc(read(root, HUB))
    assert hub.fm_get("status") == "out-of-scope" and "too costly" in hub.get("Withdrawal")
    assert "| payments | Pay approved grants | out-of-scope |" in read(root, "01-Requirements/FEATURES.md")
    note = {int(r.num): r.get("Status") for r in model.note_rows(Doc(read(root, NOTE)))}
    assert note[2] == note[4] == note[6] == "withdrawn" and note[1] == "new", note  # grant-intake rows stay live
    assert Doc(read(root, NOTE)).fm_get("status") != "withdrawn"  # the meeting itself is not withdrawn
    assert _json(root, "feature", "withdraw", "payments", "--reason", "again")["already"]
    code, out = run(root, "lint", "--full")
    assert "illegal" not in out, out


def test_feature_withdraw_dry_writes_nothing():
    root, _ = fresh("comm-vault")
    from helpers import digest
    before = digest(root)
    _json(root, "feature", "withdraw", "payments", "--reason", "too costly", "--dry")
    assert digest(root) == before
