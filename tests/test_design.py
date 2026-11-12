"""The design stage's lookups (lib/bigin/design.py): scope, the worker's worklist, forward items,
the mechanical checks, and close — all against a spec on disk, never a worker's report."""
import json
import os

from helpers import fresh, read, run

SPEC_REL = os.path.join("04-UIUX", "UX-001 Payments.md")
HUB = os.path.join("01-Requirements", "_features", "payments.md")

SPEC = """---
id: UX-001
type: uiux
title: "Payments screens"
status: draft
version: 1.0
feature: payments
features: [payments]
platform: web
uc: [UC-003]
actors: ["Finance officer:all:few"]
absorbed: []
nav_map:
relationship_model: none
updated: 2026-09-20
---

# `UX-001 Payments` screens

## 1. Design Brief

* **Users:** Finance officer (UC-003 § 1)
* **Platform:** web. Dispatched from the project config.

**Actor & Scope**

| Actor | Sees whose records | How many | May act on | Grounded by |
|-------|--------------------|----------|------------|-------------|
| Finance officer | all approved grants | few | act on one | UC-003 S1 |

## 2. Screen Inventory

| Screen | View ID | Screen Type | Actor | Volume | Purpose | Serves | Entities | Key actions |
|--------|---------|-------------|-------|--------|---------|--------|----------|-------------|
| Payments queue | payments-payments-queue | Primary | Finance officer | few | Pay approved grants | UC-003 S1, S2 (release) | — | Release |

## 3. Screen Specs

### `Payments queue`

* **View ID:** `payments-payments-queue`
* **Screen Type:** `Primary`
* **Serves:** `UC-003 S1, S2`
* **Actor:** Finance officer
* **Regions:** `header · main`

| Element | Content / copy | Role | Field | Visible to | Grounded by |
|---------|----------------|------|-------|------------|-------------|
| Release | "Release payment" | primary action | | | UC-003 S2; BR-004 |
| Status | "Sent" / "Waiting" | success (sent) · muted (waiting) | | | UC-003 S2 |

## 4. Flows

### `UC-003 Pay an approved grant`
* **Actor:** Finance officer
* **Path:** `Payments queue`
* **Resolves:** —

## 5. Navigation & Flow Review

### Flow Review

| Flow | Actor | Steps to goal | Resolves | Verdict |
| :--- | :--- | :--- | :--- | :--- |

## 6. Open Questions

- [ ] Q1: Which bank holidays delay a transfer? (owner: client)
      A:

## Changelog
- 1.0 (2026-09-20) — created
"""


def _vault():
    root, v = fresh("comm-vault")
    os.makedirs(os.path.join(root, "04-UIUX"))
    with open(os.path.join(root, SPEC_REL), "w", encoding="utf-8") as f:
        f.write(SPEC)
    return root, v


def _j(root, *args):
    code, out = run(root, "--json", *args)
    return code, json.loads(out)


def _edit(root, old, new):
    p = os.path.join(root, SPEC_REL)
    t = read(root, SPEC_REL)
    assert old in t, old
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace(old, new))


def test_scope_reads_new_drafted_changed_current_from_files():
    root, _ = fresh("comm-vault")
    _, res = _j(root, "design", "scope", "payments")
    f = res["features"][0]
    states = {u["id"]: u for u in f["ucs"]}
    assert states["UC-003"]["state"] == "NEW" and f["ux"] is None and res["new_ids_needed"] == 1
    assert states["UC-001"]["state"] == "SKIP" and states["UC-001"]["owner"] == "grant-intake"
    assert res["platform"] == "web" and res["platform_source"] == "stated" and res["mode"] == "bootstrap"
    # screens on disk for a UC nobody stamped = a run that died before close: resume, do not redesign
    root, _ = _vault()
    _, res = _j(root, "design", "scope", "payments")
    f = res["features"][0]
    assert {u["id"]: u["state"] for u in f["ucs"]}["UC-003"] == "DRAFTED"
    _edit(root, "absorbed: []", "absorbed: [UC-003@0.9]")
    _, res = _j(root, "design", "scope", "payments")
    u = {u["id"]: u for u in res["features"][0]["ucs"]}["UC-003"]
    assert u["state"] == "CHANGED" and u["from"] == "0.9"
    _edit(root, "absorbed: [UC-003@0.9]", "absorbed: [UC-003@1.0]")
    _, res = _j(root, "design", "scope", "payments")
    assert {u["id"]: u["state"] for u in res["features"][0]["ucs"]}["UC-003"] == "CURRENT"


def test_design_worklist_carries_the_requirement_input():
    root, _ = _vault()
    code, out = run(root, "worklist", "design", "payments")
    wl = json.loads(out)
    assert code == 0 and wl["stage"] == "design"
    uc = {u["id"]: u for u in wl["use_cases"]}["UC-003"]
    assert [s["id"] for s in uc["steps"]][:2] == ["S1", "S2"] and uc["summary"]["Primary Actor"] == "Finance officer"
    assert "BR-004" in {r["id"] for r in wl["rules"]}
    assert any("NOT YOURS" in o["note"] for o in wl["other_use_cases"])
    assert wl["ux"]["screens"][0]["View ID"] == "payments-payments-queue"


def test_items_match_forward_by_id_only():
    root, _ = _vault()
    _, res = _j(root, "design", "items", "payments")
    by = {i["item"]: i for i in res["items"]}
    assert by["UC-003 S1"]["covered_by"] == ["Payments queue"] and by["UC-003 S2"]["covered_by"] == ["Payments queue"]
    assert by["BR-004"]["covered_by"] == ["Payments queue"]     # named in the block
    assert "BR-005" in res["unmatched"]                           # mirrored by the UC, on no screen
    unserved = [i["item"] for i in res["items"] if i["kind"] in ("step", "alternative", "exception") and not i["covered_by"]]
    assert set(unserved) <= set(res["unmatched"]) and res["counts"]["unmatched"] == len(res["unmatched"])


def test_check_finds_what_a_report_would_hide():
    root, _ = _vault()
    code, res = _j(root, "design", "check", "payments", "--phase", "wave")
    assert code == 0 and res["ok"], res["findings"]
    _edit(root, "| Release | \"Release payment\" | primary action |", "| Release | \"Release payment\" | call to action |")
    _edit(root, "UC-003 S1, S2 (release) |", "UC-003 S1, S2, S9 |")
    _edit(root, "\"Sent\" / \"Waiting\"", "\"Sent\" in #1a7f37, 14px")
    _edit(root, "* **Regions:** `header · main`", "* **Regions:** `header · tab-bar`")
    code, res = _j(root, "design", "check", "payments", "--phase", "wave")
    got = {(x["check"], x["level"]) for x in res["findings"]}
    msgs = " | ".join(x["msg"] for x in res["findings"])
    assert code == 2 and not res["ok"]
    assert {(2, "block"), (3, "block"), (4, "block"), (13, "block")} <= got, res["findings"]
    assert "call to action" in msgs and "#1a7f37" in msgs and "14px" in msgs and "tab-bar" in msgs
    assert "UC-003 S9" in " ".join(x["where"] for x in res["findings"])


def test_close_stamps_from_disk_and_is_idempotent():
    root, _ = _vault()
    code, res = _j(root, "design", "close", "payments")
    spec, hub = read(root, SPEC_REL), read(root, HUB)
    assert "absorbed: [UC-003@1.0]" in spec and "status: needs-clarification" in spec   # one open question
    assert "[[UX-001 Payments]] — needs-clarification — 1 screens" in hub and "UX-001" in hub.split("uiux:")[1].split("\n")[0]
    assert "Which bank holidays delay a transfer?" in hub and "(ref: UX-001 § 6 Q1)" in hub
    uc = read(root, os.path.join("01-Requirements", "_ucs", "UC-003 Pay an approved grant.md"))
    assert "**UX-001**" in uc and "no requirement change proposed" in uc
    # the forward check ran BEFORE the stamp made everything CURRENT: no Coverage table → blocking
    assert code == 2 and any(x["check"] == 17 for x in res["findings"])
    assert not any(x["check"] in (1, 5, 6) for x in res["findings"])
    before = {p: read(root, p) for p in (SPEC_REL, HUB)}
    run(root, "design", "close", "payments")
    assert before == {p: read(root, p) for p in (SPEC_REL, HUB)}
    _, sc = _j(root, "design", "scope", "payments")
    assert {u["id"]: u["state"] for u in sc["features"][0]["ucs"]}["UC-003"] == "CURRENT"


def test_close_never_stamps_a_use_case_with_no_screen():
    root, _ = _vault()
    _edit(root, "UC-003 S1, S2 (release) |", "— |")
    _, res = _j(root, "design", "close", "payments")
    assert res["absorbed"] == [] and "UC-003" in res["not_designed"]
    assert "absorbed: []" in read(root, SPEC_REL) and "status: needs-clarification" in read(root, SPEC_REL)


def test_run_record_lets_a_rerun_resume():
    root, _ = _vault()
    _edit(root, "absorbed: []", "absorbed: [UC-003@0.9]")      # CHANGED: nothing on disk says the screens landed
    _, plan = _j(root, "run", "new", "--stage", "design")
    rid = plan["id"]
    _, sc = _j(root, "design", "scope", "payments", "--run", rid)
    assert "resume" not in sc["features"][0]
    run(root, "run", "record", rid, "--task", "screens:payments", "--status", "ok")
    _, sc = _j(root, "design", "scope", "payments", "--run", rid)
    assert sc["features"][0]["resume"] == "review"
    run(root, "design", "close", "payments", "--run", rid)
    _, sc = _j(root, "design", "scope", "payments", "--run", rid)
    assert sc["features"][0]["resume"] == "done" and not sc["features"][0]["in_scope"]
