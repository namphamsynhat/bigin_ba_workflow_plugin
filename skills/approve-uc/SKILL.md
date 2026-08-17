---
name: approve-uc
description: Approve a use case (UC) once its open questions are resolved and its content is right. Reprocesses the UC's own live content — the human may have edited it directly while reviewing — promotes/updates any entity it references, then flips its status to `approved` so it's feature material, ready for PRD. Use once a UC is drafted (and, where enrichment runs, enriched) and the human is ready to sign off.
argument-hint: "<UC id, e.g. UC-012>"
---

# Approve UC

Marks a use case approved on the human's explicit call — the point where a reviewed requirement
becomes committed scope. `FR-###` is retired; this skill reads and writes `UC-###` directly under
`01-Requirements/_ucs/`, generating no PRD of its own (§ Reconciliation notes — PRD generation is
still **Planned**).

This is the approval gate of the extract → transform → load pipeline. A human reviewing a UC is free
to edit the file directly rather than route every change back through `/bigin-transform-signal` — this
skill's first job is to re-derive the UC's own state from whatever is on disk right now, not trust
whatever a prior run last wrote.

> **Artifact Standard:** Outputs:
>> **An approved UC** — `status: approved`, set only after the human confirms, with `version` bumped
>> and a `## Changelog` line if this run corrected anything.
>> **Entity docs kept current** — every `EN-###` this UC's steps/rules actually reference, promoted
>> from a `proposed` `ENTITIES.md` row or extended to match the UC's current content, plus
>> `ENTITIES.md` and every referencing feature hub's `## Entities` / `entities:` refreshed.
>> **A refreshed feature hub** — `## Requirement Readiness` reflecting the new status, and the Signal
>> Log rows this UC was drafted/updated from flipped to `applied`.

---

## Non-Negotiable Core Rules

* **Never approve on the user's behalf:** approval is a human decision, confirmed against a summary
  they can see.
* **Re-derive, don't trust stale state:** the human may have edited the UC directly while reviewing.
  Re-count `## 5` **Still open** before anything else — a UC with any unresolved `- [ ] Q:` line is
  `needs-clarification`, not approvable, no matter what `status` currently reads
  (§ Open Questions ↔ status consistency).
* **Entities are promoted from real references, never speculatively:** only an entity this UC's steps
  or rules actually cite gets a document or an update (§ Entity Data Model). Most UCs touch none —
  skip cleanly when that's true.
* **Vault-wide registers, one write at a time:** `ENTITIES.md` and `01-Requirements/_entities/` are
  shared across every feature. Approving several UCs in one sitting still writes these sequentially,
  never in parallel (same discipline as `/bigin-transform-signal` Stage 4).
* **No PRD is generated here.** `approved` means the UC is feature material (§ Feature material) —
  a human, or a future PRD stage, takes it from there. Writing a `PRD.md` section is out of scope for
  this skill.

---

## Precondition — check this first

Missing `_bigin/conventions/conventions.md` or `_bigin/templates/` → stop, say `/bigin-new-project`
must run first.

`$ARGUMENTS` names a `UC-###` that doesn't exist under `01-Requirements/_ucs/` → say so and stop; don't
guess which file was meant.

With no id given, list every UC not already `approved`/`consolidated`/`removed` as candidates (grouped
by feature) and ask which one.

## Input

Read `01-Requirements/_ucs/UC-<NNN> <Title>.md` for the id in `$ARGUMENTS`. Read its `primary_feature`'s
hub at `01-Requirements/_features/<slug>.md`, and `01-Requirements/ENTITIES.md`.

## What to do

* **Goal:** convert a reviewed use case into committed scope, ready to hand to whatever comes next
  (design, and eventually a PRD stage), while catching any drift the human's own edit introduced.
* **Action:**
  1. **Reprocess the UC.** Treat the file's current content as authoritative, not whatever a prior run
     last computed:
     * Re-count `## 5` **Still open**. Any unresolved `- [ ] Q:` line → tell the user which question(s)
       are still open and stop; don't ask to approve a UC with an open question
       (§ Open Questions ↔ status consistency's invariant — this holds regardless of what `status`
       currently reads).
     * Check `## 4`'s rule mirror against each cited `BR-###`'s current statement and enforcement
       point. `## 4` is a read-only mirror (§ Use Case) — if a human edit left it drifted from the BR
       file, refresh the mirror to match; never invent a rule that isn't already in a `BR-###` file.
     * If `status` isn't `enriched` yet, note that `/enrich-feature` hasn't (or can't yet) run against
       this UC and ask whether to proceed anyway — enrichment is expected, not enforced.
  2. **Process entities.** For every entity this UC's `## 2`/`## 3` steps or `## 4` rules actually
     reference — its `entities: []` list, plus anything a human edit introduced that isn't listed yet:
     * Match the entity against `01-Requirements/ENTITIES.md`. A `proposed` row this UC references,
       with no `EN-###` document yet, gets promoted now: instantiate
       `_bigin/templates/entity.md` as `01-Requirements/_entities/EN-<NNN> <Entity>.md`, id from a
       `Grep` scan of `01-Requirements/_entities/` (its own sequence — never a bash `grep`/`awk`
       pipeline, § ID scheme).
     * An entity that already has an `EN-###` doc gets its `## Fields`/`## Relationships` extended
       with whatever this UC's current content adds, each row's `Source` citing this UC's `S#`/rule.
       A field that contradicts what's already recorded is a question for the human, never a silent
       overwrite.
     * Add this UC's feature slug(s) to the entity's `features:` list if missing, and add
       `EN-### <Name> (<status>)` to every referencing feature hub's `## Entities` section plus its
       `entities:` frontmatter.
     * Update this UC's own `entities: []` frontmatter to the final list.
     * An entity still at `status: proposed`/`draft` and settled enough for this review — no open
       question against its fields, nothing contradicted this run — can move to `approved` per
       `_bigin/templates/entity.md`'s own vocabulary ("human confirmed at a UC/BR review gate").
       Include it in the confirmation in step 3 rather than flipping it silently: an entity shared
       across features may still be unsettled from another UC's point of view.
     * Most UCs reference no new or changed entity. Skip this step cleanly when that's true — never
       promote or extend one speculatively.
  3. **Show a short summary** — the goal, main-flow step count, any drift this run corrected in `## 4`,
     entities touched (and any recommended for `approved`) — and confirm the user intends to approve.
  4. **On confirmation:** set `status: approved` on the UC, bump `version`, and add one `## Changelog`
     line noting the approval and anything this run corrected. Flip any confirmed entity to `approved`
     in the same pass.
  5. **Refresh the owning feature hub(s).** For every feature in this UC's `features:` list, update
     `## Requirement Readiness` to reflect `approved`, and flip this UC's Signal Log rows to `applied`
     if not already (§ Feature Hub — Maintenance contract).
  6. **Confirm and point to next.** Tell the user the UC is ready for PRD — `/bigin-generate-design` can
     run off it now (it doesn't wait on approval), and a PRD/epics stage, once one exists, picks up
     `approved` UCs as feature material (§ Feature material).
