---
id: PRD-
type: prd
title:                  # the FEATURE, in business words — not "PRD for X", just "<Feature>"
status: draft           # draft | approved (_bigin/conventions/conventions.md § Status vocabularies).
                        # /bigin-generate-prd only ever writes draft; approved is human-only (P5).
version: 1.0
feature:                # the ONE FEATURES.md slug this PRD covers. One PRD per feature — a re-run
                        # updates it in place, never forks it.
features: []            # every slug whose UCs appear in this document, owner first (a cross-feature
                        # UC is carried in its primary_feature's PRD)
uc: []                  # UC-### ids folded into §§ 5-9 — APPROVED ONLY (P2)
pending_uc: []          # UC-### ids listed in § 10 Pending Scope — explicitly NOT this PRD's scope
brs: []                 # BR-### ids mirrored in § 7
entities: []            # EN-### ids described in § 8
pain_points: []         # PP-### ids this feature exists to resolve (§ 2)
uiux: []                # UX-### id(s) whose screens are reported in § 9
absorbed: []            # UC-<NNN>@<version> — THE staleness record (conventions.md § Absorbed).
                        # Only approved UCs that really got a capability row this run. Re-stamped
                        # WHOLE every run, never appended to.
design_absorbed: []     # UX-<NNN>@<version> for each design reported in § 9. Same discipline.
sources: []             # INT-### ids, unioned from every UC in uc: — append-only
chain: full             # full | cr — from the FEATURES.md row's Status (conventions.md
                        # § Traceability chain). A `built` feature takes the lightweight CR chain,
                        # which SKIPS the PRD; a PRD exists here only because a human asked for one.
engine:                 # which PRD engine produced this: bmad | built-in
owner: team
updated:
---

# `PRD-<NNN> <Feature>`

> [!summary]- Summary
> <2-3 sentences: what this feature lets the business do, for whom, and what changes once it ships.
> Plain business language — a sponsor reads this and nothing else.>

<!-- WHAT THIS DOCUMENT IS, AND IS NOT.

A business-flow PRD. It states what the business needs to happen, for whom, in what order, under
which policies — and what the screens already look like. It is NOT a technical specification: no
API, no schema, no field type, no framework, no endpoint, no table, no architecture, no sizing.
The test (P1): a sentence a developer needs in order to implement, but a business owner cannot
confirm or deny, is in the wrong document.

Ids ARE welcome here and required in §§ 5-7 and § Traceability — this is an internal document and
traceability is the point. That is the opposite of a prototype prompt, which must carry no ids at
all (design-conventions.md D6); do not carry that rule across. The prose must still read
completely without the ids: cite them, never lean on them.

Every section: fill it from the artifacts, or write "not stated". A blank line reads as "nobody
looked"; "not stated" is a real and useful fact about the source material. Never invent a goal, a
metric, a stakeholder, or a constraint the sources did not state (P3). -->

## 1. Executive Summary
<!-- Assembled from every folded UC's § 1 Business Need / Goal, the pain points in § 2, and
_bigin/system/project.md. Dense, zero fluff, no more than a short paragraph plus the three lines
below. Never a restatement of the flows — that's § 6. -->

* **What this feature delivers:** `<the business outcome, one sentence>`
* **Who it is for:** `<the primary actor(s), as roles>`
* **Why now:** `<the stated driver — a pain point, a commitment, a deadline. "not stated" if none>`

## 2. Business Context & Problem
<!-- The problem in the client's own words. Pain points mirror 01-Requirements/PAIN-POINTS.md rows
for this feature by id — the register carries the statement, this table carries it read-only
(conventions.md § Pain Point Register). Never invent a pain point to justify a capability. -->

* **Current state, as stated:** `<how the business does this today, from the sources. "not stated">`
* **What makes it a problem:** `<cost, delay, error, risk — only as stated>`

| PP-### | Pain point (as stated) | Who feels it | Addressed by |
|--------|------------------------|--------------|--------------|

## 3. Goals & Success Measures
<!-- Business outcomes, not engineering targets. A measure the sources never stated is written as
"not stated — decision needed" and raised in § 11, never guessed at. Numbers only when a source
said the number. -->

| # | Business goal | How the business will know it worked | Stated by |
|---|---------------|--------------------------------------|-----------|

**Explicit non-goals:** `<what this feature deliberately does not try to do, as stated. "not stated">`

## 4. Actors & Stakeholders
<!-- Roles, never named people. Primary and secondary actors are lifted from each folded UC's § 1;
a sponsor or other stakeholder role comes from _bigin/system/project.md's contact tables. -->

| Actor / stakeholder | Role in this feature | Appears in |
|---------------------|----------------------|------------|

## 5. Business Capabilities
<!-- THE CAPABILITY CONTRACT. One row per approved UC folded into this PRD — the business-worded
answer to "what will the business be able to do that it cannot do today?".

One capability per UC, phrased as the actor's goal in active words ("Enrol a student in a course"),
never as a system function ("enrolment API"). `Value` is why the business wants it, from the UC's
§ 1 Business Need. Approved UCs only (P2) — anything else belongs in § 10. -->

| # | Capability | Actor | Value to the business | UC | Flow |
|---|------------|-------|-----------------------|----|------|

## 6. Business Flows
<!-- THE HEART OF THIS DOCUMENT. One block per approved UC, in the order the business experiences
them, not in id order.

Each flow is the UC's § 2 main success scenario retold as a business narrative: one line per step,
the actor's intent and what the business gets, plainly. Cite the S# so the line stays traceable,
but write the line so it reads without it. NEVER copy a UC step's System Response column verbatim
into a technical sentence — translate it ("the enrolment is recorded and the parent is notified",
not "POST /enrolments returns 201").

`Screen` is filled from § 9's inventory when a design exists — the screen the actor is on for that
step. Leave it "—" when no design covers that step yet; never invent one (P6).

Branches come from the UC's § 3. State each as the business situation that triggers it and how it
ends. Omit the branch table entirely for a UC with no § 3 — never invent a failure path. -->

### `<Capability name>` — `UC-<NNN>`
* **Trigger:** `<the business event that starts this, in plain words>`
* **Before it can start:** `<the pre-conditions that matter to the business. "none stated">`
* **Once it succeeds:** `<what is true for the business afterwards — records, notifications, money>`
* **If it is abandoned part-way:** `<the UC's failure post-condition, in business terms>`
  <!-- The most commonly skipped line here, and the one a sponsor most often has an opinion about. -->

| Step | What happens | Actor | Screen |
|------|--------------|-------|--------|

**When it goes differently**

| Situation | What the business does | How it ends | Ref |
|-----------|------------------------|-------------|-----|

## 7. Business Rules & Policies
<!-- A MIRROR of 01-Requirements/_brs/, never the source (conventions.md § ID scheme: the BR file is
the rule). Edit the BR; this table is refreshed from it on every run.

`Applies at` names the moment in the business flow the rule bites — the capability and step in
words, with the S# in brackets. A rule that no folded flow enforces is reported as a gap in § 11,
not silently dropped. -->

| BR | Policy (as stated) | Applies at | Consequence if broken |
|----|--------------------|------------|-----------------------|

## 8. Business Information
<!-- What information the business needs to keep and why — NOT a data model (P1). No field types, no
keys, no relationships-as-cardinality, no schema. One row per EN-### the folded UCs reference.

`Key facts held` is the handful of business-meaningful attributes a stakeholder would name out
loud, in their words. `Who owns it` is the role accountable for it being right. Cite the EN-### so
the real field list stays one hop away; do not reproduce it here. -->

| EN | Information | Why the business keeps it | Key facts held | Who owns it |
|----|-------------|---------------------------|----------------|-------------|

## 9. Experience & Design
<!-- What the design ALREADY says, quoted from 04-UIUX/UX-<NNN> <Feature>.md. This section reports;
it never decides (P6). No token names, no hex, no px, no component API, no layout grid — those live
in the design system and mean nothing to a business reader. A screen that does not exist in the UX
spec is not listed here, however obviously needed: that is an entry in § 11.

Omit the whole section, with one line saying so, when the feature has no UX spec yet. Never
describe screens from imagination to fill it. -->

* **Design spec:** `<UX-<NNN> <Feature>>` — `<status, and the version this PRD read>`
* **Platform:** `<web / mobile / both, as the design states it. "not stated">`
* **Design intent, as stated to us:** `<the DESIGN-PRINCIPLES rows and hub directives the design applied, in the client's own words>`

**Screens**

| Screen | What the actor does there | Serves capability |
|--------|---------------------------|-------------------|

**Journeys**

| Capability | The path through the screens | Ends on |
|------------|-----------------------------|---------|

* **Prototype:** `<where the prompts are, e.g. "both prototype prompts are ready in UX-<NNN> § Prototype Prompt">` — never restate a prompt here
* **Known design gaps:** `<one line per unchecked question on the UX spec's § 6, in business words>`

## 10. Scope & Release Framing
<!-- What this PRD commits to, and what it explicitly does not. Never invent phasing: if nothing in
the sources asked for a phased release, say the whole scope is one release rather than inventing an
MVP boundary the client never agreed to. -->

**In scope** — the capabilities in § 5, and nothing else.

**Out of scope, as stated**

| # | Out of scope | Stated by |
|---|--------------|-----------|

**Pending scope — not part of this PRD**
<!-- Every UC on this feature that is NOT approved but has a drafted main flow. It is listed so
nothing silently disappears, and excluded so this document never reads as sign-off on unapproved
scope (P2). Re-run this skill once it is approved and it moves up into §§ 5-9. -->

| UC | Goal | Status | What it is waiting on |
|----|------|--------|-----------------------|

## 11. Open Business Decisions
<!-- Every unresolved decision this PRD is exposed to, in one place, so a sponsor can clear them in
one sitting. Sourced from: each folded UC's § 5 Still open, the UX spec's § 6 questions marked as
requirement gaps, the feature hub's open ## Coverage Gaps rows (what nobody has described at all —
these block no single UC, so they reach here with every folded UC looking clean), and anything this
run found unanswerable in §§ 1-10.

This list is why status stays `draft` — a PRD with open decisions is not approvable.

A decision belongs to the artifact that owns it: answering one means going back through
/bigin-transform-signal (requirements) or /bigin-generate-design (screens), never editing this
document into agreement with itself. Wording rules: conventions.md § Open Questions wording —
self-contained, one decision per line, plain business language.

Format:
- [ ] Q: <the decision, stated so a business reader can answer it without opening another file> (owner: client|team) (ref: UC-<NNN> § 5 / UX-<NNN> § 6 / <slug> ## Coverage Gaps #<n> / PRD-<NNN>)
      A: -->

## 12. Assumptions, Dependencies & Constraints
<!-- Only what a source actually stated. An unstated dependency is not a guess to make; an assumed
one that turns out false is the most expensive kind of PRD error. Leave a subsection as
"none stated" rather than filling it. -->

* **Assumptions:** `<what this PRD takes as true without confirmation, and who assumed it>`
* **Depends on:** `<another feature, a third party, a client-side decision or data hand-over>`
* **Constraints:** `<a stated deadline, volume, compliance obligation, or channel limit>`
  <!-- From a UC's § 6 Special Requirements or the project file. -->

## Traceability
<!-- One row per capability, end to end. This is what makes the PRD auditable: a capability that
cannot fill its UC cell is unapproved scope, and a UC cell with no INT source is a requirement
nobody actually asked for. Fill every cell or write "—" (nothing exists yet), never leave blank. -->

| Capability | UC | Rules | Information | Screens | Raised in |
|------------|----|-------|-------------|---------|-----------|

## Changelog
- 1.0 (YYYY-MM-DD) — created from `UC-<NNN>@<version>`
