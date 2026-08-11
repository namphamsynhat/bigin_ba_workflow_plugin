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
