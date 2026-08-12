# Subagent dispatch

## Extraction subagent (Step 2)

One fresh `Agent` call per note, `subagent_type: general-purpose`, `model: haiku`, `run_in_background: false`. The subagent has no memory of this conversation, so give it the cheap facts already known and point it at the real files rather than paraphrasing them — a summary risks the subagent trusting a stale paraphrase over the source of truth.

```text
Extract and file the signals in <INT-###> (full path: 00-Inbox/<filename>.md).

This is <"a fresh run" | "a fold-in — every previously-open question is now answered">.

Read, in full, before doing anything:
- references/conventions.md (the plugin-wide ID scheme, frontmatter schema, and Signal Log status vocabulary)
- skills/extract-signal/references/extraction-rules.md (the signal catalog, anchoring rules, hub schema)
- .claude/bigin-ba-workflow-plugin.local.md, if it exists (plugin settings — project-specific overrides)
- 01-Requirements/FEATURES.md (the slug registry)
- the note itself

Then, following extraction-rules.md exactly:
1. Extract every discrete signal from ## Raw into ## Extracted signals (or, on a fold-in,
   only the rows still blocked on an answer). Run the four self-checks in
   extraction-rules.md § Before finalizing a note before you consider this step done.
2. Anchor each signal to a FEATURES.md slug. Never guess — an unresolved signal gets a
   question in ## Open Questions instead.
3. For each anchored signal, append a row to 01-Requirements/_features/<slug>.md's
   ## Signal Log (columns: # | Signal | Type | Source | Status | Destination | Notes;
   Status is new, question, conflict, or rejected — never anything else; Destination
   blank) — create the hub from skills/extract-signal/template/feature-hub.md first if it
   doesn't exist yet, and update only its Signal Log, Pain Points, sources, and updated
   fields, nothing else in the hub.
4. For any pain-point signal, also mirror it into 01-Requirements/PAIN-POINTS.md (create
   from skills/extract-signal/template/pain-points-register.md if missing) and the hub's
   own ## Pain Points table, both copies identical. For an entity/field signal, add a
   proposed row to 01-Requirements/ENTITIES.md (template: entities-register.md). For a
   durable, cross-cutting design constraint, add a row to
   01-Requirements/DESIGN-PRINCIPLES.md (template: design-principles-register.md) in
   addition to its normal Signal Log filing.
5. Before touching the note's status, re-open every hub you just wrote to and confirm the
   new row(s) are actually there. Only then set the note's frontmatter status: in-review
   if every question is resolved, needs-clarification if any remain. If a hub write didn't
   land, leave the note's status as-is and say so in your report instead of finalizing it.

Report back: int (the note id), note_status (the status you set, or "unchanged — hub write
pending" if step 5 blocked), signals (count extracted this run), features_touched (every
slug you filed to, as a list).
```

## Verification subagent (Step 3)

One `Agent` call per batch, `model: haiku`, `general-purpose`, foreground. It checks the batch's own claims — it does not re-open `## Raw` or re-extract anything.

```text
Verify the extract-signal batch below without re-extracting anything.

Batch (int, note_status, signals, features_touched):
<paste each note's reported verdict from Step 2>

For each note:
1. Open 00-Inbox/<INT-###>.md. Confirm its frontmatter status matches note_status, and
   that status is in-review only if every ## Open Questions box is checked.
2. For every slug in features_touched, open 01-Requirements/_features/<slug>.md and
   confirm its ## Signal Log has a row whose Source cell cites this INT id, and that the
   row count filed from this note is consistent with its own ## Extracted signals table.
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
at once, which is the under-reading failure `extraction-rules.md` § Reading long sources warns
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
  client's words (extraction-rules.md § The Why field) — it can never support a signal.
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

- **Overreach** (the quote says less than the row claims): correct the row in place down to what
  the source supports, `Notes: corrected: narrowed to source`, and mirror the correction onto every
  hub row already filed from it.
- **No support at all**: leave the row (hard rule 1 — nothing is deleted), set its `Status` to
  `question`, `Notes: unsupported by source — needs confirmation`, raise a `- [ ] Q:` on the note
  asking the client to confirm or correct the claim in plain language, and set the note's
  `status: needs-clarification`. If a hub row was already filed from it, set that row to `question`
  too, with the same note.
- Report the count in the batch summary. A run with unsupported rows is not a clean run.

## Repair, on a mismatch

A note that reports success but is missing its hub row is stranded, not done — a finalized note (`status: in-review`) drops out of every future scan of `{inbox_dir}`, so nothing else will ever catch this. Treat any verification mismatch as blocking.

Dispatch one more small subagent (same model, same type) scoped to exactly the gap:

```text
Repair 00-Inbox/<INT-###>.md → 01-Requirements/_features/<slug>.md.

Its ## Extracted signals table already has the correct row(s) for this feature — do not
re-extract or re-anchor anything. Copy the missing row(s) (# <n>) onto the hub's
## Signal Log (Status: new, Destination blank), in the format
skills/extract-signal/template/feature-hub.md defines — and mirror any pain-point row(s)
into 01-Requirements/PAIN-POINTS.md and the hub's ## Pain Points table too. Report the
row(s) you added.
```

Re-run the relevant part of the verification check for that one note afterward. Only move on to the next batch once it comes back clean.
