"""Phase 2 — change sets, the ledger, single writes, worklists, migration of legacy Discussion entries."""
import json
import os
import re

from helpers import ROOT, find, fresh, lint_clean, read, run, write_json

from bigin import model
from bigin.util import sha


def _rw(path, fn):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(fn(text))


def cs(i, **kw):
    base = {"id": f"cs-test-{i}"}
    base.update(kw)
    return base


def apply(root, sets, *extra):
    p = write_json(root, f"cs-{abs(hash(json.dumps(sets))) % 10**8}.json", {"kind": "changesets", "changesets": sets})
    return run(root, "apply", p, *extra)


def uc_text(root, uid):
    return read(root, find(root, "01-Requirements/_ucs", uid))


def test_schema_rejects_bad_change_sets():
    root, _ = fresh("comm-vault")
    code, out = apply(root, [cs(1, target={"kind": "UC", "id": "UC-003"}, op="drop_step")])
    assert code == 2 and "missing required 'anchor'" in out, out


def test_new_step_never_renumbers_and_flags_review():
    root, v = fresh("comm-vault")
    s1 = next(s for s in model.steps(v.load_id("UC-003")) if s.id == "S1")
    code, out = apply(root, [cs(1, trace={"int": "INT-002", "hub": "payments", "hub_rows": ["4"]},
                                target={"kind": "UC", "id": "UC-003", "section": "2"}, op="new_step_after",
                                anchor={"ref": "S1", "sha": sha(s1.text)},
                                cells={"actor": "Finance officer checks bank details.", "system": "System blocks release until confirmed."})])
    assert code == 0, out
    t = uc_text(root, "UC-003")
    ids = re.findall(r"^\| \*\*(S\d+)\*\* \|", t, re.M)
    assert ids == ["S1", "S3", "S2"], ids  # next unused id, placed after the anchor
    assert "§ 2 changed — flagged for review" in t and "cs: cs-test-1." in t
    assert "version: 1.1" in t
    assert re.search(r"^\| 4 \|.*\| applied \| UC-003 S3 \|", read(root, "01-Requirements/_features/payments.md"), re.M)
    lint_clean(root)


def test_apply_is_idempotent():
    root, _ = fresh("comm-vault")
    sets = [cs(1, target={"kind": "UC", "id": "UC-002", "section": "1", "field": "Trigger"}, op="set_field",
               text="The reviewer opens the review queue"),
            cs(2, target={"kind": "UC", "id": "UC-002"}, op="add_question", text="Can a reviewer skip an application?",
               owner="client")]
    apply(root, sets)
    before = uc_text(root, "UC-002")
    code, out = apply(root, sets)
    assert "0 applied · 2 already" in out, out
    assert uc_text(root, "UC-002") == before


def test_drift_raises_one_question_and_overwrites_nothing():
    root, v = fresh("comm-vault")
    s2 = next(s for s in model.steps(v.load_id("UC-002")) if s.id == "S2")
    old_sha = sha(s2.text)
    p = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-002"))
    _rw(p, lambda s: s.replace("Reviewer approves or rejects it.", "Reviewer approves, rejects, or asks for more information."))
    code, out = apply(root, [cs(1, target={"kind": "UC", "id": "UC-002", "section": "2"}, op="replace_step",
                                anchor={"ref": "S2", "sha": old_sha},
                                cells={"actor": "Reviewer approves or rejects it, giving a reason.", "system": "System records the decision."})])
    assert "1 drift" in out, out
    t = uc_text(root, "UC-002")
    assert "asks for more information" in t and "giving a reason" in t.split("## 5.")[1]
    assert "giving a reason" not in t.split("## 5.")[0], "drift overwrote the human's wording"
    assert len(re.findall(r"^- \[ \] Q: S2 of UC-002 was reworded", t, re.M)) == 1
    apply(root, [cs(1, target={"kind": "UC", "id": "UC-002", "section": "2"}, op="replace_step",
                    anchor={"ref": "S2", "sha": old_sha},
                    cells={"actor": "Reviewer approves or rejects it, giving a reason.", "system": "System records the decision."})])
    assert len(re.findall(r"^- \[ \] Q: S2 of UC-002 was reworded", uc_text(root, "UC-002"), re.M)) == 1
    run(root, "status")
    assert "status: needs-clarification" in uc_text(root, "UC-002")


def test_hand_applied_change_counts_as_applied():
    root, v = fresh("comm-vault")
    s1 = next(s for s in model.steps(v.load_id("UC-002")) if s.id == "S1")
    code, out = apply(root, [cs(1, target={"kind": "UC", "id": "UC-002", "section": "2"}, op="replace_step",
                                anchor={"ref": "S1", "sha": "stale0000000"},
                                cells={"actor": s1.actor, "system": s1.system})])
    assert "1 already" in out and "drift" not in out.split("·")[3] or "0 drift" in out, out


def test_gate_goes_to_ledger_then_releases():
    root, v = fresh("comm-vault")
    code, out = apply(root, [cs(1, trace={"int": "INT-002", "hub": "payments", "hub_rows": ["2"]},
                                target={"kind": "UC", "id": "UC-003", "section": "2"}, op="new_step_after",
                                cells={"actor": "Finance officer splits the payment.", "system": "System schedules the instalments."},
                                gate={"question": "May a grant be paid in instalments?", "owner": "client", "blocks": True})])
    assert "1 gated" in out, out
    t = uc_text(root, "UC-003")
    assert "## Pending changes" in t and "cs-test-1" in t and "May a grant be paid in instalments?" in t
    assert "splits the payment" not in t.split("## 3.")[0]
    code, out = run(root, "ledger", "release")
    assert "1 still waiting" in out, out
    p = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-003"))
    s = open(p).read()
    s = re.sub(r"- \[ \] Q: May a grant be paid in instalments\?(.*)\n  A:", r"- [x] Q: May a grant be paid in instalments?\1\n  A: Yes, in up to three instalments.", s)
    open(p, "w").write(s)
    code, out = run(root, "ledger", "release")
    assert "1 released" in out, out
    t = uc_text(root, "UC-003")
    assert "splits the payment" in t.split("## 3.")[0]
    assert "## Pending changes" not in t
    assert "May a grant be paid in instalments?" in t.split("**Decision log**")[1], "settled question not moved"
    assert re.search(r"^\| 2 \|.*\| applied \|", read(root, "01-Requirements/_features/payments.md"), re.M)
    lint_clean(root)


def test_refusal_answer_needs_judgement():
    root, _ = fresh("comm-vault")
    apply(root, [cs(1, target={"kind": "BR", "id": "BR-006"}, op="append_rule_clause", text="Confirmation expires after a year.",
                    gate={"question": "Does a bank-details confirmation expire?", "blocks": True})])
    p = os.path.join(root, find(root, "01-Requirements/_brs", "BR-006"))
    s = open(p).read().replace("- [ ] Q: Does a bank-details confirmation expire?", "- [x] Q: Does a bank-details confirmation expire?")
    s = re.sub(r"(Does a bank-details confirmation expire\?[^\n]*\n\s*A:)", r"\1 No, never.", s)
    open(p, "w").write(s)
    code, out = run(root, "ledger", "release")
    assert "1 need judgement" in out, out
    assert "expires after a year" not in read(root, find(root, "01-Requirements/_brs", "BR-006")).split("## ")[0]
    v = write_json(root, "v.json", {"kind": "verdicts", "verdicts": [{"id": "cs-test-1", "verdict": "supersede", "reason": "answer is no"}]})
    code, out = run(root, "ledger", "release", "--verdicts", v)
    assert "1 superseded" in out, out


def test_flows_drop_and_questions():
    root, v = fresh("comm-vault")
    code, out = apply(root, [
        cs(1, target={"kind": "UC", "id": "UC-001", "section": "3"}, op="new_flow",
           flow={"kind": "E", "name": "The school name is missing", "body": "* **Branch point:** S2\n* **Failure condition:** The school name is blank.\n1. System asks for it.\n2. **Ends:** the parent stays on the draft."}),
        cs(2, target={"kind": "UC", "id": "UC-001", "section": "3"}, op="new_flow",
           flow={"kind": "A", "name": "Parent saves and returns later", "body": "* **Branch point:** S2\n* **Condition:** The parent leaves.\n1. System keeps the draft.\n2. **Rejoins** S2"}),
        cs(3, target={"kind": "UC", "id": "UC-001", "section": "2"}, op="drop_step", anchor={"ref": "S3"}, reason="merged into S2"),
        cs(4, target={"kind": "UC", "id": "UC-001"}, op="answer_question",
           anchor={"ref": "Is there a maximum amount a parent may request?"}, text="Yes: $20,000."),
    ])
    assert "4 applied" in out, out
    t = uc_text(root, "UC-001")
    heads = re.findall(r"^### ([AE]\d+):", t, re.M)
    assert heads == ["A1", "E1", "E2"], heads
    assert "| **S3** | Dropped — merged into S2 | — |" in t
    assert "Is there a maximum amount" in t.split("**Decision log**")[1]
    assert "Is there a maximum amount" not in t.split("**Still open**")[1].split("**Decision log**")[0]
    lint_clean(root)


def test_create_and_mirror_in_one_batch():
    root, _ = fresh("comm-vault")
    code, out = apply(root, [
        cs(1, key="lim", target={"kind": "BR", "id": "new:lim"}, op="create_br",
           create={"title": "Maximum request", "feature": "grant-intake", "statement": "If a parent requests more than $20,000, then the application must be refused."},
           trace={"int": "INT-001"}),
        cs(2, target={"kind": "UC", "id": "UC-001", "section": "4"}, op="mirror_br", br="new:lim", enforced_at="S2"),
    ])
    assert "created: lim=BR-007" in out, out
    t = uc_text(root, "UC-001")
    assert "| BR-007 | If a parent requests more than $20,000" in t
    assert "brs: [BR-001, BR-002, BR-007]" in t
    assert "uc: [UC-001]" in read(root, find(root, "01-Requirements/_brs", "BR-007"))
    assert "BR-007" in read(root, "01-Requirements/_features/grant-intake.md").split("---")[1]
    code, out = apply(root, [cs(3, target={"kind": "UC", "id": "UC-001", "section": "4"}, op="mirror_br", br="BR-004", enforced_at="S9")])
    assert "1 invalid" in out and "S9" in out
    lint_clean(root)


def test_worklist_and_context_are_compact():
    root, _ = fresh("comm-vault")
    code, out = run(root, "--json", "worklist", "route", "payments")
    w = json.loads(out)
    assert [r["row"] for r in w["rows"]] == ["4"]
    uc3 = next(c for c in w["candidates"] if c["id"] == "UC-003")
    assert all("sha" in s for s in uc3["steps"]) and "<!--" not in out
    code, out = run(root, "--json", "context", "UC-001", "--sections", "1,5")
    c = json.loads(out)
    assert "<!--" not in json.dumps(c) and c["card"]["summary"]["Primary Actor"] == "Parent"


def test_migrate_discussion_to_ledger():
    root, v = fresh("comm-vault")
    code, out = run(root, "migrate", "discussion-to-ledger")
    res = json.loads(out)
    assert res["converted"] == 3 and not res["unparsed"], res
    for aid in ("UC-001", "BR-005"):
        d = model.discussion_text(v.__class__(root).load_id(aid))
        assert "**INT-" not in d, f"{aid} still has a staged entry"
    t = uc_text(root, "UC-001")
    assert "| **S5** | Parent appeals a rejection once | System records the appeal and returns the application to review. |" in t
    assert "* **Trigger:** The parent opens the grant application." in t
    assert "approver's name" in read(root, find(root, "01-Requirements/_brs", "BR-005"))
    assert os.listdir(os.path.join(root, "_runs")), "no snapshot / change-set record"
    lint_clean(root)
    code, out = run(root, "migrate", "discussion-to-ledger")
    assert json.loads(out)["converted"] == 0


def test_no_agent_edits_requirement_files():
    """Phase 2 acceptance: only the interactive bigin-ba agent keeps Edit on UC/BR/hub files."""
    for p in os.listdir(os.path.join(ROOT, "agents")):
        text = open(os.path.join(ROOT, "agents", p)).read()
        fm = text.split("---")[1]
        tools = re.search(r"^tools:\s*(.*)$", fm, re.M)
        if p in ("bigin-ba.md", "render-feature-od-worker.md", "hub-bookkeeper.md"):
            continue
        assert tools and "Edit" not in tools.group(1), f"{p} still has Edit: {tools.group(1) if tools else 'all tools'}"


def test_golden_one_run_transform():
    """Phase 2 acceptance: the scripted router output for `payments` lands in ONE run, with zero
    ## Discussion staging, and produces exactly the golden UC-003 / BR-005 / hub (UPDATE_GOLDEN=1 to regenerate)."""
    golden = os.path.join(ROOT, "tests", "golden")
    root, _ = fresh("comm-vault")
    code, out = run(root, "apply", os.path.join(golden, "transform-payments.changesets.json"))
    assert code == 0 and "4 applied" in out, out
    for rel, name in ((find(root, "01-Requirements/_ucs", "UC-003"), "UC-003.md"),
                      (find(root, "01-Requirements/_brs", "BR-005"), "BR-005.md"),
                      ("01-Requirements/_features/payments.md", "payments.md")):
        got = read(root, rel)
        assert "(staged 2026" not in got.split("## Discussion")[-1].split("## Changelog")[0] or name == "BR-005.md"
        gp = os.path.join(golden, name)
        if os.environ.get("UPDATE_GOLDEN") == "1" or not os.path.exists(gp):
            open(gp, "w").write(got)
        assert got == open(gp).read(), f"{name} differs from tests/golden/{name}"
    lint_clean(root)


def test_split_moves_rule_and_resolves_new_keys():
    root, _ = fresh("comm-vault")
    code, out = apply(root, [
        cs(1, key="appeal", target={"kind": "UC", "id": "new:appeal"}, op="create_uc",
           create={"title": "Appeal a rejection", "primary_feature": "grant-intake"}),
        cs(2, target={"kind": "UC", "id": "UC-001", "section": "2"}, op="drop_step", anchor={"ref": "S4"},
           reason="moved to new:appeal"),
        cs(3, target={"kind": "UC", "id": "UC-001", "section": "4"}, op="unmirror_br", br="BR-001", reason="moved to new:appeal"),
    ])
    assert "3 applied" in out, out
    t = uc_text(root, "UC-001")
    assert "| **S4** | Dropped — moved to UC-005 | — |" in t and "| BR-001 |" not in t
    assert "uc: []" in read(root, find(root, "01-Requirements/_brs", "BR-001"))


def test_extract_path_write_signals_then_file_apply():
    root, _ = fresh("comm-vault")
    sig = write_json(root, "sig.json", {"kind": "signals", "int": "INT-003", "rows": [
        {"type": "constraint", "signal": "Appeals must be filed within 14 days of the rejection", "why": "not stated", "source": "Dana Client 2026-09-12"},
        {"type": "pain-point", "signal": "Reviewers cannot see an applicant's previous grants", "source": "Dana Client 2026-09-12"},
        {"type": "requirement", "signal": "Reviewers see the applicant's previous grants when reviewing", "why": "derived from #2", "source": "Dana Client 2026-09-12"}]})
    code, out = run(root, "note", "write-signals", sig)
    assert code == 0 and '"added": [1, 2, 3]' in out, out
    code, out = run(root, "note", "write-signals", sig)
    assert '"added": []' in out and '"skipped_duplicates": 3' in out, out  # re-run is a reported no-op
    p = os.path.join(root, "00-Inbox/INT-003.md")
    _rw(p, lambda s: s.replace("declared_features: []", "declared_features: [grant-intake, applicant-history]"))
    fil = write_json(root, "fil.json", {"kind": "filing", "int": "INT-003",
        "new_features": [{"slug": "applicant-history", "name": "Applicant history", "scope": "reviewers see past grants"}],
        "rows": [{"n": 1, "feature": "grant-intake", "status": "new"}, {"n": 2, "feature": "applicant-history", "status": "new"},
                 {"n": 3, "feature": "applicant-history", "status": "question"}],
        "hub_rows": [{"hub": "grant-intake", "signal": "Appeals must be filed within 14 days of the rejection", "type": "constraint", "note_rows": [1], "status": "new"},
                     {"hub": "applicant-history", "signal": "Reviewers cannot see an applicant's previous grants", "type": "pain-point", "note_rows": [2], "status": "new"},
                     {"hub": "applicant-history", "signal": "Reviewers see the applicant's previous grants when reviewing", "type": "requirement", "note_rows": [3], "status": "question"}],
        "pain_points": [{"statement": "Reviewers cannot see an applicant's previous grants", "feature": "applicant-history", "n": 2}],
        "questions": [{"where": "note", "text": "Row #3 is inferred from the pain point — do reviewers actually need past grants on screen?", "owner": "client"}]})
    code, out = run(root, "file", "apply", fil)
    assert code == 0, out
    note = read(root, "00-Inbox/INT-003.md")
    assert "status: needs-clarification" in note and "| grant-intake | new |" in note and "PP-002" in note
    hub = read(root, "01-Requirements/_features/applicant-history.md")
    assert "INT-003 #2 — Dana Client 2026-09-12" in hub and "PP-002" in hub
    assert re.search(r"^\| 1 \| Reviewers cannot see.*\| PP-002 \|$", hub, re.M), "minted PP not cited on the hub row"
    assert "| applicant-history | Applicant history | proposed |" in read(root, "01-Requirements/FEATURES.md")
    assert re.search(r"^\| 6 \| Appeals must be filed", read(root, "01-Requirements/_features/grant-intake.md"), re.M)
    lint_clean(root)


def test_engine_legacy_hatch():
    root, _ = fresh("comm-vault")
    pj = os.path.join(root, "_bigin/system/project.md")
    _rw(pj, lambda s: s.replace("workspace_version:", "engine: legacy\nworkspace_version:"))
    code, out = apply(root, [cs(1, target={"kind": "UC", "id": "UC-002"}, op="add_question", text="x?")])
    assert code == 2 and "engine: legacy" in out
    assert run(root, "hub", "refresh", "--all")[0] == 0


def test_conflict_principle_and_orphan_answer():
    root, _ = fresh("comm-vault")
    p = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-001"))
    _rw(p, lambda s: re.sub(r"- \[ \] Q: Is there a maximum amount(.*)\n  A:", r"- [x] Q: Is there a maximum amount\1\n  A: $20,000", s))
    code, out = apply(root, [
        cs(1, trace={"int": "INT-002", "hub": "payments", "hub_rows": ["4"]}, target={"kind": "HUB", "id": "payments"},
           op="flag_conflict", text="Row #4 says bank details are confirmed before payment; row #1 says payment is automatic. Which holds?"),
        cs(2, target={"kind": "DESIGN", "id": "principles", "field": "tone"}, op="add_principle", text="Plain language on every screen"),
        cs(3, target={"kind": "UC", "id": "UC-001"}, op="answer_question", anchor={"ref": "Is there a maximum amount"}, text="(from A:)"),
    ])
    assert "3 applied" in out, out
    assert re.search(r"^\| 4 \|.*\| conflict \|", read(root, "01-Requirements/_features/payments.md"), re.M)
    assert "Plain language on every screen" in read(root, "01-Requirements/DESIGN-PRINCIPLES.md")
    assert "$20,000" in uc_text(root, "UC-001").split("**Decision log**")[1]
