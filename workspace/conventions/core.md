# Conventions — core

The rules **every** stage needs, and the only conventions file a skill reads unconditionally:
the ID scheme, the frontmatter schema, the status vocabularies, Obsidian-safe markdown, file
naming, and the changelog section.

The precondition version check is **not** here — it is `version-check.md`, because a skill runs it
and a worker never does.

Everything else lives in a sibling file, loaded only by the stage that needs it — see
`conventions.md` for the map.

## ID scheme (permanent, never reused)

| Prefix | Artifact | Folder | Status |
|---|---|---|---|
| INT | Intake note (email / meeting; requirement or feedback) | 00-Inbox | Implemented |
| UC | **Use case** — the requirement artifact: one user goal, its flow, its branches, its rules mirror, its open questions | 01-Requirements/_ucs | Implemented — its own file, `UC-<NNN> <Title>.md`, drafted/updated by `/bigin-transform-signal`. May span features. Status: `draft → enriched → approved → consolidated`, plus `needs-clarification`/`removed` (§ Status vocabularies). See `use-case.md` § Use Case |
| BR | Business rule | 01-Requirements/_brs | Implemented — its own file, `BR-<NNN> <Title>.md`, `uc: []` citing the use case(s) it governs (feature-level if none apply yet). Same status vocab as UC. **The source of the rule** — a UC's `§ 4` is a read-only mirror |
| PP | Pain point (register row, ids cited from a UC's `pain_points:`, no separate per-item file) | 01-Requirements | Implemented |
| EN | Entity data model | 01-Requirements/_entities | Implemented — `/bigin-transform-signal` only cites an `ENTITIES.md` `proposed` row, by name; `/sync-entities` is the only skill that promotes one into its own file, `EN-<NNN> <Entity>.md`, and only once an approved UC (or a BR it mirrors) actually references it. Deferring promotion until after approval means a still-drafting UC never leaves behind an entity doc nobody ended up needing |
| FR | ~~Feature requirement~~ | 01-Requirements/_frs | **Retired**, replaced by `UC-###`. Existing files stay on disk, frozen, carrying `absorbed_by: UC-###`; ids keep resolving and nothing writes there any more (`use-case.md` § Use Case → What it replaced) |
| SCN | ~~Business scenario (cross-feature flow)~~ | 01-Requirements/SCENARIOS.md | **Retired**, replaced by a `UC-###` whose `features:` lists every slug it touches. Existing rows stay, `superseded`, naming the UC that absorbed them (`registers.md` § Business Scenarios (retired)) |
| PRD | Product requirements doc | 02-PRD | Implemented — **one file per feature**, `PRD-<NNN> <Feature>.md`, written by `/bigin-generate-prd` from that feature's **`approved`** UCs (`feature-hub.md` § Feature material) plus its `UX-###` design. Granularity is settled: per feature, not per-UC and not one vault-wide document (§ Reconciliation notes). A business-flow document, never a technical spec — its six hard rules live in that skill's `SKILL.md`, not here, the same way design's live in `design-conventions.md`. Status: `draft → approved`, `approved` human-only (§ Status vocabularies). Carries `absorbed: [UC-###@version]`, which is what makes PRD drift detectable (`runtime.md` § Absorbed) |
| EP | Epic | 03-Epics-Stories | **Not built** — nothing writes epics or stories today; they are cut by hand from approved UCs. Same `draft → approved` status vocab once split out |
| US | User story | 03-Epics-Stories | **Planned** — stories live nested under their epic in `epics.md` today, not as their own `US-###` files. Same `draft → approved` status vocab once split out |
| UX | UI/UX spec | 04-UIUX | Implemented — one `UX-<NNN> <Feature>.md` per feature, written by `/bigin-generate-design` from the feature's UC(s). Its `## 8 Rendered Artifacts` is the one section that skill never writes: `/bigin-render-design-od` appends a pointer row there when a human asks for a prototype. **Its rules are not in this file:** the design rulebook is `_bigin/conventions/design-conventions.md`, deliberately separate, and it carries UX's own status vocabulary (`draft → needs-clarification → accepted`), paths, and hard rules. The deleted `/prototype-design` wrote `<feature-id>-prototype.md` with no id |

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
(`use-case.md` § Use Case → Step ids). They are the citation target that replaced per-statement `FR-###` ids, so a
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
(`type: feature-hub`) — see `feature-hub.md` § Feature Hub below. Also singleton, vault-wide:
`01-Requirements/DESIGN-PRINCIPLES.md` (`type: design-principles`) — the standing client
design-preference register, maintained by `/extract-signal`, see `registers.md` § Design Principles Register
below. Also singleton, vault-wide: `01-Requirements/ENTITIES.md` (`type: entity-map`) — the
canonical entity list. `/extract-signal` files a `proposed` row the moment a signal describes one;
`/sync-entities` points a row at its promoted `EN-###` doc once one exists. Mirrors `FEATURES.md`
(see `registers.md` § Entity Data Model). Also singleton, vault-wide: `01-Requirements/PAIN-POINTS.md`
(`type: pain-point-register`) — the vault-wide pain-point register (see `registers.md` § Pain Point Register).

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
                         # and `registers.md` § Entity Data Model for EN. An intake note's own status vocabulary
                         # (raw | needs-clarification | in-review | consumed) is separate again —
                         # see `intake.md` § Intake capture & the question loop.
version: 1.0
synced: true             # use-case only: false from the moment /approve-uc sets status: approved,
                         # until /sync-entities has promoted/extended entities: [] and refreshed the
                         # feature hub(s) for this UC (`registers.md` § Entity Data Model). Meaningless otherwise.
level: user-goal         # use-case only: summary | user-goal | subfunction (`use-case.md` § Use Case)
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
                         # missing here is never read (`intake.md` § Intake capture & the question loop)
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
   (`registers.md` § When a signal can't map).
3. **One line per table cell.** GFM has no multi-line cell. Long System Response text stays one
   line and wraps; if it genuinely needs a break, use `<br>`. A literal newline splits the table.
4. **Only real questions are checkboxes.** A `- [ ] Q:` line in an artifact body is counted by
   `questions.md` § Open Questions ↔ status consistency, so a *format example* belongs inside the template's
   guidance comment, never in the body — instantiating it otherwise mints a phantom open question
   and renders an empty checkbox.

**Instantiate the structure, not the guidance.** A template's `<!-- … -->` blocks are the schema
spec for whoever writes the artifact; they are not artifact content. Copy the frontmatter keys,
headings, and table headers — drop the guidance comments. The rules they restate live in
`_bigin/stages/` and in this file, which is where a later stage looks them up anyway. Carrying them
into the artifact costs every downstream stage the tokens to re-read them on every open, and leaves
them visible in Obsidian's Live Preview. Retain only a comment that records something about *this*
artifact (why a section is deliberately empty, for instance).

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
| `draft` | Content exists — created or last folded in by `/bigin-transform-signal`. The default resting state until a human approves it. |
| `needs-clarification` | At least one unresolved `- [ ] Q:` line in the artifact's question list — a UC's `## 5` **Still open**, a BR's `## Open Questions` (`questions.md` § Open Questions ↔ status consistency's invariant — unchanged, just now one value in this list rather than sitting alongside a separate `in-review`). Once every question resolves, status moves to whatever it would otherwise be — `draft`, or `approved`/`consolidated` if a later-stage edit is what raised the question. Never a fixed placeholder. |
| `enriched` | Permanently unreachable on a UC — enrichment moved off the UC entirely to a feature-scoped, hub-level pass (§ Reconciliation notes, `feature-hub.md` § Feature Hub). Kept only as a defined value for a pre-migration vault that already carries it. |
| `approved` | A human has approved it via `/approve-uc`; it's feature material (`feature-hub.md` § Feature material) and `/bigin-generate-prd` will fold it into its feature's PRD on the next run. Epics/stories still wait on a migrated stage (§ Reconciliation notes). |
| `consolidated` | **Legacy-only, unreachable.** It meant an epic/story had been generated back from the UC. No skill sets it — the epic/story stage was never built — so nothing may gate on it. |
| `removed` | A human decided this UC/BR is no longer relevant/wanted (`intake.md` § Feedback handling's "Removing scope") — human-gated like `approved`, never set by an agent. Not deletion (hard rule 1): the file, id, and history stay intact. |

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
resolvable for anything that already cites it (`registers.md` § Entity Data Model, A fragment already on disk).

**INT** (intake notes): `raw | needs-clarification | in-review | consumed` — see § Intake capture
& the question loop and `/bigin-intake`'s own queue logic. Unrelated to the UC/BR list above;
don't conflate the two just because both use `needs-clarification`.

## File naming

`<ID> <short title>.md` — e.g. `UC-012 Export invoices in bulk.md`

## Changelog section (all non-intake artifacts)

```md
## Changelog
- 1.0 (2026-07-02) — initial draft from INT-003
- 1.1 (2026-07-05) — INT-009 feedback: export limited to 500 rows
```
