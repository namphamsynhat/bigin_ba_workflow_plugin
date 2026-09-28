"""Tests for coverage classification (G6: staged-gated rows parked vs missing)."""
import json
import os

from helpers import fresh, run


def test_staged_gated_row_is_parked_and_ungated_staged_is_missing():
    root, v = fresh("comm-vault")
    # In comm-vault:
    # payments row #3 is staged -> BR-005, citing INT-002 #4.
    # Without a ledger entry, INT-002 #4 is reported as missing.
    code, out = run(root, "coverage", "--stage", "transform")
    assert "INT-002 #4" in out
    assert code == 1

    # Add an open, gated ledger change set for payments hub row #3
    ledger_dir = os.path.join(root, "01-Requirements", "_ledger")
    os.makedirs(ledger_dir, exist_ok=True)
    entry = {
        "id": "cs-test-payments-r3",
        "state": "open",
        "artifact": "BR-005",
        "question": "Is finance sign-off required for payments exceeding $10,000?",
        "changeset": {
            "id": "cs-test-payments-r3",
            "trace": {"hub": "payments", "hub_rows": ["3"]},
            "gate": {"question": "Is finance sign-off required for payments exceeding $10,000?", "blocks": True},
        },
    }
    with open(os.path.join(ledger_dir, "payments.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    # Re-run coverage: INT-002 #4 should now be PARKED, not missing!
    code, out = run(root, "coverage", "--stage", "transform")
    assert "INT-002 #4" not in out

    # Now add another staged row with NO ledger entry to payments hub
    hub_path = v.hub_path("payments")
    with open(hub_path, encoding="utf-8") as f:
        text = f.read()
    new_row = "| 5 | An ungated staged rule | constraint | INT-002 #7 | staged | BR-005 | |\n"
    note_path = os.path.join(root, "00-Inbox", "INT-002.md")
    with open(note_path, encoding="utf-8") as f:
        ntext = f.read()
    note_row = "| 7 | constraint | An ungated staged rule | audit | [00:15] | payments | new | |\n"
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(ntext.replace("## Open Questions", note_row + "\n## Open Questions"))
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(text.replace("## Use Cases", new_row + "\n## Use Cases"))

    # INT-002 #7 is staged with no ledger entry, so it MUST be missing
    code, out = run(root, "coverage", "--stage", "transform")
    assert "INT-002 #7" in out
    assert "INT-002 #4" not in out


def test_project_id_pattern_yaml_escapes_are_decoded():
    # project.md stores coverage_id_pattern as a YAML double-quoted string ("XR-[A-Z]+-\\d{3}");
    # the engine must decode "\\" → "\" or id mode matches nothing.
    root, v = fresh("code-vault")
    code, out = run(root, "coverage", "--stage", "file")
    assert "ids: 12" in out, out


def test_frontmatter_backslash_round_trips():
    import sys
    from helpers import ROOT
    sys.path.insert(0, os.path.join(ROOT, "lib"))
    from bigin.vault import Doc
    d = Doc('---\nid: X\ntitle: "a"\n---\n\nbody\n', "/tmp/x.md")
    d.fm_set("title", 'C:\\path "q"')
    d2 = Doc(d.text, "/tmp/x.md")
    assert d2.fm_get("title") == 'C:\\path "q"', d2.fm_get("title")


def test_null_gate_in_ledger_does_not_crash_coverage():
    root, v = fresh("comm-vault")
    ledger_dir = os.path.join(root, "01-Requirements", "_ledger")
    os.makedirs(ledger_dir, exist_ok=True)
    entry = {"id": "cs-null-gate", "state": "open", "artifact": "BR-005", "question": "",
             "changeset": {"id": "cs-null-gate", "trace": {"hub": "payments", "hub_rows": ["3"]}, "gate": None}}
    with open(os.path.join(ledger_dir, "payments.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    code, out = run(root, "coverage", "--stage", "transform")
    assert "Traceback" not in out, out
    assert "INT-002 #4" in out, out
