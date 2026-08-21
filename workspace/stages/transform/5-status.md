# Stage 5 — Status, verification, and report

```text
runs: orchestrator, LAST
in:   every artifact this run touched
out:  every status set from a LIVE RE-COUNT · hubs refreshed · nine checks · the report
never: a status decided in Stages 1-4 — they write content and leave status alone
```

A status decided mid-stage and left stale by a later edit to the same artifact is this vault's most
common drift.

## Part 1 — Set every status from a live re-count

```text
per artifact, in this order:
1  apply every accepted change to the question list first
     a UC's ## 5 Still open · a BR's ## Open Questions
     tick NOTHING that isn't genuinely resolved
     move genuinely resolved lines into the UC's decision-log table
2  RE-COUNT the remaining unchecked "- [ ] Q:" lines BY READING THE SECTION ON DISK
     on a UC, count the Still open list ONLY — a decision-log row is answered history
3  set the status:
     count > 0 → needs-clarification
     count = 0 → draft, or the stage the artifact had already reached if this run only resolved a
                 question without editing content
```

Two hard limits:

- **Never write `in-review` or `superseded` on a UC/BR** — both retired. Never write `removed` either —
  human-gated only.
- **Editing content on an `enriched`/`approved`/`consolidated` artifact sets it back** to
  `draft`/`needs-clarification`. Approval does not freeze a UC. This is exactly what makes Stage 4
  Part 2's review flag real rather than cosmetic: a § 2 change on an already-`approved` UC lands here
  and drops it back automatically — Part 2's Changelog line just makes the reason legible without a
  diff.

## Part 2 — Refresh the hub, don't restate it

Per touched hub — **including every hub a cross-feature UC named in `features:`**, not just the ones
whose own signals were processed:

```text
refresh ## Requirement Readiness   # a snapshot for orientation, re-derived from each UC's/BR's own
                                   # status. NOT the gate — each artifact's own status is
confirm ## Use Cases and uc: match the UC's features:   # Stage 4 Part 1b wrote them; this is read-back
confirm every `open`/`answered` ## Coverage Gaps row is mirrored in ## Open Questions / Gates
LEAVE ## Coverage Gaps ITSELF ALONE  # Stage 4 Part 4 owns it (4b-coverage.md). Never re-derive,
                                   # re-status, or add a row here — and never delete the section
                                   # because it is empty: empty means the set adds up, MISSING means
                                   # nobody has checked, which is the coverage pass's backfill trigger
append one ## Notes / History bullet
DO NOT change the hub's status:    # it mirrors the {requirements_file} row — a SCOPE state, not a
                                   # workflow state. There is no "ready for PRD" feature status.
```

## Part 3 — Verify before reporting

Each is a real failure that otherwise reports as success. Check all nine, every run. **A mismatch is
blocking:** repair and re-check rather than report a count the vault doesn't support.

### Run the deterministic checker first

Four of the nine, plus parts of two more, are pure counting — and a program that counts beats an agent
that counts, both in cost and in not being able to talk itself into a pass:

```text
ORCHESTRATOR ONLY, once, before working the table below:
    Bash: python3 "${CLAUDE_PLUGIN_ROOT}/hooks/bigin-lint.py" --full
    exit 0 → checks 1, 5, 7, 8 and the mechanical halves of 4 and 6 are clean; skip re-doing them
    exit 1 → its findings ARE Part 3 mismatches. Blocking, same as any other. Repair, re-run it.

    ${CLAUDE_PLUGIN_ROOT} does not resolve, python3 is missing, or the command is denied
        → SAY SO in the report, then do all nine checks by hand as below.
        NEVER treat an unavailable checker as a pass: a run that silently skipped verification
        is exactly the failure this whole section exists to prevent.
```

**A subagent cannot run this** — `${CLAUDE_PLUGIN_ROOT}` only resolves in the orchestrator, which is
where Part 3 runs anyway. Don't hand the command to a dispatched agent.

| # | The checker covers | Still yours |
| :--- | :--- | :--- |
| 1 | fully | — |
| 2 | — | all of it: "would the existing text satisfy a tester checking this signal" is judgment |
| 3 | — | all of it: needs to know what changed *this run*, which only you know |
| 4 | the `- [ ] Q:` exists on the artifact named | whether it duplicates a question already open on the source note |
| 5 | fully | — |
| 6 | duplicate ids, and every `## 3`/`## 4` reference resolving to a live step | whether anything was renumbered *this run* |
| 7 | fully | — |
| 8 | fully | — |
| 9 | — | all of it: the row → question link is prose, not a parseable field |

The checker is an accelerator, not a replacement. It cannot see intent, and it cannot see history.

**Coverage gaps are deliberately not a tenth check.** The nine are consistency invariants — a
statement the vault either satisfies or doesn't. "This feature's use-case set doesn't add up" is a
judgment about the business, made once per touched feature in Stage 4 Part 4 with the whole set in
view, and it moves no artifact's status. The one thing Part 2 above does assert is the *mirror*: an
`open` gap row that never reached `## Open Questions / Gates` is invisible to the human, which is a
bookkeeping failure and does belong here.

| # | Check | Why |
| :--- | :--- | :--- |
| 1 | every `staged` row has a matching `## Discussion` entry citing its `INT-###` | a `staged` row with nothing staged is stranded — it no longer reads as pending, so no future run collects it |
| 2 | every `applied` row shows its content at the id its `Destination`/`Notes` names, or carries a pointer explaining why no change was needed | `2-qualification.md` Gate 4 |
| 3 | no Signal Log row renumbered, deleted, un-merged, or had its `Signal`/`Source` rewritten — except a Gate 3 clause refresh carrying `Notes: refreshed from <INT-###>` | row `#`s are permanent, and a themed row's `Source` cite is the only trail back to the note rows it covers |
| 4 | every question raised exists as an unchecked `- [ ] Q:` on the artifact named, and duplicates no question already open on the source `INT` note | one question, two places — never two questions |
| 5 | each touched artifact's `status` matches its live unchecked-question count | the invariant Part 1 exists to hold |
| 6 | **no `S#`/`A#`/`E#` reused, renumbered, or deleted this run**, and every `## 3` branch point and `## 4` enforcement point resolves to a step id that exists and isn't removed | these ids are cited from rules, flows, stories, and prototypes; a renumber breaks all of them silently |
| 7 | for every UC touched, each slug in its `features:` has a `## Use Cases` row and the id in its `uc:` list — and no hub lists a UC that doesn't name it | a cross-feature UC on one hub reads as complete while the other features have no idea they're involved |
| 8 | **no two files in `{uc_dir}` carry the same `UC-###` id** (`Grep '^id:' {uc_dir}`, compare against the filenames) — same for `{br_dir}` and `BR-###` | the backstop on the id-mint race. Up to four features process concurrently; only the orchestrator may mint (`4-sync.md`), and this check is what catches it if that discipline slipped. Two UCs sharing an id means every citation of it is ambiguous forever |
| 9 | **no `conflict`/`question` Signal Log row on a touched hub whose linked question now carries a filled `A:`** — those should have been re-entered as `new` by Stage 1 and drafted by Stage 3 this same run | `1-foldin.md` § Re-entry. A row left here is an answered, qualified requirement that no future stage will ever collect: not `staged` (so fold-in skips it) and not `new`/`held` (so qualification skips it) |

## Part 4 — Report

```text
Stage 1 (fold-in): <N> UC/BR resolved — <slug>: UC-### now draft
                   <N> re-entered — <slug> #<n>: <the decision that unblocked it>   # 1-foldin § Re-entry
                   <N> drift question(s) raised instead of applied
Stage 2 (qualify): <N> qualified, <N> held (<reason>), <N> applied as duplicate/already-covered
Stage 3 (draft):   <N> UC created, <N> updated, <N> BR created, <N> BR updated
                   — <slug>: UC-### (staged, needs-clarification | staged, draft)
                   steps staged: <slug> UC-### — <N> new, <N> changed, <N> flow(s)
                   design: <N> directive(s) — <slug> ## Design Directives, <N> DESIGN-PRINCIPLES row(s)
Stage 4 (sync):    <N> UC id(s) minted, <N> cross-feature UC change(s),
                   <N> UC(s) with § 2/§ 3 drafted, <N> flagged for review, <N> conflict(s) — or none
                   dispatch coverage: <N> dispatched / <N> accounted for              # 4-sync § Part 2b
                   set coverage: <slug> — <N> new gap(s) (<lens>, <lens>), <N> closed,
                       <N> held back | <slug> — clean                              # 4b-coverage.md
cross-feature:     UC-### spans <slug> · <slug> — pointers written on both
remaining:         <slug>: UC-###/BR-### — N open question(s), owner client|team
                   <slug>: N coverage gap(s) open — for the next client conversation, not a UC blocker
next:              <slug> ready for /approve-uc | <slug> ready for /bigin-generate-design (design-only)
```

**Report what the vault says after Part 3, not what the run intended.** A held signal names its remedy;
a blocked row names why. An FR adoption is always named explicitly — the one case where one signal
produces a large diff.

## Failure modes

- **Setting status from intent.** "I resolved that question" ≠ "the box is ticked on disk."
- **Counting decision-log rows as open questions.** They are answered history; counting them parks a
  finished UC at `needs-clarification` forever.
- **Reporting before verifying.** All nine checks pass silently when they pass — that's the point. The
  run that skips them is indistinguishable from the run that passes them, until a signal goes missing.
- **Reading check 9 as "the human hasn't answered yet".** Check the `A:` line, not the checkbox: an
  answer written without ticking the box is still an answer, and the row still has to re-enter.
- **Re-deriving or tidying `## Coverage Gaps` in the hub refresh.** It is not a derived table; erasing
  a real gap and inventing a wrong one are the same mistake, and deleting the empty section resets the
  feature to "never checked".
- **Reporting a coverage gap as if it blocked a UC.** It blocks the feature, not the artifact — a UC
  with zero open questions is still ready while its feature carries three gaps.
- **Changing a hub's `status:`.** It mirrors scope from `{requirements_file}`; overwriting it desyncs
  the registry with nothing to reconcile them.
- **Flipping an artifact off `needs-clarification` with a question still unchecked** — including one
  raised earlier in the same run and forgotten.
