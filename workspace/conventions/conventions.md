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
| `/bigin-transform-signal` | ID scheme · Use Case · Frontmatter schema · Status vocabularies · Feature Hub · Open Questions wording · Open Questions ↔ status consistency · Feedback handling · Resumable unattended apply |
| `/bigin-generate-prd` | Feature material · Traceability chain · Absorbed · Status vocabularies · Open Questions wording · Pain Point Register |
| `/enrich-feature` → `/consolidate-prd` | Traceability chain · Summary block · Feature material |

**Every stage that writes an artifact also reads § Obsidian-safe markdown.** The vault is read in
Obsidian; a rule broken there is a rule that silently deletes text a human was supposed to see.

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
| UC | **Use case** — the requirement artifact: one user goal, its flow, its branches, its rules mirror, its open questions | 01-Requirements/_ucs | Implemented — its own file, `UC-<NNN> <Title>.md`, drafted/updated by `/bigin-transform-signal`. May span features. Status: `draft → enriched → approved → consolidated`, plus `needs-clarification`/`removed` (§ Status vocabularies). See § Use Case |
| BR | Business rule | 01-Requirements/_brs | Implemented — its own file, `BR-<NNN> <Title>.md`, `uc: []` citing the use case(s) it governs (feature-level if none apply yet). Same status vocab as UC. **The source of the rule** — a UC's `§ 4` is a read-only mirror |
| PP | Pain point (register row, ids cited from a UC's `pain_points:`, no separate per-item file) | 01-Requirements | Implemented |
| EN | Entity data model | 01-Requirements/_entities | Implemented — `/bigin-transform-signal` only cites an `ENTITIES.md` `proposed` row, by name; `/sync-entities` is the only skill that promotes one into its own file, `EN-<NNN> <Entity>.md`, and only once an approved UC (or a BR it mirrors) actually references it. Deferring promotion until after approval means a still-drafting UC never leaves behind an entity doc nobody ended up needing |
| FR | ~~Feature requirement~~ | 01-Requirements/_frs | **Retired**, replaced by `UC-###`. Existing files stay on disk, frozen, carrying `absorbed_by: UC-###`; ids keep resolving and nothing writes there any more (§ Use Case → What it replaced) |
| SCN | ~~Business scenario (cross-feature flow)~~ | 01-Requirements/SCENARIOS.md | **Retired**, replaced by a `UC-###` whose `features:` lists every slug it touches. Existing rows stay, `superseded`, naming the UC that absorbed them (§ Business Scenarios (retired)) |
| PRD | Product requirements doc | 02-PRD | Implemented — **one file per feature**, `PRD-<NNN> <Feature>.md`, written by `/bigin-generate-prd` from that feature's **`approved`** UCs (§ Feature material) plus its `UX-###` design. Granularity is settled: per feature, not per-UC and not one vault-wide document (§ Reconciliation notes). A business-flow document, never a technical spec — its six hard rules live in that skill's `SKILL.md`, not here, the same way design's live in `design-conventions.md`. Status: `draft → approved`, `approved` human-only (§ Status vocabularies). Carries `absorbed: [UC-###@version]`, which is what makes PRD drift detectable (§ Absorbed) |
| EP | Epic | 03-Epics-Stories | **Planned** — `/consolidate-prd` today writes one flat `epics.md`, not per-`EP-###` files. Same `draft → approved` status vocab once split out |
| US | User story | 03-Epics-Stories | **Planned** — stories live nested under their epic in `epics.md` today, not as their own `US-###` files. Same `draft → approved` status vocab once split out |
| UX | UI/UX spec | 04-UIUX | Implemented — one `UX-<NNN> <Feature>.md` per feature, written by `/bigin-generate-design` from the feature's UC(s). **Its rules are not in this file:** the design rulebook is `_bigin/conventions/design-conventions.md`, deliberately separate, and it carries UX's own status vocabulary (`draft → needs-clarification → accepted`), paths, and hard rules. The retired `/prototype-design` wrote `<feature-id>-prototype.md` with no id |

Next-ID: scan the relevant folder for the highest existing number and increment —
`01-Requirements/_ucs/`, `_brs/`, `_entities/` for `UC-###`/`BR-###`/`EN-###` respectively. Each is
its **own** independent sequence (`/bigin-transform-signal`'s actual numbering rule) — an earlier
draft of this document specified one shared vault-wide sequence across `BR-###` and `EN-###`; that
was never built, and the per-directory scan above is what's real. `PP-###` scans
`01-Requirements/PAIN-POINTS.md`, not any UC, since a pain point can predate its feature's use case.
`UC-###` numbering ignores `_frs/` entirely — the two sequences are unrelated, and a UC that absorbs
`FR-007` does not become `UC-007`.

**Ids inside a use case** — a flow step's `S#`, an alternative flow's `A#`, an exception flow's
`E#` — are minted per UC, in mint order, and are **permanent**: never reused, renumbered, or deleted
(§ Use Case → Step ids). They are the citation target that replaced per-statement `FR-###` ids, so a
rule, a story, a test, or a prototype screen refers to `UC-012 S4`.

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
canonical entity list. `/extract-signal` files a `proposed` row the moment a signal describes one;
`/sync-entities` points a row at its promoted `EN-###` doc once one exists. Mirrors `FEATURES.md`
(see § Entity Data Model). Also singleton, vault-wide: `01-Requirements/PAIN-POINTS.md`
(`type: pain-point-register`) — the vault-wide pain-point register (see § Pain Point Register).

**Planned** working file: `00-Inbox/_extract-signal/AGENDA <date>.md` (`type: refine-agenda`) — a
per-batch progress tracker. Not built yet; `extract-signal` currently reports batch progress
inline (§ Step 4 of its `SKILL.md`) rather than persisting an agenda file.

## Frontmatter schema (all artifacts)

```yaml
---
id: UC-012
type: use-case           # intake | use-case | business-rule | entity | prd | epic | story | uiux
kind: requirement        # intake only: requirement | feedback | mixed | info (ops/admin — never refined)
title: Export invoices in bulk    # a use case's title is its GOAL, as a short active verb phrase
status: draft            # vocabulary is per artifact type, not one shared list — see
                         # § UC/BR status below for UC/BR, § PRD/Epic/Story status for those,
                         # and § Entity Data Model for EN. An intake note's own status vocabulary
                         # (raw | needs-clarification | in-review | consumed) is separate again —
                         # see § Intake capture & the question loop.
version: 1.0
synced: true             # use-case only: false from the moment /approve-uc sets status: approved,
                         # until /sync-entities has promoted/extended entities: [] and refreshed the
                         # feature hub(s) for this UC (§ Entity Data Model). Meaningless otherwise.
level: user-goal         # use-case only: summary | user-goal | subfunction (§ Use Case)
scope: Bigin Portal      # use-case only: the system under design, black-box
primary_feature: invoicing        # use-case only: the ONE slug that owns the file — write-ownership
features: [invoicing]    # use-case only: every slug this UC touches, primary first. A UC may span
                         # features; `feature:` (singular) is what every OTHER artifact type carries
feature: invoicing       # every non-use-case artifact: the stable slug shared across the chain
uc: []                   # business-rule only: the UC-### id(s) this rule governs
brs: []                  # use-case only: BR-### ids mirrored read-only in its § 4
entities: []             # use-case only: EN-### ids its steps reference
pain_points: []          # use-case only: PP-### ids this workflow exists to resolve (ids only)
sources: [INT-003]       # upstream links
links: [PRD-002]         # downstream links
attachments: []          # use-case only: vault-relative paths to source documents
                         # (e.g. 00-Inbox/_attachments/INT-012/spec.docx) — /bigin-transform-signal
                         # copies these from consumed INT notes so the feature's material is complete
absorbs: []              # use-case only: FR-### / SCN-### ids this UC took over (migration only)
absorbed_by:             # retired FR only: the UC-### that took this FR's content over
source_ids: []           # intake only: email provider's conversation+message ids (Outlook, or Spark thread id) /
                         # meeting provider's meeting id (Fathom, Spark, or Firefly) — re-run dedup; see
                         # `email_provider`/`meeting_provider` in `_bigin/system/project.md`
raw_sources: []          # intake only: manifest of ## Raw's blocks, one per "### SRC-n" —
                         # "SRC-1 · transcript · <ref>". /extract-signal's read plan; a source
                         # missing here is never read (§ Intake capture & the question loop)
tags: []                 # intake only: e.g. needs-review (unknown sender/invitee)
owner: team
updated: 2026-07-03
---
```

**`amends:` is retired along with `FR-###`.** It existed for the rare case where one feature's scope
split into two independent decisions that couldn't share a document. A feature carrying several
genuinely distinct user goals now simply carries several use cases, each with its own id — that is
normal rather than exceptional, so there is nothing left for the field to mark. A pre-migration FR
that still has it keeps it as history.

**Quote any free-text scalar.** `title:`, `source_ref:`, `name:`, `scope:` and every other
human-worded value goes in double quotes unless it is a bare slug, id, number, or date. Unquoted
YAML loses or rejects ordinary prose, and Obsidian responds by dumping the whole frontmatter into
the note body as raw text:

```yaml
source_ref: Kickoff meeting #3 notes     # → "Kickoff meeting"  (everything from # is a comment)
title: UC-008: Review and approve        # → parse error, frontmatter renders as body text
title: [Draft] Review flow               # → parse error, read as a list
```
```yaml
source_ref: "Kickoff meeting #3 notes"   # correct
title: "UC-008: Review and approve"      # correct
```

## Obsidian-safe markdown (all artifacts)

Every artifact this plugin writes is read in Obsidian. Obsidian renders raw inline HTML and uses
GitHub-flavoured tables, so four things in ordinary BA prose delete or corrupt content **silently** —
the note looks finished, and the missing part is invisible rather than obviously broken.

1. **Never leave a bare `<…>` in body text.** Obsidian parses `<name>`, `<NNN>`, `<YYYY-MM-DD>`,
   `<Goal as a short verb phrase>` as HTML tags and renders **nothing** — in Reading view *and*
   Live Preview. Backtick every placeholder or angle-bracketed literal: `` `<NNN>` ``. This matters
   most for a slot an agent left unfilled: bare, it renders as blank and reads as done.
   (Frontmatter and fenced code blocks are exempt — neither is parsed as markdown.)
2. **Never put a raw `|` inside a table cell.** It ends the cell, so that one row gains a column and
   every cell after it shifts. Join alternatives with `/` or ` · `, or escape as `\|`. This is why
   an unresolvable feature anchor reads `unresolved — candidates: a / b`
   (§ When a signal can't map).
3. **One line per table cell.** GFM has no multi-line cell. Long System Response text stays one
   line and wraps; if it genuinely needs a break, use `<br>`. A literal newline splits the table.
4. **Only real questions are checkboxes.** A `- [ ] Q:` line in an artifact body is counted by
   § Open Questions ↔ status consistency, so a *format example* belongs inside the template's
   guidance comment, never in the body — instantiating it otherwise mints a phantom open question
   and renders an empty checkbox.

**Instantiate the structure, not the guidance.** A template's `<!-- … -->` blocks are the schema
spec for whoever writes the artifact; they are not artifact content. Copy the frontmatter keys,
headings, and table headers — drop the guidance comments. The rules they restate live in
`_bigin/stages/` and in this file, which is where a later stage looks them up anyway. Carrying them
into the artifact costs every downstream stage the tokens to re-read them on every open, and leaves
them visible in Obsidian's Live Preview. Retain only a comment that records something about *this*
artifact (why a section is deliberately empty, for instance).

## Use Case

`01-Requirements/_ucs/UC-<NNN> <Title>.md` (`type: use-case`, instantiate from
`_bigin/templates/use-case.md`) is **the** requirement artifact and the unit a human reviews and
approves. One use case is one user goal: an actor, a trigger, the flow that delivers the goal, the
branches that can happen instead, the rules that govern it, and the questions still open about it —
in one document.

It replaced `FR-###`, which was one file per testable statement. That was faithful to the signal and
unreviewable: a client reading "the system must capture the vendor's tax ID" cannot tell whether the
workflow they care about holds together. Use-Case 2.0 puts it directly — a use case is *the context
for a set of related requirements*, and the set of all use cases is the system's functional
requirements. The requirements didn't go anywhere; they acquired the context that makes them
approvable.

**Structure** (the numbered sections are the reviewable document; the rest is machinery):

| Section | Holds |
|---|---|
| `## 1. Context & Metadata` | Primary/secondary actors, business need, trigger, pre-conditions, success **and failure** post-conditions |
| `## 2. Main Success Scenario` | The happy path as a step table: `Step` (an `S#` id) · `Actor Action` · `System Response & Validation` |
| `## 3. Alternative & Exception Flows` | Optional. `A#` alternatives and `E#` exceptions, each with a branch-point `S#`, a condition stated as a detected fact, and an ending |
| `## 4. Business Rules & Compliance Constraints` | A **read-only mirror** of `BR-###` files: id, short statement, and the enforcement point (which `S#` the rule bites at) |
| `## 5. Open Questions & Decision Log` | The canonical `- [ ] Q:` list for what is still open, plus a decision-log table of settled items with speaker context |
| `## 6. Special Requirements & Related Information` | Optional. Workflow-scoped non-functional constraints, priority, frequency, performance target |
| `## Discussion` · `## Domain Concerns` · `## Changelog` | The staging gate, `/enrich-feature`'s findings, and history |

**Goal level.** `level:` is `user-goal` (the default — real work, one sitting, 3–9 main-flow steps,
passing Cockburn's *boss test*), `summary` (several user goals composed, only ever to group UCs that
already exist), or `subfunction` (a step sequence several UCs share, written once). A "use case" that
is a single validation is a step inside someone else's goal, or a `BR-###`.

**Step ids are permanent.** An `S#`/`A#`/`E#` is minted in mint order and never reused, renumbered, or
deleted; **row order is the flow order**, so a step inserted between `S4` and `S5` gets the next unused
id and sits in the third row. Non-sequential ids are correct. Positional numbering was rejected because
a step number is cited from at least four places — an extension's branch point, a rule's enforcement
point, a Signal Log `Destination`, and later a story or prototype screen — and renumbering would
invalidate all of them silently. That is the same failure the retired `SCN-###` register had with
`(step N of M)`. A removed step keeps its row and id, marked removed with the reason, so every citation
still resolves.

**A use case may span features.** `features: []` lists every slug it touches, and `primary_feature:`
names the one that **owns the file** — the feature whose actor holds the goal. Ownership is a
write-ownership fact, not importance: only that feature's `/bigin-transform-signal` subagent writes the
file, because Stage 3 fans out per feature and a shared UC would otherwise have concurrent writers. A
change reported from a participating feature is applied by the orchestrator in Stage 4
(`_bigin/stages/transform/3-lane-uc.md` § Ownership). Every participating hub carries the same
`## Use Cases` pointer.

**A feature may carry several use cases** — one per genuinely distinct user goal. This is the deliberate
break from the retired one-FR-per-feature norm: four goals means four UCs, and that is not
fragmentation. What a feature must never carry is two use cases for the same goal.

**Rules stay outside.** `## 4` is a mirror; `BR-###` under `01-Requirements/_brs/` is the source, citing
`uc: []`. BABOK's *Use Cases and Scenarios* technique is explicit that rules are captured separately so
a rule change does not force a use-case change — and one rule routinely governs several workflows, so
no single one of them can own it. The one fact the mirror adds is the enforcement point.

**Updated many times, never re-forked.** New signals keep arriving for the life of a feature; each one
edits the UC in place (version bump + `## Changelog`, hard rule 7 — approval doesn't freeze it), staged
through `## Discussion` and folded in after the human gate. A use case filled only as far as pass 2 is
not defective: Cockburn's own template guidance is to fill it in several passes, and Use-Case 2.0 starts
a narrative as a bulleted outline before it becomes a table.

**What it replaced:** `FR-###` (retired, frozen, `absorbed_by:`) and `SCN-###` (retired — a
cross-feature UC is a business scenario that also carries actors, branches, rules, and a review gate).
Unchanged: `BR-###`, `EN-###`, `PP-###`, and design directives, which still bypass the UC entirely.

The reasoning behind each of these choices, with sources, is in this plugin's
`skills/bigin-transform-signal/references/use-case-standard.md` — read it before changing the template,
not during a run.

## Status vocabularies

There is no single shared `status` list across every artifact type — each type has its own, sized
to what that artifact actually needs to track. All of them share one discipline, though:
**status can move freely, in either direction.** None of these are a strict forward-only gate —
hard rule 7 means a later edit can knock a `consolidated` UC back to `draft`, an `approved` PRD
back to `draft`, and so on. Treat every arrow below as "can move to," never "can only move
forward to."

**UC/BR** (`01-Requirements/_ucs/`, `01-Requirements/_brs/`):

`draft → enriched → approved → consolidated`, plus two side-states reachable from any of those
four:

| Status | Meaning |
|---|---|
| `draft` | Content exists — created or last folded in by `/bigin-transform-signal` — but hasn't been through `/enrich-feature` yet. The default resting state. |
| `needs-clarification` | At least one unresolved `- [ ] Q:` line in the artifact's question list — a UC's `## 5` **Still open**, a BR's `## Open Questions` (§ Open Questions ↔ status consistency's invariant — unchanged, just now one value in this list rather than sitting alongside a separate `in-review`). Once every question resolves, status moves to whatever it would otherwise be — `draft` if it hasn't been enriched yet, `enriched`/`approved`/`consolidated` if a later-stage edit is what raised the question. Never a fixed placeholder. |
| `enriched` | `/enrich-feature` has run: domain research + entity mapping done, concerns resolved or accepted as risk. |
| `approved` | A human has approved it via `/approve-uc`; it's feature material (§ Feature material) and `/bigin-generate-prd` will fold it into its feature's PRD on the next run. Epics/stories still wait on a migrated stage (§ Reconciliation notes). |
| `consolidated` | `/consolidate-prd` has merged prototype-driven changes back and generated its epic/story. The UC's pipeline is complete — until new feedback lands. |
| `removed` | A human decided this UC/BR is no longer relevant/wanted (§ Feedback handling's "Removing scope") — human-gated like `approved`, never set by an agent. Not deletion (hard rule 1): the file, id, and history stay intact. |

An earlier draft of this document specified `raw | draft | in-review | needs-clarification |
approved | superseded | removed` as one shared vocabulary for every artifact type; that's
superseded by the per-type lists here. `in-review` and `superseded` are retired for UC/BR — a
resolved `needs-clarification` now returns to whatever stage the artifact was already at (no
placeholder "reviewed" state needed), and there's no separate "old version" state to track since
hard rule 7 already means every edit lands in place, not as a fork.

**PRD / Epic / Story** (`02-PRD/`, `03-Epics-Stories/`): `draft → approved`, where `approved` means
ready for / queued into development — nothing more granular than that. **PRD is real now**: one file
per feature, written by `/bigin-generate-prd`, which only ever writes `draft` — a human approves a PRD
the same way a human approves a UC (hard rule 4). Epic/Story are still **Planned** as their own files
(see § Reconciliation notes).

**EN** (entities): its own vocab, `proposed → draft → approved`, plus one side-state — see § Entity
Data Model. Simpler because an entity doc is a field list assembled from already-approved-adjacent
signals, not a thing that itself needs an `enriched`/`consolidated` pipeline pass. The side-state is
`merged`: an attribute-shaped doc whose fields have been folded into the business object that owns
them, carrying `merged_into: EN-###` and a one-line pointer body. Never deletion — the id stays
resolvable for anything that already cites it (§ Entity Data Model, A fragment already on disk).

**INT** (intake notes): `raw | needs-clarification | in-review | consumed` — see § Intake capture
& the question loop and `/bigin-intake`'s own queue logic. Unrelated to the UC/BR list above;
don't conflate the two just because both use `needs-clarification`.

## Traceability chain

`/bigin-generate-prd` and `/consolidate-prd` (Epics/Stories) branch on the UC's `primary_feature:`
slug looked up in `01-Requirements/FEATURES.md` — the feature's `Status` there decides which of two
valid chains applies. `/approve-uc` itself doesn't branch on this: it approves the UC regardless of
which chain the feature will take, and stops there (§ Feature material):

- **Full** — feature `proposed` / `committed` / `not-built` (new scope):
  `INT → UC/BR → PRD → EP → US → UX`.
- **Lightweight CR** — feature already `built` (a change/fix/improvement on something shipped):
  `INT → UC/BR → US → UX`, skipping PRD and EP. The US cites the UC directly in `sources` instead
  of an EP, and the UC's `links` points at the US id(s) instead of a PRD id.

  A UC spanning several features whose `Status` values disagree takes the chain of its
  `primary_feature` — the feature that owns the goal — and the disagreement is worth naming in the
  report rather than resolving silently per participating feature.

  Cutting the epics and stories is where Use-Case 2.0's **slices** belong: a slice is one or more of a
  UC's flows taken together as a work item of clear value, basic flow first, then the alternative and
  exception flows. `/bigin-transform-signal` never slices anything — this is guidance for
  `/consolidate-prd` once it migrates.
- **Design** — a presentation-only signal, at any feature status: `INT → design directive → UX`,
  skipping UC, PRD, EP, and US entirely. A statement about look, layout, tone, copy voice,
  interaction feel, or an accessibility affordance produces **no functional scope**, so there is
  nothing for a PRD section to carry and nothing for a story to decompose. It becomes a directive
  in one of two places — a `DESIGN-PRINCIPLES.md` row when it's durable and cross-cutting, or a row
  in its feature hub's own `## Design Directives` section when it's scoped to one feature — and
  `/bigin-generate-design` reads both directly. The directive carries no id of its own; its
  traceability runs through the originating Signal Log row's `Destination` cell.

  The chain is chosen by a strict test, not by the client's phrasing: **if a tester could write a
  pass/fail assertion for it that never mentions appearance, it is UC or BR, not a design
  directive** — "ask for confirmation before deleting" adds a step to a flow and takes the Full or
  CR chain, however visual the request sounded. An ambiguous signal takes the UC chain, because an
  over-routed step is caught at the human gate while an under-routed directive skips the gate.
  `_bigin/stages/transform/3-lane-design.md` and `_bigin/stages/transform/3-routing.md` hold the
  boundary test and the destination rules.

**Partly live.** The **PRD stage distinguishes the two chains**: `/bigin-generate-prd` reads the
`FEATURES.md` row's `Status` and skips a `built` feature, because the CR chain has no PRD in it —
writing one anyway is how a chain quietly changes. It stamps `chain:` with which one applied. What is
still **Planned** is the CR chain's *destination*: nothing cuts the `US-###` a CR is supposed to land
in, so a CR against a shipped feature today ends at its reviewed UC plus its design, and the story is
cut by hand. The **Design chain is live**: `/bigin-transform-signal` files directives to both
destinations, and `/bigin-generate-design` reads both — `DESIGN-PRINCIPLES.md` and each hub's
`## Design Directives` — plus the UC itself, and writes the `UX-###` the chain ends at. It runs off
`UC-###` directly and needs no PRD, so a design-only feature and a feature whose PRD isn't written
yet both reach `UX` normally. See § Reconciliation notes for the stages still on the old layout.

Every link in the chosen chain must resolve; if one can't be established, add an Open Question
instead of guessing.

The feature slug is the horizontal anchor across the chain: every slug in a UC's `features:` must
exist as a row in `01-Requirements/FEATURES.md`. New intake about a mapped feature updates the
relevant use case **in place, at any status** (hard rule 7, § Feedback handling) — approval doesn't
freeze it, and neither does the feature shipping — never as an unrelated parallel UC for the same goal.

A cross-feature flow is **not** a fork of this chain and no longer an overlay artifact of its own: it
is one `UC-###` listing every participating slug in `features:`, running the chain of its
`primary_feature`. The `SCN-###` register that used to annotate how several per-feature chains
composed is retired (§ Business Scenarios (retired)).

## Absorbed — the reprocess trigger (**Planned**)

`sources:` answers *"which upstream artifacts does this one trace to?"* — a permanent,
never-pruned traceability record (hard rule 3). It cannot answer *"is this artifact still
current?"*, and since hard rule 7 nothing else could either: a CR edits an approved UC **in
place** — same id, bumped `version`, no new id anywhere — so a PRD section that cites `UC-007`
keeps looking covered no matter how far `UC-007`'s content has since moved. The failure mode this
guards against: new intake updates a UC, the human re-approves it, and the feature's
PRD/epics/prototype sit stale from the cascade — visually identical to freshly drafted work
awaiting review, with nothing anywhere saying "the downstream steps need to re-run."

**`absorbed:` is the record that would close it, once built.** Every artifact downstream of
another would carry it:

| Artifact | `absorbed:` entries | Written by |
|---|---|---|
| PRD | `UC-###@version` for each approved UC folded into it, plus `UX-###@version` in `design_absorbed:` for the design it reported | `/bigin-generate-prd` — **implemented**, re-stamped whole every run |
| Epic/Story | `PRD-###@version` (or `UC-###@version` on the lightweight path) it decomposes | `/consolidate-prd` |
| Prototype | `UC-###@version` / PRD section version it designed from | `/bigin-generate-design` |

**The rule, once implemented: an artifact is stale when an upstream it *cites* has a current
`id@version` that its `absorbed:` doesn't list.** Two states, don't conflate them:

- **Never processed** — the upstream id appears in no downstream `sources:` at all. The
  downstream step simply hasn't run for it yet.
- **Processed, then drifted** — cited, but the version moved on. This is the re-approved-CR case,
  and the one that's invisible without this field.

Whoever produces an artifact **re-stamps** its `absorbed:` on every run — that's what makes this
self-healing rather than another mirror to go stale: there is no separate counter, and a re-run
cannot leave a false "current" claim behind. Two of the three rows above are live —
`/bigin-generate-design` for `UX-###` and `/bigin-generate-prd` for `PRD-###`, so "this design is
stale" and "this PRD has drifted from its use cases" are both detectable today. The epic/story row is
still planned: until it's built, treat any UC edited after its feature's epics were cut as needing a
manual re-check, and note that explicitly in the report rather than assuming they're still accurate.

## Feature material (the approve → process handoff)

Approval converts a UC from *work in progress* into **staged material on its feature**:

- A UC with `status: approved` **is** feature material — no extra flag. Everything sharing its slug
  aggregates into the feature's material set: the approved UC(s) with their BRs, resolved discussion,
  and `attachments`, plus the source INT notes. A cross-feature UC is material on every feature in its
  `features:` list.
- Only `approved` UCs qualify as material. Feedback that touches a UC — at any status, including
  already-`approved` material, before or after the feature ships — is applied **in place** and
  sets it back to (or keeps it at) `draft`/`needs-clarification` (hard rule 7: approval
  doesn't freeze a UC). Feedback that touches an already-approved UC therefore **does**
  un-stage it, the same way it would for any other status: the edit lands in the same UC (version
  bump + changelog citing the source), and it drops out of the feature's material set until the
  human re-approves it. A feature carries as many UCs as it has distinct user goals, each staged as
  material only while it is currently `approved` — so a feature can be part-approved, and that is a
  real, useful state rather than a defect.
- Humans gate `approved` (hard rule 4) — an agent never sets it; `/approve-uc` is the point where
  a human confirms and the status flips.
- **What consumes the material:** `/bigin-generate-prd` folds a feature's currently-`approved` UCs
  into `02-PRD/PRD-<NNN> <Feature>.md` and stamps `absorbed: [UC-###@version]` (§ Absorbed), so a
  part-approved feature yields a PRD covering exactly what is approved, with the rest listed as
  pending scope. It reads the UC's **own** `status:`, never a hub table, and it changes no
  requirement — approval stays the only gate. `/bigin-generate-design` needs no approval at all and
  runs off any UC with a main flow.
- **Planned** — a richer engagement (a front-end dashboard, a workflow picker per feature) may
  eventually replace the fixed `/enrich-feature → /approve-uc → /bigin-generate-design →
  /consolidate-prd` pipeline described here with something that dispatches per-feature by need.
  Not built today; the fixed order is what every feature runs.

## Feature Hub

`01-Requirements/_features/<slug>.md` (`type: feature-hub`) is the single note that shows
everything about one feature, and the file to hand an agent when saying "work on `<slug>`".
`FEATURES.md` stays the canonical index (one row per feature, the anti-fragmentation anchor); the
hub is the rich per-feature view generated from the same underlying artifacts, so nothing here is
ever hand-authored content — it's always assembled/refreshed from the UC(s), INT sources, PRD
section, epics/stories, and prototype that already exist for that slug.

**Frontmatter:**
```yaml
---
type: feature-hub
feature: <slug>
name:           # display name — mirrors the FEATURES.md row's Feature column. This is the source
                # of truth for any consumer (this plugin's own skills, or a front-end app) reading
                # Slug/Feature/UC/Code areas/Sources — read from this frontmatter, not by parsing
                # FEATURES.md's table (§ Feature Map format)
status: <mirrors the FEATURES.md row's Status at last refresh>
uc: []          # every UC-### id this feature owns OR participates in — one per distinct user
                # goal, so several is normal. A cross-feature UC appears on every participating
                # hub's list; ## Use Cases says which of them owns it. Oldest first; [] before the
                # first use case is drafted. Written by /bigin-transform-signal
br: []          # every BR-### id this feature has ever had, same discipline as uc: above —
                # written by /bigin-transform-signal
fr: []          # RETIRED — pre-UC FR-### ids, kept so old ids resolve. Nothing writes here
code_areas: []  # mirrors the FEATURES.md row's Code areas column (project_mode: ongoing only)
sources: []     # mirrors the FEATURES.md row's Sources column — INT-###/document ids/paths
prd:            # PRD-### id, or blank — set by /bigin-generate-prd, one PRD per feature
epics: []       # EP-### id(s) — Planned; today epics.md has no per-epic id to cite
stories: []     # US-### id(s) — Planned, same as above
uiux:           # UX-### id, or blank — Planned; today this would point at the prototype file path
entities: []    # EN-### id(s) this feature's UC(s)/BR(s) reference — [] until one exists.
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
- `## Signal Log` — the append-only register every downstream process reads. One row per
  **functional theme**, in landing order:

  | # | Signal | Type | Source | Status | Destination | Notes |
  |---|--------|------|--------|--------|--------------|-------|

  - **A row is a theme, not a signal.** Signals from one `INT-###` describing the same rule, flow,
    or decision file as a single row — `Signal` reads `**<Theme>** — <detail>; <detail>; <detail>`
    with every claim kept as its own clause, `Type` joins the member types with ` + `, and `Source`
    cites the note row numbers it covers: `INT-014 #3, #5, #7 — Jane Doe 2026-08-05`. Those numbers
    are the trail back to the note's `## Extracted signals`, which stays a flat one-row-per-signal
    raw record — **the two tables' row counts are not meant to match**, and anything comparing them
    is checking the wrong thing. Signals never merge across notes, across `Status` (only `new`
    consolidates), across the design/behaviour boundary, or when they contradict each other. A
    theme of one is normal. Full rules: `/extract-signal`'s `3-filing.md`
    § Step 2 — File to the Feature Hub.
  - **`#` is permanent** once assigned, like a `BR-###` number — never renumbered or deleted. A
    conflicting or superseding signal is always a **new row**; the old row's `Status`/`Notes` gets
    updated to point at the row that superseded it. History is never rewritten in place.
  - **`Status` values**: `new` (just landed, not yet triaged) · `held` (anchored to the feature, no
    UC exists yet — resting state pre-UC, no gate, no urgency; once a UC exists, a new signal
    against it moves straight to `staged` rather than resting here, regardless of the UC's status
    — hard rule 7, approval no longer freezes it) · `staged` (a proposed change sitting in a UC's
    `## Discussion`, not yet applied) · `applied` (folded into UC content) · `question` (the signal
    *is* an open question, not a requirement — tracked until answered) · `conflict` (contradicts
    an earlier row — needs human resolution before either can be applied) · `superseded` (an older
    row a resolved conflict/newer decision overrode) · `rejected` (explicitly out of scope). This
    plugin's `extract-signal` skill only ever writes `new`/`question`/`conflict`/`rejected` when
    filing a fresh signal (§ its own `3-filing.md`) — `held`/`staged`/`applied`/
    `superseded` describe a signal's relationship to a UC, which is `/bigin-transform-signal`'s
    job to set, not extraction's.
  - **"Processed" = `applied` \| `superseded` \| `rejected`. "Not yet processed" = everything
    else** (`new`/`held`/`staged`/`question`/`conflict`) — this is the queue a human or agent works
    from, not a percentage-done bar.
  - **Conflict handling**: when a new signal contradicts a `held`/`staged`/`applied` row, add the
    new signal as its own row with `Status: conflict`, citing the row number(s) it conflicts with
    in `Notes`. Raise an Open Question (never guess which one wins) on the UC it belongs to (its
    most recent open one, if any exist; otherwise the closest applicable UC) or on this note if
    none exists. Once the human answers, the losing row flips to `superseded` (`Notes: "superseded
    by #N, resolved <date>"`), the winning row flips to `staged`/`applied`, and the content updates
    **in place** (version bump + changelog), regardless of whether that UC is still unapproved or
    already `approved` (hard rule 7 — an approved UC's fold-in also flips it back to `draft`).
- `## Use Cases` — one row per `UC-###` in this hub's `uc:` list: `UC | Goal | Role | Status`, where
  `Role` is `owns` (this feature is the UC's `primary_feature`) or `participates`. A cross-feature UC
  appears on every participating hub with the same id — that is the artifact working, not duplication
  to fix. **No step numbers or ranges**: the UC file is the only place the flow is written out
  (§ Business Scenarios (retired) for why). Written by `/bigin-transform-signal` Stage 4.
- `## Requirement Readiness` — a refreshed **snapshot for orientation, not the gate itself**:

  | Artifact | Status | Ready for next step? | Blocking |
  |----------|--------|------------------------|----------|

  One row per UC/BR touching this feature — a feature with four distinct user goals gets four UC rows,
  oldest first, which is normal rather than fragmentation (§ Use Case). The
  authoritative gate for `/enrich-feature`/`/approve-uc`/`/bigin-generate-design` is always each UC's
  own live frontmatter `status` (§ Feature material) — this table just saves a human or agent from
  having to open every UC to see what's ready; a skill still checks the UC directly before
  proceeding, never trusts a possibly-stale table alone. An `approved` UC can still receive new
  signals later (hard rule 7 — approval doesn't freeze it); when that happens it's applied in
  place via the normal fold-in flow the next time `/bigin-transform-signal` touches this feature,
  not held in a separate backlog — note it here the same way as any other pending change
  ("approved — N new signal(s) since approval, not yet run through `/bigin-transform-signal`").
- `## Related Documents` — the UC(s)' `attachments:` list.
- `## Domain Research` (**Planned**) — one entry per domain-research run for this feature,
  appended only by `/enrich-feature` when the feature's enrichment needed external grounding it
  can't get from client signals alone (a regulated/compliance domain, a named third-party
  platform/API's real behavior, industry-standard practice) — most features never populate this.
  Each entry: date, topic, one-line summary of key findings, link to the full report under
  `01-Requirements/_research/<slug>/`. Not built yet — `/enrich-feature` currently appends its
  findings straight into the UC file's own `## Domain Concerns` section instead of a hub-level log.
- `## Business Scenarios` (**retired**) — pre-UC `SCN-###` pointers, kept as history. Cross-feature
  flows are use cases now and live in `## Use Cases` above (§ Business Scenarios (retired)). Never add
  a row; omit the section entirely on a new hub.
- `## Entities` — every `EN-###` this feature's UC(s)/BR(s) reference, with each entity's current
  status. See § Entity Data Model.
- `## Pain Points` — a table mirroring this feature's rows from `01-Requirements/PAIN-POINTS.md`:
  `PP-### | Statement | Status | Proposed solution | Resolved by` (§ Pain Point Register). Empty
  until a `[pain-point]` signal anchors here.
- `## PRD` — link + status, or "not started." Refreshed by `/bigin-generate-prd` together with the
  `prd:` frontmatter field: `[[PRD-<NNN> <Feature>]] — <status>, N capabilities, M pending`.
- `## Epics & Stories` — table of epic/story ids with status, or a pointer into `epics.md` until
  `EP-###`/`US-###` exist as their own ids.
- `## Design Directives` — feature-scoped presentation directives on the Design chain (§
  Traceability chain): `# | Directive | Source | Status | Notes`, `#` permanent and append-only
  like the Signal Log, `Status` one of `open` / `reflected` / `superseded` / `conflict`. Written by
  `/bigin-transform-signal`'s design lane; read by `/bigin-generate-design` as the feature's
  presentation brief (**Planned** — that skill doesn't read it yet, § Reconciliation notes). Empty
  for most features. Durable, cross-cutting preferences go to `DESIGN-PRINCIPLES.md` instead, or as
  well (§ Design Principles Register).
- `## Prototype` — link + status, or "not started." (The hub template calls this section
  `## UX Spec`; treat the two names as the same section until one of them is renamed.)
- `## Open Questions / Gates` — every Signal Log row with `Status: question` or `Status: conflict`,
  plus every open UC's `## 5` **Still open** lines and every open BR's `## Open Questions` — what's
  actually blocking progress right now. A settled decision-log row is not an open item. An
  `approved` UC normally contributes nothing here — its questions were resolved before approval —
  but a later edit can reopen it (hard rule 7, § Feedback handling) and reintroduce questions the
  same as any other UC update.
- `## Changelog` — one line per refresh: date, what changed, which run touched it.

**Maintenance contract — who refreshes it, and when:**
- `/extract-signal`: for the signals a run extracts, **append** one `## Signal Log` row per
  functional theme, each citing the note row numbers it covers (never overwrite a prior row's
  `#`/`Signal`/`Source` — only its `Status`/`Notes` when a later signal supersedes or conflicts
  with it). Create the hub from the template if it doesn't exist yet.
  Refresh `## Requirement Readiness` and `## Open Questions / Gates` to match. **Refresh
  `## Pain Points`** to mirror any `PP-###` row this run minted or updated in
  `01-Requirements/PAIN-POINTS.md` for this feature — a pain point can land here even before any
  UC exists.
- `/bigin-transform-signal`: drafts/updates UC/BR files under `_ucs`/`_brs` (§ Feedback handling),
  after each confirmed human-gate fold-in flips the affected Signal Log row from `staged` to
  `applied`, and refreshes `## Use Cases`, `## Requirement Readiness`, `uc:`/`br:` frontmatter. It
  never touches `## Entities`/`entities:` — it doesn't promote an entity, only cites a `proposed` row
  by name (§ Entity Data Model); `/sync-entities` is what refreshes those. For a UC spanning features it
  writes `## Use Cases` and `uc:` on **every** participating hub, in its
  sequential Stage 4 pass. Also appends to `## Design Directives` for
  every presentation-only signal it routes down the Design chain, and fills each processed Signal
  Log row's `Destination` cell (the column `/extract-signal` leaves blank) with where the signal
  actually landed. It never sets a hub's own `status:` — that mirrors the `FEATURES.md` row's scope
  state, not a workflow state, and there is no "ready for PRD" feature status.
- `/enrich-feature`: refreshes `## Requirement Readiness`/`## Related Documents`/
  `## Open Questions / Gates`, and **`## Pain Points`** whenever it folds a pain-point signal into the
  UC's `pain_points:` list.
- `/approve-uc`: writes nothing to the hub at all — it only flips the UC's own `status`/`version`/
  `## Changelog` and sets `synced: false` (§ Entity Data Model). `/sync-entities` does the hub refresh
  that used to run inline here, separately, whenever it runs: `## Requirement Readiness` to reflect
  the UC's current status, `## Entities`/`entities:` for any entity it promoted or extended, and the
  corresponding Signal Log rows (the ones the UC was drafted/updated from) flipped to `applied` if not
  already. Writes nothing to `## PRD` — that's `/bigin-generate-prd`'s row below; approving a UC makes
  it PRD material, it does not itself document it.
- `/bigin-generate-design`: refresh `## UX Spec` (link + status) and `uiux:`, flip the
  `## Design Directives` rows a screen actually implements to `reflected`, and mirror its design
  questions into `## Open Questions / Gates`. If the source UC is still open (not yet `approved`),
  also append a line to its `## Discussion` citing the UX spec as supporting evidence — this is
  never how an already-`approved` UC gets a content change (that's `/bigin-transform-signal`'s
  feedback loop, § Feedback handling). It writes nothing else on a UC/BR, and never touches the
  Signal Log or `## Requirement Readiness`. Its own rules live in
  `_bigin/conventions/design-conventions.md`. (The retired `/prototype-design` held this slot.)
- `/bigin-generate-prd`: refresh `## PRD` (link + status + capability/pending counts) and the `prd:`
  frontmatter field, and mirror its `§ 11 Open Business Decisions` lines into
  `## Open Questions / Gates` **using the same sentence** as the UC/UX they came from (§ One question,
  two places). Nothing else on the hub — not the Signal Log, not `## Requirement Readiness`, not
  `## Use Cases`, not `status:`, not `uc:`/`br:`/`uiux:`. There is no "ready for PRD" feature status
  and it does not invent one. It writes no UC, BR, entity, or UX file at all — unlike
  `/bigin-generate-design`, it has no sanctioned `## Discussion` exception.
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
| `UC` | agent | Every `UC-###` id this feature owns or participates in |
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

**Source-of-truth split:** the `Slug`/`Feature`/`UC`/`Code areas`/`Sources` columns above should be
read from each feature hub's own frontmatter (`name`/`fr`/`code_areas`/`sources`, § Feature Hub),
not by parsing `FEATURES.md`'s table — point at notes that already exist and read their metadata,
instead of scanning a markdown table by column position. `FEATURES.md`'s table is still what
`/extract-signal` writes and still the human-facing index (and still what a brand-new feature
shows up in first, before its hub exists) — but it should not be any consumer's *source* for those
five columns. **`Status` is the one exception, read live from `FEATURES.md`'s table**, not from
the hub's `status:` mirror — Status is the column a human hand-edits directly (`proposed` →
`committed`/`built`/`out-of-scope`) and that edit is meant to take effect immediately, not wait for
the next `/extract-signal`/`/enrich-feature` run to catch the hub's mirror up. Practically, this
means `/extract-signal` writes every row's `Feature`/`UC`/`Code areas`/`Sources` value onto that
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

`/bigin-intake` is **capture-only**: it writes frontmatter, verbatim `## Raw`, attachments, plus two
bookkeeping sections — `## Capture history` (what was fetched, what failed) and `## Referenced but not
captured` (things the source points at but doesn't contain, such as files pasted into meeting chat).
Nothing else. `## Raw` holds source text only: a retry narrative written there is read downstream as if
the client had said it. The only judgement intake makes is the `kind:` filing label.

`## Raw` is a **container of source blocks**, not a body of text — one
`### SRC-<n> · <kind> · <ref>` block per artifact captured, `kind` being
`transcript · summary · email · attachment · webpage · note`, each mirrored as an entry in the
`raw_sources:` frontmatter manifest. `/extract-signal` plans its reads from that manifest and reads
every block on it, so a source with no block is a source nothing downstream will ever see. Three rules
carry the weight: a meeting stores its **full transcript** in its own block and the AI recap in a
separate `summary` block (derived text — navigable, never quotable as a signal or a `Why`); an
attachment gets a block holding its text, or its path when binary; and an append is always a **new**
block, never merged into an existing one.

All interpretation belongs to `/extract-signal`, which fills the note's `## Extracted signals` table
(`_bigin/templates/intake.md`): one row per signal —
`# | Type | Signal | Why | Source | Feature | Status | Notes` — each traced to a message,
timestamp, or attachment.

Every claim is classified **as-is / pain / to-be** before it is typed
(`_bigin/stages/extract/2-extraction.md` § Classify first): a description of the system being replaced
is a `decision`, a named frustration is a `pain-point`, and only a statement about the new system is a
`requirement`. This matters because most client sessions are a walkthrough of the incumbent product, and
an extractor that skips the call records the software being thrown away as the specification for its
replacement.

A `Why` is carried by `requirement`/`feedback` rows only, and is one of three values: the client's stated
reason · `derived from #<n>` (a to-be inferred from as-is + pain rows, flagged for client confirmation) ·
the literal `not stated`. A guessed rationale is never acceptable. `not stated` rows are recorded as
such; the ones whose missing reason would change what gets built are raised together in **one** batched
question rather than one question each — a note carrying dozens of checkboxes gets none of them answered.

`/extract-signal` records that call **on the row**, in `Notes`: `rationale: in question` for a row
carried in the batched question, `rationale: non-blocking` for one deliberately left unasked
(`3-filing.md` § Step 5). `/bigin-transform-signal` reads that marker and nothing else to decide
whether the row blocks (`2-qualification.md` § Gate 1). A `not stated` rationale is **never itself a
blocker**: a non-blocking row qualifies with the gap carried verbatim onto its staged entry, and an
unmarked row qualifies the same way and is reported as a filing gap — never parked. Parking on a
missing reason nobody asked about strands the requirement behind a remedy that cannot clear it.

`Feature` and `Status` make the row's anchor and progress machine-readable — `Status` reuses the same
vocabulary as the Feature Hub's `## Signal Log` (§ Feature Hub) so a signal reads the same state at both
levels.

This table is the vault's **raw signal record**, and it stays flat: one row per signal in arrival
order, never merged or grouped, however many rows describe the same thing. It's what the source
audit quotes against and what every later stage re-reads to see what was actually said, so a merge
here destroys evidence. Grouping is the *hub's* job — these rows file onto the Feature Hub as
themed Signal Log rows citing their `#` back here (§ Feature Hub).

Questions raised by `/extract-signal` live **only on the source INT note's `## Open Questions`** —
`- [ ] Q: … (owner: client|team) ↦ —` with an `A:` answer line. **There is no UC mirror of an
extract-stage question**, by design: the filing stage never touches a UC (`3-filing.md` § Scope), so a
promised mirror would be a promise nothing keeps — the note would read as having a copy elsewhere while
the UC had nothing. The `↦` field stays `—` until a later stage rewrites it to `↦ UC-###` as a *pointer*,
not a second copy of the question.

A question about UC content is raised on the UC by `/bigin-transform-signal` instead
(`3-lane-uc.md` § Questions), and that one *is* the canonical copy of itself. When both exist for the same
ambiguity, that is the "one question, two places" bug below, not a mirror.

A note left with unanswered questions is parked `status: needs-clarification`: that flag is what surfaces
it for the human to jump in. Three ways to close a question:

- **Answer inline**: fill the `A:` line, tick the box. The next `/extract-signal` pass folds the
  answer in, ticks the UC copy, and flips the note to `in-review`.
- **Answer arrives from the client**: `/bigin-intake` appends the reply to the note and resets it
  `status: raw`, which re-enters the extraction queue; extraction matches the reply to the open
  question as an `[answer]`.
- **Answer arrives inside a *different*, later note**: that note's own extraction produces an `answer`
  row, and filing ticks **both** copies — the question where it was raised, and this note's — citing the
  resolving `INT-###` (`3-filing.md` § Step 5b). Without that fold-back the earlier note sits
  `needs-clarification` forever with an unticked box, reading as blocking when the answer has been on
  record for weeks.

### One question, two places — never two questions

A `question`/`concern` row in `## Extracted signals` and its `## Open Questions` line are **two
views of one question**, not two questions. The row is the extraction ledger entry (what was
found, where, what state it's in); the `## Open Questions` line is the human-facing copy — the
one thing to answer. Three rules keep them one question:

1. **Never re-word the mirror into a second question.** The mirror may add context the human
   needs to answer (which UC it collides with, what's already decided) — but the *ask itself*
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

`status: needs-clarification` and the artifact's own question list are two mirrors
of one fact — that list is `## 5`'s **Still open** section on a use case, and `## Open Questions` on an
INT note or a BR — the same drift risk as a stale Feature Hub Signal Log `Status` column left
`question` after its UC absorbed the row (§ Feature Hub), just on the `status:`
frontmatter/body pairing instead. A human reads whichever surfaces first (a queue badge reads
`status:`; opening the note reads the section body) and both must agree, or the note reads as
done in one place and stuck in the other.

**The invariant:** zero unchecked `- [ ] Q:` lines in that list (INT note, UC, or BR) ⟺
`status` is not `needs-clarification`. Any unchecked line ⟺ `status` **is**
`needs-clarification`. This holds for every artifact that carries one — INT notes, use cases, and BRs
alike. **A use case's decision-log rows are not open items**: they are settled history, and counting
them would park a finished UC at `needs-clarification` forever.

Every skill that writes to a question list or sets `status` on such an artifact
(`/extract-signal`, `/bigin-transform-signal`, `/enrich-feature`) must make the status line the
**last** write-back step, derived by re-counting the section **after** every accepted change has
been applied to it that run — never decided earlier in the run and then left stale by a later
edit to the same section:

1. Apply every accepted change to the question list first (tick resolved boxes with `A:` filled, append
   genuinely new ones; on a use case, move a genuinely resolved line into the `## 5` decision log).
2. Count remaining unchecked `- [ ] Q:` lines in that list.
3. Set `status: needs-clarification` if the count is > 0; otherwise move it to whatever "done"
   means for that artifact type (`in-review` for an INT note; whatever stage the UC/BR was
   already at — `draft` if it hasn't been enriched yet — for a UC/BR, § Status vocabularies).
   Do this from the count, not from memory of what the run intended to resolve.

**Common ways this drifts** (treat each as the bug it is, not a cosmetic gap): ticking every box
while `status` still reads a stale `needs-clarification` from before the run; flipping `status`
off `needs-clarification` while a `- [ ] Q:` line — even one raised earlier in the same session
and forgotten — is still unchecked in the body; ticking a box that isn't genuinely resolved (an
answer that still needs a client round-trip stays unchecked, and `status` stays
`needs-clarification`, even if every *other* question closed) just to make the count zero.

## Resumable unattended apply (checkpoint + idempotent writes)

An unattended fold-in — matching a human's already-written inline answer to its UC and folding it
in, whether that's `/bigin-transform-signal`'s Stage 1 fold-in, `/extract-signal`'s per-note batch
processing, or a future `--auto` mode — is a multi-file write: the UC itself, the feature hub,
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
   landed: does the UC's `## Changelog` already cite this INT id's fold-in, or does the
   `## Open Questions` line already read as resolved (not merely ticked) rather than unticked? If
   yes, this run is a retry of an already-completed apply — do nothing to that UC, and move
   straight to reconciling any mirror that's still behind (step 3). Never re-append a changelog or
   Discussion line just because this run started before checking.
2. **The UC's own file write is the checkpoint — make it one atomic write, and make it first.**
   Compose the *entire* change (requirement body wording, `version` bump, `## Changelog` line,
   re-counted `status`) and write the UC file once. Before that single write lands, nothing has
   changed on disk — a kill at any point up to here leaves the note exactly as it was, correctly
   still eligible for a future run to pick up (no special "in progress" marker needed; there is
   nothing to distinguish from "not started yet"). After it lands, the fold-in is **done** —
   everything downstream is a re-derivable mirror, never the source of truth.
3. **Mirrors are always safe to reconcile, never a one-shot append.** The feature hub's Signal Log
   row, `FEATURES.md`, and the source INT note's own tick/status are all *read from the UC's
   current state* and corrected to match — flip a Signal Log row to `applied` if the UC it points
   at now shows the fold-in, tick the INT note's copy if the UC copy is already resolved. Setting
   an already-correct mirror field again is a no-op, not a duplicate, so this step never needs its
   own resume logic: run it every time, unconditionally, whether this is the first pass or the
   tenth.
4. **A subsequent run's gate check is therefore a 3-way read, not a 2-way one.** For any UC
   carrying a fold-in candidate: (a) **genuinely unanswered** — the INT note's `A:` line is still
   blank → wait for a human, not eligible. (b) **already applied** — the UC's
   `## Changelog`/body already reflect it → not eligible for another apply, but still worth a
   mirror-reconciliation pass (step 3) in case a prior run's kill landed the UC write but not the
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
number without restating what that number means — e.g. "Does UC4's Organization Experience
narrative-question set *replace* UC-004 S23's single" (which "UC4"? the fourth item in *this* note,
or the `UC-###` artifact id? "S23's single" — single *what*?). This
applies wherever `/extract-signal`, `/bigin-transform-signal`, or `/enrich-feature` write a
`- [ ] Q: …` line, on an INT note or a UC.

**Format:**

```
- [ ] Q: <How it works today — plain business language, no ids.> <What the new request changed —
  plain business language.> <The one decision needed, as its own question sentence: yes/no,
  A-or-B, or an (a)/(b)/(c) list when there are three or more options.> (owner: client|team)
  (ref: UC-###, BR-###, INT-### — traceability only, safe to ignore when answering)
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
  *fold-in*, *bucket*, *UC/BR/INT/PP/EN*. Push every id into the trailing `(ref: …)` parenthetical
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
  requires opening the UC, knowing what a `BR-###` is, or re-reading the sentence to find the
  actual question, rewrite it. A question the human has to decode is a question that sits
  unanswered.

**Before/after** (the id-reference failure):

> ❌ *Does UC4's Organization Experience narrative-question set *replace* UC-004 S23's single*

> ✅ *In UC-004, the existing Organization Experience question is a single free-text field
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

### Answering a question (the human side of the loop)

A question is written to be answered **cold, in the file** — a BA opens the UC, BR, or INT note on
their own time, types on the `A:` lines, and comes back later. Everything downstream reads that line
and nothing else, so:

- **The answer goes on the question's own `A:` line, verbatim.** An answer given in chat, in a comment,
  or in prose above the question is invisible to every skill: the fold-in's three-way read
  (`transform/1-foldin.md`) looks at the `A:` line to tell "unanswered" from "answered, not applied".
  Whoever relays such an answer moves it onto the `A:` line first; that is the one edit allowed.
- **Tick the box only if the answer genuinely settles the question.** "Ask the client", "TBD after the
  demo", a reply restating the disagreement, or one that answers a *different* question, all leave the
  box unchecked — the box is what the status invariant counts (§ Open Questions ↔ status consistency),
  so ticking an unsettled one is what makes a parked artifact read as approvable.
- **An answer still needing a client round-trip stays unchecked but is still worth writing.** A partial
  answer set is normal: the fold-in applies what settled and leaves the rest.
- **Don't hand-edit the numbered sections to match your own answer.** The fold-in applies the answer
  into the content and moves the question into the decision log; editing both is how the same change
  lands twice, or how a staged change silently overwrites the reviewer's wording (`1-foldin.md`
  § The human may have edited the section first).
- **Then say "process UC-###".** That pass reads the answers instead of re-asking them, folds in once,
  and returns either the follow-up questions it produced or the flow and an approval ask
  (`agents/bigin-ba.md` § Answers already written: the process-the-UC pass).

## Signal → artifact mapping

Every `[requirement]`/`[feedback]` signal `/bigin-transform-signal` folds in lands in exactly one
(sometimes two, when it's genuinely both) of these places — never loose in prose:

| Signal is… | Goes to |
|---|---|
| A testable, actionable statement about behaviour | a step in a new/updated `UC-###`'s flow (§ Use Case) |
| A conditional/policy constraint, feature-level or governing one workflow | a new/updated `BR-###`, `uc: []` citing the use case(s) it governs, mirrored read-only in each one's `§ 4` (§ ID scheme, § Use Case) |
| A presentation-only statement — look, layout, tone, copy voice, interaction feel, accessibility affordance — that changes no behaviour | a **design directive**, never a UC line: a `DESIGN-PRINCIPLES.md` row when durable/cross-cutting, a row in its feature hub's `## Design Directives` when feature-scoped, or both (§ Traceability chain's Design chain, § Design Principles Register) |
| A data field/entity described — a thing the business tracks and its attributes | a `proposed` row in `ENTITIES.md`, later promoted to `EN-###` `## Fields` (§ Entity Data Model) — new or existing entity |
| Narrative context — the client's stated why, not yet actionable on its own | the UC's `## 1` Business Need / Goal |
| A concrete frustration/cost the client named, with no requirement attached yet | a new `PP-###` in `01-Requirements/PAIN-POINTS.md` (§ Pain Point Register), its id added to the UC's `pain_points:` once one exists |
| A description of how the **current/legacy** system behaves (`[decision]`, as-is) | context, not a build item: an `ENTITIES.md` row when it names data the business tracks, the UC's `## 1` Business Need when it explains why the replacement is wanted. Never a functional requirement — it describes software being retired |
| Something a person committed to supply or do (`[commitment]`) | stays on its feature hub's `## Signal Log` as its own row until delivered; its `Notes` names the row or question it unblocks. Often the authoritative version of a rule the transcript states loosely |

A `[pain-point]` with no attached requirement is not a gap to fill — it's kept on record
(`PP-###`, `Status: open`) until a later signal turns it into a UC/BR line or an epic/story
resolves it, or it just stays as context. Never force a pain point into a functional requirement
it doesn't actually support, and never drop it for lack of a home. A signal can legitimately land
in more than one row at once — e.g. a field-level rule is both an `EN-###` mapping row and, if the
client also gave a reason, feeds that entity's or the citing UC's own context.

## Entity Data Model

A `[requirement]` signal sometimes describes not a behavior but a **thing the business tracks** —
a Vendor record, an Application, a Wallet — and the concrete data it must carry: field names,
types, and relationships. Left to plain UC routing, this either gets buried as a clause inside a
Functional requirement sentence ("the system must capture the vendor's tax ID") or repeated with
drift across every UC that happens to touch the same entity — entities are usually **shared across
features** (a Vendor's fields matter to both a Vendor Management feature and a Payments feature),
so a per-UC field list duplicates and drifts.

`01-Requirements/_entities/EN-<NNN>-<slug>.md` (`type: entity`) is the artifact for this: one
document per business entity, promoted by `/sync-entities` from a `proposed` row in
`01-Requirements/ENTITIES.md`, the first time a UC it's processing (or a `BR-###` that UC mirrors)
actually references it. `/bigin-transform-signal` never promotes one — a UC/BR drafted or updated
mid-review can cite the entity by name against the `proposed` row, but the row stays a row until
approval, so a goal that never reaches `/approve-uc` never leaves behind an entity doc nobody needed.

Promotion itself is decoupled from the approval moment: `/approve-uc` only ever flips the UC's own
`status`/`version`/`## Changelog` and sets its `synced: false` — it never touches `ENTITIES.md`, an
`EN-###` doc, or a feature hub, so approving several UCs in a row is never blocked on shared-file
writes. `/sync-entities` is what actually does the promotion/extension described below, run separately
whenever convenient (right after an approval, batched at the end of a review session, or lazily before
whatever later stage needs the entity data) — it scans for `status: approved` + `synced: false` UCs
and processes them one at a time, the same sequential discipline as always, and flips each to
`synced: true` once done.

**Frontmatter (`_bigin/templates/entity.md`):**
```yaml
---
type: entity
id: EN-
name:
kind:            # actor | data | system
status: proposed # proposed (row exists in ENTITIES.md, no doc yet) -> draft (this doc exists,
                 # fields still settling) -> approved (human confirmed at a UC/BR review gate)
features: []     # every feature slug whose UC(s)/BR(s) reference this entity
updated:
---
```

**Body:**
- `## Fields` — `Field | Type | Required? | Source | Notes`. `Source` cites the Signal Log row (or
  UC/BR) that introduced or last changed the field.
- `## Relationships` — how this entity references others (e.g. "belongs to EN-002 Customer
  (many-to-one)"), each citing the UC/BR it's drawn from.
- `## Changelog` — same convention as every other artifact.

A field-level business rule is **not** a subsection of the entity doc — it's a full `BR-###` file
under `01-Requirements/_brs/` like any other business rule (§ ID scheme), citing the entity's
fields it governs in its own body. An earlier draft of this document described a
`## Field-level Business Rules & Mapping` subsection inside the entity doc, sharing one vault-wide
`BR-###` sequence with `EN-###`; that was never built — `BR-###` is its own independent sequence
(§ ID scheme's Next-ID rule), and there is no per-entity BR subsection.

### The doc is a data dictionary, not a diff of the last approval

What a developer, a PRD reader, or a designer opens an `EN-###` for is **the whole shape of one
business object** — every field it carries, each field's type, whether it's required, and what values
it may take. Three rules make it that, and each one exists because the obvious incremental behaviour
produces a document that is worse than useless: an authoritative-looking file that is quietly a
fragment.

- **One doc per real-world business object — never per field.** `Application`, `Vendor`, `Wallet`.
  An attribute is a **row inside** its owner's `## Fields`, never its own `EN-###`: a doc named
  `Application.Private-School Certification Status`, whose `## Fields` holds exactly the one row it
  was named after, is this rule broken — the field belongs in `EN-001 Application`. Resolve a
  `<Entity>.<Field>` name (in an `ENTITIES.md` row, a UC's `entities:`, or an existing doc) to the
  owning object before writing anything, and cluster aggressively when in doubt: a field wrongly
  filed under a neighbouring object is one row to move, while a fragment doc splits an entity's
  definition across files nobody knows to open together.
- **Every known field, every time — not just the ones the UC being synced happened to touch.**
  `/sync-entities` runs per approved UC, but the doc it writes is not scoped to that UC: before
  writing, gather the union of every field any source has stated for this object — the
  `ENTITIES.md` row's `Fields (so far)`, this doc's existing rows, and every UC/BR listed in its
  `features:` that references it — and write the full set, each row keeping its own `Source`.
  A doc rebuilt from one UC's view is how an entity ends up documented as whatever was approved
  last Tuesday.
- **Spell out the values.** A `Type` cell reading a bare `enum`, `status`, or `code` documents
  nothing. Enumerate the states inline, separated by ` / ` because a `|` would break the table
  (`enum: Pending School Review / Certified / Rejected`), and give a format where one was stated
  (`date: YYYY-MM-DD`, `money: USD`). Values genuinely never stated → write
  `enum: values not stated` rather than a plausible list, and raise the gap as a `- [ ] Q:` on a UC
  that references the field, where the status invariant will actually track it.

**Never invent a field, a type, a value, or a required-ness the sources didn't state** (hard rule 1).
"Complete" here means complete over what the vault actually knows, with the gaps visible as gaps —
not a developer's guess at what an Application record probably needs.

### A fragment already on disk: merge, never delete

Attribute-shaped docs exist in vaults created before this contract. `/sync-entities` repairs one when
it next touches the owning object: every row from the fragment moves into the owner's `## Fields` with
its `Source` cite intact, and the fragment is stamped `status: merged` + `merged_into: EN-###`, its
body replaced by a one-line pointer. **The id is never reused and the file is never deleted** (hard
rule 1) — a `PRD-###`, `UX-###`, or UC frontmatter that still cites it must keep resolving. Every
`ENTITIES.md` row, `entities:` list, and hub `## Entities` line pointing at the fragment is repointed
at the owner in the same pass.

**Registry:** `01-Requirements/ENTITIES.md` (`type: entities-register`, singleton,
`_bigin/templates/entities-register.md`) —
`EN-### | Entity | Status | Fields (so far) | Features | Notes`, created by `/extract-signal` the
moment a signal describes a data field or entity attribute, with a `proposed` row per entity.
Cluster aggressively — **one row per real-world business object, not per field**: a signal about a
new field on a tracked object adds to that object's `Fields (so far)` cell, and never earns a row of
its own. A row named `<Entity>.<Field>` is always the bug, not the exception.
`/sync-entities` promotes a row to its own `EN-###` document; the register keeps the row afterward as
the vault-wide index (mirroring how `FEATURES.md` stays the index once a feature hub exists).

## Pain Point Register

Every `[pain-point]` signal gets a **`PP-###` id the moment it's extracted** — **or cites the existing
one it restates.** Clients repeat the same frustration in meeting after meeting, so `/extract-signal`
matches against the register before minting: a match adds the new `INT-###` to that row's `Source` and
cites its id on the signal row instead of creating a near-duplicate. Ids are vault-wide,
numbered like `BR-###` (scan `01-Requirements/PAIN-POINTS.md`, not any UC, since a pain point can
predate its feature's UC) — tracked in `01-Requirements/PAIN-POINTS.md`
(`type: pain-point-register`, singleton, instantiate from
`_bigin/templates/pain-points-register.md`):

| PP-### | Statement | Feature | Source | Status | Proposed solution | Resolved by |
|--------|-----------|---------|--------|--------|--------------------|--------------|

- **Status**: `open` (named, nothing addressing it yet) · `addressed` (a `Resolved by` link exists
  and a human confirmed it's sufficient — this is a judgement call, so it never auto-flips the way
  `needs-clarification` does) · `orphaned` (the feature/UC that would have addressed it went
  `out-of-scope`, or the client explicitly walked it back — never silently deleted).
- **Proposed solution**: a short, plain-language description of the approach addressing it, filled
  in as soon as a requirement/story is drafted with this pain point in mind. Not a separate
  approval-gated artifact — a solution is a fact **about** the row, not a new document.
- **Resolved by**: starts blank or citing whatever's available first (a UC functional-requirement
  line, a `BR-###`), then gets **backfilled** once `/consolidate-prd` produces the epic/story that
  actually implements the solution, since that's the concrete unit of work a PO tracks a pain
  point's resolution against.
- Same append-only discipline as every other register here: `PP-###` is permanent, a row is never
  deleted — a walked-back pain point becomes `orphaned` with an explanation in `Resolved by`.

**Cited from the use case** once one exists: the UC's `pain_points:` frontmatter lists the `PP-###`
ids the workflow exists to resolve — **ids only, no fourth copy of the table**. The register is the
vault-wide source of truth (queryable across features) and each feature hub's `## Pain Points` is the
per-feature mirror a human reads; a third table on the UC would be a third thing to keep in sync for
facts that are one grep away. The pre-UC `FR-###` model did carry that table, which is why an absorbed
FR still shows it.

**Created** by `/extract-signal` the moment a `[pain-point]` signal is extracted. **Solution +
`Resolved by` backfilled** by `/enrich-feature` (UC-level solution) and `/consolidate-prd`
(epic/story backfill). **Status flipped to `addressed`** only by a human.

## Design Principles Register

A `[constraint]` signal sometimes isn't feature-specific at all — "keep it minimal," "use our
brand colors," "our users skew older, avoid tiny tap targets" apply to every feature, not just
whichever UC happens to be open when the client says it. Left to the normal signal→UC routing
above, a cross-cutting preference either gets awkwardly bolted onto one feature's
`## Business Rules` or is lost entirely if no UC exists yet when it's said.

`01-Requirements/DESIGN-PRINCIPLES.md` (`type: design-principles`, singleton, vault-wide) is the
standing register for these. `/extract-signal` appends a row whenever an extracted `constraint`
signal reads as a durable, cross-cutting preference rather than a one-off constraint tied to a
single feature:

- **Feature-specific** visual/interaction constraints ("this donor dashboard should feel warm,
  less corporate") go to that feature hub's own `## Design Directives` section, on the Design chain
  (§ Traceability chain) — **not** onto its UC. An earlier draft of this document routed them to
  the UC; that put untestable presentation language inside approved functional scope and made a
  purely visual note wait behind `/approve-uc` before `/bigin-generate-design` could ever see it. A
  feature-scoped directive that turns out to change behaviour was misrouted and belongs back on the
  UC — see `_bigin/stages/transform/3-routing.md` § The design boundary test.
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

Downstream: `/bigin-generate-prd` reaches it only **through** the `UX-###` that already applied it —
its § 9 quotes the design's stated intent (`Principles applied`) rather than re-reading this register,
so a PRD can never claim a client preference the screens don't actually reflect. An earlier draft of
this document had a PRD stage reading the register directly and citing rows in a design-goals section;
that reading is deliberately not what got built. `/bigin-generate-design`
reads it **directly** (not via a PRD at all) and seeds the shared design system's `## Foundations` from its
`active` rows — so it stays authoritative even if a given PRD section forgot to transcribe a
preference, and so a feature that reaches design before its PRD is finished still produces screens
consistent with what the client has said. That register is **read-only** to the design stage: it
holds client-stated preferences, and a token or pattern an agent chose is not one.

## Business Scenarios (retired)

A `[requirement]`/`[feedback]` signal sometimes describes a real-world flow that crosses feature
boundaries — a request submitted in one feature, approved in another, settling as a financial
adjustment in a third (not just "this feature calls that API" — an end-to-end sequence a human
would narrate as one story). When the requirement artifact was one `FR-###` per testable statement,
that flow had no home, and `01-Requirements/SCENARIOS.md` (`SCN-###`, one register row per scenario)
was built to give it one.

**A use case is that home, and it is strictly more.** A `UC-###` whose `features:` lists every
participating slug records the same sequence *plus* the actors, the trigger, the pre- and
post-conditions, the alternative and exception paths, the rules that govern it, its open questions, and
a human review gate — none of which a register row could carry. So `SCN-###` is retired:

- **Never create or extend a `SCN-###` row.** A cross-feature flow routes down the UC lane like any
  other flow (`_bigin/stages/transform/3-routing.md` § The lane table).
- **Existing rows stay** (hard rule 1 — nothing is deleted). Set `Status: superseded` with
  `Notes: absorbed by UC-###`, and list the `SCN-###` in that UC's `absorbs:` frontmatter, the first
  time a signal brings the flow back into play.
- **Existing hub `## Business Scenarios` sections stay** as history. The live pointer is the
  `## Use Cases` row, on every participating hub, and it deliberately carries **no step number** — the
  `(step N of M)` on each hub was this register's worst failure mode, going stale silently every time a
  step was inserted mid-flow. The UC file is the single place the flow is written out.
- `01-Requirements/SCENARIOS.md` and `_bigin/templates/scenario-register.md` remain readable so old
  ids resolve; nothing writes to either.

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
  the agent thinks was meant, **and never minted either** — minting a typo creates a permanent
  duplicate slug, which is worse than either option the flag offers.
  The runnable procedure is `_bigin/stages/extract/3-filing.md` § The declared-slug exception —
  that file is what the filing stage actually reads, and it is the only place this exception's steps
  are written out. This bullet is the standard; that section is the procedure. They must not
  disagree: an earlier version of this pair had conventions granting the exception while the filing
  guide said "NEVER a new `{requirements_file}` row", which made the case a coin flip.
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

When no existing row fits, `/extract-signal` never guesses the anchor — but it doesn't stop at "no
match" either. It distinguishes two failure shapes, because they ask a human two different questions
(full rules: `/extract-signal`'s `3-filing.md` § Step 1 — Anchor):

- **Ambiguous among existing features** — more than one slug's scope plausibly fits: record the
  candidates on the signal line (`unresolved — candidates: a / b`) and ask which one. Candidates are
  joined with `/`, never `|`: this value lands in a table cell, and a raw pipe splits the row.
- **No existing feature fits, and the signal reads like new scope** — record `unresolved — none
  found`, and draft a **suggested slug** (kebab-case, from the signal's own vocabulary, checked
  against the registry for a near-miss first) plus a **one-line scope** statement, so the question
  gives a human something to confirm or edit rather than a blank line to fill from scratch.

Either way:

- Add an Open Question (owner: team) on the closest UC, or on the source INT note itself if no UC
  exists yet, worded for whichever shape it is (`3-filing.md` § Step 5 — Questions has the exact
  templates).
- Park the source INT note `status: needs-clarification` and add `needs-review` to its `tags:` —
  the same surfacing mechanism as any other open question, so it's visible as specifically needing
  a human to map the feature, not just answer a content question.
- The human closes it by writing the correct slug back — as the `A:` answer on the note's Open
  Questions line, or by setting the note's `feature:` frontmatter directly — and ticking the box.
  For a new-scope question, the human mints the `proposed` `{requirements_file}` row themselves
  (the drafted slug/scope is a starting point, not something `/extract-signal` ever writes there
  unattended). The next `/extract-signal` pass reads the answer as the resolved mapping and stages
  the signal against the named feature.

## Feedback handling

Feedback is just intake (`kind: feedback`) — and CR material against a UC can equally well arrive
as an ordinary `kind: requirement` signal from a meeting/email that happens to touch shipped scope.
Either way, `/bigin-transform-signal` applies it to the affected UC/BR **the same way, regardless
of that UC's current status** (hard rule 7 — approval no longer freezes a UC, and neither does
the feature shipping):

- **Update in place, always.** Edit content, bump `version`, log the reason + source `INT-###` in
  `## Changelog`. If the UC was `approved` (or `enriched`/`consolidated`), the same edit also sets
  `status` back to `draft` — un-staging it as feature material (§ Feature material) until the
  human re-approves. Interactively,
  this runs as a discussion round in the UC's `## Discussion`: present the proposed change (quoted
  signal + INT id + proposed edit), the human confirms, the answer folds in. Unattended, the
  proposed change is written into the UC's `## Discussion` and its Signal Log row flips to
  `staged` — never auto-applied without a human confirming — and the UC's `status` moves to
  `needs-clarification` so the pending decision surfaces exactly like any other UC awaiting a
  human look.
- **There is no forking to a new `amends:`-linked sibling UC for this case.** The same UC carries
  its whole history in its own `## Changelog` — whether it's still open, already approved, or the
  feature has since shipped. `amends:` frontmatter is reserved for the rare case where a feature's
  scope genuinely splits into a second, independent decision that doesn't belong in the same
  document; confirm that split explicitly with the human before minting a second UC for one slug —
  never reach for it just because the source UC happens to be `approved`.
- **Removing scope.** If a discussion round concludes the UC's scope — or part of it — should come
  out entirely (the client walked it back, it's no longer wanted), a human sets `status: removed`
  with the reason in `## Changelog` (human-gated like `approved`; an agent may raise this as an
  Open Question, never set the status itself). This is not deletion (hard rule 1): the file, its
  id, and its full history stay intact. Cascade the same as any other edit (below) so every
  downstream artifact that traced to it surfaces as needing a human decision, rather than silently
  going stale with no explanation.
- **Reinstating.** A human can later move a `removed` UC back to `draft` if the scope returns —
  logged in `## Changelog` with why. `/bigin-transform-signal` never does this unattended; a
  signal that looks like "bring this back" is an Open Question for the human, the same as any
  judgement call an agent can't make on its own.
- Either way — cascade: set the downstream PRD/epic/story/prototype that trace (via
  `sources`/`links`) to the affected UC back to `draft` too (a changelog entry on each citing
  the INT id and naming the upstream UC change that triggered it), so stale artifacts surface
  until `/approve-uc`/`/bigin-generate-design`/`/consolidate-prd` re-run.
- Open questions with owner `client` stay listed in the (current) UC's `## Open Questions` for the
  human to raise with the client; answers return through `/bigin-intake` as feedback.

## File naming

`<ID> <short title>.md` — e.g. `UC-012 Export invoices in bulk.md`

## Changelog section (all non-intake artifacts)

```md
## Changelog
- 1.0 (2026-07-02) — initial draft from INT-003
- 1.1 (2026-07-05) — INT-009 feedback: export limited to 500 rows
```

## Summary block (use case only — scannability)

Reading a long UC cold means scrolling past open questions, business rules, and prose just to find
out what the note is about. The UC template carries a collapsed summary right after frontmatter,
before `## 1. Context & Metadata`, so a reader gets the gist in one glance without opening the whole
document:

```md
> [!summary]- Summary
> 2-3 sentences here.
```

It's a **synthesis, never new content** — same contract as any diagram/visual aid a skill adds: it
illustrates what the note already states, it doesn't add to it. Drafted by `/enrich-feature` when
the UC is first enriched, refreshed by any `/bigin-transform-signal` fold-in that changes the UC's
content (version bump), so it never goes stale relative to the sections below it.

**Write it for a client/PO skimming the note, not for an auditor tracing artifact lineage.**
2-3 short sentences, plain business language:

1. **Source + what changed** — where this came from (INT id, or "a change request against
   UC-XXX") and the concrete thing being added/changed, in business terms (a field, a rule, a
   capability) — not "3 new flow steps and BR-104".
2. **Why** — the pain point/business reason, in the client's terms (drawn from `## 1`'s Business
   Need / Goal and the `pain_points:` it cites), not a citation of which section it came from.
3. *(only if it changes how the reader should read the UC)* one short clause on what's still
   open — not a restatement of frontmatter status. Omit entirely if there's nothing unusual to
   flag; `status:` and the Open Questions count already show on the note.

**Avoid:** stacking multiple artifact ids in prose (one incidental `UC-XXX` mention is fine; a chain
of `UC-004 … BR-104 … S7` reads like a diff, not a description). Narrating the
pipeline ("per the extraction step", "pending enrichment") — the reader doesn't need to know which
skill wrote this. Hedge-y meta phrasing ("leaving the conflicting parts to a separate UC-022") —
say what *this* UC does; a sibling UC's scope belongs on that UC, not narrated here.

**Before/after** (same UC, real case):

> ❌ *This UC is a change request against the already-approved UC-004 (vendor management),
> expanding the vendor profile/application field set based on the client's `CFEF CRM Flow.pdf`
> reference document. It exists because that document revealed additional fields (Website,
> Customer Tags, W-9 flag, Marketable flag, notes fields), a defined 4-value Reimbursement
> Restrictions dropdown, and a much richer Organization Experience narrative-question set beyond
> what UC-004 originally captured. It adds 4 flow steps and BR-104 (fixing the
> Reimbursement Restrictions value set) as additive detail only, leaving the conflicting parts of
> the same document to a separate UC-022. It still carries 1 open question — whether the new
> narrative questions replace or supplement UC-004's original educational-value field — and is
> `needs-clarification`, pending further elicitation.*

> ✅ *Adds the vendor profile fields the client's `CFEF CRM Flow.pdf` calls for — Website,
> Customer Tags, W-9 and Marketable flags, notes, a 4-value Reimbursement Restrictions list, and
> richer Organization Experience questions — that UC-004's original vendor form didn't capture.
> Open question: whether the new questions replace or add to the existing educational-value
> field.*

Same content, same traceability (still one `UC-004` mention, still names the source document) —
just business-first instead of artifact-first. If a reader wants the artifact-level trace, that's
what `sources`/`absorbs`/the Changelog are for; the summary's job is "what is this, in plain
terms," not "how does this fit the pipeline."

**Intentionally not on INT** — an intake note is raw capture only; even a purely descriptive
summary is a step toward interpretation this vault deliberately keeps out of `/bigin-intake`. An
INT note's "what is this" question is answered instead by its `## Extracted signals` table once
`/extract-signal` fills it, or by opening the note (they're short — that's the point of raw
capture).

Not currently applied to PRD/Epic/Story/feature-hub either — the feature hub already carries a
one-line description under its `# <Feature Name>` heading for the same purpose. Extend the pattern
to other artifact types only if the same scan-cost problem shows up there.

## Workspace version check (every skill, at its precondition)

`_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/` are **copies**. The originals live in the
installed plugin, and `_bigin/system/project.md`'s `workspace_version` records which plugin version last
copied them. Those two can disagree in **both** directions, and only one of them is a warning.

```text
at every skill's existing "missing _bigin/ → stop" precondition, add one Grep each:
    workspace = Grep '^workspace_version:' _bigin/system/project.md
    plugin    = Grep '"version"' ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json

COMPARE AS SEMVER — component by component, numerically. Never as strings: "1.10.0" sorts BEFORE
"1.6.5" lexically, so a string compare reports an upgrade as a downgrade at exactly the version
where it starts to matter.

workspace == plugin   → proceed silently. The ordinary case.
workspace <  plugin    → WARN and proceed: "workspace is on <a>, plugin is <b> — run
                         /bigin-upgrade-project". The rulebook this run follows is the older one,
                         which is usually harmless for one run and always worth saying.
workspace >  plugin    → STOP. Do not run.
                         Say: the vault's content was built against a NEWER rulebook than the one
                         installed here, so this run would follow superseded rules and, worse, an
                         upgrade run would copy the older rulebook over the newer one and stamp the
                         version backwards. Usual cause: a stale plugin cache being resolved as
                         ${CLAUDE_PLUGIN_ROOT} while the workspace was materialized from a newer
                         install. Name both versions and the cache path, and stop.
workspace_version absent / unparseable → warn, name it, proceed. An old project predates the field.
```

**Why "ahead" is a stop rather than a warning.** Every other version mismatch costs one run following
slightly stale rules. This one is the only case where continuing can *destroy* correct state: the
materialized rulebook gets overwritten with an older one, `workspace_version` is stamped down, and the
next run has no way left to tell that a downgrade happened. There is nothing to reconcile from
afterwards, because the record of what the content was built against is exactly what got overwritten.

`${CLAUDE_PLUGIN_ROOT}` is otherwise not a path any stage reads — see § Reconciliation notes.

## Reconciliation notes for this plugin

Concrete gaps between this document and the plugin's actual skills, collected here instead of as
scattered inline caveats — resolve and delete each line as the corresponding skill is migrated.

- ~~**Plugin-internal paths were unreachable at runtime.**~~ **Resolved (plugin 1.2.0).** The rulebook
  and templates are now materialized into the project by `/bigin-new-project`
  (`_bigin/conventions/`, `_bigin/stages/`, `_bigin/templates/`), and every skill, dispatch prompt, and
  template refers to them project-relatively. Anything still pointing at `references/…`,
  `skills/*/SKILL.md`, or `skills/*/template/…` for a file a subagent has to read is a bug.
  `${CLAUDE_PLUGIN_ROOT}` has exactly four legitimate uses, all of them in the orchestrator and none
  in a subagent: `/bigin-new-project` § 2 and `/bigin-upgrade-project` § 5 resolve the copy source;
  every skill's precondition reads `plugin.json`'s `version` for § Workspace version check; and
  `5-status.md` Part 3 plus `/extract-signal`'s batch check invoke the plugin's own deterministic
  checker (`hooks/bigin-lint.py --full`). A stage file may name that path because Part 3 and the batch
  check both run in the orchestrator — never hand it to a dispatched agent, which cannot resolve it.
  An unavailable checker is always **reported**, never read as a pass.
- ~~**The design stage was on the old layout.**~~ **Resolved.** `/prototype-design` is superseded by
  **`/bigin-generate-design`**, which reads `01-Requirements/_ucs/` directly, accepts a feature
  carrying several UCs and a UC spanning several features, and writes `04-UIUX/UX-<NNN> …` plus the
  shared design system. It runs off UCs, not a PRD, so it does not wait on `/approve-uc`. Its rules
  are in `_bigin/conventions/design-conventions.md` — **a separate rulebook on purpose**; design
  conventions and requirement conventions are never merged into this file. `/prototype-design` is
  kept only so old references resolve; do not run both.
- ~~**The approval stage was on the old layout and the retired `FR-###` artifact.**~~ **Resolved.**
  `/approve-fr` is superseded by **`/approve-uc`**, which reads and writes `01-Requirements/_ucs/`
  directly and re-derives the UC's live state (a human may edit the file directly while reviewing,
  outside `/bigin-transform-signal`) rather than trusting stale status. It touches only the UC's own
  file — promoting/extending any `EN-###` the UC references is **`/sync-entities`**'s job, run
  separately (§ Entity Data Model), not part of the same gate any more. `/approve-uc` does **not**
  write a PRD — that's `/bigin-generate-prd`, a separate stage run when convenient, so `approved`
  means "feature material" (§ Feature material) and the PRD picks it up on its next run rather than
  the approval producing one inline. `/approve-fr` is
  kept only so old references resolve; do not run both.
- **`enrich-feature` and `consolidate-prd` are HALTED, not merely stale.** Both are on the old
  `.bigin/` flat-file layout AND on the retired `FR-###` artifact (`.bigin/features/FR-<id>-*.md`,
  `.bigin/PRD.md`, `.bigin/epics.md`, inline `Status:` headings) — not the
  `01-Requirements/_ucs/`/`_brs/` model with `status:` frontmatter that `bigin-intake`,
  `bigin-new-project`, `extract-signal`, `bigin-transform-signal`, `bigin-generate-design`,
  `approve-uc`, and `sync-entities` use. In any migrated project `.bigin/features/` does not exist, so
  **their preconditions halt unconditionally: there is no input they can read, and no run of either
  can succeed.** Each now says so in its own first line rather than looking runnable.
  Three consequences that were live bugs and are now closed:
  - the `enriched` status is **unreachable**, so nothing may gate on it. `/approve-uc` asks about
    enrichment only when `.bigin/features/` actually exists — otherwise it doesn't mention it, instead
    of asking "enrichment hasn't run, proceed anyway?" on every approval forever.
  - `draft → approved` is the live path. § Status vocabularies keeps `enriched` as a defined value
    because a pre-migration vault has UCs already carrying it; nothing writes it today.
  - `/bigin-ba` does not route to either skill. Its pipeline list marks both as halted.

  **The migration is the largest open item in this plugin**, and it is a two-axis gap: both skills need
  the path migration *and* the FR→UC migration. Concretely, each of them:
  - reads `.bigin/features/FR-<id>-*.md` and must read `01-Requirements/_ucs/UC-<NNN> <Title>.md`;
  - keys its whole run on a single FR id per feature and must accept a feature carrying **several**
    UCs, plus a UC spanning **several** features (`primary_feature` decides the chain);
  - expects an FR's `## Functional requirements` list and must read a UC's `## 2`/`## 3` flows, its
    `## 4` rule mirror, and its `## 5` **Still open** list (not `## Open Questions`);
  - in `/consolidate-prd`'s case, should cut epics/stories as **use-case slices** (§ Traceability
    chain), flows first, rather than one story per FR line.

  `/enrich-feature`'s target shape is settled even though it isn't built: per-**UC** enrichment writing
  `## Domain Concerns` onto the UC itself (§ Feature Hub's `## Domain Research` bullet), not per-feature
  enrichment writing a hub section. Each skill's own body carries its target contract under a heading
  saying it isn't runnable, so the design intent survives without either skill looking live.

  Until then, § Feature Hub's "Maintenance contract" rows for those two describe the target, not
  the current read/write paths. **Four exits from `/bigin-transform-signal` work:** the design one
  (`/bigin-generate-design`, live), the approval one (`/approve-uc`, live), the PRD one
  (`/bigin-generate-prd`, live — it consumes what `/approve-uc` approved), and the human. Only the
  epics/stories exit is missing.
  `/prototype-design` is off the load path entirely — superseded by `/bigin-generate-design`, kept only
  so old references resolve.
  § Absorbed is now real for both load stages: `/bigin-generate-design` stamps `UC-###@version` on
  `UX-###`, and `/bigin-generate-prd` stamps it on `PRD-###` (plus `UX-###@version` in
  `design_absorbed:`) — both re-stamped whole each run, which is what makes "this design is stale" and
  "this PRD has drifted" detectable. Only the epic/story row in that table remains planned.
- **Vaults created before the UC migration need a first-touch adoption pass.** `FR-###` and `SCN-###`
  are retired but not deleted (hard rule 1). The adoption path is defined and unattended-safe —
  `_bigin/stages/transform/3-lane-uc.md` § Adopting an existing FR: the first signal that touches a
  feature with FRs mints a UC, lists them in `absorbs:`, stages their existing lines as proposed flow
  steps for the human gate, and stamps each FR `absorbed_by:`. **A feature that receives no new signal
  is never migrated**, by design: nothing rewrites requirement content unprompted. Expect a vault to
  hold both models for as long as some features stay quiet.
- ~~**FR/BR status vocabulary decided but not yet applied where it's written down.**~~ **Resolved.**
  `_bigin/templates/use-case.md`, `_bigin/templates/br.md`, and that skill's `SKILL.md` now
  all use § Status vocabularies' list (`draft → enriched → approved → consolidated`, plus
  `needs-clarification`/`removed`) and land results on `draft`, never the retired `in-review`.
  Anything still writing `in-review` or `superseded` onto a UC/BR is a bug.
- **Command order mismatch**: this document's Full chain is `PRD → EP → US → UX`, but design does not
  sit at the end of it — `/bigin-generate-design` runs off `UC-###` as soon as a UC has a main flow,
  needing neither approval nor a PRD. In practice the two load stages run in either order, and
  `/bigin-generate-prd` is the one that depends on the other: its § 9 reports whatever design exists,
  and says so plainly when none does. So the real order is `INT → UC/BR → (UX ∥ approve) → PRD → EP →
  US`, with `UX` re-run whenever a UC drifts. Decide whether the chain notation above should say so
  explicitly rather than implying a strict sequence nothing follows.
- ~~**PRD file granularity was undecided.**~~ **Resolved — PRD is one file per feature.**
  `/bigin-generate-prd` writes `02-PRD/PRD-<NNN> <Feature>.md`, one per `FEATURES.md` slug, carrying
  every currently-`approved` UC on that feature (a cross-feature UC lands in its `primary_feature`'s
  PRD, and every participating slug appears in `features:`). This matches how the rest of the vault is
  organised — the hub, the `UX-###`, and the hub's own `prd:` field are all per feature — and it makes
  per-feature staleness detectable via `absorbed:` (§ Absorbed). The two rejected readings, recorded so
  they don't come back: one vault-wide `PRD.md` with a section per feature (no per-feature staleness,
  and `prd:` degrades to a section anchor), and one PRD per UC (a PRD is a feature-level document; per
  UC it is just a reformatted use case). **`UX-###` is settled the same way**: one file per feature,
  `04-UIUX/UX-<NNN> <Feature>.md`, per `_bigin/conventions/design-conventions.md`.
- **Epic/Story file granularity is still undecided** — only their status vocab is decided
  (`draft → approved`, § Status vocabularies). This document assumes `EP-###`/`US-###` are each their
  own file with their own id; `/consolidate-prd` writes one flat `epics.md` and is halted. Decide
  per-artifact files or the flat model when that stage is migrated — and cut them as **use-case
  slices**, flows first (§ Traceability chain), not one story per requirement line. `PRD-###` is now
  settled either way, so an epics stage has a real, versioned input to decompose.
- **No front-end app exists yet to consume this vault.** A companion front-end is planned as a
  separate repository (not an Obsidian plugin bundled with this one) — treat every "a front-end
  app" mention above as a future integration point, not a dependency this plugin currently has.
