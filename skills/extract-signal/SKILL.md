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
| `{audit_rules}` | `_bigin/stages/extract/2b-audit.md` | the **source-audit** subagent's only rulebook, plus the table-repair procedure |
| `{filing_rules}` | `_bigin/stages/extract/3-filing.md` | the **filing** subagent's only rulebook |
| `{conventions_file}` | `.agents/bigin-ba-workflow-plugin.local.md` (or `.claude/bigin-ba-workflow-plugin.local.md`) | optional project overrides |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | canonical `PP-###`; each hub mirrors its own rows |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | candidate `EN-###`; no hub mirror |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | cross-cutting constraints; no hub mirror |
| `{template_*}` | `_bigin/templates/*` | `feature-hub`, `pain-points-register`, `entities-register`, `design-principles-register` |

Project-relative, materialized by `/bigin-new-project`. Missing `{extraction_rules}`, `{audit_rules}`,
`{filing_rules}`, or `{conventions_reference}` → stop, say `/bigin-new-project` must run first. A subagent
that can't read its rules improvises and reports success.

Then run `{conventions_reference}` § Workspace version check — one `Grep` of `_bigin/system/project.md`
against the installed plugin's version. Behind → warn and recommend `/bigin-upgrade-project`; **ahead →
stop**: the materialized rulebook this run would follow is older than the one the vault was built
against, and filing against an older contract is how a stage silently regresses.

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

**Dispatch the named agents** — `signal-extractor`, `signal-auditor`, `signal-repairer`, `signal-filer`,
`signal-batch-verifier` — never a bare `general-purpose` agent. Each pins its own model and tool set in
its frontmatter, and each reads its own rulebook from `_bigin/`. Every subagent is fresh: reuse grows
context instead of resetting it.

**`references/agent-dispatch.md` carries the per-run data to hand each one, and nothing else.** Do not
paste a procedure into a prompt — that is how two copies of one rule drift apart, and a dispatch-prompt
copy also overrides a project's own `_bigin/` override of that rule.

```text
for batch in chunks(queue, 5):

  # ---- per-note, nothing shared: run these CONCURRENTLY across the batch, <= 4 at a time ----
  for note in batch, in parallel:

    2a  Agent(signal-extractor)                                  [dispatch § 2a]
        reads   every SRC block in note.sources · {extraction_rules}
        writes  ## Extracted signals — # · Type · Signal · Why · Source
                Feature and Status left blank
        if any SRC block unread        → re-spawn scoped to that block
        if why "not stated" > 30% of requirement/feedback rows
                                       → re-spawn scoped to those rows

    2b  Agent(signal-auditor)                                    [dispatch § 2b]
        reads   ## Raw by line range FIRST (table unseen), then the table · {audit_rules}
        writes  a two-direction gap report — repairs nothing
        SKIPPABLE: ## Raw under ~100 lines, ONE block, kind != transcript, no `derived` row
                   → orchestrator checks inline instead, reported as "audit: inline"
                   → NEVER skip on a transcript, however short  [{audit_rules} § When this pass
                     may be skipped]

    2b-repair  Agent(signal-repairer), only if 2b found something [dispatch § 2b-repair]
        handed  the audit report VERBATIM — it never re-reads the source
        writes  the table repairs: gap → append · overreach → narrow · inversion → re-type + add
                the ask · bad cite → fix · no support → question · contradiction → conflict pair
        → repair touched > 2 rows → RE-AUDIT those rows, scoped, before filing
        → NOT done in the orchestrator: that pulls every table and audit report into the one
          context this whole fan-out exists to keep small

  # ---- shared writes: SEQUENTIAL, one note at a time ----
  for note in batch, in order:

    2c  Agent(signal-filer)                                      [dispatch § 2c]
        reads   the repaired table · {filing_rules} · {requirements_file}    # never ## Raw
        writes  Feature · Status · Notes · themed hub rows · registers
                · questions · a resolving tick on an earlier note's question (§ Step 5b)
                · this note's status LAST
        → sequential because hubs and the three registers are shared: two concurrent notes
          appending to one hub lose a row

  3a  ORCHESTRATOR: python3 "${CLAUDE_PLUGIN_ROOT}/hooks/bigin-lint.py" --full
      the mechanical half of the batch check, for free and without judgment: table shape, cite
      resolution, illegal status values, note rows cited by no hub row or cited twice on one hub
      exit 1 → its findings are blocking, same as the verifier's
      unavailable (no python3, path won't resolve, command denied) → SAY SO and let 3b cover it all;
      never read an unavailable checker as a pass
  3b  Agent(signal-batch-verifier), one per batch                [dispatch § 3]
      the half a program can't do: does this note's status match what was reported, is every
      question actually mirrored where a human will see it, is a themed Signal cell really carrying
      a clause per number it cites, was the rationale question batched
      mismatch → blocking; dispatch signal-repairer in hub-repair mode, re-check, then move on
  4   report(batch)                                              # before the next batch starts
```

**Why 2a/2b parallelize and 2c does not.** 2a and 2b touch exactly one file each — that note's own
table. The shared-write hazard the old sequential loop guarded against lives entirely in 2c, where hubs
and the vault-wide registers are appended to. Serializing whole notes to protect 2c costs the wall-clock
of the entire chain per note and protects nothing extra.

## Rules

- **Recall is the point.** A wrong row dies in the audit; a missing row is invisible forever.
- **Classify before typing** — as-is · pain · to-be. A screen-share of the old system is a `decision`,
  not a `requirement`. Classifying changes a row's `Type`, never whether it gets written.
- **Never guess an anchor.** No matching slug → a written question, never the closest slug.
- **Never mint a feature slug from your own reading.** Permanent, everything downstream anchors to it — a
  human's call, which is why this skill has no `AskUserQuestion`. **One exception**, and only one: a slug
  the human themselves typed into `declared_features:` at capture, which has no `{requirements_file}` row
  yet, gets a `proposed` row added and reported (`{filing_rules}` § The declared-slug exception). That
  isn't the agent deciding scope; it is recording a decision a human already made.
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
- **Row numbers on a note's table are permanent ids.** A re-extraction or a repair corrects a row in
  place, supersedes it with a new row, or appends — it never renumbers. Hub `Source` cites point at these
  numbers, and a renumber re-points every one of them at a different claim without breaking anything
  visibly (`{extraction_rules}` § Row numbers are permanent ids).
- **An answer folds back to the note that asked.** When a row of this note resolves a question raised on
  a hub or an earlier note, 2c ticks **both** copies and cites this note. Otherwise the earlier note sits
  `needs-clarification` forever with an unticked box, reading as blocking when it isn't
  (`{filing_rules}` § Step 5b).
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
audit:     INT-###: dispatched | inline (<N> lines, <kind>) — and, if repaired, re-audited (<rows>) | not
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
checks every anchored row appears in exactly one hub row **per feature it anchored to**. A signal spanning
two features is filed to both hubs and cited once on each — that is the dual-anchor rule working, not a
duplicate.

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

- **`references/agent-dispatch.md`** — the per-run data to hand each of the five named agents, and the
  parallelism rule. Their procedures live in `_bigin/` (`{extraction_rules}`, `{audit_rules}`,
  `{filing_rules}`) or in the agent's own body — one home each, never a second copy here.
