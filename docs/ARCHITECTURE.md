# Architecture — the engine, the agents, and the contract between them

Plugin v1.12.0. The design principle of the restructure:

> **LLM for judgement, scripts for bookkeeping, JSON between them, one write per artifact.**

Everything the plugin guaranteed before — the written review gate, the traceability chain, as-built
discipline, never-renumber, add-only questions, `/approve-uc` as the only human approval — is still
guaranteed. It moved from "every agent re-reads and re-enforces the rule" to "one engine enforces it".

```
scripts/bigin / scripts/bigin.cmd   thin launchers → lib/bigin/cli.py (python3/python; Windows .cmd)
lib/bigin/              the engine — Python 3.9+, standard library only
workflows/*.js          Workflow-tool orchestration (fan-out, retries, resume)
agents/*.md             small agents (≤ 4 KB), JSON out, no Edit on vault files
cards/*.md              per-role instruction cards (≤ 3 KB) — what agents read
skills/*/SKILL.md       entry points; call scripts/bigin and dispatch agents
workspace/              conventions (human reference), stages, templates (+ *.guide.md)
hooks/hooks.json        PostToolUse → python lib/bigin/cli.py lint --hook --quiet (python3 fallback)
tests/                  fixtures (comm-vault, code-vault) + stdlib test runner
```

## 1. The engine (`lib/bigin/`)

The engine is **not** materialized into a project. Skills call
`python "${CLAUDE_PLUGIN_ROOT}/lib/bigin/cli.py" …` (fallback `python3` — portable on Windows cmd; or
`"${CLAUDE_PLUGIN_ROOT}/scripts/bigin"` / `scripts/bigin.cmd`).
Agents that cannot resolve `CLAUDE_PLUGIN_ROOT` (every subagent, including the interactive `bigin-ba`) use
`_bigin/bin/bigin` / `_bigin/bin/bigin.cmd` — shims `bigin launcher` generates with the installed plugin's
absolute path — and read their card at `_bigin/cards/<card>`. `/bigin-new-project` and
`/bigin-upgrade-project` run `bigin launcher`.
Global options: `--vault <root>` (default: discovered upward from cwd, or `$BIGIN_VAULT`) and `--json`.
Exit codes: `0` ok · `1` findings/missing (lint, coverage) · `2` refused (bad input, drift, stale file) ·
`64` usage.

| Module | Command(s) | Job |
|---|---|---|
| `vault.py` | — | Section-aware Markdown I/O. Headings count only at column 0 **outside** `<!-- -->` and fenced code. Frontmatter keeps key order, inline vs block list style and quoting. Every edit is a splice, so an untouched file round-trips byte-identically. `Vault.write` = verify (no lost heading, no untouched section or frontmatter key changed) → refuse if the file changed on disk since it was read → back up to `_runs/_backups/<date>/` → atomic replace → re-read verify → restore on mismatch. |
| `model.py` | — | Read-side model: UC steps/flows/§ 4/§ 5, BR statement, hub Signal Log (hub or `<slug>.signals.md`), note signal table. |
| `ids.py` | `mint uc\|br\|int\|route --spec` | Next id = highest in use (file names **and** `id:`) + 1, under `exclusive_file_lock` on `01-Requirements/.ids.lock` (fcntl on POSIX, msvcrt on Windows). Instantiates templates (structure, never guidance). `mint route` mints every `new` UC a uc-router Phase A proposed and writes `<route>.minted.json`. |
| `hub.py` | `hub refresh\|flip\|sweep\|citers\|fix-tables` | Replaces the retired `hub-bookkeeper` agent. `refresh`: `uc:` pointers, ## Use Cases, ## Requirement Readiness (one row per artifact; Ready ⟺ status ≠ needs-clarification ∧ 0 open questions ∧ nothing pending in the ledger or ## Discussion ∧ § 2 drafted), ADD-ONLY ## Open Questions / Gates mirror (ticks a mirror only when its source is ticked with an `A:`; coverage gaps mirrored), one Changelog line. Signal Log and Coverage Gaps are never edited — the write is refused if they change. Idempotent. |
| `mirror.py` | `mirror br`, `links sync` | § 4 statements ← the BR's current rule (never over a placeholder, never over a row that reads as a *different* rule — reported instead); enforcement points validated against live step/flow ids; `brs:` = § 4. `links sync`: BR `uc:` ⊇ mirroring UCs, UC `features:` ⊇ BR features, `sources:` ⊇ INT ids cited outside comments, FEATURES.md UC column. |
| `design.py` | `design scope\|items\|check\|close`, `worklist design`, `mint ux --count` | The design stage's lookups, from the UX spec on disk: Stage 1 scope (NEW / CHANGED / CURRENT per UC against `absorbed:`, the four gates, platform, mode; `DRAFTED` and `resume:` when a dead run left screens behind), the screens worker's worklist (in-scope UCs whole, cited BR/EN, open pain points, directives, principles, nav tree, sibling screens), Stage 5's requirement items matched forward by id, the mechanical half of the nineteen close checks (`block` vs `confirm` findings), and close (stamp `absorbed:`, status from the live question count, hub pointer + `uiux:`, questions mirrored with `(ref: UX-### § 6 Q<n>)`, the one UC `## Discussion` line, `designed:<slug>` on the run). Screen boundaries, flows, the flow review and whether an unmatched item is really on a screen stay with a model. |
| `qualify.py` | `qualify <slug> [--apply]` | Transform Stage 2's lookup gates per `new`/`held` Signal Log row: an open note question naming the row (reads `#7`, `row 34`, `rows 7, 10 and 14–16`), an attachment missing on disk, a cited note row that does not resolve. Returns `pass` / `held` (flipped with `--apply`) / `check` — the rows only a reader can weigh, each with exactly the text needed. Gate 4 (dedup) stays a judgement. |
| `status.py` | `status` | UC/BR status from a live open-question count; moves only between `draft` and `needs-clarification`. |
| `coverage.py` | `coverage --stage extract\|file\|transform` | Traceability. Row mode (default): every note signal row. Id mode (`--id-pattern` or project `coverage_id_pattern`): every rule-card id, optionally against `--universe`. Filed units whose hub rows are all question/conflict/held count as *parked*. |
| `lint.py` | `lint --full\|--hook [--quiet]\|--self-test\|--fix-citations` | The former `hooks/bigin-lint.py` (still there as a shim). v1.9 adds: comment-masked section parsing, ledger-aware staged-row check, split-Signal-Log support, and a tier-2 check that flags e-mail addresses, key-like tokens and internal hostnames in UC/BR/hub text. |
| `jsonschema_lite.py` + `schema/` | — | Draft 2020-12 subset validator; schemas `changeset`, `changesets`, `route`, `signals`, `audit`, `filing`, `adjudication`, `verdicts`, `result`, `rule-card`. |
| `changeset.py` | `apply <file\|dir> [--run] [--dry]` | **The only writer of UC/BR/hub content for new work** (§ 2). |
| `ledger.py` | `ledger list\|render\|release\|supersede` | Change sets gated on a question (§ 3). |
| `worklist.py` | `worklist route\|adjudicate\|extract\|audit\|file\|analyze\|release\|split\|coverage <scope> [--out]`, `context <ID> --sections` | Compact task inputs (§ 4). `route --phase a\|b` splits the router's input across its two dispatches; `file` ranks open questions elsewhere and reports the cut; `coverage` is the Stage 4b input for one feature's use-case set, with the two lookup lenses (`rule`, pain-point `goal`) pre-computed. |
| `questions.py` | `questions list\|pack\|sent`; `prematch` at intake | Open questions carry `(asked:)` / `(sent: … via …)`; a computed `[q:xxxxxx]` tag (hash of the words) names each. `list` ages and ranks by what a question blocks (open ledger change sets, UCs at needs-clarification); `pack` writes `06-Outbox/` paste files per Jira key or owner; a reply quoting a tag is recorded on its note as a pre-matched answer for the filer. Nothing is posted. |
| `digest.py` | `digest [--since date\|run] [--for ba\|client\|dev] [--write]` | The same vault facts for three readers, no LLM: came in (Capture history), changed (UCs/BRs updated since, Before / After), decided (Decision log, released ledger entries), waiting (`questions`), ready to approve (no open question or change set, `jira.approval_gate` ok), stale downstream (`cascade`), dev feedback (offshore comments on a ticket already in dev), spend (`metrics`). `--for client` moves every id into a trailing `(ref: …)`. |
| `intake/confluence.py` | `intake confluence --page <raw.json>` | One living INT note per Confluence page (`source: confluence`). High-water mark `conf:<pageId>@v<n>` in `source_ids`; the last body is kept in `00-Inbox/_raw/confluence/<id>.json`; a newer version is diffed by heading section — changed/added sections append one block each, a removed one a `removed` block. Shares `intake/common.py` (`append_blocks`, capture history) with Jira. |
| `metrics.py` quality · `evalgrade.py` | `metrics report --quality` · `metrics quality-add` · `eval prepare\|grade <run>` | Passive quality rows in `_runs/<id>/quality.jsonl` (unverified-quote rate, uncovered source %, auditor findings by kind, repair rounds, approved → draft flips) and question latency (`(asked:)` → `(answered:)`). `eval` stages and grades the golden set in `tests/evals/` by code only (recall, precision, type accuracy, inversions, routing lane/target); `workflows/eval.js` runs the real extractor/router on it — by hand, before a card, schema or model change. |
| `notes.py` | `note write-signals\|audit-apply <json>`, `file apply <filing.json>` | Engine half of extraction and filing. Note row ids are engine-assigned and permanent; the note's status is written last. `write-signals` also looks each row's `quote` up in `## Raw` (`quotes.py`): a row whose quote is absent is flagged `[unverified]`, over 10% unverified owes the audit, and source runs of ≥ 5 lines far from any verified quote are returned as `uncovered`. |
| `runs.py` | `run new\|summary\|done\|record`, `ingest <json> [--kind] [--run]` | `_runs/<id>/` run ledger; schema-validates an agent's output before anything applies it. |
| `metrics.py` | `metrics add\|report` | Token/agent accounting per run, budget overruns from project `budgets:`. `ingest --run` writes an **estimated** row for every agent output (card + task input + source lines + output, a lower bound) with no agent involved; `metrics add --usage` adds a **measured** one. The two are reported side by side, never summed. |
| `intake/` | `intake codebase\|communication` | Codebase rule-card import (no LLM) and locked note scaffolding (§ 6). |
| `migrate.py` | `migrate snapshot\|plan\|all\|discussion-to-ledger\|strip-guidance\|split-signal-log` | Vault format migrations (`docs/MIGRATION.md`). |
| `audit.py` | `audit [--baseline <tgz\|dir>] [--strict] [--id-pattern]` | Read-only invariant audit (C1–C12) against a pre-run snapshot: questions add-only, step ids kept, Signal Log rows kept, no automated approvals. |
| `cli.py` | `launcher` | writes `_bigin/bin/bigin` + `_bigin/bin/bigin.cmd` and refreshes `_bigin/cards/`. |
| `edit.py`, `util.py` | — | Shared write helpers (Changelog, version bump, question matching), ids, JSON. |

While `apply` runs it sets `BIGIN_BATCH=1`, which makes the PostToolUse hook silent — a transient
mid-apply state never reaches an agent's context.

## 2. The change set — the one contract between agents and the engine

`lib/bigin/schema/changeset.json`. One change set = one intended edit to one artifact:

```json
{"id": "cs-<run>-<n>",
 "trace": {"int": "INT-015", "note_rows": [375], "hub": "account-recovery", "hub_rows": ["23"], "xr": [], "evidence": []},
 "target": {"kind": "UC|BR|HUB|ENTITY_REF|DESIGN", "id": "UC-133 | new:<key> | <slug>", "section": "2", "field": "Trigger"},
 "op": "new_step_after", "anchor": {"ref": "S3", "sha": "<from the worklist>"},
 "cells": {"actor": "…", "system": "…"}, "text": "final text", "gate": null}
```

Ops: `new_step_after`, `replace_step`, `drop_step`, `new_flow`, `replace_flow`, `drop_flow`,
`set_field`, `append_note`, `mirror_br`, `add_question`, `answer_question`, `set_rule`,
`append_rule_clause`, `create_uc`, `create_br`, `link`, `add_directive`, `add_principle`, `flag_conflict`,
`unmirror_br` (the only op that removes a link — a rule moved off a UC, with a reason).

What `bigin apply` guarantees, so no agent has to:

- **Validate** every set against the schema (rejected sets are reported, never half-applied); duplicate ids refused.
- **Create first.** `create_uc`/`create_br` mint under the id lock; other sets in the batch point at them as `new:<key>`.
- **Per artifact, one write**, in a fixed order (structure → § 1/§ 6 → rule → § 4 mirrors → questions), then version bump,
  `updated:`, and ONE Changelog line carrying the trace and `cs: <ids>` (re-applying is a no-op — the ids are the record).
  Gated and drifted ids are recorded under `gated:` / `drift:` so they never count as applied.
- **Never renumber.** A new step takes the next unused `S#` and sits after its anchor; a placeholder `S1` is filled first;
  `drop_*` keeps the id as `Dropped — <reason>`; new flows take the next `A#`/`E#`.
- **Drift.** An anchor `sha` that no longer matches the current text → nothing is overwritten; ONE question naming
  both wordings is raised on the artifact. Text that already equals the proposal counts as applied (hand-applied).
- **Gate.** `gate.blocks: true` → the set goes to the ledger, its question to the artifact.
- **Review flag.** A § 2 change adds "§ 2 changed — flagged for review" to the Changelog line; status is untouched.
- **Mirrors after apply.** Traced hub Signal Log rows flip (`applied` when every set for the row landed and nothing is
  open in the ledger; `staged` when gated or drifted), then `links sync`, `hub refresh` of touched hubs, `status`
  recount of touched artifacts, `ledger render`.

## 3. The ledger (replaces staged `## Discussion` entries)

`01-Requirements/_ledger/<slug>.jsonl` — one line per gated change set: `id`, `state`
(`open | needs-judgement | released | superseded`), `artifact`, `question`, the full `changeset`.

- **What reviewers see:** `bigin ledger render` writes a read-only `## Pending changes` block into each affected UC/BR —
  every waiting change, its op, anchor, final text, and the question it waits on. `/approve-uc` refuses while one is open.
- **Release:** `bigin ledger release` finds each gate question on its artifact. Ticked with a filled `A:` → applied
  (the answered question then moves to the UC's Decision log). An answer that reads as a refusal ("no", "reject",
  "out of scope" …) is never applied blindly: the set becomes `needs-judgement`; `bigin worklist release` hands those to a
  judging agent whose `verdicts` file (`apply | supersede | revise`) settles them via `ledger release --verdicts`.
- `## Discussion` is human discussion only for new work. Legacy staged entries are converted by
  `bigin migrate discussion-to-ledger`.

## 4. How agents and the engine interact — the B.5 loop

Works with or without the Workflow tool:

1. The orchestrating skill runs `bigin worklist <stage> <scope> --out _runs/<id>/tasks/<task>.in.json`. The worklist
   holds only what the task needs (and only what THIS dispatch decides on: `worklist route --phase a|b` splits the
   router's input when its two phases are separate dispatches) — rows, anchor texts with their `sha`, UC cards (summary, steps, flows, § 4 ids, open
   questions), BR cards, a vault-wide UC title index — never whole files. `bigin context <ID> --sections 1,5` gives a
   comment-free slice of one artifact.
2. The agent prompt is its card path + the `.in.json` path + the `.out.json` path. The agent reads its card and the
   input, reads code or sources only when its card says so, writes the `.out.json`, and replies with ONE line
   (`OK <out> <counts>` or `BLOCKED <reason>`).
3. The orchestrator runs `bigin ingest <out> --run <id>`; schema errors go back to the same agent once; then
   `bigin apply` (or `note write-signals` / `file apply`).
4. The orchestrator never reads transcripts or prose reports — only `bigin run summary <id>` (≤ 20 lines).

## 5. Workflows (`workflows/*.js`)

Workflow scripts have no shell, so every engine step runs through a cheap *engine-runner* agent (`haiku`, low
effort) that executes exactly the given `scripts/bigin` commands and returns their JSON. Judgement agents are dispatched
by `agentType` with their card. **One runner per transition, not per command:** a runner call carries every command
up to the next judgement (validate → write → record → build the next worklist), because each spawn pays a fresh
agent's fixed cost. That is two runners per feature in transform and three per note in extract, plus a handful per
run; `tests/test_workflows.py` pins the counts.

| Script | Per unit | Steps |
|---|---|---|
| `transform.js` | feature (pipelined across features) | `worklist route --phase a` (index cards) → uc-router Phase A (`route`) → [ingest · `mint route` · `worklist route --phase b --spec`] (full cards for the routed UCs only) → uc-router Phase B (`changesets`) → [ingest · `apply` · `hub refresh` · record] → (code-grounded) `adjudicate.js` → once per run: impact, coverage, `lint --full`. A schema failure gets one repair round by the same judge. |
| `adjudicate.js` | conflict/held row | `worklist adjudicate` → one `code-adjudicator` per row (a second independent judge for P0/security rows; disagreement leaves it for a human) → `ingest` + `apply` |
| `eval.js` | golden-set case | `eval prepare` → `signal-extractor` (and `uc-router` where the case has a route worklist) per case → `eval grade` (code only). By hand, before releasing a card, schema or model change. |
| `extract.js` | note | `signal-extractor` (`signals`) → [ingest · `note write-signals --run` · `worklist audit`] — the **engine** returns `audit_owed` and `why_repair` → Why repair by the same extractor (`not stated` > 30%) → one quote/recall repair round by the same extractor (`unverified`, `uncovered`) → `signal-auditor` → `note audit-apply` where owed; then **serial** `signal-filer` per note → `file apply`; then `intake-analyst` per note → `note analysis-apply`; `lint --full` + `coverage --stage file` |

Resume: every workflow records task completion in `_runs/<id>/results.jsonl` (`bigin run record`) and skips what
`bigin run done <id>` lists; the Workflow tool's own resume caches unchanged agent calls. Writes are engine-only and
atomic, so a rate-limit stop leaves a clean resume point. Without the Workflow tool, the skill runs the same steps
with `Agent` calls (the B.5 loop above).

Model tiering (agent frontmatter): every judgement agent is pinned to `sonnet` (`uc-router`, `code-adjudicator`, `uc-splitter`, `bigin-ba`,
`signal-extractor`, `signal-filer`, `signal-auditor`, `intake-analyst`) so a session on another model cannot change the output; the design and
story workers are dispatched with `model: "sonnet"`; engine runners — `haiku`.

## 6. Two intake modes, one pipeline

```
                 COMMUNICATION MODE                         CODEBASE MODE
  intake   /bigin-intake (email, meeting, direct)      bigin intake codebase --cards <json|csv>
           verbatim note, SRC blocks                    one INT note per group, rule pack attached,
                                                        one signal row per card (no LLM)
  extract  signal-extractor → signals.json              (cards ARE the signals)
           signal-auditor when owed → audit.json
  file     signal-filer → filing.json                   feature from --assignment / card / capability /
           bigin file apply                              path; filed per (feature, theme) deterministically;
                                                        only the unmapped remainder goes to one filer task
  transform (identical)  route → changesets → apply → adjudicate (grounding: codebase|both) → status/coverage/lint
  load     design / approve-uc / sync-entities / stories (PRD retired 1.13.0)
```

`project.md` carries `grounding: communication | codebase | both`, `repos:` (read-only code roots),
`conflict_policy: code-first | ask`, `coverage_id_pattern`, `budgets`, `signal_log: split | inline`,
`engine: engine | legacy`. Codebase intake details: `docs/CODEBASE-INTAKE.md`.

## 7. Vault layout additions

| Path | Owner | Notes |
|---|---|---|
| `01-Requirements/_ledger/<slug>.jsonl` | engine | gated change sets |
| `01-Requirements/_features/<slug>.signals.md` | engine (append-only rows) | the Signal Log, once split |
| `_runs/<id>/` | engine | `plan.json`, `tasks/*.json`, `results.jsonl`, `metrics.jsonl` |
| `_runs/_backups/<date>/` | engine | a copy of every file before the engine rewrote it |
| `_runs/migrate-*.tgz` | engine | pre-migration snapshots of `01-Requirements/` + `00-Inbox/` |
| `_bigin/cards/` | plugin (materialized) | role cards |
| `_bigin/bin/bigin` (+ `bigin.cmd`) | generated by `bigin launcher` | engine shims for agents without `CLAUDE_PLUGIN_ROOT` |

Instantiated UCs/BRs/hubs carry one comment, `<!-- guide: _bigin/templates/<name>.guide.md -->`, instead of the
template's guidance blocks. The human-facing shape of UC/BR files (§ 1–§ 6, Changelog, Decision log) is unchanged.

## 8. Cards

`cards/<role>.md`, ≤ 3 KB: inputs, output schema, the 5–10 rules that role can actually break, one worked example,
the model tier and why. Each rule cites its source as `‹file § heading›`; `tests/test_phase34.py` fails if a cited
heading no longer exists in `workspace/conventions/` or `workspace/stages/`, so a card cannot drift silently.

## 9. What must not change

`/approve-uc` is the only way a UC becomes approved · raw intake is verbatim, note row ids permanent · questions are
add-only; ticking needs a filled `A:`; intent questions are never auto-ticked · steps are never renumbered · every
UC/BR keeps its trace to INT rows, hub rows and (codebase mode) rule ids · asymmetries are specified per surface ·
`repos/` is never written · no secrets, credentials, e-mail addresses, OTP-bypass values or internal hostnames are
reproduced (lint enforces the last one).

## 10. Tests

`python3 tests/run.py` (stdlib; pytest-compatible). Fixtures: `tests/fixtures/comm-vault/` (3 notes, 2 hubs, 4 UCs,
6 BRs, legacy staged entries) and `tests/fixtures/code-vault/` (a codebase note, 20 rule cards). Regenerate with
`python3 tests/fixtures/build_fixtures.py`.
