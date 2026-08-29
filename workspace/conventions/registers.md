# Conventions — the vault-wide registers

The four cross-feature registers and the mapping rules that decide what lands in each:
entities, pain points, design principles, and the retired scenario register — plus how a signal
becomes an artifact, and what happens when it maps to no feature at all.

**Read by** `/extract-signal` (filing), `/bigin-transform-signal` (Stage 4 sync), `/sync-entities`.

## Signal → artifact mapping

Every `[requirement]`/`[feedback]` signal `/bigin-transform-signal` folds in lands in exactly one
(sometimes two, when it's genuinely both) of these places — never loose in prose:

| Signal is… | Goes to |
|---|---|
| A testable, actionable statement about behaviour | a step in a new/updated `UC-###`'s flow (`use-case.md` § Use Case) |
| A conditional/policy constraint, feature-level or governing one workflow | a new/updated `BR-###`, `uc: []` citing the use case(s) it governs, mirrored read-only in each one's `§ 4` (`core.md` § ID scheme, `use-case.md` § Use Case) |
| A presentation-only statement — look, layout, tone, copy voice, interaction feel, accessibility affordance — that changes no behaviour | a **design directive**, never a UC line: a `DESIGN-PRINCIPLES.md` row when durable/cross-cutting, a row in its feature hub's `## Design Directives` when feature-scoped, or both (`use-case.md` § Traceability chain's Design chain, § Design Principles Register) |
| A data field/entity described — a thing the business tracks and its attributes | a `proposed` row in `ENTITIES.md`, later promoted to `EN-###` `## Fields` (§ Entity Data Model) — new or existing entity |
| Narrative context — the client's stated why, not yet actionable on its own | the UC's `## 1` Business Need / Goal |
| A concrete frustration/cost the client named, with no requirement attached yet | a new `PP-###` in `01-Requirements/PAIN-POINTS.md` (§ Pain Point Register), its id added to the UC's `pain_points:` once one exists |
| A description of how the **current/legacy** system behaves (`[decision]`, as-is) | context, not a build item: an `ENTITIES.md` row when it names data the business tracks, the UC's `## 1` Business Need when it explains why the replacement is wanted. Never a functional requirement — it describes software being retired |
| Something a person committed to supply or do (`[commitment]`) | stays on its feature hub's `## Signal Log` as its own row until delivered; its `Notes` names the row or question it unblocks. Often the authoritative version of a rule the transcript states loosely |

A `[pain-point]` with no attached requirement is not a gap to fill — it's kept on record
(`PP-###`, `Status: open`) until a later signal turns it into a UC/BR line or an epic/story
resolves it, or it just stays as context. Never force a pain point into a functional requirement
it doesn't actually support, and never drop it for lack of a home. A signal can legitimately land
in more than one row at once — e.g. a field-level rule is both an `EN-###` mapping row and, if the
client also gave a reason, feeds that entity's or the citing UC's own context.

## Entity Data Model

A `[requirement]` signal sometimes describes not a behavior but a **thing the business tracks** —
a Vendor record, an Application, a Wallet — and the concrete data it must carry: field names,
types, and relationships. Left to plain UC routing, this either gets buried as a clause inside a
Functional requirement sentence ("the system must capture the vendor's tax ID") or repeated with
drift across every UC that happens to touch the same entity — entities are usually **shared across
features** (a Vendor's fields matter to both a Vendor Management feature and a Payments feature),
so a per-UC field list duplicates and drifts.

`01-Requirements/_entities/EN-<NNN>-<slug>.md` (`type: entity`) is the artifact for this: one
document per business entity, promoted by `/sync-entities` from a `proposed` row in
`01-Requirements/ENTITIES.md`, the first time a UC it's processing (or a `BR-###` that UC mirrors)
actually references it. `/bigin-transform-signal` never promotes one — a UC/BR drafted or updated
mid-review can cite the entity by name against the `proposed` row, but the row stays a row until
approval, so a goal that never reaches `/approve-uc` never leaves behind an entity doc nobody needed.

Promotion itself is decoupled from the approval moment: `/approve-uc` only ever flips the UC's own
`status`/`version`/`## Changelog` and sets its `synced: false` — it never touches `ENTITIES.md`, an
`EN-###` doc, or a feature hub, so approving several UCs in a row is never blocked on shared-file
writes. `/sync-entities` is what actually does the promotion/extension described below, run separately
whenever convenient (right after an approval, batched at the end of a review session, or lazily before
whatever later stage needs the entity data) — it scans for `status: approved` + `synced: false` UCs
and processes them one at a time, the same sequential discipline as always, and flips each to
`synced: true` once done.

**Frontmatter (`_bigin/templates/entity.md`):**
```yaml
---
type: entity
id: EN-
name:
kind:            # actor | data | system
status: proposed # proposed (row exists in ENTITIES.md, no doc yet) -> draft (this doc exists,
                 # fields still settling) -> approved (human confirmed at a UC/BR review gate)
features: []     # every feature slug whose UC(s)/BR(s) reference this entity
updated:
---
```

**Body:**
- `## Fields` — `Field | Type | Required? | Source | Notes`. `Source` cites the Signal Log row (or
  UC/BR) that introduced or last changed the field.
- `## Relationships` — how this entity references others (e.g. "belongs to EN-002 Customer
  (many-to-one)"), each citing the UC/BR it's drawn from.
- `## Changelog` — same convention as every other artifact.

A field-level business rule is **not** a subsection of the entity doc — it's a full `BR-###` file
under `01-Requirements/_brs/` like any other business rule (`core.md` § ID scheme), citing the entity's
fields it governs in its own body. An earlier draft of this document described a
`## Field-level Business Rules & Mapping` subsection inside the entity doc, sharing one vault-wide
`BR-###` sequence with `EN-###`; that was never built — `BR-###` is its own independent sequence
(`core.md` § ID scheme's Next-ID rule), and there is no per-entity BR subsection.

### The doc is a data dictionary, not a diff of the last approval

What a developer, a PRD reader, or a designer opens an `EN-###` for is **the whole shape of one
business object** — every field it carries, each field's type, whether it's required, and what values
it may take. Three rules make it that, and each one exists because the obvious incremental behaviour
produces a document that is worse than useless: an authoritative-looking file that is quietly a
fragment.

- **One doc per real-world business object — never per field.** `Application`, `Vendor`, `Wallet`.
  An attribute is a **row inside** its owner's `## Fields`, never its own `EN-###`: a doc named
  `Application.Private-School Certification Status`, whose `## Fields` holds exactly the one row it
  was named after, is this rule broken — the field belongs in `EN-001 Application`. Resolve a
  `<Entity>.<Field>` name (in an `ENTITIES.md` row, a UC's `entities:`, or an existing doc) to the
  owning object before writing anything, and cluster aggressively when in doubt: a field wrongly
  filed under a neighbouring object is one row to move, while a fragment doc splits an entity's
  definition across files nobody knows to open together.
- **Every known field, every time — not just the ones the UC being synced happened to touch.**
  `/sync-entities` runs per approved UC, but the doc it writes is not scoped to that UC: before
  writing, gather the union of every field any source has stated for this object — the
  `ENTITIES.md` row's `Fields (so far)`, this doc's existing rows, and every UC/BR listed in its
  `features:` that references it — and write the full set, each row keeping its own `Source`.
  A doc rebuilt from one UC's view is how an entity ends up documented as whatever was approved
  last Tuesday.
- **Spell out the values.** A `Type` cell reading a bare `enum`, `status`, or `code` documents
  nothing. Enumerate the states inline, separated by ` / ` because a `|` would break the table
  (`enum: Pending School Review / Certified / Rejected`), and give a format where one was stated
  (`date: YYYY-MM-DD`, `money: USD`). Values genuinely never stated → write
  `enum: values not stated` rather than a plausible list, and raise the gap as a `- [ ] Q:` on a UC
  that references the field, where the status invariant will actually track it.

**Never invent a field, a type, a value, or a required-ness the sources didn't state** (hard rule 1).
"Complete" here means complete over what the vault actually knows, with the gaps visible as gaps —
not a developer's guess at what an Application record probably needs.

### A fragment already on disk: merge, never delete

Attribute-shaped docs exist in vaults created before this contract. `/sync-entities` repairs one when
it next touches the owning object: every row from the fragment moves into the owner's `## Fields` with
its `Source` cite intact, and the fragment is stamped `status: merged` + `merged_into: EN-###`, its
body replaced by a one-line pointer. **The id is never reused and the file is never deleted** (hard
rule 1) — a `PRD-###`, `UX-###`, or UC frontmatter that still cites it must keep resolving. Every
`ENTITIES.md` row, `entities:` list, and hub `## Entities` line pointing at the fragment is repointed
at the owner in the same pass.

**Registry:** `01-Requirements/ENTITIES.md` (`type: entities-register`, singleton,
`_bigin/templates/entities-register.md`) —
`EN-### | Entity | Status | Fields (so far) | Features | Notes`, created by `/extract-signal` the
moment a signal describes a data field or entity attribute, with a `proposed` row per entity.
Cluster aggressively — **one row per real-world business object, not per field**: a signal about a
new field on a tracked object adds to that object's `Fields (so far)` cell, and never earns a row of
its own. A row named `<Entity>.<Field>` is always the bug, not the exception.
`/sync-entities` promotes a row to its own `EN-###` document; the register keeps the row afterward as
the vault-wide index (mirroring how `FEATURES.md` stays the index once a feature hub exists).

## Pain Point Register

Every `[pain-point]` signal gets a **`PP-###` id the moment it's extracted** — **or cites the existing
one it restates.** Clients repeat the same frustration in meeting after meeting, so `/extract-signal`
matches against the register before minting: a match adds the new `INT-###` to that row's `Source` and
cites its id on the signal row instead of creating a near-duplicate. Ids are vault-wide,
numbered like `BR-###` (scan `01-Requirements/PAIN-POINTS.md`, not any UC, since a pain point can
predate its feature's UC) — tracked in `01-Requirements/PAIN-POINTS.md`
(`type: pain-point-register`, singleton, instantiate from
`_bigin/templates/pain-points-register.md`):

| PP-### | Statement | Feature | Source | Status | Proposed solution | Resolved by |
|--------|-----------|---------|--------|--------|--------------------|--------------|

- **Status**: `open` (named, nothing addressing it yet) · `addressed` (a `Resolved by` link exists
  and a human confirmed it's sufficient — this is a judgement call, so it never auto-flips the way
  `needs-clarification` does) · `orphaned` (the feature/UC that would have addressed it went
  `out-of-scope`, or the client explicitly walked it back — never silently deleted).
- **Proposed solution**: a short, plain-language description of the approach addressing it, filled
  in as soon as a requirement/story is drafted with this pain point in mind. Not a separate
  approval-gated artifact — a solution is a fact **about** the row, not a new document.
- **Resolved by**: starts blank or citing whatever's available first (a UC functional-requirement
  line, a `BR-###`). It would be **backfilled** by an epic/story stage, which does not exist, so
  actually implements the solution, since that's the concrete unit of work a PO tracks a pain
  point's resolution against.
- Same append-only discipline as every other register here: `PP-###` is permanent, a row is never
  deleted — a walked-back pain point becomes `orphaned` with an explanation in `Resolved by`.

**Cited from the use case** once one exists: the UC's `pain_points:` frontmatter lists the `PP-###`
ids the workflow exists to resolve — **ids only, no fourth copy of the table**. The register is the
vault-wide source of truth (queryable across features) and each feature hub's `## Pain Points` is the
per-feature mirror a human reads; a third table on the UC would be a third thing to keep in sync for
facts that are one grep away. The pre-UC `FR-###` model did carry that table, which is why an absorbed
FR still shows it.

**Created** by `/extract-signal` the moment a `[pain-point]` signal is extracted. **`Resolved by`
(epic/story) never backfilled** — no skill produces one. **Solution** is no longer backfilled by
`/enrich-feature` — enrichment moved off the UC (§ Reconciliation notes), so a human fills it
directly, or it's left blank. **Status flipped to `addressed`** only by a human.

## Design Principles Register

A `[constraint]` signal sometimes isn't feature-specific at all — "keep it minimal," "use our
brand colors," "our users skew older, avoid tiny tap targets" apply to every feature, not just
whichever UC happens to be open when the client says it. Left to the normal signal→UC routing
above, a cross-cutting preference either gets awkwardly bolted onto one feature's
`## Business Rules` or is lost entirely if no UC exists yet when it's said.

`01-Requirements/DESIGN-PRINCIPLES.md` (`type: design-principles`, singleton, vault-wide) is the
standing register for these. `/extract-signal` appends a row whenever an extracted `constraint`
signal reads as a durable, cross-cutting preference rather than a one-off constraint tied to a
single feature:

- **Feature-specific** visual/interaction constraints ("this donor dashboard should feel warm,
  less corporate") go to that feature hub's own `## Design Directives` section, on the Design chain
  (`use-case.md` § Traceability chain) — **not** onto its UC. An earlier draft of this document routed them to
  the UC; that put untestable presentation language inside approved functional scope and made a
  purely visual note wait behind `/approve-uc` before `/bigin-generate-design` could ever see it. A
  feature-scoped directive that turns out to change behaviour was misrouted and belongs back on the
  UC — see `_bigin/stages/transform/3-routing.md` § The design boundary test.
- **Cross-cutting** preferences (brand, tone, accessibility, interaction, layout, content,
  platform) append a row to `DESIGN-PRINCIPLES.md`: `# | Principle | Why | Category | Source |
  Status | Notes`, citing the INT id like any other signal. A signal can land in both places at
  once if it's stated about one feature but clearly generalizes. An earlier draft of this document
  specified the columns without `Why`, and the register template shipped without `Category` or
  `Status`; the seven-column form above is canonical, and a register file already created with the
  older header keeps it — append rows matching whatever header is on disk rather than migrating a
  live register mid-run.
- Same append-only discipline as `FEATURES.md`/the Signal Log: `#` is permanent, never delete a
  row — a later statement that contradicts an earlier one is a new row, with the old row's
  `Status` flipped to `superseded` (or `rejected` if the client/team explicitly walked it back)
  and `Notes` pointing at what replaced it. Every edit bumps the file's `version` and appends a
  `## Changelog` line, so the register's own history is auditable over time, same as any other
  vault artifact.

Downstream: `/bigin-generate-prd` reaches it only **through** the `UX-###` that already applied it —
its § 9 quotes the design's stated intent (`Principles applied`) rather than re-reading this register,
so a PRD can never claim a client preference the screens don't actually reflect. An earlier draft of
this document had a PRD stage reading the register directly and citing rows in a design-goals section;
that reading is deliberately not what got built. `/bigin-generate-design`
reads it **directly** (not via a PRD at all) and seeds the shared design system's `## Foundations` from its
`active` rows — so it stays authoritative even if a given PRD section forgot to transcribe a
preference, and so a feature that reaches design before its PRD is finished still produces screens
consistent with what the client has said. That register is **read-only** to the design stage: it
holds client-stated preferences, and a token or pattern an agent chose is not one.

## Business Scenarios (retired)

A `[requirement]`/`[feedback]` signal sometimes describes a real-world flow that crosses feature
boundaries — a request submitted in one feature, approved in another, settling as a financial
adjustment in a third (not just "this feature calls that API" — an end-to-end sequence a human
would narrate as one story). When the requirement artifact was one `FR-###` per testable statement,
that flow had no home, and `01-Requirements/SCENARIOS.md` (`SCN-###`, one register row per scenario)
was built to give it one.

**A use case is that home, and it is strictly more.** A `UC-###` whose `features:` lists every
participating slug records the same sequence *plus* the actors, the trigger, the pre- and
post-conditions, the alternative and exception paths, the rules that govern it, its open questions, and
a human review gate — none of which a register row could carry. So `SCN-###` is retired:

- **Never create or extend a `SCN-###` row.** A cross-feature flow routes down the UC lane like any
  other flow (`_bigin/stages/transform/3-routing.md` § The lane table).
- **Existing rows stay** (hard rule 1 — nothing is deleted). Set `Status: superseded` with
  `Notes: absorbed by UC-###`, and list the `SCN-###` in that UC's `absorbs:` frontmatter, the first
  time a signal brings the flow back into play.
- **Existing hub `## Business Scenarios` sections stay** as history. The live pointer is the
  `## Use Cases` row, on every participating hub, and it deliberately carries **no step number** — the
  `(step N of M)` on each hub was this register's worst failure mode, going stale silently every time a
  step was inserted mid-flow. The UC file is the single place the flow is written out.
- `01-Requirements/SCENARIOS.md` and `_bigin/templates/scenario-register.md` remain readable so old
  ids resolve; nothing writes to either.

## Signal → feature mapping (and what happens when it can't map)

Every signal must anchor to a `01-Requirements/FEATURES.md` slug before it can be staged.

### Declared features (direct intake only) — a floor, not a ceiling

`source: direct` is the one intake path with a human present at capture, so it's the one that can
**ask** which feature(s) the material belongs to instead of working it out later. `/bigin-intake`
offers a multi-select over `FEATURES.md` (skipping is a first-class answer) and records the result
in the note's `declared_features:` frontmatter — **only ever what the user actually named**. An
agent must never populate it from its own reading of the content; that would launder a guess into
a human declaration and break capture-only.

Two feature fields live on an INT note and they are not the same thing:

| Field | Written by | Means |
|---|---|---|
| `declared_features: []` | `/bigin-intake` (direct only), from the user's selection | "The human said, at capture, that this is about these features." Plural, up-front, advisory-but-authoritative. Never rewritten by `/extract-signal`. |
| `feature:` | `/extract-signal`, or a human repairing an unmapped signal | The resolved single anchor — and the repair channel below. Singular, an outcome. |

How `/extract-signal` consumes a non-empty `declared_features:`:

- **Every declared slug is settled — don't re-litigate it.** No "which feature?" open question, no
  `unresolved` row, no `needs-review` tag, no scope-triage question for a signal that plainly
  belongs to one of them. The human already answered; re-asking is the same duplicate-gate problem
  `intake.md` § Feedback handling exists to avoid.
- **A declared slug with no `FEATURES.md` row gets a `proposed` row added** (version bump +
  changelog, `Sources` citing the INT id). This is the single exception to "agents never add scope
  rows unattended" — it holds *only* because the slug came from a human at capture. A slug that
  looks like a typo of an existing row is flagged in the report, never silently remapped to what
  the agent thinks was meant, **and never minted either** — minting a typo creates a permanent
  duplicate slug, which is worse than either option the flag offers.
  The runnable procedure is `_bigin/stages/extract/3-filing.md` § The declared-slug exception —
  that file is what the filing stage actually reads, and it is the only place this exception's steps
  are written out. This bullet is the standard; that section is the procedure. They must not
  disagree: an earlier version of this pair had conventions granting the exception while the filing
  guide said "NEVER a new `{requirements_file}` row", which made the case a coin flip.
- **The scan continues anyway.** The declaration is what the human knew when they typed it, not a
  promise about content they may not have re-read — a note declared `vendor-management` can still
  carry a payments signal. Those anchor normally. This is what makes it a floor rather than a
  ceiling.
- **A declared slug that ends up with no signal anchored to it is reported as a mismatch**, and
  the declaration is left in place. It usually means the content didn't say what the human
  thought — worth their attention, never silently dropped, and never patched over by manufacturing
  a signal to justify it.
- **Empty or absent → nothing changes.** Anchoring runs exactly as it does for every email and
  meeting note, per the rules below.

### When a signal can't map

When no existing row fits, `/extract-signal` never guesses the anchor — but it doesn't stop at "no
match" either. It distinguishes two failure shapes, because they ask a human two different questions
(full rules: `/extract-signal`'s `3-filing.md` § Step 1 — Anchor):

- **Ambiguous among existing features** — more than one slug's scope plausibly fits: record the
  candidates on the signal line (`unresolved — candidates: a / b`) and ask which one. Candidates are
  joined with `/`, never `|`: this value lands in a table cell, and a raw pipe splits the row.
- **No existing feature fits, and the signal reads like new scope** — record `unresolved — none
  found`, and draft a **suggested slug** (kebab-case, from the signal's own vocabulary, checked
  against the registry for a near-miss first) plus a **one-line scope** statement, so the question
  gives a human something to confirm or edit rather than a blank line to fill from scratch.

Either way:

- Add an Open Question (owner: team) on the closest UC, or on the source INT note itself if no UC
  exists yet, worded for whichever shape it is (`3-filing.md` § Step 5 — Questions has the exact
  templates).
- Park the source INT note `status: needs-clarification` and add `needs-review` to its `tags:` —
  the same surfacing mechanism as any other open question, so it's visible as specifically needing
  a human to map the feature, not just answer a content question.
- The human closes it by writing the correct slug back — as the `A:` answer on the note's Open
  Questions line, or by setting the note's `feature:` frontmatter directly — and ticking the box.
  For a new-scope question, the human mints the `proposed` `{requirements_file}` row themselves
  (the drafted slug/scope is a starting point, not something `/extract-signal` ever writes there
  unattended). The next `/extract-signal` pass reads the answer as the resolved mapping and stages
  the signal against the named feature.
