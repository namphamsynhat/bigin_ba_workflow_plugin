# Subagent dispatch — extract stage (fallback loop, and what workflows/extract.js does)

Four named agents, each returning ONE JSON file the engine validates and writes. None of them has `Edit`;
`Write` is limited by its card to its own `.out.json`.

| # | Agent | Model | When | Card → output schema |
|---|---|---|---|---|
| 2a | `signal-extractor` | `sonnet` | every communication-mode note | `cards/extractor.md` → `signals` |
| 2b | `signal-auditor` | `sonnet`, one per note, never per batch | only when the audit is owed | `cards/auditor.md` → `audit` |
| 2c | `signal-filer` | `sonnet` | every note, **serially** | `cards/filer.md` → `filing` |
| 2d | `intake-analyst` | `sonnet` | every filed note, in parallel (applies serial) | `cards/analyst.md` → `analysis` |

Codebase-mode notes have no 2a/2b: `bigin intake codebase` writes their rows and files them deterministically;
only its `--unmapped-out` remainder becomes one 2c classification task.

## The prompt — the same three lines for every agent

```text
Read your card <plugin>/cards/<card>.md, then the task input <vault>/_runs/<run>/tasks/<task>.in.json.
Write your JSON result to <vault>/_runs/<run>/tasks/<task>.out.json and nothing else.
Reply with one line: OK <out> <counts> | BLOCKED <reason>.
```

Add only per-run facts the agent cannot derive: a project override's text (never the whole override file),
"hub-repair mode: rows #…", "fold-in run: questions answered since last run". **Never paste a procedure** into a
prompt — two copies of one rule drift apart, and the card is the one home.

## The loop — per note

```text
for note in queue:                                   # extractors may run 4 at a time; filers never overlap
  bigin worklist extract <INT> --out _runs/RUN/tasks/<INT>.extract.in.json
  Agent(signal-extractor) → <INT>.signals.out.json
  bigin ingest <out> --kind signals --run RUN        # INVALID → SendMessage the errors to the SAME agent once
  bigin note write-signals <out> --run RUN           # prints {added, audit_owed, audit_reasons, why_repair?};
                                                     # records extracted:<INT> (and audit-owed:<INT>)
  why_repair present → SendMessage(same extractor): "REPAIR run (mode: repair): rows #… have Why `not stated`;
       redo the Why search; output only the rows whose Why you found, with n" → <INT>.whyrepair.out.json
       bigin ingest … --kind signals --run RUN ; bigin note write-signals <that file>
  audit_owed → bigin worklist audit <INT> --out … ; Agent(signal-auditor) ; bigin ingest … --kind audit --run RUN ;
       bigin note audit-apply <out> ; bigin run record RUN --task audited:<INT> --status ok
  bigin worklist file <INT> --out … ; Agent(signal-filer) ; bigin ingest … --kind filing --run RUN ;
       bigin file apply <out>                         # prints {hub_rows, pp, en, hubs_created, status}
  bigin run record RUN --task filed:<INT> --status ok
  bigin worklist analyze <INT> --out … ; Agent(intake-analyst) ; bigin ingest … --kind analysis --run RUN ;
       bigin note analysis-apply <out>                # prints {affected, conflicts, blocking, questions_added, …}
  bigin run record RUN --task analysed:<INT> --status ok
bigin lint --full ; bigin coverage --stage file
```

A schema error from `ingest` goes back to the SAME agent once ("rewrite <out> so it validates"); still invalid →
record the task failed, park the note, move on.

**Cost is recorded for you.** `bigin ingest --run` writes an estimated metrics row for every agent output (card +
task input + source lines + output). When a task notification carries a `<usage>` block, add the measured figure
too: `bigin metrics add --run RUN --stage extract --task <INT> --agent <name> --usage "<usage block>"`.

## Audit depth — the engine's call

`bigin note write-signals` decides: `audit_owed: true` with `audit_reasons` → dispatch `signal-auditor`; otherwise
the extractor's self-audit stands and the note is reported `audit: self`. The triggers are
`_bigin/stages/extract/2b-audit.md` § When the independent pass is owed. Never override the verdict in either
direction, and never audit inline.

## Re-spawns

- The extractor reports an unread block → re-dispatch scoped to that block (`mode: append`).
- `why_repair` rows (`not stated` over 30%) → the Why repair in the loop above. It is not an audit trigger.
