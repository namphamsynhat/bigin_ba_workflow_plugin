# Subagent dispatch — one per feature

Stage 3 fans out **one subagent per feature slug**, never one per lane. A feature's hub and its
FR/BR files are a single ownership domain that two lanes routinely both touch; features are
independent of each other, so they parallelize safely.

`subagent_type: general-purpose`, **session default model** (not `haiku` — this is judgment work,
unlike `extract-signal`'s mechanical extraction), `run_in_background: false`.

Dispatch concurrently across features. Within a feature, the subagent processes its signals
sequentially. Run at most **4 features concurrently** and report between waves, so a failure costs
one wave rather than the whole backlog.

**Skip the subagent entirely when a feature has one or two qualified signals** — the dispatch
overhead exceeds the work, and the orchestrator can run the lane guide inline.

## The prompt

The subagent has no memory of this conversation. Give it the cheap facts already known and point it
at real files rather than paraphrasing them — a paraphrase risks the subagent trusting a stale
summary over the source of truth.

```text
Draft the requirement artifacts for feature <slug> from its already-qualified signals.

Qualified signals (hub row # → lane), decided in Stage 2/3 — do not re-qualify or re-route them:
<row #>: <signal text> | lane: FR|BR|design|entity|context | new-or-update: <FR-### | new>
<...>

Read before writing anything:
- _bigin/conventions/conventions.md — these sections ONLY, not the whole file: § ID scheme,
  § Frontmatter schema, § Status vocabularies, § Feature Hub, § Open Questions wording,
  § Open Questions ↔ status consistency, § Feedback handling. Add § Entity Data Model or
  § Business Scenarios only if this run has an entity or scenario candidate. Skip the rest —
  it governs stages this task never touches.
- _bigin/conventions/paths.md — resolves {fr_dir}, {br_dir}, {entity_dir}, {template_fr},
  {template_br} and every other variable the lane guides refer to
- _bigin/stages/transform/3-lane-<x>.md for ONLY the lanes listed above — not all four — and
  _bigin/stages/transform/3-routing.md § New vs. update if any row says "new"
- 01-Requirements/_features/<slug>.md — the hub
- every FR/BR listed in that hub's fr: / br: frontmatter, in full

Then, one signal at a time, in hub row order:
1. Follow that signal's lane guide exactly. Stage FR/BR content into ## Discussion — never
   write into ## Functional requirements or a BR's rule statement, which is the fold-in
   stage's job on a later run.
2. Update the hub's Signal Log row: Status and Destination per 3-routing.md § Recording the
   routing decision. Never renumber or delete a row.
3. Raise a question only when a decision is genuinely needed (3-lane-fr.md § Raising a
   question). Never copy a question that already exists on the source INT note.

Do NOT write to any of these — they are vault-wide and other features are being processed
concurrently. Report candidates instead and the orchestrator will apply them:
  01-Requirements/ENTITIES.md, 01-Requirements/_entities/, 01-Requirements/SCENARIOS.md,
  01-Requirements/DESIGN-PRINCIPLES.md, 01-Requirements/FEATURES.md, 01-Requirements/PAIN-POINTS.md
Do NOT touch another feature's hub, or any file under 00-Inbox/.
Do NOT set status: approved, removed, enriched, consolidated, in-review, or superseded on an
FR/BR. Leave every FR/BR status as draft; the orchestrator sets the final status from a live
open-question count in Stage 5.

Report back, as plain lines:
  feature: <slug>
  fr: <FR-### created|updated|unchanged> (one line each)
  br: <BR-### created|updated|unchanged> (one line each)
  design_directives: <N> written to the hub's ## Design Directives (row #s)
  staged: <hub row #> -> <FR-###|BR-###> (one line each)
  questions: <artifact> -> <the question>, owner client|team (one line each)
  entity_candidates: <name> | fields: <field>:<type>:<required?> … | source: <INT-###> |
                     referenced_by: <FR-###|BR-###>
  scenario_candidates: <one-line flow> | features: <slug> -> <slug> | this_feature_step: <N> |
                       source: <INT-###>
  design_principle_candidates: <preference> | source: <INT-###>
  blocked: <hub row #> — <why, in one line> (any row you could not process)
```

## Verifying the wave

After each wave, before starting the next, check the wave's own claims — do not re-draft anything.
This is cheap and catches the failure that matters: a subagent that reports success while its hub
write never landed leaves a signal that no future run will re-collect, because its Signal Log row
now reads `staged` with nothing staged anywhere.

For every feature in the wave:

1. Open each `FR-###`/`BR-###` the subagent reported creating or updating. Confirm the
   `## Discussion` entry exists and cites the `INT-###`.
2. Open the hub. Confirm every reported `staged` row shows `Status: staged` and a `Destination`
   matching the artifact, and that no row was renumbered or removed.
3. Confirm every reported question exists as an unchecked `- [ ] Q:` line on the artifact named.
4. Confirm the subagent wrote nothing to a shared register: `git diff --stat` (or a timestamp
   check) over `ENTITIES.md`, `SCENARIOS.md`, `DESIGN-PRINCIPLES.md`, `PAIN-POINTS.md`, and
   `_entities/` should show no change until Stage 4 runs.

A mismatch is blocking. Dispatch one small repair subagent scoped to exactly the gap — the same
model and type, told which artifact and which hub row disagree, and told to fix only that. Re-check
that one feature before moving on.

```text
Repair 01-Requirements/_features/<slug>.md ↔ 01-Requirements/_frs/FR-<NNN> <Title>.md.

The hub's Signal Log row #<n> says Status: staged, Destination: FR-<NNN>, but that FR's
## Discussion has no entry citing <INT-###>. The signal text is in the hub row.

Write the missing ## Discussion entry in the format _bigin/templates/fr.md
defines, citing <INT-###>. Do not re-route the signal, do not create a new FR, do not change
any Status. Report the entry you added.
```

## When not to fan out at all

A run whose entire worklist is one or two features with a handful of signals is faster and easier
to follow inline. Fan out when the run spans several features or a feature carries a large batch of
qualified signals — the point of the per-feature subagent is bounded context per feature, not
throughput for its own sake.
