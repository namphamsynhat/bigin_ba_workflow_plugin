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
Agent(session default model, general-purpose, foreground), one per UC

Pull every requirement fact tied to this UC before writing a word:
1  read the UC file in full — § 1 through § 6 as they stand today, and EVERY ## Discussion entry,
   not only the ones this run staged
2  for each entry about to be applied, read its cited hub Signal Log row(s) in full (Signal, Notes,
   Status) — the entry's own paraphrase can predate a citation correction made since it was staged
3  note every existing S#/A#/E# id already in use, including removed rows, so nothing mints a
   duplicate

Apply ONLY entries whose destination starts "new step", "S# becomes:", "S# is removed because",
"new flow", "A#/E# becomes:", or "A#/E# is removed because". Leave every other entry alone — do not
remove it, do not fold it in.

| Destination says                          | Do |
| :--- | :--- |
| new step after S4: <text>                 | mint the next unused S# (one higher than the highest ever used, including removed rows), insert after S4, never renumber the rows below |
| S6 becomes: <text>                        | replace S6's two cells, keep the id S6 |
| S6 is removed because <reason>            | keep the row and id, write **S6** *(removed v<version> — <reason>)*, empty the cells |
| new flow A2: <text> / new flow E2: <text> | mint the next unused id in its own series (A# or E#, one higher than the highest ever used including removed), append as a new § 3 subsection with the stated branch point, condition, steps, and ending |
| A2 becomes: <text>                        | replace A2's body, keep its id and heading |
| A2 is removed because <reason>            | keep the heading and id, write *(removed v<version> — <reason>)*, empty the body |

Write § 2 cells SHORT and HIGH-LEVEL, one line, plain business language:
    "Parent submits the payment request" — not a paragraph with every validation clause.
Write a § 3 flow to the template's own shape: branch point as an S# id, condition as a detected fact
never a question, and an explicit ending (rejoins an S#, reaches a different success, or fails).
Never invent a step, flow, validation, or branch nobody stated — missing detail stays missing, never
guessed. Before minting an A#/E#, confirm its stated branch point S# still exists and isn't removed —
if it is, that inconsistency is a question (see step 4 below), not a fold-in.

Example of the level of detail § 2 wants:
    Parent submits the payment request
    Parent selects the student/award
    Parent selects the vendor or submits a new vendor
    Parent enters the amount, date, invoice number
    System checks the request and records it with the entered data

Then, ONE write:
1  remove the entries you just applied from ## Discussion — leave every other entry in place
2  bump version, append one ## Changelog line per INT-### applied
3  flip that INT's hub Signal Log row: staged → applied
4  if a branch point or enforcement point no longer resolves to a live S#, raise ONE question on
   § 5 naming both sides instead of silently re-pointing it (same rule as Stage 1's fold-in)
5  if § 2 changed this pass (a step added, changed, or removed) — flag for review:
     a  if status is enriched/approved/consolidated, this content edit already reverts it per
        5-status.md's hard rule — say so explicitly in the Changelog line, e.g. "... — reverts from
        approved, main flow changed, needs /enrich-feature + /approve-uc re-review"
     b  regardless of prior status, end the Changelog line with "flagged for /enrich-feature +
        /approve-uc review" so the reason a human should look again is visible without diffing
   a § 3-only change (no § 2 step touched) does NOT trigger this flag — a stated branch changing what
   happens off the happy path is lower-stakes than the happy path itself changing

Report: UC-### — N step(s) added, N changed, N removed to § 2; N flow(s) added, N changed, N removed
to § 3; flagged for review: yes/no.
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

Report: `<N> entity promotion(s), <N> design-principle row(s), <N> cross-feature UC change(s), <N>
UC(s) with § 2 and/or § 3 drafted, <N> of those flagged for review, <N> in-feature conflict(s)` — or
`none this run`. Stage 5 re-counts questions on every artifact this stage touched, including any UC
that just gained a conflict question or dropped back from `approved`/`enriched` because its main flow
changed.

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
