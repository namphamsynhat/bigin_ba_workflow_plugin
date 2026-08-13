---
type: feature-hub
feature:
name:           # display name — mirrors the FEATURES.md row's Feature column. Source of truth
                # for the command-center plugin (§ Feature Map format, conventions.md) — the
                # plugin reads Slug/Feature/FR/Code areas/Sources from this frontmatter, not by
                # parsing FEATURES.md's table.
status:
fr: []          # FR-### id(s) this feature owns — populated by /bigin-transform-signal
br: []          # BR-### id(s) this feature owns (including feature-level BRs not tied to
                # one FR) — populated by /bigin-transform-signal
code_areas: []  # mirrors the FEATURES.md row's Code areas column — populated for
                # project_mode: ongoing only, blank/omitted otherwise
sources: []     # mirrors the FEATURES.md row's Sources column — INT-###/document ids/paths
prd:
epics: []
stories: []
uiux:
entities: []    # EN-### id(s) this feature's FR(s) reference — [] until one exists
updated:
---

# <Feature Name>

<one-line description — what this feature is, in plain language>

## Notes / History
<!-- Append-only, dated bullets, oldest first — the readable "story" of this feature (why it
exists, what each meeting/CR round added, what got resolved). This is where /bigin-transform-signal
and /enrich-feature write narrative content — never into FEATURES.md's Notes cell, which is a
one-line pointer only (conventions.md § Feature Map format). The Signal Log below stays the
atomic per-signal trace table; this section is the chronological narrative a human reads
top-to-bottom. -->

## Signal Log
<!-- One row per FUNCTIONAL THEME, in the order it landed — not one row per signal. Signals from the same INT note describing the same rule, flow, or decision file as a single row: Signal reads "**<Theme>** — <detail>; <detail>; <detail>" (every claim kept as its own clause, nothing summarized away), Type joins the member types with " + ", and Source cites the note row numbers it covers, e.g. "INT-014 #3, #5, #7 — Jane Doe 2026-08-05". Those numbers are the traceability back to the note's flat ## Extracted signals table, which stays the raw one-row-per-signal record. Row counts between the two are not meant to match. Signals never merge across notes (a continuing theme cites the older row as "extends #<n>"), across Status (only new consolidates — question/conflict/rejected stay 1:1), across the design/behaviour boundary, or when they contradict each other. A theme of one is normal. Rules: _bigin/stages/extract/2-extraction.md § Consolidating into themed hub rows.
Never renumber or delete a row — a row's # is permanent, like a BR-### number. When a later signal conflicts with or supersedes an earlier one, add the NEW row and update the OLD row's Status + Notes to point at it; don't rewrite history in place.
Status values: new (just landed) · held (anchored to feature, no FR yet — resting state pre-FR; once an FR exists, a new signal moves straight to staged instead, regardless of the FR's status — hard rule 7, approval no longer freezes it) · staged (proposed change sitting in an FR's ## Discussion, not yet applied) · applied (folded into FR content) · question (the signal IS an open question, tracked until answered) · conflict (contradicts an earlier row — needs human resolution) · superseded (an older row overridden by a resolved conflict/newer decision) · rejected (explicitly decided out of scope).
"Processed" = applied | superseded | rejected. "Not yet processed" = new | held | staged | question | conflict. -->

| # | Signal | Type | Source | Status | Destination | Notes |
|---|--------|------|--------|--------|--------------|-------|

## Requirement Readiness
<!-- A refreshed snapshot for orientation — NOT the authoritative gate. The authoritative gate is always the FR/BR's own frontmatter status, checked live by /bigin-transform-signal, /prd, /uiux at run time (see conventions.md § Feature material). This table just saves a human (or agent) from opening every FR/BR to see what's ready. An approved FR can still receive new signals later (hard rule 7 — approval doesn't freeze it); when that happens it's staged and re-applied via /bigin-transform-signal's normal discussion round, not held in a separate backlog — note it here the same way as any other pending change (e.g. "approved — 2 new signal(s) since approval, not yet run through /bigin-transform-signal"). -->

| Artifact | Status | Ready for next step? | Blocking |
|----------|--------|------------------------|----------|
| — no FR/BR yet — | — | No | Human decision: brainstorm now / draft FR directly / hold |

## Related Documents
<!-- FR(s)'/BR(s)' attachments: list, vault-relative paths -->

## Domain Research
<!-- One entry per domain-research run for this feature. Appended by /enrich-feature (step 3,
Phase 2.5) only when the feature's enrichment needed external grounding (regulatory/compliance
facts, a named third-party platform/API's real behavior, industry-standard practice) — never
hand-authored, and empty for most features, since most enrichment needs nothing external.
Entry format: `- **<date>** — <topic> — <one-line summary of key findings> ([full report](<path>))` -->

## Business Scenarios
<!-- Every SCN-### this feature participates in, and this feature's step number within it, e.g.
"- SCN-001 Scholarship switch → wallet adjustment → notification (step 2 of 4)". Empty for most
features — only populated when a signal's flow genuinely crosses feature boundaries
(conventions.md § Business Scenarios). Refreshed by /bigin-transform-signal (creation/update at a
cross-feature discussion round) and /prd (citation + backfill once this feature's EP/US ids exist). -->

## Entities
<!-- Every EN-### this feature's FR(s)/BR(s) reference, with each entity's current status
(conventions.md § Entity Data Model), e.g. "- EN-001 Vendor (approved)". Empty until a signal
defines/extends an entity's fields. An entity shared with other features shows the same id on
each of their hubs — expected, not duplication to fix. Refreshed by /bigin-transform-signal and
/enrich-feature whenever they draft/update an EN-###. -->

## Pain Points
<!-- Mirror of this feature's rows from 01-Requirements/PAIN-POINTS.md (conventions.md § Pain
Point Register): PP-### | Statement | Status | Proposed solution | Resolved by. Empty until a
[pain-point] signal anchors here — can be populated even before any FR exists. Refreshed by
/bigin-transform-signal/`/enrich-feature` (creation/updates) and /prd (Resolved by backfill once
EP-###/US-### exist). -->

| PP-### | Statement | Status | Proposed solution | Resolved by |
|--------|-----------|--------|--------------------|--------------|

## PRD
<!-- link + status, or "not started." -->

## Epics & Stories
<!-- table: id | title | status -->

## Design Directives
<!-- Feature-scoped presentation directives — look, layout, tone, interaction feel — routed here by
/bigin-transform-signal's design lane (_bigin/stages/transform/3-lane-design.md).
These reach /prototype-design WITHOUT passing through an FR, a PRD, or an approval gate
(conventions.md § Traceability chain, the Design chain), because a presentation-only statement has
no functional scope for a PRD to carry. A directive that changes what the system DOES is a
misroute — it belongs in an FR.
Durable, cross-cutting preferences go to 01-Requirements/DESIGN-PRINCIPLES.md instead (or as well);
this section is only for what is scoped to this feature.
# is permanent, never renumbered or deleted — same discipline as the Signal Log. Status: open (not
yet in a prototype) · reflected (set by /prototype-design) · superseded (Notes points at the row
that replaced it) · conflict (contradicts an earlier directive, awaiting a human). -->

| # | Directive | Source | Status | Notes |
|---|-----------|--------|--------|-------|

## UX Spec
<!-- link + status, or "not started." -->

## Open Questions / Gates
<!-- aggregated from the FR and this note's Signal Log (status = question or conflict) — what's actually blocking progress right now -->

## Changelog
- (YYYY-MM-DD) — hub created


