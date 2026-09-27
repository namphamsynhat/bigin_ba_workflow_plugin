# Migration — moving a vault from v1.8.x to v1.12.0

Run through `/bigin-upgrade-project` (§ 3b), which calls the engine. By hand, from the repo root:

```bash
B="$CLAUDE_PLUGIN_ROOT/bin/bigin"            # or the plugin checkout's bin/bigin
$B migrate plan --from 1.8.12 --to 1.12.0    # which steps are due
$B migrate all  --from 1.8.12 --to 1.12.0 --dry
$B migrate all  --from 1.8.12 --to 1.12.0    # snapshot → steps → links sync → hub refresh → status → stamp
$B lint --full                               # must be clean
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
- `bigin audit --baseline <snapshot.tgz>`: 11-point veracity and integrity audit across coverage, step numbering,
  unmodified history, and gate preservation.
- Engine write guards: `Doc.verify` and `hub.py` refuse any write where questions in `## Open Questions / Gates`
  or lines under `## Changelog` would be lost.
- Role card for `ux-brief-assembler` (`cards/ux-brief.md`) with lean JSON output contract.
- End-to-end fixture coverage for `workflows/transform.js`.


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
