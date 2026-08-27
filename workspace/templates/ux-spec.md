---
id: UX-
type: uiux
title:                  # "<Feature> screens"
status: draft           # draft | needs-clarification | accepted | superseded
                        # (_bigin/conventions/design-conventions.md § Design status vocabulary).
                        # /bigin-generate-design only ever writes draft/needs-clarification;
                        # accepted is human-only (D5).
version: 1.0
feature:                # the ONE FEATURES.md slug that OWNS this spec. One UX spec per feature —
                        # a re-run updates it in place, never forks it.
features: []            # every slug these screens touch, owner first (a cross-feature UC is
                        # designed here, in its primary_feature's spec)
platform: web           # web | mobile | both — COPIED from the project config
                        # (_bigin/system/project.md frontmatter). Absent there reads as `web`, the
                        # compatibility default. A different value here is only ever a PER-FEATURE
                        # OVERRIDE that a UC, a hub ## Design Directives row, or a DESIGN-PRINCIPLES
                        # row EXPLICITLY stated for this feature — cite it on § 1's Platform line.
                        # Never inferred from a step's wording
                        # (design-conventions.md § Platform). Verified in Stage 6 (check 12).
uc: []                  # UC-### id(s) designed here
brs: []                 # BR-### id(s) that produced a state or a validation
entities: []            # EN-### id(s) the screens render fields from
pain_points: []         # PP-### id(s) some § 4 flow's `Resolves` cell names. READ from the hub's
                        # ## Pain Points; this spec never marks one resolved on the register
                        # (design-conventions.md § Write map).
actors: []              # every role § 1's Actor & Scope table carries, each as
                        # "<role>:<own|assigned|unit|all>:<one|few|many>" — e.g.
                        # ["Member:own:one", "Administrator:all:many"]. Read from the in-scope UCs'
                        # § 1 actors, never invented (design-conventions.md § Actor scope).
                        # A spec with two actors at different volume bands must carry SEPARATE
                        # screens for them, not one screen serving both. Verified in Stage 6
                        # (check 14). Absent on a spec written before this key existed —
                        # 3-screens.md § Adopting an existing UX spec builds it on the next run.
sources: []             # UC-###/BR-###/EN-###/PP-### ids + DESIGN-PRINCIPLES row #s + hub directive #s
absorbed: []            # UC-<NNN>@<version> — THE staleness record. Only UCs that really got
                        # screens this run. Re-stamped WHOLE every run (§ Staleness).
nav_map:                # the {nav_map_file} version these screens were specced against
engine:                 # the METHOD layer that decided these screens: wds | figma | <plugin> |
                        # built-in. NOT a renderer — /bigin-generate-design renders nothing. What
                        # actually rendered this spec, if anything has, is § 8's table.
flow_review:            # pfd | <critique skill> | skipped — what Stage 4 actually did. `skipped`
                        # REQUIRES no ### Flow Review table in § 5; a named skill REQUIRES one row
                        # per § 4 flow. An empty table fails either way (Stage 6 check 17).
rendered: false         # false | true — flipped by /bigin-render-design when it appends a § 8 row.
                        # A design run never touches this key, so a spec re-designed after a render
                        # keeps it: § 8's `Against` column is what shows the render went stale.
relationship_model: none  # none | modelled — set by Stage 3 Part 4b's trigger test, verified in
                        # Stage 6 (check 9). `modelled` REQUIRES a filled § 7; `none` requires
                        # § 7 to be absent or empty. An empty § 7 with `modelled` reads as
                        # "considered, nothing found" when nobody looked
                        # (design-conventions.md § The relationship model).
updated:
---

# `UX-<NNN> <Feature>` screens

<!-- THIS SPEC CARRIES NO VISUAL SYSTEM. No colour, no type scale, no spacing, no component library,
no token names or values — /bigin-generate-design produces the EXPERIENCE (actors, screens, states,
navigation, and the flows between them) and nothing else. An element says what it is FOR, via a
semantic ROLE from a closed list (design-conventions.md § Semantic style roles); a real design system
is supplied later by the design team, or bound at render time by /bigin-render-design. -->

## 1. Design Brief
<!-- Assembled in Stage 3 Part 1. Never invented: every line traces to something already written. -->

* **Users:** `<the actors from each UC's § 1 — roles, never named people>`
  <!-- The flat roll-call. The Actor & Scope table below is the same roles with the three facts that
  decide their screens — same list, never a different one. Neither replaces the other: this line is
  what the feature's audience is, the table is what each of them can reach. -->
* **Platform:** `<web / mobile / both — the project config's value, carried down by Stage 1>`
  <!-- The config decides it. A UC, a directive, or a principle matters here only when it EXPLICITLY
  states a platform for THIS feature — then write that value and cite the row that stated it
  ("mobile — hub ## Design Directives #3: the courier's job list is phone-only"). "At a desk" is
  where an actor is, not a stated platform; ambiguous → the config value plus a § 6 question.
  "not stated" is not a value: absent everywhere means the config, and absent there means `web`. -->
* **Pain points in scope:** `<PP-### — the client's own words, one line each>`
  <!-- The hub's ## Pain Points rows that are not resolved. These are what the § 4 flows have to
  fix, and what shapes emphasis and ordering on a screen — ground 1b. A pain point NEVER grounds a
  screen, field, or capability existing (design-conventions.md § Grounding). "None open" is a real
  and common result; say it rather than leaving the line blank. -->
* **Principles applied:** `<DESIGN-PRINCIPLES row # — the principle, in the client's words>`
* **Directives applied:** `<hub ## Design Directives row # — the directive>`
* **Known gaps:** `<one line per open question already on a UC's § 5, or per entity still proposed/draft>`
  <!-- These are gaps the screens work around, not gaps to guess at. -->

**Actor & Scope**
<!-- One row per actor the in-scope UCs name in their § 1 — no more, no fewer. This table is what
stops the run designing one screen for two actors whose work is not the same work: a member reading
their own record and an administrator working a directory of ten thousand read identically in a UC
and are two different products (design-conventions.md § Actor scope).

EVERY cell is READ, never assumed. Unresolvable → the narrowest reading, plus a § 6 question.
  Sees whose   own | assigned subset | their unit's | all
               ground: a BR-### on visibility/permission, the UC's § 1 pre-conditions, or how the
               UC defines the actor
  How many     one | few | many (unbounded — it grows with the business)
               ground: the EN-### relationship cardinality, a BR-### cap, or a UC step
  May act on   read one · act on one · act on MANY at once
               ground: a UC step or a BR-###. NEVER the volume (D8) — an unstated bulk action is a
               requirement gap in § 6, owner: client, not a design call. -->

| Actor | Sees whose records | How many | May act on | Grounded by |
|-------|--------------------|----------|------------|-------------|

## 2. Screen Inventory
<!-- One row per screen. `Serves` is the step id(s) the screen delivers — every S# must exist in
that UC and not be removed.

Two UCs landing on the same place share ONE row ONLY when their actors' scope agrees. Compare the
Actor & Scope rows above (design-conventions.md § Actor scope):
    the VOLUME BAND differs      → TWO rows, each naming its own actor
    the CAPABILITY differs       → TWO rows
    both agree, only WHICH       → ONE row; carry the difference in the § 3 element table's
    FIELDS are visible differs     `Visible to` cell, citing the BR-### that restricts it
Two rows means two names that make the actor legible — `Member Directory (Admin)` beside
`My Profile`, never `Member Record` written twice.

`Volume` is the band from the Actor & Scope table — it decides the machinery the § 3 spec must
carry: a `many` screen needs a find mechanism and the volume states, a `one` screen must not have
them (there is nothing to find). -->

| Screen | Actor | Volume | Purpose | Serves | Entities | Key actions |
|--------|-------|--------|---------|--------|----------|-------------|

## 3. Screen Specs
<!-- One block per inventory row. SEMANTIC STRUCTURE ONLY: a role, never a value and never a token
id (D2). Every element carries what grounds it — a UC step, a BR, an entity field, an existing
pattern, or a directive (D3). An element grounded in nothing is a question in § 6, not a guess. -->

### `<Screen name>`

* **Purpose:** `<one line>`
* **Serves:** `UC-<NNN> S<n>, S<n>`
* **Actor:** `<the ONE role this screen is for — from the Actor & Scope table>`
* **Scope:** `<whose records · how many · what they may do, each cited — e.g. "all · many (EN-004,
  many Orders per Account) · read one, act on one (UC-030 S2)">`
  <!-- A `many` screen MUST carry a find mechanism (search, filter, or sort) and the volume states
  below; a `one` screen must carry neither. Anything past finding — bulk action, export, a saved
  view — needs its own UC step or BR-### or it is a requirement gap in § 6 (D8). -->
* **Regions:** `<this platform's vocabulary only — web: header / nav / main / aside / footer ·
  mobile: header / content / tab-bar / sheet / fab — semantic elements, not a pixel layout>`
  <!-- A `nav` region on a phone screen, or a `tab-bar` on a web one, is the wrong vocabulary: it
  asks a tool to build a shell the platform does not have (design-conventions.md § Platform;
  Stage 6 check 13). -->

<!-- PER-PLATFORM LAYOUT SPLIT — on `platform: both` ONLY, and ONLY for a screen whose two shells
genuinely differ. Everything else in this block stays SHARED: one Purpose, one Serves, one Element
table, one States table, one Interactions table — the inventory and the behaviour are the user's
goals, only the layout is the platform's. Replace the single **Regions** line above with:

* **Layout — Web:** `<header / nav / main / aside / footer>`
* **Layout — Mobile:** `<header / content / tab-bar / sheet / fab>`

Identical on both platforms → keep the one **Regions** line and write NO split. Two identical
Layout lines are worse than none: they read as a considered difference and leave the next run
maintaining two copies of one layout (check 13). -->

| Element | Content / copy | Role | Field | Visible to | Grounded by |
|---------|----------------|------|-------|------------|-------------|
<!-- `Role` is ONE semantic role from the closed list, or BLANK. Most elements are blank.
  primary action · secondary action · destructive · danger · warning · success · info ·
  emphasis · muted
NEVER a hex, a px, a font name, or a `--token` id (D2) — there is no design system here to resolve
one, and a renderer given a name it cannot resolve picks its own value. Exactly ONE
`primary action` per screen (Stage 6 check 3). A screen needing a role this list does not carry
raises a § 6 question; it never invents an eleventh.

`Visible to` is filled ONLY when a BR-### restricts an element to some of this screen's actors
(`Admin only — BR-018`). Blank means every actor of this screen sees it. It is not a place to
smuggle a second actor into a screen the split rule says should be two.

`Grounded by` accepts a UC step, a BR-###, an EN-### field, a PP-### (for EMPHASIS or ORDERING
only — never for the element existing), a vault pattern, or a directive #. -->

**States**
<!-- On a `many` screen the VOLUME states are required and grounded by the volume fact itself
(cite it like any other ground: "EN-004 many-per-Account · UC-030 S2"):
empty · few · many at real scale · loading · error. The `many` row says the real number the
prototype should render — "≈10,000 records, page 1 of 400" — because a prototype seeded with three
rows tests nothing the client is worried about. -->

| State | Trigger | What the user sees | Grounded by |
|-------|---------|--------------------|-------------|

**Interactions**

| Control | Does | Goes to |
|---------|------|---------|

## 4. Flows
<!-- ONE flow per user goal, per ACTOR — never one per platform, never one per screen. This is the
artifact a client recognises as their working day or fails to (design-conventions.md § User flows
and pain points). Written in Stage 3 Part 4c; reviewed, and possibly reordered, in Stage 4.

`Resolves` names the PP-### this journey fixes, or "—" when it serves a UC goal alone. D6: a flow
must resolve SOMETHING STATED — a UC goal or a pain point. A journey that resolves neither is
invented, and belongs in § 6 as a question rather than here as a row.

`Steps to goal` is the screen count from trigger to success. It is not a budget and there is no
right value — a five-step approval a BR requires is five steps. It exists so Stage 4 has something
to compare a journey against.

On `platform: both`, the phone splitting one web form into three sheets is the SAME journey on more
surfaces: say so inside `Path` (`web: Details → Confirm · mobile: Details → Reviewers → Confirm`),
never as a second flow. Omit this whole section on a design-only feature (no UC). -->

### `UC-<NNN> <goal>`
* **Actor:** `<the ONE role on this journey>`
* **Entry:** `<the trigger, in plain words>`
* **Path:** `<Screen>` → `<Screen>` → `<Screen>`
* **Success:** `<what the user is left with>`
* **Failures:** `<exception>` → `<screen/state the user is left on>`
* **Resolves:** `PP-<NNN>` `<or "—">`
* **Steps to goal:** `<N>`

### Coverage
<!-- Written by Stage 5 (_bigin/stages/design/5-verify.md), re-written WHOLE every run — a partial
table claims a coverage nobody checked. Read design-conventions.md § Coverage verification.

This is the FORWARD direction, and the only thing in this pipeline that can find an OMISSION. Every
other check runs backward — element to ground — and backward passes cleanly on a spec with a whole
exception flow missing, because nothing on a screen that was never drawn can be traced.

One row per: non-removed S#/A#/E# of every in-scope UC · each BR-### they cite that constrains what
an actor sees or may do · each EN-### field their steps read or write (NOT every field the entity
owns) · each UNRESOLVED hub PP-### · each open hub ## Design Directives row · each active
DESIGN-PRINCIPLES row.

Three verdicts, no fourth:
  covered                        `Covered by` names the SCREEN AND THE STATE — and for a PP-###, the
                                 FLOW and where in it, never a screen alone. A `covered` verdict
                                 over a `—` is the table claiming what nobody checked (Stage 6
                                 check 17 blocks on it)
  gap → ## 6 Q<n>                genuinely not designed. Points at a question that really exists and
                                 is unchecked
  out of scope — <reason>         excluded by something ON RECORD, and the record is cited. An
                                 uncited exclusion is a gap wearing a decision's clothes -->

| Item | Kind | Covered by | Verdict |
| :--- | :--- | :--- | :--- |
| `UC-<NNN> S<n>` | step | `<Screen> · <state>` | `covered` |
| `UC-<NNN> E<n>` | exception | `—` | `gap → ## 6 Q<n>` |
| `BR-<NNN>` | rule | `<Screen> · <state>` | `covered` |
| `PP-<NNN>` | pain point | `<Flow> · <where in it>` | `covered` |
| `EN-<NNN>.<field>` | field | `—` | `out of scope — <hub ## Design Directives #n>` |
| `directive #<n>` | directive | `<Screen> · <element>` | `covered` |
| `principle #<n>` | principle | `<where it applied>` | `covered` |

## 5. Navigation & Flow Review
<!-- Where this feature sits in the vault-wide navigation, and what Stage 4's review found. The
feature JOINS the shared navigation map at 04-UIUX/_ux/navigation-map.md; it never forks it. -->

* **Nav map version:** `<version>`
* **Nav entries added:** `<[structure] id (e.g. settings.team) — label — screen, or "none — reached
  only via another screen">`
  <!-- On `both`, name which structure each entry went into — `[Web] settings.team` /
  `[Mobile] more.team` — because the two shells are two trees: the same feature legitimately carries
  a different id in each, and an entry added to one shell only is normal, not an omission. On `web`
  or `mobile` there is one structure, so the prefix is unnecessary.

  A feature normally contributes 0-2 entries, not one per screen. Zero is common and correct: most
  screens are reached THROUGH another screen, and a menu entry for one is a second door that drifts
  from the real IA the first time one path changes. -->
* **Nav entries re-nested this run:** `<old id → new id — why, or "none">`
  <!-- Stage 4's one structural change. Still append-only (D1): the new row is added and the old id
  is retired in the nav map's § Removing an entry. An id is NEVER edited in place. -->

### Flow Review
<!-- Written by Stage 4 (_bigin/stages/design/4-flow-review.md), re-written WHOLE every run. One row
per § 4 flow.

THIS SECTION IS CONDITIONAL, and its absence means something specific. Stage 4 runs only when a
perception-first-design (or generic critique) skill is installed:
    a skill was installed   → one row per § 4 flow, and frontmatter flow_review: names the skill
    none was installed      → DELETE this heading and its table entirely, and set
                              flow_review: skipped
NEVER leave an empty table. An empty ### Flow Review reads as "every journey was reviewed and
nothing was found" — the strongest claim this pipeline makes about a flow — when nobody looked.
Stage 6 check 17 blocks on the mismatch either way.

Verdicts, and nothing else:
  sound                       the journey works, and its pain point is fixed where the row says.
                              Giving `sound` to a flow naming a PP-### without having found the
                              moment it is fixed is the one dishonest cell here
  improved — <what changed>   say WHAT, in a phrase. A human diffs this against what they last read
  gap → ## 6 Q<n>             points at a question that really exists and is unchecked

`Steps to goal` shows the change when there was one (`4 → 2`) and the single number when there was
not. -->

| Flow | Actor | Steps to goal | Resolves | Verdict |
| :--- | :--- | :--- | :--- | :--- |

## 6. Open Questions
<!-- The canonical list. Zero unchecked lines ⟺ status is not needs-clarification
(design-conventions.md § Design status vocabulary). Mirrored on the hub's ## Open Questions / Gates
with the SAME sentence. Never re-ask a question already open on a UC's § 5.
Mark a question whose answer would change what the SYSTEM DOES as a requirement gap — it is
/bigin-transform-signal's to resolve, never this stage's.

Format:
- [ ] Q: <self-contained question, plain business language> (owner: client|team) (ref: UX-<NNN>)
      A: -->

## 7. Relationship Model
<!-- CONDITIONAL. Delete this whole section unless the feature passed the relationship trigger
(_bigin/stages/design/3-screens.md Part 4b) — an empty § 7 claims the relationship was considered.
Read design-conventions.md § The relationship model first.

This section describes the relationship the requirements ALREADY imply. It never discovers that the
product needs memory, autonomy, or a dashboard (D7). Expect more requirement gaps here than rows:
a UC almost never states an autonomy ceiling, a retention rule, or who owns the memory. Every gap
goes in § 6 marked as a requirement gap and belongs to /bigin-transform-signal — never to a UC edit.
-->

### Relationship Context
<!-- One line each, each grounded or dropped. "Not stated" is a legitimate value and becomes a
requirement gap in § 6 — never a plausible number. -->

| Aspect | This feature | Grounded by |
|--------|--------------|-------------|
| Expected duration | `<how long a user stays in this relationship>` | |
| Interaction frequency | `<daily / weekly / sporadic>` | |
| Autonomy ceiling | `<the MOST the agent may do unprompted — from a BR, never assumed>` | |
| Memory sensitivity | `<what would be harmful to remember, per a rule or a stated preference>` | |

### Memory Architecture
<!-- What the agent carries between sessions. EVERY row cites an EN-### field: a system cannot
remember what nothing stores, so a row with no field behind it is a requirement gap, not a design
row. `Who controls it` is who may see, correct, or clear it — from a BR or the UC's actors. -->

| What it remembers | Entity field | Surfaced on | Who controls it | Grounded by |
|-------------------|--------------|-------------|-----------------|-------------|

### Trust Map
<!-- The longitudinal counterpart to § 3's within-session States. Per screen or per agent decision:
what the agent SHOWS versus what it DOES at each stage, and how a user corrects it. Only fill a
stage a BR actually grants (D7) — an ungranted stage 3 is a requirement gap, not a design choice. -->

| Screen / decision | Stage 1 — transparent | Stage 2 — selective | Stage 3 — autonomous | Correction path | Grounded by |
|-------------------|----------------------|---------------------|----------------------|-----------------|-------------|

### Proposed Measures
<!-- At most THREE. Owner: team, always. A measure never licenses a screen, a field, or an event to
track — instrumentation is behaviour. Not a requirement, not a target, not a dashboard. -->

| Measure | What would be observed | Which row above it tests |
|---------|------------------------|--------------------------|

## 8. Rendered Artifacts
<!-- ABSENT until somebody renders. Written by `/bigin-render-design` ALONE — no stage of
`/bigin-generate-design` touches this section, and a design run neither creates it nor clears it.

POINTERS ONLY. Rendered HTML, images, and PDFs are outputs the engine owns; pasting their contents
in makes this spec a second, drifting copy of something else, stale the next time anything renders.

| Rendered | Engine | Platform | Screens | Artifacts at | Against |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `<YYYY-MM-DD>` | `open-design (<design system id>)` | `<web \| mobile>` | `<N> of <N>` | `04-UIUX/_prototypes/<run>/ · <OD project id>` | `UX-<NNN>@<version>` |

The `Engine` cell carries the DESIGN SYSTEM in parentheses because that is the fact a reader needs
to know whether two renders are comparable — same screens rendered against two different brands look
like two different products, and since this spec carries no visual system of its own, the bound
system is the ONLY record of what the client actually saw. `Artifacts at` names the COPIED-BACK
folder first and the Open Design project id second: the folder is the durable artifact, the project
id is where it came from. Never record a `previewUrl` here — it dies when Open Design restarts.

`Against` is what makes a render's staleness visible: a spec at v1.4 whose only render was against
v1.2 has screens nobody has ever looked at. Re-rendering appends a row; it never edits one. A build
spanning several specs writes the SAME row to every participating spec, each with its own
`Against`. -->

<!-- THE SPEC ENDS HERE. There are no prototype-prompt blocks: /bigin-render-design builds its own
prompt from § 1-§ 5 plus the UCs, BRs, and entity register, so a hand-written second copy of the
same screens was a duplicate that drifted from the section above it — and it inlined token values
this pipeline no longer produces. A spec written before this change carries `## Prototype Prompt —
…` headings; they are deleted on that feature's next design run (3-screens.md § Adopting an existing
UX spec, Stage 6 check 7). -->

## Changelog
- 1.0 (YYYY-MM-DD) — created from `UC-<NNN>@<version>`
