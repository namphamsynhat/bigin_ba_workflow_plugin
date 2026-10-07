"""Epics and user stories (03-Epics-Stories/): mint, frontmatter schema, S1 lint, mermaid, coverage."""
import os

from helpers import fresh, read, run, write_json

EPIC_DIR = os.path.join("03-Epics-Stories", "EP-001 Payments")

UC = """---
id: UC-005
type: use-case
title: "Release a large payment"
status: approved
version: 2.0
primary_feature: payments
features: [payments]
brs: [BR-005]
---

# `UC-005 Release a large payment`

## 1. Context & Metadata

* **Primary Actor:** Finance officer

## 2. Main Success Scenario

| Step | Actor Action | System Response & Validation |
| :--- | :--- | :--- |
| **S1** | Finance officer opens the payment queue. | System lists payments awaiting release. |
| **S2** | Finance officer selects a payment. | System shows the amount and payee. |
| **S3** | Finance officer requests release. | System checks the sign-off rule. |
| **S4** | Finance manager signs off. | System sends the payment and records it. |

## 3. Alternative & Exception Flows

### A1: Payment under the sign-off limit
At S3 the amount is under $10,000: the system releases it without sign-off. Rejoins at S4.

### E1: Payee bank details missing
At S2 the payee has no bank details: the system blocks release. Fails.

### E2: Sign-off declined
At S4 the manager declines: the payment returns to the queue. Fails.

## 4. Business Rules & Compliance Constraints

## Changelog
- 1.0 (2026-09-20) — created
"""

EPIC = """---
id: EP-001
type: epic
title: "Payments"
status: draft
version: 1
feature: payments
source_ucs: [UC-005]
absorbed: [UC-005@2.0]
snapshot: none
stories: [US-001, US-002]
after: []
---

# `EP-001 Payments`

## 4. End-to-end screen flow

```mermaid
flowchart LR
  Queue --> Detail --> SignOff
```

## 7. Coverage Matrix

| UC step | Story |
| :--- | :--- |
| UC-005 S1–S4 | US-001 |
| UC-005 A1 | US-002 |
"""

STORY_1 = """---
id: US-001
type: user-story
title: "Release a payment"
epic: EP-001
status: draft
version: 1
priority: P1
slice_of: UC-005 S1–S4
rules: [BR-005]
screens: [SCR-01, SCR-02]
entities: []
after: []
snapshot: none
absorbed: [UC-005@2.0]
---

# `US-001 Release a payment`

## 1. Story

As a finance officer I want to release an approved payment so that the grantee is paid on time.

## 3. Flowchart

```mermaid
flowchart TD
  A[Open queue] --> B{Over the limit?}
  B -- yes --> C[Manager signs off]
```

## 6. Acceptance Criteria

- **Scenario: Payment is released after sign-off** [S3, BR-005]
- **Scenario: Payee has no bank details** [E1]
"""

STORY_2 = """---
id: US-002
type: user-story
title: "Release a small payment without sign-off"
epic: EP-001
status: draft
version: 1
priority: P2
slice_of: UC-005 A1
rules: []
screens: [SCR-02]
entities: []
after: [US-001]
snapshot: none
absorbed: [UC-005@2.0]
---

# `US-002 Release a small payment without sign-off`

## 6. Acceptance Criteria

- **Scenario: Small payment skips sign-off** [A1]
"""

EPIC_TPL = """---
id: EP-000
type: epic
title: ""
status: draft
version: 1
feature:
source_ucs: []
absorbed: []
snapshot: none
stories: []
after: []
updated:
---

# `EP-000 Feature`

## 1. Goal & outcome

## Changelog
- 1.0 (YYYY-MM-DD) — created
"""

STORY_TPL = """---
id: US-000
type: user-story
title: ""
epic:
status: draft
version: 1
priority: P2
slice_of:
rules: []
screens: []
entities: []
after: []
snapshot: none
absorbed: []
updated:
---

# `US-000 Title`

## 1. Story

## 6. Acceptance Criteria

## Changelog
- 1.0 (YYYY-MM-DD) — created
"""


def _w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def _vault(story1=STORY_1):
    root, v = fresh("comm-vault")
    _w(root, "01-Requirements/_ucs/UC-005 Release a large payment.md", UC)
    _w(root, os.path.join(EPIC_DIR, "EP-001 Payments.md"), EPIC)
    _w(root, os.path.join(EPIC_DIR, "US-001 Release a payment.md"), story1)
    _w(root, os.path.join(EPIC_DIR, "US-002 Release a small payment without sign-off.md"), STORY_2)
    return root, v


def _story_findings(out):
    keys = ("technical wording", "mermaid block", "story frontmatter", "epic frontmatter",
            "story without its epic", "snapshot missing")
    return [line for line in out.splitlines() if any(k in line for k in keys)]


def test_clean_epic_and_stories_raise_no_story_findings():
    root, _v = _vault()
    _code, out = run(root, "lint", "--full")
    assert _story_findings(out) == [], out


def test_coverage_reports_only_the_untagged_exception_flow():
    root, _v = _vault()
    code, out = run(root, "coverage", "--stage", "stories")
    assert code == 1, out
    assert "EP-001 UC-005 E2" in out
    for covered in ("S1", "S4", "A1", "E1"):
        assert f"UC-005 {covered}," not in out and not out.rstrip().endswith(f"UC-005 {covered}"), out
    assert "missing 1" in out


def test_coverage_is_clean_once_e2_is_tagged():
    root, _v = _vault(STORY_1 + "- **Scenario: Manager declines** [E2]\n")
    code, out = run(root, "coverage", "--stage", "stories")
    assert code == 0, out
    assert "missing 0" in out


def test_lint_flags_technical_word_in_a_story():
    root, _v = _vault(STORY_1.replace("so that the grantee is paid on time",
                                      "so that the payments API posts the transfer"))
    _code, out = run(root, "lint", "--full")
    assert "technical wording (S1)" in out and "`API`" in out, out


def test_lint_ignores_ordinary_words_that_look_technical():
    root, _v = _vault(STORY_1.replace("on time", "on time, and the rest of the queue stays put"))
    _code, out = run(root, "lint", "--full")
    assert "technical wording (S1)" not in out, out


def test_lint_rejects_a_mermaid_block_with_an_unknown_header():
    root, _v = _vault(STORY_1.replace("flowchart TD", "flow TD"))
    _code, out = run(root, "lint", "--full")
    assert "mermaid block" in out and "`flow`" in out, out


def test_schema_rejects_a_bad_priority():
    root, _v = _vault(STORY_1.replace("priority: P1", "priority: urgent"))
    _code, out = run(root, "lint", "--full")
    assert "story frontmatter" in out and "urgent" in out, out


def test_story_missing_from_its_epic_is_flagged():
    root, _v = _vault()
    p = os.path.join(root, EPIC_DIR, "EP-001 Payments.md")
    _w(root, p, read(root, p).replace("stories: [US-001, US-002]", "stories: [US-001]"))
    _code, out = run(root, "lint", "--full")
    assert "story without its epic" in out and "US-002" in out, out


def test_pinned_snapshot_must_exist():
    root, _v = _vault(STORY_1.replace("snapshot: none", "snapshot: 2026-10-06-v1"))
    _code, out = run(root, "lint", "--full")
    assert "snapshot missing" in out, out
    _w(root, os.path.join(EPIC_DIR, "_snapshot", "2026-10-06-v1", "SNAPSHOT.md"), "# Snapshot\n")
    _code, out = run(root, "lint", "--full")
    assert "snapshot missing" not in out, out


def test_mint_ep_then_us_numbers_vault_wide_and_links_the_story():
    root, _v = _vault()
    _w(root, "_bigin/templates/epic.md", EPIC_TPL)
    _w(root, "_bigin/templates/user-story.md", STORY_TPL)
    spec = write_json(root, "ep.json", {"title": "Grant intake", "feature": "grant-intake",
                                        "source_ucs": ["UC-001"]})
    code, out = run(root, "mint", "ep", "--spec", spec)
    assert code == 0 and "EP-002" in out, out
    ep_rel = os.path.join("03-Epics-Stories", "EP-002 Grant intake", "EP-002 Grant intake.md")
    assert "feature: grant-intake" in read(root, ep_rel)

    code, out = run(root, "mint", "ep", "--spec", spec)
    assert code != 0 and "already has an epic" in out, out

    spec = write_json(root, "us.json", {"title": "Submit an application", "epic": "EP-002",
                                        "priority": "P1", "slice_of": "UC-001 S1-S3"})
    code, out = run(root, "mint", "us", "--spec", spec)
    assert code == 0 and "US-003" in out, out  # US-001/US-002 already exist under EP-001
    assert "stories: [US-003]" in read(root, ep_rel)
    us_rel = os.path.join("03-Epics-Stories", "EP-002 Grant intake", "US-003 Submit an application.md")
    text = read(root, us_rel)
    assert "epic: EP-002" in text and "priority: P1" in text
