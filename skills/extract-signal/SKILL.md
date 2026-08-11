---
name: extract-signal
description: Drain the raw intake queue in 00-Inbox — extract each INT-### note's signals, anchor every signal to a FEATURES.md slug, and file it onto that feature's Signal Log. A signal that can't be anchored raises a written question on the note instead of a guess, parking it needs-clarification until a human supplies the slug. Never drafts or edits an FR — that's a later step. Use when the ask is to extract signals, process the intake queue, drain 00-Inbox, or map intake to features.
argument-hint: "[resume]"
disallowed-tools: AskUserQuestion
disable-model-invocation: true
---

# Extract Signal

`00-Inbox` fills with raw `INT-###` notes from `/bigin-intake` — emails, meetings, and direct notes, captured verbatim. This skill drains that queue: for each eligible note, extract its signals into the note's own `## Extracted signals` table, then anchor each signal to a feature and file it onto that feature's hub. A signal that can't be anchored becomes a written question instead of a guess.

This skill never touches an FR — it only files signals to a hub's Signal Log (plus a few vault-wide registers a signal populates directly, § Step 2). Folding a filed signal into a requirement is a separate, later step.

The vault is the only state. Nothing here persists progress outside the notes and hubs themselves, so `resume` just means running the skill again — every run rescans `{inbox_dir}` fresh.

## Paths

- `{inbox_dir}`: `00-Inbox` — skip `_attachments/` when scanning.
- `{requirements_file}`: `01-Requirements/FEATURES.md` — the slug registry; a signal can only anchor to a slug listed here.
- `{hub_dir}`: `01-Requirements/_features` — one hub file per slug, `{hub_dir}/<slug>.md`.
- `{conventions_reference}`: `references/conventions.md` — the plugin-wide ID scheme, frontmatter schema, and artifact conventions this skill follows. Not project-specific; contrast with `{conventions_file}` below.
- `{conventions_file}`: `.claude/bigin-ba-workflow-plugin.local.md` — project-specific anchoring overrides, if the project has written one. This is a plugin setting, not project data, so it lives in `.claude/` rather than `_bigin/`.
- `{pain_points_file}`: `01-Requirements/PAIN-POINTS.md` — the canonical `PP-###` register; every feature hub mirrors its own rows from here.
- `{entities_file}`: `01-Requirements/ENTITIES.md` — candidate `EN-###` rows a signal reveals; no hub mirror.
- `{design_principles_file}`: `01-Requirements/DESIGN-PRINCIPLES.md` — durable, cross-cutting design constraints; no hub mirror.
- `{template_hub}` / `{template_pain_points}` / `{template_entities}` / `{template_design_principles}`: `skills/extract-signal/template/{feature-hub,pain-points-register,entities-register,design-principles-register}.md` — scaffolds for each file above, used the first time it's needed.

## Step 1 — Build the queue

Scan `{inbox_dir}` for `INT-###` notes. For each, read its frontmatter:

- `kind: info` → not refinable, skip (operational/admin capture, never processed into signals).
- `status: raw` → eligible as a fresh run.
- `status: needs-clarification` with every `- [ ] Q:` line in `## Open Questions` now checked → eligible as a **fold-in** (a human already answered, or supplied a feature slug). Any box still unchecked → not eligible yet, it's waiting on a human.
- Any other `status` (`in-review`, `consumed`, etc.) → already processed, skip.

This is the queue. If it's empty, say so and stop.

## Step 2 — Process the queue, one note at a time

Work through the queue in batches of **5**, reporting after each batch (§ Step 4) before starting the next. Within a batch, process notes **one at a time, sequentially** — never in parallel. Two notes can anchor to the same feature; parallel edits to the same hub file would race each other, and sequential processing is what keeps every write safe without adding locking.

For each note, spawn one fresh `Agent` call (`subagent_type: general-purpose`, `model: haiku`, `run_in_background: false`) — never reuse or continue a prior note's subagent, since that grows its context with every note instead of resetting it. Give it:

- The note's id and full path.
- Whether this is a fresh run or a fold-in (so it knows whether to re-derive everything or only resolve the previously-open questions).
- An instruction to read `references/extraction-rules.md` (the signal catalog, anchoring rules, and hub schema) and `{conventions_file}` if it exists, then follow the procedure below against the note and `{requirements_file}`.

The exact prompt template and the subagent's step-by-step procedure live in `references/agent-dispatch.md` — use it verbatim rather than re-deriving the shape each time.

In brief, each subagent:

1. Extracts every discrete signal from `## Raw` into `## Extracted signals` (one row per signal — see the catalog in `references/extraction-rules.md` for the `Type`/`Why`/`Status` vocabulary and the rules that keep each field honest).
2. Anchors each signal to a `{requirements_file}` slug — checking `declared_features` first (a floor, not a ceiling: still scan every signal for features beyond it), then matching signal content against the feature list.
3. For each anchored signal, appends a row to `{hub_dir}/<slug>.md`'s `## Signal Log` (`Status: new`, `question`, `conflict`, or `rejected` — never anything else, § extraction-rules.md), creating the hub file from `{template_hub}` first if it doesn't exist yet. A `pain-point` signal also mirrors into `{pain_points_file}` and the hub's `## Pain Points` table; an entity/field signal or a durable cross-cutting constraint gets a row in `{entities_file}`/`{design_principles_file}` respectively. This skill only ever touches a hub's Signal Log, Pain Points, and a handful of frontmatter fields (`sources`, `updated`) — every other hub section belongs to a later step.
4. For any signal that doesn't match a slug, writes a question to `## Open Questions` instead of guessing (§ The feature-mapping loop) — never files it to a hub.
5. Before setting the note's `status`, confirms every hub it just touched actually shows the new row(s) on disk — a status flip to `in-review` drops the note out of every future scan, so an unwritten hub row would be lost silently. Only then sets `status`: `in-review` once every question is resolved, `needs-clarification` if any remain. If a hub write can't be completed, leaves the note's status untouched and reports exactly what's pending instead.

## Step 3 — Verify nothing was missed

After each batch, spawn one more `Agent` (`haiku`, `general-purpose`, foreground) to check the batch's own claims — not repeat the extraction. For every note in the batch and every slug it reported touching, confirm `{hub_dir}/<slug>.md`'s `## Signal Log` actually cites that `INT-###` with a row count matching the note's own `## Extracted signals` table, and confirm the note's final `status` matches its `## Open Questions` state. The full checklist and the repair procedure for a mismatch are in `references/agent-dispatch.md` — a note that reports success but is missing its hub row is stranded, not done, since a finalized note drops out of every future scan.

Treat any mismatch as blocking: dispatch one small, targeted repair subagent that copies the missing row(s) from the note's own already-extracted table onto the correct hub (it doesn't re-extract), then re-check that one note before moving on.

## Step 4 — Report

Print a short summary of the batch (or the whole run, once the queue is drained):

```text
processed: N notes
signals filed: total — per feature, e.g. <slug>: N new (Signal Log rows #a-#b)
parked — awaiting an answer: INT-### (N question(s) unanswered)
parked — awaiting a feature mapping: INT-### (signal(s) unresolved — human writes the slug into the A: line)
verification: clean | repaired (list what)
remaining in queue: N — re-run this skill to continue
```

There's no separate state to update — the next run derives the queue fresh from the vault.

## The feature-mapping loop

A signal that doesn't match any `{requirements_file}` slug is never guessed onto one. It becomes a question on the `INT` note (owner: team), tagged `needs-review`, and the note's `status` flips to `needs-clarification`. A human resolves it by writing the correct slug into the question's `A:` line — minting a new `proposed` row in `{requirements_file}` first if the scope is genuinely new — and ticking the box. The next run of this skill picks the note back up as a fold-in (Step 1 is what recognizes "needs-clarification, every question now answered") and anchors that signal properly. No separate command, no re-extraction of what was already correct.

## Model

This is extraction, matching, and filing — not judgment calls that need a stronger model. Every subagent this skill spawns, extraction and verification alike, defaults to `haiku`. Only fall back to the session's default model for a single subagent if it explicitly reports being stuck on something a written question can't cover — that should be rare, and worth a line in the report.

## Additional resources

- **`references/extraction-rules.md`** — the signal catalog (`Type`/`Why`/`Status` vocabulary), anchoring rules, and the Feature Hub's `## Signal Log` schema. Every dispatched subagent reads this.
- **`references/agent-dispatch.md`** — the exact subagent prompt templates for extraction and verification, and the targeted-repair procedure for a mismatch found in Step 3.
- **`template/feature-hub.md`** — scaffold used to create a new `{hub_dir}/<slug>.md` the first time a signal anchors to it.
- **`template/pain-points-register.md`**, **`template/entities-register.md`**, **`template/design-principles-register.md`** — scaffolds for the three vault-wide registers, each instantiated the first time a signal needs it.
