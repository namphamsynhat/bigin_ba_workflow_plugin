"""Tests for Phase 0 failure-mode guards (Item C2):
(a) any command touching ## Open Questions / Gates must refuse if a question line disappears;
(b) vault.py write must refuse if a ## Changelog heading or history line disappears;
(c) lint --full prints plugin version and path.
"""
import os
import re

from helpers import fresh, run
from bigin import __version__
from bigin.util import EngineError
from bigin.vault import Doc


def test_vault_write_refuses_when_changelog_heading_lost():
    root, v = fresh("code-vault")
    uc_path = v.uc_paths()[0]
    doc = v.load(uc_path)
    cl = doc.section("Changelog")
    assert cl is not None
    # Rename heading line directly
    doc.splice(cl.h, cl.h + 1, ["## History"])
    doc.allow_heading_change = True  # bypass generic heading check to test specific Changelog guard
    try:
        v.write(doc)
        raise AssertionError("write accepted lost Changelog heading")
    except EngineError as e:
        assert "## Changelog heading lost" in str(e)


def test_vault_write_refuses_when_changelog_history_line_lost():
    root, v = fresh("code-vault")
    uc_path = v.uc_paths()[0]
    doc = v.load(uc_path)
    cl = doc.section("Changelog")
    assert cl is not None
    # Find a history line
    idx = -1
    for i in range(cl.start, cl.end):
        if doc.lines[i].strip().startswith("- "):
            idx = i
            break
    assert idx != -1, "fixture UC has at least one changelog line"
    target_line = doc.lines[idx]
    # Drop that history line
    doc.splice(idx, idx + 1, [])
    try:
        v.write(doc)
        raise AssertionError("write accepted lost Changelog history line")
    except EngineError as e:
        assert "## Changelog history line lost" in str(e)


def test_vault_write_refuses_when_open_questions_gates_question_lost():
    root, v = fresh("code-vault")
    hub_path = v.hub_paths()[0]
    doc = v.load(hub_path)
    gates = doc.section("Open Questions / Gates")
    assert gates is not None
    # Add a question first
    q_lines = ["- [ ] Q: Original question text for testing guard?", "  A: Pending."]
    doc.splice(gates.start, gates.start, q_lines)
    v.write(doc)

    # Now reload and delete that question
    doc2 = v.load(hub_path)
    gates2 = doc2.section("Open Questions / Gates")
    # Drop all lines in the section
    doc2.replace_body("Open Questions / Gates", [""])
    try:
        v.write(doc2)
        raise AssertionError("write accepted lost Open Questions / Gates question")
    except EngineError as e:
        assert "question in ## Open Questions / Gates disappeared" in str(e)


def test_lint_full_prints_version_and_plugin_path():
    root, v = fresh("code-vault")
    code, out = run(root, "lint", "--full")
    assert code == 0, out
    assert f"bigin-lint v{__version__}" in out
    plugin_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert plugin_path in out
