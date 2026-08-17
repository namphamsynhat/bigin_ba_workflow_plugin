# Subagent dispatch — two per feature, in sequence

```text
Agent(session default model, uc-detector, foreground)        # 3a — resolves every UC target
Agent(session default model, general-purpose, foreground)    # 3b — drafts, not haiku — judgment work
one PAIR per FEATURE SLUG, never per lane
    → a feature's hub + UC/BR files are one ownership domain that two lanes routinely both touch
    → features are independent, so they parallelize safely
≤ 4 features concurrently, report between waves        # a failure costs one wave, not the backlog
within a feature → 3a runs to completion before 3b starts; signals then processed sequentially
```

**Skip both subagents entirely when a feature has one or two qualified signals** — dispatch overhead
exceeds the work, and the orchestrator can run both lane guides inline (still resolve the UC target
first, per § 3a, before drafting). Fan out when the run spans several features, or one feature carries
a large batch.

An **FR adoption** run (`3-lane-uc.md` § Adopting an existing FR) is worth running inline even for one
feature: it produces the largest diff of any single run.

## Before dispatching — resolve UC ownership

A `UC-###` is written only by its `primary_feature`'s subagent. So dispatch must already know **which
feature owns each UC** before either wave starts, or two waves write the same file.

```text
signal targets a UC owned by the feature being dispatched → include it in that worklist
signal targets a UC owned by a DIFFERENT feature          → NOT a write in either worklist
                                                             hand it to the owning feature's subagent
                                                             if that feature is in this run
                                                             else → cross_feature_uc_change for Stage 4
signal needs a NEW UC whose goal belongs to another actor → same: Stage 4 mints it
```

**Which specific `UC-###` a signal targets** (new vs. an id already on the hub) is `uc-detector`'s job,
not something the orchestrator or the drafting subagent decides — see § 3a.

## 3a — UC identification (`uc-detector`)

Runs first, per feature, over that feature's UC- and Context-lane signals only. Never touches BR,
Design, or Entity signals — those still resolve entirely inside 3b.

The subagent has no memory of this conversation. Give it the cheap known facts and point it at real
files — a paraphrase risks it trusting a stale summary over the source of truth.

```text
Identify the UC each of feature <slug>'s qualified UC/Context-lane signals belongs to — a new UC or
an existing one — before anything gets drafted into it. Mint a new UC's empty skeleton only; never
stage step content, flows, rules, a business need, or a question.

QUALIFIED SIGNALS ROUTED TO UC OR CONTEXT (hub row # → lane), decided in Stage 2/3 — do not
re-qualify or re-route:
<row #>: <signal text> | lane: UC|context
<...>

Hubs that plausibly share a workflow with this feature — read their uc: list and UC content before
deciding any signal that sounds cross-feature, even if it isn't in this list:
<candidate slugs, or "none flagged">

READ FIRST:
- _bigin/conventions/paths.md — resolves {uc_dir}, {template_uc}, and every other variable below
- _bigin/stages/transform/3-routing.md § Which UC — new or update
- _bigin/stages/transform/3-lane-uc.md § Ownership, § Granularity, § Creating a new UC,
  § Adopting an existing FR
- _bigin/conventions/conventions.md § Use Case, § ID scheme, § Frontmatter schema — nothing else
- 01-Requirements/_features/<slug>.md — the hub, its uc: list and ## Use Cases
- every UC that list names, in full — title, ## 1, and the flow, not just the title

THEN, per signal, in hub row order:
1. Read it on its own content — never by adjacency to the row before it, never by phrasing
   ("we also need…" is not evidence of a new goal).
2. Same actor sitting down to accomplish the same thing as an existing UC, AT ANY STATUS → that
   UC, update. A new step, branch, validation, or rule are all updates, never a second UC.
3. Different goal → new. Mint the next id with the Grep TOOL over {uc_dir} for the highest number
   — never a Bash pipeline; a denied pipeline silently reuses an id.
4. The goal's actor belongs to ANOTHER feature's hub → do not mint it here. Report it as owned
   elsewhere; never mint a UC on someone else's behalf.
5. A new UC you DO own: instantiate {template_uc}, fill ONLY id, title (short active verb phrase),
   status: draft, version: 1.0, level (§ Granularity — user-goal unless grouping existing UCs or a
   shared step sequence), scope, primary_feature: <slug>, features (every stated slug, primary_feature
   first), sources, attachments (copied from the source note's own attachments:), owner: team,
   updated: today. Leave links/brs/entities/pain_points/absorbs empty. Leave the summary block and
   ## 1–## 6 EMPTY — no content, not even a Business Need. Add the id to the hub's uc: list and a
   pointer row to its ## Use Cases.
6. A feature with FR-### files and no UC, touched for the first time: create the UC as in step 5
   with absorbs: [FR-###, …] listing every FR on this feature. Do not stage the FR lines yourself —
   report the adoption so 3b stages them.

DO NOT touch another feature's hub — read it freely, write nothing there. DO NOT write into
## 1–## 6, ## Discussion, or ## 5 Still open on any UC. DO NOT renumber, reuse, or delete a UC id.
DO NOT set any status but draft on a UC you mint.

REPORT, per signal:
  <hub row #> -> UC-### (new|existing) | primary_feature: <slug> | features: [<slug>, …] |
                 goal: "<title>"
  (new only)   level: <level> | skeleton written: <path>
  cross-feature reasoning: <hub(s) you read and what settled the call>, or "none needed"
adoptions:       <slug>: absorbs FR-###, … (or "none")
owned_elsewhere: <hub row #> -> belongs to <slug> (not written)
unresolved:      <hub row #> — <why you could not confidently place it>
```

Give the orchestrator's repair pass a hook: a `uc-detector` report claiming a new UC is not trustworthy
until the wave check below confirms the file actually landed with the hub pointer set.

## 3b — Drafting

Runs after `uc-detector` reports for the same feature. The subagent has no memory of this
conversation, including `uc-detector`'s run — hand it the resolved targets as data, not a pointer to
re-derive.

```text
Draft the requirement artifacts for feature <slug> from its already-qualified signals.

The requirement artifact is a USE CASE (UC-###): one user goal, with its actors and trigger (§ 1),
its main flow as a step table (§ 2), its alternative/exception flows (§ 3), a read-only mirror of
the business rules governing it (§ 4), and its open questions plus decision log (§ 5). FR-### is
retired. Steps carry permanent S# ids — never renumber, reuse, or delete one.

QUALIFIED SIGNALS (hub row # → lane), decided in Stage 2/3 — do not re-qualify or re-route:
<row #>: <signal text> | lane: UC|BR|design|entity|context | target: <UC-### | BR-### | new>
<...>

UC TARGETS — resolved by uc-detector for every UC/context-lane row above. Use them AS GIVEN: do NOT
re-decide which UC a signal belongs to, and do NOT mint a new UC id or file yourself, even if one
looks missing — report it as blocked instead, so the orchestrator can re-run 3a rather than two
subagents minting the same goal twice:
<row #>: target UC-### (new — skeleton already written | existing)
<...>

UCs you MAY write (this feature is their primary_feature): <UC-### …, or "none yet">
UCs you must NOT write (owned by another feature):        <UC-### (owner: <slug>) …, or "none">

READ FIRST:
- _bigin/conventions/conventions.md — these sections ONLY, not the whole file: § ID scheme,
  § Use Case, § Frontmatter schema, § Status vocabularies, § Feature Hub, § Open Questions
  wording, § Open Questions ↔ status consistency, § Feedback handling. Add § Entity Data Model
  only if this run has an entity candidate.
- _bigin/conventions/paths.md — resolves {uc_dir}, {br_dir}, {entity_dir}, {template_br}, and
  every other variable the lane guides refer to
- _bigin/stages/transform/3-lane-<x>.md for ONLY the lanes listed above — not all four. Skip
  3-lane-uc.md § Creating a new UC and § Adopting an existing FR — uc-detector already did that;
  read the rest (Staging a change, Writing a step, alternative/exception flows, the § 4 mirror, the
  Context sub-lane, Questions, Conflict)
- 01-Requirements/_features/<slug>.md — the hub
- every UC/BR in that hub's uc: / br: frontmatter, in full

THEN, one signal at a time, in hub row order:
1. For a UC/Context-lane signal, stage into the UC TARGET given above — never a different UC, never
   a new one. For BR/design/entity, follow that lane's guide exactly. Stage UC/BR content into
   ## Discussion, naming its destination ("new step after S4:", "S6 becomes:", "new flow E2:",
   "§ 1 Trigger becomes:", "§ 4: add BR-###, enforced at S5") as FINAL TEXT — never write into
   § 1-§ 6 or a BR's rule statement yourself. A "new step"/"S# becomes"/"new flow"/"A#/E# becomes"
   destination is applied same-run by Stage 4 Part 2; everything else is the fold-in stage's job on
   a later run.
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
DO NOT write to 01-Requirements/_frs/ or SCENARIOS.md — both retired. An FR adoption's skeleton and
absorbs: are already written by uc-detector; stage the FR's existing lines as proposed steps, then
stamp each FR absorbed_by: and change nothing else.
DO NOT set status: approved, removed, enriched, consolidated, in-review, or superseded. Leave
every UC/BR at draft — the orchestrator sets the final status from a live count in Stage 5.

REPORT, as plain lines:
  feature: <slug>
  uc: <UC-### staged|unchanged> (one line each, with its goal title — creation itself is uc-detector's)
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
  blocked: <hub row #> — <why, in one line> (any row you could not process, including a missing
           or contradictory UC target from 3a)
```

## Verifying 3a, before 3b starts

`uc-detector`'s report is not trustworthy on its own — a claimed skeleton that never landed leaves 3b
staging content into a UC that doesn't exist. Check before dispatching 3b for the same feature:

```text
per feature:
0  each "new" UC → the file exists at the reported path, with id/title/status: draft/primary_feature/
                   features set, ## 1-## 6 EMPTY, and a uc: + ## Use Cases pointer on the dispatched
                   feature's own hub — no other hub touched
1  each "existing" UC → the id is actually on the hub's uc: list (or a cross-feature hub's, for a
                   goal owned elsewhere) and its title/flow genuinely matches the same-goal call made
2  no two signals in the report resolved to the "new" case for what reads as the same goal — that's
                   two skeletons about to receive the same content from 3b
3  every owned_elsewhere / unresolved row has a real reason, not a placeholder

mismatch → BLOCKING. Re-run 3a (or a scoped repair) before 3b touches this feature.
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
