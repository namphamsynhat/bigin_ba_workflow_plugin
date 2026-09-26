---
id: UC-
type: use-case
title:              # the goal, as a short ACTIVE VERB PHRASE ("Enrol a student", not "Enrolment")
status: draft       # draft | needs-clarification | enriched | approved | consolidated | removed
                    # (`core.md` § Status vocabularies). /bigin-transform-signal
                    # only ever writes draft/needs-clarification; enriched is permanently unreachable
                    # (enrichment moved off the UC to a feature-scoped pass — nothing sets this any
                    # more), consolidated is legacy-only/unreachable, and approved/removed are human-only
                    # (hard rule 4).
version: 1.0
synced: true        # false the moment /approve-uc flips status to approved, until /sync-entities has
                    # promoted/extended any entities: [] this UC references and refreshed its feature
                    # hub(s) (`registers.md` § Entity Data Model). Meaningless at any other status —
                    # leave true.
level: user-goal    # summary | user-goal | subfunction — Cockburn's goal levels. user-goal is the
                    # default and the "boss test" level: real work, one sitting, 3-9 main-flow steps.
                    # Anything else needs a reason (3-lane-uc.md § Granularity).
scope:              # the system under design, as a black box — usually the product name
primary_feature:    # the ONE FEATURES.md slug that OWNS this file. Write-ownership, not importance:
                    # only this feature's Stage 3 subagent may write here (3-lane-uc.md § Ownership).
features: []        # every FEATURES.md slug this UC touches, primary_feature first. A UC that spans
                    # features is normal and is the point of the artifact.
brs: []             # BR-### ids governing this workflow — mirrored read-only in § 4
entities: []        # EN-### ids this UC's steps reference
pain_points: []     # PP-### ids this UC exists to resolve — ids only; the register and the hub carry
                    # the statements (`registers.md` § Pain Point Register)
sources: []         # INT-### id(s) this UC traces to — append-only, never pruned
links: []           # downstream PRD-###/EP-###/US-###/UX-### ids, once they exist
attachments: []     # vault-relative paths, copied over from every sources: INT note's own attachments
absorbs: []         # FR-### / SCN-### ids this UC took over from the pre-UC model (migration only)
owner: team
updated:
---

# `UC-<NNN> <Goal as a short active verb phrase>`

> [!summary]- Summary (retired)
> `<nothing writes this any more — enrichment moved off the UC to a feature-scoped pass
> (runtime.md § Reconciliation notes). Leave blank; omit the block entirely on a new UC.>`
> <!-- `use-case.md` § Summary block. -->

## 1. Context & Metadata
<!-- BABOK stakeholder-requirements framing. Fill every line or write "not stated" — a blank line
reads as "nobody looked", and "not stated" is a real, useful fact about the source. Never invent a
business need, a trigger, or a pre-condition the signals didn't state. -->

* **Primary Actor:** `<the role that holds the goal and initiates the flow — a role, never a named person>`
* **Secondary Actor(s):** `<other roles or systems the flow relies on: a reviewer, a payment gateway, none>`
* **Business Need / Goal:** `<the value delivered or problem solved, in the client's own words>`
* **Trigger:** `<the specific event that starts this flow — may be a time event>`
* **Pre-conditions:**
  * `<what must already be true before the flow begins>`
* **Post-conditions (success):**
  * `<the state of the world once the goal is delivered — records written, notifications sent, audit trail>`
* **Post-conditions (failure):**
  * `<what must still hold if the flow is abandoned mid-way — Cockburn's minimal guarantee>`
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
| **S1** | | |

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

### A1: `<name>`
* **Branch point:** `S<n>`
* **Condition:** `<the detected fact that makes this flow apply>`
1. `<step>`
2. **Rejoins** `S<n>` — **Ends:** `<the alternative outcome>`

### E1: `<name>`
* **Branch point:** `S<n>`
* **Failure condition:** `<the detected fact>`
1. `<step>`
2. **Ends:** `<what the actor is left with, and what § 1's failure post-condition guarantees>`

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

## Changelog
- 1.0 (YYYY-MM-DD) — created from `<INT-###>`
