---
name: bigin-transform-signal
description: This skill is used when after /extract-signal has filed signals, or when asked to derive use cases or requirements, write or update a UC, process the signal backlog, qualify signals, or check whether a feature's staged UC/BR changes have been answered. Transforms new/held signals from a Feature Hub into drafted/updated Use Cases (UC), Business Rules (BR), and Design Directives. Stages all UC/BR updates through a resumable human-review gate. It never promotes an Entity (EN) doc — it only cites the ENTITIES.md register; /approve-uc is the only skill that promotes one.
argument-hint: "[feature slug, or omit for all pending, or resume]"
---

# Bigin Transform Signal

Turn `new`/`held` signals on a Feature Hub's `## Signal Log` into **Use Cases** (UC), **Business Rules**
(BR), and **Design Directives**. Every UC/BR change passes a written, resumable human-review gate.

**The output is a use case, not a list of requirement fragments.** One `UC-###` is one user goal:
actors and trigger (`## 1`), the flow that delivers it (`## 2`), the branches that can happen instead
(`## 3`), a read-only mirror of the rules governing it (`## 4`), its open questions plus decision log
(`## 5`). A UC may span features, is updated in place as signals keep arriving, and is what a human
reviews and approves. `FR-###` is retired.

This skill is the **procedure**; `{conventions_reference}` is the **standard**. Read only its § Use
Case, § Feature Hub, § Status vocabularies, § Feedback handling, § Resumable unattended.

## Operating modes

| Mode | Behaviour |
|---|---|
| **Written gate** (default, unattended) | stage UC/BR proposals into `## Discussion` + a `- [ ] Q:` on the UC's `## 5` (a BR's `## Open Questions`). Never blocks on a human. **Two exceptions:** a Main Success Scenario step (`## 2`) or an Alternative/Exception Flow (`## 3`) write straight in, same run — Stage 4 Part 2, sweeping every in-scope UC's full `## Discussion` backlog, not just what this run staged. A `## 2` change also flags the UC for `/enrich-feature` + `/approve-uc` re-review. |
| **Interactive** | a question answered inline folds in immediately, no written round-trip. |
| **Design directives** | **not gated.** They never reach a UC, a PRD, or approval — they feed `/bigin-generate-design`, reviewed in its own right. Write them directly. |

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{conventions_reference}` | `_bigin/conventions/conventions.md` | ID scheme, § Use Case, frontmatter, status vocabularies |
| `{paths_reference}` | `_bigin/conventions/paths.md` | resolves every `{variable}` the stage files use — what a subagent reads instead of this table |
| `{stages_dir}` | `_bigin/stages/transform/` | `1-foldin`, `2-qualification`, `3-routing`, `3-lane-{uc,br,design}`, `4-sync`, `5-status` |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | the feature slug registry |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | one Feature Hub per slug |
| `{uc_dir}` | `01-Requirements/_ucs/UC-<NNN> <Title>.md` | **Use Cases** — the requirement artifact |
| `{br_dir}` | `01-Requirements/_brs/BR-<NNN> <Title>.md` | Business Rules, each its own file, `uc: []` citing what it governs |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | proposed entity register — this skill only ever reads/cites it, never writes it |
| `{entity_dir}` | `01-Requirements/_entities/EN-<NNN> <Entity>.md` | promoted entity specs — never written by this skill; `/approve-uc` promotes |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | durable cross-cutting design register |
| `{inbox_dir}` | `00-Inbox/INT-<NNN>.md` | read frontmatter, `## Extracted signals`, `## Open Questions` **only** — never `## Raw` |
| `{template_*}` | `_bigin/templates/*` | `use-case`, `br` |

Retired, read-only: `{fr_dir}` (`_frs/`), `{scenarios_file}` (`SCENARIOS.md`). Ids resolve; nothing
writes. A feature still carrying FRs gets them adopted into a UC on first touch
(`3-lane-uc.md` § Adopting an existing FR).

Missing `_bigin/conventions/`, `_bigin/stages/`, or `_bigin/templates/` → stop, say
`/bigin-new-project` must run first. A subagent that can't read `3-lane-uc.md` still writes a UC, just
one following no rule.

## Execution order

```text
scope = $ARGUMENTS slug, else every {hub_dir} file
        a UC spanning features is in scope when ANY of its slugs is

1  foldin    apply every staged UC/BR change whose question is now answered   [1-foldin.md]
2  qualify   build the worklist, gate each signal                            [2-qualification.md]
3  route     send each qualified signal down its lane                        [3-routing.md → 3-lane-*.md]
4  sync      shared registers + cross-feature UC changes, draft § 2/§ 3, flag,
             conflict-check                                                 [4-sync.md]
5  status    set every status from a live re-count, verify, report            [5-status.md]
```

Run all five in order, every invocation. **Stage 1 first is what makes a rerun useful** — it harvests
answers written since the last run before anything new gets staged.

**Load a stage file when you reach that stage, not up front** — and of the four `3-lane-*.md` guides,
only the lanes this run's signals actually hit.

## Stage 1 — Fold-in

```text
scan {uc_dir} + {br_dir} for artifacts whose feature has a `staged` Signal Log row pointing at them
per artifact → three-way read: unanswered | already applied | apply now       [1-foldin.md]
```

- **Reconcile mirrors unconditionally, every run** — including artifacts already applied, and
  **every** hub a cross-feature UC names. Re-setting a correct field is a no-op; skipping it leaves a
  hub reading `staged` against a folded-in UC forever.
- **Never renumber a step.** A new step takes the next unused `S#` in flow order; a removed step keeps
  its row and id, marked removed. Rules, branches, stories, and prototypes all cite these ids.

## Stage 2 — Qualify

```text
worklist = every Signal Log row with Status: new or held      # re-check `held` every run —
                                                              # what blocked it may now be resolved
empty → say so, stop
each row passes four gates, in order, stopping at the first failure:
    1 blocked-on-answer · 2 source-materialized · 3 fidelity · 4 dedup        [2-qualification.md]
```

- **Detect source problems; never fix them.** A signal whose note awaits an answer, whose attachment
  was never pulled, or whose thread has no reply is parked `held` with the remedy named. Extraction
  owns raw material — a transform-side pull produces a richer note that nothing re-extracts.
- **Never invent a Signal Log status.** Fixed: `new · held · staged · applied · question · conflict ·
  superseded · rejected`. A redundant signal is `applied` with a pointer, never `removed` (a UC/BR
  status, human-gated) or `duplicated` (doesn't exist).

## Stage 3 — Route and draft

```text
per qualified signal → exactly one lane, per clause not per row              [3-routing.md]
```

| Lane | Produces | Guide |
|---|---|---|
| UC | new/updated `UC-###` — steps, flows, `## 1` metadata, `## 4` mirror — staged into `## Discussion` | `3-lane-uc.md` |
| BR | new/updated `BR-###`, its own file, `uc: []` citing what it governs | `3-lane-br.md` |
| Design | a `{design_principles_file}` row, or a hub `## Design Directives` row | `3-lane-design.md` |
| Entity | a citation onto `{entities_file}`'s existing `proposed` row — never promoted here | `3-routing.md` § Entity |
| Context | the UC's `## 1` Business Need / Goal, or a `PP-###` on its `pain_points:` | `3-lane-uc.md` |

One lookup happens **inside** the Design lane, not at routing: **durable vs. feature-scoped**.
**Which UC, new or update** (most signals are a step, branch, or rule in a workflow that already
exists) is resolved by its own subagent, `uc-detector`, before any lane drafts — see below.

```text
FAN OUT ONE SUBAGENT PER FEATURE SLUG, never per lane                        [references/agent-dispatch.md]
    → a feature's hub + UC/BR files are one ownership domain; two lanes routinely touch the same UC
    → features are independent and parallelize safely; within a feature, process sequentially

within a feature, two subagents run in sequence, never merged:
  3a  uc-detector       resolves every UC/Context-lane signal to a UC-### — new or existing — reading
                        other features' hubs when a signal sounds cross-feature. Mints a new UC's
                        empty skeleton (frontmatter + hub pointer only); never stages content.
                        [agent-dispatch.md § 3a]
  3b  drafting subagent stages content into every lane, using 3a's resolved UC targets AS GIVEN — it
                        never re-decides which UC a signal belongs to, and never mints one itself.
                        [agent-dispatch.md § 3b]

a subagent NEVER writes:  {design_principles_file}                                    # vault-wide
                          a UC-### owned by another feature's primary_feature
                          another feature's hub · anything under {inbox_dir}
                          {entities_file} · {entity_dir}   # nobody writes these in this skill, not
                                                            # even Stage 4 — /approve-uc promotes,
                                                            # never here
    → it REPORTS design-principle candidates, cross_feature_uc_change items
    → Stage 4 applies them sequentially
a subagent DOES write:    its own feature's hub, its own UCs, its BRs
```

## Stage 4 — Sync, draft § 2/§ 3, and conflict-check

```text
orchestrator, sequential, after every Stage 3 subagent has reported          [4-sync.md]
    write shared registers + every cross-feature UC change, ONE AT A TIME
    write each participating hub's ## Use Cases pointer
    spawn one subagent per UC carrying an unapplied ## 2 or ## 3 entry — found by reading every
        in-scope UC's own ## Discussion directly, not just what Stage 3 reported this run —
        it pulls every requirement fact tied to that UC (the full ## Discussion, the cited hub
        Signal Log rows, the UC's own current sections) and writes ## 2 and/or ## 3 directly,
        same run (the two exceptions to the gate)
    flag any UC whose ## 2 changed this pass for /enrich-feature + /approve-uc re-review
    conflict-check each touched feature, scoped to that feature
```

A cross-feature UC change is **staged, not applied** — it is UC content, so it passes the same gate.
No entity is ever promoted here — that's `/approve-uc`'s job, at the approval gate (§ Entity Data
Model). Never auto-resolve a contradiction: raise it, name both sides, stop.

**Only `## 2` and `## 3` skip the gate.** A rule, `## 1`, `## 5`, or `## 6` always stages in
`## Discussion` and waits for Stage 1 on a later run, same as before — see `4-sync.md` § Part 2 for
exactly what qualifies, how short to write it, and when a `## 2` change must flag the UC for review.
The sweep is **cumulative, not scoped to this run** — a UC nobody's Stage 3 touched today can still
carry an entry an earlier run staged and never applied; Part 2 reads every in-scope UC's own
`## Discussion` fresh, every invocation, so a missed pass self-heals on the next run instead of
leaving `## 2`/`## 3` empty indefinitely.

## Stage 5 — Status and report

```text
orchestrator, last                                                           [5-status.md]
    set EVERY status from a LIVE RE-COUNT — never from what the run intended
        on a UC, count the ## 5 Still open list only; a decision-log row is answered history
    run the seven verification checks
    mismatch → BLOCKING: repair, re-check, then report
```

```text
Stage 1 (fold-in): <N> UC/BR resolved — <slug>: UC-### now draft, ready for /enrich-feature
Stage 2 (qualify): <N> qualified, <N> held (<reason>), <N> applied as duplicate/already-covered
Stage 3 (draft):   <N> UC created, <N> updated, <N> BR created, <N> BR updated
                   — <slug>: UC-### (staged, needs-clarification | staged, draft)
                   steps staged: <slug> UC-### — <N> new, <N> changed, <N> flow(s)
                   design: <N> directive(s) — <slug> ## Design Directives, <N> DESIGN-PRINCIPLES row(s)
Stage 4 (sync):    <N> cross-feature UC change(s),
                   <N> UC(s) with § 2/§ 3 drafted, <N> flagged for review, <N> conflict(s) — or none
cross-feature:     UC-### spans <slug> · <slug> — pointers written on both
remaining:         <slug>: UC-###/BR-### — N open question(s), owner client|team
next:              <slug> ready for /enrich-feature | <slug> ready for /bigin-generate-design (design-only)
```

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Drafting from an unqualified signal** — a flow built on an incomplete source reaches `/approve-uc`
  looking identical to a sound one.
- **Skipping `uc-detector`, or re-deciding new-vs-update inside the drafting subagent anyway** — the
  whole reason the lookup got its own step is that a busy drafting pass under-reads a cross-feature
  hub and either mints a duplicate UC or drafts into the wrong one.
- **Stretching the § 2/§ 3 direct-write exception to § 1/§ 4/§ 5/§ 6** — only a new/changed/removed
  main-flow step or flow skips the human-review wait (Stage 4 Part 2); a rule, `## 1` metadata, an
  open question, or a special requirement still stages in `## Discussion` and waits for Stage 1.
- **Scoping Stage 4 Part 2 to only this run's Stage 3 output** — a UC nobody's Stage 3 touched this
  run can still carry an old, unapplied § 2/§ 3 entry from a run whose Stage 4 skipped it. Part 2
  must read every in-scope UC's own `## Discussion` fresh, every invocation, or the gap is permanent.
- **Writing § 2 without flagging the UC for review** — a main-flow change that doesn't visibly say a
  human should look again (a status revert, or at minimum a Changelog line) reads as reviewed content
  nobody was actually asked to check.
- **Inventing a step, validation, or branch nobody stated** — the cheapest way to launder a guess into
  approved scope, and a flow reads as complete once it has one. Missing → a question.
- **Renumbering steps** — every `S#` is cited from a rule, a branch, a story, or a prototype screen.
  Non-sequential ids are the design.
- **Minting a second UC for the same goal** — splits the review and drifts. New signals about an
  existing goal are updates.
- **Fixing a source problem instead of returning it** — the new material is lost while the note looks
  complete.
- **Writing a rule statement into a UC's `## 4`** — that table is a mirror; `BR-###` is the source, and
  the UC copy is the one reviewers trust.
- **Manufacturing a question** — each one adds a round-trip and parks an artifact that was ready.
- **Routing a behaviour change down the Design lane** — that lane skips the PRD and the approval gate,
  so it reaches a prototype never reviewed as scope.
- **Treating a repeated ask as noise** — a duplicate is `applied` with a pointer; the second mention is
  evidence of priority.
- **Writing a shared register, or another feature's UC, from a per-feature subagent** — two features
  `Grep` the same highest id and both mint the same new `UC-###` number, or two appends to
  `DESIGN-PRINCIPLES.md` race and one is lost.
- **Promoting an entity, or reporting one as a candidate to promote, from anywhere in this skill** —
  that lane doesn't exist any more. Cite `{entities_file}`'s `proposed` row by name; `/approve-uc`
  is the only place a `proposed` row becomes an `EN-###` doc.
- **Pointing only the primary hub at a cross-feature UC** — the other features read as uninvolved.
- **Deciding a conflict** — recency settles a supersession, never a disagreement.
- **Setting status early** — this vault's most common drift. Re-count and set it last, every time.

## Model

Both Stage 3 subagents (`uc-detector` and the drafting subagent) run on the **session default model**,
not `haiku`: this is judgment-heavy work — which UC a signal belongs to, where a step sits in a flow,
spotting a cross-feature goal. Contrast `/extract-signal`, mechanical against a tight rule set.

Deep fidelity checking belongs to **`/extract-signal`'s source audit**, next to the raw material where
a quote-anchored check is cheap. This skill does the shallow half only (Stage 2, Gate 3).

## Additional resources

- **`references/agent-dispatch.md`** — the `uc-detector` prompt (§ 3a), the drafting subagent prompt
  (§ 3b) and its report contract, and the wave-verification checklist.
- **`references/use-case-standard.md`** — where the UC artifact's shape comes from (Cockburn, BABOK,
  Use-Case 2.0, Wiegers), what is established practice and what is a deliberate departure. Read before
  changing the template or a lane guide; not needed for a run.
