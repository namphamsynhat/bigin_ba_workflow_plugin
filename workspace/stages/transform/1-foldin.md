# Stage 1 — Resumable fold-in

```text
runs: orchestrator, FIRST, every invocation
in:   every UC/BR whose feature has a `staged` Signal Log row pointing at it
      + every `conflict`/`question` row whose linked question has since been answered (§ Re-entry)
out:  the staged change folded into the artifact · mirrors reconciled · re-entered rows back to `new`
never: status — Stage 5 sets it, from a live re-count
```

Stage 1 before Stage 2 is what makes a rerun useful: it harvests answers a human wrote since the last
run before anything new gets staged. A run that starts by drafting re-asks questions already answered
on disk.

`{variable}` resolves in `_bigin/conventions/paths.md`. Full checkpoint rationale:
`_bigin/conventions/conventions.md` § Resumable unattended apply — the procedure here is complete on
its own.

A UC/BR with no `staged` row pointing at it is not this stage's business, whatever its status.

**Build the worklist grep-first, never by reading the vault.** `Grep` `{hub_dir}` for
`Status.*staged` and for `Status.*conflict|Status.*question`, and open only the hubs that hit; open only
the UC/BR ids those rows' `Destination` cells name. Reading every hub and every UC to discover that
nothing is pending makes "nothing to fold in" cost the whole vault, and that cost grows with every
append-only Signal Log row forever. Two greps and an early exit make the same answer a two-second one.

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

### The human may have edited the section first — two rules

A staged entry carries verbatim final text, and the human is explicitly invited to edit a UC directly
while reviewing it (`/approve-uc`). So the text an entry expects to replace can already be gone.

```text
BEFORE writing, compare the entry's anchor text against what is on disk RIGHT NOW:

content already present, verbatim (or semantically identical)
    → TREAT AS APPLIED: state (b). Remove the entry, append the Changelog line, reconcile mirrors.
      Do not write it a second time — a manual apply with no Changelog cite otherwise lands twice.

the anchor text MATERIALLY DIFFERS from what the entry expected to replace
    (`§ 1 Trigger becomes:` against a Trigger a human has since reworded; a `§ 4` row whose rule
     statement no longer matches)
    → DO NOT APPLY, and do not overwrite. Raise ONE question on the artifact naming both wordings
      and asking which stands, leave the entry in ## Discussion, and leave the row `staged`.
      Silently overwriting is how a reviewer's own correction disappears with no diff anyone reads.

a whitespace, punctuation, or capitalization difference is NOT material — apply normally
```

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
                                     → AND: if the answer arrived on a DIFFERENT, later note, tick
                                       the ORIGINATING note's box too and cite the resolving id
                                       ("resolved by INT-041"). A note whose question was answered
                                       elsewhere otherwise sits `needs-clarification` forever with
                                       an unticked box, and reads as still blocking when it isn't.
4  {requirements_file}             → if the fold-in changed anything a row there mirrors
```

Never renumber, delete, or rewrite the `Signal`/`Source` text of a Signal Log row.

**Delegating this step.** Items 1–2 are pure re-derivation from facts already decided, so they may be
handed to one `hub-bookkeeper` dispatch **per hub, sequentially** rather than run in the orchestrator's
own context — that agent's whole contract is mirroring decisions it is given (`agents/hub-bookkeeper.md`).
Never two hubs concurrently, and never delegate item 3 or 4: those touch `{inbox_dir}` and
`{requirements_file}`, which that agent must not write.

## Re-entry — an answered `conflict` or `question` row

The one silent-loss path this stage exists to close. A `conflict` row stages **nothing** by design
(`3-lane-uc.md` § Conflict); a `question` row never had a lane at all (`3-routing.md` § `Type` is a
hint). Neither is `staged`, so this stage's fold-in ignores both — and neither is `new`/`held`, so
Stage 2's worklist ignores them too. Without this section a qualified, recorded requirement is
permanently stranded the moment a human answers it.

```text
scan every in-scope hub for rows with Status: conflict or Status: question
per row, find the question it raised — the `- [ ] Q:` its Notes/Destination points at, on the UC's
    ## 5, the BR's ## Open Questions, or the source INT note

A: line still blank            → leave the row exactly as it is. Not this stage's business yet.
A: line filled (ticked or not) → RE-ENTER:
    1  flip the row: Status: new
       Notes: append "re-entered <date>: <the question>, answered on <artifact> — <A: in ≤10 words>"
       → keep every existing Note; the conflict history is the reason the answer means anything
    2  the LOSING side of a conflict, if the answer picked one: flip THAT row Status: superseded,
       Notes: "superseded by the decision on #<n>"
       → never rewrite either row's Signal text. History is append-only.
    3  a conflict pair whose answer names a THIRD option neither row proposed → both rows
       `superseded`, and the re-entered row is the one carrying the decision, with the answer's own
       wording in its Notes
    4  move the resolved question into the decision log, per § The atomic write step 2
```

Stage 2 then collects the row in its ordinary `new` worklist **this same run**, and Stage 3 drafts it.

- **Draft from the decision, never by copying the losing wording.** The answer is new content: "we
  decided the school approves, not the fund" is the requirement, not either original signal's text.
  A verbatim re-stage of whichever side lost is the failure this whole path exists to avoid.
- **An answer that resolves nothing is not an answer.** A reply restating the disagreement, or naming a
  further question, leaves the row `conflict` and the box unticked. Say so in the report.
- **Report every re-entry explicitly** — it is the one case where a row's `Status` moves backwards, and
  a reader who doesn't see it named will read it as a stage that lost track of its own bookkeeping.

## Hand-off

Report per artifact: `<slug>: UC-### | BR-### — folded in (INT-###) | already applied, mirrors
reconciled | waiting on a human | drift question raised (§ The human may have edited…)`, plus
`re-entered: <slug> #<n> — <the decision>` per row § Re-entry moved back to `new`. Stage 2 never
re-collects a row this stage just set to `applied`; it always collects one this stage just set to `new`.

## Failure modes

- **Renumbering steps.** Every `S#` is cited from a branch point, a rule, a story, a prototype screen.
- **Deleting a removed step's row.** Every citation of that id becomes a dead reference.
- **Skipping the mirror reconcile on state (b).** The hub reads `staged` forever with nothing staged.
- **Reconciling only the primary hub.** A cross-feature UC's other hubs silently drift.
- **Writing the artifact in several passes.** A kill between passes is indistinguishable from "not
  started".
- **Setting `status` here.** Stage 3 may edit the same artifact after; Stage 5 re-counts.
- **Ticking a box to make the count zero.** An answer that doesn't resolve the question stays unchecked.
- **Skipping § Re-entry because "nothing is staged on that feature".** A hub can carry a dozen answered
  `conflict`/`question` rows and zero `staged` ones. Those rows are the whole reason this section runs
  on its own scan rather than as a sub-step of the fold-in worklist.
- **Applying a staged entry over a section the human already edited.** The reviewer's wording vanishes
  with nothing in any diff a human reads — see § The human may have edited the section first.
