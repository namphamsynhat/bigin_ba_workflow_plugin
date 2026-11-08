"""Before / After on the intake note: what one ticket changed in each UC, kept on the note, not the UC."""
import json
import os

from helpers import read, run

from bigin import model
from bigin.util import sha
from bigin.vault import Doc, Vault

import test_impact as ti


def _s3(root):
    d = Vault(root).load_id("UC-005")
    return next(s for s in model.steps(d) if s.id == "S3")


def _replace(root, cid, nid, actor):
    s3 = _s3(root)
    return ti._apply(root, [{"id": cid, "trace": {"int": nid, "hub": "payments", "hub_rows": ["1"]},
                             "target": {"kind": "UC", "id": "UC-005", "section": "2"}, "op": "replace_step",
                             "anchor": {"ref": "S3", "sha": sha(s3.text)},
                             "cells": {"actor": actor, "system": "System records it."}}])


def _note(root, nid):
    return read(root, f"00-Inbox/{nid}.md")


def test_ticket_note_gets_before_after_of_the_uc_it_changed():
    root = ti._vault()
    before_s3 = _s3(root).text
    code, out = _replace(root, "cs-t1", "INT-002", "Finance officer confirms with a second approver.")
    assert code == 0, out
    assert json.loads(out)["before_after"] == ["INT-002"]
    t = _note(root, "INT-002")
    assert "## Before / After" in t and "### UC-005" in t and "v2.0 →" in t, t[-1500:]
    assert "[[_snapshots/INT-002/UC-005.before.md|UC-005 before]]" in t
    assert "replace_step S3 (cs-t1)" in t and "second approver" in t
    snap = os.path.join(root, "00-Inbox", "_snapshots", "INT-002")
    before = open(os.path.join(snap, "UC-005.before.md"), encoding="utf-8").read()
    after = open(os.path.join(snap, "UC-005.after.md"), encoding="utf-8").read()
    assert "second approver" not in before and "second approver" in after
    assert Doc(before).fm_get("version") == "2.0"
    assert before_s3.split("||")[0].strip()[:20] in before


def test_before_stays_at_first_touch_and_other_tickets_stay_out_of_the_table():
    root = ti._vault()
    _replace(root, "cs-t1", "INT-002", "Finance officer confirms with a second approver.")
    _replace(root, "cs-o1", "INT-001", "Finance lead confirms the release.")       # another ticket
    _replace(root, "cs-t2", "INT-002", "Finance officer and a deputy both confirm.")
    snap = os.path.join(root, "00-Inbox", "_snapshots", "INT-002")
    before = open(os.path.join(snap, "UC-005.before.md"), encoding="utf-8").read()
    assert Doc(before).fm_get("version") == "2.0", "before = the UC before this ticket's FIRST change"
    t = _note(root, "INT-002")
    assert "(cs-t1)" in t and "(cs-t2)" in t and "(cs-o1)" not in t
    assert "Finance lead confirms" in t, "the second change's Before shows what it replaced"
    log = json.load(open(os.path.join(snap, "changes.json"), encoding="utf-8"))
    assert [c["cs"] for c in log["UC-005"]["changes"]] == ["cs-t1", "cs-t2"]
    assert "(cs-o1)" in _note(root, "INT-001") and "(cs-t1)" not in _note(root, "INT-001")


def test_reapplying_adds_nothing_and_the_section_is_regenerated_once():
    root = ti._vault()
    _replace(root, "cs-t1", "INT-002", "Finance officer confirms with a second approver.")
    t1 = _note(root, "INT-002")
    s3 = _s3(root)
    code, out = ti._apply(root, [{"id": "cs-t1", "trace": {"int": "INT-002", "hub": "payments", "hub_rows": ["1"]},
                                  "target": {"kind": "UC", "id": "UC-005", "section": "2"}, "op": "replace_step",
                                  "anchor": {"ref": "S3", "sha": sha(s3.text)},
                                  "cells": {"actor": "x", "system": "y"}}])
    assert code == 0, out
    t2 = _note(root, "INT-002")
    assert t2.count("## Before / After") == 1 and t2.count("(cs-t1)") == 1 and t1 == t2


def test_lint_is_clean_after_before_after():
    root = ti._vault()
    _replace(root, "cs-t1", "INT-002", "Finance officer confirms with a second approver.")
    code, out = run(root, "lint", "--full")
    assert code == 0 and "clean" in out, out
