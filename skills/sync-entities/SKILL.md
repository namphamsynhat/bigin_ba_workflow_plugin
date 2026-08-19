---
name: sync-entities
description: Promote and update the entities an approved use case references, and refresh the feature hub(s) that UC belongs to — the vault-wide bookkeeping `/approve-uc` no longer does inline. Run with no argument to drain every UC still waiting (`status: approved`, `synced: false`), or name one UC to process just it. Use whenever convenient after one or more approvals — at the end of a review session, before anything that needs current entity data, or any time in between.
argument-hint: "[UC id, e.g. UC-012 — omit to process every UC still waiting on sync]"
---

# Sync Entities

Does the vault-wide bookkeeping that used to happen inline inside `/approve-uc`: promotes/extends the
entities an approved UC references into their own `EN-###` documents, keeps `ENTITIES.md` current, and
refreshes each affected feature hub's `## Requirement Readiness`, `## Entities`/`entities:`, and Signal
Log rows. Splitting this out means a human reviewing and approving several UCs in one sitting is never
waiting on a shared-file write between one UC and the next — `/approve-uc` only ever touches the UC
itself; this skill catches up everything the approval implied, on its own schedule.

> **Artifact Standard:** Outputs:
>> **Entity docs kept current** — every `EN-###` a processed UC's steps/rules actually reference,
>> promoted from a `proposed` `ENTITIES.md` row or extended to match the UC's current content, plus
>> `ENTITIES.md` and every referencing feature hub's `## Entities`/`entities:` refreshed.
>> **Refreshed feature hub(s)** — `## Requirement Readiness` reflecting each processed UC's current
>> status, and the Signal Log rows it was drafted/updated from flipped to `applied`.
>> **`synced: true`** on every UC this run processed clean, so a later run doesn't reprocess it.

---

## Non-Negotiable Core Rules

* **Never approve on the user's behalf; nothing here re-litigates that.** The human already confirmed
  approval at `/approve-uc` — this skill executes the bookkeeping that follows from that decision. It
  doesn't re-show the UC or ask again, except where a genuine contradiction needs a human call
  (below).
* **Entities are promoted from real references, never speculatively:** only an entity a UC's steps or
  rules actually cite gets a document or an update (§ Entity Data Model). Most UCs touch none — skip
  cleanly when that's true, and leave nothing behind for a UC that references nothing.
* **Vault-wide registers, one write at a time:** `ENTITIES.md` and `01-Requirements/_entities/` are
  shared across every feature. Processing several UCs in one run still writes these sequentially,
  never in parallel (same discipline as `/bigin-transform-signal` Stage 4) — one UC's entity writes
  land fully before the next UC's begin.
* **A contradiction is a question, never a silent overwrite:** a field a UC's current content
  describes differently from what's already recorded on its `EN-###` doc stops that UC's entity
  processing and raises the conflict to the human — it does not fail the whole run. Finish every other
  queued UC, then report the conflict alongside the rest of the summary.
* **Skip a UC this run can't safely finish, don't half-write it.** If a UC named directly in
  `$ARGUMENTS` isn't `status: approved`, say so and stop for that UC rather than syncing a UC that
  hasn't actually been approved.

---

## Precondition — check this first

Missing `_bigin/conventions/conventions.md` or `_bigin/templates/` → stop, say `/bigin-new-project`
must run first.

Then run `_bigin/conventions/conventions.md` § Workspace version check — one `Grep` of
`_bigin/system/project.md` against the installed plugin's version, compared as semver. Behind → warn and
recommend `/bigin-upgrade-project`; **ahead → stop**.

**Model:** this skill is bookkeeping against a settled decision — promote what an approved UC actually
cites, refresh the mirrors. Run it, and anything it dispatches, on `sonnet` rather than inheriting a
higher session default; nothing here decides scope, routing, or wording.

`$ARGUMENTS` names a `UC-###` that doesn't exist under `01-Requirements/_ucs/` → say so and stop; don't
guess which file was meant. Named but not `status: approved` → say so and stop; this skill only
processes approved UCs.

With no id given, scan `01-Requirements/_ucs/` for every UC at `status: approved` with `synced: false`
(or the field missing on a UC approved before this field existed — treat that the same as `false` only
if its `entities:`/hub bookkeeping genuinely looks stale; otherwise leave it, since older approvals did
this work inline already). No candidates → say so and stop; nothing is pending.

## Input

For each UC this run processes: read `01-Requirements/_ucs/UC-<NNN> <Title>.md`, its
`primary_feature`'s (and every other listed feature's) hub at `01-Requirements/_features/<slug>.md`,
and `01-Requirements/ENTITIES.md`.

## What to do

* **Goal:** catch up every piece of vault-wide state an approval implied, for every UC still waiting,
  without re-opening the approval decision itself.
* **Action**, one queued UC at a time, in order (never parallel — the discipline this whole skill
  exists to preserve):
  1. **Process entities.** For every entity this UC's `## 2`/`## 3` steps or `## 4` rules actually
     reference — its `entities: []` list, plus anything a human edit introduced that isn't listed yet:
     * Match the entity against `01-Requirements/ENTITIES.md`. A `proposed` row this UC references,
       with no `EN-###` document yet, gets promoted now: instantiate `_bigin/templates/entity.md` as
       `01-Requirements/_entities/EN-<NNN> <Entity>.md`, id from a `Grep` scan of
       `01-Requirements/_entities/` (its own sequence — never a bash `grep`/`awk` pipeline, § ID
       scheme).
     * An entity that already has an `EN-###` doc gets its `## Fields`/`## Relationships` extended
       with whatever this UC's current content adds, each row's `Source` citing this UC's `S#`/rule.
       A field that contradicts what's already recorded is a question for the human (Core Rules) —
       raise it, skip promoting/flipping that one entity, and move on; don't overwrite it silently.
     * Add this UC's feature slug(s) to the entity's `features:` list if missing, and add
       `EN-### <Name> (<status>)` to every referencing feature hub's `## Entities` section plus its
       `entities:` frontmatter.
     * Update this UC's own `entities: []` frontmatter to the final list.
     * An entity still at `status: proposed`/`draft` and settled enough — no open question against its
       fields, nothing contradicted this run — can move to `approved` per `_bigin/templates/entity.md`'s
       own vocabulary ("human confirmed at a UC/BR review gate"): the UC's own approval already was
       that human confirmation. Include it in this run's summary rather than flipping it silently: an
       entity shared across features may still be unsettled from another UC's point of view.
     * Most UCs reference no new or changed entity. Skip this step cleanly when that's true — never
       promote or extend one speculatively.
  2. **Refresh the owning feature hub(s).** For every feature in this UC's `features:` list, update
     `## Requirement Readiness` to reflect its current status, and flip this UC's Signal Log rows to
     `applied` if not already (§ Feature Hub — Maintenance contract).
  3. **Mark it done.** Set `synced: true` on the UC once both steps above land clean for it — even if
     it referenced no entities, so a later run doesn't rescan it for nothing.
  4. **Continue to the next queued UC** rather than stopping the whole run on one contradiction.
* **Report a short summary** once every queued UC is processed: which UCs were synced clean, which
  entities were promoted/extended (and any recommended for `approved`), which hubs were refreshed, and
  any contradiction raised as a question — each tied to the specific UC and entity it came from.
