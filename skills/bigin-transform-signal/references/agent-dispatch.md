# Subagent dispatch — one per feature

Stage 3 fans out **one subagent per feature slug**, never one per lane. A feature's hub and its
UC/BR files are a single ownership domain that two lanes routinely both touch; features are
independent of each other, so they parallelize safely.

`subagent_type: general-purpose`, **session default model** (not `haiku` — this is judgment work,
unlike `extract-signal`'s mechanical extraction), `run_in_background: false`.

Dispatch concurrently across features. Within a feature, the subagent processes its signals
sequentially. Run at most **4 features concurrently** and report between waves, so a failure costs
one wave rather than the whole backlog.

**Skip the subagent entirely when a feature has one or two qualified signals** — the dispatch
overhead exceeds the work, and the orchestrator can run the lane guide inline.

## Before dispatching: resolve UC ownership

A `UC-###` is written only by its `primary_feature`'s subagent (`3-lane-uc.md` § Ownership). So for
each qualified signal, the orchestrator's routing pass must already know **which UC** it targets and
**which feature owns that UC** — otherwise two waves can both write the same file.

- Signal targets a UC owned by the feature being dispatched → include it in that subagent's worklist.
- Signal targets a UC owned by a different feature → **do not** put it in either subagent's worklist as
  a write. Hand it to the owning feature's subagent if that feature is also in this run; otherwise
  collect it as a `cross_feature_uc_change` for Stage 4.
- Signal needs a new UC whose goal belongs to another feature's actor → same: Stage 4 mints it.

## The prompt

The subagent has no memory of this conversation. Give it the cheap facts already known and point it
at real files rather than paraphrasing them — a paraphrase risks the subagent trusting a stale
summary over the source of truth.

```text
Draft the requirement artifacts for feature <slug> from its already-qualified signals.

The requirement artifact is a USE CASE (UC-###): one user goal, with its actors and trigger (§ 1),
its main flow as a step table (§ 2), its alternative/exception flows (§ 3), a read-only mirror of
the business rules governing it (§ 4), and its open questions plus decision log (§ 5). FR-### is
retired. Steps carry permanent S# ids — never renumber, reuse, or delete one.

Qualified signals (hub row # → lane), decided in Stage 2/3 — do not re-qualify or re-route them:
<row #>: <signal text> | lane: UC|BR|design|entity|context | target: <UC-### | BR-### | new>
<...>

UCs you may write (this feature is their primary_feature): <UC-### …, or "none yet">
UCs you must NOT write (owned by another feature): <UC-### (owner: <slug>) …, or "none">

Read before writing anything:
- _bigin/conventions/conventions.md — these sections ONLY, not the whole file: § ID scheme,
  § Use Case, § Frontmatter schema, § Status vocabularies, § Feature Hub, § Open Questions
  wording, § Open Questions ↔ status consistency, § Feedback handling. Add § Entity Data Model
  only if this run has an entity candidate. Skip the rest — it governs stages this task never
  touches.
- _bigin/conventions/paths.md — resolves {uc_dir}, {br_dir}, {entity_dir}, {template_uc},
  {template_br} and every other variable the lane guides refer to
- _bigin/stages/transform/3-lane-<x>.md for ONLY the lanes listed above — not all four — and
  _bigin/stages/transform/3-routing.md § Which UC — new or update if any row says "new"
- 01-Requirements/_features/<slug>.md — the hub
- every UC/BR listed in that hub's uc: / br: frontmatter, in full

Then, one signal at a time, in hub row order:
1. Follow that signal's lane guide exactly. Stage UC/BR content into ## Discussion, naming its
   destination ("new step after S4:", "S6 becomes:", "new flow E2:", "§ 1 Trigger becomes:",
   "§ 4: add BR-###, enforced at S5") as FINAL TEXT — never write into § 1-§ 6 or a BR's rule
   statement, which is the fold-in stage's job on a later run.
2. Update the hub's Signal Log row: Status and Destination per 3-routing.md § Recording the
   routing decision. Never renumber or delete a row.
3. Raise a question only when a decision is genuinely needed (3-lane-uc.md § Questions, and
   moving one to the decision log), on the UC's § 5 Still open list. Never copy a question that
   already exists on the source INT note.
4. Never invent a step, validation, threshold, notification, or branch the signal didn't state.
   Missing detail is a question, not a plausible guess.

Do NOT write to any of these — they are vault-wide or owned elsewhere, and other features are
being processed concurrently. Report candidates instead and the orchestrator will apply them:
  01-Requirements/ENTITIES.md, 01-Requirements/_entities/, 01-Requirements/DESIGN-PRINCIPLES.md,
  01-Requirements/FEATURES.md, 01-Requirements/PAIN-POINTS.md, and any UC-### listed above as
  owned by another feature
Do NOT touch another feature's hub, or any file under 00-Inbox/.
Do NOT write to 01-Requirements/_frs/ or SCENARIOS.md — both retired. If this feature has FR-###
files and no UC yet, follow 3-lane-uc.md § Adopting an existing FR: mint the UC with absorbs:,
stage the FR's existing lines as proposed steps, stamp each FR absorbed_by:, and change nothing
else about it.
Do NOT set status: approved, removed, enriched, consolidated, in-review, or superseded on a
UC/BR. Leave every UC/BR status as draft; the orchestrator sets the final status from a live
open-question count in Stage 5.

Report back, as plain lines:
  feature: <slug>
  uc: <UC-### created|updated|unchanged> (one line each, with its goal title)
  steps_staged: <UC-###> -> <N new, N changed, N removed, N flows> (one line each)
  br: <BR-### created|updated|unchanged> (one line each)
  design_directives: <N> written to the hub's ## Design Directives (row #s)
  staged: <hub row #> -> <UC-###|BR-###> (one line each)
  questions: <artifact> -> <the question>, owner client|team (one line each)
  entity_candidates: <name> | fields: <field>:<type>:<required?> … | source: <INT-###> |
                     referenced_by: <UC-### S<n>|BR-###>
  cross_feature_uc_change: <UC-###|new> | owner: <slug> | change: <the staged text> |
                           from_feature: <slug> | source: <INT-###>
  design_principle_candidates: <preference> | source: <INT-###>
  fr_adoption: <UC-### absorbs FR-###, …> (only if this feature was migrated this run)
  blocked: <hub row #> — <why, in one line> (any row you could not process)
```

## Verifying the wave

After each wave, before starting the next, check the wave's own claims — do not re-draft anything.
This is cheap and catches the failure that matters: a subagent that reports success while its hub
write never landed leaves a signal that no future run will re-collect, because its Signal Log row
now reads `staged` with nothing staged anywhere.

For every feature in the wave:

1. Open each `UC-###`/`BR-###` the subagent reported creating or updating. Confirm the
   `## Discussion` entry exists, cites the `INT-###`, and names a destination as final text rather
   than an instruction.
2. Open the hub. Confirm every reported `staged` row shows `Status: staged` and a `Destination`
   matching the artifact, and that no row was renumbered or removed.
3. Confirm every reported question exists as an unchecked `- [ ] Q:` line on the artifact named — a
   UC's `## 5` **Still open**, a BR's `## Open Questions`.
4. Confirm **no `S#`/`A#`/`E#` was renumbered or deleted** in any UC the subagent touched, and that
   nothing was written into `## 1`–`## 6` directly (the gate lives in `## Discussion`).
5. Confirm the subagent wrote nothing to a shared register or to a UC owned by another feature:
   `git diff --stat` (or a timestamp check) over `ENTITIES.md`, `DESIGN-PRINCIPLES.md`,
   `PAIN-POINTS.md`, `_entities/`, and any other-owned `UC-###` should show no change until Stage 4
   runs.

A mismatch is blocking. Dispatch one small repair subagent scoped to exactly the gap — the same
model and type, told which artifact and which hub row disagree, and told to fix only that. Re-check
that one feature before moving on.

```text
Repair 01-Requirements/_features/<slug>.md ↔ 01-Requirements/_ucs/UC-<NNN> <Title>.md.

The hub's Signal Log row #<n> says Status: staged, Destination: UC-<NNN>, but that UC's
## Discussion has no entry citing <INT-###>. The signal text is in the hub row.

Write the missing ## Discussion entry in the format _bigin/templates/use-case.md defines,
citing <INT-###> and naming its destination as final text. Do not re-route the signal, do not
create a new UC, do not write into § 1-§ 6, do not renumber any step id, and do not change any
Status. Report the entry you added.
```

## When not to fan out at all

A run whose entire worklist is one or two features with a handful of signals is faster and easier
to follow inline. Fan out when the run spans several features or a feature carries a large batch of
qualified signals — the point of the per-feature subagent is bounded context per feature, not
throughput for its own sake.

An **FR adoption** run (a migrating feature, `3-lane-uc.md` § Adopting an existing FR) is worth running
inline even for one feature: it produces the largest diff of any single run and benefits from the
orchestrator seeing it directly.
