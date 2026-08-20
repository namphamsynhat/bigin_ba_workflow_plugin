---
name: sync-entities
description: Promote and update the entities an approved use case references — each one written as a complete data dictionary for a real-world business object (every known field, enum values spelled out, attribute-shaped fragments absorbed into their owner) — and refresh the feature hub(s) that UC belongs to: the vault-wide bookkeeping `/approve-uc` no longer does inline. Run with no argument to drain every UC still waiting (`status: approved`, `synced: false`), or name one UC to process just it. Use whenever convenient after one or more approvals — at the end of a review session, before anything that needs current entity data, or any time in between.
argument-hint: "[UC-### to sync one · EN-### or `rebuild` to repair entity dictionaries · omit to process every UC still waiting on sync]"
---

# Sync Entities

Does the vault-wide bookkeeping that used to happen inline inside `/approve-uc`: promotes/extends the
entities an approved UC references into their own `EN-###` documents, keeps `ENTITIES.md` current, and
refreshes each affected feature hub's `## Requirement Readiness`, `## Entities`/`entities:`, and Signal
Log rows. Splitting this out means a human reviewing and approving several UCs in one sitting is never
waiting on a shared-file write between one UC and the next — `/approve-uc` only ever touches the UC
itself; this skill catches up everything the approval implied, on its own schedule.

> **Artifact Standard:** Outputs:
>> **Entity docs kept current, each one a complete data dictionary** — every `EN-###` a processed
>> UC's steps/rules actually reference, promoted from a `proposed` `ENTITIES.md` row or rebuilt to
>> carry **every** field the vault knows for that business object (not only the ones this UC touched),
>> with enum values spelled out, plus `ENTITIES.md` and every referencing feature hub's
>> `## Entities`/`entities:` refreshed.
>> **Attribute-shaped docs absorbed** — a pre-existing `EN-###` that documents one field of another
>> entity is merged into its owner and stamped `merged` + `merged_into:`, never deleted, with every
>> citation repointed.
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
* **One doc per business object; a field is never an entity.** `Application.Certification Status` is a
  row in `EN-001 Application`, not `EN-107`. Resolve every reference to its owning object before
  writing, whatever shape the register row or the UC's `entities:` list gave it, and absorb any
  attribute-shaped doc already on disk into its owner (§ Entity Data Model, A fragment already on
  disk). Minting one more fragment because a register row was named that way is the single failure
  this skill is most likely to commit, since the row reads like an entity name.
* **Write the whole dictionary, every time.** The doc is scoped to the *object*, not to the UC being
  synced: gather every field any source has stated for it and write the union. Never invent one that
  no source stated — complete over what the vault knows, gaps left visible as gaps.
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

`$ARGUMENTS` takes three shapes:

```text
UC-###     sync just that UC          → must be status: approved, else say so and stop
EN-### |   rebuild that entity's data dictionary in place, and absorb any attribute-shaped doc
rebuild      that belongs to it — no UC is synced and no `synced:` flag moves (§ Rebuild mode)
(omitted)  drain every UC still waiting
```

A `UC-###` that doesn't exist under `01-Requirements/_ucs/`, or an `EN-###` with no doc under
`01-Requirements/_entities/` → say so and stop; don't guess which file was meant. A `UC-###` named but
not `status: approved` → say so and stop; this skill only processes approved UCs.

With no id given, scan `01-Requirements/_ucs/` for every UC at `status: approved` with `synced: false`
(or the field missing on a UC approved before this field existed — treat that the same as `false` only
if its `entities:`/hub bookkeeping genuinely looks stale; otherwise leave it, since older approvals did
this work inline already). No candidates → say so and stop; nothing is pending.

## Input

For each UC this run processes: read `01-Requirements/_ucs/UC-<NNN> <Title>.md`, its
`primary_feature`'s (and every other listed feature's) hub at `01-Requirements/_features/<slug>.md`,
and `01-Requirements/ENTITIES.md`. For each entity it touches: that entity's own doc under
`01-Requirements/_entities/`, plus a `Grep` of `01-Requirements/_entities/` for an attribute-shaped
sibling and of `{uc_dir}`/`{br_dir}` for every other artifact stating a field on it — greps, not whole
reads, since the point is to find the field statements, not to load the vault.

## What to do

* **Goal:** catch up every piece of vault-wide state an approval implied, for every UC still waiting,
  without re-opening the approval decision itself.
* **Action**, one queued UC at a time, in order (never parallel — the discipline this whole skill
  exists to preserve):
  1. **Process entities.** For every entity this UC's `## 2`/`## 3` steps or `## 4` rules actually
     reference — its `entities: []` list, plus anything a human edit introduced that isn't listed yet.
     **The output is a data dictionary, not a diff of this approval** (§ Entity Data Model, The doc is
     a data dictionary): the doc you leave behind must read as the whole shape of one business object,
     to someone who has never opened this UC.
     * **Resolve the reference to a business object first.** `Application`, `Vendor`, `Wallet` — the
       thing the business tracks. A reference shaped `<Entity>.<Field>` ("Application.Private-School
       Certification Status"), or a register row that is plainly one attribute, names a **field**, and
       its home is a row inside the owning object's `## Fields` — never a doc of its own. Resolve it to
       the owner and carry the field name with it. Owner genuinely unclear → that is the question
       (Core Rules), not a licence to mint the fragment.
     * Match the resolved object against `01-Requirements/ENTITIES.md`. A `proposed` row this UC
       references, with no `EN-###` document yet, gets promoted now: instantiate
       `_bigin/templates/entity.md` as `01-Requirements/_entities/EN-<NNN> <Entity>.md`, id from a
       `Grep` scan of `01-Requirements/_entities/` (its own sequence — never a bash `grep`/`awk`
       pipeline, § ID scheme).
     * **Gather every known field before writing the doc, not just this UC's.** Union of: the
       `ENTITIES.md` row's `Fields (so far)` cell, the rows already on the doc, and every UC/BR in the
       entity's `features:` (plus this UC) that references it — `Grep` the entity's name and id across
       `{uc_dir}`/`{br_dir}` rather than reading those files whole. Write the full set, each row keeping
       its own `Source` cite. **A doc rebuilt from one UC's view is the fragment this step exists to
       stop producing** — and it looks authoritative while being partial, which is worse than an
       obviously empty one.
     * **Spell out the values.** Every `Type` cell enumerates its states inline, ` / `-separated
       because a `|` breaks the table: `enum: Pending School Review / Certified / Rejected`, `date:
       YYYY-MM-DD`. A bare `enum`/`status`/`code` is not a type. Values no source ever stated →
       `enum: values not stated`, **and raise a `- [ ] Q:` on a UC that references the field** so the
       gap sits somewhere the status invariant counts it; never fill it with a plausible list, and
       never invent a field, type, or required-ness no source stated (hard rule 1).
     * **Absorb an attribute-shaped doc already on disk.** Before writing the owner, `Grep`
       `01-Requirements/_entities/` for a doc whose `name:` is a field of this object (a `.` in the
       name is the usual tell, a one-row `## Fields` the confirmation). Move its rows into the owner
       with their `Source` cites intact, then stamp the fragment `status: merged`,
       `merged_into: EN-<owner>`, replace its body with a one-line pointer, and add a `## Changelog`
       line. **Never delete it and never reuse the id** (hard rule 1) — a PRD, a `UX-###`, or a UC's
       `entities:` may already cite it. Then repoint every citation in the same pass:
       ```text
       ENTITIES.md   the fragment's own row → Status: merged, Notes: "merged into EN-<owner>"
                     its fields → appended to the OWNER's row `Fields (so far)` cell
       each referencing UC/BR `entities:`   → the owner's id, the fragment's id dropped
       each hub `## Entities` + `entities:` → the owner listed, the fragment not
       ```
       A row whose content contradicts the owner's existing row for the same field is a question, not
       a merge — leave both, raise it, move on.
     * An entity that already has an `EN-###` doc is rebuilt to the same contract — the gathered field
       set replaces the doc's `## Fields` in one write, and `## Relationships` is extended with
       whatever this UC's current content adds. A field that contradicts what's already recorded is a
       question for the human (Core Rules) — raise it, keep the recorded row, skip flipping that one
       entity's status, and move on; don't overwrite it silently.
     * Add this UC's feature slug(s) to the entity's `features:` list if missing, and add
       `EN-### <Name> (<status>)` to every referencing feature hub's `## Entities` section plus its
       `entities:` frontmatter. A `merged` fragment is never listed on a hub — its owner is.
     * Update this UC's own `entities: []` frontmatter to the final list — owners, never fragments.
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
  entities were promoted/rebuilt and **how many fields each dictionary now carries** (and any
  recommended for `approved`), which attribute-shaped docs were merged into which owner and where their
  citations were repointed, which fields are sitting at `values not stated` with the question raised
  for each, which hubs were refreshed, and any contradiction raised as a question — each tied to the
  specific UC and entity it came from.

### Rebuild mode — `EN-###` or `rebuild`

The data-dictionary contract applies to docs written before it existed, and those are exactly the ones
no future approval will touch: a UC already `synced: true` never re-enters the worklist, so a fragment
minted last month stays a fragment forever unless something goes looking for it. This mode is that
something.

```text
EN-###   → resolve it: is this doc a business object, or one field of another one?
             an object  → rebuild its ## Fields as the full dictionary (step 1's gather + value
                          rules), absorb any attribute-shaped sibling belonging to it
             a fragment → merge it INTO its owner and stamp it `merged` — the id given names the
                          doc to retire, not the doc to keep
rebuild  → the same, once per doc under 01-Requirements/_entities/, sequentially, fragments last
             so their owners exist and are current before anything merges into them
```

Neither form syncs a UC, moves a `synced:` flag, refreshes a hub's `## Requirement Readiness`, or
flips an entity to `approved` — it only repairs entity docs and repoints the citations a merge
invalidates. Report in the same shape as above, with the merges called out per id.
