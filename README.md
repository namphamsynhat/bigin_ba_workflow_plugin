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
                           engagement config (including whether the product is web, mobile, or
                           both), map the codebase if it's an existing product, and check the
                           configured email/meeting providers -- and the design engine that
                           platform would default to for rendering -- are reachable. A missing
                           render engine blocks nothing on the requirements path
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
                           promotes one; that waits for /sync-entities, after approval.
                           Then checks each touched feature's use cases AS A SET: does it add up --
                           every entity's lifecycle, every pre-condition somebody produces, every
                           actor's own goal? What nobody has described lands as a Coverage Gap on
                           the hub -- never invented into a use case
        |
        |------------------------------------------.
        |                                          |
        |   (domain research already ran, once,    |  presentation-only signals take the Design
        |    per feature -- automatic, back in     |  chain — a directive on the feature hub or
        |    /extract-signal § Step 2a. Refresh     |  in DESIGN-PRINCIPLES.md, no UC, no PRD
        |    it on demand with /enrich-feature)     |
        |                                          |
/restructure-uc           (side entry, human-gated, not part of the main run) a UC that has
        |                  accumulated more than one user goal across several transform runs —
        |                  caught by /bigin-transform-signal's own granularity check
        |                  (3-lane-uc.md § Recognizing drift, which only ever proposes) or by a
        |                  human reviewing live — gets split here: moves existing steps to their
        |                  new home, repoints BRs, refreshes every touched hub. Never invents a
        |                  new intake note for the reorganization itself.
        |
/approve-uc               [Load] approve the UC once its open questions are resolved:
        |                  reprocess its live content, flip status to approved.
        |                  Touches only the UC's own file -- the PRD is a separate
        |                  stage (/bigin-generate-prd), and entity/hub bookkeeping
        |                  is deferred to /sync-entities.
        |
/sync-entities            [Load] catch up the vault-wide bookkeeping an approval
        |                  implied: promote/update any entity an approved UC
        |                  references, refresh its feature hub(s). Run whenever
        |                  convenient -- not part of the review loop.
        |
/bigin-generate-design    [Load] every UC with no current design -> one UX-### per feature: the
        |                  EXPERIENCE, and only the experience. Actors and their data scope, a
        |                  screen inventory, screen specs, the vault-wide navigation shell, and the
        |                  USER FLOWS -- each flow naming the PP-### pain point it resolves, or
        |                  saying it serves a UC goal alone. Then a flow review that walks every
        |                  journey as the actor and improves it in place (gated: it runs when a
        |                  perception-first-design or critique skill is installed, and is skipped,
        |                  silently, when none is -- a fabricated review is worse than none). Then
        |                  a forward coverage check matching every requirement item AND every open
        |                  pain point to what carries it.
        |                  NO DESIGN SYSTEM AND NO TOKENS. No palette, no type scale, no component
        |                  library. An element names a SEMANTIC ROLE from a closed list of ten
        |                  (`primary action`, `danger`, `muted`, ...), and a real design system --
        |                  the design team's, or one bound at render time -- maps those ten once,
        |                  later. A run that invented a palette would pin the client's brand to a
        |                  colour nobody chose.
        |                  Shaped by `platform:` in the project config -- a UC itself stays
        |                  platform-blind. Runs off UCs, not the PRD, so it can start as soon as a
        |                  use case has a main flow. Fully headless with NO halt: it renders
        |                  nothing, so no missing design tool can stop it. It ends at a spec proven
        |                  complete enough to render cold, on any engine, months later.
        |
/bigin-render-design      [Load, on request] finished UX-###s -> ONE interactive prototype, on
        |  (a human asks)  Open Design. `/bigin-render-design [slug|UX-### ...]
        |                  [--design-system <id>] [--project <name|id>]`. Re-designs nothing,
        |                  WRITES no requirement, and records only pointers (the spec's ## 8
        |                  Rendered Artifacts). NEVER run unasked, and never across every spec
        |                  at once.
        |                  MODULAR, and it ASKS before it spends anything. Step 0 resolves four
        |                  things and asks about any it cannot: is Open Design connected; share
        |                  an existing Open Design project or create a new one for this vault;
        |                  WHICH DESIGN SYSTEM -- listed from Open Design's own catalog
        |                  resources, or named by the human as the design team's. THIS IS THE ONLY
        |                  PLACE A VISUAL SYSTEM ENTERS THE PIPELINE, since the vault holds none,
        |                  so it is never guessed; DESIGN-PRINCIPLES still outranks whichever is
        |                  picked. And which model, from list_agents rather than a hardcoded id.
        |                  Then: Step 1 scopes the features; Step 2 builds ONE self-contained
        |                  prompt per feature (UX spec + UC/BR/ENTITIES data + nav map + each
        |                  element's semantic role stated IN WORDS for the bound system to
        |                  resolve + the fidelity bar, every vault id expanded into words);
        |                  Step 3 fans out one
        |                  start_run per feature into that ONE shared project, each watched by
        |                  its own render-screen-worker across the 5-30 minutes a run takes,
        |                  which reads the artifacts back and checks BOTH halves of the
        |                  traceability contract -- no /(UC|BR|EN|UX)-\d/ in visible copy, and
        |                  data-ux/data-screen actually present; Step 4 barriers on all of them
        |                  and dispatches render-prototype-assembler for one final start_run
        |                  that wires every screen into one self-contained index.html from
        |                  navigation-map.md's ## Structure, then proves every nav entry,
        |                  control target, and route resolves; Step 5 COPIES EVERYTHING BACK to
        |                  04-UIUX/_prototypes/<date>-<slug>/ with a RENDER.md manifest, because
        |                  an engine is a dependency that can be uninstalled and the vault is
        |                  what has to still have the prototype next year.
        |                  Open Design unreachable -> retries, then hands over the built prompts
        |                  to paste in by hand. A missing engine never costs this pipeline its
        |                  output. Aim: output that reads as finished production software, not a
        |                  wireframe with colour.
        |
/bigin-generate-prd       [Load] every approved UC of a feature -> one PRD-### per feature:
        |                  business capabilities, business flows (with the screens each step
        |                  lands on), rules, information, the generated design, pending scope,
        |                  and open business decisions. Business flow, never a technical spec.
        |                  Wraps BMAD's create-PRD workflow in headless mode when BMAD is
        |                  installed; complete on its own when it isn't. Headless.
        |
(/consolidate-prd)        [Load] HALTED, unmigrated — would generate Epics & User Stories from
                           the PRD. Epics/stories are still cut by hand; the PRD itself is now
                           written by /bigin-generate-prd above
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
_bigin/system/project.md         engagement config: client, contacts, providers,
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
├── _features/<slug>.md          one Feature Hub per slug — Signal Log, Use Cases, Coverage Gaps,
│                                 Requirement Readiness, Entities, Pain Points
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
04-UIUX/UX-<NNN> <Feature>.md    one UX spec per feature, from /bigin-generate-design: actors and
                                  their data scope, screen inventory, screen specs (semantic roles,
                                  never colours or tokens), the user flows and the pain point each
                                  resolves, the ### Flow Review verdicts, and the ### Coverage
                                  table proving nothing in the requirements went undesigned. Its
                                  ## 8 Rendered Artifacts holds pointers, written only by
                                  /bigin-render-design
04-UIUX/_ux/navigation-map.md    the ONE vault-wide navigation shell -- every directly-reachable
                                  menu entry and the screen it opens, append-only, at arbitrary
                                  depth via a dot-path id. A web tree, a mobile tab bar of at most
                                  five, or one file carrying both. It is /bigin-render-design's
                                  single source of truth for routing
04-UIUX/_design-system/          LEGACY, unread. A vault materialized before design systems left
                                  this pipeline may still have design-tokens.md and components/
                                  here. Nothing reads them and nothing deletes them; they are a
                                  record of what earlier runs specced against
04-UIUX/_prototypes/<run>/       the rendered prototype, COPIED BACK out of Open Design by
                                  /bigin-render-design: index.html, screens/, assets/, and a
                                  RENDER.md manifest naming the project, design system, model,
                                  and each feature's run id. Written by that skill and nothing
                                  else
02-PRD/PRD-<NNN> <Feature>.md    one PRD per feature, from /bigin-generate-prd: the feature's
                                  approved UCs as business capabilities and business flows, its
                                  rules and information, the UX-### design, pending scope, and open
                                  business decisions. absorbed: [UC-###@version] is what makes
                                  "this PRD has drifted from its use cases" detectable
epics.md                          PLANNED — /consolidate-prd is halted, so nothing generates these
.bigin/  (legacy)                 the pre-migration flat-file layout /consolidate-prd still reads.
                                  Absent in any project created on the current model, which is
                                  exactly why that one skill halts. /enrich-feature no longer reads
                                  this layout -- it's live, and feature-scoped (§ Reconciliation notes)
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

`/bigin-transform-signal`'s Stage 3/4 dispatches follow the same pattern: `agents/uc-router.md` (one
agent, resumed rather than redispatched between its Phase A UC-identification and Phase B
lane-drafting, so the hub/UC content Phase A reads is never read twice) and `uc-applier.md`
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

`/restructure-uc` dispatches `agents/uc-splitter.md` (`sonnet`) once per restructuring operation — given
an already-decided split plan (never deciding the boundary itself), it moves existing `## 2`/`## 3`
content to its new home, marks the source's originals `removed because`, and repoints every affected
`BR-###`. It never touches a feature hub or `FEATURES.md` itself; it reports what changed so the skill
can dispatch `hub-bookkeeper` per touched hub, same pattern as everywhere else in the pipeline.

`/bigin-generate-design`'s Stage 3 dispatches `agents/ux-brief-assembler.md` per feature that clears
a size threshold (3+ in-scope UCs, or 4+ distinct cited entities) — a read-only pass that combines a
feature's UCs, the `EN-###` entities they cite, their `BR-###` rule mirrors, open hub directives, and
active design principles into one Design Brief for that feature's screens-writing worker. It never
writes a file and never finalizes a screen boundary, a semantic role, a user flow, or the Part 4b
relationship verdict —
those stay the screens worker's judgment; the assembler only removes the need to re-derive the
mechanical parts of the read from scratch in the same context that then has to design the screens.

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

Every UC's own frontmatter `status` (`draft` ⇄ `needs-clarification` → `approved`, human-only per `/approve-uc`) is the authoritative gate. `enriched` and `consolidated` remain defined values for pre-migration vaults that already carry them, but nothing writes either today — enrichment moved off the UC entirely (it's a feature-level, hub-scoped pass now — § Reconciliation notes) and `/consolidate-prd` is still halted, so `draft → approved` is the live path and nothing may gate on `enriched` — `approved` is what `/bigin-generate-prd` folds into a feature's PRD. A feature carries one use case per distinct user goal, so several at different stages at once is normal, and a use case that spans features is owned by one of them (`primary_feature:`) while appearing on every participating hub. Each Feature Hub's `## Requirement Readiness` table is a refreshed snapshot for orientation, not the gate itself. Features are matched by slug across stages, so `/extract-signal` and `/bigin-transform-signal` update an existing hub/UC rather than duplicating one when new signals map to the same feature — and a new signal about an existing *goal* is a step, branch, or rule inside that UC, not a second one.

> **Migration note:** `/consolidate-prd` is **halted, not merely stale**. It reads the older `.bigin/features/FR-<id>-*.md` single-file model **and keys on the retired `FR-###` artifact**, and that directory does not exist in a project on the current layout — so every invocation halts with no input to read. It says so in its own first line and keeps its target contract under a heading marked not-runnable, so the design intent survives without looking live. `/enrich-feature` is **not** in this state any more — it was retargeted from that same old per-UC design to a feature-level, hub-scoped domain-research refresh, and is live (§ Reconciliation notes). Consequences the rest of the plugin respects: `enriched` stays unreachable and nothing gates on it, but for a different reason now — enrichment was moved off the UC, not halted; `/approve-uc` no longer mentions enrichment at all, since it's not a UC-level concept; and the `bigin-ba` agent routes to `/enrich-feature` for a manual research refresh, never for `/consolidate-prd`. `/prototype-design` is off the load path too — superseded by `/bigin-generate-design`, kept only so old references resolve.
>
> `/bigin-generate-design`, `/approve-uc`, `/sync-entities`, and `/bigin-generate-prd` **are** on the current model (all four read `_ucs/`/`_entities/` directly), so the design exit, the human-approval exit, and the PRD exit from `/bigin-transform-signal` all work today — only epics/stories still need a person. See `_bigin/conventions/conventions.md` § Reconciliation notes for the per-skill breakdown and the target contract for each halted stage.

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

Every stage is available three ways: type `/<stage>` yourself, run `/bigin-run` to have the pipeline
routed for you, or dispatch the `bigin-ba` agent to work one feature unattended. All three read the
vault to decide what runs next, continue automatically where the next stage needs no decision, and stop
at the ones that do — `/approve-uc`'s confirmation, `/bigin-new-project`'s engagement config, and
`/bigin-render-design`, which is never routed to at all: a prototype is something a human asks for, on
the Open Design project, design system, and at the moment they choose.

**`/bigin-run` is the home for any run that fans out.** `/extract-signal` dispatches a named worker per
note, and `/bigin-transform-signal`, `/bigin-generate-design`, and `/bigin-generate-prd` each dispatch a
worker per feature past a documented scope threshold — all of which need the `Agent` tool, which only the main session has. The
`bigin-ba` agent is a subagent and has no such tool, so it covers the inline scopes (one feature, small
batches) and hands anything larger back rather than running a degraded pass that would pull every
transcript into a single context. `/extract-signal` it never runs at all. That boundary is stated in
both places — the agent's § What you cannot run from here, and the skill's § Why this runs in the main
session — because neither can read the other's file at run time. `/bigin-transform-signal` is **not** one of them: it never
blocks on a human, staging its UC/BR changes as final text and writing a question only where a decision
is genuinely needed. The human-confirmation requirements live inside the skills that have them, so they
hold whether a person or the agent invoked them.

`/bigin-run` and the `bigin-ba` agent carry **routing only** — which skill runs when. Each skill's
semantics live in its own `SKILL.md`, and migration status lives in § Reconciliation notes alone, because
a router restating either goes stale the day a skill changes and then reads as authoritative while being
wrong. The routing table itself is the one thing deliberately duplicated between them: a subagent cannot
resolve `${CLAUDE_PLUGIN_ROOT}`, so it cannot read the skill's copy. Change one, change both — and the
durable fix is materializing routing into `_bigin/` alongside the stage guides. The same brief exists for
non-Claude-Code runtimes at `.agents/AGENTS.md`, kept deliberately thin for the same reason.

## Answering open questions offline

A BA does not have to sit in a chat session to clear a use case's open questions. Every `- [ ] Q:` line
is written to be answered cold: open `01-Requirements/_ucs/UC-### <Title>.md`, find `## 5 Open Questions
& Decision Log`, and type the answer on that question's own `A:` line — in the file, in your own words.
Leave the checkbox unticked unless the answer fully settles the question; "we'll ask the client" and
"TBD after the demo" are not settled, and ticking one anyway is what makes a parked use case read as
approvable. Don't edit the numbered sections to match your own answer — the pipeline applies it, and
doing both is how the same change lands twice.

Then say **"process UC-###"** (or the feature's name) to `/bigin-run` or the `bigin-ba` agent. That pass
reads what you wrote instead of re-asking it, folds every filled `A:` in with one
`/bigin-transform-signal` run, re-counts what is still open, and comes back **once** with whichever
outcome each UC earned: the follow-up questions that pass actually produced — a question the drafting
raised, an answer that didn't settle its question, two answers that collide — or, at zero open questions,
the flow itself and an approval ask. Questions you already answered cleanly are never shown again. The
procedure has one home, `agents/bigin-ba.md` § Answers already written: the process-the-UC pass, and the
conventions side is § Answering a question.

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
