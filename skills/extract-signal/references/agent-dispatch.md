# Subagent dispatch — what to hand each agent, and why

Five workers in run order — **2a extract** → **2b audit** → **2b-repair** → **2c file** → **3 verify** —
each a **named agent** with its model pinned in its own frontmatter:

| # | Agent | Model | Why that model |
|---|---|---|---|
| 2a | `signal-extractor` | session default (never `haiku`) | finding every discrete claim in natural language is the hardest judgment here, and it sets the ceiling on everything downstream |
| 2b | `signal-auditor` | `sonnet`, one per note — never per batch | a per-batch agent holds several transcripts at once, the exact under-reading failure segmentation exists to prevent |
| 2b-repair | `signal-repairer` | `sonnet` | applies findings it is handed; kept out of the orchestrator so the batch doesn't accumulate every table and audit report in one context |
| 2c | `signal-filer` | `sonnet` | anchoring is scope-matching judgment; a weaker model files by adjacency and the tail of a long note lands wrong, permanently |
| 3 | `signal-batch-verifier` | `haiku`, one per batch | checks claims against files, no judgment |

## One procedure, one home

**This file carries only the per-run data** — the facts an agent has no way to already know. Every
agent's *procedure* lives in exactly one place, and it is a project-materialized file under `_bigin/`
that the agent reads for itself:

| Agent | Its procedure lives in |
|---|---|
| `signal-extractor` | `_bigin/stages/extract/2-extraction.md`, in full |
| `signal-auditor` | `_bigin/stages/extract/2b-audit.md` (§ Order is load-bearing → § Report) |
| `signal-repairer` | `_bigin/stages/extract/2b-audit.md` § Repairing the table, or `3-filing.md` § Step 2 |
| `signal-filer` | `_bigin/stages/extract/3-filing.md`, in full |
| `signal-batch-verifier` | its own agent body — the checklist is short enough to have no stage file, and it has no other reader |

**Never paste a procedure into a dispatch prompt.** Two copies of the same rule is how this pipeline
already shipped a `signal-auditor` missing the mandatory unresolved-mechanism case while the dispatch
prompt had it, and a batch verifier accepting question mirrors in places nothing writes them. A dispatch
prompt that restates a rule also silently overrides the project's own `_bigin/` override of that rule,
which is the whole point of materializing the rulebook.

What a dispatch prompt is for: the note path, this run's mode, the read plan, and the handful of
per-run findings the agent cannot derive. Nothing else.

---

## 2a — `signal-extractor`

```text
Extract the signals in <INT-###> (00-Inbox/<filename>.md) into its ## Extracted signals table,
following _bigin/stages/extract/2-extraction.md exactly.

MODE: <"fresh run" | "partial fold-in — harvest these newly-answered questions, leave the rest:
<list>">

YOUR SOURCES — ## Raw holds one "### SRC-n · <kind> · <ref>" block per source. Read EVERY one, one
at a time by line range, and open any file a block names instead of inlining its text. This is the
complete material; nothing else about this note is read by anyone downstream.
<the note's raw_sources manifest, one line each — or "manifest empty: work the ### SRC blocks you
find in ## Raw">
## Raw spans <N> lines.

OPEN QUESTIONS elsewhere in the vault — if something here resolves one, extract it as Type: answer
citing the question's id. This list is gathered once per run by the orchestrator; do not re-gather it:
<the batch's list, or "none">

Report in the shape 2-extraction.md § Before reporting and your own § Report define.
```

Nothing else belongs in this prompt. Recall discipline, segmenting, classify-first, the `Why` search,
field tables, the 8-cell shape, the 30%-`not stated` stop rule — all of it is in the stage file, in full,
and the agent is told to read it in full.

---

## 2b — `signal-auditor`

Check `2b-audit.md` § When this pass may be skipped **before dispatching**: a short single-block
non-transcript note gets an inline orchestrator check instead, reported as `audit: inline`. Everything
else gets this.

```text
Audit the signal table of <INT-###> (00-Inbox/<filename>.md) against its source, in both directions,
following _bigin/stages/extract/2b-audit.md exactly. Report only — repair nothing.

## Raw spans <N> lines, across <N> blocks: <the raw_sources manifest, one line each>.

WHAT 2a REPORTED, so you know where to press hardest:
- blocks read: <per-block reads, or "SRC-n NOT READ — <why>">
- why_not_stated: <N of M (X%)>
- derived rows: <row #s, or none>
- restated rules: <row #s of the "two wordings" question rows, or none>
<a re-audit only> SCOPE: audit only rows <#list> — the rows the repair pass just touched, and what
each repair claims to have fixed: <one line each>.
```

The load-bearing ordering rule (write your own claim list *before* opening the table), the UNSUPPORTED
case table including the unresolved-mechanism case, the exemption for declared inferences, and the
four-part report format are all in the stage file. Do not restate any of them here.

---

## 2b-repair — `signal-repairer`

Only when the audit returned findings. Hand it the audit report **verbatim** — it does not re-read the
source, so a gap line you summarize is a signal lost a second time.

```text
Repair the ## Extracted signals table of <INT-###> (00-Inbox/<filename>.md) from the audit findings
below, following _bigin/stages/extract/2b-audit.md § Repairing the table exactly.

THE AUDIT REPORT, VERBATIM:
<paste parts A, B, and C of the auditor's report, unedited>
```

Then, per that section's own rule: re-audit scoped to the touched rows when a repair touched more than
two, and only dispatch 2c once the table is settled.

---

## 2c — `signal-filer`

```text
Anchor and file the signals already extracted in <INT-###> (00-Inbox/<filename>.md), following
_bigin/stages/extract/3-filing.md exactly. The ## Extracted signals table is COMPLETE and already
audited — do not re-extract, do not add rows, do not change any row's #, Type, Signal, or Why, and
never open ## Raw, a transcript, or an attachment.

DECLARED FEATURES (from the note's frontmatter, set by a human at capture): <list, or "none">
    → a floor, not a ceiling: every one is settled and never re-questioned, and the scan still
      matches every row independently (3-filing.md § Step 1)

Rows the audit flagged, to file as Status: question with a client-facing confirmation question:
<list, or "none">
Contradicting row pairs the audit found, to file as Status: conflict: <list, or "none">

HUB OPEN QUESTIONS this note's rows may resolve — if a row answers one, strike it there and tick the
originating note's own copy too (3-filing.md § Step 5b):
<per hub: the open question lines, or "none">
```

Anchoring row-by-row, the theme test, the four never-merge cases, the register rules, question wording
and batching, and the pre-finalize gate are all in the stage file, in full.

---

## 3 — `signal-batch-verifier`

One per batch, after every note in it has been filed.

```text
Verify the extract-signal batch below without re-extracting anything, per your own checklist.

Batch (int, note_status, features_touched, rows_filed):
<paste each note's reported verdict from 2c, verbatim>
```

Its checks — table shape, note status vs open questions, hub citations, orphaned rows, pain-point ids,
question mirrors, rationale batching, and cite resolution — are its own agent body's § What you check.
That body is the single source; this prompt supplies the batch and nothing more.

**Any mismatch is blocking.** A note reporting success while missing its hub row is stranded, not done:
`status: in-review` drops it from every future scan, so nothing else will ever catch it. Dispatch
`signal-repairer` in hub-repair mode scoped to exactly the gap, re-verify that note, and only then move
to the next batch.

---

## Parallelism

```text
2a and 2b are per-note and touch NOTHING shared — one note's own ## Extracted signals table.
    → run them across the batch's notes CONCURRENTLY, ≤ 4 at a time
2b-repair is per-note too, same table          → concurrent, same cap
2c writes SHARED files — feature hubs, PAIN-POINTS.md, ENTITIES.md, DESIGN-PRINCIPLES.md
    → SEQUENTIAL, one note at a time. Two notes filing to one hub race, and one append is lost.
    → the registers make it sequential even for notes touching different hubs
3 is one dispatch per batch, after every 2c in it has finished
```

Serializing 2a/2b behind 2c gains nothing and costs the wall-clock of the whole chain per note; the
shared-write hazard only ever existed in 2c. Report between batches either way — a failure should cost
one batch, not the queue.
