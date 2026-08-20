---
id: UX-
type: uiux
title:                  # "<Feature> screens"
status: draft           # draft | needs-clarification | accepted | superseded
                        # (_bigin/conventions/design-conventions.md § Design status vocabulary).
                        # /bigin-generate-design only ever writes draft/needs-clarification;
                        # accepted is human-only (D5).
version: 1.0
feature:                # the ONE FEATURES.md slug that OWNS this spec. One UX spec per feature —
                        # a re-run updates it in place, never forks it.
features: []            # every slug these screens touch, owner first (a cross-feature UC is
                        # designed here, in its primary_feature's spec)
uc: []                  # UC-### id(s) designed here
brs: []                 # BR-### id(s) that produced a state or a validation
entities: []            # EN-### id(s) the screens render fields from
sources: []             # UC-###/BR-###/EN-### ids + DESIGN-PRINCIPLES row #s + hub directive #s
absorbed: []            # UC-<NNN>@<version> — THE staleness record. Only UCs that really got
                        # screens this run. Re-stamped WHOLE every run (§ Staleness).
design_system:          # the {tokens_file} version these screens were specced against
nav_map:                # the {nav_map_file} version these screens were specced against
engine:                 # which design engine produced this: wds | figma | <plugin> | built-in
relationship_model: none  # none | modelled — set by Stage 3 Part 4b's trigger test, verified in
                        # Stage 5 (check 10). `modelled` REQUIRES a filled ## 7; `none` requires
                        # ## 7 to be absent or empty. An empty ## 7 with `modelled` reads as
                        # "considered, nothing found" when nobody looked
                        # (design-conventions.md § The relationship model).
updated:
---

# `UX-<NNN> <Feature>` screens

## 1. Design Brief
<!-- Assembled in Stage 3 Part 1. Never invented: every line traces to something already written. -->

* **Users:** `<the actors from each UC's § 1 — roles, never named people>`
* **Platform:** `<web / mobile / both — only if a UC, a directive, or a principle says so>`
* **Principles applied:** `<DESIGN-PRINCIPLES row # — the principle, in the client's words>`
* **Directives applied:** `<hub ## Design Directives row # — the directive>`
* **Known gaps:** `<one line per open question already on a UC's § 5, or per entity still proposed/draft>`
  <!-- These are gaps the screens work around, not gaps to guess at. -->

## 2. Screen Inventory
<!-- One row per screen. `Serves` is the step id(s) the screen delivers — every S# must exist in
that UC and not be removed. Two UCs landing on the same place share ONE row. -->

| Screen | Purpose | Serves | Entities | Key actions |
|--------|---------|--------|----------|-------------|

## 3. Screen Specs
<!-- One block per inventory row. SEMANTIC STRUCTURE ONLY: token names, never values (D2). Every
element carries what grounds it — a UC step, a BR, an entity field, an existing pattern, or a
directive (D3). An element grounded in nothing is a question in § 6, not a guess. -->

### `<Screen name>`

* **Purpose:** `<one line>`
* **Serves:** `UC-<NNN> S<n>, S<n>`
* **Regions:** `<header / nav / main / aside / footer — semantic elements, not a pixel layout>`

| Element | Content / copy | Token(s) | Field | Grounded by |
|---------|----------------|----------|-------|-------------|

**States**

| State | Trigger | What the user sees | Grounded by |
|-------|---------|--------------------|-------------|

**Interactions**

| Control | Does | Goes to |
|---------|------|---------|

## 4. Flows
<!-- Per UC: entry → screens in order → the success end and each failure end. One line per step.
Mirrors the UC's flow; never restates its step text. Omit the whole section on a design-only
feature (no UC). -->

### `UC-<NNN> <goal>`
* **Entry:** `<the trigger, in plain words>`
* **Path:** `<Screen>` → `<Screen>` → `<Screen>`
* **Success:** `<what the user is left with>`
* **Failures:** `<exception>` → `<screen/state the user is left on>`

## 5. Design System Usage
<!-- What these screens take from 04-UIUX/_design-system/, and what they added to it. The feature
references the shared system; it never forks it. -->

* **Design system version:** `<version>`
* **Tokens used:** `<name, name, …>`
* **Components used:** `<name, name, …>`
* **Added this run:** `<token/component — why nothing existing fitted>`
* **Nav map version:** `<version>`
* **Nav entries added:** `<id (e.g. settings.team) — label — screen, or "none — reached only via another screen">`

## 6. Open Questions
<!-- The canonical list. Zero unchecked lines ⟺ status is not needs-clarification
(design-conventions.md § Design status vocabulary). Mirrored on the hub's ## Open Questions / Gates
with the SAME sentence. Never re-ask a question already open on a UC's § 5.
Mark a question whose answer would change what the SYSTEM DOES as a requirement gap — it is
/bigin-transform-signal's to resolve, never this stage's.

Format:
- [ ] Q: <self-contained question, plain business language> (owner: client|team) (ref: UX-<NNN>)
      A: -->

## 7. Relationship Model
<!-- CONDITIONAL. Delete this whole section unless the feature passed the relationship trigger
(_bigin/stages/design/3-screens.md Part 4b) — an empty ## 7 claims the relationship was considered.
Read design-conventions.md § The relationship model first.

This section describes the relationship the requirements ALREADY imply. It never discovers that the
product needs memory, autonomy, or a dashboard (D7). Expect more requirement gaps here than rows:
a UC almost never states an autonomy ceiling, a retention rule, or who owns the memory. Every gap
goes in § 6 marked as a requirement gap and belongs to /bigin-transform-signal — never to a UC edit.
-->

### Relationship Context
<!-- One line each, each grounded or dropped. "Not stated" is a legitimate value and becomes a
requirement gap in § 6 — never a plausible number. -->

| Aspect | This feature | Grounded by |
|--------|--------------|-------------|
| Expected duration | `<how long a user stays in this relationship>` | |
| Interaction frequency | `<daily / weekly / sporadic>` | |
| Autonomy ceiling | `<the MOST the agent may do unprompted — from a BR, never assumed>` | |
| Memory sensitivity | `<what would be harmful to remember, per a rule or a stated preference>` | |

### Memory Architecture
<!-- What the agent carries between sessions. EVERY row cites an EN-### field: a system cannot
remember what nothing stores, so a row with no field behind it is a requirement gap, not a design
row. `Who controls it` is who may see, correct, or clear it — from a BR or the UC's actors. -->

| What it remembers | Entity field | Surfaced on | Who controls it | Grounded by |
|-------------------|--------------|-------------|-----------------|-------------|

### Trust Map
<!-- The longitudinal counterpart to § 3's within-session States. Per screen or per agent decision:
what the agent SHOWS versus what it DOES at each stage, and how a user corrects it. Only fill a
stage a BR actually grants (D7) — an ungranted stage 3 is a requirement gap, not a design choice. -->

| Screen / decision | Stage 1 — transparent | Stage 2 — selective | Stage 3 — autonomous | Correction path | Grounded by |
|-------------------|----------------------|---------------------|----------------------|-----------------|-------------|

### Proposed Measures
<!-- At most THREE. Owner: team, always. A measure never licenses a screen, a field, or an event to
track — instrumentation is behaviour. Not a requirement, not a target, not a dashboard. -->

| Measure | What would be observed | Which row above it tests |
|---------|------------------------|--------------------------|

## Prototype Prompt — Claude design
<!-- Self-contained (D6): no UC-/BR-/EN-/PP-/UX-/INT-/PRD- id, no step id, anywhere below.
Built in Stage 4 from these screens plus the design system's real values. -->

## Prototype Prompt — Figma Make
<!-- Same screens, same tokens, same copy as the block above — addressed to a design tool
(frames, components, variants) instead of a builder. Self-contained (D6). -->

## Changelog
- 1.0 (YYYY-MM-DD) — created from `UC-<NNN>@<version>`
