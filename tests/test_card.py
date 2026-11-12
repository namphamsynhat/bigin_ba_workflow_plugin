"""Dev cards (lib/bigin/card.py): one checkable page per screen / back-end process, rendered from the vault."""
import json
import os

from helpers import read, run

import test_before_after as tba
import test_stories as ts

UX = """---
id: UX-001
type: uiux
title: "Payments screens"
status: accepted
version: 1.0
feature: payments
uc: [UC-005]
absorbed: [UC-005@2.0]
updated: 2026-09-20
---

# `UX-001 Payments`

## 2. Screen Inventory

| Screen | View ID | Screen Type | Actor | Volume | Purpose | Serves | Entities | Key actions |
|--------|---------|-------------|-------|--------|---------|--------|----------|-------------|
| Payment queue | payments-queue | Primary | Finance officer | few | Pick a payment to release | UC-005 S1, S2, E1 | EN-002 | Release |

## 3. Screen Specs

### `Payment queue`

* **View ID:** `payments-queue`
* **Serves:** `UC-005 S1, S2`

| Element | Content / copy | Role | Field | Visible to | Grounded by |
|---------|----------------|------|-------|------------|-------------|
| Release | "Release payment" | primary action | | | UC-005 S3; BR-005 |
| Hold timer | "Held for 5 min" | muted | | | pattern: soft lock |

**States**

| State | Trigger | What the user sees | Grounded by |
|-------|---------|--------------------|-------------|
| empty | no payments | "Nothing to release" | UC-005 S1 |

**Interactions**

| Control | Does | Goes to |
|---------|------|---------|
| Release | asks for sign-off | Sign-off |

## Changelog
- 1.0 (2026-09-20) — created
"""

HUB_ROW = "| 5 | Officers release from a queue | requirement | INT-002 #7 — [00:15] | applied | UC-005 S1, S2 |  |\n"


def _vault():
    root = tba.ti._vault()
    ts._w(root, "04-UIUX/UX-001 Payments.md", UX)
    hub = os.path.join(root, "01-Requirements", "_features", "payments.md")
    t = open(hub, encoding="utf-8").read()
    anchor = next(line for line in t.splitlines(True) if line.startswith("| 4 |"))
    t = t.replace(anchor, anchor + HUB_ROW, 1)
    open(hub, "w", encoding="utf-8").write(t)
    p = os.path.join(root, ts.EPIC_DIR, "US-001 Release a payment.md")
    t = open(p, encoding="utf-8").read()
    t += "\n## 7. Boundaries\n\n* Refunds stay in UC-004\n\n## 8. Notes\n\n**Still open**\n\n**Decisions**\n\n" \
         "**Assumptions**\n\n* The queue shows today's payments only\n"
    open(p, "w", encoding="utf-8").write(t)
    return root


def _cards(root, target="EP-001"):
    code, out = run(root, "--json", "card", target)
    assert code == 0, out
    return json.loads(out)


def test_one_card_per_screen_and_one_per_unserved_process():
    res = _cards(_vault())
    kinds = [(c["type"], c["id"]) for c in res["cards"]]
    assert ("screen", "payments-queue") in kinds
    assert ("process", "UC-005-process") in kinds, "S3/S4/A1/E2 have no screen: a back-end card holds them"
    scr = next(c for c in res["cards"] if c["id"] == "payments-queue")
    assert scr["stories"] == ["US-001"], "US-002 slices A1 only, which no screen serves"
    assert scr["size"]["elements"] == 2 and scr["size"]["states"] == 1 and scr["size"]["actions"] == 1


def test_ai_assumed_lists_design_only_unsourced_and_declared_lines():
    res = _cards(_vault())
    scr = next(c for c in res["cards"] if c["id"] == "payments-queue")
    whys = {a["why"] for a in scr["assumed"]}
    whats = " ".join(a["what"] for a in scr["assumed"])
    assert "Hold timer" in whats and any(w.startswith("design only") for w in whys)
    assert "UC-005 S1" not in whats and "UC-005 S2" not in whats, "hub row #5 cites INT-002 for S1, S2"
    assert "today's payments" in whats, "story § 8 Assumptions are listed"
    proc = next(c for c in res["cards"] if c["type"] == "process")
    assert any("UC-005 S4" in a["what"] and a["why"] == "no client signal" for a in proc["assumed"])


def test_card_carries_rules_scope_and_acceptance():
    res = _cards(_vault())
    scr = next(c for c in res["cards"] if c["id"] == "payments-queue")
    assert "Refunds stay in UC-004" in scr["out_of_scope"]
    assert any(r["id"] == "BR-005" for r in scr["rules"])
    assert any("Payee has no bank details" in a for a in scr["acceptance"]), "E1 is served by this screen"


def test_change_request_shows_before_after_from_the_note():
    root = _vault()
    code, out = tba._replace(root, "cs-c1", "INT-002", "Finance officer confirms with a second approver.")
    assert code == 0, out
    run(root, "cascade")
    res = _cards(root)
    proc = next(c for c in res["cards"] if c["type"] == "process")
    row = next(r for r in proc["changes"] if r["where"].startswith("UC-005"))
    assert "S3" in row["where"] and "second approver" in row["after"] and "INT-002" in row["cite"]


def test_story_target_and_write():
    root = _vault()
    res = _cards(root, "US-002")
    assert [c["stories"] for c in res["cards"]] == [["US-002"]]
    code, out = run(root, "card", "EP-001", "--write")
    assert code == 0 and "[written:" in out, out
    text = read(root, os.path.join(ts.EPIC_DIR, "_cards.md"))
    assert "## payments-queue · Payment queue" in text and "AI assumed (check these!):" in text
    code, out = run(root, "lint", "--full")
    assert "_cards.md" not in out, "the card file is not a story and lint leaves it alone"


def test_lint_flags_a_story_screen_the_ux_spec_does_not_name():
    root = _vault()
    code, out = run(root, "lint", "--full")
    assert "story screen not in the UX spec" in out and "SCR-01" in out, out[-800:]
    for name in ("US-001 Release a payment.md", "US-002 Release a small payment without sign-off.md"):
        p = os.path.join(root, ts.EPIC_DIR, name)
        t = open(p, encoding="utf-8").read()
        t = t.replace("screens: [SCR-01, SCR-02]", "screens: [payments-queue]").replace("screens: [SCR-02]", "screens: [Payment queue]")
        open(p, "w", encoding="utf-8").write(t)
    code, out = run(root, "lint", "--full")
    assert "story screen not in the UX spec" not in out, out[-800:]


def test_build_pack_is_self_contained_and_stamped():
    root = _vault()
    code, out = run(root, "card", "US-001", "--for", "agent", "--write")
    assert code == 0 and "[written:" in out, out
    text = read(root, os.path.join(ts.EPIC_DIR, "_build", "US-001.md"))
    assert text.startswith("# Build pack — US-001@1 ")
    assert "Not approved yet" not in text, "the fixture's stories are approved"
    assert "| S3 | Finance officer requests release. |" in text, "the sliced UC steps travel with the pack"
    assert "**BR-005@" in text and "(no statement)" not in text.split("**BR-005@")[1].splitlines()[0]
    assert "US-001 AC1" in text and "stop and ask" in text


def _set_hours(root, key, task, hours):
    p = os.path.join(root, ts.EPIC_DIR, "_estimate.md")
    lines = open(p, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"| {key} |"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            cells[2], cells[3] = task, hours
            lines[i] = "| " + " | ".join(cells) + " |"
            lines.insert(i + 1, f"|  |  | extra task | 1.5 | dev added |")
            break
    else:
        raise AssertionError(key)
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def test_estimate_sheet_keeps_dev_lines_and_flags_removed_scope():
    root = _vault()
    code, out = run(root, "card", "EP-001", "--estimate")
    assert code == 0 and "_estimate.md" in out, out
    text = read(root, os.path.join(ts.EPIC_DIR, "_estimate.md"))
    key = "payments-queue · US-001 Payee has no bank details"
    assert f"| {key} |" in text and "## UC-005-process" not in text and "## UC-005 Release a large payment" in text
    _set_hours(root, key, "block release when bank details missing", "3")
    code, out = run(root, "card", "EP-001", "--estimate")
    text = read(root, os.path.join(ts.EPIC_DIR, "_estimate.md"))
    assert "block release when bank details missing | 3 |" in text and "extra task | 1.5" in text
    assert "**Total: 4.5 h (with AI)**" in text and "0 new scope row(s)" in out
    p = os.path.join(root, ts.EPIC_DIR, "US-001 Release a payment.md")
    t = open(p, encoding="utf-8").read().replace("- **Scenario: Payee has no bank details** [E1]", "")
    open(p, "w", encoding="utf-8").write(t)
    code, out = run(root, "card", "EP-001", "--estimate")
    text = read(root, os.path.join(ts.EPIC_DIR, "_estimate.md"))
    assert "## Source removed" in text and "source removed" in text and "3 |" in text
    assert "1 with source removed" in out, out


def test_jira_paste_text_is_written_for_a_human_and_touches_no_story():
    root = _vault()
    before = read(root, os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md"))
    code, out = run(root, "card", "EP-001", "--for", "jira", "--write")
    assert code == 0 and "[written:" in out, out
    text = read(root, os.path.join(ts.EPIC_DIR, "_jira.md"))
    assert "## Epic — EP-001" in text and "## Story — US-001" in text and "## Story — US-002" in text
    assert "**Summary:** US-001@1 Release a payment" in text and "**Acceptance criteria:**" in text
    assert "AI assumed" in text, "the story's cards travel in the description"
    assert read(root, os.path.join(ts.EPIC_DIR, "US-001 Release a payment.md")) == before
    code, out = run(root, "card", "US-002", "--for", "jira")
    assert "## Story — US-002" in out and "US-001" not in out.split("## Story — US-002")[0].split("-->")[-1]


def test_lint_advises_on_size_and_plain_english():
    root = _vault()
    p = os.path.join(root, ts.EPIC_DIR, "US-001 Release a payment.md")
    t = open(p, encoding="utf-8").read()
    long = ("As a finance officer who works in the payments team every single day of the week I want to release "
            "an approved payment quickly so that the grantee is paid on time and nobody waits.")
    t = t.replace("As a finance officer I want to release an approved payment so that the grantee is paid on time.", long)
    t = t.replace("screens: [SCR-01, SCR-02]", "screens: [a, b, c, d]")
    open(p, "w", encoding="utf-8").write(t)
    code, out = run(root, "lint", "--full")
    assert "story may be bigger than one PR" in out and "4 screens" in out, out[-800:]
    assert "plain English" in out and "-word sentence" in out, out[-800:]
