---
name: extract-signal
description: This skill should be used when the ask is to extract signals, process the intake queue, drain 00-Inbox, or map intake to features. This skill will drain the raw intake queue in 00-Inbox — extract each INT-### note's signals into a flat raw record on the note, audit that record against the source in both directions, then anchor every signal to a FEATURES.md slug and file it onto that feature's Signal Log grouped by functional theme. A signal that can't be anchored raises a written question on the note instead of a guess, parking it needs-clarification until a human supplies the slug. Never drafts or edits an FR — that's a later step.
argument-hint: "[resume]"
disallowed-tools: AskUserQuestion
---

# Extract Signal

`/bigin-intake` fills `00-Inbox` with verbatim `INT-###` notes. This skill drains that queue: per
eligible note, extract signals into its `## Extracted signals` table, audit that table against the source,
then anchor each signal to a feature and file it onto that feature's hub. An unanchorable signal becomes a
written question, never a guess.

**Recall is what this skill is for.** Every later stage reads the note's table instead of the source —
`/bigin-transform-signal` never re-opens `## Raw`. A signal that doesn't land in the table is not a
missed signal, it is a requirement that never existed, and nothing downstream can detect it. A wrong row
is caught in review; a missing one is invisible forever. Every design choice below follows from that
asymmetry, and § Why the pipeline has this shape records the ones that look like extra cost.

The two tables it writes are deliberately different shapes. The note's `## Extracted signals` is the
**raw record** — one flat row per signal, arrival order, never grouped. The hub's `## Signal Log` is the
**working register** — the same signals grouped by functional theme, one row per theme (§ Themed hub
rows). Row counts between the two won't match, and shouldn't.

Never touches an FR — only a hub's Signal Log, plus the vault-wide registers a signal populates directly.
Folding a filed signal into a requirement is a later step.

The vault is the only state, so `resume` just means running again — every run rescans `{inbox_dir}` fresh.

## Paths

- `{inbox_dir}`: `00-Inbox` — skip `_attachments/` when scanning.
- `{requirements_file}`: `01-Requirements/FEATURES.md` — the slug registry; a signal can only anchor to a slug listed here.
- `{hub_dir}`: `01-Requirements/_features` — one hub file per slug, `{hub_dir}/<slug>.md`.
- `{uc_dir}`: `01-Requirements/_ucs` — read only, to collect open questions (§ Step 1).
- `{conventions_reference}`: `_bigin/conventions/conventions.md` — the rulebook: ID scheme, frontmatter schema, artifact conventions.
- `{extraction_rules}`: `_bigin/stages/extract/2-extraction.md` — signal catalog, segmentation, `Why` discipline. The **extraction** subagent's only rulebook.
- `{filing_rules}`: `_bigin/stages/extract/3-filing.md` — anchoring, hub schema, themed consolidation, registers, questions, status. The **filing** subagent's only rulebook.
- `{conventions_file}`: `.claude/bigin-ba-workflow-plugin.local.md` — optional project overrides. A plugin setting, not project data, hence `.claude/`.
- `{pain_points_file}`: `01-Requirements/PAIN-POINTS.md` — canonical `PP-###` register; each hub mirrors its own rows from here.
- `{entities_file}`: `01-Requirements/ENTITIES.md` — candidate `EN-###` rows; no hub mirror.
- `{design_principles_file}`: `01-Requirements/DESIGN-PRINCIPLES.md` — durable cross-cutting constraints; no hub mirror.
- `{template_hub}` / `{template_pain_points}` / `{template_entities}` / `{template_design_principles}`: `_bigin/templates/{feature-hub,pain-points-register,entities-register,design-principles-register}.md`.

All project-relative, materialized by `/bigin-new-project`. Confirm `{extraction_rules}`, `{filing_rules}`,
and `{conventions_reference}` exist before building the queue — if any is missing, stop and say
`/bigin-new-project` must run first. A subagent that can't read its rules doesn't fail loudly; it
improvises and reports success.

## Step 1 — Build the queue

### Step 1.1 - get the int list

Scan `{inbox_dir}` for `INT-###` notes and read each frontmatter:

- `kind: info` → skip. Operational/admin capture, never refined into signals.
- `status: raw` → eligible, fresh run.
- `status: needs-clarification` with **at least one** `- [ ] Q:` box newly checked → eligible as a
  **partial fold-in**. Harvest the answered questions, leave the unanswered ones parked. Waiting for every
  box strands the answered ones behind the slowest question on the page.
- `status: needs-clarification`, nothing newly answered → still waiting on a human.
- Any other `status` (`in-review`, `consumed`, …) → already processed, skip.

### Step 1.2 - Collect open questions

Scan `{uc_dir}` and `{inbox_dir}` once for every unchecked `- [ ] Q:` line — on a use case that list is
its `## 5` **Still open** section — then pass the list to each
extraction subagent. This is what lets a statement that resolves someone else's question get typed
`answer` and cited, instead of landing as a generic requirement or being dropped as restated context.

- **≤ 40 open questions:** pass the full list.
- **> 40:** scope it down to `{inbox_dir}`'s questions plus `{uc_dir}` questions for features in the
  note's `declared_features` — cuts context noise without dropping anything the batch could resolve.

### Step 1.3 - Next or Stop
Empty queue: say so and stop. Otherwise, report the full list and continue to `§ Step 2`

## Step 2 — Process the queue, one note at a time

Batches of **5**, reporting after each (§ Step 4) before the next. Within a batch, process notes
**sequentially, never in parallel** — two notes can anchor to the same feature, and parallel edits to one
hub file race.

Each note runs three subagents in a fixed order, each fresh (never reuse a prior note's subagent, which
grows its context instead of resetting it). Prompts for all of them are in
`references/agent-dispatch.md` — use them verbatim rather than re-deriving their shape.

### 2a — Extract (session default model, or `sonnet`)

One `Agent`, `general-purpose`, foreground. Reads the note's `## Raw` and `{extraction_rules}`. Writes
one flat row per discrete signal into `## Extracted signals`, filling `#`/`Type`/`Signal`/`Why`/`Source`
and **leaving `Feature`/`Status`/`Notes` blank** — anchoring hasn't happened yet.

It **segments the source first** and reports rows per segment. A single pass over a long transcript
captures each topic's throughline and drops the one-line asides inside it; segmenting is what makes that
loss visible instead of silent. A segment with zero rows is a claim, not a gap in the report.

This subagent is never told about themes, hubs, or consolidation. An extractor that knows its rows will
be grouped downstream starts pre-grouping them here, and the raw record is the one place where that is
unrecoverable.

### 2b — Audit the record against the source (`sonnet`)

One `Agent`, `general-purpose`, foreground. The only place in the plugin where the table is checked
against the raw material it claims, and it runs in **both directions**:

- **Source → rows (recall).** Reads `## Raw` only — locate the section's line range with `grep -n` and
  `Read` that range, so the existing table stays out of context — and independently lists every discrete
  claim it finds, with a quote. **This list is written before the table is opened.** An agent that reads
  the table first confirms it instead of auditing it.
- **Rows → source (fidelity).** Then opens the table and reports both a row with no locatable quote and a
  claim in the source with no row.

The orchestrator diffs the two, appends the gap rows to the table from the audit's own quotes (no
re-reading the source), and corrects or downgrades unsupported rows. The note's table ends up as the
**union of two independent passes** over the same source — that union is where the recall gain comes
from. Repair rules: `references/agent-dispatch.md` § Repairing the table.

Nothing is filed to a hub until this step is clean, so a bad row is corrected in the table rather than
surgically removed from a themed hub row later.

### 2c — File (`haiku`)

One `Agent`, `general-purpose`, foreground. Reads the finished table plus `{filing_rules}` and
`{requirements_file}` — **never `## Raw`**. Fills `Feature`/`Status`/`Notes`, groups the anchored rows per
feature by functional theme, appends one row per theme to `{hub_dir}/<slug>.md`'s `## Signal Log`, mirrors
registers per signal, raises questions for what won't anchor, and sets the note's `status` — but only
after confirming every hub write is on disk. A flip to `in-review` drops the note from every future scan,
so an unwritten row would vanish silently.

**A signal revealing a genuinely new feature does not mint its own `{requirements_file}` row.** The
subagent raises the question and stops (§ The feature-mapping loop). A slug is permanent and everything
downstream anchors to it, so it's a human's call — and this skill has no `AskUserQuestion` to make it any
other way.

## Step 3 — Verify the filing

After each batch, one `Agent` (`haiku`, `general-purpose`, foreground) checks the batch's own claims. Per
note and per slug reported, confirm:

- `{hub_dir}/<slug>.md`'s `## Signal Log` cites that `INT-###`.
- **Every anchored row number in the note's table appears in exactly one hub row's `Source` cite** — none
  missing, none cited twice.
- The note's `status` matches its `## Open Questions` state.

Row counts are *not* the check: a themed row covers several note rows by design, so counting hub rows
against note rows would flag every correct consolidation and miss the one thing that actually goes wrong,
a signal dropped inside a merge.

Any mismatch is blocking: dispatch one targeted repair subagent to file the uncited row(s) from the
already-extracted table onto the correct hub (no re-extraction), then re-check that note. A note reporting
success while missing its hub row is stranded, not done.

## Step 4 — Report

```text
processed: N notes
coverage: INT-###: M segments, N rows (segments with 0 rows: <list, or none>)
          field tables: <N fields → N rows, or none>
audit: INT-###: N claims found in source, N gaps appended, N rows narrowed, N downgraded to question
signals filed: total — per feature, e.g. <slug>: N signals in M themed rows (Signal Log rows #a-#b)
parked — awaiting an answer: INT-### (N question(s) unanswered)
parked — awaiting a feature mapping: INT-### (signal(s) unresolved — human writes the slug into the A: line)
verification: clean | repaired (list what)
remaining in queue: N — re-run this skill to continue
```

The `coverage` and `audit` lines are the point of the report, not decoration: they are the only place
under-extraction is ever visible. A run whose audit appended gaps was a run that would otherwise have lost
those requirements — say so plainly rather than folding it into "clean".

## Themed hub rows

A hub row answers "what did this note tell us about this feature?", not "what was signal #4?". So the
signals a note contributes to one feature are filed **grouped by functional theme** — one row per theme,
carrying every member's detail as its own clause.

The test for a theme is *would a drafter write these into one requirement statement?* Three signals
reading "age is computed from date of birth", "the cut-off is 1 September", and "under-18s need guardian
consent" are one theme — *age eligibility* — and become one row. Two signals about two different screens
are two themes, however adjacent they were in the transcript. Adjacency isn't a theme; sharing a slug
isn't a theme; a theme of one is normal and needs no forcing.

```text
note INT-014 ## Extracted signals — the raw record, still three flat rows:
  #3 requirement  age is computed from date of birth
  #5 decision     the cut-off is 1 September
  #7 constraint   under-18s need guardian consent

hub enrolment-eligibility ## Signal Log — one themed row:
| # | Signal | Type | Source | Status | Destination | Notes |
| 7 | **Age eligibility** — age is computed from date of birth; the cut-off is 1 September; under-18s need guardian consent | requirement + constraint + decision | INT-014 #3, #5, #7 — Jane Doe 2026-08-05 | new | | |
```

The `Source` cite's row numbers are what makes this followable — they're the traceability that replaces
one-row-per-signal, and Step 3 verifies every anchored note row appears in exactly one of them.

Four things never merge — full rules in `{filing_rules}` § Consolidating into themed hub rows:

- **Different notes or runs.** The log is append-only; a continuing theme cites the older row as
  `Notes: extends #<n>`.
- **Different `Status`.** Only `new` rows consolidate.
- **Presentation vs. behavioural.** Different lanes, and the design lane skips the approval gate.
- **Contradicting signals.** That's a `conflict`, not a merge.

Over-merging is the failure mode to watch. A row that reads like one ask but hides four is worse than a
long log — the detail a drafter needs is still on the page but no longer legible as separate obligations.

## The feature-mapping loop

A signal matching no `{requirements_file}` slug is never guessed onto one — it becomes a question on the
`INT` note (owner: team, tagged `needs-review`), and the note flips to `needs-clarification`. Wording
depends on why the match failed (`{filing_rules}` § Anchoring a signal to a feature):

- **Ambiguous among existing slugs:** the question asks which one.
- **Nothing fits:** the question ships with a **drafted slug and one-line scope** for a possible new
  feature — a proposal to confirm or edit, not a blank line to fill.

Either way, a human resolves it by writing the slug into the `A:` line — minting a `proposed` row first if
the scope is genuinely new, using the draft as a starting point rather than accepting it verbatim — and
ticking the box. The next run folds the note in and anchors it properly. No separate command, no
re-extraction of what was already correct.

## Additional resources

Paths and templates are in § Paths. **`references/agent-dispatch.md`** holds the four subagent prompts
(extraction, source audit, filing, batch verification), the table-repair procedure the orchestrator runs
on an audit finding, and the hub-repair procedure for a Step 3 mismatch.
