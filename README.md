# Bigin BA Workflow Plugin

A Claude Code plugin that guides a Business Analyst through turning raw communication (meetings, emails, chat notes) into structured requirement documentation — from first capture to approved use cases and a prototype design. (PRD, epics, and stories are a planned stage, not a built one — see the migration note below.)

## Workflow

Structured as ETL: `extract-signal` **extracts** raw intake into per-feature signals,
`bigin-transform-signal` **transforms** those signals into Use Cases and Business Rules (each its own
file, a UC free to span features), and the load stages take them on to design, approval, and entity
modelling. The full ID scheme and artifact conventions
live in the rulebook, which `/bigin-new-project` materializes into the project at
`_bigin/conventions/conventions.md` (it ships in the plugin at `workspace/conventions/conventions.md`).
Each stage's own procedure lives in one numbered file per stage under `workspace/stages/<skill>/`, so
what governs a stage is findable from the stage, and a run loads only the files its signals reach.

```
/bigin-new-project        initiate the project in this repo: scaffold the workspace, capture the
                           engagement config, map the codebase if it's an existing product, and
                           check the configured email/meeting providers are reachable
        |
/bigin-intake             capture raw intake, unmodified (auto: email/meeting, or direct: freeform note)
        |
/extract-signal           [Extract] drain the intake queue: extract signals into a flat raw record
                           on the note, anchor each to a feature, file them onto that feature's
                           Signal Log grouped by functional theme
        |
/bigin-transform-signal   [Transform] qualify each filed signal, route it to a lane, turn it into
                           drafted/updated Use Cases (a user goal with its flow, branches, rules
                           mirror and open questions) and the BRs governing them, human-gate every
                           UC/BR change first. Cites an Entity's proposed row by name -- never
                           promotes one; that waits for /sync-entities, after approval
        |
        |------------------------------------------.
        |                                          |
        |                                          |  presentation-only signals take the Design
        |   (/enrich-feature would sit here —      |  chain — a directive on the feature hub or
        |    HALTED, unmigrated. Not runnable,     |  in DESIGN-PRINCIPLES.md, no UC, no PRD
        |    and nothing gates on it)              |
        |                                          |
/approve-uc               [Load] approve the UC once its open questions are resolved:
        |                  reprocess its live content, flip status to approved.
        |                  Touches only the UC's own file -- no PRD written here
        |                  yet (still Planned), and entity/hub bookkeeping is
        |                  deferred to /sync-entities.
        |
/sync-entities            [Load] catch up the vault-wide bookkeeping an approval
        |                  implied: promote/update any entity an approved UC
        |                  references, refresh its feature hub(s). Run whenever
        |                  convenient -- not part of the review loop.
        |
/bigin-generate-design    [Load] every UC with no current design -> one UX-### per feature:
        |                  screen specs, the shared design system, and two prototype prompts
        |                  (Claude design + Figma Make). Runs off UCs, not the PRD, so it can
        |                  start as soon as a use case has a main flow — and it is headless.
        |
(/consolidate-prd)        [Load] HALTED, unmigrated — would merge design decisions into a PRD and
                           generate Epics & User Stories. Nothing writes a PRD today; an approved
                           UC is feature material a human hands off
```

`/bigin-transform-signal` runs five stages per invocation: **fold-in** (apply staged changes a human
has since answered — first, so a rerun is always useful), **qualify** (four gates: blocked on an
answer, source materialized, fidelity, dedup), **route and draft** (one subagent per feature, never
per lane — a feature's hub and UC/BR files are one ownership domain), **sync** (shared registers
and cross-feature use-case changes,
written sequentially, plus an in-feature conflict check), and **status and report**. Signals it
can't safely act on are parked `held` with the remedy named, never repaired by re-reading raw
material — extraction owns that, and its own source audit is where a signal is checked
quote-by-quote against the source it claims to come from, and where a claim the source makes with
no signal to show for it gets found.

All state is written into the current repo — `_bigin/` for engagement config plus the materialized
rulebook, `00-Inbox`/`01-Requirements` for the requirements vault:

```
_bigin/system/project.md         engagement config: client, approver, contacts, providers,
                                  new vs. ongoing product, codebase map, provider readiness
_bigin/conventions/               the shared standard, copied in by /bigin-new-project —
                                  conventions.md (ID scheme, schemas, status vocabularies) and
                                  paths.md ({variable} → path). Plugin-owned: refreshed on re-run
_bigin/stages/                    one file per pipeline stage, same ownership. Grouped by the skill
    extract/2-extraction.md        that runs it and numbered by stage, so what governs a stage is
    extract/2b-audit.md            findable from the stage alone — and a run loads only the files
    extract/3-filing.md            its own signals reach, never the whole rulebook. Extraction,
    transform/1-foldin.md          auditing, and filing are separate files because they are separate
    transform/2-qualification.md   subagents: the extractor must not know its rows get grouped
                                   downstream, and the auditor must build its own list of claims
                                   before it ever sees the extractor's table
    transform/3-routing.md
    transform/3-lane-{uc,br,design}.md
    transform/4-sync.md
    transform/5-status.md
_bigin/templates/                 blank scaffolds for every artifact type, same ownership
00-Inbox/
└── INT-<NNN>.md                 raw captures, one file per intake, verbatim
01-Requirements/
├── FEATURES.md                  the feature slug registry — everything anchors to a row here
├── PAIN-POINTS.md               canonical PP-### register
├── ENTITIES.md                  candidate EN-### rows a signal reveals (proposed only)
├── DESIGN-PRINCIPLES.md         durable, cross-cutting design constraints
├── _features/<slug>.md          one Feature Hub per slug — Signal Log, Use Cases, Entities,
│                                 Requirement Readiness, Pain Points
├── _ucs/UC-<NNN> <Title>.md      one Use Case doc per user goal — THE requirement artifact:
│                                 actors, flow, branches, rules mirror, open questions. May span
│                                 features (features: [], owned by primary_feature:)
├── _brs/BR-<NNN> <Title>.md      one Business Rule doc per BR — always its own file, uc: []
│                                 citing the use case(s) it governs (or [] if feature-level)
├── _entities/EN-<NNN> <Title>.md one entity doc per promoted EN-### (domain-modeled, not just
│                                 proposed) — a field-level BR is still its own _brs/ file
├── _frs/FR-<NNN> <Title>.md      RETIRED — pre-UC requirement docs, frozen, absorbed_by: UC-###
└── SCENARIOS.md                  RETIRED — pre-UC SCN-### cross-feature register; a cross-feature
                                  flow is now one UC
04-UIUX/UX-<NNN> <Feature>.md    one design spec per feature, from /bigin-generate-design: screen
                                  inventory, screen specs, flows, plus the shared append-only design
                                  system under 04-UIUX/_design-system/
PRD.md                            PLANNED — nothing writes this. /approve-uc approves the UC and
                                  stops there; no PRD-generation stage is built (migration note below)
epics.md                          PLANNED — /consolidate-prd is halted, so nothing generates these
.bigin/  (legacy)                 the pre-migration flat-file layout /enrich-feature and
                                  /consolidate-prd still read. Absent in any project created on the
                                  current model, which is exactly why both skills halt
```

### Why the rulebook is copied into the project

Every stage after intake does its real work inside dispatched subagents — one per intake note in
`/extract-signal`, one per feature in `/bigin-transform-signal`. A subagent gets no plugin context of
its own, so it cannot resolve a path into wherever the plugin happens to be installed. Copying the
rulebook and templates into `_bigin/` at init gives skills, subagents, and the `bigin-ba` agent one
path convention that all three can actually read. It also makes the rules inspectable: a BA can open
`_bigin/stages/transform/3-lane-uc.md` and see exactly what governed a use case.

`/extract-signal`'s five dispatched subagents are named, versioned agent definitions —
`agents/signal-extractor.md` (2a), `signal-auditor.md` (2b), `signal-repairer.md` (2b-repair and
hub repair), `signal-filer.md` (2c), and `signal-batch-verifier.md` (Stage 3) — rather than a fresh
hand-written prompt per dispatch. Each resolves `{variable}`s from the project's own materialized
`_bigin/conventions/paths.md` and reads its stage's rulebook from `_bigin/stages/extract/` at runtime,
so a project-level override still applies; the agent file fixes only the identity, tool scope, model,
and report contract — never the procedure.

**One procedure, one home.** `skills/extract-signal/references/agent-dispatch.md` carries only the
per-run data handed to each agent (which note, the read plan, this run's mode, the audit's findings).
It deliberately does *not* restate a procedure: two copies of one rule is how this plugin previously
shipped a `signal-auditor` missing a mandatory check that the dispatch prompt had, and a batch verifier
accepting question mirrors in places nothing writes them. A dispatch-prompt copy of a rule also silently
overrides a project's own `_bigin/` override of that rule, which defeats the point of materializing the
rulebook at all. The audit stage now has its own `_bigin/stages/extract/2b-audit.md`, so all five agents
work the same way — that file also owns the table-repair procedure, which is why the repair is a
dispatched agent rather than orchestrator work.

`/bigin-transform-signal`'s Stage 3/4 dispatches follow the same pattern: `agents/uc-detector.md`
(3a, UC identification), `uc-drafter.md` (3b, staging content into every lane), and `uc-applier.md`
(Stage 4 Part 2, applying an already-staged main-flow step/flow into `## 2`/`## 3`) each read their
stage's rulebook (`3-routing.md`, `3-lane-uc.md`, `3-lane-br.md`, `3-lane-design.md`, `4-sync.md`)
from `_bigin/stages/transform/` at runtime rather than hard-coding it, for the same override reason.
Before these existed, `references/agent-dispatch.md` dispatched Stage 3b and Part 2 as a bare
`general-purpose` agent with the entire rulebook re-typed into the prompt on every call — expensive
and inconsistent across runs, and the reason these two files exist now. `agents/hub-bookkeeper.md` (`haiku`) is the same
idea applied to the mechanical hub-table refresh: two steps may now delegate to it, **one hub per
dispatch, sequentially** — `1-foldin.md` § Reconcile mirrors (its hub items only) and `4-sync.md`
§ Part 1b's per-participating-hub pointer. Delegating keeps a pure re-derivation out of the
orchestrator's own context, which is the one context the whole fan-out exists to protect. It is never
handed a decision: a `Status`, `Destination`, id, or lane arrives as settled fact or the dispatch is
`blocked`.

The tradeoff is that a project pins the rulebook it was initiated with. `_bigin/system/project.md`
records `workspace_version`; re-running `/bigin-new-project` after a plugin upgrade refreshes
`_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/` to the new version. All three are
plugin-owned and overwritten on refresh — per-project overrides belong in
`.claude/bigin-ba-workflow-plugin.local.md`, never in the materialized rules.

`/bigin-new-project` is re-runnable by design: it re-materializes the workspace every run, shows the
existing config and only rewrites what you confirm, re-checks provider access, and never touches
captured intake, features, or the PRD. It can also import a `proposed` feature list from a project proposal or SOW. For
`project_mode: ongoing` it records `codebase_path`, but the **codebase map is currently deferred** —
that section stays empty in both modes until the repo-mapping approach is settled.

Its last step probes the two providers the config names (§ 7) and records the result in
`## Provider readiness`. Reachability has four states, not two, and only one of them is fixed by
installing: **not configured** gets an automatic `claude mcp add` where the plugin has a pinned command
for it; **needs authentication** cannot be fixed here at all, since OAuth needs a browser and a human;
**failed to connect** is retried once and then reported verbatim; **connected but missing the expected
tools** is a name collision, reported rather than reinstalled over. The step never blocks initiation —
`/bigin-intake direct …` works with no provider at all, and only Mode B's sweep depends on one.

Every UC's own frontmatter `status` (`draft` ⇄ `needs-clarification` → `approved`, human-only per `/approve-uc`) is the authoritative gate. `enriched` and `consolidated` remain defined values for pre-migration vaults that already carry them, but nothing writes either today — `/enrich-feature` and `/consolidate-prd` are halted, so `draft → approved` is the live path and nothing may gate on `enriched`. A feature carries one use case per distinct user goal, so several at different stages at once is normal, and a use case that spans features is owned by one of them (`primary_feature:`) while appearing on every participating hub. Each Feature Hub's `## Requirement Readiness` table is a refreshed snapshot for orientation, not the gate itself. Features are matched by slug across stages, so `/extract-signal` and `/bigin-transform-signal` update an existing hub/UC rather than duplicating one when new signals map to the same feature — and a new signal about an existing *goal* is a step, branch, or rule inside that UC, not a second one.

> **Migration note:** `/enrich-feature` and `/consolidate-prd` are **halted, not merely stale**. Both read the older `.bigin/features/FR-<id>-*.md` single-file model **and key on the retired `FR-###` artifact**, and that directory does not exist in a project on the current layout — so every invocation halts with no input to read. Each now says so in its own first line and keeps its target contract under a heading marked not-runnable, so the design intent survives without either looking live. Three consequences the rest of the plugin respects: `enriched` is unreachable and nothing gates on it; `/approve-uc` mentions enrichment only when `.bigin/features/` actually exists, instead of asking "proceed anyway?" on every approval forever; and the `bigin-ba` agent does not route to either. `/prototype-design` is off the load path too — superseded by `/bigin-generate-design`, kept only so old references resolve.
>
> `/bigin-generate-design`, `/approve-uc`, and `/sync-entities` **are** migrated (all three read `_ucs/`/`_entities/` directly), so both the design exit and the human-approval exit from `/bigin-transform-signal` work today, while the PRD/epics exit needs a person. See `_bigin/conventions/conventions.md` § Reconciliation notes for the per-skill breakdown and the target contract for each halted stage.

### The deterministic checker and its hook

A chunk of the pipeline's verification is pure counting — no two use cases share an ID, a signal table's
rows have the right number of columns, a hub citation points at a note row that exists, a status is one
of its documented values. `hooks/bigin-lint.py` does that counting. It runs in two places:

| Mode | When | What it checks | On a finding |
|---|---|---|---|
| `--hook` | automatically, after any write into `00-Inbox/` or `01-Requirements/` | **tier 1** only — the invariants, scoped to the file just written | exits 2 so the finding is fed straight back to the agent that made the write |
| `--full` | called by the orchestrator at Stage 5 of a transform run, and after each extract batch | tier 1 across the vault **plus tier 2** | exits 1; the findings are that stage's own blocking mismatches |

The split is the whole design. **Tier 1** is checks that are never legitimately false, not even halfway
through a stage: an ID collision or a malformed table row is a defect the instant it lands. **Tier 2** is
checks that *are* legitimately false mid-stage — a hub row flipped before the use-case entry lands, a
status before Stage 5 recounts it — so running them on every write would flag correct behaviour as
broken, and a checker that cries wolf is one the agent learns to skim past. Tier 2 therefore only runs at
a stage boundary, where the vault is supposed to add up.

What it deliberately does **not** cover: anything needing judgment (does existing text already satisfy
this signal?) or history (was a step renumbered *this run*?). [5-status.md](workspace/stages/transform/5-status.md)
carries the check-by-check split. It's an accelerator, not a replacement — and both stages are told that
an unavailable checker is reported, never read as a pass.

**Scope and safety.** The hook is inert outside a Bigin vault: no `_bigin/system/project.md` under the
project root and it exits immediately, doing nothing. Any internal error, unreadable payload, or missing
`python3` also exits silently rather than interrupting a session. Three environment variables override it:

```
BIGIN_LINT_OFF=1        disable entirely
BIGIN_LINT_ADVISORY=1   findings print to stdout and exit 0, instead of being fed back as an error
BIGIN_LINT_DEBUG=1      raise internal errors instead of swallowing them
```

**Hooks load at session start,** so after installing or upgrading the plugin the hook isn't active until
Claude Code is restarted. `/hooks` lists what's loaded in the current session.

`python3 hooks/bigin-lint.py --self-test` runs 15 fixtures — every check must fire on a broken vault and
stay silent on a clean one. That proves the parsers do what they claim; it does **not** prove the
false-alarm rate on a real vault, which only a real vault can tell you. If it turns out noisy, reach for
`BIGIN_LINT_ADVISORY=1` before switching it off — an advisory checker still reports.

## Configuration

`/extract-signal` and `/bigin-intake` read `.claude/bigin-ba-workflow-plugin.local.md` if present — a plugin settings file (not project data, so it belongs in `.claude/`, not `_bigin/`) for project-specific overrides such as a house style for `Why` phrasing or a standing list of features that always map to one obvious slug without raising a question. It's optional; omit it to use the built-in defaults. Add `.claude/*.local.md` to the project's `.gitignore` since it's user/local config.

## Invocation

Every stage is available two ways: type `/<stage>` yourself, or let the `bigin-ba` agent drive the
pipeline stage by stage. The agent reads the vault to decide what runs next, continues automatically
where the next stage needs no decision, and stops at the ones that do — `/approve-uc`'s confirmation,
and `/bigin-new-project`'s engagement config. `/bigin-transform-signal` is **not** one of them: it never
blocks on a human, staging its UC/BR changes as final text and writing a question only where a decision
is genuinely needed. The human-confirmation requirements live inside the skills that have them, so they
hold whether a person or the agent invoked them.

The `bigin-ba` agent carries **routing only** — which skill runs when. Each skill's semantics live in
its own `SKILL.md`, and migration status lives in § Reconciliation notes alone, because an agent body
restating either goes stale the day a skill changes and then reads as authoritative while being wrong.
The same brief exists for non-Claude-Code runtimes at `.agents/AGENTS.md`, kept deliberately thin for
the same reason.

## Install (local development)

```bash
claude --plugin-dir /path/to/bigin_ba_workflow_plugin
```

Then run `/bigin-new-project` to initiate the project — this is what materializes
`_bigin/conventions/`, `_bigin/stages/`, and `_bigin/templates/`, so nothing else works until it has
run — and `/bigin-intake` to capture the first
input. Use `/reload-plugins` after editing any `SKILL.md` to pick up changes without restarting; after
editing anything under `workspace/`, re-run `/bigin-new-project` in the test project to
re-materialize it.

## Install (from a marketplace)

Once published to a marketplace:

```
/plugin install bigin-ba-workflow-plugin@<marketplace-name>
```
