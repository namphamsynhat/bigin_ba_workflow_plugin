# Subagent dispatch

## Extraction subagent (Step 2)

One fresh `Agent` call per note, `subagent_type: general-purpose`, `model: haiku`, `run_in_background: false`. The subagent has no memory of this conversation, so give it the cheap facts already known and point it at the real files rather than paraphrasing them — a summary risks the subagent trusting a stale paraphrase over the source of truth.

```text
Extract and file the signals in <INT-###> (full path: 00-Inbox/<filename>.md).

This is <"a fresh run" | "a fold-in — every previously-open question is now answered">.

Read before doing anything:
- _bigin/stages/extract/2-extraction.md — in full (the signal catalog, anchoring rules, hub schema)
- _bigin/conventions/paths.md — resolves every {variable} that file refers to
- _bigin/conventions/conventions.md — these sections ONLY, not the whole file: § ID scheme,
  § Feature Hub, § Signal → feature mapping, § Open Questions wording, § Pain Point Register,
  § Design Principles Register, § Entity Data Model. The rest governs FR/BR drafting and later
  stages, which this task never touches.
- .claude/bigin-ba-workflow-plugin.local.md, if it exists (project-specific overrides)
- 01-Requirements/FEATURES.md (the slug registry)
- the note itself

Then, following 2-extraction.md exactly:
1. Extract every discrete signal from ## Raw into ## Extracted signals (or, on a fold-in,
   only the rows still blocked on an answer). This table is the RAW RECORD: one flat row
   per signal, in arrival order, never merged and never grouped, however many rows describe
   the same thing. Run the self-checks in 2-extraction.md § Before finalizing a note before
   you consider this step done.
2. Anchor each signal to a FEATURES.md slug. Never guess — an unresolved signal gets a
   question in ## Open Questions instead.
3. Group this note's anchored signals for each slug BY FUNCTIONAL THEME, then append ONE
   row per theme to 01-Requirements/_features/<slug>.md's ## Signal Log — not one row per
   signal. Follow 2-extraction.md § Consolidating into themed hub rows exactly for the
   theme test, the four never-merge cases, and the row format. In short (columns:
   # | Signal | Type | Source | Status | Destination | Notes):
     - Signal: **<Theme>** — <detail>; <detail>; <detail> — every member's claim kept as
       its own clause, nothing compressed away, nothing claiming more than its note row did
     - Type: member types in catalog order joined with " + ", e.g. requirement + constraint
     - Source: <INT-###> #<n>, #<n> — <the note's own Source cite>, citing the note row
       numbers this row consolidates. Every anchored note row must appear in exactly one
       hub row's Source cite — this is the traceability, and it is verified afterwards.
     - Status: new, question, conflict, or rejected — never anything else. Only `new` rows
       consolidate; a question/conflict/rejected signal files as its own row.
     - Destination: blank.
   A theme of one is normal — don't stretch unrelated signals together to shorten the
   table. Create the hub from _bigin/templates/feature-hub.md first if it doesn't exist
   yet, and update only its Signal Log, Pain Points, sources, and updated fields, nothing
   else in the hub.
4. Registers stay PER SIGNAL — consolidation never collapses a register row. For any
   pain-point signal, mirror it into 01-Requirements/PAIN-POINTS.md (create from
   _bigin/templates/pain-points-register.md if missing) and the hub's own ## Pain Points
   table, both copies identical. For an entity/field signal, add a proposed row to
   01-Requirements/ENTITIES.md (template: entities-register.md). For a durable,
   cross-cutting design constraint, add a row to 01-Requirements/DESIGN-PRINCIPLES.md
   (template: design-principles-register.md) in addition to its normal Signal Log filing.
   Cite the ids you minted in the themed row's Notes.
5. Before touching the note's status, re-open every hub you just wrote to and confirm the
   new row(s) are actually there. Only then set the note's frontmatter status: in-review
   if every question is resolved, needs-clarification if any remain. If a hub write didn't
   land, leave the note's status as-is and say so in your report instead of finalizing it.

Report back: int (the note id), note_status (the status you set, or "unchanged — hub write
pending" if step 5 blocked), signals (count extracted this run), features_touched (every
slug you filed to, as a list), and rows_filed — per slug, the hub row #s you added and the
note row #s each one cites, e.g. "vendor-payouts: #7 cites #3,#5,#7 · #8 cites #4".
```

## Verification subagent (Step 3)

One `Agent` call per batch, `model: haiku`, `general-purpose`, foreground. It checks the batch's own claims — it does not re-open `## Raw` or re-extract anything.

```text
Verify the extract-signal batch below without re-extracting anything.

Batch (int, note_status, signals, features_touched, rows_filed):
<paste each note's reported verdict from Step 2>

Hub Signal Log rows are grouped by functional theme: ONE row can legitimately cover several
of the note's signals, citing their row numbers in its Source cell (e.g.
"INT-014 #3, #5, #7 — Jane Doe 2026-08-05"). Do not compare row counts between the note and
the hub — they are not meant to match. Check the citations instead.

For each note:
1. Open 00-Inbox/<INT-###>.md. Confirm its frontmatter status matches note_status, and
   that status is in-review only if every ## Open Questions box is checked.
2. For every slug in features_touched, open 01-Requirements/_features/<slug>.md and
   confirm its ## Signal Log has row(s) whose Source cell cites this INT id, then collect
   every note row number cited across those rows. Every row in the note's
   ## Extracted signals with a resolved Feature must appear in exactly one of them —
   report any that appears in none (a signal dropped inside a merge) or in more than one.
   Also confirm each themed row's Signal cell visibly carries a clause for each number it
   cites, rather than one summary sentence standing in for several signals.
3. For every pain-point-type signal in that note, confirm a matching row exists in both
   01-Requirements/PAIN-POINTS.md and the hub's own ## Pain Points table.
4. Spot-check one entity/field or design-constraint signal per note, if the note reported
   any, against 01-Requirements/ENTITIES.md / DESIGN-PRINCIPLES.md.
5. Confirm every signal whose ## Extracted signals row shows Feature: unresolved... has
   a matching ## Open Questions entry — not just a claimed one.

Report one line per note: clean, or exactly what's missing (which hub, which row).
```

## Fidelity subagent (Step 3b) — is each signal actually supported by the source?

The verification subagent above checks that the *filing* is complete. This one checks that the
*content* is real: that every extracted signal traces to something the client actually said, rather
than to an inference the extracting model made and then wrote down as a claim. A fabricated signal
that clears filing verification is worse than a missed one — it becomes an FR nobody asked for, and
by then the transcript is three stages upstream.

This runs **here, not in `/bigin-transform-signal`**, because it is only cheap next to the raw
material. One `Agent` per note (never per batch — a per-batch agent would hold several transcripts
at once, which is the under-reading failure `2-extraction.md` § Reading long sources warns
about). `model: sonnet`, `general-purpose`, foreground.

Sonnet rather than `haiku` is deliberate and is the one place in this skill worth the cost:
detecting a plausible-sounding claim that the source does not support is exactly the judgment a
smaller model is weakest at, and it is the last checkpoint before the raw source stops being read
by anything downstream.

```text
Check whether every signal extracted from <INT-###> (00-Inbox/<filename>.md) is actually
supported by its source. Do not re-extract, re-anchor, or rewrite anything.

Read the note's ## Extracted signals table and its ## Raw section (plus any attachment the
table cites). If ## Raw is long, work through it in sections rather than in one pass.

For EVERY row whose Type is requirement, constraint, decision, or feedback — the types that
become requirement content downstream — find the exact supporting text in the source and
quote it. Sample at least half the remaining rows the same way.

A row is SUPPORTED only if you can quote source text that states it. Judge these as NOT
supported:
- No locatable quote — the claim reads as a reasonable inference from the discussion rather
  than something said.
- The only support is a meeting tool's AI-generated summary. That is derived text, not the
  client's words (2-extraction.md § The Why field) — it can never support a signal.
- The quote is real but says less than the row claims: a hedge turned into a commitment, a
  single example turned into a general rule, an unstated number, unit, threshold, or
  timezone.
- The row's Why cites a reason the quote does not give, including a Why written as
  "not stated beyond <paraphrase>".

Report one line per row: <#> supported "<the quote, trimmed>" | <#> UNSUPPORTED <which of
the four cases, in a few words>. Then one summary line: <N> rows checked, <N> unsupported.
```

**On any unsupported row**, the orchestrator repairs the note before finalizing it — never leaves
it filed:

A note row's hub counterpart is the themed Signal Log row whose `Source` cite includes that row's
`#` — one themed row can cover several note rows, so read the cite rather than assuming a 1:1 row.
Both repairs below edit a row this same run filed, before the note finalizes; that's the
`Notes: corrected: …` path the extraction rules already allow, not a rewrite of settled history.

- **Overreach** (the quote says less than the row claims): correct the row in place down to what
  the source supports, `Notes: corrected: narrowed to source`, and narrow the matching clause in
  every hub row citing it — the clause only, leaving that row's other clauses untouched.
- **No support at all**: leave the row (hard rule 1 — nothing is deleted), set its `Status` to
  `question`, `Notes: unsupported by source — needs confirmation`, raise a `- [ ] Q:` on the note
  asking the client to confirm or correct the claim in plain language, and set the note's
  `status: needs-clarification`. On the hub, this row can no longer travel with its theme —
  `question` rows never consolidate. Drop its clause from the themed row and its `#` from that
  row's `Source` cite, then append it as its own new row, `Status: question`, with the same note.
  If it was the themed row's only member, flip that row to `question` in place instead.
- Report the count in the batch summary. A run with unsupported rows is not a clean run.

## Repair, on a mismatch

A note that reports success but is missing its hub row is stranded, not done — a finalized note (`status: in-review`) drops out of every future scan of `{inbox_dir}`, so nothing else will ever catch this. Treat any verification mismatch as blocking.

Dispatch one more small subagent (same model, same type) scoped to exactly the gap:

```text
Repair 00-Inbox/<INT-###>.md → 01-Requirements/_features/<slug>.md.

Its ## Extracted signals table already has the correct row(s) for this feature — do not
re-extract or re-anchor anything. Note row(s) # <n> are anchored to this slug but cited by
no hub Signal Log row. File them now, following _bigin/stages/extract/2-extraction.md
§ Consolidating into themed hub rows: group them by functional theme and append one row per
theme (Status: new, Destination blank), Source citing the note row numbers each row covers.

Do NOT edit an existing hub row to absorb them — the log is append-only. If they continue a
theme already on the hub, the new row cites it as "Notes: extends #<n>".

Mirror any pain-point row(s) into 01-Requirements/PAIN-POINTS.md and the hub's ## Pain
Points table too, one row per pain point. Report the hub row(s) you added and which note
row #s each cites.
```

Re-run the relevant part of the verification check for that one note afterward. Only move on to the next batch once it comes back clean.
