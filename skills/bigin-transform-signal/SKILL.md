---
name: bigin-transform-signal
description: Turn signals extract-signal has already filed onto a Feature Hub's Signal Log (Status new/held) into drafted or updated Functional Requirements (FR), Business Rules (BR), and design directives, keep cross-feature Entities (EN) and Business Scenarios (SCN) in sync, and hold every FR/BR change at a written, resumable human-review gate before folding it in. This is the Transform stage of the extract → transform → load pipeline. Use after /extract-signal has filed signals, or when asked to derive FRs/BRs, process the signal backlog, qualify signals, or check whether a feature's staged FR/BR changes have been answered.
argument-hint: "[feature slug, or omit for all pending, or resume]"
---

# Bigin Transform Signal

Turns `new`/`held` signals on a Feature Hub's `## Signal Log` into drafted/updated FRs, BRs, and
design directives, syncing cross-feature Entities and Business Scenarios. Every FR/BR change passes a
written, resumable human-review gate before integration.

This skill is the procedure; `{conventions_reference}` is the standard it follows. Read that skill's
§ Feature Hub, § Status vocabularies, § Feedback handling, and § Resumable unattended apply before
Stage 1 — not the whole file.

## Operating modes

* **Written gate (default, unattended):** stage FR/BR proposals into `## Discussion`, add
  `- [ ] Q: ... A:` items to `## Open Questions`. Never blocks on a human.
* **Interactive path:** a question answered inline folds in immediately, no written round-trip.
* **Design directives are not gated.** They never reach an FR, PRD, or approval — they feed
  `/prototype-design`, reviewed in its own right. Write them directly (§ Stage 3,
  `{stages_dir}/3-lane-design.md`); raise a question only if the directive itself is ambiguous.

## Paths

| Variable | Target path | Description |
| :--- | :--- | :--- |
| `{conventions_reference}` | `_bigin/conventions/conventions.md` | The rulebook: ID scheme, frontmatter schema, status vocabularies, artifact conventions |
| `{paths_reference}` | `_bigin/conventions/paths.md` | Resolves every `{variable}` the stage files below refer to — what a subagent reads instead of this table |
| `{stages_dir}` | `_bigin/stages/transform/` | One file per stage, numbered: `1-foldin`, `2-qualification`, `3-routing`, `3-lane-{fr,br,design,entity}`, `4-sync`, `5-status` |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | The feature slug registry |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | One Feature Hub per slug |
| `{fr_dir}` | `01-Requirements/_frs/FR-<NNN> <Title>.md` | Functional Requirements |
| `{br_dir}` | `01-Requirements/_brs/BR-<NNN> <Title>.md` | Business Rules (each its own file, `fr: []` citing what it constrains) |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | Proposed entity register |
| `{entity_dir}` | `01-Requirements/_entities/EN-<NNN> <Entity>.md` | Promoted entity specs |
| `{scenarios_file}` | `01-Requirements/SCENARIOS.md` | Cross-feature scenario register (`SCN-###`) |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | Durable cross-cutting design register |
| `{inbox_dir}` | `00-Inbox/INT-<NNN>.md` | Source intake notes — read frontmatter, `## Extracted signals`, and `## Open Questions` only, never `## Raw` (§ Stage 2) |
| `{template_*}` | `_bigin/templates/*` | Scaffolds (`fr`, `br`, `entity`, `scenario-register`) |

All paths are project-relative; `/bigin-new-project` materializes `_bigin/conventions/`,
`_bigin/stages/`, and `_bigin/templates/`. Confirm they exist before Stage 1 — if not, stop and say
`/bigin-new-project` must run first. A subagent that can't read `3-lane-fr.md` still writes an FR, just
one following no rule.

## Execution order

Run the five stages in order every invocation. Stage 1 first is what makes a rerun useful: it
harvests answers written since the last run before staging anything new.

Each stage has one file in `{stages_dir}`; the sections below say when to run it and what it hands the
next stage, the file holds the procedure. **Load a stage file when you reach that stage, not up front** —
and of the four `3-lane-*.md` guides, only the lanes this run's signals actually hit.

| # | Stage | Procedure | Runs in |
|---|---|---|---|
| 1 | **Fold-in** — apply every staged FR/BR change whose question has been answered | `1-foldin.md` | orchestrator |
| 2 | **Qualify** — build the worklist and gate each signal before it can become requirement content | `2-qualification.md` | orchestrator |
| 3 | **Route and draft** — send each qualified signal down its lane | `3-routing.md` → `3-lane-*.md` | one subagent per feature |
| 4 | **Sync** — write the shared registers, then conflict-check each touched feature | `4-sync.md` | orchestrator (sequential) |
| 5 | **Status and report** — set every status from a live re-count, then verify | `5-status.md` | orchestrator |

Scope every stage to the slug in `$ARGUMENTS` when one is given; otherwise scan every
`{hub_dir}` file.

## Stage 1 — Resumable fold-in

Scan `{fr_dir}`/`{br_dir}` for every artifact whose feature has a `staged` Signal Log row pointing at
it. Read **`{stages_dir}/1-foldin.md`** for the three-way read (unanswered / already applied / apply
now), the atomic-write order, and the mirror reconcile.

One rule matters enough to state here: **reconcile mirrors unconditionally, every run** — including for
an artifact that was already applied. Re-setting a correct field is a no-op, not a duplicate; skipping
it is how a prior run's kill leaves a hub reading `staged` against a folded-in FR forever.

## Stage 2 — Qualify the worklist

Collect every Signal Log row with `Status: new` or `held`. Re-check `held` rows every run — what
blocked one last time may be resolved now. Empty worklist: say so and stop.

Each row passes four gates — **blocked-on-answer, source-materialized, fidelity, dedup**. Read
**`{stages_dir}/2-qualification.md`** for the procedure and the exact `Status`/`Notes` per outcome.

Two rules matter enough to state here:

- **Detect source problems; never fix them.** A signal whose note awaits an answer, whose attachment
  was never pulled, or whose thread has no reply yet is parked `held` with the remedy named — never
  repaired by re-reading `## Raw` or pulling the source here. Extraction owns raw material; re-running
  `/bigin-intake` and `/extract-signal` re-derives a signal whose source has since grown.
- **Never invent a Signal Log status.** Fixed vocabulary: `new · held · staged · applied · question ·
  conflict · superseded · rejected` (`conventions.md` § Feature Hub). A redundant signal is `applied`
  with a `Notes` pointer, not `removed` or `duplicated` — `removed` is an FR/BR status, human-gated
  only (hard rule 4).

## Stage 3 — Route and draft

Route each qualified signal to exactly one lane via the decision table in
**`{stages_dir}/3-routing.md`**, which also covers the two calls that are lookups rather than properties
of the signal: new-vs-update (does an existing FR/BR on this feature already cover it?) and
durable-vs-feature-scoped for a design signal.

| Lane | Produces | Guide |
|---|---|---|
| FR | New or updated `FR-###`, staged into `## Discussion` | `{stages_dir}/3-lane-fr.md` |
| BR | New or updated `BR-###`, its own file, `fr: []` citing what it constrains | `{stages_dir}/3-lane-br.md` |
| Design | A `{design_principles_file}` row, or a directive on the hub's `## UX Spec` | `{stages_dir}/3-lane-design.md` |
| Entity | An `{entities_file}` row promoted to `{entity_dir}` | `{stages_dir}/3-lane-entity.md` |
| Context | `## Business goal` / `## Problem & Pain Points` on the FR | `{stages_dir}/3-lane-fr.md` |

**Fan out one subagent per feature slug, never per lane.** A feature's hub and FR/BR files are one
ownership domain — two lanes on the same feature routinely touch the same FR, so a per-lane fan-out
races itself. Features are independent and parallelize safely; within a feature, process signals
sequentially. Dispatch prompt: **`references/agent-dispatch.md`**.

**Subagents never write a shared register.** `{entities_file}`, `{entity_dir}`, `{scenarios_file}`,
and `{design_principles_file}` are vault-wide and would race across concurrent features. A subagent
*reports* its entity, scenario, and cross-cutting-design candidates; the orchestrator applies them
sequentially in Stage 4. A subagent does write its own feature's hub and FR/BR files.

## Stage 4 — Sync and conflict-check

Write the shared registers from what Stage 3's subagents reported — **one at a time, in the
orchestrator** — then conflict-check each touched feature, scoped to that feature. Procedure:
**`{stages_dir}/4-sync.md`**.

Most signals touch neither an entity nor a scenario. Never promote an entity or manufacture a scenario
speculatively — both stay `proposed`/absent until a signal genuinely needs them. And never auto-resolve
a contradiction: raise it, name both sides, stop.

## Stage 5 — Status and report

**Set every status last, from a live re-count** — never decide it earlier in a stage and leave it stale
(`conventions.md` § Open Questions ↔ status consistency). Then run the five verification checks before
reporting: each catches a real failure that otherwise reports as success. Procedure and the full
checklist: **`{stages_dir}/5-status.md`**.

A verification mismatch is blocking: repair and re-check rather than report a count the vault doesn't
support.

```text
Stage 1 (fold-in): <N> FR/BR resolved — <slug>: FR-### now draft, ready for /enrich-feature
Stage 2 (qualify): <N> qualified, <N> held (<reason>), <N> applied as duplicate/already-covered
Stage 3 (draft):   <N> FR created, <N> updated, <N> BR created, <N> BR updated — <slug>: FR-### (staged, needs-clarification | staged, draft)
                   design: <N> directive(s) — <slug> ## UX Spec, <N> DESIGN-PRINCIPLES row(s)
Stage 4 (sync):    <N> entity promotion(s), <N> scenario(s), <N> in-feature conflict(s) — or "none this run"
remaining unanswered: <slug>: FR-###/BR-### — N open question(s), owner client|team
next: <slug> ready for /enrich-feature | <slug> ready for /prototype-design (design-only)
```

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Drafting from an unqualified signal.** Skipping Stage 2 produces an FR built on an incomplete
  source or an unchased rationale. It reaches `/approve-fr` looking identical to a sound one.
- **Fixing a source problem instead of returning it.** Pulling a missing attachment or re-reading
  `## Raw` makes a richer note that nothing re-extracts — the new material is lost while the note
  looks complete.
- **Manufacturing a question to have one.** Each unnecessary question adds a round-trip and parks an
  artifact at `needs-clarification` that was ready to fold.
- **Routing a behaviour change down the Design lane.** That lane skips the PRD and the approval gate,
  which makes it the cheap path — a misrouted behaviour change reaches a prototype never reviewed as
  scope (`{stages_dir}/3-routing.md` § The design boundary test).
- **Treating a repeated ask as noise.** A duplicate is `applied` with a pointer, never dropped — the
  second mention is evidence of priority.
- **Writing a shared register from a per-feature subagent.** Two concurrent features `Grep` the same
  highest id and both mint `EN-007`, or one append overwrites the other.
- **Deciding a conflict.** Recency settles a supersession, never a disagreement between two people's
  stated requirements. Raise it, name both sides, stop.
- **Setting status early.** A status decided mid-stage and left stale is this vault's most common
  drift — re-count and set it last, every time.

## Model

Per-feature subagents run on the **session's default model**, not `haiku`: drafting is judgment-heavy
(new-vs-update, wording a self-contained question, spotting a cross-feature flow). Contrast
`extract-signal`, mechanical against a tight rule set, `haiku` throughout.

Deep fidelity checking belongs to **`extract-signal`'s verification pass**, next to the raw material
where a quote-anchored check is cheap. This skill does the shallow half only (§ Stage 2): the hub row
matches the note's row and its `Source` cite is specific. Re-reading transcripts here would duplicate
a rule that already has an owner, then drift from it.

## Additional resources

Paths are in § Paths; each is cited at the stage that needs it. Load a lane guide only for lanes this
run's signals actually hit. **`references/agent-dispatch.md`** holds the per-feature subagent prompt
and its report contract.
