# Bigin BA Workflow Plugin

A Claude Code plugin that guides a Business Analyst through turning raw communication (meetings, emails, chat notes) into structured requirement documentation — from first capture to Epics and User Stories.

## Workflow

Structured as ETL: `extract-signal` **extracts** raw intake into per-feature signals,
`bigin-transform-signal` **transforms** those signals into FRs and BRs (each its own file, with
Entities/Business Scenarios kept in sync across features), and the remaining stages **load**
approved requirements into the PRD, prototype, and epics. The full ID scheme and artifact conventions
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
                           mirror and open questions) and the BRs governing them, keep
                           cross-feature Entities in sync, human-gate every UC/BR change first
        |
        |------------------------------------------.
        |                                          |
/enrich-feature           [Load] domain research    |  presentation-only signals take the Design
        |                  + entity mapping         |  chain — a directive on the feature hub or
        |                                           |  in DESIGN-PRINCIPLES.md, no UC, no PRD
/approve-uc               [Load] approve the UC once its open questions are resolved:
        |                  reprocess its live content, promote/update any entity
        |                  it references, flip status to approved. No PRD is
        |                  written here yet -- that stage is still Planned.
        |
/bigin-generate-design    [Load] every UC with no current design -> one UX-### per feature:
        |                  screen specs, the shared design system, and two prototype prompts
        |                  (Claude design + Figma Make). Runs off UCs, not the PRD, so it can
        |                  start as soon as a use case has a main flow — and it is headless.
        |
/consolidate-prd          [Load] merge design decisions into the PRD, generate Epics & User Stories
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
    extract/3-filing.md            findable from the stage alone — and a run loads only the files
    transform/1-foldin.md          its own signals reach, never the whole rulebook. Extraction and
    transform/2-qualification.md   filing are separate files because they are separate subagents:
                                   the extractor must not know its rows get grouped downstream
    transform/3-routing.md
    transform/3-lane-{uc,br,design,entity}.md
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
PRD.md                            Planned — nothing writes this yet. /approve-uc approves the UC
                                  and stops there; a PRD-generation stage isn't built (see the
                                  migration note below)
prototypes/FR-<NNN>-prototype.md flows/screens for an approved feature (still FR-keyed — see
                                  the migration note below)
epics.md                          generated Epics & User Stories
```

### Why the rulebook is copied into the project

Every stage after intake does its real work inside dispatched subagents — one per intake note in
`/extract-signal`, one per feature in `/bigin-transform-signal`. A subagent gets no plugin context of
its own, so it cannot resolve a path into wherever the plugin happens to be installed. Copying the
rulebook and templates into `_bigin/` at init gives skills, subagents, and the `bigin-ba` agent one
path convention that all three can actually read. It also makes the rules inspectable: a BA can open
`_bigin/stages/transform/3-lane-uc.md` and see exactly what governed a use case.

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

Every UC's own frontmatter `status` (`draft` ⇄ `needs-clarification` → `enriched` → `approved`, human-only per `/approve-uc`, → `consolidated`) is the authoritative gate. A feature carries one use case per distinct user goal, so several at different stages at once is normal, and a use case that spans features is owned by one of them (`primary_feature:`) while appearing on every participating hub. Each Feature Hub's `## Requirement Readiness` table is a refreshed snapshot for orientation, not the gate itself. Features are matched by slug across stages, so `/extract-signal` and `/bigin-transform-signal` update an existing hub/UC rather than duplicating one when new signals map to the same feature — and a new signal about an existing *goal* is a step, branch, or rule inside that UC, not a second one.

> **Migration note:** `/enrich-feature` and `/consolidate-prd` still read the older `.bigin/features/FR-<id>-*.md` single-file model **and still key on the retired `FR-###` artifact**. They haven't been moved onto the `01-Requirements/` layout or onto `UC-###` yet — that's the remaining stage of this migration, and it is a two-axis gap. `/bigin-generate-design` and `/approve-uc` **are** migrated (`/bigin-generate-design` replaces `/prototype-design`, reads `_ucs/` directly, and needs no PRD; `/approve-uc` replaces `/approve-fr`, reads/writes `_ucs/` directly, and generates no PRD of its own — that's still Planned), so both the design exit and the human-approval exit from `/bigin-transform-signal` work today, while the PRD/epics exit still needs a person. See `_bigin/conventions/conventions.md` § Reconciliation notes for the per-skill breakdown.

## Configuration

`/extract-signal` and `/bigin-intake` read `.claude/bigin-ba-workflow-plugin.local.md` if present — a plugin settings file (not project data, so it belongs in `.claude/`, not `_bigin/`) for project-specific overrides such as a house style for `Why` phrasing or a standing list of features that always map to one obvious slug without raising a question. It's optional; omit it to use the built-in defaults. Add `.claude/*.local.md` to the project's `.gitignore` since it's user/local config.

## Invocation

Every stage is available two ways: type `/<stage>` yourself, or let the `bigin-ba` agent drive the
pipeline stage by stage. The agent reads the vault to decide what runs next, continues automatically
where the next stage needs no decision, and stops at the ones that do — `/approve-uc`, and
`/bigin-transform-signal`'s UC/BR review gate. The human-confirmation requirements live inside those
skills, so they hold whether a person or the agent invoked them.

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
