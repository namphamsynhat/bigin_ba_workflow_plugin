"""W5 — Confluence / shared docs as a living note: first capture, no-op on an unchanged version, one block per
edited section, removed sections marked, headings that cannot break the note."""
import json
import os

from helpers import fresh, read, run, write_json

from bigin.intake import confluence

V1 = """Intro paragraph about the grant process.

## Eligibility

Applicants must be registered schools.

## Deadlines

Appeals are filed within 14 days.

# Payment

Payment is made within 10 days.
"""

V2 = V1.replace("within 14 days", "within 21 days")
V3 = V2.replace("## Deadlines\n\nAppeals are filed within 21 days.\n\n", "")


def _page(version, body, **kw):
    return dict({"id": "98765", "title": "Grant rules", "version": version, "space": "ACME", "url": "https://x/wiki/98765",
                 "updated": "2026-10-0%d" % version, "author": "Jane Roe", "body": body}, **kw)


def _cap(root, page, name="page.json"):
    p = write_json(root, name, page)
    code, out = run(root, "--json", "intake", "confluence", "--page", p)
    assert code == 0, out
    return json.loads(out)


def _blocks(root, res):
    import re
    return re.findall(r"^### SRC-(\d+) · (\S+) · (.*)$", read(root, res["path"]), re.M)


def test_sections_split_on_headings_and_repeats_are_keyed():
    secs = confluence.sections("intro\n\n## A\n\nx\n\n## A\n\ny\n\n```\n## not a heading\n```\n")
    assert [k for k, _h, _t in secs] == ["(intro)", "A", "A #2"], secs
    assert "## not a heading" in secs[2][2]


def test_first_capture_mints_one_note_with_a_block_per_section():
    root, _ = fresh("comm-vault")
    res = _cap(root, _page(1, V1))
    assert res["action"] == "minted" and res["new_blocks"] == 4, res
    note = read(root, res["path"])
    assert "source: confluence" in note and 'conf:98765@v1' in note and "confluence_id" in note
    assert [b[1] for b in _blocks(root, res)] == ["section"] * 4
    assert "\n## Eligibility" not in note.split("## Raw")[1].split("## Capture history")[0]   # demoted, cannot split the note
    assert os.path.exists(os.path.join(root, "00-Inbox/_raw/confluence/98765.json"))
    code, out = run(root, "lint", "--full")
    assert code == 0, out


def test_unchanged_or_older_version_is_a_no_op():
    root, _ = fresh("comm-vault")
    first = _cap(root, _page(2, V1))
    before = read(root, first["path"])
    assert _cap(root, _page(2, V1))["action"] == "unchanged"
    assert _cap(root, _page(1, V2))["action"] == "unchanged"
    assert read(root, first["path"]) == before


def test_edited_section_appends_exactly_one_block_and_reopens_the_note():
    root, _ = fresh("comm-vault")
    first = _cap(root, _page(1, V1))
    p = os.path.join(root, first["path"])
    s = read(root, first["path"]).replace("status: raw", "status: extracted", 1)          # as if it had been filed
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    res = _cap(root, _page(2, V2))
    assert res["action"] == "appended" and res["new_blocks"] == 1 and res["removed"] == [], res
    blocks = _blocks(root, res)
    assert len(blocks) == 5 and blocks[-1][1] == "section" and "Deadlines" in blocks[-1][2], blocks
    note = read(root, res["path"])
    assert "status: raw" in note and "within 21 days" in note and "within 14 days" in note   # old block is never touched
    assert 'conf:98765@v2' in note and 'conf:98765@v1' not in note
    assert note.count("captured Confluence page 98765 v1") == 1 and "v1 → v2" in note


def test_removed_section_is_a_removed_block():
    root, _ = fresh("comm-vault")
    _cap(root, _page(1, V1))
    _cap(root, _page(2, V2))
    res = _cap(root, _page(3, V3))
    assert res["new_blocks"] == 1 and res["removed"] == ["Deadlines"], res
    kind = _blocks(root, res)[-1][1]
    assert kind == "removed", kind
    assert "was removed from the page in v3" in read(root, res["path"])


def test_dry_writes_nothing_and_lint_flags_a_missing_high_water_mark():
    root, _ = fresh("comm-vault")
    res = _cap(root, _page(1, V1))
    code, out = run(root, "--json", "intake", "confluence", "--dry", "--page", write_json(root, "p2.json", _page(2, V2)))
    assert code == 0 and json.loads(out)["action"] == "append"
    assert 'conf:98765@v2' not in read(root, res["path"])
    p = os.path.join(root, res["path"])
    s = read(root, res["path"]).replace("conf:98765@v1", "x")
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    code, out = run(root, "lint", "--full")
    assert code == 1 and "high-water mark" in out, out
