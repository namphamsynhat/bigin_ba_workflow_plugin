# Stage 1 — Resumable fold-in

**Runs in the orchestrator, first, every invocation.** Stage 1 before Stage 2 is what makes a rerun
useful: it harvests answers a human has written since the last run before anything new gets staged.
A run that starts by drafting instead re-asks questions that are already answered on disk.

Variables resolve against `_bigin/conventions/paths.md`. The full checkpoint rationale is
`_bigin/conventions/conventions.md` § Resumable unattended apply — read it once if you're unsure why the
write order below is what it is; the procedure here is complete on its own.

## What's in scope

Every FR/BR this skill has ever staged a change on. Find them by scanning `{fr_dir}` and `{br_dir}` for
an artifact whose feature has a Signal Log row with `Status: staged` pointing at it.

An FR/BR with no `staged` row pointing at it is not this stage's business, whatever its status.

## The three-way read

For each candidate, decide which of three states it's in — a bare "is the box ticked?" check can't tell
(b) from a half-applied (c) on a resumed run:

| State | How to tell | Do |
| :--- | :--- | :--- |
| **(a) Genuinely unanswered** | the `A:` line is still blank | Nothing. Wait for a human. Not eligible. |
| **(b) Already applied** | the artifact's `## Changelog` already cites this fold-in's `INT-###` | Write nothing to the artifact — this run is a retry of a completed apply. Still do § Reconcile mirrors. |
| **(c) Answered, not yet applied** | neither of the above | Apply it: § The atomic write, then § Reconcile mirrors. |

## The atomic write

Compose the **entire** change first, then write the file **once**:

1. Fold the `## Discussion` entry into `## Functional requirements` (FR) or the rule statement (BR).
2. Tick the resolved `- [ ] Q:` line in `## Open Questions` — only if it's genuinely resolved. An answer
   that still needs a client round-trip stays unchecked.
3. Bump `version`.
4. Append the `## Changelog` line, citing the `INT-###`.
5. Leave `status` for Stage 5 (`5-status.md`) — it is set last, from a live re-count, never here.

**One write, not five.** Before that single write lands, nothing has changed on disk, so a mid-run kill
leaves the artifact exactly as it was and correctly still eligible for the next run. After it lands the
fold-in is done, and everything downstream is a re-derivable mirror.

Never re-append a `## Changelog` or `## Discussion` line because this run started before checking
state (b).

## Reconcile mirrors — unconditionally, every run

Mirrors are read from the artifact's *current* state and corrected to match. Setting an already-correct
field again is a no-op, not a duplicate — so this step needs no resume logic of its own. **Run it for
(b) as well as (c);** never skip it because the three-way read said "already done." A prior run killed
between the artifact write and the hub refresh is exactly what this repairs.

1. **The hub's Signal Log row** → `applied`, if the artifact now shows the fold-in.
2. **The source `INT` note's `## Open Questions` copy** → ticked, if the artifact's copy is already
   resolved. One question, two places — never two questions (`conventions.md` § Intake capture).
3. **`{requirements_file}`**, if the fold-in changed anything a row there mirrors.

Never renumber, delete, or rewrite the `Signal`/`Source` text of a Signal Log row.

## Hand-off to Stage 2

Report per artifact: `<slug>: FR-### | BR-### — folded in (INT-###) | already applied, mirrors
reconciled | waiting on a human`. Stage 2 collects `new`/`held` rows and never re-collects a row this
stage just set to `applied`.

## Failure modes

- **Skipping the mirror reconcile on state (b).** The artifact is right and the hub still reads
  `staged`, so a future run re-collects a signal that's already folded in — or worse, reads as pending
  forever with nothing staged anywhere.
- **Writing the artifact in several passes.** A kill between passes leaves a fold-in half-applied with
  no way to tell it from "not started."
- **Setting `status` here.** Stage 5 re-counts and sets it. A status decided in Stage 1 and left stale
  by a Stage 3 edit to the same artifact is this vault's most common drift.
- **Ticking a box to make the count zero.** An answer that doesn't actually resolve the question stays
  unchecked, and the artifact stays `needs-clarification`.
