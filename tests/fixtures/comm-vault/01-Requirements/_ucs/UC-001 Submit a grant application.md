---
id: UC-001
type: use-case
title: "Submit a grant application"
status: needs-clarification
version: 1.0
synced: true
level: user-goal
scope: Acme Grants Portal
primary_feature: grant-intake
features: [grant-intake, payments]
brs: [BR-001, BR-002]
entities: []
pain_points: []
sources: [INT-001, INT-002]
links: []
attachments: []
absorbs: []
owner: team
updated: 2026-09-20
---

# `UC-001 Submit a grant application`


## 1. Context & Metadata
<!-- BABOK stakeholder-requirements framing. Fill every line or write "not stated" — a blank line
reads as "nobody looked", and "not stated" is a real, useful fact about the source. Never invent a
business need, a trigger, or a pre-condition the signals didn't state. -->

* **Primary Actor:** Parent
* **Secondary Actor(s):** Reviewer
* **Business Need / Goal:** Apply for a school grant online
* **Trigger:** not stated
* **Pre-conditions:**
  * The parent has an account
* **Post-conditions (success):**
  * An application is recorded and awaiting review
* **Post-conditions (failure):**
  * No partial application is kept
    <!-- The most commonly skipped field on this template, and the one whose absence produces the
    worst defects: it is what tells a developer whether a half-finished flow leaves a partial
    record behind. -->

## 2. Main Success Scenario
<!-- The happy path: trigger to goal delivery, plus any cleanup. Nothing goes wrong here — every
branch belongs in § 3.

One of the two sections /bigin-transform-signal writes without waiting for a human (§ 3 is the
other): Stage 4 Part 2 drafts a new/changed/removed step here directly, same run — sweeping every
outstanding ## Discussion entry for this section, not only what the current run staged. Keep it
short and high-level, plain business language, one line per step — a business reader should get the
whole flow from a handful of lines. Because this section skips the wait, any run that changes it
flags this UC for /approve-uc re-review (dropping status back from
enriched/approved/consolidated if it had reached one of those). Every other section still stages in
## Discussion and waits.

STEP IDS ARE PERMANENT. An S# is assigned in mint order and is never reused, renumbered, or deleted;
ROW ORDER is the flow order. A step inserted between S4 and S5 gets the next unused id (e.g. S10) and
sits in the third row. Non-sequential ids are expected — extensions, § 4's enforcement points, Signal
Log Destinations, and downstream stories all cite these ids, and renumbering would silently
invalidate every one of them (references/use-case-standard.md § Deliberate departures).

WRITING RULES (Cockburn, 3-lane-uc.md § Writing a step):
- One step = one interaction, one validation, or one state change, with its actor named.
- Actor INTENT, never UI gesture: "Parent provides the student's details: Student First Name, Student Last Name, Residence Address: line, City, Zip, State", not "Parent types into the
  name field and clicks Next". A flow written in gestures is design smuggled into a requirement.
- 3-9 steps at user-goal level. More than ~12 means this is a summary-level UC and wants splitting.
- The System column is not optional. What validates, what gets recorded, what the actor sees next.
- A step may start as one line of an outline before it earns a table row — a partially detailed UC is
  a UC at pass 2, not a defective one (Use-Case 2.0, progressive detail). -->

| Step | Actor Action | System Response & Validation |
| :--- | :--- | :--- |
| **S1** | Parent starts a grant application. | System opens a new draft application. |
| **S2** | Parent provides the school name and the amount requested. | System validates both are present. |
| **S3** | Parent submits the application. | System records it and routes it to a reviewer. |
| **S4** | Reviewer approves or rejects the application. | System records the decision and notifies the parent. |

## 3. Alternative & Exception Flows
<!-- OPTIONAL — omit the whole section when no branch has been stated. Never invent one to look
thorough; an invented failure path becomes scope the client never asked for.

A: alternative (a different route to a valid outcome). E: exception (a failure the system must
handle). Number within this UC, in mint order, permanently: A1, A2, E1, E2.

Every flow states its branch point as an S# id, its condition as a DETECTED FACT ("Card is invalid:")
never as a question ("Is the card valid?"), and how it ends: rejoins the main flow at an S#, reaches a
different success, or fails. A flow with no ending is an unfinished flow.

The other section /bigin-transform-signal writes without waiting for a human: Stage 4 Part 2 drafts a
new/changed/removed flow here directly, same run, sweeping every outstanding ## Discussion entry for
this section the same way it does for § 2. Unlike § 2, a § 3-only change does not by itself flag this
UC for review — only a § 2 change does (4-sync.md Part 2). -->

### E1: The amount is missing
* **Branch point:** S2
* **Failure condition:** The amount requested is blank.
1. System asks for the amount.
2. **Ends:** the parent stays on the draft.

## 4. Business Rules & Compliance Constraints
<!-- A MIRROR of 01-Requirements/_brs/, never the source (BABOK § 10.47: rules are captured
separately so a rule change doesn't force a use-case change). Edit the BR file; this table is
refreshed from it on every fold-in that touches it.

The one fact that lives here and nowhere else is Enforced at — which step of THIS flow the rule bites
at. Cite an S# id, or "pre-condition" / "post-condition" when it constrains the state rather than a
step. A rule this UC references but that no step enforces is either a missing step or a misfiled rule
— raise it as a question rather than leaving the cell blank.

Empty is normal for a workflow with no policy constraints. -->

| Rule | Statement (short) | Enforced at |
| :--- | :--- | :--- |
| BR-001 | If the amount requested exceeds $5,000, then a second reviewer must approve the application. | S4 |
| BR-002 | If an application is submitted, then the school name and the amount requested must both be present. | S2 |

## 5. Open Questions & Decision Log
<!-- Two lists, two jobs. Cockburn's template carries OPEN ISSUES as a first-class section; this is
that section, plus the settled history behind it.

STILL OPEN — the canonical checkbox list. This is what the status invariant counts: zero unchecked
- [ ] Q: lines here ⟺ status is not needs-clarification (`questions.md` § Open Questions ↔ status
consistency). Wording rules: `questions.md` § Open Questions wording — self-contained, plain business
language for owner: client, one decision per line.

- [ ] Q: <question> (owner: client|team) (ref: <INT-###>)
      A:

ANSWERING — this is where a reviewing BA writes, and the only place they need to. Type the answer on
that question's own A: line, in your own words; an answer written anywhere else (a comment, a line
above the question, a chat message) is not read by anything. Leave the box UNCHECKED unless the answer
fully settles the question — "we'll ask the client", "TBD after the demo", or a reply that raises a
new question is not settled, and ticking it anyway is what makes a parked use case read as
approvable. Don't edit the numbered sections to match your own answer: say "process UC-###" and the
pipeline folds every filled A: in, then comes back with the follow-ups that pass produced — or the
flow to approve when there are none (`questions.md` § Answering a question).

SETTLED — move a question here once its A: line is filled and the change is folded in. This is where
the speaker context goes: who raised it, what they said, what was decided. Append-only; never delete
a settled row, and never re-ask a question that has a row here. -->

**Still open**

- [ ] Q: Is there a maximum amount a parent may request? (owner: client) (ref: INT-001 #2)
  A:

**Decision log**

| # | Topic | Raised by / source | Decision | Date |
| :--- | :--- | :--- | :--- | :--- |

## 6. Special Requirements & Related Information
<!-- OPTIONAL, blank for most UCs. Use-Case 2.0's "special requirements that apply to the whole use
case and are often non-functional" — this vault has no NFR artifact, so a performance, volume,
availability, or compliance constraint scoped to this workflow lands here rather than being dropped.

Only what a source actually stated. Cockburn's Related Information fields are welcome when known:
Priority, Performance target, Frequency, Superordinate UC, Subordinate UC(s), channels to actors.
An unstated frequency is not a guess to make. -->

## Discussion
<!-- Staged, not-yet-applied change proposals — one entry per pending signal, cleared into the
numbered sections above once resolved (SKILL.md Stage 3 stages it). Two speeds:
- a main-flow step ("new step ...", "S# becomes:", "S# is removed because ...") or a flow ("new
  flow A#/E#:", "A#/E# becomes:", "A#/E# is removed because ...") clears into § 2/§ 3 the SAME run,
  Stage 4 Part 2 — no human wait, and swept every run regardless of which run staged it
- everything else (a rule, § 1, § 6) waits for a human and clears on a later run, Stage 1

Format:

- **<INT-###>** (staged <YYYY-MM-DD>): <quoted/tightly paraphrased signal> → proposed: <the exact
  final text this becomes, naming its destination — "new step after S4:", "S6 becomes:", "new flow
  E2:", "§ 1 Trigger becomes:">

Write the proposal as FINAL TEXT, not as a description of what to write — Stage 1 copies it in
verbatim and cannot re-derive an instruction. Never fold an entry in without the gate. -->

- **INT-002** (staged 2026-09-20): "A rejected applicant can appeal once" (grant-intake hub row #5) → proposed: new step after S4: Parent appeals a rejection once || System records the appeal and returns the application to review.
- **INT-001** (staged 2026-09-20): "Parents apply online" (grant-intake hub row #1) → proposed: § 1 Trigger becomes: The parent opens the grant application.

## Changelog
- 1.0 (2026-09-20) — created from INT-001
- 1.1 (2026-09-20) — INT-002: reviewer decision added as S4
