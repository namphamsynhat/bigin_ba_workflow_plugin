# Bigin BA workflow plugin — restructure plan (Phases 1–4)

Plugin root: `/Users/nampham/Documents/Bigin/bigin_ba_workflow_plugin` (v1.8.12 at time of writing).
Executor: a coding agent (e.g. Antigravity). This document is self-contained.
Phase 0 (finishing the in-flight Agoyu run without plugin changes) is a separate plan:
`/Users/nampham/Documents/Bigin/Agoyu_refactor/analysis/ba/PHASE-0-PLAN.md`. Its scripts
(`analysis/ba/vaultlib.py`, `foldin_mirrors.py`, `sync_links.py`, `hub_refresh.py`, `sweep_applied.py`,
`set_status.py`, `sync_uc_pointers.py`, the backstops) are the seed code for Phase 1 — port them, don't rewrite.

---

## Part A — Why the plugin is expensive (evidence from the Agoyu run, 2026-09-26)

| Measure | Value |
|---|---|
| Worker agents dispatched in one transform run | ~350 |
| Tokens per worker (usage blocks) | 60k–180k, typically 100–150k |
| Estimated worker tokens for the run | ~40M, plus a coordinator context that grew every turn |
| Share of every instantiated UC that is template guidance comments | 37% (1.5 MB of 4.1 MB, 213 UCs) |
| Average hub size / largest | 68 KB / 214 KB; 60% of hub bytes are the Signal Log |
| Rulebook text a fold-in worker loads before touching a file | ~50–60 KB (stage file + use-case.md + questions.md + override + CLAUDE.md) |
| Readiness rows the hub-bookkeeper (LLM) got wrong, corrected by a script | 87, 80, 40 on three hubs |

Root causes, in order of cost:
1. **Double write.** Every UC/BR change is staged as final text in `## Discussion`, then a second run's Stage 1
   re-reads every artifact and copies it into its section. § 2/§ 3 changes need a third agent (uc-applier).
   One second pass = 117 extra fold-in workers for ~4,200 entries.
2. **LLM doing bookkeeping.** hub-bookkeeper, row flips, readiness, § 4 mirror copying, `brs:`/`uc:`/`sources:` sync,
   lint repair — all deterministic, all done by agents, all needing script backstops afterwards.
3. **No shared tooling.** Nearly every worker wrote its own Markdown parser. Result: a truncation incident (regex
   matched a heading inside an HTML comment) and scratch-file collisions between parallel workers.
4. **Fat artifacts, whole-file reads.** Workers re-read 37% boilerplate and whole 68–214 KB hubs to change a few
   lines. Each tool call re-sends everything already read, so an early large read is paid on every later call.
5. **Whole rulebooks per worker.** Conventions are written for humans and loaded whole by agents that need 3 KB.
6. **Orchestration in the model's context.** The coordinator dispatches turn by turn and reads 2–5 KB prose reports.
7. **Advisory PostToolUse lint on every Write/Edit** injects findings into the writing agent's context on every
   call, including mid-change states it already knows are transient.

Contrast — `code-modernization` `workflows/extract-rules.js`:
- orchestration is a JS workflow script (loops, `parallel`, dedup, loop-until-dry) — state lives in code;
- workers get short inline prompts (~1–2 KB) and a narrow task ("read ONLY the cited location");
- workers return **schema-validated JSON**; the caller writes the final document **once** from structured data;
- verification is targeted (one referee per rule) and escalated only where it matters (P0 panel).

**Design principle for the restructure:** *LLM for judgement, scripts for bookkeeping, JSON between them, one write
per artifact.* Everything the plugin guarantees today (written review gate, traceability chain, as-built discipline,
never-renumber, add-only questions, `/approve-uc` human decision) is preserved — it moves from "every agent re-reads
and re-enforces the rule" to "one engine enforces it".

---

## Part B — Target architecture

### B.1 Directory layout (after Phase 4)

```
bigin_ba_workflow_plugin/
  bin/bigin                      # thin launcher: python3 "$(dirname "$0")/../lib/bigin/cli.py" "$@"
  lib/bigin/                     # the engine (pure Python 3.9+, stdlib only)
    cli.py                       # argparse front door, one sub-command per module
    vault.py                     # section-aware Markdown I/O (frontmatter, sections, tables), atomic write + verify
    ids.py                       # id minting with a file lock (INT/UC/BR/EN/PP/UX)
    schema/                      # JSON Schemas: changeset, signal, filing, route, adjudication, result
    changeset.py                 # validate + apply change sets (the ONLY writer of UC/BR/hub content)
    ledger.py                    # gated change sets waiting on a question
    hub.py                       # Signal Log store + regeneration of every derived hub table
    mirror.py                    # § 4 rule mirrors, links (brs/uc/features/sources), pointers
    status.py                    # status from live re-count (was set_status)
    coverage.py                  # traceability checks (generalised check_xr_coverage)
    lint.py                      # bigin-lint moved here; hooks call it
    intake/
      communication.py           # note scaffolding helpers for email/meeting/direct intake
      codebase.py                # rule-card import (extract-rules output) → INT notes + signal tables
    worklist.py                  # compact JSON worklists / context slices for agents
    metrics.py                   # token/agent accounting per stage
  workflows/                     # Workflow-tool scripts (Phase 3)
    extract.js
    transform.js
    adjudicate.js
  agents/                        # fewer, smaller agents; each ≤ 4 KB, JSON out
  cards/                         # per-role instruction cards (≤ 3 KB), what agents actually read
  skills/                        # SKILL.md files become thin orchestration docs that call bin/bigin + agents
  workspace/                     # conventions (human documentation), stages, templates
  hooks/                         # hooks.json → bin/bigin lint --hook (quiet mode)
  tests/                         # fixtures + pytest-style tests for lib/bigin
  docs/                          # this plan, ARCHITECTURE.md, MIGRATION.md
```

Materialized into a project by `/bigin-new-project` / `/bigin-upgrade-project` (unchanged contract):
`_bigin/{conventions,stages,templates,cards}` (plugin-owned) and `_bigin/system/project.md` (project-owned).
The engine is NOT copied; skills call `"${CLAUDE_PLUGIN_ROOT}/bin/bigin"`. Subagents that cannot resolve
`CLAUDE_PLUGIN_ROOT` never call the engine — the orchestrating skill does (see B.5).

### B.2 Vault layout changes

| Today | After | Why |
|---|---|---|
| `_features/<slug>.md` holds Signal Log + all derived tables | `_features/<slug>.md` (summary: Use Cases, Readiness, Open Questions/Gates, Coverage Gaps, Design Directives, Changelog) + `_features/<slug>.signals.md` (Signal Log only) | 60% of hub bytes leave the file agents read most |
| UC/BR `## Discussion` holds staged final text | `## Discussion` is human discussion only. Pending changes live in `01-Requirements/_ledger/<slug>.jsonl` and are rendered read-only into a `## Pending changes` block by `bigin ledger render` | no double write; reviewers still see what is pending |
| Every UC carries the template's guidance comments | Instantiated UC carries one comment: `<!-- guide: _bigin/templates/use-case.guide.md -->` | −37% UC bytes |
| Run state spread across ad-hoc files | `_runs/<run-id>/` : `plan.json`, `tasks/*.json` (agent outputs), `results.jsonl`, `metrics.jsonl`, `report.md` | resumable, machine-readable, never re-read by agents |

The human-facing shape of UC/BR files (sections § 1–§ 6, Changelog, Decision log) does NOT change.

### B.3 The change set — the one contract between agents and the engine

`lib/bigin/schema/changeset.json` (JSON Schema draft 2020-12). One change set = one intended edit.

```json
{
  "id": "cs-<run>-<n>",
  "trace": {"int": "INT-015", "note_rows": [375, 377], "hub": "account-recovery", "hub_rows": ["23"],
            "xr": ["XR-VALI-370"], "evidence": ["repos/backend:Packages/User/Requests/ResetCompleteRequest.php:rules :16"]},
  "target": {"kind": "UC|BR|HUB|ENTITY_REF|DESIGN", "id": "UC-133", "section": "1|2|3|4|5|6|rule|title",
             "field": "Trigger (optional, for § 1)"},
  "op": "set_field|append_note|new_step_after|replace_step|drop_step|new_flow|replace_flow|drop_flow|
         mirror_br|add_question|answer_question|set_rule|append_rule_clause|create_br|create_uc|link",
  "anchor": {"ref": "S3", "sha": "<sha1 of current anchor text, filled by the worklist>"},
  "text": "final text, exactly as it should land",
  "gate": null | {"question": "…", "owner": "client|team", "blocks": true},
  "flags": {"review": true}
}
```

Engine rules (`changeset.py apply`), replacing what agents re-implement today:
- **Validate** against schema; target exists (or `create_*`); anchor `sha` matches → else **drift**: do not apply,
  add ONE question naming both wordings (the `1-foldin.md` § human-edited rule), mark result `drift`.
- **Gate:** `gate.blocks` → append to the ledger, add the `- [ ] Q:` to the artifact (§ 5 / BR Open Questions) and
  mirror it to the hub. Else apply now.
- **Ops enforce invariants:** never renumber (`new_step_after` mints the next unused `S#` and places the row after the
  anchor); `drop_*` keeps the id with `Dropped — <reason>`; `mirror_br` copies the BR's current rule statement and
  validates the enforcement point; `answer_question` moves the line to the Decision log; questions are add-only.
- **One write per artifact per apply call**, backup + post-write verification (`vault.py`), version bump, one
  Changelog line carrying `trace` (INT ids, hub rows, XR ids), review flag when § 2 changed, `status` untouched.
- **Mirrors after apply:** hub Signal Log row → `applied` when all its change sets landed; derived hub tables
  regenerated; links synced. No agent does this.
- **Ledger release:** `bigin ledger release` re-checks each gated change set; when its question has a filled `A:`
  and is ticked, it applies (or, if the answer contradicts it, marks it `superseded` and reports).

### B.4 Two intake modes, one pipeline

```
                 COMMUNICATION MODE                         CODEBASE MODE
  intake   /bigin-intake (email, meeting, direct) ─┐   bigin intake codebase --cards <json> ─┐
           verbatim note, SRC blocks               │   one INT note per capability group,    │
                                                   │   one signal row per rule card (script) │
  extract  signal-extractor (LLM, JSON rows)       │   (no LLM extraction: cards ARE signals) │
           signal-auditor (LLM, when owed)         │   card-referee only if the card lacks a │
                                                   │   verified citation                     │
  file     signal-filer → JSON filing decisions ───┴── feature mapping: from card metadata /  ┘
           (anchor, theme, type, questions)             rule-assignment; LLM only for unmapped
           bigin file apply  (script writes hub Signal Log + registers + note status)
  transform  (identical for both modes)
     route     uc-router Phase A/B → JSON route + change sets
     adjudicate (codebase mode, or any project with repos:)  code-adjudicator per conflict (JSON verdict)
     apply     bigin apply  (engine; ledger for gated sets)
     status    bigin status · bigin coverage · bigin lint --full
  load     design / approve-uc / sync-entities / prd — unchanged
```

`project.md` gains `grounding: communication | codebase | both` and `repos:` (list of read-only code roots with
their role). `grounding: codebase|both` enables the adjudication stage and the codebase intake. Agoyu is
`grounding: both` (it has code and could later receive client mail).

### B.5 How agents and the engine interact (works with or without the Workflow tool)

1. Orchestrating skill runs `bigin worklist <stage> <scope> --out _runs/<id>/tasks/<task>.in.json`. The worklist
   contains ONLY what the task needs: the rows, the anchor texts with their `sha`, the target section excerpts
   (via `bigin context <ID> --sections 2,3`), candidate UC ids and titles — not whole files.
2. Agent prompt = its card path + the `.in.json` path + the `.out.json` path. The agent reads its card and the input,
   reads code/sources only if its card says so, writes `.out.json` (schema-validated by the engine on ingest), and
   replies with ONE line (`OK <task> <counts>` or `BLOCKED <reason>`).
3. Orchestrator runs `bigin ingest _runs/<id>/tasks/<task>.out.json` → validation errors go back to the same agent
   (resume via SendMessage) once; then `bigin apply`.
4. The orchestrator never reads agent transcripts or prose reports; it reads `bigin run summary <id>` (≤ 20 lines).

---

## Part C — Phases

Each phase ships as its own plugin minor version, with `/bigin-upgrade-project` migrating existing vaults, and must
pass `tests/` before merge. Phases are ordered so each one pays for itself even if later ones slip.

### Phase 1 — Engine and scripted bookkeeping (target v1.9.0)

Goal: every deterministic step becomes a `bin/bigin` sub-command; agents stop doing bookkeeping. Vault format unchanged.

Tasks:
1. **`lib/bigin/vault.py`** — port `Agoyu_refactor/analysis/ba/vaultlib.py`. Requirements:
   - Frontmatter parse/emit preserving key order and inline `[a, b]` list style.
   - Section tree: headings recognised only at column 0, outside `<!-- -->` and fenced code.
   - Table read/write with `|` escaping; tolerate the known split-table defect (fix_split_tables logic).
   - `write()` = backup → write → re-read verify (all `## N.` headings present, frontmatter parses, no unexpected
     line loss) → restore on failure.
   - Test: byte-identical round trip over a fixture vault AND over the Agoyu vault (read-only copy).
2. **`ids.py`** — `bigin mint uc|br|int --spec spec.json` with an `fcntl` lock file `01-Requirements/.ids.lock`.
   Port `mint_uc.py` semantics (skeleton from template, hub pointer). Parallel-safe.
3. **`hub.py`** — `bigin hub refresh <slug|--all>` replaces the `hub-bookkeeper` agent entirely:
   Use Cases table; Requirement Readiness (one row per artifact, never ranges; Ready rule = status ≠
   needs-clarification ∧ 0 open questions ∧ nothing pending in the ledger/Discussion); Open Questions/Gates ADD-ONLY
   mirror; Changelog line; `updated:`. Port `hub_refresh.py`, `mirror_br_questions.py`, `fix_readiness.py`,
   `dedupe_hub_questions.py` (exact duplicates only), `sync_uc_pointers.py`. Signal Log and Coverage Gaps untouched
   (assert byte-identical).
   `bigin hub flip <slug> <row>=<status>[:<dest>][@note]` and `bigin hub sweep` (port `flip_rows.py`,
   `sweep_applied.py`, `row_citers.py`).
4. **`mirror.py`** — `bigin mirror br --all|<UC>` (§ 4 rows from BR current statements, enforcement-point
   validation, `brs:`), `bigin links sync` (BR `uc:` ⊇ mirroring UCs; UC `features:` ⊇ BR features; `sources:` ⊇
   cited INT ids; FEATURES.md UC column).
5. **`status.py`, `coverage.py`, `lint.py`** — port `set_status.py`; generalise `check_xr_coverage.py` into
   `bigin coverage --stage extract|transform [--id-pattern 'XR-[A-Z]+-\d+']` (for communication-mode projects the
   traced unit is the note row id instead of an XR id); move `hooks/bigin-lint.py` into `lib/bigin/lint.py`, keep
   `hooks/bigin-lint.py` as a 3-line shim for back-compat.
6. **Quiet hook** — `hooks.json` PostToolUse runs `bin/bigin lint --hook --quiet`: print only findings for the file
   just written, max 5 lines, and nothing at all when `BIGIN_BATCH=1` is set (the engine sets it while applying).
7. **Skill edits (text only)** — in `bigin-transform-signal`, `extract-signal`, `approve-uc`, `sync-entities`,
   `bigin-run`: replace every "dispatch hub-bookkeeper" / "run fix_*.py backstop" / "the orchestrator flips the row"
   instruction with the corresponding `bin/bigin` command. Delete `agents/hub-bookkeeper.md` (keep a stub that says
   "replaced by `bigin hub refresh`" for one version).
8. **Tests** — `tests/fixtures/comm-vault/` (3 INT notes from email/meeting, 2 hubs, 4 UCs, 6 BRs) and
   `tests/fixtures/code-vault/` (1 codebase INT note with 20 rule cards, 2 hubs, 3 UCs). Tests for every command:
   idempotence (running twice = no diff), ADD-ONLY questions, no renumbering, readiness truth table, lint clean.

Acceptance:
- On a copy of the Agoyu vault: `bigin hub refresh --all && bigin links sync && bigin hub sweep && bigin lint --full`
  gives 0 findings and changes only derived tables, links and statuses (diff review).
- No skill text still instructs an agent to edit a hub's derived tables.
- Expected saving: removes ~35 bookkeeper runs + all backstop cycles per transform run.

### Phase 2 — Change sets, the ledger, and single writes (target v1.10.0)

Goal: agents emit change sets; the engine applies them once; `## Discussion` staging and the fold-in pass disappear
for new work. This is the largest saving.

Tasks:
1. **Schemas** in `lib/bigin/schema/`: `changeset`, `route` (Phase A output: signal → UC id | `new` with title/goal),
   `filing` (note row → slug, theme row, type, question), `signal` (extractor row), `adjudication` (verdict),
   `result` (per-task summary). Version them (`"$schema_version": 1`).
2. **`changeset.py`** — `bigin apply <file|dir> [--dry]` implementing B.3 exactly; `bigin ingest` (validate +
   store under `_runs/`). Idempotent: re-applying an applied change set is a no-op (match on `id` recorded in the
   artifact Changelog).
3. **`ledger.py`** — `bigin ledger list|render|release|supersede`. `render` writes the read-only
   `## Pending changes` block into each affected UC/BR (so `/approve-uc` reviewers see pending text, as today).
4. **Worklists** — `bigin worklist route <slug>` (qualified rows + candidate UCs with § 1 summary and step ids +
   anchors with sha), `bigin worklist adjudicate <slug>`, `bigin context <ID> --sections …`.
5. **Agents rewritten to JSON-out** (each agent file ≤ 4 KB; instructions moved to `cards/`):
   - `uc-router` → reads worklist, outputs `route.json` (Phase A) then `changesets.json` (Phase B, resumed). No file
     writes. `tools: Read, Grep, Write` (Write limited by card to its own `.out.json`).
   - `uc-applier` → **deleted**; § 2/§ 3 edits are `new_step_after`/`replace_step`/`new_flow` change sets.
   - `uc-splitter` → outputs a split plan as change sets (`drop_step` on source + `create_uc`/`new_flow` on targets).
   - `signal-filer` → outputs `filing.json`; `bigin file apply` writes hub rows, registers, note Feature/Status
     columns and note status (last).
   - `signal-extractor` / `signal-auditor` → output `signals.json` / `audit.json`; `bigin note write-signals`
     writes the `## Extracted signals` table (row ids permanent, append-only repairs).
6. **Stage files rewritten** — `workspace/stages/transform/1-foldin.md` shrinks to "run `bigin ledger release`";
   `4-sync.md` Part 2 (applier sweep) becomes "`bigin apply`"; `3-lane-*.md` describe WHAT a change set must contain,
   not how to edit files.
7. **Back-compat fold-in** — `bigin migrate discussion-to-ledger`: parse legacy staged Discussion entries (the shape
   documented in `workspace/conventions/use-case.md` § Discussion) into change sets; mechanical kinds (§ 4 mirrors,
   § 2/§ 3 destinations) convert automatically; § 1/§ 5/§ 6 prose entries convert to `set_field`/`append_note` with
   the text verbatim; anything unparseable stays in Discussion and is listed. `/bigin-upgrade-project` runs it.
8. **`approve-uc`** — reads the ledger block and blocks approval while a gated change set for that UC is open.

Acceptance:
- Fixture comm-vault: an end-to-end transform run produces the same UC/BR content as v1.8.12 would after its second
  pass, in ONE run, with zero `## Discussion` staging (golden-file diff).
- Drift test: hand-edit an anchor, re-apply → drift question raised, nothing overwritten.
- Gate test: change set with `gate.blocks` → ledger + question; answer it → `ledger release` applies it.
- No agent in `agents/` has `Edit` on UC/BR/hub files except `bigin-ba` (interactive).

### Phase 3 — Workflow-script orchestration (target v1.11.0)

Goal: fan-out, retries and sequencing move from the coordinator's context into scripts, like `extract-rules.js`.
The skills remain the entry points; they call the Workflow tool when available and fall back to the B.5 loop.

Tasks:
1. **`workflows/transform.js`** — per feature (parallel across features, sequential within one):
   `worklist route` → `agent(uc-router, schema: route)` → `mint` (engine, serial, locked) →
   resume router Phase B `schema: changesets` → `bigin apply` → (if `grounding` has code and the feature has
   `conflict`/`held` rows) `adjudicate` sub-pipeline → `bigin hub refresh` → `bigin coverage` → return
   `{feature, applied, gated, drift, questions, coverage}`. Enforce ≤ N concurrent agents (config, default 6).
2. **`workflows/adjudicate.js`** — per conflict pair: one `code-adjudicator` referee (`schema: adjudication`: winner
   row, loser row, evidence `repo:path:symbol :lines`, custom-layer verdict, settled|not_settleable + reason) →
   engine applies supersede/tick/transform. Optional second judge only for rows tagged P0/security (mirrors the
   extract-rules P0 panel).
3. **`workflows/extract.js`** — communication mode: per note `signal-extractor` → (audit owed?) `signal-auditor` →
   `bigin note write-signals` → per batch serial `signal-filer` → `bigin file apply` → `bigin lint --full`.
   Codebase mode skips extractor/auditor (see Phase 4 task 4).
4. **Run ledger & resume** — every workflow writes `_runs/<id>/plan.json` and `results.jsonl`; re-running with the
   same run id skips completed tasks (the Workflow tool's resume + our `results.jsonl`). A rate-limit stop leaves
   a clean resume point instead of half-written files (writes are engine-only and atomic).
5. **Skill fallback** — if the Workflow tool is not available or not opted in, the skill runs the same steps with
   `Agent` calls, but still reads only `bigin run summary` between steps.
6. **Model tiering in agent frontmatter** — `uc-router`, `code-adjudicator`, `uc-splitter`: `opus`/`inherit`;
   `signal-extractor`, `signal-filer`: `sonnet`; `signal-auditor` (mechanical cross-check), card-referee: `sonnet`;
   anything purely classificatory: `haiku`. Record the choice and the reason in each card.

Acceptance:
- Fixture code-vault transform completes via `workflows/transform.js` with the coordinator context under 30k tokens
  (measure via `metrics.jsonl`).
- Kill the run mid-feature → re-run resumes, no duplicate Changelog lines, lint clean.

### Phase 4 — Slim inputs: cards, lean artifacts, codebase intake (target v1.12.0)

Tasks:
1. **Role cards** `cards/<role>.md` (≤ 3 KB each): router, extractor, auditor, filer, adjudicator, splitter,
   design-screens, prd-writer. Each card = inputs, outputs (schema name), the 5–10 rules that role can actually
   violate, and 1 worked example. Conventions in `workspace/conventions/` stay as the human reference and the source
   the cards are derived from; add a test that every rule id cited in a card exists in a convention (so they cannot
   drift silently). Agents read their card, never whole convention files.
2. **Lean UCs** — split `workspace/templates/use-case.md` into `use-case.md` (skeleton, one guide comment) and
   `use-case.guide.md` (all current guidance). `bigin migrate strip-guidance` removes the repeated comment blocks
   from instantiated UCs (only exact template comment blocks; anything else is left). Same for `br.md`,
   `feature-hub.md`.
3. **Hub split** — `bigin migrate split-signal-log`: move `## Signal Log` into `<slug>.signals.md`; lint, hub,
   coverage, row_citers and all stage docs read it from there. Agents get Signal Log rows only through worklists.
4. **Codebase intake** — `bigin intake codebase --cards <path.json> [--assignment <map.json>] [--group-by capability]`:
   - Accepts the `code-modernization:modernize-extract-rules` output (`analysis/_rules-store.json` shape: `rules` map
     of `{name, category, priority, source, plainEnglish, given, when, then, …}`) and a generic JSON/CSV card format
     (documented in `docs/CODEBASE-INTAKE.md`).
   - Writes one INT note per group (`kind: requirement`, `source: codebase`, provenance header, asymmetry warning),
     the rule pack as its attachment, and the `## Extracted signals` table directly — one row per card, XR/card id
     verbatim, Cites as Source, suspected-defect and SME-question as separate `problem`/`question` rows. No LLM.
   - Feature mapping: use `--assignment` when given; otherwise map by capability/module heuristics; send only the
     unmapped remainder to one `signal-filer` classification task (JSON).
   - Filing groups rows by (feature, card theme) deterministically; LLM filing only for rows flagged ambiguous.
   - Marks each note with `grounding: codebase` so transform enables adjudication and treats code as the tie-breaker
     (today this lives only in the Agoyu local override "Conflict resolution — read the code first"; promote it to a
     documented plugin option `conflict_policy: code-first | ask` in `project.md`).
5. **Communication mode keeps its extraction** — email/meeting/transcripts still need the extractor + auditor
   (recall matters, sources are prose). Improvements there: extractor reads SRC blocks by line range from the
   worklist (no whole-note reads), writes `signals.json`; auditor runs only when `audit_owed` (unchanged rule).
6. **Metrics & budgets** — `bigin metrics add` (skills call it with each task-notification usage block);
   `bigin metrics report <run>` prints tokens per stage/feature/agent. `project.md` gains
   `budgets: {transform_per_feature_tokens: …}`; the run report flags overruns.
7. **`agents/bigin-ba.md`** (48 KB) — split into the routing table (≤ 6 KB) + cards it loads on demand
   (review flow, answer-it-yourself triage). It is the interactive agent; keep its behaviours, shrink its always-loaded
   text.

Acceptance:
- Fixture code-vault: codebase intake of 20 cards → notes + hub rows with 0 LLM calls (except unmapped rows).
- Agoyu vault copy after `strip-guidance` + `split-signal-log`: UC bytes −30% or more, hub summary files −55% or
  more, `bigin lint --full` clean, `bigin coverage --stage transform` unchanged.
- Card/convention drift test passes.

---

## Part D — Migration and rollout

1. Each phase: bump `plugin.json` version; `/bigin-upgrade-project` detects the vault's `workspace_version` and runs
   the migrations for every phase in between (`bigin migrate --from <v> --to <v> --dry` first, then for real).
2. Every migration: snapshot the vault (`tar czf _runs/migrate-<v>.tgz 01-Requirements 00-Inbox`) because vaults
   are often untracked by git; print a diff summary; lint must be clean after.
3. Order of adoption for the Agoyu vault: finish Phase 0 on v1.8.12 → upgrade to Phase 1 (no format change) →
   Phase 2 migration converts any leftover gated Discussion entries to the ledger → Phase 4 strip/split.
4. Keep v1.8.x behaviour available behind `project.md: engine: legacy` for one minor version, so a half-migrated
   vault can still finish a run.

## Part E — What must not change (regression checklist)

- `/approve-uc` remains the only way a UC becomes approved; nothing auto-approves.
- Raw intake is verbatim; `## Raw` is never paraphrased; row ids on notes are permanent.
- Questions are add-only; ticking needs a filled `A:`; intent questions are never auto-ticked.
- Steps are never renumbered; dropped steps keep their ids.
- Every UC/BR keeps its trace to INT rows, hub rows and (codebase mode) XR ids.
- Asymmetries are specified per surface; one cross-surface statement over a divergence is never written.
- `repos/` is never written by any command or agent.
- No secrets, credentials, e-mail addresses, OTP-bypass values or internal hostnames are reproduced
  (add a `lint` rule: flag e-mail-address, key-like and host-like patterns in UC/BR/hub text).

## Part F — Risks

| Risk | Mitigation |
|---|---|
| Engine parser corrupts files (the Agoyu truncation incident) | backup + verify-after-write in `vault.py`; round-trip test over real vaults before any write command ships |
| Change-set schema too rigid for real BA prose | `set_field` / `append_note` carry free text; only structural ops (steps, flows, mirrors, questions) are typed |
| Losing the "staged text is reviewable" property | ledger render block + Changelog + review flag; `/approve-uc` shows pending sets |
| Workflow tool not available in some hosts | B.5 fallback loop in every skill |
| Cards drift from conventions | card-rule-id test (Phase 4 task 1) |
| Communication-mode recall drops if extraction is over-slimmed | extractor/auditor logic unchanged; only their I/O becomes JSON and line-range reads |

## Part G — Deliverables checklist for the executor

- [ ] Phase 1: `bin/bigin`, `lib/bigin/{vault,ids,hub,mirror,status,coverage,lint,cli}.py`, quiet hook, skill text
      updated, hub-bookkeeper retired, `tests/` with both fixtures, `docs/ARCHITECTURE.md`.
- [ ] Phase 2: schemas, `changeset.py`, `ledger.py`, worklists, JSON-out agents, uc-applier removed, stage files
      rewritten, `migrate discussion-to-ledger`, approve-uc ledger check, golden-file test.
- [ ] Phase 3: `workflows/{transform,adjudicate,extract}.js`, `_runs/` resume, skill fallback, model tiering.
- [ ] Phase 4: `cards/`, lean templates + `strip-guidance`, `split-signal-log`, `intake codebase` +
      `docs/CODEBASE-INTAKE.md`, `conflict_policy`, metrics & budgets, slim `bigin-ba.md`.
- [ ] `docs/MIGRATION.md` describing every `bigin migrate` step and how to roll back from the snapshot.
- [ ] README/USER_GUIDE updated: the two modes, the engine, the ledger, what reviewers see.
