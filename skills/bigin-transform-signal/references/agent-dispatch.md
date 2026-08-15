# Subagent dispatch — one per feature

```text
Agent(session default model, general-purpose, foreground)   # not haiku — this is judgment work
one per FEATURE SLUG, never per lane
    → a feature's hub + UC/BR files are one ownership domain that two lanes routinely both touch
    → features are independent, so they parallelize safely
≤ 4 features concurrently, report between waves        # a failure costs one wave, not the backlog
within a feature → signals processed sequentially
```

**Skip the subagent entirely when a feature has one or two qualified signals** — dispatch overhead
exceeds the work, and the orchestrator can run the lane guide inline. Fan out when the run spans
several features, or one feature carries a large batch.

An **FR adoption** run (`3-lane-uc.md` § Adopting an existing FR) is worth running inline even for one
feature: it produces the largest diff of any single run.

## Before dispatching — resolve UC ownership

A `UC-###` is written only by its `primary_feature`'s subagent. So routing must already know **which
UC** each signal targets and **which feature owns it**, or two waves write the same file.

```text
signal targets a UC owned by the feature being dispatched → include it in that worklist
signal targets a UC owned by a DIFFERENT feature          → NOT a write in either worklist
                                                             hand it to the owning feature's subagent
                                                             if that feature is in this run
                                                             else → cross_feature_uc_change for Stage 4
signal needs a NEW UC whose goal belongs to another actor → same: Stage 4 mints it
```

## The prompt

The subagent has no memory of this conversation. Give it the cheap known facts and point it at real
files — a paraphrase risks it trusting a stale summary over the source of truth.

```text
Draft the requirement artifacts for feature <slug> from its already-qualified signals.

The requirement artifact is a USE CASE (UC-###): one user goal, with its actors and trigger (§ 1),
its main flow as a step table (§ 2), its alternative/exception flows (§ 3), a read-only mirror of
the business rules governing it (§ 4), and its open questions plus decision log (§ 5). FR-### is
retired. Steps carry permanent S# ids — never renumber, reuse, or delete one.

QUALIFIED SIGNALS (hub row # → lane), decided in Stage 2/3 — do not re-qualify or re-route:
<row #>: <signal text> | lane: UC|BR|design|entity|context | target: <UC-### | BR-### | new>
<...>

UCs you MAY write (this feature is their primary_feature): <UC-### …, or "none yet">
UCs you must NOT write (owned by another feature):        <UC-### (owner: <slug>) …, or "none">

READ FIRST:
- _bigin/conventions/conventions.md — these sections ONLY, not the whole file: § ID scheme,
  § Use Case, § Frontmatter schema, § Status vocabularies, § Feature Hub, § Open Questions
  wording, § Open Questions ↔ status consistency, § Feedback handling. Add § Entity Data Model
  only if this run has an entity candidate.
- _bigin/conventions/paths.md — resolves {uc_dir}, {br_dir}, {entity_dir}, {template_uc},
  {template_br}, and every other variable the lane guides refer to
- _bigin/stages/transform/3-lane-<x>.md for ONLY the lanes listed above — not all four — plus
  3-routing.md § Which UC — new or update if any row says "new"
- 01-Requirements/_features/<slug>.md — the hub
- every UC/BR in that hub's uc: / br: frontmatter, in full

THEN, one signal at a time, in hub row order:
1. Follow that signal's lane guide exactly. Stage UC/BR content into ## Discussion, naming its
   destination ("new step after S4:", "S6 becomes:", "new flow E2:", "§ 1 Trigger becomes:",
   "§ 4: add BR-###, enforced at S5") as FINAL TEXT — never write into § 1-§ 6 or a BR's rule
   statement, which is the fold-in stage's job on a later run.
2. Update the hub's Signal Log row: Status and Destination per 3-routing.md § Recording the
   routing decision. Never renumber or delete a row.
3. Raise a question ONLY when a decision is genuinely needed (3-lane-uc.md § Questions), on the
   UC's § 5 Still open list. Never copy a question that already exists on the source INT note.
4. NEVER invent a step, validation, threshold, notification, or branch the signal didn't state.
   Missing detail is a question, not a plausible guess.

DO NOT WRITE — vault-wide or owned elsewhere, and other features run concurrently. Report
candidates instead; the orchestrator applies them in Stage 4:
  01-Requirements/ENTITIES.md · 01-Requirements/_entities/ · DESIGN-PRINCIPLES.md
  01-Requirements/FEATURES.md · PAIN-POINTS.md · any UC-### listed above as owned elsewhere
DO NOT touch another feature's hub, or any file under 00-Inbox/.
DO NOT write to 01-Requirements/_frs/ or SCENARIOS.md — both retired. If this feature has FR-###
files and no UC yet, follow 3-lane-uc.md § Adopting an existing FR: mint the UC with absorbs:,
stage the FR's existing lines as proposed steps, stamp each FR absorbed_by:, change nothing else.
DO NOT set status: approved, removed, enriched, consolidated, in-review, or superseded. Leave
every UC/BR at draft — the orchestrator sets the final status from a live count in Stage 5.

REPORT, as plain lines:
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

After each wave, before the next. Check the wave's own claims — do not re-draft anything. This catches
the failure that matters: a subagent reporting success while its hub write never landed leaves a
signal no future run re-collects, because its row now reads `staged` with nothing staged anywhere.

```text
per feature in the wave:
1  each reported UC/BR → ## Discussion entry exists, cites the INT-###, names a destination
                         as FINAL TEXT rather than an instruction
2  the hub            → every reported `staged` row shows Status: staged + a matching Destination
                         no row renumbered or removed
3  each question      → exists as an unchecked "- [ ] Q:" on the artifact named
                         (a UC's ## 5 Still open, a BR's ## Open Questions)
4  each touched UC    → NO S#/A#/E# renumbered or deleted, and nothing written into ## 1-## 6
                         (the gate lives in ## Discussion)
5  shared registers   → git diff --stat over ENTITIES.md, DESIGN-PRINCIPLES.md, PAIN-POINTS.md,
                         _entities/, and any other-owned UC-### shows NO change until Stage 4

mismatch → BLOCKING. Dispatch one scoped repair subagent, re-check that feature, then move on.
```

```text
Repair 01-Requirements/_features/<slug>.md ↔ 01-Requirements/_ucs/UC-<NNN> <Title>.md.

The hub's Signal Log row #<n> says Status: staged, Destination: UC-<NNN>, but that UC's
## Discussion has no entry citing <INT-###>. The signal text is in the hub row.

Write the missing ## Discussion entry in the format _bigin/templates/use-case.md defines,
citing <INT-###> and naming its destination as final text. Do not re-route the signal, do not
create a new UC, do not write into § 1-§ 6, do not renumber any step id, and do not change any
Status. Report the entry you added.
```
