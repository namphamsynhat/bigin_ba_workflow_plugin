# Subagent dispatch — two per feature, in sequence

```text
Agent(uc-detector, foreground)        # 3a — resolves every UC target (read-only; proposes new ids)
   ORCHESTRATOR MINTS                 # between the waves — § Minting new UCs, below
Agent(uc-drafter, foreground)         # 3b — drafts the staged content
one PAIR per FEATURE SLUG, never per lane
    → a feature's hub + UC/BR files are one ownership domain that two lanes routinely both touch
    → features are independent, so they parallelize safely
≤ 4 features concurrently, report between waves        # a failure costs one wave, not the backlog
within a feature → 3a runs to completion before 3b starts; signals then processed sequentially
```

**Each agent pins its own model in its frontmatter** (`agents/uc-detector.md`, `agents/uc-drafter.md`,
`agents/uc-applier.md`) — don't restate or override a tier from a dispatch prompt. The rationale for
each tier is in `SKILL.md § Model`; the tier itself lives in exactly one place, the agent file.

**Skip both subagents entirely when a feature has three or fewer qualified signals** — dispatch overhead
exceeds the work. Two subagents each read the hub and its UCs in full, so a 3-signal dispatch pays a
duplicate ~100k-token hub read to save a few inline minutes; the orchestrator runs both lane guides
inline instead (still resolve the UC target first, per § 3a, before drafting). Fan out when the run spans
several features, or one feature carries a batch of four or more.

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
an existing one — before anything gets drafted into it. You are READ-ONLY: report a genuinely new goal
as `new (unminted)` with the frontmatter values it needs; the orchestrator mints the id and the
skeleton after you report. Never write any file, never stage step content, flows, rules, a business
need, or a question.

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
- 01-Requirements/_features/<slug>.md — READ IT TARGETED, not whole: its frontmatter (uc:, br:,
  features), its ## Use Cases table, and only the Signal Log rows this dispatch's signals cite.
  A hub's Signal Log is append-only and mostly irrelevant to a same-goal call; reading it in full
  costs more every month and tells you nothing the ## Use Cases table doesn't.
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
3. Different goal → new. Report it as `new (unminted)`. DO NOT Grep for the next id and DO NOT
   create the file: up to four features run concurrently and two concurrent scans return the same
   highest number, so two features would mint the same UC-### and one file would overwrite the
   other. The orchestrator mints, one at a time, from your report.
4. The goal's actor belongs to ANOTHER feature's hub → report it as owned elsewhere; never propose a
   UC on someone else's behalf.
5. A new UC you DO own: report the exact frontmatter it needs, so the orchestrator writes it without
   re-deriving anything — title (short active verb phrase), level (§ Granularity — user-goal unless
   grouping existing UCs or a shared step sequence), scope, primary_feature: <slug>, features (every
   stated slug, primary_feature first), sources, attachments (copied from the source note's own
   attachments:). status: draft, version: 1.0, owner: team, updated: today are fixed and need no
   reporting. ## 1–## 6 and the summary block stay EMPTY — no content, not even a Business Need.
6. A feature with FR-### files and no UC, touched for the first time: report it as a new UC per
   step 5 plus `absorbs: [FR-###, …]` listing every FR on this feature. Do not stage the FR lines
   yourself — report the adoption so 3b stages them.

YOU WRITE NOTHING AT ALL — not a UC, not a skeleton, not a hub pointer, not a status. Read any hub or
UC you need; edit none of them.

REPORT, per signal:
  <hub row #> -> UC-### (existing) | UC (new, unminted) | primary_feature: <slug> |
                 features: [<slug>, …] | goal: "<title>"
  (new only)   level: <level> | frontmatter: <the field values from step 5>
  (existing only) evidence: ## 2 | ## 3 (<A#/E#>) | ## Discussion (<the entry>) — whichever
                 section actually settled the same-goal call
  cross-feature reasoning: <hub(s) you read and what settled the call>, or "none needed"
adoptions:       <slug>: absorbs FR-###, … (or "none")
owned_elsewhere: <hub row #> -> belongs to <slug> (not written)
unresolved:      <hub row #> — <why you could not confidently place it>
```

## Minting new UCs, between 3a and 3b

**The orchestrator, sequentially, one id at a time**, for every `new (unminted)` a wave's detectors
reported — the same discipline `4-sync.md` § Part 1 already applies to cross-feature news, extended to
every new id because the hazard is identical.

```text
per `new (unminted)`, in report order, one completing before the next starts:
1  DEDUPE THE WAVE FIRST — two detectors in the same wave can report the same goal under different
   words (a cross-feature flow both features think they own). Same goal → ONE UC, primary_feature =
   the feature whose actor holds the goal; the other feature is a `features:` entry, not a second UC.
2  Grep {uc_dir} for the highest existing UC-### and increment. Use the Grep TOOL, never a Bash
   pipeline — a denied pipeline reads as "no matches" and silently reuses an id.
3  instantiate {template_uc} at {uc_dir}/UC-<NNN> <Title>.md with exactly the frontmatter the
   detector reported, ## 1-## 6 and the summary block empty
4  add the id to the owning hub's uc: list and a pointer row to its ## Use Cases
4b add the id to {requirements_file}'s UC column for the owning feature's row too — same write,
   same pass (conventions.md § Feature Map format). Skipping this is what lets FEATURES.md's UC
   column go stale relative to the hub's own uc: list/## Use Cases table, which is otherwise the
   only place that later gets read
5  record the mapping <hub row #> -> UC-<NNN> — that is what 3b is handed as a resolved target
```

Only then dispatch 3b for that feature.

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

## Verifying 3a and the mint, before 3b starts

A detector report is a set of claims, and 3b staging content into a UC that doesn't exist is the failure
this catches. Check after minting, before dispatching 3b for the same feature:

```text
per feature:
0  each minted UC → the file exists at {uc_dir}/UC-<NNN> <Title>.md with id/title/status: draft/
                   primary_feature/features set, ## 1-## 6 EMPTY, and a uc: + ## Use Cases pointer on
                   the owning hub — no other hub touched yet (Stage 4 Part 1b does the rest)
1  each "existing" UC → the id is actually on the hub's uc: list (or a cross-feature hub's, for a
                   goal owned elsewhere) and its ## 2/## 3/## Discussion genuinely matches the
                   same-goal call made, per the reported `evidence:` line — not just its title
2  no two signals resolved to `new (unminted)` for what reads as the same goal, ACROSS THE WHOLE
                   WAVE, not just within one feature — the § Minting dedupe step should have caught
                   it; this is the read-back
3  id uniqueness → `Grep '^id:' {uc_dir}` shows no duplicate UC-###, and every id matches its own
                   filename. The mint race's only real backstop
4  every owned_elsewhere / unresolved row has a real reason, not a placeholder

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
2  the hub            → every reported `staged` row shows Status: staged + a matching Destination,
                         and a themed row whose Type is `<a> + <b>` names a destination PER CLAUSE
                         (` · `-joined) — one destination on a two-clause row is a dropped clause
                         no row renumbered or removed
3  each question      → exists as an unchecked "- [ ] Q:" on the artifact named
                         (a UC's ## 5 Still open, a BR's ## Open Questions)
4  each touched UC    → NO S#/A#/E# renumbered or deleted, and nothing written into ## 1-## 6
                         — INCLUDING ## 1: a Context-lane Business Need stages into ## Discussion
                         like everything else (3-lane-uc.md § The Context sub-lane)
5  shared registers   → git diff --stat over DESIGN-PRINCIPLES.md, PAIN-POINTS.md, and any
                         other-owned UC-### shows NO change until Stage 4; over ENTITIES.md and
                         _entities/ shows NO change at all — this skill never writes either
6  coverage           → every row in the dispatch worklist appears somewhere in the report — staged,
                         questioned, conflicted, or blocked. A row in neither is UNACCOUNTED, and a
                         partial pass reports the same shape as a complete one

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
