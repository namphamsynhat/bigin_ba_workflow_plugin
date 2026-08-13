# Conventions

The vault-wide rulebook: ID scheme, frontmatter schema, artifact lifecycle, and the conventions
every skill in this plugin follows so artifacts stay consistent and machine-readable across
engagements.

**Read only the sections your stage needs.** This file is ~12k words; no stage uses all of it. Grep
for `^## ` to list sections, then read the ones named below. Reading it whole costs more than the work.

| Stage | Sections |
|---|---|
| `/bigin-intake` | ID scheme · Intake sources · Intake capture & the question loop |
| `/extract-signal` | ID scheme · Feature Hub · Signal → feature mapping · Open Questions wording · Pain Point / Design Principles / Entity registers |
| `/bigin-transform-signal` | ID scheme · Frontmatter schema · Status vocabularies · Feature Hub · Open Questions wording · Open Questions ↔ status consistency · Feedback handling · Resumable unattended apply |
| `/enrich-feature` → `/consolidate-prd` | Traceability chain · Summary block · Feature material |

**This file is a materialized copy, not project data.** `/bigin-new-project` writes it to
`_bigin/conventions/conventions.md` so that every skill and every dispatched subagent can reach it at a
project-relative path (alongside `paths.md`, which resolves the `{variable}` names the stage guides in
`_bigin/stages/` use), and overwrites it on each re-run to pick up a plugin upgrade. Edits made here
are lost on the next run. Project-level overrides go in `.claude/bigin-ba-workflow-plugin.local.md`
(also scaffolded by `/bigin-new-project`), which may layer optional house-style preferences on top —
a `Why`-phrasing convention, a standing feature-slug shortcut — but never contradicts the schema
defined here. The schema is what every skill's parsing and writing logic is built against, not a
per-client preference.

**A note on scope, since this plugin is still under active development.** This document was
adapted from a further-along, related vault system's conventions file, which assumes a richer
artifact set and a front-end (an Obsidian plugin) that don't exist here yet. Sections describing
something this plugin doesn't build today are marked **Planned**; the current, real gap between
this document and the actual skills is tracked in one place at the bottom (§ Reconciliation notes
for this plugin) rather than scattered as caveats through every paragraph. Treat **Planned**
sections as the target shape new work should converge on, not as documentation of something you
can already run.

## ID scheme (permanent, never reused)

| Prefix | Artifact | Folder | Status |
|---|---|---|---|
| INT | Intake note (email / meeting; requirement or feedback) | 00-Inbox | Implemented |
| FR | Feature requirement | 01-Requirements/_frs | Implemented — its own file, `FR-<NNN> <Title>.md`, drafted/updated by `/bigin-transform-signal`. Status: `draft → enriched → approved → consolidated`, plus `needs-clarification`/`removed` (§ Status vocabularies) |
| BR | Business rule | 01-Requirements/_brs | Implemented — its own file, `BR-<NNN> <Title>.md`, `fr: []` citing the FR(s) it constrains (feature-level if none apply yet). Same status vocab as FR |
| PP | Pain point (register row + FR mirror, no separate per-item file, same discipline as BR) | 01-Requirements | Implemented |
| EN | Entity data model | 01-Requirements/_entities | Implemented — `/bigin-transform-signal` promotes an `ENTITIES.md` `proposed` row into its own file, `EN-<NNN> <Entity>.md` |
| SCN | Business scenario (cross-feature flow) | 01-Requirements/SCENARIOS.md | Implemented — one **register file** with one row per scenario (`SCN-###`), not one document per scenario |
| PRD | Product requirements doc | 02-PRD | **Planned** — `/approve-fr` today writes one consolidated `PRD.md` with a section per approved feature, not a per-`PRD-###` file. Decided status vocab once it exists as its own artifact: `draft → approved` (§ Status vocabularies) |
| EP | Epic | 03-Epics-Stories | **Planned** — `/consolidate-prd` today writes one flat `epics.md`, not per-`EP-###` files. Same `draft → approved` status vocab once split out |
| US | User story | 03-Epics-Stories | **Planned** — stories live nested under their epic in `epics.md` today, not as their own `US-###` files. Same `draft → approved` status vocab once split out |
| UX | UI/UX spec | 04-UIUX | **Planned** — `/prototype-design` today writes one `<feature-id>-prototype.md` per feature, not a `UX-###` id |

Next-ID: scan the relevant folder for the highest existing number and increment —
`01-Requirements/_frs/`, `_brs/`, `_entities/` for `FR-###`/`BR-###`/`EN-###` respectively. Each is
its **own** independent sequence (`/bigin-transform-signal`'s actual numbering rule) — an earlier
draft of this document specified one shared vault-wide sequence across `BR-###` and `EN-###`; that
was never built, and the per-directory scan above is what's real. `PP-###` scans
`01-Requirements/PAIN-POINTS.md`, not any FR, since a pain point can predate its feature's FR.

**Do that scan with the `Grep` tool, never a Bash `grep`/`awk` pipeline.** Treat any unattended or
looped run in this plugin (a batch of `extract-signal` subagents, a future `--auto` mode) as
running under a tool allowlist that may grant `Grep` but not a bare shell interpreter — a
`grep -roE 'BR-[0-9]{3}' … | awk …` one-liner can be silently denied without failing the run, so
the run finalizes having quietly skipped the scan and can reuse an id that already exists. Use
`Grep` with `pattern: "BR-[0-9]{3}"`, `output_mode: "content"` over `01-Requirements`, and take the
highest match. `awk` in particular is a shell escape (`awk 'BEGIN{system(…)}'`), and these loops
read client transcripts — untrusted text — so don't "fix" a denial by asking for the interpreter
rule; route around it with `Grep` instead.

Singleton (no ID prefix): `01-Requirements/FEATURES.md` (`type: feature-map`) — the canonical
feature list, maintained by `/extract-signal`. Every artifact's `feature:` slug must match one of
its rows. Also singleton, one per feature: `01-Requirements/_features/<slug>.md`
(`type: feature-hub`) — see § Feature Hub below. Also singleton, vault-wide:
`01-Requirements/DESIGN-PRINCIPLES.md` (`type: design-principles`) — the standing client
design-preference register, maintained by `/extract-signal`, see § Design Principles Register
below. Also singleton, vault-wide: `01-Requirements/ENTITIES.md` (`type: entity-map`) — the
canonical entity list, maintained by `/extract-signal`/`/enrich-feature`, mirrors `FEATURES.md`
(see § Entity Data Model). Also singleton, vault-wide: `01-Requirements/PAIN-POINTS.md`
(`type: pain-point-register`) — the vault-wide pain-point register (see § Pain Point Register).

**Planned** working file: `00-Inbox/_extract-signal/AGENDA <date>.md` (`type: refine-agenda`) — a
per-batch progress tracker. Not built yet; `extract-signal` currently reports batch progress
inline (§ Step 4 of its `SKILL.md`) rather than persisting an agenda file.

## Frontmatter schema (all artifacts)

```yaml
---
id: FR-012
type: requirement        # intake | requirement | prd | epic | story | uiux
kind: requirement        # intake only: requirement | feedback | mixed | info (ops/admin — never refined)
title: Bulk invoice export
status: draft            # vocabulary is per artifact type, not one shared list — see
                         # § FR/BR status below for FR/BR, § PRD/Epic/Story status for those,
                         # and § Entity Data Model for EN. An intake note's own status vocabulary
                         # (raw | needs-clarification | in-review | consumed) is separate again —
                         # see § Intake capture & the question loop.
version: 1.0
feature: invoicing       # stable slug shared across the chain
sources: [INT-003]       # upstream links
links: [PRD-002]         # downstream links
attachments: []          # requirement only: vault-relative paths to source documents
                         # (e.g. 00-Inbox/_attachments/INT-012/spec.docx) — /bigin-transform-signal
                         # copies these from consumed INT notes so the feature's material is complete
amends:                  # requirement only: the FR-### id this one changes, if any (hard rule 7) —
                         # blank for almost every FR, including one folding in a CR against an
                         # already-approved feature (that's an in-place edit to the same FR, not a
                         # new one). Set only for the rare case where a feature's scope genuinely
                         # splits into a second, independent decision that doesn't belong in the
                         # same document.
source_ids: []           # intake only: email provider's conversation+message ids (Outlook, or Spark thread id) /
                         # meeting provider's meeting id (Fathom, Spark, or Firefly) — re-run dedup; see
                         # `email_provider`/`meeting_provider` in `_bigin/system/project.md`
tags: []                 # intake only: e.g. needs-review (unknown sender/invitee)
owner: team
updated: 2026-07-03
---
```

## Status vocabularies

There is no single shared `status` list across every artifact type — each type has its own, sized
to what that artifact actually needs to track. All of them share one discipline, though:
**status can move freely, in either direction.** None of these are a strict forward-only gate —
hard rule 7 means a later edit can knock a `consolidated` FR back to `draft`, an `approved` PRD
back to `draft`, and so on. Treat every arrow below as "can move to," never "can only move
forward to."

**FR/BR** (`01-Requirements/_frs/`, `01-Requirements/_brs/`):

`draft → enriched → approved → consolidated`, plus two side-states reachable from any of those
four:

| Status | Meaning |
|---|---|
| `draft` | Content exists — created or last folded in by `/bigin-transform-signal` — but hasn't been through `/enrich-feature` yet. The default resting state. |
| `needs-clarification` | At least one unresolved `- [ ] Q:` line in `## Open Questions` (§ Open Questions ↔ status consistency's invariant — unchanged, just now one value in this list rather than sitting alongside a separate `in-review`). Once every question resolves, status moves to whatever it would otherwise be — `draft` if it hasn't been enriched yet, `enriched`/`approved`/`consolidated` if a later-stage edit is what raised the question. Never a fixed placeholder. |
| `enriched` | `/enrich-feature` has run: domain research + entity mapping done, concerns resolved or accepted as risk. |
| `approved` | A human has approved it via `/approve-fr`; it's feature material (§ Feature material) and folded into the PRD. |
| `consolidated` | `/consolidate-prd` has merged prototype-driven changes back and generated its epic/story. The FR's pipeline is complete — until new feedback lands. |
| `removed` | A human decided this FR/BR is no longer relevant/wanted (§ Feedback handling's "Removing scope") — human-gated like `approved`, never set by an agent. Not deletion (hard rule 1): the file, id, and history stay intact. |

An earlier draft of this document specified `raw | draft | in-review | needs-clarification |
approved | superseded | removed` as one shared vocabulary for every artifact type; that's
superseded by the per-type lists here. `in-review` and `superseded` are retired for FR/BR — a
resolved `needs-clarification` now returns to whatever stage the artifact was already at (no
placeholder "reviewed" state needed), and there's no separate "old version" state to track since
hard rule 7 already means every edit lands in place, not as a fork.

**PRD / Epic / Story** (`02-PRD/`, `03-Epics-Stories/`, once they exist as their own files — see
§ Reconciliation notes for today's flat-file reality): `draft → approved`, where `approved` means
ready for / queued into development — nothing more granular than that.

**EN** (entities): its own three-state vocab, `proposed → draft → approved` — see § Entity Data
Model. Simpler because an entity doc is a field list assembled from already-approved-adjacent
signals, not a thing that itself needs an `enriched`/`consolidated` pipeline pass.

**INT** (intake notes): `raw | needs-clarification | in-review | consumed` — see § Intake capture
& the question loop and `/bigin-intake`'s own queue logic. Unrelated to the FR/BR list above;
don't conflate the two just because both use `needs-clarification`.

## Traceability chain

`/approve-fr` (PRD) and `/consolidate-prd` (Epics/Stories) branch on the FR's `feature:` slug
looked up in `01-Requirements/FEATURES.md` — the feature's `Status` there decides which of two
valid chains applies:

- **Full** — feature `proposed` / `committed` / `not-built` (new scope):
  `INT → FR/BR → PRD → EP → US → UX`.
- **Lightweight CR** — feature already `built` (a change/fix/improvement on something shipped):
  `INT → FR/BR → US → UX`, skipping PRD and EP. The US cites the FR directly in `sources` instead
  of an EP, and the FR's `links` points at the US id(s) instead of a PRD id.
- **Design** — a presentation-only signal, at any feature status: `INT → design directive → UX`,
  skipping FR, PRD, EP, and US entirely. A statement about look, layout, tone, copy voice,
  interaction feel, or an accessibility affordance produces **no functional scope**, so there is
  nothing for a PRD section to carry and nothing for a story to decompose. It becomes a directive
  in one of two places — a `DESIGN-PRINCIPLES.md` row when it's durable and cross-cutting, or a row
  in its feature hub's own `## Design Directives` section when it's scoped to one feature — and
  `/prototype-design` reads both directly. The directive carries no id of its own; its
  traceability runs through the originating Signal Log row's `Destination` cell.

  The chain is chosen by a strict test, not by the client's phrasing: **if a tester could write a
  pass/fail assertion for it that never mentions appearance, it is FR or BR, not a design
  directive** — "ask for confirmation before deleting" adds a step to a flow and takes the Full or
  CR chain, however visual the request sounded. An ambiguous signal takes the FR chain, because an
  over-routed FR is caught at the human gate while an under-routed directive skips the gate.
  `_bigin/stages/transform/3-lane-design.md` and `_bigin/stages/transform/3-routing.md` hold the
  boundary test and the destination rules.

**Planned** — this plugin doesn't yet distinguish the Full and CR chains; every feature with an FR
runs the same fixed pipeline (`/enrich-feature → /approve-fr → /prototype-design →
`/consolidate-prd`) regardless of whether it's new scope or a CR against something shipped. The
Design chain is **half-built**: `/bigin-transform-signal` files directives to both destinations
today, and `/prototype-design` already reads `DESIGN-PRINCIPLES.md` directly, but it doesn't yet
read a hub's `## Design Directives` and still keys on an FR id — so a design-only feature (no FR
at all) has its directives filed correctly but cannot yet be handed to `/prototype-design`. See
§ Reconciliation notes.

Every link in the chosen chain must resolve; if one can't be established, add an Open Question
instead of guessing.

The `feature:` slug is the horizontal anchor across the chain: it must exist as a row in
`01-Requirements/FEATURES.md`. New intake about a mapped feature updates its FR **in place, at any
status** (hard rule 7, § Feedback handling) — approval doesn't freeze it, and neither does the
feature shipping — never as an unrelated parallel FR for the same slug.

A `SCN-###` Business Scenario (§ Business Scenarios) is a cross-cutting **overlay**,
not a fork of this chain: it annotates which several complete
`INT→FR→PRD→EP→US→UX` chains — one per participating feature — compose a single real-world
business flow. Nothing about it changes how any one feature's own chain resolves.

## Absorbed — the reprocess trigger (**Planned**)

`sources:` answers *"which upstream artifacts does this one trace to?"* — a permanent,
never-pruned traceability record (hard rule 3). It cannot answer *"is this artifact still
current?"*, and since hard rule 7 nothing else could either: a CR edits an approved FR **in
place** — same id, bumped `version`, no new id anywhere — so a PRD section that cites `FR-007`
keeps looking covered no matter how far `FR-007`'s content has since moved. The failure mode this
guards against: new intake updates an FR, the human re-approves it, and the feature's
PRD/epics/prototype sit stale from the cascade — visually identical to freshly drafted work
awaiting review, with nothing anywhere saying "the downstream steps need to re-run."

**`absorbed:` is the record that would close it, once built.** Every artifact downstream of
another would carry it:

| Artifact | `absorbed:` entries | Written by |
|---|---|---|
| PRD section | `FR-###@version` for each approved FR folded into it | `/approve-fr` |
| Epic/Story | `PRD-###@version` (or `FR-###@version` on the lightweight path) it decomposes | `/consolidate-prd` |
| Prototype | `FR-###@version` / PRD section version it designed from | `/prototype-design` |

**The rule, once implemented: an artifact is stale when an upstream it *cites* has a current
`id@version` that its `absorbed:` doesn't list.** Two states, don't conflate them:

- **Never processed** — the upstream id appears in no downstream `sources:` at all. The
  downstream step simply hasn't run for it yet.
- **Processed, then drifted** — cited, but the version moved on. This is the re-approved-CR case,
  and the one that's invisible without this field.

Whoever produces an artifact would **re-stamp** its `absorbed:` on every run — that's what makes
this self-healing rather than another mirror to go stale: there is no separate counter, and a
re-run cannot leave a false "current" claim behind. Until this is built, treat any FR edited after
its feature's PRD/prototype/epics were generated as needing a manual re-check, and note that
explicitly in the report rather than assuming downstream artifacts are still accurate.

## Feature material (the approve → process handoff)

Approval converts an FR from *work in progress* into **staged material on its feature**:

- An FR with `status: approved` **is** feature material — no extra flag. Everything sharing its
  `feature:` slug aggregates into the feature's material set: the approved FR(s) with their BRs,
  resolved discussion, and `attachments`, plus the source INT notes.
- Only `approved` FRs qualify as material. Feedback that touches an FR — at any status, including
  already-`approved` material, before or after the feature ships — is applied **in place** and
  sets it back to (or keeps it at) `draft`/`needs-clarification` (hard rule 7: approval
  doesn't freeze an FR any more). Feedback that touches an already-approved FR therefore **does**
  un-stage it, the same way it would for any other status: the edit lands in the same FR (version
  bump + changelog citing the source), and it drops out of the feature's material set until the
  human re-approves it. There's no forking to a new `amends:`-linked sibling FR for this case — a
  feature normally carries just the one FR across its life, staged as material only while it's
  currently `approved`.
- Humans gate `approved` (hard rule 4) — an agent never sets it; `/approve-fr` is the point where
  a human confirms and the status flips.
- **Planned** — a richer engagement (a front-end dashboard, a workflow picker per feature) may
  eventually replace the fixed `/enrich-feature → /approve-fr → /prototype-design →
  /consolidate-prd` pipeline described here with something that dispatches per-feature by need.
  Not built today; the fixed order is what every feature runs.

## Feature Hub

`01-Requirements/_features/<slug>.md` (`type: feature-hub`) is the single note that shows
everything about one feature, and the file to hand an agent when saying "work on `<slug>`".
`FEATURES.md` stays the canonical index (one row per feature, the anti-fragmentation anchor); the
hub is the rich per-feature view generated from the same underlying artifacts, so nothing here is
ever hand-authored content — it's always assembled/refreshed from the FR(s), INT sources, PRD
section, epics/stories, and prototype that already exist for that slug.

**Frontmatter:**
```yaml
---
type: feature-hub
feature: <slug>
name:           # display name — mirrors the FEATURES.md row's Feature column. This is the source
                # of truth for any consumer (this plugin's own skills, or a front-end app) reading
                # Slug/Feature/FR/Code areas/Sources — read from this frontmatter, not by parsing
                # FEATURES.md's table (§ Feature Map format)
status: <mirrors the FEATURES.md row's Status at last refresh>
fr: []          # every FR-### id this feature has ever had — normally just one across the
                # feature's whole life, since a CR edits it in place rather than forking (hard
                # rule 7); occasionally more than one only when the feature genuinely spans more
                # than one independent decision. Oldest first; [] before the first FR is drafted.
                # Written by /bigin-transform-signal
br: []          # every BR-### id this feature has ever had, same discipline as fr: above —
                # written by /bigin-transform-signal
code_areas: []  # mirrors the FEATURES.md row's Code areas column (project_mode: ongoing only)
sources: []     # mirrors the FEATURES.md row's Sources column — INT-###/document ids/paths
prd:            # PRD-### id, or blank — Planned; today this would point at the PRD.md section anchor
epics: []       # EP-### id(s) — Planned; today epics.md has no per-epic id to cite
stories: []     # US-### id(s) — Planned, same as above
uiux:           # UX-### id, or blank — Planned; today this would point at the prototype file path
entities: []    # EN-### id(s) this feature's FR(s)/BR(s) reference — [] until one exists.
                # Written by /bigin-transform-signal (§ Entity Data Model)
updated:
---
```

Signals never stop arriving — a feature accumulates them across many meetings/emails over the
life of the project, some processed immediately, some held for months, some later contradicted by
a follow-up call. **There is no single feature-wide "done" state** — progress is tracked
signal-by-signal and requirement-by-requirement, never as one blanket checkbox.

**Body sections** (instantiate from `_bigin/templates/feature-hub.md`):
- `## Notes / History` — the readable, append-only, dated-bullet narrative of the feature (§
  Feature Map format) — placed right after the one-line description, before `## Signal Log`. This
  is where `/extract-signal`/`/bigin-transform-signal` write the "story" (why it exists, what each
  meeting/CR round added, what got resolved); `FEATURES.md`'s own Notes cell is a one-line pointer
  here, never inline prose.
- `## Signal Log` — the append-only register every downstream process reads. One row per signal,
  in landing order:

  | # | Signal | Type | Source | Status | Destination | Notes |
  |---|--------|------|--------|--------|--------------|-------|

  - **`#` is permanent** once assigned, like a `BR-###` number — never renumbered or deleted. A
    conflicting or superseding signal is always a **new row**; the old row's `Status`/`Notes` gets
    updated to point at the row that superseded it. History is never rewritten in place.
  - **`Status` values**: `new` (just landed, not yet triaged) · `held` (anchored to the feature, no
    FR exists yet — resting state pre-FR, no gate, no urgency; once an FR exists, a new signal
    against it moves straight to `staged` rather than resting here, regardless of the FR's status
    — hard rule 7, approval no longer freezes it) · `staged` (a proposed change sitting in an FR's
    `## Discussion`, not yet applied) · `applied` (folded into FR content) · `question` (the signal
    *is* an open question, not a requirement — tracked until answered) · `conflict` (contradicts
    an earlier row — needs human resolution before either can be applied) · `superseded` (an older
    row a resolved conflict/newer decision overrode) · `rejected` (explicitly out of scope). This
    plugin's `extract-signal` skill only ever writes `new`/`question`/`conflict`/`rejected` when
    filing a fresh signal (§ its own `2-extraction.md`) — `held`/`staged`/`applied`/
    `superseded` describe a signal's relationship to an FR, which is `/bigin-transform-signal`'s
    job to set, not extraction's.
  - **"Processed" = `applied` \| `superseded` \| `rejected`. "Not yet processed" = everything
    else** (`new`/`held`/`staged`/`question`/`conflict`) — this is the queue a human or agent works
    from, not a percentage-done bar.
  - **Conflict handling**: when a new signal contradicts a `held`/`staged`/`applied` row, add the
    new signal as its own row with `Status: conflict`, citing the row number(s) it conflicts with
    in `Notes`. Raise an Open Question (never guess which one wins) on the FR it belongs to (its
    most recent open one, if any exist; otherwise the closest applicable FR) or on this note if
    none exists. Once the human answers, the losing row flips to `superseded` (`Notes: "superseded
    by #N, resolved <date>"`), the winning row flips to `staged`/`applied`, and the content updates
    **in place** (version bump + changelog), regardless of whether that FR is still unapproved or
    already `approved` (hard rule 7 — an approved FR's fold-in also flips it back to `draft`).
- `## Requirement Readiness` — a refreshed **snapshot for orientation, not the gate itself**:

  | Artifact | Status | Ready for next step? | Blocking |
  |----------|--------|------------------------|----------|

  One row per FR/BR touching this feature — the rare feature with more than one FR (hard rule 7 —
  only when they're genuinely distinct decisions) gets one row per FR, oldest first. The
  authoritative gate for `/enrich-feature`/`/approve-fr`/`/prototype-design` is always each FR's
  own live frontmatter `status` (§ Feature material) — this table just saves a human or agent from
  having to open every FR to see what's ready; a skill still checks the FR directly before
  proceeding, never trusts a possibly-stale table alone. An `approved` FR can still receive new
  signals later (hard rule 7 — approval doesn't freeze it); when that happens it's applied in
  place via the normal fold-in flow the next time `/bigin-transform-signal` touches this feature,
  not held in a separate backlog — note it here the same way as any other pending change
  ("approved — N new signal(s) since approval, not yet run through `/bigin-transform-signal`").
- `## Related Documents` — the FR(s)' `attachments:` list.
- `## Domain Research` (**Planned**) — one entry per domain-research run for this feature,
  appended only by `/enrich-feature` when the feature's enrichment needed external grounding it
  can't get from client signals alone (a regulated/compliance domain, a named third-party
  platform/API's real behavior, industry-standard practice) — most features never populate this.
  Each entry: date, topic, one-line summary of key findings, link to the full report under
  `01-Requirements/_research/<slug>/`. Not built yet — `/enrich-feature` currently appends its
  findings straight into the FR file's own `## Domain Concerns` section instead of a hub-level log.
- `## Business Scenarios` — every `SCN-###` this feature participates in, and this feature's step
  number within it (a one-line pointer; the full step sequence lives in `01-Requirements/
  SCENARIOS.md`, § Business Scenarios below). Empty for most features.
- `## Entities` — every `EN-###` this feature's FR(s)/BR(s) reference, with each entity's current
  status. See § Entity Data Model.
- `## Pain Points` — a table mirroring this feature's rows from `01-Requirements/PAIN-POINTS.md`:
  `PP-### | Statement | Status | Proposed solution | Resolved by` (§ Pain Point Register). Empty
  until a `[pain-point]` signal anchors here.
- `## PRD` — link + status, or "not started."
- `## Epics & Stories` — table of epic/story ids with status, or a pointer into `epics.md` until
  `EP-###`/`US-###` exist as their own ids.
- `## Design Directives` — feature-scoped presentation directives on the Design chain (§
  Traceability chain): `# | Directive | Source | Status | Notes`, `#` permanent and append-only
  like the Signal Log, `Status` one of `open` / `reflected` / `superseded` / `conflict`. Written by
  `/bigin-transform-signal`'s design lane; read by `/prototype-design` as the feature's
  presentation brief (**Planned** — that skill doesn't read it yet, § Reconciliation notes). Empty
  for most features. Durable, cross-cutting preferences go to `DESIGN-PRINCIPLES.md` instead, or as
  well (§ Design Principles Register).
- `## Prototype` — link + status, or "not started." (The hub template calls this section
  `## UX Spec`; treat the two names as the same section until one of them is renamed.)
- `## Open Questions / Gates` — every Signal Log row with `Status: question` or `Status: conflict`,
  plus every open FR's own Open Questions — what's actually blocking progress right now. An
  `approved` FR normally contributes nothing here — its questions were resolved before approval —
  but a later edit can reopen it (hard rule 7, § Feedback handling) and reintroduce questions the
  same as any other FR update.
- `## Changelog` — one line per refresh: date, what changed, which run touched it.

**Maintenance contract — who refreshes it, and when:**
- `/extract-signal`: for every signal a run extracts, **append** a `## Signal Log` row (never
  overwrite a prior row's `#`/`Signal`/`Source` — only its `Status`/`Notes` when a later signal
  supersedes or conflicts with it). Create the hub from the template if it doesn't exist yet.
  Refresh `## Requirement Readiness` and `## Open Questions / Gates` to match. **Refresh
  `## Pain Points`** to mirror any `PP-###` row this run minted or updated in
  `01-Requirements/PAIN-POINTS.md` for this feature — a pain point can land here even before any
  FR exists.
- `/bigin-transform-signal`: drafts/updates FR/BR files under `_frs`/`_brs` (§ Feedback handling),
  after each confirmed human-gate fold-in flips the affected Signal Log row from `staged` to
  `applied`, and refreshes `## Requirement Readiness`, `fr:`/`br:` frontmatter, and — for the
  cross-feature cases it catches (§ Entity Data Model, § Business Scenarios) — `## Entities`,
  `## Business Scenarios`, and `entities:` frontmatter. Also appends to `## Design Directives` for
  every presentation-only signal it routes down the Design chain, and fills each processed Signal
  Log row's `Destination` cell (the column `/extract-signal` leaves blank) with where the signal
  actually landed. It never sets a hub's own `status:` — that mirrors the `FEATURES.md` row's scope
  state, not a workflow state, and there is no "ready for PRD" feature status.
- `/enrich-feature`: refreshes `## Requirement Readiness`/`## Related Documents`/
  `## Open Questions / Gates`, and **`## Pain Points`** whenever it folds a pain-point signal into
  the FR's own `## Problem & Pain Points` table.
- `/approve-fr`: refresh `## PRD`, and flip the corresponding Signal Log rows (the ones the PRD
  was drafted from) to `applied` if not already.
- `/prototype-design`: refresh `## Prototype` with the link/status. If the source FR is still open
  (not yet `approved`), also append a line to its `## Discussion` citing the prototype as
  supporting evidence — this is never how an already-`approved` FR gets a content change (that's
  `/bigin-transform-signal`'s feedback loop, § Feedback handling).
- `/consolidate-prd`: refresh `## Epics & Stories` and the PRD's `## Design` subsection.
- A human changing the `FEATURES.md` row's `Status` (e.g. `proposed` → `committed`) doesn't
  retroactively touch the hub — its `status:` field catches up the next time any of the above runs
  against that slug.
- The hub is a generated index like `FEATURES.md`, not an approval-gated artifact (hard rule 4
  doesn't apply to it) — but never delete Signal Log history, only append and update
  `Status`/`Notes` forward.

## Feature Map format

`FEATURES.md` is an **index, not a narrative** — one short row per feature. A markdown table cell
has no real newlines and no reliable `|`-escaping, so a Notes cell that grows past a line or gains
a stray `|` silently corrupts that row for any reader — including a future front-end app parsing
this table.

**Column contract** — every row author (`/extract-signal`) must respect this positional shape;
treat it as a load-bearing "API" any future front-end's `readFeatures()`-equivalent would depend
on (a regex header match + positional `|`-split, not a schema-validated parse):

| Column | Owner | Contents |
|---|---|---|
| `Slug` | agent (permanent once set) | Never renamed/reordered without also updating any downstream parser |
| `Feature` | agent | Short display name |
| `Status` | **human** | `proposed \| committed \| not-built \| built \| out-of-scope` (agents only ever write `proposed`) |
| `FR` | agent | Every `FR-###` id this feature has ever carried (hard rule 7) |
| `Code areas` | agent | Optional |
| `Sources` | agent | INT-###/document ids/paths this row traces to |
| `Notes` | agent | **A one-line pointer only** — `See _features/<slug>.md § Notes / History`. Never inline prose. |

**Where the narrative actually lives:** every feature hub (`01-Requirements/_features/<slug>.md`,
§ Feature Hub) carries a `## Notes / History` section, placed right after the feature's one-line
description and before `## Signal Log` — an **append-only, dated bullet list** (one bullet per
event/date, oldest first), the same discipline as `## Changelog`. This is where
`/extract-signal`/`/bigin-transform-signal` write the readable "story" of a feature (why it
exists, what each meeting/CR round added, what got resolved) — the Signal Log stays the atomic
per-signal trace table; the Notes/History section is the chronological narrative a human reads
top-to-bottom. Writing here instead of into `FEATURES.md`'s Notes cell is what keeps the index
thin — do **not** duplicate the same prose in both places.

**Source-of-truth split:** the `Slug`/`Feature`/`FR`/`Code areas`/`Sources` columns above should be
read from each feature hub's own frontmatter (`name`/`fr`/`code_areas`/`sources`, § Feature Hub),
not by parsing `FEATURES.md`'s table — point at notes that already exist and read their metadata,
instead of scanning a markdown table by column position. `FEATURES.md`'s table is still what
`/extract-signal` writes and still the human-facing index (and still what a brand-new feature
shows up in first, before its hub exists) — but it should not be any consumer's *source* for those
five columns. **`Status` is the one exception, read live from `FEATURES.md`'s table**, not from
the hub's `status:` mirror — Status is the column a human hand-edits directly (`proposed` →
`committed`/`built`/`out-of-scope`) and that edit is meant to take effect immediately, not wait for
the next `/extract-signal`/`/enrich-feature` run to catch the hub's mirror up. Practically, this
means `/extract-signal` writes every row's `Feature`/`FR`/`Code areas`/`Sources` value onto that
feature's hub frontmatter at the same time it writes the `FEATURES.md` row (creating the hub from
the template first if it doesn't exist yet) — the two copies must never drift, since the hub copy
is what's actually read.

## Intake sources

`/bigin-intake` accepts three source types, recorded in the `source:` frontmatter field:

| `source:` | What it is | `source_ref:` | `source_ids:` |
|---|---|---|---|
| `email` | Message or thread from the project's `email_provider` (Outlook MCP, or Spark Desktop via the `spark` CLI) | Thread subject | Conversation id + message id(s) (Outlook) or thread id (Spark) |
| `meeting` | Transcript from the project's `meeting_provider` (Fathom MCP, Spark CLI, or a connected Firefly MCP) — or drop-folder fallback | Meeting name + date | Provider's meeting id |
| `direct` | User-typed description, fetched URL, or local file | URL · filename · "user input YYYY-MM-DD" | URL (link intakes only) |

**Provider config**: `email_provider` and `meeting_provider` in `_bigin/system/project.md`
frontmatter select which tool `/bigin-intake` talks to for each source type (default `outlook` /
`fathom` when unset, for vaults created before this field existed).

**Direct intake** is a first-class path — triggered when the user provides text, a URL, or a file
path along with `/bigin-intake` instead of (or alongside) the automated pull. It creates an INT
note with `source: direct`; all other rules (dedup, `kind:`, `## Raw`, attachment handling) apply
identically.

It is also the **only** path that can carry `declared_features:` — the feature slug(s) the user
named at capture — because it's the only one with a human present when the note is written. Email
and meeting notes are pulled unattended, so they have nobody to ask and always anchor from the
signals in `/extract-signal`. Semantics: § Signal → feature mapping → Declared features.

## Intake capture & the question loop

`/bigin-intake` is **capture-only**: it writes frontmatter, verbatim `## Raw`, and attachments —
nothing else. The only judgement it makes is the `kind:` filing label. All interpretation belongs
to `/extract-signal`, which fills the note's `## Extracted signals` table
(`_bigin/templates/intake.md`): one row per signal —
`# | Type | Signal | Why | Source | Feature | Status | Notes` — each traced to a message,
timestamp, or attachment, and every `requirement`/`feedback` row carrying a `Why` (the client's
stated reason). A requirement without a stated why is not ready — the missing why becomes a
`question` row, never a guessed rationale. `Feature` and `Status` make the row's anchor and
progress machine-readable — `Status` reuses the same vocabulary as the Feature Hub's
`## Signal Log` (§ Feature Hub) so a signal reads the same state at both levels.

Questions raised by `/extract-signal` are written **into the source INT note's `## Open
Questions`** — `- [ ] Q: … (owner: client|team) ↦ FR-###` with an `A:` answer line — mirrored on
the FR when one exists (the FR copy is canonical). A note left with unanswered questions is parked
`status: needs-clarification`: that flag is what surfaces it for the human to jump in. Two ways to
close a question:

- **Answer inline**: fill the `A:` line, tick the box. The next `/extract-signal` pass folds the
  answer in, ticks the FR copy, and flips the note to `in-review`.
- **Answer arrives from the client**: `/bigin-intake` appends the reply to the note and resets it
  `status: raw`, which re-enters the extraction queue; extraction matches the reply to the open
  question as an `[answer]`.

### One question, two places — never two questions

A `question`/`concern` row in `## Extracted signals` and its `## Open Questions` line are **two
views of one question**, not two questions. The row is the extraction ledger entry (what was
found, where, what state it's in); the `## Open Questions` line is the human-facing copy — the
one thing to answer. Three rules keep them one question:

1. **Never re-word the mirror into a second question.** The mirror may add context the human
   needs to answer (which FR it collides with, what's already decided) — but the *ask itself*
   must be recognisably the same sentence as the row's `Signal` cell, not an independently
   composed question. Two separately-drafted phrasings of one ambiguity read as two open items
   to a human, get answered twice, and cannot be paired back up by any tooling: the wordings
   routinely share too few words for text matching to help.
2. **Every `question`/`concern` row gets a mirror**, in the same run that writes the row. A row
   with no mirror is a question the human is never shown — the note reads as "nothing to
   answer" while the ledger says otherwise.
3. **`## Open Questions` is authoritative for reading.** Anything that surfaces questions to a
   human reads that section and stops there when it has items; the signal table is a
   **fallback**, read only when the section is empty (rule 2 was violated). A ticked row in the
   section counts as an item: its ledger twin is answered history, not something to ask again.
   Reading both formats is what double-renders every mirrored question, so don't reintroduce it.

## Open Questions ↔ status consistency (verification, not just intent)

`status: needs-clarification` and the artifact's own `## Open Questions` section are two mirrors
of one fact — the same drift risk as a stale Feature Hub Signal Log `Status` column left
`question` after its FR absorbed the row (§ Feature Hub), just on the `status:`
frontmatter/body pairing instead. A human reads whichever surfaces first (a queue badge reads
`status:`; opening the note reads the section body) and both must agree, or the note reads as
done in one place and stuck in the other.

**The invariant:** zero unchecked `- [ ] Q:` lines in `## Open Questions` (INT note or FR) ⟺
`status` is not `needs-clarification`. Any unchecked line ⟺ `status` **is**
`needs-clarification`. This holds for every artifact that carries an `## Open Questions` section
— INT notes and FRs alike.

Every skill that writes to `## Open Questions` or sets `status` on such an artifact
(`/extract-signal`, `/bigin-transform-signal`, `/enrich-feature`) must make the status line the
**last** write-back step, derived by re-counting the section **after** every accepted change has
been applied to it that run — never decided earlier in the run and then left stale by a later
edit to the same section:

1. Apply every accepted change to `## Open Questions` first (tick resolved boxes with `A:` filled,
   append genuinely new ones).
2. Count remaining unchecked `- [ ] Q:` lines in that section.
3. Set `status: needs-clarification` if the count is > 0; otherwise move it to whatever "done"
   means for that artifact type (`in-review` for an INT note; whatever stage the FR/BR was
   already at — `draft` if it hasn't been enriched yet — for an FR/BR, § Status vocabularies).
   Do this from the count, not from memory of what the run intended to resolve.

**Common ways this drifts** (treat each as the bug it is, not a cosmetic gap): ticking every box
while `status` still reads a stale `needs-clarification` from before the run; flipping `status`
off `needs-clarification` while a `- [ ] Q:` line — even one raised earlier in the same session
and forgotten — is still unchecked in the body; ticking a box that isn't genuinely resolved (an
answer that still needs a client round-trip stays unchecked, and `status` stays
`needs-clarification`, even if every *other* question closed) just to make the count zero.

## Resumable unattended apply (checkpoint + idempotent writes)

An unattended fold-in — matching a human's already-written inline answer to its FR and folding it
in, whether that's `/bigin-transform-signal`'s Stage 1 fold-in, `/extract-signal`'s per-note batch
processing, or a future `--auto` mode — is a multi-file write: the FR itself, the feature hub,
sometimes `FEATURES.md`, sometimes the source INT note. Nothing here runs inside a database
transaction — the process can be killed between any two of those writes by an external timeout or
a session running out of budget, which kills the parent process while an orphaned child keeps
mutating files in the background. Applying an answer directly (rather than staging it for a later
human confirm) removes one failure mode but must not introduce a worse one — a fold-in that's
half-applied across files, with no way to tell "not started" from "partially done" from "fully
done."

The fix is the same one durable-execution agent runtimes converge on for exactly this problem —
checkpointed writes, idempotent retries, an append-only decision trail — applied with the vault's
existing tools, not a new ledger file:

1. **Dedup-check before writing anything.** Before applying an answer, check whether it's already
   landed: does the FR's `## Changelog` already cite this INT id's fold-in, or does the
   `## Open Questions` line already read as resolved (not merely ticked) rather than unticked? If
   yes, this run is a retry of an already-completed apply — do nothing to that FR, and move
   straight to reconciling any mirror that's still behind (step 3). Never re-append a changelog or
   Discussion line just because this run started before checking.
2. **The FR's own file write is the checkpoint — make it one atomic write, and make it first.**
   Compose the *entire* change (requirement body wording, `version` bump, `## Changelog` line,
   re-counted `status`) and write the FR file once. Before that single write lands, nothing has
   changed on disk — a kill at any point up to here leaves the note exactly as it was, correctly
   still eligible for a future run to pick up (no special "in progress" marker needed; there is
   nothing to distinguish from "not started yet"). After it lands, the fold-in is **done** —
   everything downstream is a re-derivable mirror, never the source of truth.
3. **Mirrors are always safe to reconcile, never a one-shot append.** The feature hub's Signal Log
   row, `FEATURES.md`, and the source INT note's own tick/status are all *read from the FR's
   current state* and corrected to match — flip a Signal Log row to `applied` if the FR it points
   at now shows the fold-in, tick the INT note's copy if the FR copy is already resolved. Setting
   an already-correct mirror field again is a no-op, not a duplicate, so this step never needs its
   own resume logic: run it every time, unconditionally, whether this is the first pass or the
   tenth.
4. **A subsequent run's gate check is therefore a 3-way read, not a 2-way one.** For any FR
   carrying a fold-in candidate: (a) **genuinely unanswered** — the INT note's `A:` line is still
   blank → wait for a human, not eligible. (b) **already applied** — the FR's
   `## Changelog`/body already reflect it → not eligible for another apply, but still worth a
   mirror-reconciliation pass (step 3) in case a prior run's kill landed the FR write but not the
   hub refresh. (c) **neither** → apply it now (steps 1–3). This replaces a bare "is the box
   ticked?" check, which can't tell (b) from a half-applied (c) on a resumed run.

No new state file, ledger, or `status:` value is introduced — the artifacts remain the only ground
truth. A stuck fold-in is never a dead end: the next run of the same skill re-derives exactly
where it left off from steps 1 and 4 above, applies what's missing, and reconciles the rest — safe
to invoke repeatedly, including from a fresh session with no memory of the interrupted one.

## Open Questions wording (all artifacts)

An Open Question gets read cold — by a client, or by whoever picks up the vault days after it was
drafted — with none of the drafting context loaded. **It must be self-contained.** The failure
mode: a question that only makes sense to whoever just wrote it, because it references an internal
number without restating what that number means — e.g. "Does FR4's Organization Experience
narrative-question set *replace* FR-004 FR23's single" (which "FR4"? a functional requirement
numbered 4 inside *this* note, or the `FR-###` artifact id? "FR23's single" — single *what*?). This
applies wherever `/extract-signal`, `/bigin-transform-signal`, or `/enrich-feature` write a
`- [ ] Q: …` line, on an INT note or an FR.

**Format:**

```
- [ ] Q: <How it works today — plain business language, no ids.> <What the new request changed —
  plain business language.> <The one decision needed, as its own question sentence: yes/no,
  A-or-B, or an (a)/(b)/(c) list when there are three or more options.> (owner: client|team)
  (ref: FR-###, BR-###, INT-### — traceability only, safe to ignore when answering)
```

**Rules — content:**

- **Quote or tightly paraphrase both sides in plain business language** — the requirement as it
  stands today, and what the new signal proposes — before asking anything. Never point at a bare
  internal number ("FR4", "FR23", "BR-104") as if it's self-explanatory; if a number is cited for
  traceability, always pair it with what it says ("FR3 — the vendor must submit a W-9 before
  payout"). Where the readability rules below send ids to the trailing `(ref: …)` instead, they
  need no gloss there — that block is pure traceability the answerer skips; the pairing rule
  governs any id that appears in the ask itself.
- **End with one concrete, answerable question** — a yes/no or a named choice ("replace or
  supplement?", "which one wins?") — not a sentence fragment or a dangling clause.
- **One question, one decision.** Don't compress two ambiguities into a single run-on question;
  split them into separate `Q:` lines instead.
- **Never assume the reader has the note open elsewhere.** The question must stand alone even if
  it's the only line anyone reads.

**Rules — readability.** Pairing every id with its meaning is necessary but *not sufficient*: a
question can satisfy every rule above and still be unreadable, because it's written in vault
register — dense with ids, in one long sentence, using vocabulary coined while drafting. So also:

- **Write in the register of the question's `owner`.** `owner: client` means this line will be
  read — often pasted verbatim into an email — by someone outside the vault. No ids in the ask
  itself, and none of the vault's own vocabulary: no *signal*, *CR*, *intake*, *staged*,
  *fold-in*, *bucket*, *FR/BR/INT/PP/EN*. Push every id into the trailing `(ref: …)` parenthetical
  where a reader can skip it. `owner: team` may use ids inline — still always paired with what
  they say.
- **Use only the client's own words for the business concepts.** Never invent a term to compress
  something ("the 20% cap bucket", "the narrative-question set") unless the client or the source
  document actually used it. If you need a name for a group of things, list the things.
- **Three short sentences, and the question is one of them.** Today → what changed → what we need
  decided. Never bury the ask behind a *but*, an em-dash, or a subordinate clause on the end of a
  statement — a reader scanning for "what am I being asked?" must find a sentence that starts as a
  question and ends with `?`.
- **Three or more options → an `(a)/(b)/(c)` list**, each option a complete alternative in plain
  terms. Two options may stay inline ("replace, or keep both?").
- **Say what the answer decides** when the consequence isn't obvious from the question — one short
  clause is enough ("this sets which limit the wallet enforces at checkout").
- **Self-check before writing the line.** Read it once as the `owner` would, cold. If answering it
  requires opening the FR, knowing what a `BR-###` is, or re-reading the sentence to find the
  actual question, rewrite it. A question the human has to decode is a question that sits
  unanswered.

**Before/after** (the id-reference failure):

> ❌ *Does FR4's Organization Experience narrative-question set *replace* FR-004 FR23's single*

> ✅ *In FR-004, the existing Organization Experience question is a single free-text field
> ("Describe your organization's relevant experience"). The new signal proposes a richer
> narrative-question set covering scope, past engagements, and references instead. Should the new
> set **replace** the original field, or should both appear on the form? (owner: client)*

**Before/after** (the readability failure — the ❌ version below satisfies every content rule
above, and was still unreadable to the human who had to answer it):

> ❌ *BR-039's original 20% cap bucket covered supplies, equipment, subscriptions, and
> recreational-activity together. The recent CR (INT-014) gives equipment/supplies their own
> dollar caps (BR-138) and narrows the 20% cap to extracurriculars only (BR-139), but the signal
> never mentions where **subscriptions** now lands — still under the 20% cap (renamed
> "extracurriculars"), moved to a new dollar cap of its own, or dropped as a distinct category
> entirely? (owner: client)*
>
> Four ids in three clauses; "cap bucket", "the CR", "the signal" are vault vocabulary; one
> 60-word sentence with the ask hanging off a *but*; three options run together after a dash.

> ✅ *The program guidelines currently put four kinds of spending under a single ceiling of 20% of
> the award: supplies, equipment, subscriptions, and recreational activities. The recent update
> gave supplies and equipment their own fixed dollar limits, and left the 20% ceiling covering
> recreational activities only — it didn't say what happens to **subscriptions**. Where should
> subscription spending sit now? (a) still inside the 20% ceiling, (b) under its own fixed dollar
> limit — please state the amount, or (c) no longer tracked as its own category. This decides
> which limit the wallet enforces when a student spends on a subscription. (owner: client)
> (ref: BR-039, BR-138, BR-139, INT-014)*

## Signal → artifact mapping

Every `[requirement]`/`[feedback]` signal `/bigin-transform-signal` folds in lands in exactly one
(sometimes two, when it's genuinely both) of these places — never loose in prose:

| Signal is… | Goes to |
|---|---|
| A testable, actionable statement | a new/updated `FR-###` (§ ID scheme) |
| A conditional/policy constraint, feature-level or anchored to one FR | a new/updated `BR-###`, `fr: []` citing the FR(s) it constrains (§ ID scheme, § Entity Data Model) |
| A presentation-only statement — look, layout, tone, copy voice, interaction feel, accessibility affordance — that changes no behaviour | a **design directive**, never an FR line: a `DESIGN-PRINCIPLES.md` row when durable/cross-cutting, a row in its feature hub's `## Design Directives` when feature-scoped, or both (§ Traceability chain's Design chain, § Design Principles Register) |
| A data field/entity described — a thing the business tracks and its attributes | a `proposed` row in `ENTITIES.md`, later promoted to `EN-###` `## Fields` (§ Entity Data Model) — new or existing entity |
| Narrative context — the client's stated why, not yet actionable on its own | `## Problem & Pain Points` as `[problem]` |
| A concrete frustration/cost the client named, with no requirement attached yet | a new `PP-###` in `01-Requirements/PAIN-POINTS.md` (§ Pain Point Register), mirrored on the FR once one exists |

A `[pain-point]` with no attached requirement is not a gap to fill — it's kept on record
(`PP-###`, `Status: open`) until a later signal turns it into an FR/BR line or an epic/story
resolves it, or it just stays as context. Never force a pain point into a functional requirement
it doesn't actually support, and never drop it for lack of a home. A signal can legitimately land
in more than one row at once — e.g. a field-level rule is both an `EN-###` mapping row and, if the
client also gave a reason, feeds that entity's or the citing FR's own context.

## Entity Data Model

A `[requirement]` signal sometimes describes not a behavior but a **thing the business tracks** —
a Vendor record, an Application, a Wallet — and the concrete data it must carry: field names,
types, and relationships. Left to plain FR routing, this either gets buried as a clause inside a
Functional requirement sentence ("the system must capture the vendor's tax ID") or repeated with
drift across every FR that happens to touch the same entity — entities are usually **shared across
features** (a Vendor's fields matter to both a Vendor Management feature and a Payments feature),
so a per-FR field list duplicates and drifts.

`01-Requirements/_entities/EN-<NNN>-<slug>.md` (`type: entity`) is the artifact for this: one
document per business entity, promoted by `/bigin-transform-signal` (Stage 4) from a `proposed`
row in `01-Requirements/ENTITIES.md` the first time an FR/BR actually references it.

**Frontmatter (`_bigin/templates/entity.md`):**
```yaml
---
type: entity
id: EN-
name:
kind:            # actor | data | system
status: proposed # proposed (row exists in ENTITIES.md, no doc yet) -> draft (this doc exists,
                 # fields still settling) -> approved (human confirmed at an FR/BR review gate)
features: []     # every feature slug whose FR(s)/BR(s) reference this entity
updated:
---
```

**Body:**
- `## Fields` — `Field | Type | Required? | Source | Notes`. `Source` cites the Signal Log row (or
  FR/BR) that introduced or last changed the field.
- `## Relationships` — how this entity references others (e.g. "belongs to EN-002 Customer
  (many-to-one)"), each citing the FR/BR it's drawn from.
- `## Changelog` — same convention as every other artifact.

A field-level business rule is **not** a subsection of the entity doc — it's a full `BR-###` file
under `01-Requirements/_brs/` like any other business rule (§ ID scheme), citing the entity's
fields it governs in its own body. An earlier draft of this document described a
`## Field-level Business Rules & Mapping` subsection inside the entity doc, sharing one vault-wide
`BR-###` sequence with `EN-###`; that was never built — `BR-###` is its own independent sequence
(§ ID scheme's Next-ID rule), and there is no per-entity BR subsection.

**Registry:** `01-Requirements/ENTITIES.md` (`type: entities-register`, singleton,
`_bigin/templates/entities-register.md`) —
`EN-### | Entity | Status | Fields (so far) | Features | Notes`, created by `/extract-signal` the
moment a signal describes a data field or entity attribute, with a `proposed` row per entity.
Cluster aggressively — one row per real-world business object, not per field.
`/bigin-transform-signal` promotes a row to its own `EN-###` document; the register keeps the row
afterward as the vault-wide index (mirroring how `FEATURES.md` stays the index once a feature hub
exists).

## Pain Point Register

Every `[pain-point]` signal gets a **`PP-###` id the moment it's extracted** — vault-wide,
numbered like `BR-###` (scan `01-Requirements/PAIN-POINTS.md`, not any FR, since a pain point can
predate its feature's FR) — tracked in `01-Requirements/PAIN-POINTS.md`
(`type: pain-point-register`, singleton, instantiate from
`_bigin/templates/pain-points-register.md`):

| PP-### | Statement | Feature | Source | Status | Proposed solution | Resolved by |
|--------|-----------|---------|--------|--------|--------------------|--------------|

- **Status**: `open` (named, nothing addressing it yet) · `addressed` (a `Resolved by` link exists
  and a human confirmed it's sufficient — this is a judgement call, so it never auto-flips the way
  `needs-clarification` does) · `orphaned` (the feature/FR that would have addressed it went
  `out-of-scope`, or the client explicitly walked it back — never silently deleted).
- **Proposed solution**: a short, plain-language description of the approach addressing it, filled
  in as soon as a requirement/story is drafted with this pain point in mind. Not a separate
  approval-gated artifact — a solution is a fact **about** the row, not a new document.
- **Resolved by**: starts blank or citing whatever's available first (an FR functional-requirement
  line, a `BR-###`), then gets **backfilled** once `/consolidate-prd` produces the epic/story that
  actually implements the solution, since that's the concrete unit of work a PO tracks a pain
  point's resolution against.
- Same append-only discipline as every other register here: `PP-###` is permanent, a row is never
  deleted — a walked-back pain point becomes `orphaned` with an explanation in `Resolved by`.

**Mirrored on the FR** once one exists: the FR's `## Problem & Pain Points` section carries a
matching table with the same `PP-###`, `Status`, `Resolved by` for every pain point anchored to
that feature — the register is the vault-wide source of truth (queryable across features), the FR
section is the same facts for a reader who only has that one FR open.

**Created** by `/extract-signal` the moment a `[pain-point]` signal is extracted. **Solution +
`Resolved by` backfilled** by `/enrich-feature` (FR-level solution) and `/consolidate-prd`
(epic/story backfill). **Status flipped to `addressed`** only by a human.

## Design Principles Register

A `[constraint]` signal sometimes isn't feature-specific at all — "keep it minimal," "use our
brand colors," "our users skew older, avoid tiny tap targets" apply to every feature, not just
whichever FR happens to be open when the client says it. Left to the normal signal→FR routing
above, a cross-cutting preference either gets awkwardly bolted onto one feature's
`## Business Rules` or is lost entirely if no FR exists yet when it's said.

`01-Requirements/DESIGN-PRINCIPLES.md` (`type: design-principles`, singleton, vault-wide) is the
standing register for these. `/extract-signal` appends a row whenever an extracted `constraint`
signal reads as a durable, cross-cutting preference rather than a one-off constraint tied to a
single feature:

- **Feature-specific** visual/interaction constraints ("this donor dashboard should feel warm,
  less corporate") go to that feature hub's own `## Design Directives` section, on the Design chain
  (§ Traceability chain) — **not** onto its FR. An earlier draft of this document routed them to
  the FR; that put untestable presentation language inside approved functional scope and made a
  purely visual note wait behind `/approve-fr` before `/prototype-design` could ever see it. A
  feature-scoped directive that turns out to change behaviour was misrouted and belongs back on the
  FR — see `_bigin/stages/transform/3-routing.md` § The design boundary test.
- **Cross-cutting** preferences (brand, tone, accessibility, interaction, layout, content,
  platform) append a row to `DESIGN-PRINCIPLES.md`: `# | Principle | Why | Category | Source |
  Status | Notes`, citing the INT id like any other signal. A signal can land in both places at
  once if it's stated about one feature but clearly generalizes. An earlier draft of this document
  specified the columns without `Why`, and the register template shipped without `Category` or
  `Status`; the seven-column form above is canonical, and a register file already created with the
  older header keeps it — append rows matching whatever header is on disk rather than migrating a
  live register mid-run.
- Same append-only discipline as `FEATURES.md`/the Signal Log: `#` is permanent, never delete a
  row — a later statement that contradicts an earlier one is a new row, with the old row's
  `Status` flipped to `superseded` (or `rejected` if the client/team explicitly walked it back)
  and `Notes` pointing at what replaced it. Every edit bumps the file's `version` and appends a
  `## Changelog` line, so the register's own history is auditable over time, same as any other
  vault artifact.

Downstream: `/approve-fr` reads it when drafting a PRD section's design-goals content, citing rows
instead of re-deriving the same preference per feature. `/prototype-design` reads it **directly**
(not only via the PRD) as a primary input to any shared design conventions — so it stays
authoritative even if a given PRD section forgot to transcribe a preference, and so a feature that
reaches prototyping before its PRD is finished still produces a prototype consistent with what the
client has said.

## Business Scenarios

A `[requirement]`/`[feedback]` signal sometimes describes a real-world flow that crosses feature
boundaries — a request submitted in one feature, approved in another, settling as a financial
adjustment in a third (not just "this feature calls that API" — an end-to-end sequence a human
would narrate as one story). Left to the normal signal→feature anchor (one slug per signal), each
feature involved gets its own correct slice, but the end-to-end flow itself has no home.

`01-Requirements/SCENARIOS.md` (`type: scenario-register`, singleton,
`_bigin/templates/scenario-register.md`) is the artifact for this — **one
register file**, not one document per scenario:

| SCN-### | Name | Steps (feature: what happens) | Status | Notes |
|---------|------|-------------------------------|--------|-------|

An earlier draft of this document specified one document per scenario
(`01-Requirements/_scenarios/SCN-### <title>.md`) with a diagram and a richer `## Steps` table
citing FR/BR/entity-fields-exchanged per step; what's actually built is the single-register form
above. `/bigin-transform-signal` (Stage 4) creates/updates a row the moment it identifies a signal
describing a genuinely cross-feature flow — each participating feature's hub mirrors a one-line
pointer into its own `## Business Scenarios` section (`- SCN-### <name> (step N of M)`); the
register is the only place the full step sequence is written out. `/consolidate-prd` and
`/prototype-design` would cite/backfill and read from it once they're migrated to the
`01-Requirements/` model (§ Reconciliation notes) — today they don't yet look at it.

## Signal → feature mapping (and what happens when it can't map)

Every signal must anchor to a `01-Requirements/FEATURES.md` slug before it can be staged.

### Declared features (direct intake only) — a floor, not a ceiling

`source: direct` is the one intake path with a human present at capture, so it's the one that can
**ask** which feature(s) the material belongs to instead of working it out later. `/bigin-intake`
offers a multi-select over `FEATURES.md` (skipping is a first-class answer) and records the result
in the note's `declared_features:` frontmatter — **only ever what the user actually named**. An
agent must never populate it from its own reading of the content; that would launder a guess into
a human declaration and break capture-only.

Two feature fields live on an INT note and they are not the same thing:

| Field | Written by | Means |
|---|---|---|
| `declared_features: []` | `/bigin-intake` (direct only), from the user's selection | "The human said, at capture, that this is about these features." Plural, up-front, advisory-but-authoritative. Never rewritten by `/extract-signal`. |
| `feature:` | `/extract-signal`, or a human repairing an unmapped signal | The resolved single anchor — and the repair channel below. Singular, an outcome. |

How `/extract-signal` consumes a non-empty `declared_features:`:

- **Every declared slug is settled — don't re-litigate it.** No "which feature?" open question, no
  `unresolved` row, no `needs-review` tag, no scope-triage question for a signal that plainly
  belongs to one of them. The human already answered; re-asking is the same duplicate-gate problem
  § Feedback handling exists to avoid.
- **A declared slug with no `FEATURES.md` row gets a `proposed` row added** (version bump +
  changelog, `Sources` citing the INT id). This is the single exception to "agents never add scope
  rows unattended" — it holds *only* because the slug came from a human at capture. A slug that
  looks like a typo of an existing row is flagged in the report, never silently remapped to what
  the agent thinks was meant.
- **The scan continues anyway.** The declaration is what the human knew when they typed it, not a
  promise about content they may not have re-read — a note declared `vendor-management` can still
  carry a payments signal. Those anchor normally. This is what makes it a floor rather than a
  ceiling.
- **A declared slug that ends up with no signal anchored to it is reported as a mismatch**, and
  the declaration is left in place. It usually means the content didn't say what the human
  thought — worth their attention, never silently dropped, and never patched over by manufacturing
  a signal to justify it.
- **Empty or absent → nothing changes.** Anchoring runs exactly as it does for every email and
  meeting note, per the rules below.

### When a signal can't map

When no existing row fits and it isn't clearly new scope either, `/extract-signal` never guesses
the anchor:

- Record the proposed anchor candidates (or "none found") on the signal line.
- Add an Open Question (owner: team) — "Which feature does this belong to?" with the candidate
  slugs listed — on the closest FR, or on the source INT note itself if no FR exists yet.
- Park the source INT note `status: needs-clarification` and add `needs-review` to its `tags:` —
  the same surfacing mechanism as any other open question, so it's visible as specifically needing
  a human to map the feature, not just answer a content question.
- The human closes it by writing the correct slug back — as the `A:` answer on the note's Open
  Questions line, or by setting the note's `feature:` frontmatter directly — and ticking the box.
  The next `/extract-signal` pass reads that as the resolved mapping and stages the signal against
  the named feature, creating a new `proposed` row first if the slug doesn't exist yet.

## Feedback handling

Feedback is just intake (`kind: feedback`) — and CR material against an FR can equally well arrive
as an ordinary `kind: requirement` signal from a meeting/email that happens to touch shipped scope.
Either way, `/bigin-transform-signal` applies it to the affected FR/BR **the same way, regardless
of that FR's current status** (hard rule 7 — approval no longer freezes an FR, and neither does
the feature shipping):

- **Update in place, always.** Edit content, bump `version`, log the reason + source `INT-###` in
  `## Changelog`. If the FR was `approved` (or `enriched`/`consolidated`), the same edit also sets
  `status` back to `draft` — un-staging it as feature material (§ Feature material) until the
  human re-approves. Interactively,
  this runs as a discussion round in the FR's `## Discussion`: present the proposed change (quoted
  signal + INT id + proposed edit), the human confirms, the answer folds in. Unattended, the
  proposed change is written into the FR's `## Discussion` and its Signal Log row flips to
  `staged` — never auto-applied without a human confirming — and the FR's `status` moves to
  `needs-clarification` so the pending decision surfaces exactly like any other FR awaiting a
  human look.
- **There is no forking to a new `amends:`-linked sibling FR for this case.** The same FR carries
  its whole history in its own `## Changelog` — whether it's still open, already approved, or the
  feature has since shipped. `amends:` frontmatter is reserved for the rare case where a feature's
  scope genuinely splits into a second, independent decision that doesn't belong in the same
  document; confirm that split explicitly with the human before minting a second FR for one slug —
  never reach for it just because the source FR happens to be `approved`.
- **Removing scope.** If a discussion round concludes the FR's scope — or part of it — should come
  out entirely (the client walked it back, it's no longer wanted), a human sets `status: removed`
  with the reason in `## Changelog` (human-gated like `approved`; an agent may raise this as an
  Open Question, never set the status itself). This is not deletion (hard rule 1): the file, its
  id, and its full history stay intact. Cascade the same as any other edit (below) so every
  downstream artifact that traced to it surfaces as needing a human decision, rather than silently
  going stale with no explanation.
- **Reinstating.** A human can later move a `removed` FR back to `draft` if the scope returns —
  logged in `## Changelog` with why. `/bigin-transform-signal` never does this unattended; a
  signal that looks like "bring this back" is an Open Question for the human, the same as any
  judgement call an agent can't make on its own.
- Either way — cascade: set the downstream PRD/epic/story/prototype that trace (via
  `sources`/`links`) to the affected FR back to `draft` too (a changelog entry on each citing
  the INT id and naming the upstream FR change that triggered it), so stale artifacts surface
  until `/approve-fr`/`/prototype-design`/`/consolidate-prd` re-run.
- Open questions with owner `client` stay listed in the (current) FR's `## Open Questions` for the
  human to raise with the client; answers return through `/bigin-intake` as feedback.

## File naming

`<ID> <short title>.md` — e.g. `FR-012 Bulk invoice export.md`

## Changelog section (all non-intake artifacts)

```md
## Changelog
- 1.0 (2026-07-02) — initial draft from INT-003
- 1.1 (2026-07-05) — INT-009 feedback: export limited to 500 rows
```

## Summary block (FR only — scannability)

Reading a long FR cold means scrolling past open questions, business rules, and prose just to find
out what the note is about. The FR template carries a collapsed summary right after frontmatter,
before `## Business goal`, so a reader gets the gist in one glance without opening the whole note:

```md
> [!summary]- Summary
> 2-3 sentences here.
```

It's a **synthesis, never new content** — same contract as any diagram/visual aid a skill adds: it
illustrates what the note already states, it doesn't add to it. Drafted by `/enrich-feature` when
the FR is first enriched, refreshed by any `/bigin-transform-signal` fold-in that changes the FR's
content (version bump), so it never goes stale relative to the sections below it.

**Write it for a client/PO skimming the note, not for an auditor tracing artifact lineage.**
2-3 short sentences, plain business language:

1. **Source + what changed** — where this came from (INT id, or "a change request against
   FR-XXX") and the concrete thing being added/changed, in business terms (a field, a rule, a
   capability) — not "N functional requirements and BR-104".
2. **Why** — the pain point/business reason, in the client's terms (drawn from `## Business
   goal` + `## Problem & Pain Points`), not a citation of which section it came from.
3. *(only if it changes how the reader should read the FR)* one short clause on what's still
   open — not a restatement of frontmatter status. Omit entirely if there's nothing unusual to
   flag; `status:` and the Open Questions count already show on the note.

**Avoid:** stacking multiple artifact ids in prose (one incidental `FR-XXX`/`amends:` mention is
fine; a chain of `FR-004 … BR-104 … FR-022` reads like a diff, not a description). Narrating the
pipeline ("per the extraction step", "pending enrichment") — the reader doesn't need to know which
skill wrote this. Hedge-y meta phrasing ("leaving the conflicting parts to a separate FR-022") —
say what *this* FR does; a sibling FR's scope belongs on that FR, not narrated here.

**Before/after** (same FR, real case):

> ❌ *This FR is a change request against the already-approved FR-004 (vendor management),
> expanding the vendor profile/application field set based on the client's `CFEF CRM Flow.pdf`
> reference document. It exists because that document revealed additional fields (Website,
> Customer Tags, W-9 flag, Marketable flag, notes fields), a defined 4-value Reimbursement
> Restrictions dropdown, and a much richer Organization Experience narrative-question set beyond
> what FR-004 originally captured. It adds 4 functional requirements and BR-104 (fixing the
> Reimbursement Restrictions value set) as additive detail only, leaving the conflicting parts of
> the same document to a separate FR-022. It still carries 1 open question — whether the new
> narrative questions replace or supplement FR-004's original educational-value field — and is
> `needs-clarification`, pending further elicitation.*

> ✅ *Adds the vendor profile fields the client's `CFEF CRM Flow.pdf` calls for — Website,
> Customer Tags, W-9 and Marketable flags, notes, a 4-value Reimbursement Restrictions list, and
> richer Organization Experience questions — that FR-004's original vendor form didn't capture.
> Open question: whether the new questions replace or add to the existing educational-value
> field.*

Same content, same traceability (still one `FR-004` mention, still names the source document) —
just business-first instead of artifact-first. If a reader wants the artifact-level trace, that's
what `sources`/`amends`/the Changelog are for; the summary's job is "what is this, in plain
terms," not "how does this fit the pipeline."

**Intentionally not on INT** — an intake note is raw capture only; even a purely descriptive
summary is a step toward interpretation this vault deliberately keeps out of `/bigin-intake`. An
INT note's "what is this" question is answered instead by its `## Extracted signals` table once
`/extract-signal` fills it, or by opening the note (they're short — that's the point of raw
capture).

Not currently applied to PRD/Epic/Story/feature-hub either — the feature hub already carries a
one-line description under its `# <Feature Name>` heading for the same purpose. Extend the pattern
to other artifact types only if the same scan-cost problem shows up there.

## Reconciliation notes for this plugin

Concrete gaps between this document and the plugin's actual skills, collected here instead of as
scattered inline caveats — resolve and delete each line as the corresponding skill is migrated.

- ~~**Plugin-internal paths were unreachable at runtime.**~~ **Resolved (plugin 1.2.0).** The rulebook
  and templates are now materialized into the project by `/bigin-new-project`
  (`_bigin/conventions/`, `_bigin/stages/`, `_bigin/templates/`), and every skill, dispatch prompt, and
  template refers to them project-relatively. Anything still pointing at `references/…`,
  `skills/*/SKILL.md`, or `skills/*/template/…` for a file a subagent has to read is a bug. `${CLAUDE_PLUGIN_ROOT}` has exactly one legitimate use in this
  plugin: `/bigin-new-project` § 2, resolving the copy source.
- **`enrich-feature`, `approve-fr`, `prototype-design`, `consolidate-prd` still use the old
  `.bigin/` flat-file layout** (`.bigin/features/FR-<id>-*.md`, `.bigin/PRD.md`,
  `.bigin/prototypes/`, `.bigin/epics.md`, inline `Status:` headings) — not the
  `01-Requirements/_frs/`/`_brs/` model with `status:` frontmatter that `bigin-intake`,
  `bigin-new-project`, `extract-signal`, and now `bigin-transform-signal` already use. This gap
  got wider, not narrower, once `bigin-transform-signal` was rebuilt against the real
  `01-Requirements/` paths: `enrich-feature` reads `.bigin/features/FR-<id>-*.md`, but
  `bigin-transform-signal` now writes `01-Requirements/_frs/FR-<NNN> <Title>.md` — nothing bridges
  the two yet. Until these four are migrated, most of § Feature Hub's "Maintenance contract" past
  `/bigin-transform-signal` and all of § Absorbed describe the target, not the current read/write
  paths.
- ~~**FR/BR status vocabulary decided but not yet applied where it's written down.**~~ **Resolved.**
  `_bigin/templates/fr.md`, `_bigin/templates/br.md`, and that skill's `SKILL.md` now
  all use § Status vocabularies' list (`draft → enriched → approved → consolidated`, plus
  `needs-clarification`/`removed`) and land results on `draft`, never the retired `in-review`.
  Anything still writing `in-review` or `superseded` onto an FR/BR is a bug.
- **Command order mismatch**: this document's Full chain is `PRD → EP → US → UX`, but this
  plugin's actual command order is `/approve-fr` (PRD) → `/prototype-design` (UX) →
  `/consolidate-prd` (Epics/Stories) — UX before Epics/Stories. Decide which order is right for
  this plugin and correct whichever side is wrong.
- **PRD/Epic/Story/UX file granularity is still undecided** — only their status vocab is decided
  (`draft → approved`, § Status vocabularies). This document assumes `PRD-###`/`EP-###`/
  `US-###`/`UX-###` are each their own file with their own id. Today `/approve-fr` writes one
  consolidated `PRD.md`, `/consolidate-prd` writes one flat `epics.md`, and `/prototype-design`
  writes one prototype file per feature with no `UX-###` id. Decide whether to build toward
  per-artifact files (as this document assumes) or formalize the flat-file model instead —
  don't let both readings coexist in downstream skill docs.
- **No front-end app exists yet to consume this vault.** A companion front-end is planned as a
  separate repository (not an Obsidian plugin bundled with this one) — treat every "a front-end
  app" mention above as a future integration point, not a dependency this plugin currently has.
