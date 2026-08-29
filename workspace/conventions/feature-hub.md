# Conventions — the Feature Hub

The hub's own schema — its frontmatter, its tables, what each one is derived from — plus the
`FEATURES.md` feature-map format and the feature-material handoff a PRD reads.

**Read by** `/extract-signal` (filing), `/bigin-transform-signal` (sync), `/enrich-feature`,
`hub-bookkeeper`, and `/bigin-generate-prd` (§ Feature material).

## Feature material (the approve → process handoff)

Approval converts a UC from *work in progress* into **staged material on its feature**:

- A UC with `status: approved` **is** feature material — no extra flag. Everything sharing its slug
  aggregates into the feature's material set: the approved UC(s) with their BRs, resolved discussion,
  and `attachments`, plus the source INT notes. A cross-feature UC is material on every feature in its
  `features:` list.
- Only `approved` UCs qualify as material. Feedback that touches a UC — at any status, including
  already-`approved` material, before or after the feature ships — is applied **in place** and
  sets it back to (or keeps it at) `draft`/`needs-clarification` (hard rule 7: approval
  doesn't freeze a UC). Feedback that touches an already-approved UC therefore **does**
  un-stage it, the same way it would for any other status: the edit lands in the same UC (version
  bump + changelog citing the source), and it drops out of the feature's material set until the
  human re-approves it. A feature carries as many UCs as it has distinct user goals, each staged as
  material only while it is currently `approved` — so a feature can be part-approved, and that is a
  real, useful state rather than a defect.
- Humans gate `approved` (hard rule 4) — an agent never sets it; `/approve-uc` is the point where
  a human confirms and the status flips.
- **What consumes the material:** `/bigin-generate-prd` folds a feature's currently-`approved` UCs
  into `02-PRD/PRD-<NNN> <Feature>.md` and stamps `absorbed: [UC-###@version]` (`runtime.md` § Absorbed), so a
  part-approved feature yields a PRD covering exactly what is approved, with the rest listed as
  pending scope. It reads the UC's **own** `status:`, never a hub table, and it changes no
  requirement — approval stays the only gate. `/bigin-generate-design` needs no approval at all and
  runs off any UC with a main flow.
- **Planned** — a richer engagement (a front-end dashboard, a workflow picker per feature) may
  eventually replace the fixed `/approve-uc → /bigin-generate-design → /bigin-generate-prd` pipeline
  described here with something that dispatches per-feature by need. Not built today; the fixed
  order is what every feature runs. (`/enrich-feature` no longer sits in this UC-level chain at all
  — it's a feature-scoped pass that runs earlier, at registration, and never gates approval.)

## Feature Hub

`01-Requirements/_features/<slug>.md` (`type: feature-hub`) is the single note that shows
everything about one feature, and the file to hand an agent when saying "work on `<slug>`".
`FEATURES.md` stays the canonical index (one row per feature, the anti-fragmentation anchor); the
hub is the rich per-feature view generated from the same underlying artifacts, so nothing here is
ever hand-authored content — it's always assembled/refreshed from the UC(s), INT sources, PRD
section, epics/stories, and prototype that already exist for that slug.

**Frontmatter:**
```yaml
---
type: feature-hub
feature: <slug>
name:           # display name — mirrors the FEATURES.md row's Feature column. This is the source
                # of truth for any consumer (this plugin's own skills, or a front-end app) reading
                # Slug/Feature/UC/Code areas/Sources — read from this frontmatter, not by parsing
                # FEATURES.md's table (§ Feature Map format)
status: <mirrors the FEATURES.md row's Status at last refresh>
uc: []          # every UC-### id this feature owns OR participates in — one per distinct user
                # goal, so several is normal. A cross-feature UC appears on every participating
                # hub's list; ## Use Cases says which of them owns it. Oldest first; [] before the
                # first use case is drafted. Written by /bigin-transform-signal
br: []          # every BR-### id this feature has ever had, same discipline as uc: above —
                # written by /bigin-transform-signal
fr: []          # RETIRED — pre-UC FR-### ids, kept so old ids resolve. Nothing writes here
code_areas: []  # mirrors the FEATURES.md row's Code areas column (project_mode: ongoing only)
sources: []     # mirrors the FEATURES.md row's Sources column — INT-###/document ids/paths
prd:            # PRD-### id, or blank — set by /bigin-generate-prd, one PRD per feature
epics: []       # EP-### id(s) — Planned; today epics.md has no per-epic id to cite
stories: []     # US-### id(s) — Planned, same as above
uiux:           # UX-### id, or blank — Planned; today this would point at the prototype file path
entities: []    # EN-### id(s) this feature's UC(s)/BR(s) reference — [] until one exists.
                # Written by /bigin-transform-signal (`registers.md` § Entity Data Model)
updated:
---
```

Signals never stop arriving — a feature accumulates them across many meetings/emails over the
life of the project, some processed immediately, some held for months, some later contradicted by
a follow-up call. **There is no single feature-wide "done" state** — progress is tracked
signal-by-signal and requirement-by-requirement, never as one blanket checkbox.

**Body sections** (instantiate from `_bigin/templates/feature-hub.md`):
- `## Notes / History` — the readable, append-only, dated-bullet narrative of the feature (§
  Feature Map format) — placed right after the one-line description, before `## Signal Log`. This
  is where `/extract-signal`/`/bigin-transform-signal` write the "story" (why it exists, what each
  meeting/CR round added, what got resolved); `FEATURES.md`'s own Notes cell is a one-line pointer
  here, never inline prose.
- `## Signal Log` — the append-only register every downstream process reads. One row per
  **functional theme**, in landing order:

  | # | Signal | Type | Source | Status | Destination | Notes |
  |---|--------|------|--------|--------|--------------|-------|

  - **A row is a theme, not a signal.** Signals from one `INT-###` describing the same rule, flow,
    or decision file as a single row — `Signal` reads `**<Theme>** — <detail>; <detail>; <detail>`
    with every claim kept as its own clause, `Type` joins the member types with ` + `, and `Source`
    cites the note row numbers it covers: `INT-014 #3, #5, #7 — Jane Doe 2026-08-05`. Those numbers
    are the trail back to the note's `## Extracted signals`, which stays a flat one-row-per-signal
    raw record — **the two tables' row counts are not meant to match**, and anything comparing them
    is checking the wrong thing. Signals never merge across notes, across `Status` (only `new`
    consolidates), across the design/behaviour boundary, or when they contradict each other. A
    theme of one is normal. Full rules: `/extract-signal`'s `3-filing.md`
    § Step 2 — File to the Feature Hub.
  - **`#` is permanent** once assigned, like a `BR-###` number — never renumbered or deleted. A
    conflicting or superseding signal is always a **new row**; the old row's `Status`/`Notes` gets
    updated to point at the row that superseded it. History is never rewritten in place.
  - **`Status` values**: `new` (just landed, not yet triaged) · `held` (anchored to the feature, no
    UC exists yet — resting state pre-UC, no gate, no urgency; once a UC exists, a new signal
    against it moves straight to `staged` rather than resting here, regardless of the UC's status
    — hard rule 7, approval no longer freezes it) · `staged` (a proposed change sitting in a UC's
    `## Discussion`, not yet applied) · `applied` (folded into UC content) · `question` (the signal
    *is* an open question, not a requirement — tracked until answered) · `conflict` (contradicts
    an earlier row — needs human resolution before either can be applied) · `superseded` (an older
    row a resolved conflict/newer decision overrode) · `rejected` (explicitly out of scope). This
    plugin's `extract-signal` skill only ever writes `new`/`question`/`conflict`/`rejected` when
    filing a fresh signal (§ its own `3-filing.md`) — `held`/`staged`/`applied`/
    `superseded` describe a signal's relationship to a UC, which is `/bigin-transform-signal`'s
    job to set, not extraction's.
  - **"Processed" = `applied` \| `superseded` \| `rejected`. "Not yet processed" = everything
    else** (`new`/`held`/`staged`/`question`/`conflict`) — this is the queue a human or agent works
    from, not a percentage-done bar.
  - **Conflict handling**: when a new signal contradicts a `held`/`staged`/`applied` row, add the
    new signal as its own row with `Status: conflict`, citing the row number(s) it conflicts with
    in `Notes`. Raise an Open Question (never guess which one wins) on the UC it belongs to (its
    most recent open one, if any exist; otherwise the closest applicable UC) or on this note if
    none exists. Once the human answers, the losing row flips to `superseded` (`Notes: "superseded
    by #N, resolved <date>"`), the winning row flips to `staged`/`applied`, and the content updates
    **in place** (version bump + changelog), regardless of whether that UC is still unapproved or
    already `approved` (hard rule 7 — an approved UC's fold-in also flips it back to `draft`).
- `## Use Cases` — one row per `UC-###` in this hub's `uc:` list: `UC | Goal | Role | Status`, where
  `Role` is `owns` (this feature is the UC's `primary_feature`) or `participates`. A cross-feature UC
  appears on every participating hub with the same id — that is the artifact working, not duplication
  to fix. **No step numbers or ranges**: the UC file is the only place the flow is written out
  (`registers.md` § Business Scenarios (retired) for why). Written by `/bigin-transform-signal` Stage 4.
- `## Coverage Gaps` — what this feature's use-case set does **not** account for:

  | # | Gap | Lens | Raised | Status | Notes |
  |---|-----|------|--------|--------|-------|

  The other half of the conflict check. `## Signal Log` records what somebody said; this records what
  **nobody** said and the business plainly needs — the absence that leaves no trace anywhere else. A
  feature can carry four individually sound, individually `approved` use cases (record a gift, issue a
  certificate, audit a change) while nothing describes how the donor those gifts hang off is created,
  found, corrected, or retired; no signal ever arrived saying so, so no row, question, or conflict ever
  appears, and it surfaces at build. Written by `/bigin-transform-signal`'s Stage 4 Part 4
  (`_bigin/stages/transform/4b-coverage.md`), which is the **only** pass that reads a feature's UC set
  *as a set*, against six lenses: entity lifecycle, dangling `## 1` pre-conditions, an actor with no
  goal of its own, the feature's own stated purpose and open `PP-###` rows, data a step or rule reads
  that no UC writes, and a `BR-###` no UC's `## 4` enforces.
  - **A gap is a finding, never a work order.** The `Gap` cell says what nobody has described, in one
    sentence of plain business language a client can answer out loud, and **never proposes the
    answer** — a plausible-shaped guess on this table gets read as something the client said. The
    content comes from the answer, arriving as `/bigin-intake` → `/extract-signal` like every other
    requirement; nothing is ever drafted from a hub cell.
  - **A gap never parks a UC.** It is feature-level by nature, so a UC that is otherwise ready stays
    ready, and a gap is never written as a `- [ ] Q:` on a UC's `## 5`. That separation is the whole
    reason this table exists instead of reusing the question mechanism.
  - `#` is permanent and append-only, like the Signal Log's. `Status`: `open` (nobody has answered) ·
    `answered` (a human said what should happen; it still has to arrive through intake) · `covered` (a
    UC now covers it — cite the id) · `rejected` (out of scope — cite who decided). `Lens` names which
    of the six tests found it, so a reader can see why anyone thinks it is missing.
  - **Empty and missing mean different things.** An empty table is a real result — the set adds up. A
    hub with **no such section** has never been checked, and that is the backfill trigger the coverage
    pass keys off (§ its own guide's When it runs); it is inserted from `{template_hub}` the first time
    the pass touches such a hub, so no migration is needed.
- `## Requirement Readiness` — a refreshed **snapshot for orientation, not the gate itself**:

  | Artifact | Status | Ready for next step? | Blocking |
  |----------|--------|------------------------|----------|

  One row per UC/BR touching this feature — a feature with four distinct user goals gets four UC rows,
  oldest first, which is normal rather than fragmentation (`use-case.md` § Use Case). The
  authoritative gate for `/approve-uc`/`/bigin-generate-design` is always each UC's
  own live frontmatter `status` (§ Feature material) — this table just saves a human or agent from
  having to open every UC to see what's ready; a skill still checks the UC directly before
  proceeding, never trusts a possibly-stale table alone. An `approved` UC can still receive new
  signals later (hard rule 7 — approval doesn't freeze it); when that happens it's applied in
  place via the normal fold-in flow the next time `/bigin-transform-signal` touches this feature,
  not held in a separate backlog — note it here the same way as any other pending change
  ("approved — N new signal(s) since approval, not yet run through `/bigin-transform-signal`").
- `## Related Documents` — the UC(s)' `attachments:` list.
- `## Domain Research` — one entry per domain-research run for this feature. The first lands
  automatically, the run `/extract-signal` § Step 2a first creates this hub — the feature's stated
  scope researched (industry context, comparable products, compliance concerns, common failure
  modes, typical entities/integrations — `_bigin/conventions/domain-research-method.md`) before any
  signal has to rediscover it. Refreshable later on demand via `/enrich-feature`. Each entry: date,
  topic, one-line summary of key findings, link to the full report under
  `01-Requirements/_research/<slug>/`.
- `## Business Scenarios` (**retired**) — pre-UC `SCN-###` pointers, kept as history. Cross-feature
  flows are use cases now and live in `## Use Cases` above (`registers.md` § Business Scenarios (retired)). Never add
  a row; omit the section entirely on a new hub.
- `## Entities` — every `EN-###` this feature's UC(s)/BR(s) reference, with each entity's current
  status. See `registers.md` § Entity Data Model.
- `## Pain Points` — a table mirroring this feature's rows from `01-Requirements/PAIN-POINTS.md`:
  `PP-### | Statement | Status | Proposed solution | Resolved by` (`registers.md` § Pain Point Register). Empty
  until a `[pain-point]` signal anchors here.
- `## PRD` — link + status, or "not started." Refreshed by `/bigin-generate-prd` together with the
  `prd:` frontmatter field: `[[PRD-<NNN> <Feature>]] — <status>, N capabilities, M pending`.
- `## Epics & Stories` — table of epic/story ids with status, or a pointer into `epics.md` until
  `EP-###`/`US-###` exist as their own ids.
- `## Design Directives` — feature-scoped presentation directives on the Design chain (`use-case.md` § Traceability chain): `# | Directive | Source | Status | Notes`, `#` permanent and append-only
  like the Signal Log, `Status` one of `open` / `reflected` / `superseded` / `conflict`. Written by
  `/bigin-transform-signal`'s design lane; read by `/bigin-generate-design` as the feature's
  presentation brief (**Planned** — that skill doesn't read it yet, § Reconciliation notes). Empty
  for most features. Durable, cross-cutting preferences go to `DESIGN-PRINCIPLES.md` instead, or as
  well (`registers.md` § Design Principles Register).
- `## Prototype` — link + status, or "not started." (The hub template calls this section
  `## UX Spec`; treat the two names as the same section until one of them is renamed.)
- `## Open Questions / Gates` — every Signal Log row with `Status: question` or `Status: conflict`,
  plus every open UC's `## 5` **Still open** lines, every open BR's `## Open Questions`, and every
  `## Coverage Gaps` row still `open` or `answered` — what's actually blocking progress right now.
  A coverage gap is mirrored here **in the same sentence** as its own row (`intake.md` § One question, two places),
  and it is the one item here that blocks no single artifact — it is the feature's own hole. A settled decision-log row is not an open item. An
  `approved` UC normally contributes nothing here — its questions were resolved before approval —
  but a later edit can reopen it (hard rule 7, `intake.md` § Feedback handling) and reintroduce questions the
  same as any other UC update.
- `## Changelog` — one line per refresh: date, what changed, which run touched it.

**Maintenance contract — who refreshes it, and when:**
- `/extract-signal`: for the signals a run extracts, **append** one `## Signal Log` row per
  functional theme, each citing the note row numbers it covers (never overwrite a prior row's
  `#`/`Signal`/`Source` — only its `Status`/`Notes` when a later signal supersedes or conflicts
  with it). Create the hub from the template if it doesn't exist yet.
  Refresh `## Requirement Readiness` and `## Open Questions / Gates` to match. **Refresh
  `## Pain Points`** to mirror any `PP-###` row this run minted or updated in
  `01-Requirements/PAIN-POINTS.md` for this feature — a pain point can land here even before any
  UC exists. **On a brand-new hub only** (§ Step 2a), also appends the first `## Domain Research`
  entry — the one and only time this stage writes that section; a signal filed to an already-existing
  hub never touches it.
- `/bigin-transform-signal`: drafts/updates UC/BR files under `_ucs`/`_brs` (`intake.md` § Feedback handling),
  after each confirmed human-gate fold-in flips the affected Signal Log row from `staged` to
  `applied`, and refreshes `## Use Cases`, `## Requirement Readiness`, `uc:`/`br:` frontmatter. It
  never touches `## Entities`/`entities:` — it doesn't promote an entity, only cites a `proposed` row
  by name (`registers.md` § Entity Data Model); `/sync-entities` is what refreshes those. For a UC spanning features it
  writes `## Use Cases` and `uc:` on **every** participating hub, in its
  sequential Stage 4 pass. Also appends to `## Design Directives` for
  every presentation-only signal it routes down the Design chain, and fills each processed Signal
  Log row's `Destination` cell (the column `/extract-signal` leaves blank) with where the signal
  actually landed. **Appends to `## Coverage Gaps`** (and re-statuses its existing rows) on every
  feature whose UC set it changed, mirroring the `open`/`answered` ones into
  `## Open Questions / Gates` — its Stage 4 Part 4. It never sets a hub's own `status:` — that mirrors
  the `FEATURES.md` row's scope state, not a workflow state, and there is no "ready for PRD" feature
  status.
- `/enrich-feature`: appends to `## Domain Research` only, on manual re-run. (The automatic first
  run at hub creation is `/extract-signal` § Step 2a — same section, same output shape.) Touches
  nothing else on the hub, and never a UC.
- `/approve-uc`: writes nothing to the hub at all — it only flips the UC's own `status`/`version`/
  `## Changelog` and sets `synced: false` (`registers.md` § Entity Data Model). `/sync-entities` does the hub refresh
  that used to run inline here, separately, whenever it runs: `## Requirement Readiness` to reflect
  the UC's current status, `## Entities`/`entities:` for any entity it promoted or extended, and the
  corresponding Signal Log rows (the ones the UC was drafted/updated from) flipped to `applied` if not
  already. Writes nothing to `## PRD` — that's `/bigin-generate-prd`'s row below; approving a UC makes
  it PRD material, it does not itself document it.
- `/bigin-generate-design`: refresh `## UX Spec` (link + status) and `uiux:`, flip the
  `## Design Directives` rows a screen actually implements to `reflected`, and mirror its design
  questions into `## Open Questions / Gates`. If the source UC is still open (not yet `approved`),
  also append a line to its `## Discussion` citing the UX spec as supporting evidence — this is
  never how an already-`approved` UC gets a content change (that's `/bigin-transform-signal`'s
  feedback loop, `intake.md` § Feedback handling). It writes nothing else on a UC/BR, and never touches the
  Signal Log or `## Requirement Readiness`. Its own rules live in
  `_bigin/conventions/design-conventions.md`.
- `/bigin-render-design-od`: **writes no hub and no requirement at all.** Its Stage 4 Part 4a does *read*
  `_ucs/`, `_brs/`, `_entities/`, and `ENTITIES.md` — for **data only** (field types, validation
  predicates, enum vocabularies, state keys, real volume numbers), filtered by the UX spec's own screen
  inventory, and by one subagent that writes nothing. The agent that renders the UI never opens them at
  all, which is what keeps a render from re-designing. It renders a finished `UX-###`
  into prototype artifacts on the engine a human chose, and writes only that spec's `## 8 Rendered
  Artifacts` (one appended pointer row), its `rendered:` flag, and one `## Changelog` line. A render is
  not a requirement event, so nothing on a hub changes because one happened. It is also the only place
  in this plugin that still halts for a missing external tool — a design run no longer does.
- `/bigin-generate-prd`: refresh `## PRD` (link + status + capability/pending counts) and the `prd:`
  frontmatter field, and mirror its `§ 11 Open Business Decisions` lines into
  `## Open Questions / Gates` **using the same sentence** as the UC/UX they came from (§ One question,
  two places). Nothing else on the hub — not the Signal Log, not `## Requirement Readiness`, not
  `## Use Cases`, not `status:`, not `uc:`/`br:`/`uiux:`. There is no "ready for PRD" feature status
  and it does not invent one. It writes no UC, BR, entity, or UX file at all — unlike
  `/bigin-generate-design`, it has no sanctioned `## Discussion` exception.
- A human changing the `FEATURES.md` row's `Status` (e.g. `proposed` → `committed`) doesn't
  retroactively touch the hub — its `status:` field catches up the next time any of the above runs
  against that slug.
- The hub is a generated index like `FEATURES.md`, not an approval-gated artifact (hard rule 4
  doesn't apply to it) — but never delete Signal Log history, only append and update
  `Status`/`Notes` forward.

## Feature Map format

`FEATURES.md` is an **index, not a narrative** — one short row per feature. A markdown table cell
has no real newlines and no reliable `|`-escaping, so a Notes cell that grows past a line or gains
a stray `|` silently corrupts that row for any reader — including a future front-end app parsing
this table.

**Column contract** — every row author (`/extract-signal`) must respect this positional shape;
treat it as a load-bearing "API" any future front-end's `readFeatures()`-equivalent would depend
on (a regex header match + positional `|`-split, not a schema-validated parse):

| Column | Owner | Contents |
|---|---|---|
| `Slug` | agent (permanent once set) | Never renamed/reordered without also updating any downstream parser |
| `Feature` | agent | Short display name |
| `Status` | **human** | `proposed \| committed \| not-built \| built \| out-of-scope` (agents only ever write `proposed`) |
| `UC` | agent | Every `UC-###` id this feature owns or participates in |
| `Code areas` | agent | Optional |
| `Sources` | agent | INT-###/document ids/paths this row traces to |
| `Notes` | agent | **A one-line pointer only** — `See _features/<slug>.md § Notes / History`. Never inline prose. |

**Where the narrative actually lives:** every feature hub (`01-Requirements/_features/<slug>.md`,
§ Feature Hub) carries a `## Notes / History` section, placed right after the feature's one-line
description and before `## Signal Log` — an **append-only, dated bullet list** (one bullet per
event/date, oldest first), the same discipline as `## Changelog`. This is where
`/extract-signal`/`/bigin-transform-signal` write the readable "story" of a feature (why it
exists, what each meeting/CR round added, what got resolved) — the Signal Log stays the atomic
per-signal trace table; the Notes/History section is the chronological narrative a human reads
top-to-bottom. Writing here instead of into `FEATURES.md`'s Notes cell is what keeps the index
thin — do **not** duplicate the same prose in both places.

**Source-of-truth split:** the `Slug`/`Feature`/`UC`/`Code areas`/`Sources` columns above should be
read from each feature hub's own frontmatter (`name`/`fr`/`code_areas`/`sources`, § Feature Hub),
not by parsing `FEATURES.md`'s table — point at notes that already exist and read their metadata,
instead of scanning a markdown table by column position. `FEATURES.md`'s table is still what
`/extract-signal` writes and still the human-facing index (and still what a brand-new feature
shows up in first, before its hub exists) — but it should not be any consumer's *source* for those
five columns. **`Status` is the one exception, read live from `FEATURES.md`'s table**, not from
the hub's `status:` mirror — Status is the column a human hand-edits directly (`proposed` →
`committed`/`built`/`out-of-scope`) and that edit is meant to take effect immediately, not wait for
the next `/extract-signal` run to catch the hub's mirror up. Practically, this
means `/extract-signal` writes every row's `Feature`/`UC`/`Code areas`/`Sources` value onto that
feature's hub frontmatter at the same time it writes the `FEATURES.md` row (creating the hub from
the template first if it doesn't exist yet) — the two copies must never drift, since the hub copy
is what's actually read.

That "never drift" rule applies past the row's creation, too: whenever a later run adds a `UC-###`
to a hub's `uc:` list — `/bigin-transform-signal` minting a new UC (`3-lane-uc.md` § Minting new
UCs, `4-sync.md` § Part 1b) or `/restructure-uc` moving one between hubs — the same actor writes
the matching id onto that feature's `FEATURES.md` `UC` column in the same pass, never leaving it
for a later run to notice. This is always the orchestrating skill's own write, never
`hub-bookkeeper`'s (`agents/hub-bookkeeper.md` never writes `FEATURES.md`) — mirroring a hub's own
tables and mirroring the registry are different writers by design. Skip it and `FEATURES.md`'s `UC`
column goes stale relative to the hub's own `uc:`/`## Use Cases`, silently, with nothing else ever
catching the drift — which is how a reader (human or agent) ends up trusting the registry's
stale, smaller UC set instead of the hub's current one.
