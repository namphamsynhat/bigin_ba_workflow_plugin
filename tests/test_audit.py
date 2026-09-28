"""Tests for `bigin audit` (port of audit_phase0.py)."""
import os
import re
import tarfile
import tempfile

from helpers import fresh, run


def _make_baseline(root):
    """Create a baseline tar.gz of 01-Requirements."""
    tgz_path = tempfile.mktemp(suffix=".tgz", prefix="audit-base-")
    with tarfile.open(tgz_path, "w:gz") as t:
        req = os.path.join(root, "01-Requirements")
        t.add(req, arcname="01-Requirements")
    return tgz_path


def test_audit_passes_on_clean_fixture():
    root, v = fresh("code-vault")
    baseline = _make_baseline(root)
    try:
        code, out = run(root, "audit", "--baseline", baseline)
        assert code == 0, out
        assert "PASS  C1 lint" in out
        assert "PASS  C2 staged" in out
        assert "PASS  C3 coverage" in out
        assert "PASS  C4 questions (hubs)" in out
        assert "PASS  C5 steps" in out
        assert "PASS  C6 structure" in out
    finally:
        if os.path.exists(baseline):
            os.remove(baseline)


def test_audit_fails_when_hub_question_deleted():
    root, v = fresh("code-vault")
    hub_path = os.path.join(root, "01-Requirements", "_features", "rates.md")
    # Add a question to the hub first so baseline includes it
    with open(hub_path, encoding="utf-8") as f:
        text = f.read()
    question_line = "\n- [ ] Q: Is this rate valid across all postal zones?\n  A: Pending verification.\n"
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(text.replace("## Open Questions / Gates", "## Open Questions / Gates" + question_line))

    baseline = _make_baseline(root)
    try:
        # Now remove the question from the live vault
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(text)

        code, out = run(root, "audit", "--baseline", baseline)
        assert code == 1, out
        assert "FAIL  C4 questions (hubs)" in out
        assert "hub question(s) vanished" in out
    finally:
        if os.path.exists(baseline):
            os.remove(baseline)


def test_audit_fails_when_step_renumbered_or_lost():
    root, v = fresh("code-vault")
    baseline = _make_baseline(root)
    try:
        # Modify a UC to lose a step ID
        uc_files = [p for p in os.listdir(os.path.join(root, "01-Requirements", "_ucs")) if p.endswith(".md")]
        assert uc_files
        uc_path = os.path.join(root, "01-Requirements", "_ucs", uc_files[0])
        with open(uc_path, encoding="utf-8") as f:
            text = f.read()
        assert "**S1**" in text
        new_text = text.replace("**S1**", "**S99**")
        with open(uc_path, "w", encoding="utf-8") as f:
            f.write(new_text)

        code, out = run(root, "audit", "--baseline", baseline)
        assert code == 1, out
        assert "FAIL  C5 steps" in out
        assert "lost a step/flow id" in out
    finally:
        if os.path.exists(baseline):
            os.remove(baseline)


def test_audit_fails_when_changelog_dropped():
    root, v = fresh("code-vault")
    baseline = _make_baseline(root)
    try:
        # Remove ## Changelog section from a UC
        uc_files = [p for p in os.listdir(os.path.join(root, "01-Requirements", "_ucs")) if p.endswith(".md")]
        assert uc_files
        uc_path = os.path.join(root, "01-Requirements", "_ucs", uc_files[0])
        with open(uc_path, encoding="utf-8") as f:
            text = f.read()
        assert "## Changelog" in text
        new_text = text.replace("## Changelog", "## OldLog")
        with open(uc_path, "w", encoding="utf-8") as f:
            f.write(new_text)

        code, out = run(root, "audit", "--baseline", baseline)
        assert code == 1, out
        assert "FAIL  C6 structure" in out
        assert "structurally broken file(s)" in out
    finally:
        if os.path.exists(baseline):
            os.remove(baseline)


def test_audit_c12_partials():
    root, v = fresh("code-vault")
    baseline = _make_baseline(root)
    hub_path = os.path.join(root, "01-Requirements", "_features", "rates.md")
    with open(hub_path, encoding="utf-8") as f:
        orig = f.read()

    try:
        # Unticked question with filled A: and no fold marker -> WARN C12
        partial_q = "\n- [ ] Q: Does the rate calculation cap at 500?\n  A: Code fact: calculation caps at 500.\n"
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(orig.replace("## Open Questions / Gates", "## Open Questions / Gates" + partial_q))

        code, out = run(root, "audit", "--baseline", baseline)
        assert "WARN  C12 partials" in out
        assert "1 unticked question(s) with an unfolded partial answer" in out

        # Now add Folded (as-built half): marker -> PASS C12
        folded_q = "\n- [ ] Q: Does the rate calculation cap at 500?\n  A: Code fact: calculation caps at 500.\n  Folded (as-built half): cs-test-123\n"
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(orig.replace("## Open Questions / Gates", "## Open Questions / Gates" + folded_q))

        code, out = run(root, "audit", "--baseline", baseline)
        assert "PASS  C12 partials" in out
        assert "partial answer(s) verified" in out

        # Alternatively not settleable marker -> PASS C12
        settle_q = "\n- [ ] Q: Does the rate calculation cap at 500?\n  A: not settleable from code.\n"
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(orig.replace("## Open Questions / Gates", "## Open Questions / Gates" + settle_q))

        code, out = run(root, "audit", "--baseline", baseline)
        assert "PASS  C12 partials" in out
        assert "partial answer(s) verified" in out
    finally:
        if os.path.exists(baseline):
            os.remove(baseline)
