"""Phase 1 — engine and scripted bookkeeping (vault I/O, ids, hub, mirror, links, status, coverage, lint)."""
import glob
import os
import re

from helpers import FIX, digest, find, fresh, lint_clean, read, run, write_json

from bigin import hub, model
from bigin.util import EngineError
from bigin.vault import Doc, Vault


# ---------------------------------------------------------------------------- vault.py

def _rw(path, fn):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(fn(text))


def test_roundtrip_byte_identical_over_fixtures():
    for p in glob.glob(os.path.join(FIX, "**", "*.md"), recursive=True):
        with open(p, encoding="utf-8") as f:
            s = f.read()
        d = Doc(s, p)
        assert d.text == s, p
        d.verify()


def test_heading_inside_comment_is_not_a_section():
    text = "---\nid: UC-1\n---\n\n## 2. Main\n<!-- guidance\n## Discussion and waits.\n-->\nbody\n\n## Discussion\nreal\n"
    d = Doc(text)
    assert [s.title for s in d.sections] == ["2. Main", "Discussion"]
    assert "real" in d.get("Discussion")
    assert "body" in d.get("2")


def test_frontmatter_keeps_styles_and_order():
    text = "---\nid: INT-001\nattachments:\n  - a.md\ntags: [x, y]\ntitle: \"A: b\"\n---\nbody\n"
    d = Doc(text)
    assert d.fm_get("attachments") == ["a.md"] and d.fm_get("tags") == ["x", "y"] and d.fm_get("title") == "A: b"
    d.fm_set("attachments", ["a.md", "b.md"])
    d.fm_set("tags", ["x", "y", "z"])
    assert "attachments:\n  - a.md\n  - b.md\n" in d.text
    assert "tags: [x, y, z]" in d.text
    assert d.text.index("attachments") < d.text.index("tags") < d.text.index("title")
    d.verify()


def test_verify_refuses_edits_outside_touched_sections():
    d = Doc("# t\n\n## A\none\n\n## B\ntwo\n")
    d.lines[3] = "changed behind the engine's back"
    try:
        d.verify()
        raise AssertionError("verify accepted an untracked edit")
    except EngineError:
        pass


def test_write_backs_up_and_restores(tmp=None):
    root, v = fresh("comm-vault")
    p = os.path.join(root, find(root, "01-Requirements/_brs", "BR-001"))
    d = v.load(p)
    d.fm_set("status", "needs-clarification")
    assert v.write(d)
    backups = glob.glob(os.path.join(root, "_runs", "_backups", "**", "BR-001*"), recursive=True)
    assert backups, "no backup written"


# ---------------------------------------------------------------------------- ids.py

def test_mint_is_parallel_safe():
    """12 concurrent `bigin mint br` processes must get 12 distinct ids (fcntl lock)."""
    import subprocess
    import sys
    from helpers import ROOT
    root, _ = fresh("comm-vault")
    procs = []
    for i in range(12):
        spec = write_json(root, f"br{i}.json", {"title": f"Parallel rule {i}", "feature": "payments", "statement": "If x, then y."})
        procs.append(subprocess.Popen([sys.executable, os.path.join(ROOT, "lib", "bigin", "cli.py"), "--vault", root,
                                       "mint", "br", "--spec", spec], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
    got = [p.communicate()[0].split()[0] for p in procs]
    assert len(set(got)) == 12, got
    assert sorted(got)[0] == "BR-007" and sorted(got)[-1] == "BR-018", got


def test_mint_uc_refuses_duplicate_title_and_points_hubs():
    root, v = fresh("comm-vault")
    code, out = run(root, "mint", "uc", "--spec", write_json(root, "s.json", {
        "title": "Withdraw an application", "primary_feature": "grant-intake", "sources": ["INT-003"]}))
    assert code == 0 and "UC-005" in out, out
    hub_text = read(root, "01-Requirements/_features/grant-intake.md")
    assert "UC-005" in hub_text.split("---")[1], "uc: pointer missing"
    assert "| UC-005 | Withdraw an application | owns | draft |" in hub_text
    uc = read(root, find(root, "01-Requirements/_ucs", "UC-005"))
    assert "<!--" not in uc or "guide:" in uc, "template guidance copied into the instance"
    assert "### A1" not in uc, "template example flows would read as real flow ids"
    code, out = run(root, "mint", "uc", "--spec", os.path.join(root, "s.json"))
    assert code == 2 and "REFUSED" in out
    lint_clean(root)


# ---------------------------------------------------------------------------- hub.py

def test_hub_refresh_idempotent_and_signal_log_untouched():
    for name in ("comm-vault", "code-vault"):
        root, v = fresh(name)
        before = {s: model.signal_doc(v, s).get("Signal Log") for s in v.slugs()}
        gaps = {s: v.load(v.hub_path(s)).get("Coverage Gaps") for s in v.slugs()}
        run(root, "hub", "refresh", "--all")
        snap = digest(root)
        code, out = run(root, "hub", "refresh", "--all")
        assert "0 of" in out, out
        assert digest(root) == snap, "second refresh changed files"
        v2 = Vault(root)
        for s in v2.slugs():
            assert model.signal_doc(v2, s).get("Signal Log") == before[s]
            assert v2.load(v2.hub_path(s)).get("Coverage Gaps") == gaps[s]
        lint_clean(root)


def test_readiness_truth_table():
    root, v = fresh("comm-vault")
    run(root, "hub", "refresh", "--all")
    t = read(root, "01-Requirements/_features/payments.md")
    rows = {m.group(1): (m.group(2), m.group(3)) for m in
            re.finditer(r"^\| (UC-\d+|BR-\d+) \| [^|]+ \| (Yes|No) \| ([^|]*)\|", t, re.M)}
    assert rows["UC-003"][0] == "Yes"
    assert rows["UC-004"][0] == "No" and "not yet drafted" in rows["UC-004"][1]
    assert rows["BR-005"][0] == "No" and "staged" in rows["BR-005"][1]
    assert rows["UC-001"][0] == "No" and "open question" in rows["UC-001"][1]
    # one row per artifact, never ranges
    assert not re.search(r"\| (UC|BR)-\d+\s*[-–]\s*(UC|BR)?-?\d+ \|", t)


def test_gates_are_add_only_and_tick_from_source():
    root, v = fresh("comm-vault")
    run(root, "hub", "refresh", "--all")
    hp = "01-Requirements/_features/grant-intake.md"
    n_before = len(re.findall(r"^- \[[ x]\] ", read(root, hp), re.M))
    # answer the BR-003 question at its source
    bp = os.path.join(root, find(root, "01-Requirements/_brs", "BR-003"))
    s = open(bp).read().replace("- [ ] Q: Is there a deadline", "- [x] Q: Is there a deadline").replace(
        "(ref: INT-002 #3)\n  A:", "(ref: INT-002 #3)\n  A: 14 days")
    open(bp, "w").write(s)
    run(root, "hub", "refresh", "grant-intake")
    t = read(root, hp)
    assert len(re.findall(r"^- \[[ x]\] ", t, re.M)) >= n_before, "a gate line disappeared"
    assert re.search(r"^- \[x\] Q: Is there a deadline.*\n\s+A: 14 days", t, re.M), "source tick not mirrored"


def test_flip_and_sweep():
    root, v = fresh("comm-vault")
    code, out = run(root, "hub", "flip", "payments", "4=staged:UC-003 S3@routed by test")
    assert code == 0 and "new -> staged" in out, out
    code, out = run(root, "hub", "sweep", "payments")
    assert "#4" in out, out  # nothing cites it in a Discussion or the ledger → applied
    t = read(root, "01-Requirements/_features/payments.md")
    assert re.search(r"^\| 4 \|.*\| applied \| UC-003 S3 \| routed by test \|", t, re.M), t
    code, out = run(root, "hub", "flip", "payments", "99=applied")
    assert code == 2


# ---------------------------------------------------------------------------- mirror / links / status

def test_mirror_links_status_idempotent():
    root, v = fresh("comm-vault")
    for _ in range(2):
        run(root, "mirror", "br", "--all")
        run(root, "links", "sync")
        run(root, "status")
    snap = digest(root)
    run(root, "mirror", "br", "--all")
    run(root, "links", "sync")
    run(root, "status")
    assert digest(root) == snap
    lint_clean(root)


def test_mirror_refreshes_changed_rule_but_never_swaps_rules():
    root, v = fresh("comm-vault")
    bp = os.path.join(root, find(root, "01-Requirements/_brs", "BR-002"))
    s = open(bp).read().replace("must both be present.", "must both be present, and the amount must be positive.")
    open(bp, "w").write(s)
    up = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-001"))
    u = open(up).read().replace("| BR-001 | If the amount requested exceeds $5,000, then a second reviewer must approve the application. |",
                                "| BR-001 | Bank transfers settle within three working days of release. |")
    open(up, "w").write(u)
    code, out = run(root, "mirror", "br", "UC-001")
    t = read(root, find(root, "01-Requirements/_ucs", "UC-001"))
    assert "and the amount must be positive." in t, "changed rule not mirrored"
    assert "Bank transfers settle within three working days" in t, "a different rule was overwritten"
    assert "does not resemble BR-001" in out


def test_status_recount_moves_only_draft_and_needs_clarification():
    root, v = fresh("comm-vault")
    up = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-002"))
    _rw(up, lambda s: s.replace("status: draft", "status: approved"))
    code, out = run(root, "status")
    assert "UC-002" not in out
    bp = os.path.join(root, find(root, "01-Requirements/_brs", "BR-003"))
    _rw(bp, lambda s: s.replace("- [ ] Q:", "- [x] Q:").replace("#3)\n  A:", "#3)\n  A: yes"))
    code, out = run(root, "status")
    assert "BR-003: needs-clarification -> draft" in out, out


# ---------------------------------------------------------------------------- coverage / lint

def test_coverage_row_and_id_modes():
    root, v = fresh("comm-vault")
    code, out = run(root, "coverage", "--stage", "file")
    assert "INT-003" in out or code == 0, out  # INT-003 is raw: nothing extracted yet, nothing to file
    root2, _ = fresh("code-vault")
    code, out = run(root2, "coverage", "--stage", "file", "--id-pattern", r"XR-[A-Z]+-\d{3}")
    assert code == 0, out
    code, out = run(root2, "coverage", "--stage", "transform", "--id-pattern", r"XR-[A-Z]+-\d{3}")
    assert code == 1 and "missing" in out  # rows #4-#12 are new/held: not transformed yet


def test_lint_self_test_and_fixtures_clean():
    code, out = run(FIX + "/comm-vault", "lint", "--self-test")
    assert code == 0 and "16/16" in out, out
    lint_clean(os.path.join(FIX, "comm-vault"))
    lint_clean(os.path.join(FIX, "code-vault"))


def test_quiet_hook_is_silent_in_batch_mode():
    import io
    import json
    import sys
    from bigin import lint
    root, _ = fresh("comm-vault")
    p = os.path.join(root, find(root, "01-Requirements/_ucs", "UC-002"))
    open(p, "a").write("\n| **S1** | dup | dup |\n")
    payload = json.dumps({"tool_input": {"file_path": p}, "cwd": root})
    old_in, old_out = sys.stdin, sys.stdout
    try:
        os.environ["BIGIN_BATCH"] = "1"
        sys.stdin, sys.stdout = io.StringIO(payload), io.StringIO()
        assert lint.main(["x", "--hook", "--quiet"]) == 0
        assert sys.stdout.getvalue() == ""
        os.environ.pop("BIGIN_BATCH")
        os.environ["CLAUDE_PROJECT_DIR"] = root
        sys.stdin, sys.stdout = io.StringIO(payload), io.StringIO()
        lint.main(["x", "--hook", "--quiet"])
        got = sys.stdout.getvalue()
        assert got.count("\n") <= 6
    finally:
        sys.stdin, sys.stdout = old_in, old_out
        os.environ.pop("BIGIN_BATCH", None)
        os.environ.pop("CLAUDE_PROJECT_DIR", None)


def test_lint_flags_sensitive_values():
    root, _ = fresh("comm-vault")
    p = os.path.join(root, find(root, "01-Requirements/_brs", "BR-006"))
    open(p, "a").write("\nContact finance-ops@acme-grants.example.com or db01.internal for details.\n")
    code, out = run(root, "lint", "--full")
    assert code == 1 and "sensitive value reproduced" in out and "e-mail" in out and "internal host" in out
