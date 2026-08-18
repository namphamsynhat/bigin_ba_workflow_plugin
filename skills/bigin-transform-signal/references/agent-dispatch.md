# Subagent dispatch — two per feature, in sequence

```text
Agent(session default model, uc-detector, foreground)        # 3a — resolves every UC target
Agent(session default model, uc-drafter, foreground)         # 3b — drafts, not haiku — judgment work
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
- every UC that list names, in full — title, ## 1, ## 2 (Main Success Scenario — the happy path
  only, no branches), ## 3 (every Alternative & Exception Flow), and ## Discussion (proposals
  already staged but not yet folded into ## 2/## 3 — they're part of the flow's real, current
  shape even though unapplied). Not just the title, and not just ## 2.

THEN, per signal, in hub row order:
1. Read it on its own content — never by adjacency to the row before it, never by phrasing
   ("we also need…" is not evidence of a new goal).
2. Same actor sitting down to accomplish the same thing as an existing UC, AT ANY STATUS → that
   UC, update. A new step, branch, validation, or rule are all updates, never a second UC. A
   signal that reads as a branch off an existing ## 2 or ## 3, or that matches a proposal already
   sitting in ## Discussion, IS the same goal — never rule "different goal" from the title or
   ## 2 alone; check ## 3 and ## Discussion first.
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
  (existing only) evidence: ## 2 | ## 3 (<A#/E#>) | ## Discussion (<the entry>) — whichever
                 section actually settled the same-goal call
  cross-feature reasoning: <hub(s) you read and what settled the call>, or "none needed"
adoptions:       <slug>: absorbs FR-###, … (or "none")
owned_elsewhere: <hub row #> -> belongs to <slug> (not written)
unresolved:      <hub row #> — <why you could not confidently place it>
```

Give the orchestrator's repair pass a hook: a `uc-detector` report claiming a new UC is not trustworthy
until the wave check below confirms the file actually landed with the hub pointer set.

## 3b — Drafting (`uc-drafter`)

Runs after `uc-detector` reports for the same feature. The subagent has no memory of this
conversation, including `uc-detector`'s run — hand it the resolved targets as data, not a pointer to
re-derive. Its rulebook (which conventions/lane-guide sections to read, the DO-NOT-WRITE list, the
report format) is baked into `agents/uc-drafter.md` — this dispatch only needs to supply the
per-run facts that agent has no way to already know:

```text
Draft the requirement artifacts for feature <slug> from its already-qualified signals.

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

01-Requirements/_features/<slug>.md is the hub. Every UC/BR in its uc: / br: frontmatter is fair
game to read in full before drafting.
```

Report format is fixed in `agents/uc-drafter.md` § Report — do not restate it in the dispatch prompt.

## Verifying 3a, before 3b starts

`uc-detector`'s report is not trustworthy on its own — a claimed skeleton that never landed leaves 3b
staging content into a UC that doesn't exist. Check before dispatching 3b for the same feature:

```text
per feature:
0  each "new" UC → the file exists at the reported path, with id/title/status: draft/primary_feature/
                   features set, ## 1-## 6 EMPTY, and a uc: + ## Use Cases pointer on the dispatched
                   feature's own hub — no other hub touched
1  each "existing" UC → the id is actually on the hub's uc: list (or a cross-feature hub's, for a
                   goal owned elsewhere) and its ## 2/## 3/## Discussion genuinely matches the
                   same-goal call made, per the reported `evidence:` line — not just its title
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
5  shared registers   → git diff --stat over DESIGN-PRINCIPLES.md, PAIN-POINTS.md, and any
                         other-owned UC-### shows NO change until Stage 4; over ENTITIES.md and
                         _entities/ shows NO change at all — this skill never writes either

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
