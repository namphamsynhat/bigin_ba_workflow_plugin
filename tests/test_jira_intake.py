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


# ---------------------------------------------------------------------------- dev phase: ticket clear → use cases

DEV_ROW = "| ACME | * | Ready for Dev | dev |\n"


def _with_dev(root):
    p = os.path.join(root, "_bigin", "system", "project.md")
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("| ACME | * | Done | done |\n", DEV_ROW + "| ACME | * | Done | done |\n"))


def _hub_row(root, nid):
    p = os.path.join(root, "01-Requirements", "_features", "grant-intake.md")
    with open(p, encoding="utf-8") as f:
        t = f.read()
    anchor = "| 1 | **Online application**"
    i = t.index(anchor)
    end = t.index("\n", i)
    row = f"\n| 2 | **Second reviewer** — over $10,000 | requirement | {nid} #2 — Jane Roe 2026-10-03 | new |  |  |"
    with open(p, "w", encoding="utf-8") as f:
        f.write(t[:end] + row + t[end:])


def _route(root):
    import json
    code, out = run(root, "--json", "worklist", "route", "grant-intake")
    assert code == 0, out
    return json.loads(out)


def ready_for_dev():
    d = day5()
    d["issue"]["fields"]["status"] = {"name": "Ready for Dev"}
    d["issue"]["fields"]["updated"] = "2026-10-06T09:00:00.000+0700"
    d["changelog"].append({"id": "504", "author": ONSHORE, "created": "2026-10-06T09:00:00.000+0700",
                           "items": [{"field": "status", "fromString": "Scope Agreed", "toString": "Ready for Dev"}]})
    return d


def _cite(root, uc, nid):
    """Make ``uc`` built from intake note ``nid`` (its sources: list), as bigin apply would."""
    import glob
    p = glob.glob(os.path.join(root, "01-Requirements", "_ucs", f"{uc}*.md"))[0]
    with open(p, encoding="utf-8") as f:
        t = f.read()
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.replace("sources: [INT-001, INT-002]", f"sources: [INT-001, INT-002, {nid}]", 1))


def _ux(root, uc, ver):
    d = os.path.join(root, "04-UIUX")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "UX-001 grant-intake.md"), "w", encoding="utf-8") as f:
        f.write(f"---\nid: UX-001\ntype: ux-spec\nabsorbed: [{uc}@{ver}]\n---\n\n# UX-001\n")


def _gate(root, uc):
    import json
    code, out = run(root, "--json", "intake", "jira-gate", "--uc", uc)
    return code, json.loads(out)


def test_rows_route_to_use_cases_before_ready_for_dev():
    root = setup()
    _with_dev(root)
    r = capture(root, day1())
    _hub_row(root, r["id"])
    w = _route(root)
    assert [x["row"] for x in w["rows"]] == ["2"], "UC + design are drafted while the questions go back and forth"
    assert "waiting_on_jira" not in w


def test_approval_waits_for_ready_for_dev_then_names_the_ucs():
    root = setup()
    _with_dev(root)
    r = capture(root, day1())
    _cite(root, "UC-001", r["id"])
    code, g = _gate(root, "UC-001")
    assert code == 1 and not g["ok"] and g["waiting"][0]["key"] == "ACME-123", g
    capture(root, day5())                                  # scope agreed is still not dev
    assert _gate(root, "UC-001")[1]["ok"] is False

    res = capture(root, ready_for_dev())
    assert res["phase"] == "dev" and res["previous_phase"] == "scope-agreed" and res["released"] is True, res
    assert res["ready_ucs"] == ["UC-001"], res
    assert "its use cases may now be approved" in note_text(root, res)
    code, g = _gate(root, "UC-001")
    assert code == 0 and g["ok"] and g["waiting"] == []
    code, out = run(root, "intake", "jira", "--issue", os.path.join(root, "ACME-123.json"))
    assert "READY FOR DEV" not in out, "released only once"


def test_without_a_dev_mapping_approval_is_never_held():
    root = setup()
    r = capture(root, day1())
    _cite(root, "UC-001", r["id"])
    code, g = _gate(root, "UC-001")
    assert code == 0 and g["ok"], g


def test_sprint_report_shows_each_tickets_ucs_and_design():
    root = setup()
    _with_dev(root)
    _sprint(root, "Sprint 13", "ACME-123")
    r = capture(root, day1())
    _cite(root, "UC-001", r["id"])
    t = _report(root)["tickets"][0]
    assert t["ucs"] == [{"id": "UC-001", "status": "needs-clarification", "design": "none", "ux": None}], t
    assert t["ready_for_dev"] is False
    _ux(root, "UC-001", "1.0")
    assert _report(root)["tickets"][0]["ucs"][0]["design"] == "current"
    _ux(root, "UC-001", "0.9")
    assert _report(root)["tickets"][0]["ucs"][0]["design"] == "stale"
    code, out = run(root, "intake", "jira-sprint", "--report")
    assert "UC-001 needs-clarification · design stale (UX-001) · approval waits for Ready for Dev" in out, out


# ---------------------------------------------------------------------------- sprint watch list

def _ticket(key, parent="", summary="A ticket"):
    d = day1()
    d["issue"]["key"] = key
    d["issue"]["fields"]["summary"] = summary
    d["issue"]["fields"]["parent"] = {"key": parent} if parent else None
    return d


def _sprint(root, name, *keys):
    import json
    code, out = run(root, "--json", "intake", "jira-sprint", "--sprint", name, "--keys", *keys)
    assert code == 0, out
    return json.loads(out)


def _fm(root, res):
    return Doc(note_text(root, res))


def test_sprint_start_records_watch_list_and_names_tickets_to_fetch():
    root = setup()
    old = capture(root, _ticket("ACME-1"), "ACME-1.json")          # captured before any sprint
    res = _sprint(root, "Sprint 12", "ACME-100,ACME-2", "ACME-1")
    assert res["watch"] == ["ACME-100", "ACME-2", "ACME-1"] and res["to_fetch"] == ["ACME-100", "ACME-2"], res
    assert res["kept"] == [f"ACME-1 {old['id']}"] and res["closed"] == []
    proj = Doc(read(root, "_bigin/system/project.md"))
    assert proj.fm_get("jira_sprint") == "Sprint 12" and proj.fm_list("jira_watch") == ["ACME-100", "ACME-2", "ACME-1"]
    d = _fm(root, old)
    assert d.fm_get("jira_watch") == "true" and d.fm_get("jira_sprint") == "Sprint 12"


def test_new_child_of_a_watched_epic_is_watched_on_capture():
    root = setup()
    _sprint(root, "Sprint 12", "ACME-100")
    res = capture(root, _ticket("ACME-7", parent="ACME-100"), "ACME-7.json")
    d = _fm(root, res)
    assert d.fm_get("jira_watch") == "true" and d.fm_get("jira_sprint") == "Sprint 12", d.text[:800]


def test_next_sprint_closes_old_tickets_and_keeps_carried_over_ones():
    root = setup()
    _sprint(root, "Sprint 12", "ACME-1", "ACME-2", "ACME-100")
    a = capture(root, _ticket("ACME-1"), "ACME-1.json")
    b = capture(root, _ticket("ACME-2"), "ACME-2.json")
    child = capture(root, _ticket("ACME-7", parent="ACME-100"), "ACME-7.json")
    res = _sprint(root, "Sprint 13", "ACME-2", "ACME-100", "ACME-9")
    assert res["closed"] == [f"ACME-1 {a['id']}"], res
    assert sorted(res["kept"]) == sorted([f"ACME-2 {b['id']}", f"ACME-7 {child['id']}"]), res
    assert res["to_fetch"] == ["ACME-100", "ACME-9"]
    d = _fm(root, a)
    assert d.fm_get("jira_watch") == "false" and d.fm_get("jira_sprint_closed") == "Sprint 12"
    assert "sprint Sprint 13 started: ACME-1 is not on it — closed" in d.text
    assert _fm(root, b).fm_get("jira_sprint") == "Sprint 13"


def test_closed_ticket_fetched_explicitly_warns_and_stays_closed():
    root = setup()
    _sprint(root, "Sprint 12", "ACME-1")
    a = capture(root, _ticket("ACME-1"), "ACME-1.json")
    _sprint(root, "Sprint 13", "ACME-2")
    later = _ticket("ACME-1")
    later["comments"] = [{"id": "1", "author": ONSHORE, "created": "2026-10-09T08:00:00.000+0700",
                          "updated": "2026-10-09T08:00:00.000+0700", "body": adf("late comment")}]
    res = capture(root, later, "ACME-1.json")
    assert res["action"] == "appended" and any("not on sprint Sprint 13" in w for w in res["warnings"]), res
    assert _fm(root, a).fm_get("jira_watch") == "false"


def test_relisting_a_closed_ticket_reopens_it():
    root = setup()
    _sprint(root, "Sprint 12", "ACME-1")
    a = capture(root, _ticket("ACME-1"), "ACME-1.json")
    _sprint(root, "Sprint 13", "ACME-2")
    res = _sprint(root, "Sprint 14", "ACME-1")
    assert res["reopened"] == [f"ACME-1 {a['id']}"], res
    assert _fm(root, a).fm_get("jira_watch") == "true"


def test_closing_a_ticket_still_waiting_on_dev_warns():
    root = setup()
    _with_dev(root)
    _sprint(root, "Sprint 12", "ACME-123")
    capture(root, day1())
    res = _sprint(root, "Sprint 13", "ACME-2")
    assert any("ACME-123" in w and "waiting on a dev status" in w for w in res["warnings"]), res


def test_sprint_start_rejects_bad_input():
    root = setup()
    code, out = run(root, "intake", "jira-sprint", "--sprint", "S1", "--keys", "not-a-key")
    assert code != 0 and "not Jira keys" in out, out
    code, out = run(root, "intake", "jira-sprint", "--keys", "ACME-1")
    assert code != 0 and "--sprint" in out, out


# ---------------------------------------------------------------------------- sprint report: new feature / update / bug

def _signal(root, res, feature):
    """Simulate /extract-signal: one row in the note's ## Extracted signals with ``feature`` anchored."""
    p = os.path.join(root, res["path"])
    with open(p, encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = next(n for n, l in enumerate(lines) if l.startswith("## Extracted signals"))
    j = next(n for n in range(i, len(lines)) if lines[n].startswith("|---") or lines[n].startswith("| ---")
             or lines[n].startswith("|--"))
    lines.insert(j + 1, f"| 1 | requirement | a claim | not stated | x | {feature} | new |  |")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _feature_row(root, slug, sources):
    p = os.path.join(root, "01-Requirements", "FEATURES.md")
    with open(p, encoding="utf-8") as f:
        t = f.read().rstrip("\n")
    with open(p, "w", encoding="utf-8") as f:
        f.write(t + f"\n| {slug} | {slug} | proposed |  |  | {sources} |  |\n")


def _report(root):
    import json
    code, out = run(root, "--json", "intake", "jira-sprint", "--report")
    assert code == 0, out
    return json.loads(out)


def test_sprint_report_classifies_new_feature_update_bug_and_pending():
    root = setup()
    _sprint(root, "Sprint 13", "ACME-100", "ACME-2", "ACME-3", "ACME-4", "ACME-5", "ACME-6")
    ep = _ticket("ACME-100", summary="Grant renewals")
    ep["issue"]["fields"]["issuetype"] = {"name": "Epic"}
    epic = capture(root, ep, "ACME-100.json")
    upd = capture(root, _ticket("ACME-2"), "ACME-2.json")
    bug = _ticket("ACME-3")
    bug["issue"]["fields"]["issuetype"] = {"name": "Bug"}
    bug = capture(root, bug, "ACME-3.json")
    nf = capture(root, _ticket("ACME-4"), "ACME-4.json")
    amb = capture(root, _ticket("ACME-5"), "ACME-5.json")
    ep2 = _ticket("ACME-6")
    ep2["issue"]["fields"]["issuetype"] = {"name": "Epic"}
    pend = capture(root, ep2, "ACME-6.json")

    _signal(root, epic, "grant-renewals")                 # a slug born this sprint
    _feature_row(root, "grant-renewals", epic["id"])
    _signal(root, upd, "grant-intake")                    # existed before the sprint
    _signal(root, bug, "payments")
    _signal(root, nf, "unresolved — none found")
    _signal(root, amb, "unresolved — candidates: grant-intake / payments")

    r = _report(root)
    kinds = {t["key"]: t["kind"] for t in r["tickets"]}
    assert kinds == {"ACME-100": "new-feature", "ACME-2": "update", "ACME-3": "bug", "ACME-4": "new-feature",
                     "ACME-5": "needs-anchor", "ACME-6": "pending"}, kinds
    by = {t["key"]: t for t in r["tickets"]}
    assert "grant-renewals" in by["ACME-100"]["detail"] and "on payments" in by["ACME-3"]["detail"]
    assert "Epic — likely a new feature" in by["ACME-6"]["detail"]
    assert r["counts"]["new-feature"] == 2 and r["not_fetched"] == []
    code, out = run(root, "intake", "jira-sprint", "--report")
    assert "2 new-feature" in out and "1 bug" in out, out


def test_feature_from_an_earlier_ticket_is_an_update_not_new():
    root = setup()
    _sprint(root, "Sprint 12", "ACME-1")
    a = capture(root, _ticket("ACME-1"), "ACME-1.json")
    _signal(root, a, "renewals")
    _feature_row(root, "renewals", a["id"])
    assert _report(root)["tickets"][0]["kind"] == "new-feature"     # new in the sprint that created it
    _sprint(root, "Sprint 13", "ACME-2")
    b = capture(root, _ticket("ACME-2"), "ACME-2.json")
    _signal(root, b, "renewals")
    t = _report(root)["tickets"]
    assert [(x["key"], x["kind"]) for x in t] == [("ACME-2", "update")], t
