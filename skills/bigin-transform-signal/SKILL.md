---
name: bigin-transform-signal
description: Turn signals extract-signal has already filed onto a Feature Hub's Signal Log (Status new/held) into drafted or updated Functional Requirements (FR), Business Rules (BR), and design directives, keep cross-feature Entities (EN) and Business Scenarios (SCN) in sync, and hold every FR/BR change at a written, resumable human-review gate before folding it in. This is the Transform stage of the extract → transform → load pipeline. Use after /extract-signal has filed signals, or when asked to derive FRs/BRs, process the signal backlog, qualify signals, or check whether a feature's staged FR/BR changes have been answered.
argument-hint: "[feature slug, or omit for all pending, or resume]"
disable-model-invocation: true
---

# Bigin Transform Signal

Transforms raw signals (`Status: new`/`held`) on a Feature Hub's `## Signal Log` into
drafted/updated Functional Requirements (FRs), Business Rules (BRs), and design directives, while
synchronizing cross-feature Entities (ENs) and Business Scenarios (SCNs). Every FR/BR change goes
through a written, resumable human-review gate before integration.

> **Rulebook Reference:** Read `{conventions_reference}` before running. This skill provides the
> execution procedure; `conventions.md` defines the underlying standards (Feedback handling,
> Feature Hub, Status vocabularies, and Resumable unattended apply).

## Operating modes

* **Written gate (default, unattended):** Stage FR/BR proposals into `## Discussion` and add
  `- [ ] Q: ... A:` items to `## Open Questions`. Runs across single or multiple features without
  blocking on a human.
* **Interactive path:** If a human answers a question inline during conversation, fold it in
  immediately rather than creating a written round-trip.
* **Design directives are not gated.** They never enter an FR, a PRD, or an approval — they are an
  input to `/prototype-design`, which a human reviews in its own right. Write them directly
  (§ Stage 3, `references/lane-design.md`); raise a question only when the directive itself is
  ambiguous.

## Paths

| Variable | Target path | Description |
| :--- | :--- | :--- |
| `{conventions_reference}` | `references/conventions.md` (plugin root) | The rulebook: ID scheme, frontmatter schema, status vocabularies, artifact conventions |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | The feature slug registry |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | One Feature Hub per slug |
| `{fr_dir}` | `01-Requirements/_frs/FR-<NNN> <Title>.md` | Functional Requirements |
| `{br_dir}` | `01-Requirements/_brs/BR-<NNN> <Title>.md` | Business Rules (each its own file, `fr: []` citing what it constrains) |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | Proposed entity register |
| `{entity_dir}` | `01-Requirements/_entities/EN-<NNN> <Entity>.md` | Promoted entity specs |
| `{scenarios_file}` | `01-Requirements/SCENARIOS.md` | Cross-feature scenario register (`SCN-###`) |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | Durable cross-cutting design register |
| `{inbox_dir}` | `00-Inbox/INT-<NNN>.md` | Source intake notes — read frontmatter, `## Extracted signals`, and `## Open Questions` only, never `## Raw` (§ Stage 2) |
| `{template_*}` | `skills/bigin-transform-signal/template/*` | Scaffolds (`fr`, `br`, `entity`, `scenario-register`) |

## Execution order

Run the five stages in order on every invocation. Stage 1 first is what makes a rerun useful:
it harvests answers a human wrote since the last run before this run stages anything new.

1. **Fold-in** — apply every staged FR/BR change whose question has been answered.
2. **Qualify** — build the worklist and gate each signal before it can become requirement content.
3. **Route and draft** — send each qualified signal down its lane; one subagent per feature.
4. **Sync** — write the shared registers, then conflict-check each touched feature.
5. **Status and report**.

Scope every stage to the slug in `$ARGUMENTS` when one is given; otherwise scan every
`{hub_dir}` file.

## Stage 1 — Resumable fold-in

For every FR/BR this skill has ever staged a change on (scan `{fr_dir}`/`{br_dir}` for one whose
feature has a `staged` Signal Log row pointing at it):

1. **Dedup-check before writing anything.** If the artifact's `## Changelog` already cites this
   fold-in's `INT-###`, this is a retry of a completed apply — write nothing, skip to step 3.
2. **Skip the genuinely unanswered** (the `A:` line is still blank). Otherwise compose the *entire*
   change — fold the `## Discussion` entry into `## Functional requirements` (FR) or the rule
   statement (BR), bump `version`, append `## Changelog` — and write the file **once, atomically**.
   Before that write lands nothing has changed, so a kill mid-run leaves it exactly where a future
   run can safely retry (`conventions.md` § Resumable unattended apply).
3. **Reconcile mirrors, unconditionally, every run.** Flip the hub's Signal Log row to `applied`
   if the artifact now shows the fold-in; tick the source INT note's own `## Open Questions` copy
   once the FR/BR's copy is resolved. Setting an already-correct field again is a no-op, not a
   duplicate — never skip this because step 1 said "already done."
4. Set `status` last, per § Stage 5.

## Stage 2 — Qualify the worklist

Collect every Signal Log row whose `Status` is `new` or `held`. `held` rows are re-checked every
run: what blocked one last time may be resolved now. If the worklist is empty after this stage,
say so and stop.

Each row passes four gates before it can become requirement content — **blocked-on-answer,
source-materialized, fidelity, and dedup**. The full gate procedure, including the exact `Status`
and `Notes` to write for each outcome, is in **`references/qualification.md`**. Read it before
running this stage.

Two rules matter enough to state here:

- **This skill detects source problems; it does not fix them.** A signal whose intake note is
  still waiting on an answer, whose attachment was never pulled, or whose email thread has no
  reply yet is parked `held` with a note naming the remedy — never repaired by re-reading `## Raw`
  or pulling the missing source here. Extraction owns raw material; re-running `/bigin-intake` and
  `/extract-signal` is what re-derives a signal from a source that has since grown.
- **Never invent a Signal Log status.** The vocabulary is fixed at `new · held · staged · applied ·
  question · conflict · superseded · rejected` (`conventions.md` § Feature Hub). A redundant signal
  is `applied` with a `Notes` pointer, not `removed` or `duplicated` — `removed` is an FR/BR status
  and human-gated only (hard rule 4).

## Stage 3 — Route and draft

Route each qualified signal to exactly one lane using the decision table in
**`references/routing.md`** — which also covers the two routing calls that are lookups rather than
properties of the signal: new-vs-update (does an FR/BR on this feature already cover it?) and
durable-vs-feature-scoped for a design signal.

| Lane | Produces | Guide |
|---|---|---|
| FR | New or updated `FR-###`, staged into `## Discussion` | `references/lane-fr.md` |
| BR | New or updated `BR-###`, its own file, `fr: []` citing what it constrains | `references/lane-br.md` |
| Design | A `{design_principles_file}` row, or a directive on the hub's `## UX Spec` | `references/lane-design.md` |
| Entity | An `{entities_file}` row promoted to `{entity_dir}` | `references/lane-entity.md` |
| Context | `## Business goal` / `## Problem & Pain Points` on the FR | `references/lane-fr.md` |

**Fan out one subagent per feature slug, never per lane.** A feature's hub and its FR/BR files are
one ownership domain — two lanes on the same feature routinely touch the same FR file, so a
per-lane fan-out races itself. Features are independent, so they parallelize safely. Within a
feature, process signals sequentially. The dispatch prompt is in
**`references/agent-dispatch.md`**.

**Subagents never write a shared register.** `{entities_file}`, `{entity_dir}`,
`{scenarios_file}`, and `{design_principles_file}` are vault-wide and would race across concurrent
features. A subagent *reports* its entity, scenario, and cross-cutting-design candidates; the
orchestrator applies them in Stage 4, sequentially. A subagent does write its own feature's hub
and FR/BR files.

## Stage 4 — Sync and conflict-check

1. **Write the shared registers**, one at a time, from what Stage 3's subagents reported: promote
   entities, create/update `SCN-###` rows, append design-principle rows, and add the matching
   one-line pointers to each participating hub's `## Entities` / `## Business Scenarios` sections.
   `references/lane-entity.md` and `references/lane-design.md` hold the detail.
2. **Conflict-check each touched feature, scoped to that feature.** After a new or updated FR/BR
   lands, re-read that feature's FR together with its BRs and look for a genuine contradiction —
   two statements that cannot both hold. Scope is the feature, not the vault: a vault-wide sweep
   costs quadratically more and belongs to `/enrich-feature`'s concern surfacing.
   A contradiction is never auto-resolved. Raise one `- [ ] Q:` on the FR naming both sides, flip
   the triggering Signal Log row to `conflict` citing the earlier row's `#`, and let Stage 5 set
   the status.

Most signals touch neither an entity nor a scenario. Never promote an entity or manufacture a
scenario speculatively — both stay `proposed`/absent until a signal genuinely needs them.

## Stage 5 — Status and report

**Set every status last, from a live re-count** — never decide it earlier in a stage and leave it
stale (`conventions.md` § Open Questions ↔ status consistency):

- Re-count unchecked `## Open Questions` boxes on each artifact touched this run. `> 0` →
  `status: needs-clarification`. `0` → `draft`, or the stage the artifact had already reached if
  this run only resolved a question without editing content.
- **Never write `in-review` or `superseded` on an FR/BR** — both are retired from that vocabulary
  (`conventions.md` § Status vocabularies). Editing content on an `enriched`/`approved`/
  `consolidated` artifact sets it back to `draft`/`needs-clarification`; approval does not freeze
  an FR (hard rule 7).
- Refresh each touched hub's `## Requirement Readiness` snapshot and append a `## Notes / History`
  bullet. **Do not change the hub's `status:`** — it mirrors the `{requirements_file}` row
  (`proposed`/`committed`/`built`/…), which is a scope state, not a workflow state. There is no
  "ready for PRD" feature status; readiness is the snapshot table plus each FR's own status.

**Before reporting, verify these five — every run.** Each is a real failure that reports as success:

1. Every row moved to `staged` has a matching `## Discussion` entry citing its `INT-###`. A `staged`
   row with nothing staged is stranded: it no longer reads as pending, so no future run collects it.
2. Every row moved to `applied` shows its content in the artifact, or a `Notes` pointer explaining
   why no change was needed (`qualification.md` § Gate 4).
3. No Signal Log row was renumbered, deleted, or had its `Signal`/`Source` text rewritten.
4. Every question raised this run exists as an unchecked `- [ ] Q:` on the artifact named, and no
   question duplicates one already open on the source INT note.
5. Each touched artifact's `status` matches its live unchecked-question count.

A mismatch is blocking: repair it and re-check before reporting, rather than reporting a count that
the vault does not support.

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

Named because each one produces a run that looks clean. Ordered by how expensive they are to
discover later.

- **Drafting from an unqualified signal.** Skipping Stage 2 to get to the drafting produces an FR
  built on a claim whose source was incomplete or whose rationale is still being chased. It reaches
  `/approve-fr` looking identical to a sound one.
- **Fixing a source problem instead of returning it.** Pulling a missing attachment or re-reading
  `## Raw` here produces a richer note that nothing re-extracts — the new material is silently lost
  while the note now looks complete.
- **Manufacturing a question to have one.** Every unnecessary question adds a human round-trip and
  parks an artifact at `needs-clarification` that was ready to fold.
- **Routing a behaviour change down the Design lane.** The Design lane skips the PRD and the
  approval gate, which makes it the cheap path. A misrouted behaviour change reaches a prototype
  having never been reviewed as scope (`references/routing.md` § The design boundary test).
- **Treating a repeated ask as noise.** A duplicate is `applied` with a pointer, never dropped —
  the second mention is evidence of priority, and deleting the row destroys it.
- **Writing a shared register from inside a per-feature subagent.** Two concurrent features `Grep`
  the same highest id and both mint `EN-007`, or one register append overwrites the other.
- **Deciding a conflict.** Recency settles a supersession; it never settles a disagreement between
  two people's stated requirements. Raise it, name both sides, stop.
- **Setting status early.** A status decided mid-stage and left stale is the single most common
  drift in this vault — re-count and set it last, every time.

## Model and agent involvement

Drafting an FR/BR is judgment-heavy — new-vs-update, wording a self-contained question, spotting a
cross-feature flow — so per-feature subagents run on the **session's default model**, not `haiku`.
Contrast `extract-signal`, whose inner loop is mechanical extraction against a tight rule set and
defaults to `haiku` throughout.

Deep fidelity checking — confirming a signal is actually supported by the raw source rather than
inferred by a model — lives in **`extract-signal`'s verification pass**, next to the raw material,
where a quote-anchored check is cheap. This skill does the shallow half only (§ Stage 2): the hub
row still matches the note's own row, and its `Source` cite is specific. Re-reading transcripts and
attachments here would duplicate a rule that already has an owner and would drift from it.

## Additional resources

- **`references/conventions.md`** (plugin root) — the rulebook: ID scheme and numbering, the
  Signal Log status vocabulary, FR/BR status vocabulary, `## Open Questions` wording, the
  resumable-apply checkpoint discipline, and § Feedback handling's in-place-edit rule (hard
  rule 7).
- **`references/qualification.md`** — Stage 2's four gates, outcome-by-outcome.
- **`references/routing.md`** — the lane decision table and the design-vs-FR boundary test.
- **`references/lane-fr.md`**, **`references/lane-br.md`**, **`references/lane-design.md`**,
  **`references/lane-entity.md`** — one drafting guide per lane, loaded by the per-feature
  subagent for the lanes its signals actually need.
- **`references/agent-dispatch.md`** — the per-feature subagent prompt and its report contract.
- **`template/fr.md`**, **`template/br.md`**, **`template/entity.md`**,
  **`template/scenario-register.md`** — scaffolds for each artifact this skill creates.
