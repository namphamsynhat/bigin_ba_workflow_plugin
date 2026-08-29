---
type: feature-hub
feature:
name:           # display name — mirrors the FEATURES.md row's Feature column. Source of truth
                # for the command-center plugin (`feature-hub.md` § Feature Map format, conventions.md) — the
                # plugin reads Slug/Feature/UC/Code areas/Sources from this frontmatter, not by
                # parsing FEATURES.md's table.
status:
uc: []          # UC-### id(s) this feature owns OR participates in — populated by
                # /bigin-transform-signal. A UC can span features, so the same id appears on
                # several hubs; ## Use Cases below says which of them owns it.
br: []          # BR-### id(s) this feature owns (including feature-level BRs not tied to
                # one UC) — populated by /bigin-transform-signal
fr: []          # RETIRED. Pre-UC FR-### id(s), kept so old ids still resolve. Nothing writes
                # here any more (`core.md` § ID scheme).
code_areas: []  # mirrors the FEATURES.md row's Code areas column — populated for
                # project_mode: ongoing only, blank/omitted otherwise
sources: []     # mirrors the FEATURES.md row's Sources column — INT-###/document ids/paths
prd:
epics: []
stories: []
uiux:
entities: []    # EN-### id(s) this feature's UC(s)/BR(s) reference — [] until one exists
updated:
---

# `<Feature Name>`

`<one-line description — what this feature is, in plain language>`

## Notes / History
<!-- Append-only, dated bullets, oldest first — the readable "story" of this feature (why it
exists, what each meeting/CR round added, what got resolved). This is where /bigin-transform-signal
and /enrich-feature write narrative content — never into FEATURES.md's Notes cell, which is a
one-line pointer only (`feature-hub.md` § Feature Map format). The Signal Log below stays the
atomic per-signal trace table; this section is the chronological narrative a human reads
top-to-bottom. -->

## Signal Log
<!-- One row per FUNCTIONAL THEME, in the order it landed — not one row per signal. Signals from the same INT note describing the same rule, flow, or decision file as a single row: Signal reads "**<Theme>** — <detail>; <detail>; <detail>" (every claim kept as its own clause, nothing summarized away), Type joins the member types with " + ", and Source cites the note row numbers it covers, e.g. "INT-014 #3, #5, #7 — Jane Doe 2026-08-05". Those numbers are the traceability back to the note's flat ## Extracted signals table, which stays the raw one-row-per-signal record. Row counts between the two are not meant to match. Signals never merge across notes (a continuing theme cites the older row as "extends #<n>"), across Status (only new consolidates — question/conflict/rejected stay 1:1), across the design/behaviour boundary, or when they contradict each other. A theme of one is normal. Rules: _bigin/stages/extract/3-filing.md § Step 2 — File to the Feature Hub.
Never renumber or delete a row — a row's # is permanent, like a BR-### number. When a later signal conflicts with or supersedes an earlier one, add the NEW row and update the OLD row's Status + Notes to point at it; don't rewrite history in place.
Status values: new (just landed) · held (anchored to feature, no UC yet — resting state pre-UC; once a UC exists, a new signal moves straight to staged instead, regardless of the UC's status — hard rule 7, approval no longer freezes it) · staged (proposed change sitting in a UC's or BR's ## Discussion, not yet applied) · applied (folded into UC/BR content) · question (the signal IS an open question, tracked until answered) · conflict (contradicts an earlier row — needs human resolution) · superseded (an older row overridden by a resolved conflict/newer decision) · rejected (explicitly decided out of scope).
"Processed" = applied | superseded | rejected. "Not yet processed" = new | held | staged | question | conflict. -->

| # | Signal | Type | Source | Status | Destination | Notes |
|---|--------|------|--------|--------|--------------|-------|

## Use Cases
<!-- One row per UC-### in this hub's uc: list. A UC is the reviewable requirement artifact: one user
goal, its flow, its branches, its rules mirror, its open questions (`use-case.md` § Use Case).

Role says whether this feature OWNS the UC (it is the UC's primary_feature — the only feature whose
Stage 3 subagent may write that file) or PARTICIPATES in it (a step of the flow lands here). A
cross-feature UC appears on every participating hub with the same id; that is the point of the
artifact, not duplication to fix.

No step counts or step ranges here — the UC file is the only place the flow is written out. The
retired SCN-### register carried "(step 2 of 4)" on each hub and it went stale silently every time a
step was inserted. Refreshed by /bigin-transform-signal Stage 4. -->

| UC | Goal | Role | Status |
|----|------|------|--------|

## Coverage Gaps
<!-- What this feature's use-case set does NOT account for — the half a conflict check can't see.
Written by /bigin-transform-signal's coverage pass (_bigin/stages/transform/4b-coverage.md), which
reads the feature's whole UC set as a SET and tests it against six lenses: entity lifecycle (created,
found, corrected, state-changed, retired, merged), dangling ## 1 pre-conditions, actors with no goal
of their own, the feature's own stated purpose and open PP-### rows, data a step or rule reads that
no UC writes, and a BR-### no UC's ## 4 enforces.
A gap is a FINDING, never a work order: the Gap cell states what nobody has described, in plain
business language a client can answer out loud, and NEVER proposes the answer. It is not a UC's open
question and must never park a UC that is otherwise ready — a gap is feature-level by nature.
# is permanent, append-only, never renumbered or deleted — same discipline as the Signal Log.
Status: open (nobody has answered) · answered (a human said what should happen; it still has to
arrive through /bigin-intake before it can become content) · covered (a UC now covers it — cite the
id in Notes) · rejected (explicitly out of scope — cite who decided). Open and answered rows mirror
into ## Open Questions / Gates, same sentence. Empty is a real and good result for a feature whose
set adds up; a MISSING section means nobody has checked yet. -->

| # | Gap | Lens | Raised | Status | Notes |
|---|-----|------|--------|--------|-------|

## Requirement Readiness
<!-- A refreshed snapshot for orientation — NOT the authoritative gate. The authoritative gate is always the UC/BR's own frontmatter status, checked live by /bigin-transform-signal, /prd, /uiux at run time (see `feature-hub.md` § Feature material). This table just saves a human (or agent) from opening every UC/BR to see what's ready. An approved UC can still receive new signals later (hard rule 7 — approval doesn't freeze it); when that happens it's staged and re-applied via /bigin-transform-signal's normal discussion round, not held in a separate backlog — note it here the same way as any other pending change (e.g. "approved — 2 new signal(s) since approval, not yet run through /bigin-transform-signal"). -->

| Artifact | Status | Ready for next step? | Blocking |
|----------|--------|------------------------|----------|
| — no UC/BR yet — | — | No | Human decision: brainstorm now / draft the use case directly / hold |

## Related Documents
<!-- UC(s)'/BR(s)' attachments: list, vault-relative paths -->

## Domain Research
<!-- One entry per domain-research run for this feature. The first lands automatically, the run
this hub is first created — /extract-signal § Step 2a (_bigin/stages/extract/3-filing.md)
researches the feature's stated scope and appends the finding here, plus a full report at
01-Requirements/_research/<slug>/domain-research.md. Refreshable later on demand via
/enrich-feature (e.g. scope changed materially, or the automatic run failed/was skipped). Never
hand-authored.
Entry format: `- **<date>** — <topic> — <one-line summary of key findings> ([full report](<path>))` -->

## Business Scenarios
<!-- RETIRED — kept only so a pre-UC hub still parses. Cross-feature flows are now use cases: one
UC-### whose features: lists every slug it touches, listed in ## Use Cases above (`registers.md` § Business Scenarios (retired)). Leave any existing SCN-### pointers in place, marked superseded by
the UC that absorbed them; never add a new one. Omit this section entirely on a new hub. -->

## Entities
<!-- Every EN-### this feature's UC(s)/BR(s) reference, with each entity's current status
(`registers.md` § Entity Data Model), e.g. "- EN-001 Vendor (approved)". Empty until a signal
defines/extends an entity's fields. An entity shared with other features shows the same id on
each of their hubs — expected, not duplication to fix. Refreshed by /bigin-transform-signal and
/enrich-feature whenever they draft/update an EN-###. -->

## Pain Points
<!-- Mirror of this feature's rows from 01-Requirements/PAIN-POINTS.md (registers.md § Pain
Point Register): PP-### | Statement | Status | Proposed solution | Resolved by. Empty until a
[pain-point] signal anchors here — can be populated even before any UC exists. Refreshed by
/bigin-transform-signal/`/enrich-feature` (creation/updates) and /prd (Resolved by backfill once
EP-###/US-### exist). -->

| PP-### | Statement | Status | Proposed solution | Resolved by |
|--------|-----------|--------|--------------------|--------------|

## PRD
<!-- link + status, or "not started." Refreshed by /bigin-generate-prd together with the `prd:`
frontmatter field, one PRD per feature (`core.md` § ID scheme):
  [[PRD-<NNN> <Feature>]] — draft, N capabilities, M pending
`N capabilities` is how many approved UCs the PRD folded; `M pending` is how many of this feature's
UCs are listed in its § 10 Pending Scope because they are not approved yet. Both counts come from
the PRD file, not from this hub's own tables. -->

## Epics & Stories
<!-- table: id | title | status -->

## Design Directives
<!-- Feature-scoped presentation directives — look, layout, tone, interaction feel — routed here by
/bigin-transform-signal's design lane (_bigin/stages/transform/3-lane-design.md).
These reach /bigin-generate-design WITHOUT passing through a UC, a PRD, or an approval gate
(`use-case.md` § Traceability chain, the Design chain), because a presentation-only statement has
no functional scope for a PRD to carry. A directive that changes what the system DOES is a
misroute — it belongs in a UC step.
Durable, cross-cutting preferences go to 01-Requirements/DESIGN-PRINCIPLES.md instead (or as well);
this section is only for what is scoped to this feature.
# is permanent, never renumbered or deleted — same discipline as the Signal Log. Status: open (not
yet in a prototype) · reflected (set by /bigin-generate-design) · superseded (Notes points at the row
that replaced it) · conflict (contradicts an earlier directive, awaiting a human). -->

| # | Directive | Source | Status | Notes |
|---|-----------|--------|--------|-------|

## UX Spec
<!-- link + status, or "not started." -->

## Open Questions / Gates
<!-- aggregated from every UC/BR on this feature (their ## 5 Still open / ## Open Questions lines) and this note's Signal Log (status = question or conflict) — what's actually blocking progress right now -->

## Changelog
- (YYYY-MM-DD) — hub created


