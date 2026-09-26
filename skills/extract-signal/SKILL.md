---
name: extract-signal
description: This skill should be used when the ask is to extract signals, process the intake queue, drain 00-Inbox, or map intake to features. Drains the raw intake queue in 00-Inbox — extracts each communication-mode INT-### note's signals into a flat raw record on the note, audits that record against the source where the audit is owed, then anchors every signal to a FEATURES.md slug and files it onto that feature's Signal Log grouped by functional theme. Agents return JSON; the engine (`bin/bigin`) does every write. A signal that can't be anchored raises a written question instead of a guess. Codebase-mode notes are imported by `/bigin-intake` (`bigin intake codebase`) and never come here. Never drafts or edits a UC.
argument-hint: "[resume <run-id>]"
disallowed-tools: AskUserQuestion
---

# Extract Signal

Per `INT-###` note in `00-Inbox`: extract → audit (when owed) → file. Extract stage of extract → transform →
load. Never drafts or edits a UC or BR. **LLM for judgement, the engine for every write:** agents read a compact
worklist and return one JSON file; `bin/bigin` validates and writes it.

`BIN` below = `"${CLAUDE_PLUGIN_ROOT}/bin/bigin"` (run from the vault root).

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
RUN = $(BIN run new --stage extract --scope <n>-notes)
```

**With the Workflow tool** (preferred — orchestration lives in the script, not in this context):

```text
Workflow(scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/extract.js",
         args: {run: RUN, vault: ".", plugin_root: "${CLAUDE_PLUGIN_ROOT}", notes: [<INT ids>]})
```

Per note, in parallel: `worklist extract` → `signal-extractor` → `ingest` + `note write-signals`; when the
extractor reports `audit_owed`: `worklist audit` → `signal-auditor` → `note audit-apply`. Then filing, **serially**
(a later note's theme may extend a row an earlier note just filed): `worklist file` → `signal-filer` → `ingest` +
`file apply`. Then `lint --full` and `coverage --stage file`. Resume = re-run with the same `run`
(completed tasks are skipped via `run done`), or the Workflow tool's `resumeFromRunId`.

**Without it (B.5 fallback)** — the same steps, one `Agent` call per judgement task:

```text
for note in queue:                                   # extractors may run 4 at a time; filers never overlap
  BIN worklist extract <INT> --out _runs/RUN/tasks/<INT>.extract.in.json
  Agent(signal-extractor): "card <plugin>/cards/extractor.md · in <…>.extract.in.json · out <…>.signals.out.json"
  BIN ingest <out> --kind signals --run RUN         # invalid → SendMessage the errors to the same agent, once
  BIN note write-signals <out>                       # prints audit_owed
  owed → BIN worklist audit <INT> --out … ; Agent(signal-auditor) ; BIN ingest … --kind audit ; BIN note audit-apply <out>
  BIN worklist file <INT> --out … ; Agent(signal-filer) ; BIN ingest … --kind filing ; BIN file apply <out>
  BIN run record RUN --task filed:<INT> --status ok
  BIN metrics add --run RUN --stage extract --task <INT> --agent <name> --usage "<usage block>"   # per agent
BIN lint --full ; BIN coverage --stage file
```

Between steps read only the one-line agent reply and `BIN run summary RUN` (≤ 20 lines) — never an agent
transcript, never `## Raw`. **Never audit inline** in this context: either the extractor's self-audit stands or a
fresh `signal-auditor` is dispatched. The audit-owed triggers live in `2b-audit.md` § When the independent pass is
owed; report which depth ran on each note (`audit: self` vs `audit: independent (<trigger>)`).

**Gate.** `BIN lint --full` closes the run and is blocking. A filing gap (note rows anchored to a slug that no hub
row cites) → dispatch `signal-filer` in hub-repair mode scoped to exactly those rows, `BIN file apply`, re-run
`--full`. Lint unavailable → say so; never read an unavailable checker as a pass.

**Declared slug with no FEATURES.md row.** `file apply` refuses it; add the `proposed` row yourself (the
declared-slug exception, and the only FEATURES.md write this skill makes), then re-run `file apply`.

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

## Stage 3 — Report

```text
run:       <RUN> — BIN run summary RUN
sources:   INT-###: N/N blocks read · unread: <what + why | none>
mix:       INT-###: as-is N · pain N · to-be N · derived N · why stated N of M (X% not stated)
audit:     INT-###: <self | independent (<trigger>)> — gaps N, narrowed N, inversions N, conflicts N
filed:     <slug>: N signals in M themed rows (#a-#b) · new hubs: <slugs + research entry>
registers: PP minted <ids> · PP matched <ids> · entities N · design N
parked:    INT-### awaiting an answer (N open) · awaiting a feature mapping
gate:      bigin lint --full: clean | repaired (<what>) | UNAVAILABLE (<why>) · coverage --stage file: missing N
tokens:    BIN metrics report --run RUN
```

## Additional resources

- `references/agent-dispatch.md` — the prompt shape for each agent in the fallback loop, and the audit-owed test.
- `cards/extractor.md`, `cards/auditor.md`, `cards/filer.md` — what each agent reads (≤ 3 KB each).
- `_bigin/stages/extract/` — the human reference the cards are derived from.
