# Stage 4 — Sync the shared writes, draft § 2 / § 3, then conflict- and coverage-check

```text
runs: orchestrator, after every Stage 3 subagent has reported
      Part 1 and Part 1b are STRICTLY SEQUENTIAL — every write completes before the next starts
      Part 2 parallelizes across UCs owned by DIFFERENT features (§ Part 2), never within one
in:   the candidates Stage 3's subagents REPORTED, plus every in-scope UC's own ## Discussion —
      Part 2 sweeps the full backlog every run, not just what this run staged
out:  shared registers written · every new UC id minted · cross-feature UC changes staged · every
      participating hub pointed · § 2 Main Success Scenario and § 3 Alternative/Exception Flows
      drafted for any UC carrying an unapplied entry for either · a review flag written whenever
      § 2 changed · coverage diffed against what was dispatched · each touched feature
      conflict-checked, then coverage-checked as a whole UC set
never: an id minted inside a per-feature subagent — two concurrent features Grep the same highest id
       and both mint the same new UC-### number, or one append to a shared register overwrites
       the other
```

Most runs sync nothing.

## Part 1 — Write the shared and cross-feature changes, one at a time

Each write completing before the next starts:

| # | Candidate | Write | Detail |
| :--- | :--- | :--- | :--- |
| 1 | `design_principle_candidates` | `{design_principles_file}` row | `3-lane-design.md` § Destination 1 |
| 2 | `cross_feature_uc_change` | the staged `## Discussion` entry on the UC its `owner` names — creating the UC from `{template_uc}` if the candidate says `new` | `3-lane-uc.md` |
| 3 | — | the matching pointer on **each participating hub** | § Part 1b |

Steps 2 and 3 belong in this same sequential pass, not back in Stage 3: a cross-feature UC touches hubs
whose own subagent has already finished, and a pointer written from two places at once loses a row.

No entity is minted or promoted here — that's `/sync-entities`'s job, run separately once a UC is
approved, never Stage 4 (§ Entity Data Model). This stage only ever cites an existing `{entities_file}`
row by name.

```text
MINT EVERY ID IN THE ORCHESTRATOR, never in a subagent — including every ordinary new UC-###, which
    `uc-router`'s Phase A only PROPOSES as `new (unminted)` and the orchestrator mints between Phase A
    and Phase B (references/agent-dispatch.md § Minting new UCs). This section covers the ones that
    surface later: a `new` cross_feature_uc_change, and anything a repair pass adds.
    Grep for the highest existing id and increment
    create a register from its template ({template_design_principles}) if absent

a cross_feature_uc_change is STAGED, NOT APPLIED — it is UC content, so it passes the same gate:
    write the ## Discussion entry
    flip the REPORTING feature's Signal Log row: Status: staged, Destination: UC-###
    Stage 1 folds it in on a later run — UNLESS it's a main-flow step or a flow, which Part 2 below
    picks up this same pass, same as any other § 2/§ 3 entry
```

### Part 1b — every participating hub, not just the primary

For each UC this run created or changed, re-derive its pointers from the UC's own `features:` list:

```text
## Use Cases
- UC-012 Enrol a student — owns (primary) | participates | draft
```

- One row per UC on **each** hub in `features:`, and the id in each hub's `uc:` list.
- The row says whether that feature `owns` the UC (it is `primary_feature`) or `participates`.
- **No step counts.** The retired `SCN-###` register carried `(step 2 of 4)` on each hub, which went
  stale silently every time a step was inserted. The UC file is the only place the flow is written out.
- Setting an already-correct pointer again is a no-op — **re-derive all of them every run** rather than
  tracking which changed.
- **May be delegated, one hub per dispatch, sequentially** — to `hub-bookkeeper` (`agents/hub-bookkeeper.md`),
  whose whole contract is re-deriving a hub's own tables from facts already decided. Hand it the UC ids
  touched and let it re-read their frontmatter itself. Never two hubs at once: concurrent appends to two
  hubs is fine, but concurrent *dispatches for the same UC* is how one hub's pointer row goes missing.
- **`{requirements_file}`'s `UC` column stays the orchestrator's own write, never `hub-bookkeeper`'s**
  (`agents/hub-bookkeeper.md` never writes `{requirements_file}`). After every hub's `uc:` list is
  re-derived above, the orchestrator re-derives the `UC` column of each touched feature's
  `{requirements_file}` row the same way — from that hub's now-current `uc:` list, not by tracking
  what changed this run. Missing this step is how the registry's UC column quietly drifts behind the
  hub's own `uc:`/`## Use Cases`, which stays correct — until some later reader trusts the stale
  registry column instead of the hub and scopes their work to the wrong set of UCs.

## Part 2 — Draft § 2 and § 3, then flag review

```text
runs: one subagent per UC carrying an unapplied § 2 or § 3 entry — build this worklist over every
      in-scope UC's own ## Discussion, not from what Stage 3 reported this run.
      A UC nobody's Stage 3 touched this run can still carry an entry an earlier run staged and no
      run has ever applied — sweep for it every time, same as a freshly-staged one.
      BUILD IT GREP-FIRST: Grep {uc_dir} for `→ proposed: (new step|S[0-9]+ becomes|S[0-9]+ is
      removed|new flow|A[0-9]+ becomes|E[0-9]+ becomes|A[0-9]+ is removed|E[0-9]+ is removed)`
      and open only the UCs that hit. Reading every in-scope UC in full to discover that none carry
      an entry is the same O(vault) cost Stage 1 avoids the same way — and it grows every run.
in:   that UC's ## Discussion entries whose destination is "new step ...", "S# becomes:", "S# is
      removed because ...", "new flow A#/E#:", "A#/E# becomes:", or "A#/E# is removed because ..." —
      PLUS everything needed to write them faithfully: the UC's own current § 1-§ 4 (actor names,
      existing step/flow ids, rule cross-references) and the hub Signal Log row(s) each entry's
      INT-### citation names, read for that row's full CURRENT Notes — a citation can have been
      corrected or extended since the entry was first staged
out:  § 2 and § 3 written directly, same run · a review flag written on any UC whose § 2 changed
never: touch § 1, § 4, § 5, § 6, or invent a step/flow/branch condition no entry proposed
```

**Why this sweeps everything, not just today's.** An entry that misses one run's Part 2 — because that
run's Stage 3 never re-touched the UC, an earlier invocation of this skill stopped before Stage 4 ran,
or an older version of this stage only checked "staged this run" — otherwise sits in `## Discussion`
forever: nothing else ever revisits it, and a UC can carry a fully-written main-flow step or branch for
months while its `## 2`/`## 3` stay a placeholder row. Reading every in-scope UC's own `## Discussion`
section, every run, is what makes a missed pass self-healing instead of a silent, permanent gap.

**Why § 3 now writes directly too.** A branch is a business-story fact the same way a step is — "the
card is declined" is not an inherently riskier claim than "the parent submits the card." What kept § 3
waiting before was caution, not a real difference in review weight; the review flag below (a write
made visible *after* the fact) now carries that caution instead of a pre-write wait.

```text
Agent(uc-applier, foreground), one per UC — the agent pins its own model tier, one below session
    default (agents/uc-applier.md frontmatter); the orchestrator does not override it

PARALLELISM: UCs owned by DIFFERENT primary_features may run concurrently, ≤ 4 at a time.
    Two UCs on the same primary_feature run SEQUENTIALLY — they can share a hub row, a BR mirror,
    or a step id neither has minted yet.
    THE ORCHESTRATOR FLIPS THE HUB SIGNAL LOG ROWS ITSELF, after each wave reports — that is the
    only write two concurrent appliers would contend on, so it does not live in the agent.
```

Its rulebook — the three-way pre-read, the destination table, the § 2 wording standard, the one-write
sequence, and the review-flag rule — is baked into `agents/uc-applier.md`; this dispatch only needs to
name the one UC to apply this pass over. Report format is fixed in that agent's own § Report.

### The human may have edited § 2/§ 3 first

Same hazard as Stage 1's, and the same two rules (`1-foldin.md` § The human may have edited the section
first) — a reviewer is explicitly invited to hand-edit a flow while reviewing it, so an entry's anchor
text can already be gone by the time this pass runs:

```text
`S6 becomes:` and S6's current text ALREADY MATCHES the entry's proposed text
    → treat as applied: drop the entry, append the Changelog line, flip the row. Write nothing.
      (a hand-applied change carries no Changelog cite, so without this it lands a second time)
`S6 becomes:` and S6 has been REWORDED since the entry was staged, materially
    → DO NOT overwrite. Raise ONE question on the UC's ## 5 naming both wordings, leave the entry in
      ## Discussion, leave the row `staged`, and report it. Stage 5 will read the new question and
      set needs-clarification.
`new step after S4:` whose text already exists as some other S#
    → treat as applied, citing the id it actually landed as
```

Overwriting is the worse failure of the two: a reviewer's own correction disappears with nothing in any
diff a human reads, and the UC then carries text nobody approved under a Changelog line that says it
was applied routinely.

## Part 2b — Coverage, not claims

Before Part 3, diff what was **dispatched** against what was **reported**. Every stage in this skill
reports its own success, and a subagent that silently skipped a row reports the rows it did handle —
which reads identically to a clean run.

```text
1  dispatched vs reported — for each Stage 3 feature, the worklist you handed it vs the rows its
   report accounts for. A row in the dispatch and in no report line is UNACCOUNTED: re-dispatch it
   scoped, or park it `held` with why. Never let it fall off the ledger silently.
2  per-clause coverage — a themed row whose Type is `<a> + <b>` must show a destination per clause
   in its Destination cell (` · `-joined). One destination on a two-clause row means a clause was
   dropped at routing (3-routing.md § Route per CLAUSE).
3  no qualified row still `new` — a row Stage 2 qualified this run must now read `staged`, `applied`,
   `conflict`, or `question`. One still sitting at `new` after Stage 3 and Stage 4 is a row nothing
   processed and nothing will report as missed.
```

A mismatch here is **blocking**, the same as Stage 5's checks: fix or park with a written reason, then
re-check. Report the counts either way — "3 dispatched, 3 accounted for" is the line that makes a future
silent drop visible by contrast.

## Part 3 — Conflict-check each touched feature

Scoped **to that feature**, not the vault. After a new or updated UC/BR lands, re-read that feature's
UC(s) together with its BRs and look for a genuine contradiction — two statements that cannot both hold.

```text
1  step vs. rule       — a ## 4 rule whose condition contradicts what a step does
2  rule vs. rule       — two BRs on the same feature that cannot both hold
3  dangling citation   — a ## 4 enforcement point or ## 3 branch point naming an S# that doesn't
                         exist, or that names a row marked removed
```

A vault-wide sweep costs quadratically more, and nothing runs one today — the per-UC contradiction
sweep was never `/enrich-feature`'s job even under its old design, and its retargeted, feature-scoped
form (`conventions.md` § Reconciliation notes) doesn't read UC content at all. Do **not** promote this
scoped check into
a vault-wide one to compensate: per-feature every run is what keeps an unattended run's cost proportional
to what changed. A wording difference, a narrower restatement, or two rules about different conditions are
**not** contradictions.

```text
NEVER auto-resolve one. Recency settles a supersession; it never settles a disagreement between
two people's stated requirements.

on finding one:
1  raise ONE "- [ ] Q:" on the UC's ## 5, naming both sides and where each came from
   → it must read cold, to someone with no context
2  flip the triggering Signal Log row to `conflict`, citing the earlier row's # in Notes
3  STOP THERE. Stage 5 sets the status from the live question count.
```

## Part 4 — Coverage-check each touched feature

Part 3 asked whether this feature's requirements contradict each other. Part 4 asks the other half —
whether they **add up**: whether the actor could get this feature's job done with only what is written
down. Its whole procedure, the six lenses, the guard that keeps silence from becoming a guess, and the
`## Coverage Gaps` row format live in `4b-coverage.md`. Run it per in-scope feature, after Part 3.

```text
run it when: a UC on this feature was created this run or its § 2 changed
             · the hub has no `## Coverage Gaps` section yet (never checked — backfill once)
             · $ARGUMENTS named this slug (so an EMPTY Stage 2 worklist does not skip it)
skip it when: the feature has no UC at all — there is no set to reason about
writes:      `## Coverage Gaps` rows on that feature's hub, plus the open ones mirrored into
             `## Open Questions / Gates`
never:       a UC, a step, a Signal Log row, a `- [ ] Q:` on any UC, or another feature's hub
```

A coverage gap **never parks a UC**. It is a feature-level finding, so a UC that is otherwise ready
stays ready — which is exactly why gaps get their own register instead of borrowing `## 5`'s question
mechanism (`4b-coverage.md` § What this stage never does).

## Hand-off

Report: `<N> design-principle row(s), <N> UC id(s) minted, <N> cross-feature UC change(s), <N>
UC(s) with § 2 and/or § 3 drafted, <N> of those flagged for review, <N> drift question(s) raised
instead of applied, <N> dispatched/<N> accounted for (Part 2b), <N> in-feature conflict(s),
<N> coverage gap(s) raised and <N> closed across <N> feature(s)` — or `none this run`. Name the
features whose coverage came back clean rather than omitting them (`4b-coverage.md` § Report line):
"clean" and "nobody looked" are different results and the report is the only place they differ.

Stage 5 re-counts questions on every artifact this stage touched, including any UC that just gained a
conflict question or dropped back from `approved`/`enriched` because its main flow changed. A coverage
gap is **not** one of those counts — it lives on the hub, not on a UC, and it moves no UC's status.

## Failure modes

- **Letting a subagent write a register or another feature's UC.** Two features mint the same new
  UC-### number, or one append silently overwrites the other. This is why the stage exists.
- **Applying a cross-feature UC change instead of staging it.** It is UC content; skipping the gate
  makes it indistinguishable afterwards from reviewed content.
- **Pointing only the primary hub at a cross-feature UC.** Nobody working from the other hubs knows the
  workflow touches them.
- **Deciding a conflict.** Choosing a winner buries a real disagreement inside an artifact that then
  reads as settled.
- **Promoting an entity here at all.** That lane doesn't exist in this skill any more — a `proposed`
  row is cheap and reversible, an `EN-###` doc is a permanent id and a maintenance obligation, and
  `/approve-uc` is the only place that trade gets made, at the point a human is actually confirming
  the UC that references it.
- **Skipping the conflict check because the run "only updated" a UC.** An update is exactly how a new
  step lands next to a rule that forbids it.
- **Skipping the coverage check for the same reason.** A new step is exactly how a pre-condition
  nothing satisfies gets introduced — and a feature whose four use cases each look sound is exactly
  the shape of a feature nobody can use (`4b-coverage.md`).
- **Turning a coverage gap into a UC, a step, or a question on a UC.** A gap is a finding: the content
  comes from the answer, through `/bigin-intake`, like every other requirement. Writing it as a
  `- [ ] Q:` parks a UC that was ready over something that isn't its fault.
- **Stretching Part 2's exception to § 1/§ 4/§ 5/§ 6.** Only § 2 and § 3 entries skip the wait — a
  rule, `## 1` metadata, an open question, or a special requirement still stages in `## Discussion`
  and waits for Stage 1.
- **Scoping the sweep to only this run's Stage 3 output.** A UC nobody's Stage 3 touched this run can
  still be carrying an old, unapplied § 2/§ 3 entry from a run whose Stage 4 never ran or ran under an
  older, narrower version of this rule. Read every in-scope UC's own `## Discussion`, every run — not
  just what Stage 3 just reported — or the gap becomes permanent.
- **Writing § 2 without flagging.** Leaving an updated main flow with no visible note that a human
  should look again — whether that means an explicit status revert from `approved`/`enriched` or just
  a Changelog line saying so — reads as unreviewed content nobody was told to check.
- **Writing validation prose into a § 2 cell, or a full validation ruleset into a § 3 step.** Keep both
  to one short business line each; a real validation detail belongs in § 4, not padding the flow.
- **Overwriting a step the reviewer reworded.** The entry's text wins over a human's edit exactly never
  — see § The human may have edited § 2/§ 3 first.
- **Trusting the subagent reports instead of diffing them against the dispatch.** Part 2b exists because
  a partial pass and a complete one produce the same *shape* of report.
- **Running two `uc-appliers` on UCs that share a `primary_feature`.** They contend on the hub row, the
  BR mirror, and the next unused step id.
