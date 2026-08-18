# Stage 4 — Sync the shared writes, draft § 2 / § 3, then conflict-check

```text
runs: orchestrator, SEQUENTIALLY, after every Stage 3 subagent has reported
in:   the candidates Stage 3's subagents REPORTED, plus every in-scope UC's own ## Discussion —
      Part 2 sweeps the full backlog every run, not just what this run staged
out:  shared registers written · cross-feature UC changes staged · every participating hub pointed
      · § 2 Main Success Scenario and § 3 Alternative/Exception Flows drafted for any UC carrying an
      unapplied entry for either · a review flag written whenever § 2 changed · each touched feature
      conflict-checked
never: inside a per-feature subagent — two concurrent features Grep the same highest id and both
       mint the same new UC-### number, or one append to a shared register overwrites the other
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
MINT EVERY ID HERE, never in a subagent — UC-### for a `new` cross_feature_uc_change
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

## Part 2 — Draft § 2 and § 3, then flag review

```text
runs: one subagent per UC carrying an unapplied § 2 or § 3 entry — build this worklist by reading
      every in-scope UC's own ## Discussion directly, not from what Stage 3 reported this run.
      A UC nobody's Stage 3 touched this run can still carry an entry an earlier run staged and no
      run has ever applied — sweep for it every time, same as a freshly-staged one.
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
Agent(session default model, uc-applier, foreground), one per UC
```

Its rulebook — the three-way pre-read, the destination table, the § 2 wording standard, the one-write
sequence, and the review-flag rule — is baked into `agents/uc-applier.md`; this dispatch only needs to
name the one UC to apply this pass over. Report format is fixed in that agent's own § Report.

## Part 3 — Conflict-check each touched feature

Scoped **to that feature**, not the vault. After a new or updated UC/BR lands, re-read that feature's
UC(s) together with its BRs and look for a genuine contradiction — two statements that cannot both hold.

```text
1  step vs. rule       — a ## 4 rule whose condition contradicts what a step does
2  rule vs. rule       — two BRs on the same feature that cannot both hold
3  dangling citation   — a ## 4 enforcement point or ## 3 branch point naming an S# that doesn't
                         exist, or that names a row marked removed
```

A vault-wide sweep costs quadratically more and belongs to `/enrich-feature`. A wording difference, a
narrower restatement, or two rules about different conditions are **not** contradictions.

```text
NEVER auto-resolve one. Recency settles a supersession; it never settles a disagreement between
two people's stated requirements.

on finding one:
1  raise ONE "- [ ] Q:" on the UC's ## 5, naming both sides and where each came from
   → it must read cold, to someone with no context
2  flip the triggering Signal Log row to `conflict`, citing the earlier row's # in Notes
3  STOP THERE. Stage 5 sets the status from the live question count.
```

## Hand-off

Report: `<N> design-principle row(s), <N> cross-feature UC change(s), <N>
UC(s) with § 2 and/or § 3 drafted, <N> of those flagged for review, <N> in-feature conflict(s)` — or
`none this run`. Stage 5 re-counts questions on every artifact this stage touched, including any UC
that just gained a conflict question or dropped back from `approved`/`enriched` because its main flow
changed.

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
