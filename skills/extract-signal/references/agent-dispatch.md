# Subagent dispatch — what to hand each agent, and why

**Three workers, two of them on every note** — **2a extract + self-audit** → *(2b independent audit,
only when owed)* → **2c file** — each a **named agent** with its model pinned in its own frontmatter:

| # | Agent | Model | When | Why that model |
|---|---|---|---|---|
| 2a | `signal-extractor` | session default (never `haiku`) | every note | finding every discrete claim in natural language is the hardest judgment here, and it sets the ceiling on everything downstream. It also repairs its own table, from source it has already read |
| 2b | `signal-auditor` | `sonnet`, one per note — never per batch | only when § The audit-owed test says so | a fresh reader on the notes where self-auditing is known to fail. A per-batch agent holds several transcripts at once, the exact under-reading failure segmentation exists to prevent |
| 2c | `signal-filer` | `sonnet` | every note, sequential | anchoring is scope-matching judgment; a weaker model files by adjacency and the tail of a long note lands wrong, permanently |

**The batch gate is not an agent.** `hooks/bigin-lint.py --full` closes each batch — table shape, cite
resolution, illegal statuses, uncited and doubly-cited rows, status-vs-questions consistency — in
milliseconds and without judgment.

**What 1.8.8 removed, and why.** `signal-repairer` applied findings it was handed, from a context that
had never seen the source; folding the repair into whichever agent *found* the finding costs one less
cold start and loses nothing at the handoff. `signal-batch-verifier` re-read, per batch, files the
linter already parses. Between them they were two of every five dispatches.

## One procedure, one home

**This file carries only the per-run data** — the facts an agent has no way to already know. Every
agent's *procedure* lives in exactly one place, and it is a project-materialized file under `_bigin/`
that the agent reads for itself:

| Agent | Its procedure lives in |
|---|---|
| `signal-extractor` | `_bigin/stages/extract/2-extraction.md`, in full — plus `2b-audit.md` §§ Repairing the table, When the independent pass is owed, and nothing else from that file |
| `signal-auditor` | `_bigin/stages/extract/2b-audit.md`, in full |
| `signal-filer` | `_bigin/stages/extract/3-filing.md`, in full |

**Never paste a procedure into a dispatch prompt.** Two copies of the same rule is how this pipeline
already shipped a `signal-auditor` missing the mandatory unresolved-mechanism case while the dispatch
prompt had it. A dispatch
prompt that restates a rule also silently overrides the project's own `_bigin/` override of that rule,
which is the whole point of materializing the rulebook.

What a dispatch prompt is for: the note path, this run's mode, the read plan, and the handful of
per-run findings the agent cannot derive. Nothing else.

## Static first, per-run data last

Every template below is written the same way: the standing instructions, then a single
`--- THIS RUN ---` block holding every value that changes. Two reasons, in order of how much they
matter:

1. **A reader can see what varies.** When a dynamic slot sits mid-paragraph, the next person editing
   the template cannot tell the contract from the payload, and a rule quietly becomes a variable.
2. **It extends the cacheable prefix.** A subagent's system prompt is its agent body — identical on
   every dispatch, and cached. The dispatch prompt follows it, and the cache holds up to the first
   token that differs. Static text ahead of the first slot is covered; the same text below it is not.

Keep the gain in proportion: these prompts are a couple of dozen lines, so this saves hundreds of
tokens per dispatch, not the bulk of one. **The large per-dispatch cost is the stage file each agent
`Read`s for itself**, and that arrives as a tool result inside one subagent's own context — five
parallel extractors each pay for `2-extraction.md` separately, and no prompt ordering changes that.
Keeping those files small is what does.

---

## 2a — `signal-extractor`

```text
Extract the signals in the note named below into its ## Extracted signals table, following
_bigin/stages/extract/2-extraction.md exactly.

## Raw holds one "### SRC-n · <kind> · <ref>" block per source. Read EVERY one, one at a time by
line range, and open any file a block names instead of inlining its text. This is the complete
material; nothing else about this note is read by anyone downstream.

If something in it resolves one of the vault's open questions listed below, extract it as
Type: answer citing that question's id. That list is gathered once per run by the orchestrator; do
not re-gather it.

Then run § Step 6: re-walk each block against the table you just wrote and repair it in place,
using the categories in 2b-audit.md § Repairing the table.

Report in the shape 2-extraction.md § Before reporting and your own § Report define — INCLUDING the
`self_audit` and `audit_owed` lines. The orchestrator dispatches the independent audit on
`audit_owed`, so an omitted verdict silently downgrades a transcript to no audit at all.

--- THIS RUN ---
NOTE:      <INT-###>  (00-Inbox/<filename>.md)
MODE:      <"fresh run" | "partial fold-in — harvest these newly-answered questions, leave the
           rest: <list>">
SOURCES:   <the note's raw_sources manifest, one line each — or "manifest empty: work the ### SRC
           blocks you find in ## Raw">
RAW SPAN:  <N> lines
QUESTIONS: <the batch's open-question list, or "none">
```

Nothing else belongs in this prompt. Recall discipline, segmenting, classify-first, the `Why` search,
field tables, the 8-cell shape, the 30%-`not stated` stop rule, and the § Step 6 self-audit — all of it
is in the stage file, in full, and the agent is told to read it in full.

---

## 2b — `signal-auditor`

**Dispatch only when 2a reported `audit_owed: yes`.** That verdict is the extractor's, made against
`2b-audit.md` § When the independent pass is owed; the orchestrator does not re-derive it. Every other
note is closed by the extractor's own § Step 6 self-audit and reported as `audit: self`.

### The audit-owed test

```text
OWED when ANY holds:
    any source block's kind is `transcript`         # however short
    ## Raw is ~300 lines or more
    > 1 block, with an attachment or a thread among them
    2a could not read a block, or `not stated` > 30% of requirement/feedback rows
    2a's self-audit found an inversion or a contradiction     # found one → assume it missed one
    2a's self-audit repaired > 5 rows
```

Never dispatch it on anything else, and never check inline in the orchestrator instead — pulling
`## Raw` into that context is the one thing this fan-out exists to avoid.

```text
Audit the signal table of the note named below against its source, in both directions, following
_bigin/stages/extract/2b-audit.md exactly. Audit blind FIRST — write your own claim list before you
open the table — then repair what you found, then verify your repairs against the blocks you still
have open.

The "2a reported" block below tells you where to press hardest. Read it as a map of where the
extractor was uncertain, never as a summary of what the source says: you are here precisely because
a reader who already knows the answer cannot find what is missing.

--- THIS RUN ---
NOTE:        <INT-###>  (00-Inbox/<filename>.md)
RAW SPAN:    <N> lines across <N> blocks
SOURCES:     <the raw_sources manifest, one line each>
DISPATCHED
 BECAUSE:    <the trigger(s) from the audit-owed test that fired>
2a REPORTED:
  blocks read:    <per-block reads, or "SRC-n NOT READ — <why>">
  why_not_stated: <N of M (X%)>
  derived rows:   <row #s, or none>
  restated rules: <row #s of the "two wordings" question rows, or none>
  its self-audit: <the self_audit line, verbatim>   # what it already believes it fixed
```

The load-bearing ordering rule (write your own claim list *before* opening the table), the UNSUPPORTED
case table including the unresolved-mechanism case, the exemption for declared inferences, the repair
vocabulary, and the report format are all in the stage file. Do not restate any of them here.

**Hand it 2a's self-audit line, but nothing 2a concluded about the source.** Knowing which rows were
already touched tells it where the extractor was uncertain; a summary of what the source says would
prime exactly the confirmation bias the blind pass exists to defeat.

---

## 2c — `signal-filer`

```text
Anchor and file the signals already extracted in the note named below, following
_bigin/stages/extract/3-filing.md exactly. The ## Extracted signals table is COMPLETE and already
audited — do not re-extract, do not add rows, do not change any row's #, Type, Signal, or Why, and
never open ## Raw, a transcript, or an attachment.

DECLARED FEATURES are a floor, not a ceiling: every one is settled and never re-questioned, and the
scan still matches every row independently (3-filing.md § Step 1).

For HUB OPEN QUESTIONS — if a row of this note answers one, strike it there and tick the originating
note's own copy too (3-filing.md § Step 5b).

--- THIS RUN ---
NOTE:       <INT-###>  (00-Inbox/<filename>.md)
DECLARED:   <the note's declared_features, or "none">
FLAGGED:    <rows an audit flagged — 2a's self-audit, or 2b's, whichever ran — to file as
            Status: question with a client-facing confirmation question, or "none">
CONFLICTS:  <contradicting row pairs an audit found, to file as Status: conflict, or "none">
HUB OPEN
 QUESTIONS: <per hub: the open question lines, or "none">
```

Anchoring row-by-row, the theme test, the four never-merge cases, the register rules, question wording
and batching, and the pre-finalize gate are all in the stage file, in full.

---

## 3 — the batch gate, no agent

One command per batch, after every note in it has been filed:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/bigin-lint.py" --full
```

It checks table shape, note status against open questions, hub citations, orphaned and
doubly-cited rows, illegal status values, and cite resolution — deterministically, over the whole
vault, in milliseconds. `exit 1` means findings, and findings are blocking.

**A filing gap is blocking, and it is repairable in place.** A note reporting success while missing
its hub row is stranded, not done: `status: in-review` drops it from every future scan, so nothing
else will ever catch it. Dispatch `signal-filer` in **hub-repair mode** scoped to exactly the gap
(its own § When to invoke covers the mode), re-run `--full`, and only then move to the next batch.

**An unavailable checker is not a pass.** No `python3`, an unresolvable `${CLAUDE_PLUGIN_ROOT}`, or a
denied command → say so in the batch report and check the batch by hand against the skill's Stage 3
shape. Silence here reads as clean and is the one failure this gate cannot catch about itself.

---

## Parallelism

```text
2a and 2b are per-note and touch NOTHING shared — one note's own ## Extracted signals table.
    → run them across the batch's notes CONCURRENTLY, ≤ 4 at a time
    → 2b follows 2a on the SAME note (it needs the finished table), but a note's 2b runs happily
      alongside another note's 2a
2c writes SHARED files — feature hubs, PAIN-POINTS.md, ENTITIES.md, DESIGN-PRINCIPLES.md
    → SEQUENTIAL, one note at a time. Two notes filing to one hub race, and one append is lost.
    → the registers make it sequential even for notes touching different hubs
3 is one Bash command per batch, after every 2c in it has finished
```

Serializing 2a/2b behind 2c gains nothing and costs the wall-clock of the whole chain per note; the
shared-write hazard only ever existed in 2c. Report between batches either way — a failure should cost
one batch, not the queue.
