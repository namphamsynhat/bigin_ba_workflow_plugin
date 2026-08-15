---
name: bigin-transform-signal
description: Turn signals extract-signal has already filed onto a Feature Hub's Signal Log (Status new/held) into drafted or updated Use Cases (UC) — a user goal with its flow, branches, business rules mirror, and open questions — plus the Business Rules (BR) that govern them and design directives, keep cross-feature Entities (EN) in sync, and hold every UC/BR change at a written, resumable human-review gate before folding it in. This is the Transform stage of the extract → transform → load pipeline. Use after /extract-signal has filed signals, or when asked to derive use cases or requirements, write or update a UC, process the signal backlog, qualify signals, or check whether a feature's staged UC/BR changes have been answered.
argument-hint: "[feature slug, or omit for all pending, or resume]"
---

# Bigin Transform Signal

Turns `new`/`held` signals on a Feature Hub's `## Signal Log` into drafted/updated **Use Cases**, the **Business Rules** that govern them, and design directives, syncing cross-feature Entities.

Every UC/BR change passes a written, resumable human-review gate before integration.

> **Artifact Standard:** Outputs:
>> **Use Cases (UC)** representing a single user goal (actors, triggers, preconditions, main flow `## 2`, alternative branches `## 3`, read-only rule mirrors `## 4`, and open questions + decision log behind them `## 5`), not fragmented functional requirements. A UC may span features, is updated in place as signals keep arriving, and is the artifact a human reviews and approves.
>> **Design Principles** representing how the product should look and behave at the project or feature level, not a single fragmented design detail. Feeds `{design_principles_file}` and each hub's `## Design Directives`.

---

## Non-Negotiable Core Rules

* **Immutable Step IDs:** Never renumber steps (`S#`). Append next unused IDs for new steps; retain removed steps marked as removed.
* **Strict Vocabulary:** Never invent Signal Log statuses.
* **Mirrors vs. Source of Truth:** `BR-###` is the source of truth for business rules; `## 4` in a UC is strictly a read-only mirror.
* **Concurrency & Scoping:** Per-feature subagents.
* **No Speculation:** Never invent steps, validations, or auto-resolve conflicting requirements. If undefined, raise an open question or record a conflict.
* **Boundaries:** Design signals skip PRD/UC gates and feed `/prototype-design`. Write them directly (§ Stage 3, `{stages_dir}/3-lane-design.md`); raise a question only if the directive itself is ambiguous.
* **Read Scope:** Before Stage 1, read only `{conventions_reference}` § Use Case, § Feature Hub, § Status vocabularies, § Feedback handling, and § Resumable unattended — not the whole file.
* **Written gate (default, unattended):** stage UC/BR proposals into `## Discussion`, add `- [ ] Q: ... A:` items to the UC's `## 5` (a BR's `## Open Questions`). Never blocks on a human.
* **Interactive path:** a question answered inline folds in immediately, no written round-trip.

---

## Paths

| Variable | Target path | Description |
| :--- | :--- | :--- |
| `{conventions_reference}` | `_bigin/conventions/conventions.md` | The rulebook: ID scheme, § Use Case, frontmatter schema, status vocabularies, artifact conventions |
| `{paths_reference}` | `_bigin/conventions/paths.md` | Resolves every `{variable}` the stage files below refer to — what a subagent reads instead of this table |
| `{stages_dir}` | `_bigin/stages/transform/` | One file per stage, numbered: `1-foldin`, `2-qualification`, `3-routing`, `3-lane-{uc,br,design,entity}`, `4-sync`, `5-status` |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | The feature slug registry |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | One Feature Hub per slug |
| `{uc_dir}` | `01-Requirements/_ucs/UC-<NNN> <Title>.md` | **Use Cases** — the requirement artifact |
| `{br_dir}` | `01-Requirements/_brs/BR-<NNN> <Title>.md` | Business Rules (each its own file, `uc: []` citing what it governs) |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | Proposed entity register |
| `{entity_dir}` | `01-Requirements/_entities/EN-<NNN> <Entity>.md` | Promoted entity specs |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | Durable cross-cutting design register |
| `{inbox_dir}` | `00-Inbox/INT-<NNN>.md` | Source intake notes — read frontmatter, `## Extracted signals`, and `## Open Questions` only, never `## Raw` (§ Stage 2) |
| `{template_*}` | `_bigin/templates/*` | Scaffolds (`use-case`, `br`, `entity`, `entities-register`) |

Retired and read-only: `{fr_dir}` (`_frs/`) and `{scenarios_file}` (`SCENARIOS.md`). Ids there still
resolve; nothing writes to either. A feature that still has FRs gets them adopted into a UC on first
touch (`{stages_dir}/3-lane-uc.md` § Adopting an existing FR).

All paths are project-relative; `/bigin-new-project` materializes `_bigin/conventions/`,
`_bigin/stages/`, and `_bigin/templates/`. Confirm they exist before Stage 1 — if not, stop and say
`/bigin-new-project` must run first. A subagent that can't read `3-lane-uc.md` still writes a UC, just
one following no rule.

## Execution order

Run the five stages in order every invocation. Stage 1 first is what makes a rerun useful: it
harvests answers written since the last run before staging anything new.

Each stage has one file in `{stages_dir}`; the sections below say when to run it and what it hands the
next stage, the file holds the procedure. **Load a stage file when you reach that stage, not up front** —
and of the four `3-lane-*.md` guides, only the lanes this run's signals actually hit.

| # | Stage | Procedure | Runs in |
|---|---|---|---|
| 1 | **Fold-in** — apply every staged UC/BR change whose question has been answered | `1-foldin.md` | orchestrator |
| 2 | **Qualify** — build the worklist and gate each signal before it can become requirement content | `2-qualification.md` | orchestrator |
| 3 | **Route and draft** — send each qualified signal down its lane | `3-routing.md` → `3-lane-*.md` | one subagent per feature |
| 4 | **Sync** — write the shared registers and cross-feature UC changes, then conflict-check each touched feature | `4-sync.md` | orchestrator (sequential) |
| 5 | **Status and report** — set every status from a live re-count, then verify | `5-status.md` | orchestrator |

Scope every stage to the slug in `$ARGUMENTS` when one is given; otherwise scan every
`{hub_dir}` file. A UC spanning features is in scope when **any** of its slugs is.

## Stage 1 — Resumable fold-in

* **Goal:** Harvest answered questions from previous runs before processing new signals.
* **Action:** Scan `{uc_dir}` and `{br_dir}` for every artifact with `staged` Signal Log rows. Read **`{stages_dir}/1-foldin.md`** for the three-way read (unanswered / already applied / apply now), the atomic-write order, how a step id is minted on fold-in, and the mirror reconcile.
* **Rules:** Reconcile mirrors unconditionally on every run across all referenced feature hubs.

## Stage 2 — Qualify the worklist

* **Goal:** Gate each queued signal — ready to draft, held pending a fix, or blocked on a question — before it becomes requirement content.
* **Action:** Collect every Signal Log row with `Status: new` or `held`. Re-check `held` rows every run — what blocked one last time may be resolved now. Empty worklist: say so and stop. Each row passes four gates — **blocked-on-answer, source-materialized, fidelity, dedup**. Read **`{stages_dir}/2-qualification.md`** for the procedure and the exact `Status`/`Notes` per outcome.
* **Rules:** Detect source problems; never fix them. A signal whose note awaits an answer, whose attachment was never pulled, or whose thread has no reply yet is parked `held` with the remedy named — never repaired by re-reading `## Raw` or pulling the source here. Extraction owns raw material; re-running  `/bigin-intake` and `/extract-signal` re-derives a signal whose source has since grown.

## Stage 3 — Route and draft

* **Goal:** route each qualified signal to exactly one processing lane and draft the output — UC, BR or Design.
* **Action:** Route each qualified signal to exactly one lane via the decision table in **`{stages_dir}/3-routing.md`**. That table also covers two lookups — not properties of the signal itself: **which UC, new or update** (does an existing use case cover this *goal*? most signals are a step, a branch, or a rule inside a workflow that already exists), and **durable vs. feature-scoped** for a design signal. Load the lane guide only for lanes this run's signals actually hit:

  | Lane | Produces | Guide |
  |---|---|---|
  | UC | New or updated `UC-###` — steps, flows, `## 1` metadata, `## 4` mirror rows — staged into `## Discussion` | `{stages_dir}/3-lane-uc.md` |
  | BR | New or updated `BR-###`, its own file, `uc: []` citing what it governs | `{stages_dir}/3-lane-br.md` |
  | Design | A `{design_principles_file}` row, or a directive on the hub's `## Design Directives` | `{stages_dir}/3-lane-design.md` |
  | Entity | An `{entities_file}` row promoted to `{entity_dir}` | `{stages_dir}/3-lane-entity.md` |
  | Context | The UC's `## 1` Business Need / Goal, or a `PP-###` id on its `pain_points:` | `{stages_dir}/3-lane-uc.md` |

* **Rules:**
  - **Fan out per feature, not per lane.** A feature's hub + UCs + BRs are one ownership unit, and lanes on the same feature often touch the same UC — one subagent per feature slug avoids two lanes racing each other. Features run in parallel; signals within a feature run sequentially. Dispatch prompt: **`references/agent-dispatch.md`**.
  - **Subagents only write what they own:** their own feature's hub, UCs, BRs and design principles. Never the vault-wide registers (`{entities_file}`, `{entity_dir}`) and never a UC owned by another feature. Anything else — entity candidates, cross-cutting-design candidates, `cross_feature_uc_change` — gets *reported* for the orchestrator to apply sequentially in Stage 4.


## Stage 4 — Sync and conflict-check

* **Goal:** fold in what Stage 3's subagents couldn't write themselves — shared registers, cross-feature UC changes — then conflict-check each touched feature.
* **Action:** In the orchestrator, one item at a time: apply each reported entity promotion and cross-feature UC change from Stage 3's subagent reports, write each participating hub's `## Use Cases` pointer, then conflict-check each touched feature, scoped to that feature. Procedure: **`{stages_dir}/4-sync.md`**.
* **Rules:**
  - **Stage, don't apply.** A cross-feature UC change is UC content — it passes the same review gate as any other, never a shortcut around it.
  - **No speculative promotion.** Most signals touch no entity; promote one only when Stage 3 reported it, never preemptively.
  - **No auto-resolve.** A contradiction between two touched features is raised, not decided: name both sides and stop.

## Stage 5 — Status and report

* **Goal:** set every status from a live re-count, verify it, then report.
* **Action:** Re-count each artifact's real state and set its status from that count — on a UC, count only the `## 5` **Still open** list (a decision-log row is answered history). Run the seven verification checks before reporting. Procedure and the full checklist: **`{stages_dir}/5-status.md`**.
* **Rules:**
  - **Status set last.** Never decide it earlier in a stage and leave it stale (`conventions.md` § Open Questions ↔ status consistency).
  - **A verification mismatch is blocking.** Repair and re-check rather than report a count the vault doesn't support.

```text
Stage 1 (fold-in): <N> UC/BR resolved — <slug>: UC-### now draft, ready for /enrich-feature
Stage 2 (qualify): <N> qualified, <N> held (<reason>), <N> applied as duplicate/already-covered
Stage 3 (draft):   <N> UC created, <N> updated, <N> BR created, <N> BR updated — <slug>: UC-### (staged, needs-clarification | staged, draft)
                   steps staged: <slug> UC-### — <N> new step(s), <N> changed, <N> flow(s)
                   design: <N> directive(s) — <slug> ## Design Directives, <N> DESIGN-PRINCIPLES row(s)
Stage 4 (sync):    <N> entity promotion(s), <N> cross-feature UC change(s), <N> in-feature conflict(s) — or "none this run"
cross-feature:     UC-### spans <slug> · <slug> — pointers written on both
remaining unanswered: <slug>: UC-###/BR-### — N open question(s), owner client|team
next: <slug> ready for /enrich-feature | <slug> ready for /prototype-design (design-only)
```

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Drafting from an unqualified signal.** Skipping Stage 2 produces a flow built on an incomplete
  source or an unchased rationale. It reaches `/approve-fr` looking identical to a sound one.
- **Inventing a step, a validation, or a branch nobody stated.** A plausible-looking system response
  is the cheapest way to launder a guess into approved scope, and a flow reads as complete once it has
  one. Missing → a question, or a step that names the gap.
- **Renumbering steps to keep them sequential.** Every `S#` is cited from a rule's enforcement point, a
  branch point, a story, or a prototype screen. Non-sequential ids are the design.
- **Minting a second UC for the same goal.** Two use cases covering one goal split the review and drift
  against each other. New signals about an existing goal are updates — `3-routing.md` § Which UC.
- **Fixing a source problem instead of returning it.** Pulling a missing attachment or re-reading
  `## Raw` makes a richer note that nothing re-extracts — the new material is lost while the note
  looks complete.
- **Writing a rule statement into a UC's `## 4`.** That table is a mirror; `BR-###` is the source. A
  rule written in both places drifts, and the UC copy is the one reviewers trust.
- **Manufacturing a question to have one.** Each unnecessary question adds a round-trip and parks an
  artifact at `needs-clarification` that was ready to fold.
- **Routing a behaviour change down the Design lane.** That lane skips the PRD and the approval gate,
  which makes it the cheap path — a misrouted behaviour change reaches a prototype never reviewed as
  scope (`{stages_dir}/3-routing.md` § The design boundary test).
- **Treating a repeated ask as noise.** A duplicate is `applied` with a pointer, never dropped — the
  second mention is evidence of priority.
- **Writing a shared register, or another feature's UC, from a per-feature subagent.** Two concurrent
  features `Grep` the same highest id and both mint `EN-007`, or one write overwrites the other.
- **Pointing only the primary hub at a cross-feature UC.** The other features read as uninvolved.
- **Deciding a conflict.** Recency settles a supersession, never a disagreement between two people's
  stated requirements. Raise it, name both sides, stop.
- **Setting status early.** A status decided mid-stage and left stale is this vault's most common
  drift — re-count and set it last, every time.

## Model

Per-feature subagents run on the `sonnet`: drafting is judgment-heavy
(which UC a signal belongs to, where a step sits in a flow, wording a self-contained question,
spotting a cross-feature goal). Contrast `extract-signal`, mechanical against a tight rule set,
`haiku` throughout.

Deep fidelity checking belongs to **`extract-signal`'s source audit**, next to the raw material
where a quote-anchored check is cheap. This skill does the shallow half only (§ Stage 2): the hub row
matches the note's row and its `Source` cite is specific. Re-reading transcripts here would duplicate
a rule that already has an owner, then drift from it.

## Additional resources

Paths are in § Paths; each is cited at the stage that needs it. Load a lane guide only for lanes this
run's signals actually hit.

- **`references/agent-dispatch.md`** — the per-feature subagent prompt and its report contract.
- **`references/use-case-standard.md`** — where the UC artifact's shape comes from (Cockburn, BABOK,
  Use-Case 2.0, Wiegers), which parts are established practice, which are deliberate departures, and
  why. Read before changing the template or a lane guide; not needed for a run.
