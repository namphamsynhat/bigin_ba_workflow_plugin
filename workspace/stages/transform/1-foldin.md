# Stage 1 — Resumable fold-in

```text
runs: orchestrator, FIRST, every invocation
in:   every UC/BR whose feature has a `staged` Signal Log row pointing at it
out:  the staged change folded into the artifact · mirrors reconciled
never: status — Stage 5 sets it, from a live re-count
```

Stage 1 before Stage 2 is what makes a rerun useful: it harvests answers a human wrote since the last
run before anything new gets staged. A run that starts by drafting re-asks questions already answered
on disk.

`{variable}` resolves in `_bigin/conventions/paths.md`. Full checkpoint rationale:
`_bigin/conventions/conventions.md` § Resumable unattended apply — the procedure here is complete on
its own.

A UC/BR with no `staged` row pointing at it is not this stage's business, whatever its status.

## The three-way read

A bare "is the box ticked?" check can't tell (b) from a half-applied (c) on a resumed run.

| State | How to tell | Do |
| :--- | :--- | :--- |
| **(a) unanswered** | the `A:` line is still blank | nothing — wait for a human |
| **(b) already applied** | `## Changelog` already cites this fold-in's `INT-###` | write nothing to the artifact — this is a retry. **Still run § Reconcile mirrors.** |
| **(c) answered, not applied** | neither of the above | § The atomic write, then § Reconcile mirrors |

## The atomic write

```text
compose the ENTIRE change first, then write the file ONCE:
1  fold the ## Discussion entry into the section its `proposed:` line names
       a numbered UC section (## 1-## 6, § Folding into a UC) or a BR's rule statement
2  move the resolved question out of ## 5 Still open into the Decision log table
       topic · who raised it and what they said · the decision · the date
       an answer still needing a client round-trip STAYS an unchecked "- [ ] Q:"
3  bump version
4  append the ## Changelog line, citing the INT-###
5  leave status alone                                                    # Stage 5 owns it
```

**One write, not five.** Before it lands nothing has changed on disk, so a mid-run kill leaves the
artifact exactly as it was and correctly still eligible next run. After it lands the fold-in is done,
and everything downstream is a re-derivable mirror.

Never re-append a `## Changelog` or `## Discussion` line because this run started before checking (b).

## Folding into a UC

A main-flow step (`new step ...`, `S# becomes:`, `S# is removed because ...`) or a flow (`new flow
A#/E#:`, `A#/E# becomes:`, `A#/E# is removed because ...`) is never this stage's job. Stage 4 Part 2
(`4-sync.md`) is the only place that ever applies them, and it sweeps EVERY in-scope UC's own
`## Discussion` on EVERY invocation — not just what this run staged — so an entry like this should
never survive to a second run. If one is still sitting in `## Discussion` when this stage reads it,
leave it alone: it is Stage 4's worklist, not this stage's, and Part 2 later in this same run will
pick it up regardless of whether Stage 1 or Stage 3 touched this UC at all.

```text
when folding in a ## 4 enforcement point → check the S#/A#/E# it names still exists on § 2/§ 3 as
                        they stand on disk right now, and isn't marked removed
    a rule enforced at an already-removed step, or citing an id that was never minted, is a real
    inconsistency
    → fold in the rule mirror anyway, then raise ONE question naming both
    → NEVER silently re-point a citation at a neighbouring step
```

`## 4` rows fold in as **mirror updates only** — the rule statement comes from the `BR-###` file; this
stage copies its current text plus the staged enforcement point.

## Reconcile mirrors — unconditionally, every run

Mirrors are read from the artifact's *current* state and corrected to match. Setting an already-correct
field again is a no-op, so this step needs no resume logic. **Run it for (b) as well as (c)** — a prior
run killed between the artifact write and the hub refresh is exactly what this repairs.

```text
1  the hub's Signal Log row        → `applied`, if the artifact now shows the fold-in
2  EVERY participating hub         → the ## Use Cases pointer + `uc:` frontmatter on EACH slug in
                                     the UC's features:
                                     → a UC on only its primary_feature reads as complete while the
                                       other features have no idea they're part of it
3  the source INT's ## Open Questions copy → ticked, if the artifact's copy is resolved
                                     → one question, TWO PLACES — never two questions
4  {requirements_file}             → if the fold-in changed anything a row there mirrors
```

Never renumber, delete, or rewrite the `Signal`/`Source` text of a Signal Log row.

## Hand-off

Report per artifact: `<slug>: UC-### | BR-### — folded in (INT-###) | already applied, mirrors
reconciled | waiting on a human`. Stage 2 never re-collects a row this stage just set to `applied`.

## Failure modes

- **Renumbering steps.** Every `S#` is cited from a branch point, a rule, a story, a prototype screen.
- **Deleting a removed step's row.** Every citation of that id becomes a dead reference.
- **Skipping the mirror reconcile on state (b).** The hub reads `staged` forever with nothing staged.
- **Reconciling only the primary hub.** A cross-feature UC's other hubs silently drift.
- **Writing the artifact in several passes.** A kill between passes is indistinguishable from "not
  started".
- **Setting `status` here.** Stage 3 may edit the same artifact after; Stage 5 re-counts.
- **Ticking a box to make the count zero.** An answer that doesn't resolve the question stays unchecked.
