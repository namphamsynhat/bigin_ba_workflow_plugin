---
name: extract-signal
description: This skill should be used when the ask is to extract signals, process the intake queue, drain 00-Inbox, or map intake to features. Drains the raw intake queue in 00-Inbox — extracts each INT-### note's signals into a flat raw record on the note, audits that record against the source in both directions, then anchors every signal to a FEATURES.md slug and files it onto that feature's Signal Log grouped by functional theme. A signal that can't be anchored raises a written question instead of a guess. Never drafts or edits a UC.
argument-hint: "[resume]"
disallowed-tools: AskUserQuestion
---

# Extract Signal

Per `INT-###` note in `00-Inbox`: extract signals from every source block → audit against the source →
anchor to a feature → file onto that feature's hub.

Extract stage of extract → transform → load. Never drafts or edits a UC or BR.

## Two tables, on purpose

| Table | Where | Shape |
|---|---|---|
| **Raw record** | the note's `## Extracted signals` | one flat row per signal, arrival order, never grouped |
| **Working register** | the hub's `## Signal Log` | the same signals grouped by theme, one row per theme |

Row counts won't match, and shouldn't. Every later stage reads the raw record; nothing re-opens `## Raw`.

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{inbox_dir}` | `00-Inbox` | intake notes — skip `_attachments/` when scanning |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | the slug registry; anchors resolve only to slugs listed here |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | one Feature Hub per slug |
| `{uc_dir}` | `01-Requirements/_ucs` | read-only — scanned for open questions (Stage 1) |
| `{conventions_reference}` | `_bigin/conventions/conventions.md` | ID scheme, frontmatter schema, artifact conventions |
| `{extraction_rules}` | `_bigin/stages/extract/2-extraction.md` | the **extraction** subagent's only rulebook |
| `{filing_rules}` | `_bigin/stages/extract/3-filing.md` | the **filing** subagent's only rulebook |
| `{conventions_file}` | `.agents/bigin-ba-workflow-plugin.local.md` (or `.claude/bigin-ba-workflow-plugin.local.md`) | optional project overrides |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | canonical `PP-###`; each hub mirrors its own rows |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | candidate `EN-###`; no hub mirror |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | cross-cutting constraints; no hub mirror |
| `{template_*}` | `_bigin/templates/*` | `feature-hub`, `pain-points-register`, `entities-register`, `design-principles-register` |

Project-relative, materialized by `/bigin-new-project`. Missing `{extraction_rules}`, `{filing_rules}`,
or `{conventions_reference}` → stop, say `/bigin-new-project` must run first. A subagent that can't read
its rules improvises and reports success.

## Stage 1 — Build the queue

```text
questions = every unchecked "- [ ] Q:" in {uc_dir} + {inbox_dir}   # on a UC: its ## 5 Still open
    if > 40 → keep {inbox_dir}'s, plus {uc_dir}'s for note.declared_features

enqueue(note, mode) = queue += { note, mode,
                                 sources:   note.raw_sources,   # ## Raw's ### SRC-n blocks, in order
                                 raw_lines: span of ## Raw }
queue = []
for note in {inbox_dir}/INT-*.md:                 # skip _attachments/
    read frontmatter ONLY
    kind == info                  → skip          # ops/admin, never refined
    status == raw                 → enqueue(fresh)
    status == needs-clarification → enqueue(fold-in) if any "- [ ] Q:" newly ticked
                                    else park     # still waiting on a human
    else                          → skip          # in-review, consumed

queue empty → say so, stop
else        → report(note · mode · sources · raw_lines), continue
```

- **Partial fold-in beats waiting** — holding for every box strands answers behind the slowest question.
- **`questions` is what makes `answer` typing possible** — without it, a statement resolving someone
  else's question files as a generic requirement.
- **`raw_sources` is the read plan.** Empty manifest but blocks visible in `## Raw` → older
  `/bigin-intake`; plan from the blocks, say so. Neither → the note is empty, not eligible.
- **`raw_lines` travels with the note** — past ~1500 lines 2a must page `## Raw` instead of reading it whole.

## Stage 2 — Process the queue

Prompts: **`references/agent-dispatch.md`**, verbatim. Every subagent fresh (`Agent`,
`general-purpose`, foreground) — reuse grows context instead of resetting it.

```text
for batch in chunks(queue, 5):
  for note in batch:                        # sequential — two notes can hit one hub, and edits race

    2a  spawn Agent(session default | sonnet) → extract          [dispatch § 2a]
        reads   every SRC block in note.sources · {extraction_rules}
        writes  ## Extracted signals — # · Type · Signal · Why · Source
                Feature and Status left blank
        if any SRC block unread        → re-spawn scoped to that block
        if why "not stated" > 30% of requirement/feedback rows
                                       → re-spawn scoped to those rows

    2b  spawn Agent(sonnet) → audit                              [dispatch § 2b]
        reads   ## Raw by line range FIRST (table unseen), then the table
        writes  a two-direction gap report — repairs nothing

        repair  orchestrator, from 2b's own quotes                [dispatch § Repairing the table]
                gap → append row · overreach → narrow · inversion → re-type + add the ask
                bad cite → fix · no support → question · contradiction → conflict pair

    2c  spawn Agent(sonnet) → file                               [dispatch § 2c]
        reads   the repaired table · {filing_rules} · {requirements_file}    # never ## Raw
        writes  Feature · Status · Notes · themed hub rows · registers
                · questions · the note's status LAST

  3   spawn Agent(haiku) → verify batch                          [dispatch § 3]
      per note+slug: hub cites this INT · every anchored row # cited in exactly one hub row
                     · status matches ## Open Questions
      mismatch → blocking; spawn a scoped repair, re-check, then move on
  4   report(batch)                                              # before the next batch starts
```

## Rules

- **Recall is the point.** A wrong row dies in the audit; a missing row is invisible forever.
- **Classify before typing** — as-is · pain · to-be. A screen-share of the old system is a `decision`,
  not a `requirement`. Classifying changes a row's `Type`, never whether it gets written.
- **Never guess an anchor.** No matching slug → a written question, never the closest slug.
- **Never mint a feature slug.** Permanent, everything downstream anchors to it — a human's call, which
  is why this skill has no `AskUserQuestion`.
- **Never touch a UC or BR.** Hub Signal Log plus the vault-wide registers, nothing else.
- **The extractor is blind to themes.** One that knows its rows get grouped starts pre-grouping — the
  raw record is the one place that's unrecoverable.
- **Audit before filing.** A bad row is corrected in the table, not cut out of a themed hub row later.
- **An unread block blocks the note.** The table looks complete, the audit checks only what the table
  cites, the hub shows signals filed — nothing downstream can see the gap.
- **2c anchors row by row, never by adjacency** — otherwise the tail of a long note lands on the wrong
  feature permanently. Report the `{requirements_file}` scope phrase matched for each row.
- **2c sets `status` last**, after confirming every hub write landed. `in-review` drops the note from
  every future scan.
- **Resume = re-run.** The vault is the only state; every run rescans `{inbox_dir}` fresh.

## Stage 3 — Report

```text
processed: N notes
sources:   INT-###: N/N blocks read (<kind × n>) — ## Raw N lines in N reads · unread: <what + why | none>
coverage:  INT-###: M segments, N rows (0-row segments: <list|none>) · field tables: <N fields → N rows|none>
mix:       INT-###: as-is N · pain N · to-be N · derived N · commitments N
           why: N of M stated (X% not stated) — <ok | re-ran 2a>
audit:     INT-###: N claims in source, N gaps appended, N narrowed, N inversions re-typed,
           N conflicts paired, N downgraded to question
filed:     <slug>: N signals in M themed rows (Signal Log #a-#b)
registers: PP minted <ids> · PP matched <ids> · entities N · design N
parked:    INT-### awaiting an answer (N open) · INT-### awaiting a feature mapping
verified:  clean | repaired (<what>)
remaining: N in queue — re-run to continue
```

These four lines are the only place quality is visible: `sources` catches a source nobody read ·
`coverage` under-extraction · `mix` mis-classification · `audit` fidelity. A run that appended gaps or
re-typed inversions is never folded into "clean".

## Themed hub rows

One hub row answers "what did this note say about this feature?", not "what was signal #4?".

Test: *would a drafter write these into one requirement statement?* Adjacency isn't a theme; sharing a
slug isn't a theme; a theme of one is normal.

```text
note INT-014 ## Extracted signals — flat, unchanged
  #3 requirement  age computed from date of birth
  #5 decision     cut-off is 1 September
  #7 constraint   under-18s need guardian consent

hub  enrolment-eligibility ## Signal Log — one row
| # | Signal | Type | Source | Status | Destination | Notes |
| 7 | **Age eligibility** — age computed from date of birth; cut-off is 1 September; under-18s need
  guardian consent | requirement + constraint + decision | INT-014 #3, #5, #7 — Jane Doe 2026-08-05 | new | | |
```

The `Source` row numbers are the traceability that replaces one-row-per-signal; Stage 2's verify pass
checks every anchored row appears in exactly one.

Never merge across: **different notes or runs** (cite the older row as `Notes: extends #<n>`) ·
**different `Status`** (only `new` consolidates) · **presentation vs behavioural** (different lanes) ·
**contradictions** (that's a `conflict`).

Over-merging is the failure mode: a row that reads like one ask but hides four. Full rules:
`{filing_rules}` § Step 2 — File to the Feature Hub.

## Feature-mapping loop

```text
no {requirements_file} slug matches
    → question on the INT note (owner: team, tag needs-review), status → needs-clarification
        ambiguous among existing slugs → ask which one
        nothing fits                   → ship a drafted slug + one-line scope to confirm or edit
    → human writes the slug into the A: line, ticks the box
    → next run folds it in and anchors properly       # no re-extraction, no separate command
```

## Additional resources

- **`references/agent-dispatch.md`** — the four subagent prompts (extraction, source audit, filing,
  batch verification), the table-repair procedure, and the hub-repair procedure.
