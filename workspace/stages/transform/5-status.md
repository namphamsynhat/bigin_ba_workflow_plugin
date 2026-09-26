# Stage 5 — Status, verification, and report

```text
runs: orchestrator, LAST
in:   every artifact this run touched
out:  every status set from a LIVE RE-COUNT · hubs refreshed · checks run · the report
never: a status decided in Stages 1-4 — they write content and leave status alone
```

`BIN="${CLAUDE_PLUGIN_ROOT}/bin/bigin"`. A status decided mid-stage and left stale by a later edit is this
vault's most common drift — so a program re-counts it, last.

## Part 1 — Set every status from a live re-count

```text
$BIN status          # every UC/BR: unchecked "- [ ] Q:" in a UC's § 5 Still open (never the Decision log)
                     # or a BR's ## Open Questions → needs-clarification; none → draft
```

It only ever moves between `draft` and `needs-clarification`. `approved`, `removed`, `enriched`,
`consolidated` are never touched — and never written by this skill (`in-review`/`superseded` are retired on
a UC/BR). **An approved UC whose § 2 changed stays `approved`**: the engine's Changelog line `§ 2 changed —
flagged for review` is what sends it back through `/approve-uc`. List every flagged UC in the report.

## Part 2 — Refresh the hubs, don't restate them

```text
$BIN hub refresh <every touched slug, and every slug a touched cross-feature UC names>
```

Readiness (one row per artifact: Ready = status ≠ needs-clarification ∧ 0 open questions ∧ nothing
pending in the ledger or a legacy ## Discussion), `uc:` + `## Use Cases`, and the add-only Gates mirror
(including every `open`/`answered` Coverage Gaps row) are all derived here. The orchestrator adds only one
`## Notes / History` bullet per touched hub. **Leave `## Coverage Gaps` itself alone** (Stage 4 Part 4 owns
it) and **never change the hub's `status:`** — it mirrors the `{requirements_file}` scope state.

## Part 3 — Verify before reporting

```text
$BIN lint --full                      # exit 1 → its findings ARE mismatches: blocking, repair, re-run
$BIN coverage --stage transform       # every traced unit reaches a UC/BR, or is parked on a question
                                      # (codebase vaults: --id-pattern from project.md coverage_id_pattern)
$BIN run summary $RUN                 # dispatched vs landed
```

The binary unavailable, `python3` missing, or the command denied → **say so** and do the checks by hand.
Never treat an unavailable checker as a pass.

| # | Check | Who |
| :--- | :--- | :--- |
| 1 | every `staged` row has something pending behind it — an open ledger entry, a drift question on the artifact citing the row, or (legacy) a `## Discussion` entry | lint |
| 2 | every `applied` row's content is findable at the id its `Destination` names, or it carries a pointer explaining why no change was needed | **you** — "would the text satisfy a tester checking this signal" is judgment |
| 3 | no Signal Log row renumbered, deleted, un-merged, or had its `Signal`/`Source` rewritten (except a Gate 3 refresh noted `refreshed from <INT-###>`) | **you** |
| 4 | every question raised exists once on the artifact named and duplicates none already open on the source `INT` note | lint (exists) + **you** (duplicates) |
| 5 | each artifact's `status` matches its live open-question count | lint (after `bigin status`) |
| 6 | no `S#`/`A#`/`E#` reused or renumbered; every branch/enforcement point resolves to a live step | engine (never renumbers) + lint |
| 7 | every slug in a UC's `features:` lists it in `uc:` and `## Use Cases`, and no hub claims a UC that doesn't name it | lint (after `hub refresh`) |
| 8 | no two files share a `UC-###`/`BR-###` id | lint (the engine's id lock prevents it) |
| 9 | no `conflict`/`question` row whose linked question carries a filled `A:` — Stage 1 should have re-entered it | **you** |

A mismatch is **blocking**: repair (through the engine) and re-check rather than report a count the vault
doesn't support. Coverage gaps are deliberately not a check — they are a judgment, made in Stage 4 Part 4.

## Part 4 — Report

```text
Stage 1 (release): <N> released · <N> superseded · <N> need judgement · <N> waiting
                   <N> re-entered — <slug> #<n>: <the decision that unblocked it>   # 1-foldin § Re-entry
                   <N> legacy entries migrated (discussion-to-ledger), <N> unparsed left for a human
Stage 2 (qualify): <N> qualified, <N> held (<reason>), <N> applied as duplicate/already-covered
Stage 3 (route):   <N> UC minted, <N> updated, <N> BR created, <N> BR updated — <slug>: UC-### (status)
                   design: <N> directive(s) — <slug> ## Design Directives, <N> DESIGN-PRINCIPLES row(s)
Stage 4 (apply):   <N> applied · <N> already · <N> gated · <N> drift · <N> invalid
                   <N> flagged for review (§ 2 changed): UC-###, … · <N> conflict(s) · <N> adjudicated
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
