---
name: bigin-transform-signal
description: This skill is used when after /extract-signal has filed signals, or when asked to derive use cases or requirements, write or update a UC, process the signal backlog, qualify signals, or check whether a feature's staged UC/BR changes have been answered. Transforms new/held signals from a Feature Hub into drafted/updated Use Cases (UC), Business Rules (BR), and Design Directives. Stages every UC/BR update as final text in the artifact's `## Discussion` first, with a written question when a decision is genuinely needed — resumable, never blocking on a live human. It never promotes an Entity (EN) doc — it only cites the ENTITIES.md register; /sync-entities is the only skill that promotes one.
argument-hint: "[feature slug, or omit for all pending, or resume]"
---

# Bigin Transform Signal

Turn `new`/`held` signals on a Feature Hub's `## Signal Log` into **Use Cases** (UC), **Business Rules**
(BR), and **Design Directives**. Every UC/BR change is **staged as final text first** — written into the
artifact's `## Discussion` naming exactly where it goes, resumably, never blocking on a live human. What
that does and does not guarantee is § Operating modes' first job to state precisely.

**The output is a use case, not a list of requirement fragments.** One `UC-###` is one user goal:
actors and trigger (`## 1`), the flow that delivers it (`## 2`), the branches that can happen instead
(`## 3`), a read-only mirror of the rules governing it (`## 4`), its open questions plus decision log
(`## 5`). A UC may span features, is updated in place as signals keep arriving, and is what a human
reviews and approves. `FR-###` is retired.

This skill is the **procedure**; `{conventions_reference}` is the **standard**. Read only its § Use
Case, § Feature Hub, § Status vocabularies, § Feedback handling, § Resumable unattended.

## Operating modes

This skill is **always unattended**. There is one mode, and it never blocks on a human.

| Content | Behaviour |
|---|---|
| **UC/BR content** | staged into `## Discussion` as final text, plus a `- [ ] Q:` on the UC's `## 5` (a BR's `## Open Questions`) **when a decision is genuinely needed**. **Two exceptions:** a Main Success Scenario step (`## 2`) or an Alternative/Exception Flow (`## 3`) writes straight in, same run — Stage 4 Part 2, sweeping every in-scope UC's full `## Discussion` backlog, not just what this run staged. A `## 2` change also flags the UC for `/approve-uc` re-review. |
| **Design directives** | **not gated.** They never reach a UC, a PRD, or approval — they feed `/bigin-generate-design`, reviewed in its own right. Write them directly. |

**What "the gate" actually is, precisely.** It is a **wait for an answer, not a wait for a review.** An
entry staged *with* a question waits until a human fills that question's `A:`. An entry staged *without*
one is folded in by the next run's Stage 1 (or, for `## 2`/`## 3`, by this same run's Stage 4 Part 2) with
no human having looked at it. So:

```text
staged + a question   → genuinely gated: nothing lands until a human answers
staged, no question    → a ONE-RUN delay at most, then it lands unreviewed
## 2 / ## 3 entry      → lands THIS run, and only the review flag says a human should look
```

That is the design — an unambiguous statement should not need a human round-trip — but do not describe
it, or rely on it, as "every change is human-reviewed before it lands." The thing that makes an
unreviewed change *visible* is the review flag and the Changelog line, read at `/approve-uc`, not the
staging step. There is no interactive mode: nothing in this skill asks a live question, and nothing
folds a change in on the strength of one answered mid-run.

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
| `{entity_dir}` | `01-Requirements/_entities/EN-<NNN> <Entity>.md` | promoted entity specs — never written by this skill; `/sync-entities` promotes |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | durable cross-cutting design register |
| `{inbox_dir}` | `00-Inbox/INT-<NNN>.md` | read frontmatter, `## Extracted signals`, `## Open Questions` **only** — never `## Raw` |
| `{template_*}` | `_bigin/templates/*` | `use-case`, `br` |

Retired, read-only: `{fr_dir}` (`_frs/`), `{scenarios_file}` (`SCENARIOS.md`). Ids resolve; nothing
writes. A feature still carrying FRs gets them adopted into a UC on first touch
(`3-lane-uc.md` § Adopting an existing FR).

Missing `_bigin/conventions/`, `_bigin/stages/`, or `_bigin/templates/` → stop, say
`/bigin-new-project` must run first. A subagent that can't read `3-lane-uc.md` still writes a UC, just
one following no rule.

Then run `{conventions_reference}` § Workspace version check — one `Grep` of `_bigin/system/project.md`
against the installed plugin's version. Behind → warn and recommend `/bigin-upgrade-project`; **ahead →
stop**, because the materialized rulebook this run would follow is older than the one the vault's content
was built against.

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
GREP-FIRST, never a vault read: Grep {hub_dir} for `Status.*staged`, and for
    `Status.*conflict|Status.*question` — open only the hubs that hit
per staged artifact  → three-way read: unanswered | already applied | apply now   [1-foldin.md]
per conflict/question row whose question now has a filled A: → RE-ENTER it as `new`
```

- **Re-enter an answered `conflict`/`question` row** (`1-foldin.md` § Re-entry). This is the one path
  that would otherwise lose a requirement permanently: such a row is not `staged`, so fold-in skips it,
  and not `new`/`held`, so Stage 2 skips it. Flipping it back to `new` here is what puts an answered
  disagreement back into this same run's Stage 2 worklist. Draft it from the **decision**, never by
  re-staging whichever side lost.
- **Reconcile mirrors unconditionally, every run** — including artifacts already applied, and
  **every** hub a cross-feature UC names. Re-setting a correct field is a no-op; skipping it leaves a
  hub reading `staged` against a folded-in UC forever.
- **Never overwrite a section the human edited first.** A staged entry whose anchor text has materially
  changed raises a question instead of applying; one whose content is already present, verbatim, is
  treated as applied rather than written twice.
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
  3a  uc-detector       resolves every UC/Context-lane signal to a UC-### — an existing id, or
                        `new (unminted)` — reading other features' hubs when a signal sounds
                        cross-feature. READ-ONLY: it writes nothing at all.
                        [agent-dispatch.md § 3a]
  ↳   ORCHESTRATOR      mints every new UC id + skeleton + hub pointer, ONE AT A TIME, between the
                        waves. Never a subagent: four features run concurrently and two concurrent
                        scans for "the highest id" return the same number.
                        [agent-dispatch.md § Minting new UCs]
  3b  uc-drafter        stages content into every lane, using the resolved UC targets AS GIVEN — it
                        never re-decides which UC a signal belongs to, and never mints one itself.
                        [agent-dispatch.md § 3b]

a subagent NEVER writes:  {design_principles_file}                                    # vault-wide
                          a NEW UC-### id or skeleton              # orchestrator mints, sequentially
                          a UC-### owned by another feature's primary_feature
                          another feature's hub · anything under {inbox_dir}
                          {entities_file} · {entity_dir}   # nobody writes these in this skill, not
                                                            # even Stage 4 — /sync-entities promotes,
                                                            # never here
    → it REPORTS design-principle candidates, cross_feature_uc_change items
    → Stage 4 applies them sequentially
a subagent DOES write:    its own feature's hub, its own UCs, its BRs
```

## Stage 4 — Sync, draft § 2/§ 3, and conflict-check

```text
orchestrator, after every Stage 3 subagent has reported                      [4-sync.md]
    write shared registers + every cross-feature UC change, ONE AT A TIME
    write each participating hub's ## Use Cases pointer   (may delegate per hub → hub-bookkeeper)
    spawn one uc-applier per UC carrying an unapplied ## 2 or ## 3 entry — worklist built GREP-FIRST
        over every in-scope UC's own ## Discussion, not just what Stage 3 reported this run.
        UCs on DIFFERENT primary_features run concurrently (≤ 4); two on the SAME feature run
        sequentially. The orchestrator flips the hub Signal Log rows itself afterwards — the only
        write two concurrent appliers would contend on.
    COVERAGE, NOT CLAIMS (Part 2b): dispatched rows vs reported rows · a destination per clause on
        every `<a> + <b>` row · no qualified row still `new`.  Mismatch is BLOCKING.
    flag any UC whose ## 2 changed this pass for /approve-uc re-review
    conflict-check each touched feature, scoped to that feature
```

A cross-feature UC change is **staged, not applied** — it is UC content, so it passes the same gate.
No entity is ever promoted here — that's `/sync-entities`'s job, run separately once a UC referencing
it is approved (§ Entity Data Model). Never auto-resolve a contradiction: raise it, name both sides,
stop.

**Only `## 2` and `## 3` skip the wait.** A rule, `## 1` (including a Context-lane Business Need),
`## 5`, or `## 6` always stages in `## Discussion` and waits for Stage 1 on a later run — see
`4-sync.md` § Part 2 for exactly what qualifies, how short to write it, and when a `## 2` change must
flag the UC for review.
The sweep is **cumulative, not scoped to this run** — a UC nobody's Stage 3 touched today can still
carry an entry an earlier run staged and never applied; Part 2 reads every in-scope UC's own
`## Discussion` fresh, every invocation, so a missed pass self-heals on the next run instead of
leaving `## 2`/`## 3` empty indefinitely.

## Stage 5 — Status and report

```text
orchestrator, last                                                           [5-status.md]
    set EVERY status from a LIVE RE-COUNT — never from what the run intended
        on a UC, count the ## 5 Still open list only; a decision-log row is answered history
    run the nine verification checks — incl. UC-id uniqueness (the mint-race backstop) and
        "no answered conflict/question row left un-re-entered"
    mismatch → BLOCKING: repair, re-check, then report
```

The report template lives in `5-status.md` § Part 4 — one copy, so a change to it can't drift against
this file.

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Drafting from an unqualified signal** — a flow built on an incomplete source reaches `/approve-uc`
  looking identical to a sound one.
- **Skipping `uc-detector`, or re-deciding new-vs-update inside `uc-drafter` anyway** — the whole
  reason the lookup got its own step is that a busy drafting pass under-reads a cross-feature hub and
  either mints a duplicate UC or drafts into the wrong one.
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
  that lane doesn't exist any more. Cite `{entities_file}`'s `proposed` row by name; `/sync-entities`
  is the only place a `proposed` row becomes an `EN-###` doc.
- **Pointing only the primary hub at a cross-feature UC** — the other features read as uninvolved.
- **Deciding a conflict** — recency settles a supersession, never a disagreement.
- **Setting status early** — this vault's most common drift. Re-count and set it last, every time.
- **Leaving an answered `conflict`/`question` row where it is** — the only path in this skill that loses
  a qualified requirement *permanently*: no later stage's worklist contains it. Stage 1 § Re-entry.
- **Minting a UC id inside a per-feature subagent** — four features run at once; two get the same number.
- **Trusting a subagent's report instead of diffing it against what was dispatched** — a partial pass and
  a complete one produce the same shape of report (Stage 4 Part 2b).
- **Overwriting a step the reviewer hand-edited** — the correction vanishes with nothing in any diff a
  human reads, under a Changelog line saying the apply was routine.
- **Writing a Context-lane Business Need straight into `## 1`** — `## 1` is inside the block no lane
  writes directly; only the `pain_points:` frontmatter id is a direct Context write.

## Model

**Every tier is pinned in the agent's own frontmatter** — `agents/uc-detector.md`, `agents/uc-drafter.md`,
`agents/uc-applier.md`, `agents/hub-bookkeeper.md`. Never restate or override one from a dispatch prompt:
one place to change it, and no second copy to drift.

The reasoning behind the pins: both Stage 3 subagents inherit the session default because this is
judgment-heavy work — which UC a signal belongs to, where a step sits in a flow, spotting a cross-feature
goal. Contrast `/extract-signal`, mechanical against a tight rule set. `uc-applier` sits one tier down:
it never decides routing or wording from scratch, only applies text someone already wrote against a
documented destination table. `hub-bookkeeper` is `haiku` — it mirrors facts it is handed.

Deep fidelity checking belongs to **`/extract-signal`'s source audit**, next to the raw material where
a quote-anchored check is cheap. This skill does the shallow half only (Stage 2, Gate 3).

## Additional resources

- **`references/agent-dispatch.md`** — the per-run variable data handed to `uc-detector` (§ 3a),
  `uc-drafter` (§ 3b), and `uc-applier` (Stage 4 Part 2, in `4-sync.md`) — their own procedures and
  report contracts live in `agents/uc-detector.md`, `agents/uc-drafter.md`, and `agents/uc-applier.md`
  respectively, plus the wave-verification checklist here.
- **`references/use-case-standard.md`** — where the UC artifact's shape comes from (Cockburn, BABOK,
  Use-Case 2.0, Wiegers), what is established practice and what is a deliberate departure. Read before
  changing the template or a lane guide; not needed for a run.
- **`agents/hub-bookkeeper.md`** — a narrowly-scoped `haiku` subagent for refreshing one feature hub's
  own derived tables (Signal Log Status/Destination cells, `## Use Cases`, `## Requirement Readiness`,
  `## Open Questions / Gates`, `## Changelog`) from facts already decided elsewhere. Two steps may
  delegate to it, **one hub per dispatch, sequentially**: `1-foldin.md` § Reconcile mirrors (items 1–2
  only — never the `{inbox_dir}` or `{requirements_file}` items, which it must not write) and
  `4-sync.md` § Part 1b's per-participating-hub pointer refresh. Delegating keeps a mechanical
  re-derivation out of the orchestrator's own context, which is the one context the whole fan-out design
  exists to protect. Never two hubs concurrently, and never hand it a decision — a `Status`,
  `Destination`, id, or lane arrives as a given fact or the dispatch is `blocked`.
