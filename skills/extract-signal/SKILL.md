---
name: extract-signal
description: Drain the raw intake queue in 00-Inbox — extract each INT-### note's signals into a flat raw record on the note, anchor every signal to a FEATURES.md slug, and file them onto that feature's Signal Log grouped by functional theme. A signal that can't be anchored raises a written question on the note instead of a guess, parking it needs-clarification until a human supplies the slug. Never drafts or edits an FR — that's a later step. Use when the ask is to extract signals, process the intake queue, drain 00-Inbox, or map intake to features.
argument-hint: "[resume]"
disallowed-tools: AskUserQuestion
---

# Extract Signal

`/bigin-intake` fills `00-Inbox` with verbatim `INT-###` notes. This skill drains that queue: per
eligible note, extract signals into its `## Extracted signals` table, then anchor each to a feature and
file it onto that feature's hub. An unanchorable signal becomes a written question, never a guess.

The two tables it writes are deliberately different shapes. The note's `## Extracted signals` is the
**raw record** — one flat row per signal, arrival order, never grouped. The hub's `## Signal Log` is the
**working register** — the same signals grouped by functional theme, one row per theme (§ Themed hub
rows). Row counts between the two won't match, and shouldn't.

Never touches an FR — only a hub's Signal Log, plus the vault-wide registers a signal populates
directly (§ Step 2). Folding a filed signal into a requirement is a later step.

The vault is the only state, so `resume` just means running again — every run rescans `{inbox_dir}`
fresh.

## Paths

- `{inbox_dir}`: `00-Inbox` — skip `_attachments/` when scanning.
- `{requirements_file}`: `01-Requirements/FEATURES.md` — the slug registry; a signal can only anchor to a slug listed here.
- `{hub_dir}`: `01-Requirements/_features` — one hub file per slug, `{hub_dir}/<slug>.md`.
- `{conventions_reference}`: `_bigin/conventions/conventions.md` — the rulebook: ID scheme, frontmatter schema, artifact conventions.
- `{extraction_rules}`: `_bigin/stages/extract/2-extraction.md` — signal catalog, anchoring rules, hub schema. Every subagent reads this.
- `{conventions_file}`: `.claude/bigin-ba-workflow-plugin.local.md` — optional project anchoring overrides. A plugin setting, not project data, hence `.claude/`.
- `{pain_points_file}`: `01-Requirements/PAIN-POINTS.md` — canonical `PP-###` register; each hub mirrors its own rows from here.
- `{entities_file}`: `01-Requirements/ENTITIES.md` — candidate `EN-###` rows; no hub mirror.
- `{design_principles_file}`: `01-Requirements/DESIGN-PRINCIPLES.md` — durable cross-cutting constraints; no hub mirror.
- `{template_hub}` / `{template_pain_points}` / `{template_entities}` / `{template_design_principles}`: `_bigin/templates/{feature-hub,pain-points-register,entities-register,design-principles-register}.md` — scaffold for each file above, used first time needed.

All project-relative, materialized by `/bigin-new-project`. Confirm `{extraction_rules}` and
`{conventions_reference}` exist before building the queue — if either is missing, stop and say
`/bigin-new-project` must run first. A subagent that can't read its rules doesn't fail loudly; it
improvises and reports success.

## Step 1 — Build the queue

Scan `{inbox_dir}` for `INT-###` notes and read each frontmatter:

- `kind: info` → skip. Operational/admin capture, never refined into signals.
- `status: raw` → eligible, fresh run.
- `status: needs-clarification`, every `- [ ] Q:` box now checked → eligible as a **fold-in** (a human answered or supplied a slug). Any box unchecked → still waiting on a human.
- Any other `status` (`in-review`, `consumed`, …) → already processed, skip.

Empty queue: say so and stop.

## Step 2 — Process the queue, one note at a time

Batches of **5**, reporting after each (§ Step 4) before the next. Within a batch, process notes
**sequentially, never in parallel** — two notes can anchor to the same feature, and parallel edits to
one hub file race. Sequential processing keeps every write safe without locking.

Per note, spawn one fresh `Agent` (`subagent_type: general-purpose`, `model: haiku`,
`run_in_background: false`) — never reuse a prior note's subagent, which grows its context instead of
resetting it. Give it the note's id and path, whether this is a fresh run or a fold-in, and an
instruction to read `{extraction_rules}` plus `{conventions_file}` if present.

Use the prompt in `references/agent-dispatch.md` verbatim rather than re-deriving its shape.

In brief, each subagent:

1. Extracts every discrete signal from `## Raw` into `## Extracted signals`, one row each. This table is the **raw record and stays flat** — arrival order, never merged, never grouped, however many rows describe the same thing. It's what the fidelity check quotes against and what every later stage re-reads. `{extraction_rules}` has the `Type`/`Why`/`Status` vocabulary and the rules keeping each field honest.
2. Anchors each signal to a `{requirements_file}` slug — `declared_features` first (a floor, not a ceiling: still scan for features beyond it), then matching signal content against the feature list.
3. Groups the anchored signals by feature, then **by functional theme within each feature**. Grouping by feature is a filing order: one feature's rows append in a single edit, so a note touching three features makes three hub writes, not a dozen. Grouping by theme is an output: signals describing the same rule, flow, or decision file as **one hub row carrying all of their detail**, not one row each (§ Themed hub rows).
4. Appends each themed group to `{hub_dir}/<slug>.md`'s `## Signal Log` (`Status`: `new`, `question`, `conflict`, or `rejected` — nothing else), creating the hub from `{template_hub}` if absent. A `pain-point` also mirrors into `{pain_points_file}` and the hub's `## Pain Points`; an entity/field signal or durable cross-cutting constraint gets a row in `{entities_file}`/`{design_principles_file}` — **per signal, not per theme**; consolidation never collapses a register row. Touch only the hub's Signal Log, Pain Points, and the `sources`/`updated` frontmatter — every other section belongs to a later step.
5. Writes a question to `## Open Questions` for any signal matching no slug (§ The feature-mapping loop) — never files it to a hub.
6. Confirms every touched hub shows its new row(s) on disk *before* setting the note's `status` — a flip to `in-review` drops the note from every future scan, so an unwritten row would vanish silently. Then sets `in-review` if every question is resolved, `needs-clarification` if any remain. If a hub write didn't land, leaves `status` untouched and reports what's pending.

**A signal revealing a genuinely new feature does not mint its own `FEATURES.md` row.** The subagent
raises the feature-mapping question and stops (§ The feature-mapping loop). A slug is permanent and
everything downstream anchors to it, so it's a human's call — and this skill has no `AskUserQuestion`
to make it any other way. A `proposed` row appears only when a human writes one: answering that
question, or up front from a proposal via `/bigin-new-project` § 5.

## Step 3 — Verify nothing was missed

After each batch, spawn one `Agent` (`haiku`, `general-purpose`, foreground) to check the batch's own
claims, not repeat the extraction. Per note and per slug it reported touching, confirm
`{hub_dir}/<slug>.md`'s `## Signal Log` cites that `INT-###`, that **every anchored row number in the
note's `## Extracted signals` appears in exactly one hub row's `Source` cite** — none missing, none
cited twice — and that the note's `status` matches its `## Open Questions` state. Row counts are *not*
the check: a themed row covers several note rows by design, so counting hub rows against note rows
would flag every correct consolidation and miss the one thing that actually goes wrong, a signal
dropped inside a merge. Checklist and repair procedure: `references/agent-dispatch.md`. A note
reporting success while missing its hub row is stranded, not done — a finalized note drops out of
every future scan.

Any mismatch is blocking: dispatch one targeted repair subagent to file the uncited row(s) from the
note's already-extracted table onto the correct hub (no re-extraction), then re-check that note.

Then the **fidelity check** — one `Agent` per note (`sonnet`, `general-purpose`, foreground). This is
the only place in the plugin where a signal is checked against the raw source it claims. It quotes
supporting text for every `requirement`/`constraint`/`decision`/`feedback` row and samples the rest; a
row with no locatable quote, or whose quote says less than the row claims, is corrected down to the
source or turned into a `question` before the note finalizes. Prompt and repair rules:
`references/agent-dispatch.md` § Fidelity subagent. `/bigin-transform-signal` never re-reads `## Raw`,
so a fabrication surviving here survives into an FR.

## Step 4 — Report

Print a short summary of the batch (or the whole run, once the queue is drained):

```text
processed: N notes
signals filed: total — per feature, e.g. <slug>: N signals in M themed rows (Signal Log rows #a-#b)
parked — awaiting an answer: INT-### (N question(s) unanswered)
parked — awaiting a feature mapping: INT-### (signal(s) unresolved — human writes the slug into the A: line)
verification: clean | repaired (list what)
remaining in queue: N — re-run this skill to continue
```

No separate state to update — the next run derives the queue fresh from the vault.

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

Four things never merge: signals from **different notes or runs** (the log is append-only — a
continuing theme cites the older row as `Notes: extends #<n>` rather than reopening it), signals with
**different `Status`** (only `new` consolidates, so a `question`/`conflict`/`rejected` row stays 1:1 with
its Open Questions mirror), a presentation-only signal with a **behavioural** one (different lanes, and
the design lane skips the approval gate), and two signals that **contradict** each other (that's a
`conflict`). Full rules, including the row format and why registers stay per-signal:
`{extraction_rules}` § Consolidating into themed hub rows.

Over-merging is the failure mode to watch. A row that reads like one ask but hides four is worse than a
long log — the detail a drafter needs is still on the page but no longer legible as separate obligations.

## The feature-mapping loop

A signal matching no `{requirements_file}` slug is never guessed onto one. It becomes a question on the
`INT` note (owner: team), tagged `needs-review`, and the note flips to `needs-clarification`. A human
resolves it by writing the slug into the question's `A:` line — minting a `proposed` row first if the
scope is genuinely new — and ticking the box. The next run picks the note up as a fold-in (Step 1
recognizes "needs-clarification, every question answered") and anchors it properly. No separate
command, no re-extraction of what was already correct.

## Model

Extraction, matching, and filing don't need a strong model: every subagent defaults to `haiku`. Fall
back to the session default for a single subagent only if it reports being stuck on something a
written question can't cover — rare, and worth a line in the report.

The one exception is the **fidelity subagent** (§ Step 3), on `sonnet`. Judging whether a
plausible-sounding signal is actually supported by its source is the weakest thing a small model does,
and this is the last point where raw material is still read. Worth the cost; nothing else here is.

## Additional resources

Paths and templates are in § Paths. **`references/agent-dispatch.md`** holds the three subagent
prompts (extraction, verification, fidelity) and the targeted-repair procedure for a Step 3 mismatch.
