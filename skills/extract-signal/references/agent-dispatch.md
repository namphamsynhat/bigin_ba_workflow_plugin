# Subagent dispatch — extract stage (fallback loop, and what workflows/extract.js does)

Three named agents, each returning ONE JSON file the engine validates and writes. None of them has `Edit`;
`Write` is limited by its card to its own `.out.json`.

| # | Agent | Model | When | Card → output schema |
|---|---|---|---|---|
| 2a | `signal-extractor` | `sonnet` | every communication-mode note | `cards/extractor.md` → `signals` |
| 2b | `signal-auditor` | `sonnet`, one per note, never per batch | only when the audit is owed | `cards/auditor.md` → `audit` |
| 2c | `signal-filer` | `sonnet` | every note, **serially** | `cards/filer.md` → `filing` |

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

## After each agent

```text
BIN ingest <out> --kind <schema> --run <run>
    INVALID → SendMessage the listed errors to the SAME agent once ("rewrite <out> so it validates");
              still invalid → record the task failed, park the note, move on
BIN note write-signals <signals.out.json>      # prints {added, audit_owed}
BIN note audit-apply <audit.out.json>
BIN file apply <filing.out.json>               # prints {hub_rows, pp, en, hubs_created, status}
BIN metrics add --run <run> --stage extract --task <INT> --agent <name> --usage "<usage block>"
```

## The audit-owed test

Dispatch `signal-auditor` when ANY holds (`_bigin/stages/extract/2b-audit.md` § When the independent pass is owed):
any block is a transcript (however short) · `## Raw` ≥ ~300 lines · more than one block with an attachment or thread
among them · the extractor reported an unread block or `not stated` over 30% · its self-audit found an inversion or a
contradiction · its self-audit repaired more than 5 rows. Otherwise the self-audit stands — report `audit: self`.

## Re-spawns

- The extractor reports an unread block → re-dispatch scoped to that block (`mode: append`).
- `not stated` > 30% of requirement/feedback rows → re-dispatch scoped to those rows (`mode: repair`) to redo the
  Why search.
