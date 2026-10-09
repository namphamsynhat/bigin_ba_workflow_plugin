"""Jira capture (`bigin intake jira`): one living INT note per ticket, day-by-day deltas only."""
import copy
import os

from helpers import fresh, read, run, write_json

from bigin.intake import jira
from bigin.vault import Doc

ONSHORE = {"displayName": "Jane Roe", "emailAddress": "jane@acme.com", "accountId": "a-1"}
OFFSHORE = {"displayName": "Nam Pham", "emailAddress": "nam@bigin.vn", "accountId": "b-1"}
STRANGER = {"displayName": "Pat Unknown", "accountId": "z-9"}

MAPPING = """
## Jira status mapping

| Project | Issue types | Jira status | Phase |
|---|---|---|---|
| ACME | * | To Do | active |
| ACME | * | In Discussion | active |
| ACME | Story, Task, Bug | Scope Agreed | scope-agreed |
| ACME | Epic | Scope Agreed | scope-agreed |
| ACME | * | Done | done |
| ACME | * | Won't Do | ignore |
"""


def adf(*paras):
    return {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": p}]}
                                                      for p in paras]}


def setup():
    root, v = fresh("comm-vault")
    p = os.path.join(root, "_bigin", "system", "project.md")
    text = read(root, "_bigin/system/project.md")
    text = text.replace("client_emails: []", "client_emails: [acme.com]").replace("team_emails: []", "team_emails: []")
    text = text.replace("updated: 2026-09-20\n---", "jira_provider: atlassian\njira_site: acme.atlassian.net\n"
                        "jira_projects: [ACME]\njira_scope_marker: \"Final scope\"\njira_onshore: []\n"
                        "jira_offshore: [b-1]\nupdated: 2026-09-20\n---")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text + MAPPING)
    return root


def day1():
    return {"issue": {"key": "ACME-123", "fields": {
        "summary": "Second reviewer for large grants", "issuetype": {"name": "Story"}, "status": {"name": "To Do"},
        "project": {"key": "ACME"}, "priority": {"name": "High"}, "labels": ["grants"], "parent": {"key": "ACME-100"},
        "reporter": ONSHORE, "assignee": OFFSHORE, "created": "2026-10-01T09:14:00.000+0700",
        "updated": "2026-10-01T09:14:00.000+0700",
        "description": adf("Grants over $5,000 must be approved by a second reviewer.")}},
        "comments": [], "changelog": []}


def day3():
    d = day1()
    f = d["issue"]["fields"]
    f["status"] = {"name": "In Discussion"}
    f["description"] = adf("Grants over $10,000 must be approved by a second reviewer.",
                           "The second reviewer cannot be the first reviewer.")
    f["updated"] = "2026-10-03T10:00:00.000+0700"
    d["comments"] = [
        {"id": "10234", "author": OFFSHORE, "created": "2026-10-02T08:55:00.000+0700",
         "updated": "2026-10-02T08:55:00.000+0700", "body": adf("Is the threshold $5,000 or $10,000? Finance said 10k.")},
        {"id": "10240", "author": ONSHORE, "created": "2026-10-03T09:30:00.000+0700",
         "updated": "2026-10-03T09:30:00.000+0700", "body": "Plain-text body: it is $10,000, I updated the description."},
    ]
    d["changelog"] = [
        {"id": "501", "author": ONSHORE, "created": "2026-10-02T08:00:00.000+0700",
         "items": [{"field": "status", "fromString": "To Do", "toString": "In Discussion"}]},
        {"id": "502", "author": ONSHORE, "created": "2026-10-03T10:00:00.000+0700",
         "items": [{"field": "description", "fromString": "…", "toString": "…"}]},
    ]
    return d


def day5():
    d = day3()
    f = d["issue"]["fields"]
    f["status"] = {"name": "Scope Agreed"}
    f["updated"] = "2026-10-05T11:00:00.000+0700"
    d["comments"][0]["updated"] = "2026-10-04T07:00:00.000+0700"  # offshore edited their question
    d["comments"][0]["body"] = adf("Is the threshold $5,000 or $10,000? (edit: Finance confirmed 10k by email)")
    d["comments"].append({"id": "10301", "author": STRANGER, "created": "2026-10-05T10:00:00.000+0700",
                          "updated": "2026-10-05T10:00:00.000+0700",
                          "body": adf("Final scope: threshold $10,000; second reviewer distinct from first.")})
    d["changelog"].append({"id": "503", "author": ONSHORE, "created": "2026-10-05T11:00:00.000+0700",
                           "items": [{"field": "status", "fromString": "In Discussion", "toString": "Scope Agreed"}]})
    return d


def capture(root, raw, name="ACME-123.json"):
    p = write_json(root, name, raw)
    code, out = run(root, "--json", "intake", "jira", "--issue", p)
    assert code == 0, out
    import json
    return json.loads(out)


def note_text(root, res):
    return read(root, res["path"])


def test_adf_rendering():
    doc = {"type": "doc", "content": [
        {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Scope"}]},
        {"type": "bulletList", "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "limit", "marks": [{"type": "code"}]}, {"type": "text", "text": " is 10k"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "see"}, {"type": "hardBreak"},
                {"type": "text", "text": "doc", "marks": [{"type": "link", "attrs": {"href": "http://x"}}]}]}]}]},
        {"type": "paragraph", "content": [{"type": "mention", "attrs": {"id": "a-1", "text": "@Jane Roe"}}]},
    ]}
    md = jira.adf_to_md(doc)
    assert md.startswith("## Scope"), md
    assert "- `limit` is 10k" in md and "[doc](http://x)" in md and "@Jane Roe" in md
    assert jira.adf_to_md("plain") == "plain" and jira.adf_to_md(None) == ""


def test_day1_mints_one_note_with_sides_and_phase():
    root = setup()
    res = capture(root, day1())
    assert res["action"] == "minted" and res["phase"] == "active" and res["new_blocks"] == 1, res
    d = Doc(note_text(root, res))
    assert d.fm_get("source") == "jira" and d.fm_get("jira_key") == "ACME-123" and d.fm_get("jira_type") == "Story"
    assert d.fm_get("jira_parent") == "ACME-100" and d.fm_get("status") == "raw" and d.fm_get("kind") == "requirement"
    assert "jira:ACME-123" in d.fm_list("source_ids")
    txt = d.text
    assert "### SRC-1 · ticket · ACME-123 — Jane Roe (onshore) 2026-10-01T09:14+0700" in txt
    assert "Assignee: Nam Pham (offshore)" in txt and "$5,000" in txt
    assert d.fm_list("raw_sources") == ["SRC-1 · ticket · ACME-123 — Jane Roe (onshore) 2026-10-01T09:14+0700"]


def test_resweep_same_day_is_unchanged():
    root = setup()
    capture(root, day1())
    res = capture(root, day1())
    assert res["action"] == "unchanged" and res["new_blocks"] == 0, res


def test_day_by_day_appends_only_the_delta():
    root = setup()
    r1 = capture(root, day1())
    # pretend the note was extracted and filed in between
    p = os.path.join(root, r1["path"])
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("status: raw", "status: in-review", 1))

    r3 = capture(root, day3())
    assert r3["action"] == "appended" and r3["new_blocks"] == 4, r3  # status, 2 comments, description (its changelog entry folds in)
    d = Doc(note_text(root, r3))
    assert d.fm_get("status") == "raw", "a note that gained blocks is re-opened for extract"
    assert d.fm_get("jira_status") == "In Discussion"
    kinds = [x.split(" · ")[1] for x in d.fm_list("raw_sources")]
    assert kinds == ["ticket", "fields", "comment", "comment", "description"], kinds
    txt = d.text
    assert "SRC-1 · ticket" in txt and "$5,000 must be approved" in txt, "day-1 block is never edited"
    assert "### SRC-5 · description · ACME-123#desc — Jane Roe (onshore) 2026-10-03T10:00+0700" in txt
    assert "- status: To Do → In Discussion" in txt
    assert "Plain-text body: it is $10,000" in txt

    r5 = capture(root, day5())
    assert r5["phase"] == "scope-agreed" and r5["new_blocks"] == 3, r5  # edited comment, new comment, status
    d = Doc(note_text(root, r5))
    txt = d.text
    assert "(edited 2026-10-04T07:00+0700)" in txt and "Finance confirmed 10k" in txt
    assert "Is the threshold $5,000 or $10,000? Finance said 10k." in txt, "the original comment block stays"
    assert "Pat Unknown (unknown)" in txt and "needs-review" in d.fm_list("tags")
    assert r5["unknown_authors"] == ["Pat Unknown"]
    nums = [int(x.split(" · ")[0][4:]) for x in d.fm_list("raw_sources")]
    assert nums == list(range(1, 9)), nums
    hist = d.get("Capture history")
    assert hist.count("jira sweep ACME-123") == 2 and "captured ACME-123" in hist


def test_unmapped_status_warns_and_counts_as_active():
    root = setup()
    raw = day1()
    raw["issue"]["fields"]["status"] = {"name": "Triage"}
    res = capture(root, raw)
    assert res["phase"] == "active" and res["warnings"] and "Triage" in res["warnings"][0]


def test_ignore_and_done():
    root = setup()
    raw = day1()
    raw["issue"]["fields"]["status"] = {"name": "Won't Do"}
    assert capture(root, raw)["action"] == "ignored"
    assert not any(n.startswith("INT-004") for n in os.listdir(os.path.join(root, "00-Inbox")))
    capture(root, day1())
    done = day3()
    done["issue"]["fields"]["status"] = {"name": "Done"}
    assert capture(root, done)["action"] == "appended"
    later = copy.deepcopy(done)
    later["comments"].append({"id": "999", "author": ONSHORE, "created": "2026-10-09T09:00:00.000+0700",
                              "updated": "2026-10-09T09:00:00.000+0700", "body": "thanks"})
    assert capture(root, later)["action"] == "closed", "a done note stays closed while the ticket is done"


def test_child_inherits_epic_feature_and_bug_is_feedback():
    root = setup()
    epic = day1()
    epic["issue"]["key"] = "ACME-100"
    epic["issue"]["fields"].update({"issuetype": {"name": "Epic"}, "parent": None, "summary": "Grant review"})
    r = capture(root, epic, "ACME-100.json")
    p = os.path.join(root, r["path"])
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("\nfeature:", "\nfeature: grant-intake", 1))
    bug = day1()
    bug["issue"]["key"] = "ACME-130"
    bug["issue"]["fields"]["issuetype"] = {"name": "Bug"}
    rb = capture(root, bug, "ACME-130.json")
    d = Doc(note_text(root, rb))
    assert d.fm_list("declared_features") == ["grant-intake"] and d.fm_get("kind") == "feedback"


def test_dry_writes_nothing():
    root = setup()
    p = write_json(root, "ACME-123.json", day1())
    before = sorted(os.listdir(os.path.join(root, "00-Inbox")))
    code, out = run(root, "intake", "jira", "--issue", p, "--dry")
    assert code == 0 and "mint" in out, out
    assert sorted(os.listdir(os.path.join(root, "00-Inbox"))) == before


def test_captured_notes_lint_clean():
    root = setup()
    capture(root, day1())
    capture(root, day3())
    capture(root, day5())
    code, out = run(root, "lint", "--full")
    assert code == 0, out


def test_lint_flags_hand_edited_jira_blocks():
    root = setup()
    res = capture(root, day3())
    p = os.path.join(root, res["path"])
    with open(p, encoding="utf-8") as f:
        t = f.read()
    t = t.replace('"jira:ACME-123#c10240@2026-10-03T09:30+0700"', '"jira:ACME-123"', 1)
    t = t.replace("Nam Pham (offshore) 2026-10-02T08:55", "Nam Pham 2026-10-02T08:55")
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)
    code, out = run(root, "lint", "--full")
    assert code != 0 and "jira block not in source_ids" in out and "jira block without a side" in out, out


# ---------------------------------------------------------------------------- living-ticket extraction

def _signals(root, nid, rows, mode=None, name="sig.json"):
    obj = {"$schema_version": 1, "kind": "signals", "int": nid, "rows": rows}
    if mode:
        obj["mode"] = mode
    p = write_json(root, name, obj)
    code, out = run(root, "--json", "note", "write-signals", p)
    import json
    return code, (json.loads(out) if code == 0 else out)


def _worklist(root, nid):
    import json
    code, out = run(root, "--json", "worklist", "extract", nid)
    assert code == 0, out
    return json.loads(out)


def test_living_ticket_extracts_only_new_blocks_and_links_supersession():
    root = setup()
    r1 = capture(root, day1())
    nid = r1["id"]
    w = _worklist(root, nid)
    assert w["mode"] == "fresh" and w["jira"]["phase"] == "active" and w["jira"]["scope_marker"] == "Final scope"
    assert not any("new" in b for b in w["src_blocks"]), "first extraction reads everything"
    code, res = _signals(root, nid, [
        {"type": "requirement", "signal": "Grants over $5,000 need a second reviewer", "why": "not stated",
         "source": "ACME-123 Jane Roe (onshore) 2026-10-01", "scope": "open"}])
    assert code == 0 and res["audit_owed"] is True, res
    d = Doc(note_text(root, r1))
    assert d.fm_get("extracted_through") == "SRC-1"
    assert "[scope:open]" in d.get("Extracted signals")

    capture(root, day3())
    w = _worklist(root, nid)
    assert w["mode"] == "append"
    assert [b["src"] for b in w["src_blocks"] if b.get("new")] == ["SRC-2", "SRC-3", "SRC-4", "SRC-5"]
    assert w["existing_rows"][0]["n"] == 1 and "new: true" in w["read"]

    code, res = _signals(root, nid, [
        {"type": "requirement", "signal": "Grants over $10,000 need a second reviewer", "why": "not stated",
         "source": "ACME-123#desc Jane Roe (onshore) 2026-10-03", "scope": "agreed", "supersedes": [1]},
        {"type": "requirement", "signal": "The second reviewer is not the first reviewer", "why": "not stated",
         "source": "ACME-123#desc Jane Roe (onshore) 2026-10-03", "scope": "agreed"}])
    assert code == 0 and res["added"] == [2, 3] and res["superseded"] == [1], res
    t = Doc(note_text(root, r1)).get("Extracted signals")
    assert "| 1 | requirement | Grants over $5,000 need a second reviewer" in t, "the earlier row stays"
    assert "[scope:open]; superseded by #2" in t and "[scope:agreed]; supersedes #1" in t
    assert Doc(note_text(root, r1)).fm_get("extracted_through") == "SRC-5"


def test_supersedes_must_point_back():
    root = setup()
    r1 = capture(root, day1())
    code, out = _signals(root, r1["id"], [
        {"type": "requirement", "signal": "x", "source": "s", "supersedes": [7]}])
    assert code != 0 and "not an earlier row" in out, out


def test_file_worklist_carries_scope_and_supersession():
    import json
    root = setup()
    r1 = capture(root, day1())
    nid = r1["id"]
    _signals(root, nid, [{"type": "requirement", "signal": "Over $5,000 needs a second reviewer",
                          "source": "ACME-123 Jane Roe (onshore) 2026-10-01", "scope": "open"}])
    # file row 1 by hand, as a filer would have
    p = os.path.join(root, r1["path"])
    with open(p, encoding="utf-8") as f:
        t = f.read()
    lines = t.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("| 1 | requirement |"):
            cells = line.split("|")
            cells[6], cells[7] = " grant-intake ", " question "
            lines[i] = "|".join(cells)
    t = "\n".join(lines)
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)
    capture(root, day3())
    _signals(root, nid, [{"type": "requirement", "signal": "Over $10,000 needs a second reviewer",
                          "source": "ACME-123#desc Jane Roe (onshore) 2026-10-03", "scope": "agreed", "supersedes": [1]},
                         {"type": "requirement", "signal": "Export to PDF", "source": "ACME-123#c10234 Nam Pham (offshore)",
                          "scope": "dropped"}], name="s2.json")
    code, out = run(root, "--json", "worklist", "file", nid)
    assert code == 0, out
    rows = {r["n"]: r for r in json.loads(out)["rows"]}
    assert 1 not in rows, "filed rows are not re-filed"
    assert rows[2]["scope"] == "agreed" and rows[2]["supersedes"] == [{"n": 1, "feature": "grant-intake", "status": "question"}]
    assert rows[3]["scope"] == "dropped" and "supersedes" not in rows[3]
