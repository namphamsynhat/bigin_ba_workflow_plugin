# Migration — moving a vault from v1.8.x to v1.12.0

Run through `/bigin-upgrade-project` (§ 3b), which calls the engine. By hand, from the repo root:

```bash
bigin() { python "${CLAUDE_PLUGIN_ROOT}/lib/bigin/cli.py" "$@"; }   # python3 if no python on PATH
bigin migrate plan --from 1.8.12 --to 1.12.0    # which steps are due
bigin migrate all  --from 1.8.12 --to 1.12.0 --dry
bigin migrate all  --from 1.8.12 --to 1.12.0    # snapshot → steps → links sync → hub refresh → status → stamp
bigin lint --full                               # must be clean
```

`--from` defaults to `workspace_version` in `_bigin/system/project.md`; `--to` defaults to the engine version.

## Per-version plan

| Version | Engine step | Changes on disk |
|---|---|---|
| **1.9.0** — engine + scripted bookkeeping | none | No format change. Hub-bookkeeper, `fix_*` backstops and agent-flipped rows are replaced by `bigin hub refresh / flip / sweep`, `mirror br`, `links sync`, `status`. The first `hub refresh --all` rewrites derived hub tables once (Readiness blocking reasons become specific, e.g. "2 open questions"). |
| **1.10.0** — change sets, ledger, single writes | `discussion-to-ledger` | Staged `## Discussion` entries become change sets; `01-Requirements/_ledger/` appears; `## Pending changes` blocks appear on UCs/BRs with gated sets. |
| **1.11.0** — workflow orchestration | none | `_runs/<id>/` appears on the first workflow run. |
| **1.12.0** — slim inputs | `strip-guidance`, `split-signal-log` | Guidance comments leave UC/BR/hub instances; each hub's Signal Log moves to `<slug>.signals.md`. `_bigin/cards/` materialized by the upgrade skill. |
| **1.12.1** — audit & hardening | none | No format change. `bigin audit --baseline <tgz>` checks baseline integrity; engine guards prevent question loss and Changelog loss; `ux-brief-assembler` card/JSON contract; e2e workflow fixture tests; codebase intake docs. |
| **1.12.2** — coverage, lint & audit hardening | none | No format change. `bigin coverage` classifies open-gated staged hub rows as parked; `bigin lint` tier 2 checks question-status rows carry a matching question; `bigin audit` check C12 verifies partial answers are folded or marked not settleable. |
| **1.12.3** — review fixes | none | No format change. Quoted frontmatter values decode YAML escapes (a `coverage_id_pattern: "XR-[A-Z]+-\\d{3}"` in `project.md` now matches); `bigin coverage` tolerates a ledger entry with `gate: null`; `ux-brief-assembler` card/skill wording aligned with its `.out.json` write. |
| **1.12.4** — Windows portability | none | No vault format change. Lint hook invokes `python lib/bigin/cli.py` (fallback `python3`) instead of the extensionless `bin/bigin` sh script. Adds `bin/bigin.cmd` and launcher-generated `_bigin/bin/bigin.cmd`; `exclusive_file_lock` (msvcrt/fcntl) for parallel mint/write; UTF-8 stdio in `cli.py`; workflow `run done` parsing tolerates CRLF; skills/docs define the engine as a shell function `bigin() { python …/cli.py "$@"; }` (a string-assigned `$BIN` does not survive word splitting); `bin/bigin` and the generated `_bigin/bin/bigin` probe `python3` then `python` for 3.9+; `.gitattributes` pins `*.cmd` to CRLF. Workflows call one path, `"<plugin_root>/bin/bigin"` (cmd.exe resolves it to `bigin.cmd` via PATHEXT; `args.bin` overrides). `BIGIN_LINT_BLOCKING=1` now blocks through PostToolUse JSON `{"decision": "block"}` with exit 0 instead of stderr + exit 2, so the hook's `|| python3` fallback never re-runs. Four skill frontmatters (`bigin-generate-design`, `bigin-transform-signal`, `bigin-upgrade-project`, `sync-entities`) move to `description: >-` for YAML; `bigin-upgrade-project`'s and `bigin-generate-design`'s descriptions are also shortened — re-check their triggers. |
| **1.13.0** — epics & user stories | none | `/bigin-generate-prd` retired (existing `02-PRD/` files stay, frozen; read as optional context only). New `/bigin-generate-stories` writes `03-Epics-Stories/EP-<NNN> <Feature>/` (epic, one `US-###` per use-case slice, `_snapshot/` prototype captures); new `/approve-story`. `bigin mint ep|us`, `bigin coverage --stage stories`, EP/US lint incl. the business-language word list. Re-run `/bigin-upgrade-project` to materialize `_bigin/stages/stories/`, the epic/story templates, and `cards/story-writer.md`. |
| **1.13.0** — Jira intake | none | New intake source `jira` (`/bigin-intake jira`, § Stage 2D): one living `INT-###` per ticket; `bigin intake jira --issue <raw.json>` appends only new comments, description revisions and changelog field changes, tags each author onshore/offshore, and re-opens the note for extract. New `project.md` keys `jira_provider`, `jira_site`, `jira_projects`, `jira_jql`, `jira_scope_marker`, `jira_onshore`, `jira_offshore` and a `## Jira status mapping` table (per project); new intake frontmatter `jira_*`. Lint checks Jira block integrity. Additive — re-run `/bigin-upgrade-project` to materialize the templates. |
| **1.13.0** — living-ticket extraction | none | `bigin note write-signals` accepts `scope` (agreed / dropped / open → a `[scope:x]` Notes prefix) and `supersedes` (the engine back-links `superseded by #n` on the earlier row, which stays), records `extracted_through: SRC-n`, and always reports `audit_owed` for `source: jira`. `bigin worklist extract` flags `new: true` blocks and lists `existing_rows` on a Jira note; `worklist file` passes scope/supersession to the filer. Rulebook: `2-extraction.md` § A living Jira ticket, `3-filing.md` § Living Jira tickets (dropped → rejected/deferred), `2-qualification.md` Gate 4c (a staged superseded row → `bigin ledger supersede`). Additive. |
| **1.13.0** — impact & suspect links | none | **Behaviour change:** a content change to an `approved` (or `enriched`/`consolidated`) UC/BR now sets it back to `draft` on the same `bigin apply` write (Changelog: `Status approved → draft …`), as `intake.md` § Feedback handling always documented; a question added/answered reverts nothing. Before 1.13.0 the engine left it `approved` and only flagged `§ 2 changed`. New `bigin cascade` derives `stale: [UC-###@ver]` on UX specs, epics and stories built on a UC that moved on (status never changed; cleared by re-stamping `absorbed`), run by every apply. New `bigin impact <INT-###|touched> [--write]` / `--ucs` walks the trace graph (direct · via shared rule · shared entity · sibling features · downstream UX/epics/stories with steps hit); the transform workflow's Close step regenerates each intake note's engine-owned `## Impact` section and `01-Requirements/_impact/INT-###.json`. Lint flags an out-of-date `stale:`. Run `bin/bigin cascade` once after upgrading to flag artifacts that already drifted. |
| **1.13.0** — story handoff trace | none | Stories carry `sources: [INT-###]` and `jira: [KEY]`, derived from their slices by `bigin mint us` and kept current by `bigin cascade` (run `bin/bigin cascade` once after upgrading to backfill existing stories; lint reports `story trace out of date` until then). `bigin mint us` accepts `delta_of: US-###` — a drifted approved story stays untouched, gains `delta: [US-###]`, and the new draft story carries only the change. `bigin mint ep` accepts `cr: true` — one `<Feature> — changes` epic per feature beside its normal epic (resolves the stories/1-scope.md CR-epic conflict). Templates: `user-story.md` (`sources`, `jira`, `delta_of`, `delta`), `epic.md` (`cr`). |

## The steps

### `bigin migrate snapshot`
`tar czf _runs/migrate-<stamp>.tgz 01-Requirements 00-Inbox`. Every real run of the steps below takes one first
(`migrate all` takes a single `_runs/migrate-<to>-<stamp>.tgz`), because vaults are often untracked by git. The
engine also keeps a per-file backup under `_runs/_backups/<date>/` for every file it rewrites.

### `bigin migrate discussion-to-ledger` (1.10.0)
Parses every legacy staged entry (`- **INT-###** (staged <date>) … → proposed: …`) in UC/BR `## Discussion`:

| Legacy destination | Change set |
|---|---|
| `new step after S4:` · `S6 becomes:` · `S6 is removed because` | `new_step_after` · `replace_step` · `drop_step` |
| `new flow E2:` · `A1 becomes:` · `A1 is removed because` | `new_flow` · `replace_flow` · `drop_flow` |
| `§ 4: add BR-090 …, enforced at S2` (several joined by ` · `) | `mirror_br` per BR |
| `§ 1 <Field> becomes:` · `§ 1 <Field> — add:` | `set_field` · `append_note` |
| `§ 6: …` | `append_note` on § 6 |
| `proposed rule:` · `rule becomes:` · `proposed rule (addition):` | `set_rule` · `append_rule_clause` |
| `§ 5 question:` | `add_question` |

- Mechanical kinds (§ 2/§ 3, § 4 mirrors) apply now. Prose kinds apply now too **unless** an open question on the
  same artifact traces to the same hub row or note rows — then they go to the ledger gated on that question.
- Hub rows are traced from the entry's `<slug> hub row #N` citation; afterwards `hub sweep` flips rows nothing cites
  any more.
- An entry is removed from `## Discussion` only when all its change sets landed (applied, already applied, gated, or a
  drift question raised). Unparseable entries (free-form proposals, "correction to the staged rule above") and
  invalid sets (a mirror of a BR with no settled statement, an enforcement point naming no step) **stay** and are
  listed — a human decides them.
- The converted sets are saved to `_runs/migrate-discussion-<stamp>/changesets.json`. Idempotent: a re-run finds
  nothing to convert.

### `bigin migrate strip-guidance` (1.12.0)
Removes from UC/BR/hub instances only comment blocks that match a known template guidance block (v1.8 templates in
`lib/bigin/legacy_templates/` plus the current ones), compared after dropping backticks and collapsing whitespace.
Any other comment stays. Inserts one `<!-- guide: _bigin/templates/<name>.guide.md -->` after the H1. Refuses a file
whose heading list or visible (comment-free) text would change. Reports bytes before/after.

### `bigin migrate split-signal-log` (1.12.0)
For each hub with a `## Signal Log`, writes `_features/<slug>.signals.md` (frontmatter `type: signal-log`, the
section verbatim) and replaces the hub's section body with a one-line pointer (the heading stays). Lint, coverage,
`hub flip/sweep/citers`, worklists and `file apply` read the companion file from then on; new hubs in a split vault
are created split.

### Hardening & verification (1.12.1)
No schema migration required. Upgrading to 1.12.1 activates:
- `bigin audit --baseline <snapshot.tgz>`: read-only invariant audit (checks C1–C12: lint, staged gating, coverage, add-only questions,
  step ids, structure, Signal Log rows, status, approvals, repos untouched, secrets, partial answers).
- Engine write guards: `Doc.verify` and `hub.py` refuse any write where questions in `## Open Questions / Gates`
  or lines under `## Changelog` would be lost.
- Role card for `ux-brief-assembler` (`cards/ux-brief.md`) with lean JSON output contract.
- End-to-end fixture coverage for `workflows/transform.js`.

### Hardening & verification (1.12.2)
No schema migration required. Upgrading to 1.12.2 activates:
- `bigin coverage`: note rows whose hub row is staged behind an open, gated ledger change set are correctly classified as parked (not missing).
- `bigin lint`: tier 2 check `check_question_rows` ensures Signal Log rows at status `question`/`conflict` carry a matching open question on the hub, destination artifact, or note.
- `bigin audit`: check C12 verifies that unticked questions with filled `A:` lines carry a `Folded (as-built half):` line, a `not settleable` marker, or a record in a PARTIALS ledger.


## Rollback

```bash
tar xzf _runs/migrate-<to>-<stamp>.tgz      # from the repo root: restores 01-Requirements/ and 00-Inbox/ exactly
```

Then set `workspace_version` in `_bigin/system/project.md` back to the old value. A single file can be restored
from `_runs/_backups/<date>/<relpath>@<stamp>`.

## Legacy hatch

For one minor version, `engine: legacy` in `_bigin/system/project.md` tells skills to keep the v1.8.x behaviour
(staged `## Discussion` entries, agent bookkeeping), so a half-migrated vault can finish a run. The next upgrade
removes the hatch; switch back to `engine: engine` and run `migrate all`.

## Recommended order for a vault mid-run (e.g. Agoyu)

Finish the in-flight run on v1.8.12 → upgrade to 1.9 (no format change) → 1.10 converts leftover gated Discussion
entries into the ledger → 1.12 strip + split. `bigin coverage --stage transform` should report the same numbers
before and after.
