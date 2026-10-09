"""Story handoff carries the trace: sources / jira derived from the slices, delta stories, the CR epic."""
import json
import os
import re

from helpers import find, read, run, write_json

from bigin.vault import Doc

import test_stories as ts


def _vault():
    root, v = ts._vault()
    ts._w(root, "_bigin/templates/epic.md", ts.EPIC_TPL)
    ts._w(root, "_bigin/templates/user-story.md", ts.STORY_TPL)
    p = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-005"))
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("brs: [BR-005]", "brs: [BR-005]\nsources: [INT-002]", 1))
    p = os.path.join(root, "00-Inbox", "INT-002.md")
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("\nsource:", "\njira_key: ACME-200\nsource:", 1))
    return root


def _mint(root, kind, spec):
    p = write_json(root, f"{kind}-{abs(hash(json.dumps(spec))) % 10**6}.json", spec)
    return run(root, "mint", kind, "--spec", p)


def test_new_story_traces_to_its_intake_and_jira_key():
    root = _vault()
    code, out = _mint(root, "us", {"title": "See the payee before release", "epic": "EP-001", "slice_of": "UC-005 S1-S2"})
    assert code == 0, out
    sid = re.search(r"US-\d+", out).group(0)
    d = Doc(read(root, find(root, ts.EPIC_DIR, sid)))
    assert d.fm_list("sources") == ["INT-002"] and d.fm_list("jira") == ["ACME-200"]


def test_cascade_backfills_the_trace_on_existing_stories_and_lint_agrees():
    root = _vault()
    code, out = run(root, "lint", "--full")
    assert "story trace out of date" in out, "US-001 slices UC-005, which now traces to INT-002 / ACME-200"
    code, out = run(root, "cascade")
    assert "trace (sources / jira) refreshed" in out, out
    d = Doc(read(root, os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md")))
    assert d.fm_list("jira") == ["ACME-200"] and d.fm_list("sources") == ["INT-002"]
    code, out = run(root, "lint", "--full")
    assert "story trace out of date" not in out, out


def test_delta_story_leaves_the_approved_one_untouched():
    root = _vault()
    rel = os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md")
    p = os.path.join(root, rel)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("status: draft", "status: approved", 1))
    before = Doc(read(root, rel))
    code, out = _mint(root, "us", {"title": "Second approver on release", "epic": "EP-001",
                                   "slice_of": "UC-005 S3", "delta_of": "US-001"})
    assert code == 0, out
    sid = re.search(r"US-\d+", out).group(0)
    new = Doc(read(root, find(root, ts.EPIC_DIR, sid)))
    assert new.fm_get("delta_of") == "US-001"
    old = Doc(read(root, rel))
    assert old.fm_list("delta") == [sid] and old.fm_get("status") == "approved"
    assert old.get("1. Story") == before.get("1. Story"), "the handed-off story's content is never rewritten"


def test_one_change_request_epic_per_feature():
    root = _vault()
    code, out = _mint(root, "ep", {"title": "Payments", "feature": "payments", "cr": True})
    assert code == 0 and "EP-002" in out, out
    ep = Doc(read(root, os.path.join("03-Epics-Stories", "EP-002 Payments — changes", "EP-002 Payments — changes.md")))
    assert str(ep.fm_get("cr")).lower() == "true"
    code, out = _mint(root, "ep", {"title": "Payments", "feature": "payments", "cr": True})
    assert code != 0 and "already has a change-request epic" in out, out
    code, out = _mint(root, "ep", {"title": "Payments", "feature": "payments"})
    assert code != 0 and "already has an epic" in out, out
