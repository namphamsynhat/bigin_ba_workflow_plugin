# Design Conventions

The **UX** rulebook: what a screen spec is, what a user flow is, what the navigation map holds.

**This file is deliberately separate from `conventions.md`.** That file is the **requirement**
rulebook — what a use case is, when a signal becomes a rule, who may approve scope. This one is the
**experience** rulebook. They never merge:

```text
a rule about WHAT THE SYSTEM DOES        → conventions.md          (requirement side)
a rule about HOW A USER GETS THERE       → this file               (experience side)
a "design rule" that decides behaviour   → it is a requirement. It is in the wrong file.
```

**There is no design system here, and no tokens.** `/bigin-generate-design` produces the
**experience** — actors, screens, states, navigation, and the flows that connect them — and says
nothing about colour, type, spacing, or component styling. A screen names a **semantic role**
(§ Semantic style roles); a real design system is supplied later, by the design team or by whichever
system a render is bound to. A run that invents a palette has designed the one thing nobody asked it
for and locked the client's brand to it.

Read only the sections your stage needs.

| Stage | Sections |
|---|---|
| `1-scope` | Paths · Write map · Design status · Staleness · **Platform** |
| `2-navigation` | The navigation map · User flows and pain points · **Platform** |
| `3-screens` | The UX spec · Screen spec · Semantic style roles · Grounding · The relationship model · Open questions · The navigation map · **Platform** · **Actor scope** |
| `4-flow-review` | The flow review · User flows and pain points · The navigation map · Grounding · Open questions |
| `5-verify` | Coverage verification · Grounding · The UX spec · Open questions · Rendering is a separate step · **Platform** · **Actor scope** |
| `6-close` | Design status · Write map · Staleness · The navigation map · The flow review · The relationship model · Coverage verification · **Platform** · **Actor scope** |

## Paths

Project-relative, from the repo root.

**Experience side — this stage owns these.**

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{ux_dir}` | `04-UIUX/` | one spec per feature: `UX-<NNN> <Feature>.md` |
| `{ux_system_dir}` | `04-UIUX/_ux/` | the **one, vault-wide** UX system: navigation and the flow spine. Not a design system — it holds no colour, type, spacing, or component styling |
| `{nav_map_file}` | `04-UIUX/_ux/navigation-map.md` | the vault's menu/navigation system |
| `{prototype_dir}` | `04-UIUX/_prototypes/` | rendered prototypes copied back out of Open Design, one folder per render: `<YYYY-MM-DD>-<slug\|multi>/`. Written by `/bigin-render-design` and by nothing else — **no design stage touches it** |
| `{design_stages_dir}` | `_bigin/stages/design/` | `1-scope`, `2-navigation`, `3-screens`, `4-flow-review`, `5-verify`, `6-close` |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | this file |
| `{template_ux}` | `_bigin/templates/ux-spec.md` | |
| `{template_nav_map}` | `_bigin/templates/navigation-map.md` | |

**Requirement side — inputs. Read them; do not rewrite them.**

| Variable | Path | What design takes from it |
| :--- | :--- | :--- |
| `{uc_dir}` | `01-Requirements/_ucs/` | the flow the screens serve — `## 2` steps, `## 3` branches |
| `{br_dir}` | `01-Requirements/_brs/` | validations and error states |
| `{entity_dir}` | `01-Requirements/_entities/` | the fields a form actually has |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | the `PP-###` register — **what the flows exist to fix** (§ User flows and pain points) |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | client-stated durable preferences |
| `{hub_dir}` | `01-Requirements/_features/` | `## Design Directives` and `## Pain Points` in, `## UX Spec` out |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | the slug registry |

Missing `_bigin/conventions/`, `_bigin/stages/design/`, or `_bigin/templates/` → stop and say
`/bigin-new-project` must run first. A subagent that cannot read its stage guide still writes a
screen, just one following no rule.

**A design system, if this vault has one, is not on either list.** A design team may drop one
anywhere they like; nothing in this skill reads it, writes it, or requires it. Which system a
prototype is rendered against is `/bigin-render-design`'s question, asked of a human, at render time.

## Write map — what design may touch

```text
WRITE   {ux_dir}                      the UX spec (create, or update in place) — except `## 8
                                      Rendered Artifacts`, which only /bigin-render-design writes
        {nav_map_file}                menu entries — ADD ONLY
        hub ## UX Spec                link + status
        hub uiux:                     the UX-### id
        hub ## Design Directives      Status: open → reflected, on rows a screen really implements
        hub ## Open Questions / Gates design questions
        hub ## Notes / History · ## Changelog   one line each

READ    every path in the requirement table above

NEVER   a UC's ## 1-## 6 · a BR's rule statement · an EN field list
        DESIGN-PRINCIPLES.md          (client-stated only — research findings are not client words)
        PAIN-POINTS.md                the register is the requirement side's. A flow that resolves a
                                      pain point says so in the UX spec; it never writes the row's
                                      `Resolved by` cell, and never adds a pain point of its own
        a hub's Signal Log · ## Pain Points · ## Requirement Readiness · status: · uc: · br:
        FEATURES.md
        _bigin/system/project.md      the engagement config, INCLUDING platform: — design READS it
                                      (§ Platform) and never writes it. An unstamped config is
                                      reported and defaulted, never stamped from here: stamping it
                                      is /bigin-upgrade-project's job, with a human present to
                                      answer (1-scope.md § Adopting an existing project config).
```

**One sanctioned exception.** When a UC is **not** `approved`, append **one** line to its
`## Discussion` citing the UX spec as supporting visual evidence. Nothing else, ever, and nothing at
all on an `approved` UC.

## The eight design hard rules

```text
D1  The navigation map is APPEND-ONLY. Never delete or rename an entry — retire it.
D2  A screen spec names a SEMANTIC ROLE, never a value and never a token id. No hex, no px, no font
    name, no `--color-*` (see § Semantic style roles).
D3  Every screen, element, state, and flow is GROUNDED (see § Grounding). Ungrounded → a question.
D4  Requirement content is READ-ONLY. Design never edits a UC, a BR, an entity, or a pain point.
D5  Never write status: accepted. A human accepts a design; an agent never does.
D6  A user flow must RESOLVE SOMETHING STATED — a UC goal, or a `PP-###` pain point it names. A
    flow that resolves nothing on record is an invented journey (see § User flows and pain points).
D7  A relationship model never grants MEMORY, AUTONOMY, or RETENTION the requirements did not
    state. What an agent keeps, decides alone, or forgets is behaviour — a requirement gap, never
    a design call (see § The relationship model).
D8  An actor's DATA SCOPE and VOLUME are read from the requirements, never assumed — and volume
    licenses FINDING machinery only, never a CAPABILITY. Acting on many records at once is
    behaviour: a requirement gap, never a design call (see § Actor scope).
```

## Platform

**What is being built — a browser app, a phone app, or both.** It is the one project-wide fact that
changes the *shape* of a design without changing a single requirement, so it lives in the project
config, not in an artifact:

```text
_bigin/system/project.md  frontmatter  platform: web | mobile | both
field absent (a project initiated before the field existed)   → treat as `web`
```

`web` is the compatibility default on purpose: it is what every design run before this field produced,
so an unstamped project keeps designing exactly as it always did rather than silently changing shape.

**Read it once, at Stage 1, and pass it down.** Stage 1 announces it; Stages 2–5 and every dispatched
worker are *told* it. A worker never re-reads the project config to decide it, for the same reason it
never re-detects the method layer: two workers inferring a platform differently produces one product
with two navigation shells.

### Per-feature override — the only thing that outranks the config

A UC, a hub `## Design Directives` row, or an active `DESIGN-PRINCIPLES` row that **explicitly states
a platform for a feature** overrides the config *for that feature only*, and gets cited as its ground
like any other decision:

```text
config says `web`, a directive reads "the courier's job list is phone-only"
    → that feature designs as `mobile`, grounded by that directive row #
config says `both`, a UC's actors read "the back-office reviewer at a desk"
    → NOT an override. "At a desk" is where an actor is, not a stated platform.
nothing states a platform                → the config value, unchanged, no citation needed
```

**The bar is an explicit statement, not an inference.** Guessing "this is obviously mobile" from a
step's wording is the same failure as inventing a screen: it reaches a client as a decision somebody
made. Ambiguous → design to the config and raise an Open Question.

### The regions vocabulary, per platform

`## 3`'s `regions` line is semantic structure, never a pixel layout (§ Screen spec) — but which
semantic regions *exist* is a platform fact:

```text
web     header · nav · main · aside · footer          the persistent-shell vocabulary
mobile  header · content · tab-bar · sheet · fab      the phone vocabulary
```

A `nav` region on a mobile screen, or a `tab-bar` on a web one, is the wrong vocabulary — it produces a
spec that asks a render tool to build a shell the platform does not have.

### What `both` means, exactly

**One platform-neutral requirement set, two design outputs.** This is not a compromise; it is the
plugin's own invariant (§ The eight design hard rules, D4) applied to platform:

```text
requirements   ONE UC set, platform-blind. A UC never forks per platform, and platform never
               becomes a UC step, a branch, or a business rule.
screens        ONE screen inventory (the same user goals), with a per-platform LAYOUT SPLIT only
               where the two genuinely differ — a shared behaviour block, then `Layout — Web` /
               `Layout — Mobile`. Identical on both → one layout line, no split.
flows          ONE flow per user goal. A phone splitting one web page into three sheets is the same
               journey on more surfaces, not a second journey (§ User flows and pain points).
nav map        ONE file, TWO structures: `## Structure — Web` and `## Structure — Mobile`, mapping
               the same feature set onto each shell (§ The navigation map).
```

**Never split the screen inventory itself.** Two inventories means two designs to keep in sync, and
the second one goes stale the first time a UC changes. The inventory is the user's goals; only the
layout is the platform's.

### Mobile stays generic

No iOS-versus-Android split at this stage. A phone screen is a phone screen: one primary action, a
tab bar, sheets. Platform-specific interaction conventions (a back gesture, a system share sheet, a
material-versus-cupertino control) are build-time decisions nothing on record has stated — an
explicit client statement about one is a `DESIGN-PRINCIPLES` row, not a design call made here.

### Rendering is a separate step

`/bigin-generate-design` produces a **specification** — actors, screens, states, real copy, the
navigation shell, the flows, and a coverage table. It renders nothing, checks for no design tool, and
has **no halt of its own**.

Turning that specification into something a client can look at is `/bigin-render-design`, invoked by a
human who has decided they want a prototype:

```text
/bigin-render-design [feature slug | UX-### ...] [--design-system <id>] [--project <name|id>]

the ENGINE is Open Design, on every platform. `platform:` decides the SHELL a render builds — a
sidebar/nav-bar at desktop width, or a 390px phone frame with a bottom tab bar — never which tool
builds it.
FOUR THINGS ARE THE HUMAN'S, and that skill asks about each it cannot already resolve:
    which features            never "everything"
    which Open Design project share an existing one, or create a new one for this vault
    which DESIGN SYSTEM       the design team's, or one from Open Design's own catalog. THIS SKILL
                              PRODUCES NONE, which is exactly why it is asked rather than defaulted.
                              DESIGN-PRINCIPLES still wins over whichever is picked
    which model               from what Open Design offers, never a hardcoded id
Open Design unreachable  → that skill retries, then hands the spec over to paste in by hand.
                           Nothing upstream ever halts
```

**Why this is not part of the design run.** Which features, which design system, and when are
timing-and-taste decisions belonging to whoever is going to sit with the client. Binding them to an
unattended pipeline re-rendered features nobody asked about, picked a brand nobody was asked about,
and — the expensive part — let a missing prototype tool stop a stage that reads use cases and writes
markdown.

**What guards against a design nobody can look at.** `5-verify` proves the spec is complete enough to
render *cold*, on any engine, months later (§ Coverage verification). A spec that passes that is a
spec a render cannot go wrong on for want of input — with the single, deliberate exception of the
visual system, which is not this skill's to supply.

## Semantic style roles — what replaced tokens

A screen spec says what an element **is for**, never what it looks like. One word, from a closed
list, in the element table's `Role` cell:

```text
primary action    the one thing this screen exists for
secondary action  a real action, not the main one
destructive       deletes, cancels, or revokes something
danger            a state or badge that means something is wrong or overdue
warning           something needs attention but is not yet wrong
success           something completed
info              neutral supporting information
emphasis          content that must be read first
muted             present, deliberately quiet — metadata, timestamps, helper text
default           carries no particular weight (leave blank; `default` is the absence of a role)
```

**A role is a design-system-independent fact.** "This is the primary action" stays true whichever
brand, palette, or component library is bound later — which is the whole reason it survives where a
token name would not. Whoever supplies the design system maps the ten roles once; nothing in the
vault has to change.

```text
ALLOWED     `primary action` · `danger` · `muted`
FORBIDDEN   `#2563eb` · `16px` · `Inter Semibold` · `--color-action-primary` · `btn-primary`
            → all four are D2 broken. The first three pin a value nobody stated; the last two cite a
              system this vault does not have, so nothing resolves them and a renderer picks its own
```

A screen that needs a **role the list does not carry** does not get a new role invented for it. It is
an Open Question (owner: team) asking whether the list should grow — a private eleventh role is a
one-screen vocabulary nobody else can map.

**Layout, density, and hierarchy are not roles.** "Three columns", "compact table", "above the fold"
belong in `regions` and the element order, where they already are.

## User flows and pain points

A screen inventory says *what exists*. A **flow** says how a real person gets from a trigger to an
outcome — and it is the artifact this stage exists to get right, because it is the one a client can
recognise as their own working day or fail to.

```text
one flow  =  one user goal, for ONE actor, end to end
             entry (the trigger, in plain words)
             → the screens in order, one line each
             → the success end
             → each failure end, and the screen or state the user is left on
```

Every flow is a `## 4 Flows` entry in the UX spec, and every flow carries the two things that make it
reviewable:

```text
Resolves     the PP-### pain point(s) this journey fixes, or "—" when it serves a UC goal alone
Steps to     how many screens the actor passes through from trigger to success
goal
```

### D6 — a flow resolves something stated

```text
a UC goal                  → always sufficient. The flow delivers the UC's ## 2, end to end.
a PP-### pain point        → cite it. This is the flow saying WHY the journey is shaped this way
                             rather than some other way that also delivers the steps.
neither                    → an invented journey. It is not a flow; it is an Open Question.
```

**The pain-point register is READ-ONLY here** (§ Write map). A flow names the `PP-###` it resolves;
it never writes that row's `Resolved by` cell, never changes a pain point's status, and never adds
one. A pain point the flows reveal — a real friction nobody wrote down — is an Open Question owned by
the client, and `/bigin-transform-signal` is what puts it on the register.

**A pain point is not a licence to add a screen.** `PP-004: "reviewers lose track of what they
already approved"` grounds *how* the queue is ordered and *what* the flow shows on return; it does
not, on its own, ground a whole "approval history" screen nobody's UC asked for. Same line as
ground 2b in § Grounding: it shapes a grounded thing, it does not create one.

### Flows on `both`

One flow per user goal, not one per platform. A phone that splits one web form into three sheets is
carrying the **same journey across more surfaces** — say so inside the flow's `Path` line
(`web: Details → Confirm · mobile: Details → Reviewers → Confirm`), never as a second flow. Two flows
for one goal is two journeys to keep in sync, and the second is wrong the first time a UC changes.

## The flow review

`4-flow-review` — a pass over the flows and the navigation **as a whole**, after every screen exists
and before coverage is verified. It is the only stage that looks at the product the way a user meets
it: not "is this screen grounded?" but "does this journey make sense, and does it fix what the client
said hurt?"

**It runs when a perception-first-design skill is installed, and is skipped, silently, when one is
not** (`method-layer.md` § Stage 4). That is a deliberate gate: the pass is a real critique method,
and a run that fakes it produces a `### Flow Review` table nobody should trust. A skipped review is
reported as skipped, with the install line, and the run continues — nothing here halts.

### What it may change, and what it may only ask

```text
MAY CHANGE, in place        the flow's screen ORDER · which screen an interaction leads to · a nav
                            entry's placement or nesting · a screen's element ORDER · copy that
                            misleads · a state a flow reaches but no screen declared
                            → every one of these is still GROUNDED (§ Grounding) and changelogged

MAY ONLY ASK (## 6)         a screen that should exist and does not · a field, capability, or state
                            nothing grants · a pain point the flows cannot fix as specified · a
                            requirement gap of any kind
                            → the fix is a 3-screens dispatch next run, or /bigin-transform-signal.
                              A review pass that draws the missing screen has stopped reviewing
```

The line is the same one `5-verify` holds: **repair what is already decided; ask about what is not.**
The difference is direction — this pass repairs the *journey* between screens, `5-verify` repairs the
*bookkeeping* about them.

### The verdicts

Each flow gets one row in the UX spec's `## 5 Navigation & Flow Review`:

```text
sound                        the journey works as specified, and its pain point is fixed where the
                             row says it is
improved — <what changed>    the pass reordered, re-pointed, or re-worded something. Say what, in a
                             phrase, so a human can diff it against what they last read
gap → ## 6 Q<n>              the journey does not work and the fix is not this pass's to make
```

## Actor scope — who a screen is for, and how much they hold

Platform decides the **shape** of a design. Actor scope decides its **machinery**. The two are
orthogonal, and the second is the one a design run silently gets wrong: a UC reads "the actor views
member information" identically whether that actor is one member looking at their own record or an
administrator working a directory of ten thousand. Same words, same steps, two different products —
and the run that merges them ships the member's screen to the administrator.

Three facts, per actor, per screen. Each one is **read**, never assumed:

```text
whose records   own | assigned subset | their unit's | all
                ground: a BR-### about visibility or permission, the UC's ## 1 pre-conditions, or
                        how the UC itself defines the actor
how many        one | few (a countable handful) | many (unbounded — it grows with the business)
                ground: the EN-### relationship cardinality (one Account has many Orders), a BR-###
                        stating a cap, or a UC step that says so
what they may   read one · act on one · act on MANY at once
do              ground: a UC step or a BR-###. NEVER the volume — see D8 below.
```

Unresolvable from all three grounds → the scope is an Open Question (D3), and the screen is designed
to the **narrowest** reading in the meantime. Designing wide and asking later means the client
reviews an administrator's reach that nobody granted.

### The volume band is what changes the screen

```text
one     the record itself. NO find machinery — there is nothing to find, and a search box over one
        record is an invented affordance.
few     the set, listed whole. No pagination, no search: a filter over nine rows is noise.
many    the set can never be shown whole, so the screen's real job becomes FINDING, and it needs:
          a find mechanism    search, filter, or sort — at least one
          the volume states   empty · few · many (at real scale) · loading · error
        A `many` screen written without them is a design that works only on demo data, and it
        collapses the first time it meets the client's real table.
```

The band is a fact about the data, not a guess about the actor: `many` comes from the entity's own
cardinality or a BR, and an actor whose scope is `own` over a one-per-user entity is `one` no matter
how senior they are.

### D8 — the line volume may not cross

```text
LICENSED by the volume fact itself, cited as its ground
("EN-004 — many Orders per Account · UC-030 S2"):
    search · filter · sort · pagination or infinite scroll · a result count
    the empty / many / loading / error states
    a density choice (a table rather than cards) once the set is `many`

NOT licensed by volume, ever — every one of these is a CAPABILITY:
    bulk edit · bulk delete · "select all matching this filter" · export
    an approval, assignment, or status change applied to many records at once
    a saved view, a subscription, an alert
    → no UC step and no BR-### grants it  →  a REQUIREMENT GAP in ## 6, owner: client
```

An administrator who "obviously needs bulk delete" is exactly the failure D7 catches on the agent
side: plausible, unstated, and it reaches the client looking precisely like something somebody
specified. The client agrees to it in a prototype, and from that moment it is a requirement nobody
wrote, costed, or ruled on.

### When one place is two screens

Part 2's merge rule — two UCs landing on the same place become one screen — is the rule that
produces a one-size-fits-all design. It holds only when the actors' three facts agree:

```text
same place, two actors → compare the three facts:
    the VOLUME BAND differs      → TWO screens. A one-record view and an unbounded directory share
                                   nothing but the entity; they are not one screen with a filter bar
                                   bolted on.
    the CAPABILITY differs       → TWO screens. One actor reads their own record; another works a
                                   queue and acts on what is in it.
    both agree, and only WHICH   → ONE screen. Carry the difference in the element table's
    FIELDS are visible differs     `Visible to` cell, citing the BR-### that restricts it.
```

Same discipline as the `Layout — Web` / `Layout — Mobile` split (§ What `both` means): split what
genuinely differs, and never restate one design twice. What it splits on is different — a layout
split is **one** design on two shells, an actor split is **two** designs, because the two actors are
not doing the same work.

Two screens means two `## 2` inventory rows, each with its own `Serves` naming its own actor's UC
steps, and names that make the actor legible — `Member Directory (Admin)` beside `My Profile`, never
`Member Record` written twice. It also means **two flows** (§ User flows and pain points): the two
actors are on two journeys.

### Scope is not a persona

The same warning § The relationship model carries. The UCs already name the actors; actor scope asks
three questions about each of them and nothing else. It never invents a user, a job title, a
demographic, a seniority, or a "power user" nobody wrote down, and it never reasons from what such a
person would probably want. An actor no UC names is not in scope — it is an Open Question.

## Design status vocabulary

Its own list, unrelated to the UC/BR one.

| Status | Meaning |
|---|---|
| `draft` | screens exist, written by the design stage. The resting state. |
| `needs-clarification` | ≥ 1 unchecked `- [ ] Q:` in the spec's `## 6 Open Questions`. |
| `accepted` | a human reviewed the screens and said yes. **Human-only** (D5). |
| `superseded` | replaced by another `UX-###`. Rare — updates land in place. |

**The invariant:** zero unchecked `- [ ] Q:` in `## 6` ⟺ status is not `needs-clarification`; any
unchecked line ⟺ status **is** `needs-clarification`. Set it **last**, from a live count of the
section on disk — never from what the run intended.

The navigation map carries **no** status. It is versioned and append-only instead.

## Staleness — what "unprocessed" means

A UX spec's `absorbed:` list is the record. Each entry is `UC-<NNN>@<version>`, read from that UC's
frontmatter at the moment it was designed.

```text
per feature, per UC in the hub's uc: list:
    UC not in absorbed:                     → NEW      design it
    UC in absorbed: at an OLDER version     → CHANGED  redesign its screens
    UC in absorbed: at the same version     → CURRENT  skip, and say so
```

`sources:` can never go stale, so it can never answer this. `absorbed:` is **re-stamped whole every
run** — it describes what the spec reflects **now**, not what some earlier pass folded in.

**Only stamp a UC that actually got screens this run.** A run that designs 6 of 10 UCs stamps 6,
leaves 4 off, and stays `needs-clarification` naming them. A spec that stamps what it did not design
reads as finished forever.

## The UX spec

`{ux_dir}/UX-<NNN> <Feature>.md`, `type: uiux`, from `{template_ux}`. **One per feature** — never a
second one for a feature that already has one; a re-run updates it in place (bump `version`, append
a `## Changelog` line).

A **cross-feature UC** is designed once, in the UX spec of its `primary_feature`. Every other slug
in the UC's `features:` gets the same `## UX Spec` pointer on its hub. Same write-ownership rule the
UC itself follows.

`## 1 Design Brief` carries an **Actor & Scope** table — one row per actor the in-scope UCs name,
with the three § Actor scope facts and what grounds each. It is what stops the run designing one
screen for two actors whose work is not the same work.

Sections: `## 1 Design Brief` · `## 2 Screen Inventory` · `## 3 Screen Specs` · `## 4 Flows`
*(carrying `### Coverage` — § Coverage verification)* · `## 5 Navigation & Flow Review` ·
`## 6 Open Questions` · `## 7 Relationship Model` *(conditional — § The relationship model)* ·
`## 8 Rendered Artifacts` *(pointers only, and written by `/bigin-render-design` alone — absent
until somebody renders)* · `## Changelog`.

**The spec ends at `## 8`.** There are no prototype-prompt blocks: `/bigin-render-design` builds its
own prompt from these sections, the UCs, the BRs, and the entity register, so a second hand-written
copy of the same screens was a drifting duplicate of the thing beside it. A spec written before this
change carries `## Prototype Prompt — …` headings; they are harmless and self-heal on that feature's
next design run (`3-screens.md` § Adopting an existing UX spec).

`## 7` is **appended after `## 6`, never inserted before it.** Renumbering `## 6 Open Questions`
would silently invalidate every hub mirror, stage guide, and verification check that cites it by
number — the section list is append-only for the same reason the navigation map is (D1).

## The navigation map

**One** navigation map, at `{nav_map_file}`, shared by the whole vault — the menu/navigation system
for the platform or project: every persistent, directly-reachable entry point (a nav bar item, a
sidebar link, a tab, a flyout child) and the screen it opens. Two modes:

```text
{nav_map_file} absent  → BOOTSTRAP  create it from {template_nav_map}; the first screens seed it
{nav_map_file} present → EXTEND     load it, reuse its tree, ADD new entries screens actually need
```

It lives at `04-UIUX/_ux/`, **not** inside a design-system folder. Navigation is an experience
decision this skill owns end to end; a design system is a visual system somebody else supplies, and
putting the two in one directory made the first look like part of the second.

### The shell is a platform fact (§ Platform)

The map's own shape follows `platform:` — one file either way, but the `## Structure` it holds differs:

```text
web     ## Structure                 a persistent sidebar / nav-bar shell. Arbitrary depth, as below.
mobile  ## Structure                 a TAB BAR — at most 5 top-level entries — plus per-screen
                                     headers and sheets. Depth below a tab is still arbitrary, but a
                                     6th tab is not a nav decision, it is an Open Question.
both    ## Structure — Web           BOTH sections, in one file, mapping the SAME feature set onto
        ## Structure — Mobile        each shell. One table per section, same columns.
```

**The five-tab cap is a real constraint, not a style preference.** A phone tab bar physically stops
being usable past five, so a sixth top-level candidate means either two features share a tab or one
belongs a level down — and which of those is right is a human call (an Open Question on this file,
owner: team), never a silent sixth row.

On `both`, an entry that exists on one shell and not the other is normal and expected: a web sidebar
can carry an admin area a phone app never surfaces. Say so in that row's `Grounded by` rather than
mirroring it onto the other shell to look symmetrical.

**Arbitrary depth, via a path id.** The map is not fixed at "group → entry" — a real IA nests as
deep as "Settings → Team → Members". One row per entry, at any depth; its `id` is a dot-path, the
parent's `id` plus one segment (`settings`, then `settings.team`, then `settings.team.members`). The
path **is** the tree: no separate level or parent column, and no cap on how deep it goes. A row can
be a pure container (a section header with children but no screen of its own — `Points to: —`), a
leaf (a screen, no children), or both. On `both`, an `id` is unique **within its own `## Structure`
section** — the same feature legitimately appears as `settings.team` on web and `more.team` on
mobile, because the two shells are two trees, not one tree rendered twice.

**Not every screen gets an entry.** A screen a user reaches directly from the menu — at whatever
depth — gets one; a screen reached only *through* another screen (a detail opened from a list, a
step inside a wizard, a modal) does not — it is reachable through its parent, and a menu entry for it
is a duplicate way in that drifts from the real IA the first time one of the two paths changes.

```text
directly reachable from the menu, on its own (top-level or nested)  → gets an entry
reached only via another screen's control                          → no entry (it is a destination,
                                                                       not a menu item)
```

Every entry is **grounded** the same way any other design decision is (§ Grounding below): a role
split traces to a `BR-###` or a UC's actors, a nesting decision traces to a stated preference, an
existing branch of the tree, or a `PP-###` the placement resolves, and a label that nothing in the
flow calls for is an Open Question, never an invented menu.

**Append-only (D1).** A screen that stops existing does not get its row deleted — see the template's
§ Removing an entry: mark it `retired`, keep the row, keep the history. Retiring a container retires
its whole subtree implicitly; its children are not re-listed. Deleting a row breaks nothing
technically, but it also erases the record of why the IA looks the way it does.

**`4-flow-review` may move an entry; it may never delete one.** Re-nesting a row (changing its `id`
to sit under a different parent) is the one structural change that pass makes, and it is still
append-only in effect: the old `id` is retired in § Removing an entry with `re-nested to <new id>` as
its reason, and the new one is added. A row that silently changes `id` breaks every screen spec
citing the old path.

## Screen spec — semantic structure only

One entry per screen in `## 3`:

```text
purpose      one line: what the user achieves here
serves       UC-<NNN> S<n>, S<n> …   the steps this screen delivers
actor        the ONE role this screen is for (§ Actor scope). Two actors whose volume band or
             capability differs get two screens, not one screen serving both
scope        whose records · how many · what they may do — each cited
             (e.g. `all · many (EN-004 many-per-Account) · read one, act on one — UC-030 S2`)
regions      web:    header / nav / main / aside / footer      — semantic HTML elements
             mobile: header / content / tab-bar / sheet / fab  — the phone vocabulary
             (§ Platform. On `both`, a shared behaviour block plus a `Layout — Web` /
              `Layout — Mobile` split, ONLY where the two actually differ)
elements     per element: what it is · the content or copy · its semantic ROLE (§ Semantic style
             roles), when it carries one
             · the entity field it renders, when it renders one
             · `Visible to`, ONLY when a BR-### restricts that element to some of the screen's
               actors — blank means every actor of this screen sees it
states       empty · loading · validation-error · permission-denied · success
             each from a BR, an exception flow, or an entity's required fields — never invented
             a screen whose volume band is `many` additionally carries the VOLUME states —
             empty · few · many at real scale · loading · error — grounded by the volume fact
             itself (§ Actor scope, D8)
interactions what each control does, and which screen or state it leads to
```

**Copy is content, not styling** — real words a user reads, in the client's language, not `Lorem`.

## Grounding — the test that keeps design out of the requirements

Every non-trivial decision (a screen existing, a field appearing, a state, a flow's shape, a nav
grouping) traces to exactly one of:

```text
1  a REQUIREMENT   a UC step / branch, a BR, or an EN field         → cite the id
1b a PAIN POINT    a PP-### on the register                          → cite the id. It grounds HOW a
                                                                       flow is shaped, never THAT a
                                                                       screen exists (§ User flows)
2a a VAULT PATTERN an existing screen in this vault                  → name it
2b an EXTERNAL     a pattern from an installed design/UX skill       → name the skill and the pattern
   PATTERN
3  a PREFERENCE    a DESIGN-PRINCIPLES row or a hub directive        → cite the row #
```

**2a and 2b are not interchangeable.** A vault pattern is evidence that this product already works
that way. An external pattern is only evidence that the pattern exists somewhere:

```text
2a can ground THAT a screen, field, or state exists — a sibling feature already ships it here
2b can only shape HOW something already grounded by 1, 2a, or 3 gets built
2b ALONE                → not a ground. It is an Open Question, or a requirement gap.
```

An external catalog that grounds existence is how a whole screen nobody asked for arrives carrying a
citation. The citation makes it *look* grounded, which is strictly worse than an obvious guess.

**1b behaves like 2b, not like 1.** A pain point is real, client-stated, and on the register — but it
states a *problem*, not a system behaviour. It grounds a flow's ordering, a screen's emphasis, a nav
placement, a default. It never grounds a new screen, field, capability, or state on its own; that
needs ground 1, or it is a requirement gap.

None of the above → **it is not yours to settle**. Write an Open Question (D3). An invented screen
is scope nobody asked for, and it looks exactly like a designed one.

An entity that is still `proposed`/`draft` grounds a decision as a **known gap**, not settled fact —
say so next to the field list rather than treating it as final.

**A volume fact is ground 1, and it grounds finding machinery only.** An `EN-###` relationship
cardinality cited with the UC step that puts an actor in front of that set ("EN-004 — many Orders
per Account · UC-030 S2") grounds search, filters, sort, pagination, and the volume states — the
machinery without which the screen only works on demo data. It never grounds a capability: bulk
action, export, or a saved view needs its own UC step or BR-###, or it is a requirement gap
(§ Actor scope, D8).

## Coverage verification — the only check that can find an omission

Grounding above runs **backward**: every element on a screen back to the thing that licensed it. It
is what stops the design inventing scope, and it is completely blind to the opposite failure — a step,
a rule, a field, or a whole exception flow that nobody drew. A screen that was never drawn has no
element to trace, so every backward check passes on a spec with a third of the requirement missing.

`5-verify` runs the **forward** direction, once, per design run:

```text
every non-removed S# / A# / E# of every in-scope UC        →  the screen AND STATE that carries it
every BR-### they cite that constrains what an actor
  sees or may do                                           →  the state, validation, or Visible to
every EN-### field their steps read or write                →  the element that renders it
every PP-### this feature's hub carries, still open         →  the flow that resolves it
every open hub ## Design Directives row                     →  the screen that implements it
every active DESIGN-PRINCIPLES row                          →  where it applied
```

Three verdicts, and no fourth:

```text
covered                          the screen and the state, both named (for a PP-###: the FLOW and
                                 where in it). A `covered` verdict over an empty cell is the table
                                 claiming a coverage nobody checked
gap → ## 6 Q<n>                  genuinely not designed. A design question (owner: team), or a
                                 REQUIREMENT GAP (owner: client) when the answer would change what
                                 the system DOES — /bigin-transform-signal's, never written on the UC
out of scope — <cited reason>    excluded by something ON RECORD, and the record is cited. An
                                 exclusion with nothing behind it is a gap wearing a decision's
                                 clothes, and the field the client expected vanishes with an
                                 explanation nobody made
```

The table lives in the spec (`## 4 Flows` → `### Coverage`), is re-written **whole** every run — the
same rule `absorbed:` follows, for the same reason — and is verified on disk by `6-close`'s coverage
check.

**It repairs; it does not design.** An item a screen plainly carries whose row failed to say so gets
the row fixed. An item nothing carries gets a question. Adding the missing screen, state, or control is
a `3-screens` dispatch on the next run — a verification pass that draws the thing it was checking for
has no independent verdict left to give (D3).

**Render readiness is verified in the same pass**, and it is the safeguard that replaced the old
required-engine halt (§ Rendering is a separate step). A render may happen months later, on a tool
nobody has picked, run by someone who never read the requirements — so the spec must be sufficient
input *now*: this platform's regions, real copy and real field names, every state named, every element
carrying a role or deliberately carrying none, the nav shell resolvable, a `many` screen's real scale
in words, a phone screen's device facts. A box that cannot be ticked from the record is a question,
never a plausible fill: a render engine given a gap produces something convincing, and a convincing
prototype is reviewed as a specified one.

**The visual system is the one thing render readiness does not check.** No colour, type scale, or
component library is expected in the spec, because this skill produces none — the design system is
bound at render time (§ Rendering is a separate step). A spec is render-ready without one.

## The relationship model

`## 7 Relationship Model` on a UX spec. **Conditional** — it exists only on a feature that passes the
relationship trigger (`3-screens.md` Part 4b). Most features never get one, and an *empty* one is
worse than none: it reads as "the relationship was considered and there isn't one" when nobody looked.

It exists because one thing an agent feature's design must say has nowhere else to live:

```text
a STATE        within ONE session    empty · loading · error · success        → ## 3, per screen
a TRUST STAGE  across MONTHS         what the agent shows, suggests, or does  → ## 7
                                     alone at relationship month 1 vs 12
```

`## 3`'s `States` table is within-session by construction. A screen that discloses its full reasoning
to a new user and acts quietly for a year-old one is not in two states — it is the same state at two
points in a relationship, and squeezing that into `States` produces a spec that reads as a bug.

### The three parts, and what grounds each

| Part | Rows | Grounded by |
|---|---|---|
| **Relationship Context** | expected duration · interaction frequency · the autonomy **ceiling** · memory sensitivity | a UC's trigger/post-conditions, a BR, an active DESIGN-PRINCIPLES row, or a hub directive |
| **Memory Architecture** | what the agent carries between sessions · where that lives · who can see, correct, or clear it | **an `EN-###` field, always.** A system cannot remember what nothing stores |
| **Trust Map** | per screen or per agent decision: what stage 1 / 2 / 3 shows vs does, and the correction path | a `BR-###` about who may do this, a confidence or threshold rule, or a UC exception flow |
| **Proposed Measures** | at most **three**, each naming what would be observed and which row above it tests | owner: **team**. Never a requirement, never a screen |

### The rules that make this safe

```text
a Memory Architecture row with no EN-### field behind it   → a REQUIREMENT GAP, not a design row.
                                                             The field is the design's only evidence
                                                             the memory exists at all.
an autonomy stage no BR-### granted                        → a REQUIREMENT GAP (D7). Design may
                                                             describe how autonomy is DISCLOSED;
                                                             it never decides that it exists.
a retention or forgetting rule nothing stated              → a REQUIREMENT GAP. "The user can clear
                                                             their history" is a behaviour promise.
a Proposed Measure                                         → stays a measure. It never licenses a
                                                             screen, a field, or an event to track —
                                                             instrumentation is behaviour too.
a memory, goal, or trust SCREEN from a pattern catalog     → 2b alone (§ Grounding). Not a ground.
```

The gaps are the point. A UC almost never states an autonomy ceiling, a retention rule, or who owns
the memory — so a well-run relationship model on a real agent feature produces **more requirement
gaps than design rows**, and that is the section working, not failing. `/bigin-transform-signal` owns
every one of them; this stage writes none of them onto a UC (D4).

### What this section is not

```text
NOT a persona            the UCs already carry actors. Never invent a user to have a relationship with.
NOT an architecture      no schema, no storage design, no retention implementation. A field name and
                         an owner, nothing past that.
NOT a metrics plan       three proposed measures, team-owned. Dashboards, instrumentation, and
                         targets are product work happening somewhere else.
NOT a reason to add      it describes the relationship the requirements already imply. It never
    screens             discovers that the product needs a memory dashboard.
```

## Open questions

Design questions live on the UX spec's `## 6`, and are mirrored on the hub's
`## Open Questions / Gates`. Same sentence in both places — a re-worded mirror reads as a second
question, gets answered twice, and can never be paired back up.

```text
- [ ] Q: <self-contained question, plain business language> (owner: client|team) (ref: UX-###)
      A:
```

Never copy a question that is already open on the UC's `## 5`. If the answer would change **what the
system does** rather than how it looks or flows, say so in the question and in the report: it is a
requirement gap, and `/bigin-transform-signal` owns it.
