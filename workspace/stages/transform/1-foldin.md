# Stage 1 — Resumable fold-in

**Runs in the orchestrator, first, every invocation.** Stage 1 before Stage 2 is what makes a rerun
useful: it harvests answers a human has written since the last run before anything new gets staged.
A run that starts by drafting instead re-asks questions that are already answered on disk.

Variables resolve against `_bigin/conventions/paths.md`. The full checkpoint rationale is
`_bigin/conventions/conventions.md` § Resumable unattended apply — read it once if you're unsure why the
write order below is what it is; the procedure here is complete on its own.

## What's in scope

Every UC/BR this skill has ever staged a change on. Find them by scanning `{uc_dir}` and `{br_dir}` for
an artifact whose feature has a Signal Log row with `Status: staged` pointing at it.

A UC/BR with no `staged` row pointing at it is not this stage's business, whatever its status.

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

1. Fold the `## Discussion` entry into the section its `proposed:` line names — a numbered section of
   the UC (`## 1`–`## 6`, § Folding into a UC below), or a BR's rule statement.
2. Move the resolved question out of `## 5`'s **Still open** list into its **Decision log** table —
   topic, who raised it and what they said, the decision, the date. Only if it's genuinely resolved:
   an answer that still needs a client round-trip stays an unchecked `- [ ] Q:` line.
3. Bump `version`.
4. Append the `## Changelog` line, citing the `INT-###`.
5. Leave `status` for Stage 5 (`5-status.md`) — it is set last, from a live re-count, never here.

**One write, not five.** Before that single write lands, nothing has changed on disk, so a mid-run kill
leaves the artifact exactly as it was and correctly still eligible for the next run. After it lands the
fold-in is done, and everything downstream is a re-derivable mirror.

Never re-append a `## Changelog` or `## Discussion` line because this run started before checking
state (b).

## Folding into a UC

The staged entry names its destination (`3-lane-uc.md` § Staging a change). Four of them need care:

| `proposed:` says | Do |
| :--- | :--- |
| `new step after S4:` | **Mint the next unused `S#`** — one higher than the highest ever used in this UC, including ids whose rows are marked removed — and insert the row **after S4 in row order**. Never renumber the rows below it. |
| `S6 becomes:` | Replace that row's cells, keeping `S6`. |
| `S6 is removed because <reason>` | Keep the row and its id; mark it `**S6** *(removed v<version> — <reason>)*` with the cells struck through or emptied. Never delete the row: extensions, the `## 4` mirror, and downstream stories cite this id. |
| `new flow E2:` | Mint the next unused `E#`/`A#`, same discipline. Check its branch point `S#` still exists and isn't a removed row — if it is, that's a question, not a fold-in. |

After folding any step change, **re-check `## 4`'s enforcement points and `## 3`'s branch points**
against the ids that now exist. A rule enforced at a step that was just removed, or a flow branching
from one, is a real inconsistency: fold in the step change, then raise one question naming both. Never
silently re-point a citation at a neighbouring step.

`## 4` rows are folded in as mirror updates only — the rule statement comes from the `BR-###` file, and
this stage copies its current text plus the staged enforcement point.

## Reconcile mirrors — unconditionally, every run

Mirrors are read from the artifact's *current* state and corrected to match. Setting an already-correct
field again is a no-op, not a duplicate — so this step needs no resume logic of its own. **Run it for
(b) as well as (c);** never skip it because the three-way read said "already done." A prior run killed
between the artifact write and the hub refresh is exactly what this repairs.

1. **The hub's Signal Log row** → `applied`, if the artifact now shows the fold-in.
2. **Every participating hub**, for a UC whose `features:` lists more than one: the `## Use Cases`
   pointer and the `uc:` frontmatter list on *each* of them. A UC recorded on only its
   `primary_feature` reads as complete while the other features have no idea they're part of it.
3. **The source `INT` note's `## Open Questions` copy** → ticked, if the artifact's copy is already
   resolved. One question, two places — never two questions (`conventions.md` § Intake capture).
4. **`{requirements_file}`**, if the fold-in changed anything a row there mirrors.

Never renumber, delete, or rewrite the `Signal`/`Source` text of a Signal Log row.

## Hand-off to Stage 2

Report per artifact: `<slug>: UC-### | BR-### — folded in (INT-###) | already applied, mirrors
reconciled | waiting on a human`. Stage 2 collects `new`/`held` rows and never re-collects a row this
stage just set to `applied`.

## Failure modes

- **Renumbering steps to keep them sequential.** Every `S#` is cited from somewhere — an extension's
  branch point, a rule's enforcement point, a story, a prototype screen. Non-sequential ids are the
  design (`references/use-case-standard.md` § Deliberate departures).
- **Deleting a removed step's row.** The id stops resolving and every citation of it becomes a dead
  reference with no explanation.
- **Skipping the mirror reconcile on state (b).** The artifact is right and the hub still reads
  `staged`, so a future run re-collects a signal that's already folded in — or worse, reads as pending
  forever with nothing staged anywhere.
- **Reconciling only the primary feature's hub.** A cross-feature UC's other hubs silently drift.
- **Writing the artifact in several passes.** A kill between passes leaves a fold-in half-applied with
  no way to tell it from "not started."
- **Setting `status` here.** Stage 5 re-counts and sets it. A status decided in Stage 1 and left stale
  by a Stage 3 edit to the same artifact is this vault's most common drift.
- **Ticking a box to make the count zero.** An answer that doesn't actually resolve the question stays
  unchecked, and the artifact stays `needs-clarification`.
