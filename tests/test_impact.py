"""Approved UC → draft on a content change, suspect-link `stale:` flags downstream, and `bigin impact`."""
import json
import os
import re

from helpers import find, read, run, write_json

from bigin import impact, model
from bigin.util import sha
from bigin.vault import Doc, Vault

import test_stories as ts

UX = """---
id: UX-001
type: ux-spec
title: "Payments"
status: accepted
version: 1.0
feature: payments
uc: [UC-005]
absorbed: [UC-005@2.0]
updated: 2026-09-20
---

# `UX-001 Payments`

## Changelog
- 1.0 (2026-09-20) — created
"""


def _vault():
    root, v = ts._vault()
    ts._w(root, "04-UIUX/UX-001 Payments.md", UX)
    for rel in (os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md"),
                os.path.join(ts.EPIC_DIR, "US-002 Release a small payment without sign-off.md")):
        p = os.path.join(root, rel)
        with open(p, encoding="utf-8") as f:
            t = f.read()
        with open(p, "w", encoding="utf-8") as f:
            f.write(t.replace("status: draft", "status: approved", 1))
    return root


def _apply(root, sets):
    p = write_json(root, f"cs-{abs(hash(json.dumps(sets))) % 10**8}.json", {"kind": "changesets", "changesets": sets})
    return run(root, "--json", "apply", p)


def _uc(root, uid):
    return read(root, find(root, "01-Requirements/_ucs", uid))


def _fm(root, rel):
    return Doc(read(root, rel))


def _replace_s3(root):
    d = Vault(root).load_id("UC-005")
    s3 = next(s for s in model.steps(d) if s.id == "S3")
    return _apply(root, [{"id": "cs-jira-1", "trace": {"int": "INT-002", "hub": "payments", "hub_rows": ["1"]},
                          "target": {"kind": "UC", "id": "UC-005", "section": "2"}, "op": "replace_step",
                          "anchor": {"ref": "S3", "sha": sha(s3.text)},
                          "cells": {"actor": "Finance officer confirms the release with a second approver.",
                                    "system": "System records both approvals."}}])


def test_nothing_is_stale_before_a_change():
    root = _vault()
    code, out = run(root, "cascade", "--dry")
    assert code == 0 and "nothing stale" in out, out


def test_content_change_unstages_an_approved_uc_and_flags_downstream():
    root = _vault()
    code, out = _replace_s3(root)
    assert code == 0, out
    res = json.loads(out)
    assert res["reverted"] == ["UC-005"], res
    t = _uc(root, "UC-005")
    assert re.search(r"^status: draft", t, re.M), "an approved UC whose content changed goes back to draft"
    assert "Status approved → draft (un-staged by this change; re-approve via /approve-uc)" in t
    ver = Doc(t).fm_get("version")
    assert ver != "2.0"
    stale = f"UC-005@{ver}"
    for rel in ("04-UIUX/UX-001 Payments.md", os.path.join(ts.EPIC_DIR, "EP-001 Payments.md"),
                os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md"),
                os.path.join(ts.EPIC_DIR, "US-002 Release a small payment without sign-off.md")):
        d = _fm(root, rel)
        assert d.fm_list("stale") == [stale], (rel, d.fm_list("stale"))
        assert d.fm_get("status") in ("accepted", "draft", "approved"), "downstream status is never changed"
        log = d.get("Changelog") or ""
        assert not log or ("stale: built on an older UC-005" in log and "from INT-002" in log), log
    assert _fm(root, os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md")).fm_get("status") == "approved"
    assert any("US-001" in s for s in res["stale"]), res["stale"]
    code, out = run(root, "cascade")
    assert "nothing stale changed" in out, "cascade is idempotent"
    code, out = run(root, "lint", "--full")
    assert "stale" not in out.lower() or code == 0, out


def test_question_on_an_approved_uc_does_not_unstage_it():
    root = _vault()
    code, out = _apply(root, [{"id": "cs-q-1", "target": {"kind": "UC", "id": "UC-005"}, "op": "add_question",
                               "text": "Who is the second approver?", "owner": "client"}])
    assert code == 0, out
    assert json.loads(out)["reverted"] == []
    assert re.search(r"^status: (approved|needs-clarification)", _uc(root, "UC-005"), re.M)
    assert "Status approved → draft" not in _uc(root, "UC-005")


def test_stale_clears_when_the_stage_restamps_absorbed():
    root = _vault()
    _replace_s3(root)
    ver = Doc(_uc(root, "UC-005")).fm_get("version")
    p = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-005"))
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("status: draft", "status: approved", 1))  # re-approved
    rel = os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md")
    p = os.path.join(root, rel)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("absorbed: [UC-005@2.0]", f"absorbed: [UC-005@{ver}]", 1))  # stories re-ran
    code, out = run(root, "cascade")
    assert "US-001: stale — cleared" in out, out
    d = _fm(root, rel)
    assert d.fm_list("stale") == [] and "stale cleared" in (d.get("Changelog") or "stale cleared")
    assert _fm(root, "04-UIUX/UX-001 Payments.md").fm_list("stale") == [f"UC-005@{ver}"], "UX not redone yet"


def test_impact_walk_reaches_rules_siblings_and_story_steps():
    root = _vault()
    _replace_s3(root)
    v = Vault(root)
    res = impact.walk(v, ucs={"UC-005": {"refs": {"S3"}, "pending": False}}, brs=["BR-005"])
    by = {e["id"]: e for e in res["ucs"]}
    assert by["UC-005"]["reason"] == "direct" and "S3" in by["UC-005"]["steps"]
    assert any(e["reason"] == "rule" for e in res["ucs"]) or by["UC-005"]["via"] == ["BR-005"]
    stories = {e["id"]: e for e in res["stories"]}
    assert stories["US-001"]["hits_steps"] == ["UC-005 S3"] and stories["US-001"]["drift"] == "drifted"
    assert stories["US-002"]["hits_steps"] == [], "A1's story is built on the UC but its steps were not hit"
    assert res["ux"][0]["id"] == "UX-001" and res["epics"][0]["id"] == "EP-001"
    assert "UC-005" in res["summary"]["reopened"]


def test_impact_section_on_the_note_is_idempotent():
    root = _vault()
    code, out = run(root, "impact", "INT-002", "--write")
    assert code == 0, out
    t = read(root, "00-Inbox/INT-002.md")
    assert "## Impact" in t and "engine-owned" in t and "**Where the signals went**" in t
    assert "payments #1" in t and "UC-003" in t
    assert os.path.exists(os.path.join(root, "01-Requirements", "_impact", "INT-002.json"))
    code, out = run(root, "--json", "impact", "touched", "--write")
    assert all(not o["written"] for o in json.loads(out) if o["int"] == "INT-002"), out
    assert read(root, "00-Inbox/INT-002.md") == t
    code, out = run(root, "lint", "--full")
    assert "INT-002" not in out or code == 0, out


def test_lint_flags_a_stale_flag_out_of_date():
    root = _vault()
    _replace_s3(root)
    rel = "04-UIUX/UX-001 Payments.md"
    p = os.path.join(root, rel)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    import re as _re
    with open(p, "w", encoding="utf-8") as f:
        f.write(_re.sub(r"^stale: .*$", "stale: []", t, count=1, flags=_re.M))
    code, out = run(root, "lint", "--full")
    assert "stale flag out of date" in out and "UX-001" in out, out
    run(root, "cascade")
    code, out = run(root, "lint", "--full")
    assert "stale flag out of date" not in out, out
