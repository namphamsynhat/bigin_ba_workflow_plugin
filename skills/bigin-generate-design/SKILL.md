---
name: bigin-generate-design
description: This skill should be used when the user asks to "generate the design", "design the screens", "design the UX", "run the design stage", "load the use cases into design", "map the user flows", "review the user flow", "fix the navigation", "which features still need designing", or after /bigin-transform-signal has drafted or updated a UC. Turns every unprocessed (new or changed) UC-### plus the pain-point register and design directives into per-feature UX specs — actors, screens, states, real copy, the navigation shell, and the user flows that connect them — then runs a built-in flow review over those journeys and a forward coverage check proving nothing in the requirements went undesigned. It produces NO design system and NO tokens: colour, type, spacing, and components come from the design team or are bound at render time. It renders nothing — rendering is /bigin-render-design-od, invoked by a human, who can then run a perception-first-design (or similar) critique against the rendered artifact by hand if they want one.
argument-hint: "[feature slug | UC-### | omit for every feature that needs designing]"
disable-model-invocation: true
---

# Bigin Generate Design

The **load** step of the extract → transform → load pipeline, on the experience side. It takes use
cases that have **no current design** and produces what a prototype needs:

```text
in    UC-###  (new, or changed since it was last designed)
    + PAIN-POINTS.md / each hub's ## Pain Points    what the flows exist to FIX
    + DESIGN-PRINCIPLES.md rows + each hub's ## Design Directives
    + BR-### states  + EN-### fields
    + platform:               web | mobile | both, from _bigin/system/project.md (absent → web)

out   UX-### per feature      an Actor & Scope table + screen inventory + screen specs
                               + USER FLOWS, each naming the pain point it resolves
                               + ## 7 Relationship Model, on a feature that earns one
    + _ux/navigation-map.md   one vault-wide, append-only navigation shell — a web tree, a mobile
                               tab bar, or one file carrying both
    + a ### Flow Review        every journey walked as the actor, against the pain points, and
                               improved in place — the built-in walk, every run
    + a ### Coverage table     every requirement item AND every open pain point matched FORWARD to
                               the screen, state, or flow that carries it — the only check that
                               finds an OMISSION, and a render-readiness pass in the same sweep
```

**It produces no design system and no tokens.** No palette, no type scale, no spacing scale, no
component library. A screen element names a **semantic role** — `primary action`, `danger`, `muted` —
from a closed list of ten, and a real design system maps those ten once, later, when the design team
supplies one or `/bigin-render-design-od` binds one. A run that invented a palette designed the one
thing nobody asked it for and pinned the client's brand to it.

**It renders nothing.** Turning a spec into artifacts a client can look at is `/bigin-render-design-od`,
a separate skill a human invokes when they want a prototype (`design-platform.md` § Rendering is a separate step). Nothing
here checks for a design tool, and nothing here can halt for one.

This skill is the **procedure**. `{design_conventions}` is the **standard** — a rulebook kept
deliberately separate from the requirement one, because a rule about how a screen looks must never
end up deciding what the system does.

**It never edits a requirement.** UCs, BRs, entities, and the pain-point register are read-only here
(D4). The one exception is a single `## Discussion` line on a non-approved UC saying "screens exist
now" (Stage 6 Part 4).

**It is headless, with no halt at all.** No checkpoints, no confirmation prompts, no question put to a
human mid-run, and nothing that stops it before the work either. So it is unconditionally safe to call
from `/bigin-ba` or an unattended batch. Only a missing or ahead-of-plugin workspace stops it, as in
every skill here.

## Platform

**What is being built — a browser app, a phone app, or both.** It comes from `platform:` in
`_bigin/system/project.md`'s frontmatter, is read **once**, at Stage 1, by the orchestrator, and is
passed down to every later stage and every dispatched worker. A worker is *told* it and never
re-derives it: two workers inferring a platform differently produces one product with two navigation
shells. It changes the *shape* of a design without changing a single requirement — a UC stays
platform-blind, and platform never becomes a step, a branch, or a business rule (D4).

```text
platform: web | mobile | both     field absent → web   (the compatibility default)

drives    screen composition   one web form is legitimately three phone sheets — same steps,
                               more surfaces
          the nav shell        a sidebar/nav-bar tree (web) vs a TAB BAR of at most 5 (mobile);
                               on both, two ## Structure sections in one nav-map file
          regions vocabulary   web: header/nav/main/aside/footer · mobile: header/content/
                               tab-bar/sheet/fab — the wrong one asks a tool to build a shell
                               the platform does not have
          the render shell     what /bigin-render-design-od builds, LATER, if a human asks for a
                               prototype — never something this run needs installed

does NOT  the FLOWS. One flow per user goal, per actor — never one per platform. A phone splitting
drive     a web form into three sheets is the same journey on more surfaces, said inside the flow's
          own Path line, never as a second flow

per-feature override   ONLY a UC, a hub ## Design Directives row, or an active DESIGN-PRINCIPLES
                       row that EXPLICITLY STATES a platform for that feature, cited as its ground.
                       An inference from step wording, or from where an actor sits, is NOT an
                       override — design to the config value and raise an Open Question.
```

`design-platform.md` § Platform is the standard; this is the procedure.

## Actor scope

**Platform decides a design's shape; actor scope decides its machinery.** A UC is written
actor-neutral — "the actor views member information" reads the same whether that actor is one member
looking at their own record or an administrator working a directory of ten thousand. They are two
products, and a run that merges them on "same place" ships the member's screen to the administrator.

```text
three facts per actor, READ never assumed, filled into ## 1's Actor & Scope table before any screen
is mapped:
    sees whose records   own | assigned subset | their unit's | all
                         ground: a BR-### on visibility/permission, a UC ## 1 pre-condition
    how many             one | few | many (unbounded)
                         ground: an EN-### relationship cardinality, a BR-### cap, a UC step
    may act on           read one · act on one · act on MANY at once
                         ground: a UC step or a BR-###. NEVER the volume — D8

the band decides the machinery
    one    the record. NO find machinery — nothing to find
    few    the set, listed whole
    many   a find mechanism (search|filter|sort) + five volume states (empty · few · many AT REAL
           SCALE, with the number named · loading · error), grounded by the volume fact itself

the merge rule Part 2 applies becomes conditional
    volume band differs, or capability differs   → TWO screens, each naming its actor — and TWO
                                                   FLOWS, because the two actors are on two journeys
    both agree, only field visibility differs    → ONE screen + a `Visible to` cell citing the BR

D8, the data-side counterpart of D7: volume licenses FINDING, never a CAPABILITY. Bulk edit, bulk
delete, select-all-matching, export, a saved view — granted by a UC step or a BR-###, or a
REQUIREMENT GAP in ## 6, owner client. Never a control added because an admin would obviously want
it.
```

Nothing on record settles a cell → the **narrowest** reading plus an Open Question. Designing wide
and asking later means the client approves a reach nobody granted. And actor scope never invents an
actor: it reads the ones the UCs already name and asks three questions about each — a "power user"
nobody wrote down is a persona, and a screen for one is invented scope with an invented owner.

`design-actor-scope.md` § Actor scope is the standard; `3-screens.md` Part 2a is the procedure.

## User flows and pain points

**The flows are what this stage exists to get right.** A screen inventory says what exists; a flow
says how a real person gets from a trigger to an outcome — and it is the artifact a client either
recognises as their own working day or does not.

```text
ONE flow per user goal, per ACTOR — never one per platform, never one per screen
    Entry · Path · Success · Failures · Resolves (a PP-###, or "—") · Steps to goal (a number)

D6  a flow must RESOLVE SOMETHING STATED — a UC goal, or a PP-### it names.
    a journey that resolves neither is invented, and it is an Open Question, not a row.

every open PP-### on a feature's hub gets an ANSWER: a flow that names it, or a ## 6 question
saying why none does. Stage 5 matches every one forward and surfaces what was skipped.
```

**A pain point is ground 1b, and 1b alone grounds nothing.** `PP-004: "reviewers can never find what
they were working on yesterday"` legitimately puts in-progress items first, gives them `emphasis`,
pre-selects that filter, and argues for a shallower nav placement. It does **not** ground a "recent
activity" screen nobody's UC asked for — that is existence, it needs ground 1, and without it the
pain point becomes a question.

**The register is read-only.** A flow names the `PP-###`; it never fills a `Resolved by` cell, never
changes a status, and never adds a row. `/bigin-transform-signal` closes a pain point.

`design-navigation.md` § User flows and pain points is the standard; `3-screens.md` Part 4c is the
procedure.

## Semantic style roles — what replaced tokens

A screen spec says what an element is **for**, never what it looks like. One word, from a closed list
of ten, in the element table's `Role` cell — or blank, which most elements are:

```text
primary action · secondary action · destructive · danger · warning · success · info ·
emphasis · muted · (blank)

ALLOWED     `primary action` · `danger` · `muted`
FORBIDDEN   `#2563eb` · `16px` · `Inter Semibold` · `--color-action-primary` · `btn-primary`
            → all four are D2 broken. The first three pin a value nobody stated; the last two cite a
              system this vault does not have, so nothing resolves them and a renderer picks its own
```

**A role survives a design system it has never met.** "This is the primary action" stays true
whichever brand, palette, or component library gets bound later — which is exactly why it survives
where a token name would not. Exactly one `primary action` per screen; a screen needing an eleventh
role raises a question rather than inventing one nothing else in the vault can map.

## Operating modes

| Mode | Behaviour |
|---|---|
| **Bootstrap** | `04-UIUX/_ux/navigation-map.md` is absent. The first screens create it. |
| **Extend** (normal) | The navigation map exists. Load its tree, join it, **add** what is genuinely new. Never replace it. |
| **Design-only** | A feature with no UC but with open `## Design Directives` rows. Screens from the directives, empty `absorbed:`, no flows. |

**Platform is an orthogonal axis, not a fourth mode.** Every mode above runs on any platform, and
`both` is one run — not two — whose screens carry a layout split and whose nav map carries two trees.

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | the experience rulebook — paths, the eight hard rules, statuses, grounding, semantic roles, actor scope, flows and pain points, the flow review |
| `{design_stages_dir}` | `_bigin/stages/design/` | `1-scope`, `2-navigation`, `3-screens`, `4-flow-review`, `5-verify`, `6-close` |
| `{ux_dir}` | `04-UIUX/UX-<NNN> <Feature>.md` | one spec per feature |
| `{ux_system_dir}` | `04-UIUX/_ux/` | the vault-wide UX system — `navigation-map.md`. **Not** a design system: no colour, type, spacing, or components |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | `## Design Directives` and `## Pain Points` in, `## UX Spec` out |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | **read-only** input |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | **read-only** — what the flows exist to fix |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | **read-only** — client-stated preferences |
| `{template_*}` | `_bigin/templates/*` | `ux-spec`, `navigation-map` |

`design-core.md` § Paths is the full table, and the one a subagent reads — a `SKILL.md` lives
in the plugin install directory, which a subagent cannot reach.

**A design system, if this vault has one, is on no path table here.** Nothing in this skill reads
one, writes one, or requires one. A vault carrying a legacy `04-UIUX/_design-system/` keeps it,
unread, as a record of what earlier runs specced against.

Missing `_bigin/conventions/`, `_bigin/stages/design/`, or `_bigin/templates/` → stop and say
`/bigin-new-project` must run first.

Then run `version-check.md` § Workspace version check — one `Grep` of
`_bigin/system/project.md` against the installed plugin's version, compared as semver. Behind → warn and
recommend `/bigin-upgrade-project`; **ahead → stop**.

Then the platform — the one run-wide fact resolved before Stage 1 builds a work-list:

```text
Grep _bigin/system/project.md frontmatter for  platform: web | mobile | both
field absent  → web        (`design-platform.md` § Platform — the compatibility default)
```

## Rendering is a separate step

**Nothing here renders, so nothing here needs a renderer.** A run produces a specification — screens,
states, real copy, semantic roles, a nav shell, reviewed flows, and a coverage table.

```text
/bigin-render-design-od [feature slug | UX-###]     a HUMAN invokes it, when they want one

  the DESIGN SYSTEM is THEIR choice — this skill supplies none, which is precisely why that skill
  asks rather than defaults. DESIGN-PRINCIPLES still outranks whatever gets bound
  that skill halts when Open Design is unreachable. NOTHING HERE DOES
  it writes only the spec's ## 8 Rendered Artifacts (pointers) and its rendered: flag

  once a rendered artifact exists, a human MAY manually run a perception-first-design (or similar)
  critique skill against it — a real HTML/CSS artifact is what that kind of tool is built to
  evaluate, unlike the markdown spec this skill produces. Neither this skill nor
  /bigin-render-design-od invokes one automatically; it is a follow-up step a human reaches for,
  when they want it, on their own schedule
```

**Stage 5 is what guards against the failure a required-engine halt used to guard against** — a design
nobody can look at — by proving each spec is complete enough to render *cold*, on any engine, months
later. The visual system is the one thing it deliberately does not check for, because there is none.
`design-platform.md` § Rendering is a separate step carries the full reasoning.

## The optional method layer, and the built-in flow review

Two separate questions. Neither can halt anything, and neither reaches for an external critique
plugin any more.

```text
METHOD LAYER — how the screens get DERIVED. Optional; absence is a silent skip.
  check in order, first hit wins:
    1  BMAD WDS (Freya)   `_bmad/wds/` in the repo, or a wds-*-ux-design skill is available
    2  Figma MCP          a connected figma server
    3  any design plugin  a design/UX skill in this session's skill list
    4  built-in           always available — the method in the stage guides themselves

FLOW REVIEW (Stage 4) — whether the JOURNEYS get critiqued. UNCONDITIONAL, every run:
    the built-in walk (`4-flow-review.md` Parts 1-4) always runs, over every flow this run
    designed — no install to check, nothing to skip, no ### Flow Review table left unwritten.
[references/method-layer.md]
```

**A deeper, corpus-backed critique (perception-first-design or similar) is a human's call, made
later, against a rendered artifact — never something this run invokes.** Running one here, against a
markdown spec with no rendered surface, was always the wrong input for that kind of tool (§ Rendering
is a separate step); the built-in walk is what checks the journeys at spec time, and a human who wants
a second opinion runs a critique skill by hand once `/bigin-render-design-od` has produced something
to look at.

Detection, install commands, and how to hand work to a method layer:
**`references/method-layer.md`**. It also covers the optional per-step `designer-skills` pattern
references and the ground 2a/2b split that bounds every external pattern.

The agentic booster is the one with a real output surface: a feature that passes Stage 3's
**relationship trigger** gets a `## 7 Relationship Model` — the memory, autonomy, and trust the
requirements already imply, plus the gaps they never settled. See **`references/agentic-ux.md`**.

## Execution order

```text
scope = $ARGUMENTS slug or UC-###, else every {hub_dir} feature

1  scope     platform, then which UCs are NEW / CHANGED / CURRENT     [1-scope.md]
2  nav       seed the navigation shell, shaped by the pain points     [2-navigation.md § Part A]
3  screens   per feature: brief + actor scope → inventory → specs
             → FLOWS, each naming the pain point it resolves          [3-screens.md]
4  review    walk every journey as the actor; improve it in place     [4-flow-review.md]
             the built-in walk, unconditional, every run
5  verify    FORWARD coverage: every requirement item AND every open
             pain point → its screen, state, or flow                  [5-verify.md]
             + render readiness, so a later render cannot lack input
6  close     extend the nav map, stamp absorbed, set status, refresh
             hubs, 17 checks                    [2-navigation.md § Part B, 6-close.md]
```

Six stages, in order, every invocation, and **no precondition ahead of them**. **Load a stage file on
reaching that stage**, not up front.

The run ends at a verified specification. A prototype is `/bigin-render-design-od`, whenever a human wants
one.

## Stage 1 — Scope

**First, the one run-wide fact:** read `platform:` from `_bigin/system/project.md` (absent → `web`,
`design-platform.md` § Platform). **Announce it** in the Stage 1 output and again in the closeout, saying whether it was
stated or defaulted. Read once; every later stage and every worker is *told* the value.

```text
per feature: compare each UC's live version against the UX spec's absorbed: list
    not listed        → NEW       design it
    listed, older     → CHANGED   redesign its screens
    listed, same      → CURRENT   skip, and SAY SO
```

`absorbed:` is the whole staleness mechanism — `sources:` can never go stale, so it can never answer
"is this design still current?". Four gates then drop what cannot be designed: no main flow, a
summary-level UC, a UC owned by another feature, a removed UC.

A `needs-clarification` UC is **in** scope. Its open questions become known gaps in the brief.

**Mode is keyed on the navigation map**, not on a design system: `{nav_map_file}` absent → bootstrap,
present → extend. A run that looks for `_design-system/` reads a vault shape this plugin no longer
produces and reports `bootstrap` forever.

Count each feature's **unresolved pain points** and put the count on its work-list line. A count only
— the statements are Stage 2's and Stage 3's input, and reading them here spends the context the
fan-out exists to protect.

## Stage 2 — The navigation map (Part A)

Bootstrap it, or load it. It is the menu/navigation system for the product, and **the shape it takes
is the platform's**: seed its `## Structure` from whatever tree already exists — a dot-path `id` per
row, so it nests to whatever depth the real IA needs, not a fixed two levels.

```text
web     ## Structure              a sidebar / nav-bar shell, arbitrary depth
mobile  ## Structure              a TAB BAR — at most 5 top-level entries — plus per-screen headers
                                  and sheets. Depth below a tab is still arbitrary.
both    ## Structure — Web        BOTH sections, in ONE file, mapping the same feature set onto
        ## Structure — Mobile     each shell. An `id` is unique within its own section, so the same
                                  feature is `settings.team` on web and `more.team` on mobile.
```

Then read each in-scope feature's **open pain points** — the statements this time. A pain point is a
navigation fact before it is a screen fact: "reviewers can never find what they were working on
yesterday" says something must be reachable in one move, and the tree either allows that or it does
not. It may argue for placement, depth, and sibling order; it may **never** mint an entry pointing at
a screen no UC asked for (ground 1b).

**Do not pre-build a menu tree.** Part B adds what real screens actually turn out to need. A 6th
top-level mobile candidate is not a nav decision — it is an Open Question on the nav map (owner:
team), never a silent sixth row.

## Stage 3 — Screens and flows

```text
FAN OUT ONE WORKER PER FEATURE SLUG                    [references/agent-dispatch.md]
    → a feature's UX spec + hub are one ownership domain
    → features are independent and parallelize safely
    → one or two features: run it inline, dispatch costs more than the work

a worker NEVER writes:  {nav_map_file} · another feature's UX spec or hub · DESIGN-PRINCIPLES.md
                        · PAIN-POINTS.md or a hub's ## Pain Points · any UC, BR, or entity
                        · FEATURES.md
    → it REPORTS nav candidates, questions, designed UCs, unresolved pain points
a worker DOES write:    its own feature's UX spec (created from a number the orchestrator minted)
a worker is TOLD:       the PLATFORM and the method layer — it resolves neither, and cannot: a
                        subagent cannot read this plugin's install directory. It resolves no RENDER
                        engine at all — there is none in this run
```

**Every worker prompt carries `PLATFORM:`** — the resolved value, where it came from, and that
platform's regions vocabulary. A worker writes it into its `## 1 Design Brief` verbatim; the only
thing it may resolve itself is a **per-feature override**, and only from a source that explicitly
states one.

**A feature with 3+ in-scope UCs, or 4+ distinct cited entities, gets a `ux-brief-assembler`
dispatch first** (`agents/ux-brief-assembler.md`) — it combines that feature's UCs, the `EN-###`
entities they cite, `BR-###` mirrors, open hub directives, **open pain points**, and active design
principles into one Design Brief, so the screens worker starts from a pre-digested bundle. It never
decides a final screen boundary, a role, a state, a flow, or the Part 4b relationship verdict.

**The Actor & Scope table is filled before a single screen is mapped** (`3-screens.md` Part 2a). It
is the input to the merge rule, not a summary written afterwards.

The mapping that matters: **a run of consecutive steps by the same actor in the same place is one
screen**; a validation is a state, not a screen; an exception flow is a named error state. **Two UCs
landing on the same place merge only when their actors' scope agrees.** A `many` screen carries a find
mechanism and its five volume states with the real number named; a `one` screen carries neither. A
3–9 step UC normally yields 1–4 screens on `web`, and 2–6 on `mobile`; the bands are **per actor**.

**Then the flows** (Part 4c), which is where the journey gets written down rather than inferred: one
per user goal per actor, each with its `Resolves` and its `Steps to goal`, and every open pain point
on the hub either named by a flow or turned into a question.

**Never invent a screen, a field, a state, or a journey.** Every one traces to a UC step, a BR, an
entity field, an existing screen pattern, or a stated preference — a pain point shapes but never
creates (D6, ground 1b). Grounded in none of those → an Open Question (D3), and if the answer would
change what the system *does*, it is flagged as a requirement gap for `/bigin-transform-signal`.

**Part 4b — the relationship model, on the few features that earn one.** Three mechanical tests: the
system *judges* rather than processes, an `EN-###` field *persists* something per-user between
sessions, and the trigger *repeats* for the same actor. Three of three → `## 7`; any miss → the
section is deleted, not left empty. A real agent feature yields **more requirement gaps than rows**
here, and that is the section working (D7).

## Stage 4 — Flow review

`4-flow-review.md`, in the orchestrator, after every worker has reported. **It runs every time, on
the built-in walk** — no skill to detect, nothing to skip.

It is the only stage that looks at the product **the way a user meets it**. Five questions per flow —
does it arrive, is every step earned, can the actor get back, does it start where they are, and
**does it actually fix the pain point it names** — plus one pass over the whole navigation shell as a
stranger would meet it.

```text
MAY CHANGE, in place    a flow's screen order · which screen an interaction leads to · a nav entry's
                        placement or nesting · a screen's element order · misleading copy · a state
                        a flow plainly reaches that something already grounds
MAY ONLY ASK (## 6)     a screen that should exist and does not · a capability nothing grants · a
                        pain point the flows cannot fix as the requirements stand
```

A re-nest is still append-only (D1): the new row is added, the old `id` is retired in the nav map's
§ Removing an entry, and every spec citing the old path is updated. An `id` edited in place silently
un-points every screen that cited it.

Question 5 is the one this stage exists for. The other four are hygiene a careful reader would catch;
question 5 is the one nobody catches, because a flow that delivers every UC step reads as complete
whether or not it makes the client's day better.

## Stage 5 — Verify: coverage and render readiness

`5-verify.md`, in the orchestrator, after the flow review (or its skip). It runs the one direction
nothing else in this pipeline runs: **forward**, from each requirement item to what carries it.

```text
every non-removed S# / A# / E# of every in-scope UC        →  the screen AND STATE that carries it
every BR-### they cite that constrains what an actor
  sees or may do                                           →  the state, validation, or Visible to
every EN-### field their steps read or write                →  the element that renders it
every UNRESOLVED hub PP-###                                 →  the FLOW that resolves it, and where
every open hub ## Design Directives row                     →  the screen that implements it
every active DESIGN-PRINCIPLES row                          →  where it applied
```

**Grounding, the flow review, and Stage 6's checks cannot find an omission**, which is why this stage
exists. Grounding runs backward — every element back to what licensed it — and a screen never drawn
has no element to trace. The flow review runs sideways — journey quality — and a journey nobody wrote
gets no verdict. Only forward proves nothing was dropped.

**A pain point matches only on an explicit `Resolves` cell.** Never by resemblance: a flow that looks
like it would help and does not name the id is a hope, not coverage — and a pain point is the item
everybody assumes somebody else handled.

Three verdicts land in a `### Coverage` table under `## 4 Flows`, re-written whole every run:
`covered` (naming the screen **and** the state — or, for a `PP-###`, the flow and where in it),
`gap → ## 6 Q<n>`, or `out of scope — <cited reason>`. An uncited exclusion is a gap wearing a
decision's clothes.

**It repairs, it does not design.** A row that under-recorded coverage a screen really has gets fixed;
a screen, state, or control that does not exist gets a `## 6` question and waits for the next Stage 3.

**Part 5 is render readiness.** A render may happen months from now, on a tool nobody has picked: this
platform's regions, real copy and real field names, every state named, every role from the closed
list, a resolvable nav shell, a `many` screen's real scale in words, a phone screen's device facts,
every flow's `Path` naming screens that exist. **The visual system is deliberately not on that list** —
there is none, and raising it as a gap puts a permanent unanswerable question on every spec.

## Stage 6 — Close

Extend the navigation map first (`2-navigation.md` Part B): dedup, reuse before adding, mint ids
top-down, respect the five-tab cap, bump the version, changelog it. **Nothing is ever deleted or
renamed in place** (D1).

Then stamp `absorbed:` with `UC-###@version` for **only the UCs that really got a screen row this
run**, re-stamped whole. Set each status from a live count of unchecked questions on disk. Refresh
every hub named in `features:`, naming each `PP-###` a flow now resolves — **and never filling that
row's `Resolved by` cell**, which is the requirement side's.

Then `6-close.md` Part 5's verification checks — **seventeen** today, every one blocking on mismatch.
Check 3 is the role list; check 4 bans a raw value *and* a `--token` id; check 7 is that no
`## Prototype Prompt` heading survives in a spec this run touched; check 17 is Stage 5's coverage
table **and** Stage 4's flow-review table together, including that an empty flow-review table fails
either way.

```text
mode · platform (+ any per-feature override) · method layer
actors per feature (scope + volume band) · actor splits · capability gaps raised
per-feature screens and flows · pain points resolved by a flow / still unresolved
flow review: N sound / N improved / N gaps · nav entries re-nested
coverage per feature: N checked / N covered / N gaps / N out of scope · render-ready y|n
nav entries added (0 deleted, 0 renamed) · directives reflected · skipped
relationship: modelled|none per feature (+ gaps raised) · skipped
design system: NONE PRODUCED, by design — never reported as a gap
pending · questions (design | REQUIREMENT GAP)
next: human review → /bigin-render-design-od when they want a prototype (their design system, their
      timing)
```

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Skipping or rushing Stage 5's forward pass.** It is the only thing in this skill that can find an
  omission. Every other check runs backward or sideways and passes cleanly on a spec missing a whole
  exception flow. A design reviewed as complete with a third of the flow absent is the most expensive
  clean-looking failure this pipeline produces.
- **Leaving `### Flow Review` empty, or not writing it, when flows exist.** The built-in walk runs
  every time, over every flow this run designed — an empty table, or none at all, reads as "reviewed,
  nothing found" when the pass never actually happened.
- **Giving a flow `sound` without finding the moment its pain point is fixed.** A journey that
  delivers every UC step and touches nothing the client complained about is exactly the design that
  reviews well and disappoints in the room.
- **Leaving an open pain point unanswered.** Every one gets a flow that names it or a question saying
  why none does. Silence reads as "considered and fine" — and it was never considered.
- **Letting a pain point ground a screen.** Ground 1b shapes ordering, emphasis, and defaults on a
  screen a UC already asked for. A "recent activity" panel grounded only in `PP-004` is an invented
  screen carrying a citation, which reviews as designed where a bare guess would have been caught.
- **Marking a pain point resolved.** The register is the requirement side's. Name the id; let
  `/bigin-transform-signal` close the row. Closing it here means a pain point reads as settled on the
  strength of a design nobody has accepted yet.
- **Writing a `--token` id, a hex, a px, or a font name into a spec.** All four are D2 broken, and the
  token id is worst: it cites a design system this vault does not have, so it resolves to nothing and
  a render engine quietly picks its own value while the spec looks specified.
- **Inventing an eleventh semantic role.** The ten are closed precisely so one mapping covers the
  vault. A private role is a one-screen vocabulary nothing downstream can resolve.
- **Reintroducing a design system, a token file, or a palette.** It is the one thing this stage was
  changed to stop producing. An invented palette pins the client's brand to a colour nobody chose,
  and every screen built against it has to be redone the day the real system arrives.
- **Reporting the absent design system as a gap.** There is none by design. A `design system: missing`
  line teaches every reader that something went wrong in a run that did exactly what it should.
- **Leaving a `## Prototype Prompt` block in a spec.** It inlines token values that no longer exist
  and describes screens that may since have changed. A BA who pastes it in good faith prototypes a
  design nobody is maintaining.
- **Ticking a render-readiness box by inventing the input.** Placeholder copy, a guessed scale, a
  state nobody specified: all three pass, and all three reach the client inside a rendered prototype
  that looks specified. The render happens later, from a context that is gone.
- **Turning a coverage gap into an out-of-scope line with no citation.** It reads as a decision
  somebody made, and the exclusion outlives everyone who could contradict it.
- **Designing the missing screen inside Stage 4 or Stage 5.** The pass then has no independent verdict
  left: it drew the thing it was checking for.
- **Editing a nav entry's `id` in place to re-nest it.** Every screen spec citing the old path now
  points at nothing, and D1's record of why the IA looks the way it does is gone.
- **Shortening a flow the requirements made long.** A five-step approval a BR requires is five steps.
  Cutting one is a design deciding what the system does, and the step reappears in the build after
  the client approved a journey without it.
- **Writing two flows for one goal on `both`.** The phone splitting a form into sheets is the same
  journey on more surfaces — one flow, the split inside its `Path`.
- **Stamping `absorbed:` for a UC that got no screen.** The feature reads as designed forever.
- **Designing one screen for two actors whose work is not the same work.** A member reading their own
  record and an administrator working ten thousand land on "the same place", and whichever actor the
  prototype renders for, the other got a product that does not fit their job.
- **A `many` screen with no find machinery, or a `many` state seeded with three rows.** Both review as
  finished, because every element on them is properly grounded, and both collapse the first time the
  screen meets the client's real table.
- **Adding bulk delete or export because an administrator would obviously need it.** D8. Plausible,
  unstated, and it reaches the client in a working prototype that they approve — except this one
  deletes five hundred records at a time.
- **Designing a mobile product with the web regions vocabulary.** A `nav` region on a phone screen
  asks the render tool to build a shell the platform does not have.
- **Writing a design decision into a UC.** It bypasses the requirement review gate entirely.
- **Minting a second UX spec for a feature that has one.** The review splits and both go stale.
- **Giving every screen a nav entry.** A detail screen opened from a list is not a menu item.
- **Flipping a directive to `reflected` because it was read.** It is reflected when a screen
  implements it.
- **Letting an external pattern catalog ground a screen.** Ground 2a is a pattern *in this vault*; 2b
  is one from an installed skill, and 2b alone grounds nothing.
- **A relationship model over nothing stored.** No `EN-###` field means the system cannot remember it,
  so the row is a requirement gap. Leaving `## 7` in place and empty is the same failure inverted.
- **Setting status early.** Count the open questions from disk, last, every time.
- **Reporting a render.** Nothing here renders. A closeout line saying a render was done, skipped, or
  waived describes a step that was never part of the run.

## Model

Per-feature workers run on the **session default model**, not `haiku`. Deciding how many screens a
flow needs, which state belongs to which rule, and whether a journey actually resolves a pain point is
judgment work — the same reason `/bigin-transform-signal` fans out on the default model.

## Additional resources

- **`references/method-layer.md`** — the **optional** method layer that Stage 3 screens are derived
  through. None of it can halt anything: the provider table, how to detect each one, the install
  command to report when none is present, how the built-in method works, the per-step
  `designer-skills` pattern references, and the ground 2a/2b split that bounds them. Read at Stage 1
  by the orchestrator; the per-step section is read again by each worker at Stage 3. Stage 4's flow
  review is unconditional and built-in — it is not part of this method layer, and calls no external
  critique skill.
- **`references/agentic-ux.md`** — the relationship model: what the agentic booster does and does not
  contribute, how the trigger is decided (and why Stage 1 cannot decide it), the five pillars mapped
  onto `## 7` and `## 3`, a worked example, and the five recurring requirement gaps. Read at Stage 1,
  by the orchestrator, when the skill is installed. A worker reads `3-screens.md` Part 4b instead.
- **`references/agent-dispatch.md`** — the per-feature worker prompt, its report contract, and the
  wave-verification checklist. Read at Stage 3, before fanning out. It also names the dispatch
  threshold for `agents/ux-brief-assembler.md`.
- **`agents/ux-brief-assembler.md`** (plugin-root `agents/`, not this skill's `references/`) — the
  named subagent dispatched per qualifying feature at Stage 3, ahead of the screens worker. It never
  writes a file and never finalizes a screen boundary; it only assembles.
- **`/bigin-render-design-od`'s `references/open-design-adapter.md`** — where the Open Design tool
  contract, the design-system choice, and the halt text live. **This skill never reads it**, and that
  is the point: a design run has no engine and no design system to resolve.
