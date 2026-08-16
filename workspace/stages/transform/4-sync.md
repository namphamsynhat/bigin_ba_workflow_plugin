# Stage 4 — Sync the shared writes, draft § 2, then conflict-check

```text
runs: orchestrator, SEQUENTIALLY, after every Stage 3 subagent has reported
in:   the candidates Stage 3's subagents REPORTED
out:  shared registers written · cross-feature UC changes staged · every participating hub pointed
      · § 2 Main Success Scenario drafted for any UC with a new step this run · each touched
      feature conflict-checked
never: inside a per-feature subagent — two concurrent features Grep the same highest id and both
       mint EN-007, or one append overwrites the other
```

Most runs sync nothing. **Never promote an entity speculatively** — a `proposed` row stays a row until
a UC step or a BR genuinely references it.

## Part 1 — Write the shared and cross-feature changes, one at a time

Each write completing before the next starts:

| # | Candidate | Write | Detail |
| :--- | :--- | :--- | :--- |
| 1 | `entity_candidates` | `{entities_file}` row → promote to `{entity_dir}` | `3-lane-entity.md` |
| 2 | `design_principle_candidates` | `{design_principles_file}` row | `3-lane-design.md` § Destination 1 |
| 3 | `cross_feature_uc_change` | the staged `## Discussion` entry on the UC its `owner` names — creating the UC from `{template_uc}` if the candidate says `new` | `3-lane-uc.md` |
| 4 | — | the matching pointer on **each participating hub** | § Part 1b |

Steps 3 and 4 belong in this same sequential pass, not back in Stage 3: a cross-feature UC touches hubs
whose own subagent has already finished, and a pointer written from two places at once loses a row.

```text
MINT EVERY ID HERE, never in a subagent — EN-###, and UC-### for a `new` cross_feature_uc_change
    Grep for the highest existing id and increment
    create a register from its template ({template_entities}, {template_design_principles}) if absent

a cross_feature_uc_change is STAGED, NOT APPLIED — it is UC content, so it passes the same gate:
    write the ## Discussion entry
    flip the REPORTING feature's Signal Log row: Status: staged, Destination: UC-###
    Stage 1 folds it in on a later run — UNLESS it's a main-flow step, which Part 2 below
    picks up this same pass, same as any other § 2 entry
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

## Part 2 — Draft the Main Success Scenario

```text
runs: one subagent per UC, after Part 1, only for a UC with a new/changed/removed main-flow step
      staged this run (from Stage 3 or from Part 1 above)
in:   that UC's ## Discussion entries whose destination is "new step ...", "S# becomes:", or
      "S# is removed because ..."
out:  § 2 written directly, same run
never: touch § 1, § 3, § 4, § 5, § 6, or a flow ("new flow A#/E#") entry — those still stage and
       wait for a human, same as always
```

**Why this one section skips the wait.** § 2 is a short, high-level business story — low risk to
write straight away, and it's the thing a human actually reads to review a UC. Everything riskier
(branches, rules, exceptions) still waits for Stage 1's gate on a later run.

```text
Agent(session default model, general-purpose, foreground), one per UC

Read the UC file in full: its current § 2 and every ## Discussion entry.

Apply ONLY entries whose destination starts "new step", "S# becomes:", or "S# is removed
because". Leave every other entry alone — do not remove it, do not fold it in.

| Destination says              | Do |
| :--- | :--- |
| new step after S4: <text>     | mint the next unused S# (one higher than the highest ever used, including removed rows), insert after S4, never renumber the rows below |
| S6 becomes: <text>            | replace S6's two cells, keep the id S6 |
| S6 is removed because <reason> | keep the row and id, write **S6** *(removed v<version> — <reason>)*, empty the cells |

Write each cell SHORT and HIGH-LEVEL, one line, plain business language:
    "Parent submits the payment request" — not a paragraph with every validation clause.
Never invent a step, field, or check the signal didn't state — missing detail stays missing,
never guessed.

Example of the level of detail this section wants:
    Parent submits the payment request
    Parent selects the student/award
    Parent selects the vendor or submits a new vendor
    Parent enters the amount, date, invoice number
    System checks the request and records it with the entered data

Then, ONE write:
1  remove the entries you just applied from ## Discussion — leave every other entry in place
2  bump version, append one ## Changelog line per INT-### applied
3  flip that INT's hub Signal Log row: staged → applied

Report: UC-### — N step(s) added, N changed, N removed.
```

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

Report: `<N> entity promotion(s), <N> design-principle row(s), <N> cross-feature UC change(s),
<N> UC(s) with § 2 drafted, <N> in-feature conflict(s)` — or `none this run`. Stage 5 re-counts
questions on every artifact this stage touched, including any UC that just gained a conflict
question.

## Failure modes

- **Letting a subagent write a register or another feature's UC.** Two features mint the same `EN-###`,
  or one append silently overwrites the other. This is why the stage exists.
- **Applying a cross-feature UC change instead of staging it.** It is UC content; skipping the gate
  makes it indistinguishable afterwards from reviewed content.
- **Pointing only the primary hub at a cross-feature UC.** Nobody working from the other hubs knows the
  workflow touches them.
- **Deciding a conflict.** Choosing a winner buries a real disagreement inside an artifact that then
  reads as settled.
- **Promoting an entity nothing asked for.** A `proposed` row is cheap and reversible; an `EN-###` doc
  is a permanent id and a maintenance obligation.
- **Skipping the conflict check because the run "only updated" a UC.** An update is exactly how a new
  step lands next to a rule that forbids it.
- **Stretching Part 2's exception to § 3/§ 4/§ 6.** Only a new/changed/removed main-flow step skips
  the wait — a flow, a rule, or anything else still stages in `## Discussion` and waits for Stage 1.
- **Writing validation prose into a § 2 cell.** Keep it one short business line; a real validation
  detail belongs in § 4 or a branch, not padding the main flow.
