---
name: extract-signal
description: "Drain the raw intake queue in 00-Inbox: extract each note's signals, audit them against the source where owed, file them onto feature hubs by theme, then analyse each note against current requirements (affected use cases, conflicts, unclear points). Use on \"extract signals\", \"process the intake queue\", \"map intake to features\", \"what does this ticket impact\", or to withdraw a request the client removed. Never drafts a UC."
argument-hint: "[resume <run-id>]"
disallowed-tools: AskUserQuestion
---

# Extract Signal

Per `INT-###` note in `00-Inbox`: extract → audit (when owed) → file → analyse. Extract stage of extract →
transform → load. Never drafts or edits a UC or BR. **LLM for judgement, the engine for every write:** agents read a compact
worklist and return one JSON file; `scripts/bigin` validates and writes it.

`bigin` below is the shell function `bigin() { python "${CLAUDE_PLUGIN_ROOT}/lib/bigin/cli.py" "$@"; }` (`python3` if no
`python` on PATH; or `"${CLAUDE_PLUGIN_ROOT}/scripts/bigin"` / `scripts/bigin.cmd`) — run from the vault root.

## Two tables, on purpose

| Table | Where | Shape |
|---|---|---|
| **Raw record** | the note's `## Extracted signals` | one flat row per signal, arrival order, never grouped, row `#` permanent |
| **Working register** | the hub's `## Signal Log` (or `<slug>.signals.md` once split) | the same signals grouped by theme |

Row counts won't match, and shouldn't. Every later stage reads the raw record; nothing re-opens `## Raw`.

## Preconditions

- `_bigin/stages/extract/` and `_bigin/conventions/` exist — else stop: `/bigin-new-project` must run first.
- `version-check.md` § Workspace version check — behind → warn, recommend `/bigin-upgrade-project`; ahead → stop.
- `project.md` `grounding:` — `codebase` notes (`source: codebase`) are skipped here: their rows were written by
  `bigin intake codebase`, with no LLM. `communication` and `both` vaults run this skill for every other note.

## Stage 1 — Build the queue

```text
for note in 00-Inbox/INT-*.md (skip _attachments/), frontmatter ONLY:
    kind == info or source == codebase     → skip
    status == withdrawn                    → skip (the client removed it — § Withdrawal)
    status == raw                          → queue (fresh)
    status == needs-clarification          → queue (fold-in) if a "- [ ] Q:" was newly ticked, else park
    else                                   → skip (in-review = consumed)
queue empty → say so, stop
```

Partial fold-in beats waiting: a note with some answers is re-queued for what those answers unblock.
`raw_sources` is the read plan; an empty manifest with visible `### SRC-n` blocks is an older capture — the
worklist builds the plan from the blocks either way.

## Stage 2 — Run

```text
RUN = $(bigin run new --stage extract --scope <n>-notes)
```

**With the Workflow tool** (preferred — orchestration lives in the script, not in this context):

```text
Workflow(scriptPath: "_runs/RUN/workflows/extract.js",   # staged by `run new`; never the plugin cache path
         args: {run: RUN, vault: ".", plugin_root: "${CLAUDE_PLUGIN_ROOT}", notes: [<INT ids>]})
```

Per note, in parallel: `signal-extractor` → `ingest` + `note write-signals --run` (which prints the engine's
`audit_owed` verdict and any `why_repair` rows) → a Why repair by the same extractor where `not stated` runs over
30% → `signal-auditor` + `note audit-apply` where the audit is owed. Then filing, **serially** (a later note's theme
may extend a row an earlier note just filed): `worklist file` → `signal-filer` → `ingest` + `file apply`. Then
analysis per filed note (agents in parallel, applies serially): `worklist analyze` → `intake-analyst` → `ingest` +
`note analysis-apply`. Then `lint --full` and `coverage --stage file`. Resume = re-run with the same `run`
(completed tasks are skipped via `run done`; an audit still owed from a stopped run is picked up), or the Workflow
tool's `resumeFromRunId`.

**Without it** — the same steps, one `Agent` call per judgement task: follow `references/agent-dispatch.md`, the
one home of the fallback loop (extractors may run 4 at a time; filers never overlap).

Between steps read only the one-line agent reply and `bigin run summary RUN` (≤ 20 lines) — never an agent
transcript, never `## Raw`. **Never audit inline** in this context: either the extractor's self-audit stands or a
fresh `signal-auditor` is dispatched — and **the engine decides which**: `note write-signals` prints `audit_owed`
and `audit_reasons` from the note's structure and the extractor's self-audit counts (`2b-audit.md` § When the
independent pass is owed). Report the depth that ran on each note (`audit: self` vs `audit: independent (<reason>)`).

**Gate.** `bigin lint --full` closes the run and is blocking. A filing gap (note rows anchored to a slug that no hub
row cites) → dispatch `signal-filer` in hub-repair mode scoped to exactly those rows, `bigin file apply`, re-run
`--full`. Lint unavailable → say so; never read an unavailable checker as a pass.

**Declared slug with no FEATURES.md row.** `file apply` refuses it; add the `proposed` row yourself (the
declared-slug exception, and the only FEATURES.md write this skill makes), then re-run `file apply`.

**Analysis.** After filing, `intake-analyst` reads the note against the current requirements of every feature it
anchored to and returns what the request changes, what it contradicts and what is still unclear or missing for
implementation. `note analysis-apply` rewrites the note's engine-owned `## Analysis`, adds each conflict and
question to `## Open Questions` (add-only; a new one parks the note `needs-clarification`), and holds every
**blocking** conflict's note row and hub row at `conflict` so transform drafts nothing over the current spec.
It is not a gate: a failed analysis is reported and the run goes on. Rules: `_bigin/stages/extract/4-analysis.md`.

**New hubs.** `file apply` reports `hubs_created`. For each, run `3-filing.md` § Step 2a (domain research) and
append its `## Domain Research` entry — the one write this skill still makes itself.

## Rules

- **Recall is the point.** A wrong row dies in the audit; a missing row is invisible forever.
- **Classify before typing** — as-is · pain · to-be. Classifying changes a row's `Type`, never whether it exists.
- **Never guess an anchor, never mint a slug from an agent's reading.** Only a slug a human typed into
  `declared_features:` at capture may gain a `proposed` FEATURES.md row (`3-filing.md` § The declared-slug exception).
- **The extractor is blind to themes; audit before filing; filing is serial; the note's status is set last** (the
  engine does this last in `file apply`).
- **Row numbers on a note are permanent ids** — the engine numbers, appends, and never renumbers.
- **Questions are add-only; ticking needs a filled `A:`.** An answer folds back to the note that asked (`answers`).
- **Never touch a UC or BR.** Hubs and the three registers only — and only through `file apply`.
- **Resume = re-run.** The vault and `_runs/<id>/results.jsonl` are the only state.
- **A removed request leaves the spec, with its reason — per ticket or per feature.** A cancelled ticket →
  `bigin note withdraw <INT> --reason "<their words>" [--by "<who, where, date>"]` (a Jira status mapped to
  `withdrawn` does it on the sweep). A dropped feature → `bigin feature withdraw <slug> --reason … --by …`. Never
  withdraw a meeting or email note, never delete a note or a row, never hand-edit a UC to take content out:
  applied rows become `retract` and the next transform run removes them through change sets
  (`4-analysis.md` § Withdrawal — a removed request leaves the spec).

## Stage 3 — Report

```text
run:       <RUN> — bigin run summary RUN
sources:   INT-###: N/N blocks read · unread: <what + why | none>
mix:       INT-###: as-is N · pain N · to-be N · derived N · why stated N of M (X% not stated)
audit:     INT-###: <self | independent (<trigger>)> — gaps N, narrowed N, inversions N, conflicts N
filed:     <slug>: N signals in M themed rows (#a-#b) · new hubs: <slugs + research entry>
analysis:  INT-###: affects UC-### (S#), BR-###, new goal "<title>" · conflicts N (blocking N: held <slug> #n) · questions N
registers: PP minted <ids> · PP matched <ids> · entities N · design N
parked:    INT-### awaiting an answer (N open) · awaiting a feature mapping
gate:      bigin lint --full: clean | repaired (<what>) | UNAVAILABLE (<why>) · coverage --stage file: missing N
tokens:    bigin metrics report --run RUN   (measured where usage was recorded; always an estimate from task files)
```

## Additional resources

- `references/agent-dispatch.md` — the fallback loop, the prompt shape for each agent, and the re-spawns.
- `cards/extractor.md`, `cards/auditor.md`, `cards/filer.md`, `cards/analyst.md` — what each agent reads (≤ 3 KB each).
- `_bigin/stages/extract/` — the human reference the cards are derived from.
