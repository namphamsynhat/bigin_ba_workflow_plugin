---
name: bigin-generate-design
description: This skill should be used when the user asks to "generate the design", "design the screens", "run the design stage", "load the use cases into design", "make a prototype prompt", "give me a Claude design prompt", "give me a Figma Make prompt", "update the design system", "which features still need designing", or after /bigin-transform-signal has drafted or updated a UC. Turns every unprocessed (new or changed) UC-### plus the design principles and directives into per-feature screen specs, a durable vault-wide design system, a forward coverage check proving nothing in the requirements went undesigned, and the self-contained prototype prompt blocks its platform calls for. It renders nothing and needs no design tool installed — rendering a prototype is /bigin-render-design, invoked by a human on the engine they choose.
argument-hint: "[feature slug | UC-### | omit for every feature that needs designing]"
disable-model-invocation: true
---

# Bigin Generate Design

The **load** step of the extract → transform → load pipeline, on the design side. It takes use cases
that have **no current design** and produces what a prototype needs:

```text
in    UC-###  (new, or changed since it was last designed)
    + DESIGN-PRINCIPLES.md rows + each hub's ## Design Directives
    + BR-### states  + EN-### fields
    + platform:               web | mobile | both, from _bigin/system/project.md (absent → web)

out   UX-### per feature      an Actor & Scope table + screen inventory + screen specs + flows
                               + ## 7 Relationship Model, on a feature that earns one
    + _design-system/         one vault-wide, append-only token/component system
                               + navigation-map.md — the shell this platform has: a web tree, a
                                 mobile tab bar, or one file carrying both
    + a ### Coverage table    every requirement item matched FORWARD to the screen and state that
                               carries it, or to a written gap — the only check that finds an
                               OMISSION, and a render-readiness pass in the same sweep
    + 2 or 4 prompt blocks    Claude design + Figma Make, per platform — two on web or mobile,
                               all four on both, each self-contained
```

**It renders nothing.** Turning a spec into artifacts a client can look at is `/bigin-render-design`,
a separate skill a human invokes when they want a prototype, on the engine they choose (§ Rendering is
a separate step). Nothing here checks for a design tool, and nothing here can halt for one.

This skill is the **procedure**. `{design_conventions}` is the **standard** — a rulebook kept
deliberately separate from the requirement one, because a rule about how a screen looks must never
end up deciding what the system does.

**It never edits a requirement.** UCs, BRs, and entities are read-only here (D4). The one exception
is a single `## Discussion` line on a non-approved UC saying "screens exist now" (Stage 6 Part 4).

**It is headless, with no halt at all.** No checkpoints, no confirmation prompts, no question put to a
human mid-run, and nothing that stops it before the work either — the required-engine precondition it
used to carry moved to `/bigin-render-design`. So it is unconditionally safe to call from `/bigin-ba` or
an unattended batch. Only a missing or ahead-of-plugin workspace stops it, as in every skill here.

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
          prompt-block count   2 blocks on web or mobile, 4 on both
          the render default   which engine /bigin-render-design offers first, LATER, if a human
                               asks for a prototype — never something this run needs installed

per-feature override   ONLY a UC, a hub ## Design Directives row, or an active DESIGN-PRINCIPLES
                       row that EXPLICITLY STATES a platform for that feature, cited as its ground.
                       An inference from step wording, or from where an actor sits, is NOT an
                       override — design to the config value and raise an Open Question.
```

`{design_conventions}` § Platform is the standard; this is the procedure.

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
    volume band differs, or capability differs   → TWO screens, each naming its actor
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

`{design_conventions}` § Actor scope is the standard; `3-screens.md` Part 2a is the procedure.

## Operating modes

| Mode | Behaviour |
|---|---|
| **Bootstrap** | `04-UIUX/_design-system/design-tokens.md` is absent. The first screens create it. |
| **Extend** (normal) | The design system exists. Load it, reuse it, **add** what is genuinely new. Never replace it. |
| **Design-only** | A feature with no UC but with open `## Design Directives` rows. Screens from the directives, empty `absorbed:`, no flows. |

**Platform is an orthogonal axis, not a fourth mode.** Every mode above runs on any platform, and
`both` is one run — not two — whose screens carry a layout split and whose spec carries four prompt
blocks.

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | the design rulebook — paths, the eight hard rules, statuses, grounding, actor scope, the relationship model |
| `{design_stages_dir}` | `_bigin/stages/design/` | `1-scope`, `2-system`, `3-screens`, `4-verify`, `5-prompt`, `6-close` |
| `{ux_dir}` | `04-UIUX/UX-<NNN> <Feature>.md` | one spec per feature |
| `{design_system_dir}` | `04-UIUX/_design-system/` | `design-tokens.md` + `components/<component>.md` + `navigation-map.md` |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | `## Design Directives` in, `## UX Spec` out |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | **read-only** input |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | **read-only** — client-stated preferences |
| `{template_*}` | `_bigin/templates/*` | `ux-spec`, `design-system`, `design-component`, `navigation-map` |

`{design_conventions}` § Paths is the full table, and the one a subagent reads — a `SKILL.md` lives
in the plugin install directory, which a subagent cannot reach.

Missing `_bigin/conventions/`, `_bigin/stages/design/`, or `_bigin/templates/` → stop and say
`/bigin-new-project` must run first.

Then run `_bigin/conventions/conventions.md` § Workspace version check — one `Grep` of
`_bigin/system/project.md` against the installed plugin's version, compared as semver. Behind → warn and
recommend `/bigin-upgrade-project`; **ahead → stop**.

Then the platform — the one run-wide fact resolved before Stage 1 builds a work-list, and the only
thing resolved up front now that there is no engine to check:

```text
Grep _bigin/system/project.md frontmatter for  platform: web | mobile | both
field absent  → web        (§ Platform — the compatibility default)
```

## Rendering is a separate step

**Nothing here renders, so nothing here needs a renderer.** A run produces a specification — screens,
states, real copy, tokens, a nav shell, a coverage table, and the self-contained prompt blocks.

```text
/bigin-render-design [engine] [feature slug | UX-###]     a HUMAN invokes it, when they want one

  the ENGINE is THEIR choice — the platform supplies a default and nothing more
  that skill halts when the chosen engine is absent, with the install command. NOTHING HERE DOES
  it writes only the spec's ## 8 Rendered Artifacts (pointers) and its rendered: flag
```

The halt this replaced used to sit at the front of *this* skill, stopping a stage that reads use cases
and writes markdown because a prototype renderer was missing. **Stage 4 is what guards against the
failure that halt existed for** — a design nobody can look at — by proving each spec is complete enough
to render *cold*, on any engine, months later. `{design_conventions}` § Rendering is a separate step
carries the full reasoning.

## The optional method layer — and it can halt nothing

Separate question, and the only engine-shaped question left in this skill. It changes **how** screens
get derived and how good they read; it renders nothing, and its absence never gates a run.

```text
check in order, first hit wins:
  1  BMAD WDS (Freya)   `_bmad/wds/` in the repo, or a wds-*-ux-design skill is available
  2  Figma MCP          a connected figma server (its tools can read a real design system)
  3  any design plugin  a design/UX skill in this session's skill list
  4  built-in           always available — the method in the stage guides themselves
  none of 1-3 → run the built-in method and REPORT the install command in the closeout.
                Never halt: the built-in method is complete.
[references/engine-detection.md]
```

It **composes across the two skills**: the method layer here decided *what the screens are*, and an
engine in `/bigin-render-design` renders them, possibly weeks later. Neither substitutes for the other.

Detection of the method layer, its install commands, and how to hand work to it:
**`references/engine-detection.md`**, which also covers optional **quality boosters** layered on top
of whichever method is chosen — an agentic-relationship-UX skill for features that are genuinely
about an ongoing AI-agent relationship, a design-library skill for a non-generic starting palette on
bootstrap, per-step `designer-skills` pattern references for
STRUCTURE/ELEMENTS/TOKENS/STATES/NAVIGATION, and an optional Stage 3.5
craft-quality pass — Perception-First Design's checklist mode (Mode 1 only, never its solve or
analyze modes) when installed, or a generic heuristic-evaluation/accessibility-audit/critique-*
skill otherwise — a worker runs on its own drafted screens before reporting. None of them replaces
the built-in method; all are read only when they actually apply, and a missing
one is a **silent skip**, never a halt. Nothing in this list, and nothing in this skill, can stop a
run.

The agentic booster is the one with a real output surface: a feature that passes Stage 3's
**relationship trigger** gets a `## 7 Relationship Model` — the memory, autonomy, and trust the
requirements already imply, plus the gaps they never settled. See **`references/agentic-ux.md`**.

## Execution order

```text
scope = $ARGUMENTS slug or UC-###, else every {hub_dir} feature

1  scope     platform, then which UCs are NEW / CHANGED / CURRENT     [1-scope.md]
2  system    seed the design system so screens can cite token names   [2-system.md § Part A]
3  screens   per feature: brief + actor scope → inventory → specs     [3-screens.md]
4  verify    FORWARD coverage: every requirement item → its screen    [4-verify.md]
             + render readiness, so a later render cannot lack input
5  prompt    fold in new tokens, write 2 or 4 blocks                  [2-system.md § Part B, 5-prompt.md]
6  close     stamp absorbed, set status, refresh hubs, 18 checks       [6-close.md]
```

Six stages, in order, every invocation, and **no precondition ahead of them any more** — there is no
engine to check. **Load a stage file on reaching that stage**, not up front.

The run ends at a verified specification. A prototype is `/bigin-render-design`, whenever a human wants
one (§ Rendering is a separate step).

## Stage 1 — Scope

**First, the one run-wide fact:** read `platform:` from `_bigin/system/project.md` (absent → `web`,
§ Platform). **Announce it** in the Stage 1 output and again in the closeout, saying whether it was
stated or defaulted. Read once; every later stage and every worker is *told* the value and never
re-reads the project config.

There is **nothing else to check, and nothing that can stop the run.** The engine precondition that
used to sit beside this read now belongs to `/bigin-render-design`, so a missing prototype tool can no
longer halt a stage that does not use one.

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

## Stage 2 — Design system and navigation map (Part A)

Bootstrap it, or load it. Fill `## Foundations` from `{design_principles_file}`'s `active` rows, then
make sure the Level-2 semantic tokens the screens will need exist **by name**. Screens cite names,
so the names come first.

Do the same for `{nav_map_file}` — bootstrap or load it alongside the tokens (D3, § The navigation
map). It is the menu/navigation system for the product, and **the shape it takes is the platform's**:
seed its `## Structure` from whatever tree already exists — a dot-path `id` per row, so it nests to
whatever depth the real IA needs, not a fixed two levels. Part B is where screens add the entries a
real flow actually needs.

```text
web     ## Structure              a sidebar / nav-bar shell, arbitrary depth
mobile  ## Structure              a TAB BAR — at most 5 top-level entries — plus per-screen headers
                                  and sheets. Depth below a tab is still arbitrary.
both    ## Structure — Web        BOTH sections, in ONE file, mapping the same feature set onto
        ## Structure — Mobile     each shell. An `id` is unique within its own section, so the same
                                  feature is `settings.team` on web and `more.team` on mobile.
```

A 6th top-level mobile candidate is not a nav decision — it is an Open Question on the nav map
(owner: team), never a silent sixth row.

Do not pre-build a palette, and do not pre-build a full menu tree. Part B adds what real screens
actually turn out to need.

## Stage 3 — Screens

```text
FAN OUT ONE WORKER PER FEATURE SLUG                    [references/agent-dispatch.md]
    → a feature's UX spec + hub are one ownership domain
    → features are independent and parallelize safely
    → one or two features: run it inline, dispatch costs more than the work

a worker NEVER writes:  {design_system_dir} (incl. {nav_map_file}) · another feature's UX spec or hub
                        DESIGN-PRINCIPLES.md · any UC, BR, or entity · FEATURES.md
    → it REPORTS token candidates, component candidates, nav candidates, questions, designed UCs
a worker DOES write:    its own feature's UX spec (created from a number the orchestrator minted)
a worker is TOLD:       the PLATFORM and the method layer — it resolves neither, and cannot: a
                        subagent cannot read this plugin's install directory, and two workers
                        inferring a platform differently produce one product with two navigation
                        shells. It resolves no RENDER engine at all — there is none in this run
```

**Every worker prompt carries `PLATFORM:`** — the resolved value, where it came from, and that
platform's regions vocabulary (`agent-dispatch.md` § The prompt). A worker writes it into its
`## 1 Design Brief` verbatim; the only thing it may resolve itself is a **per-feature override**, and
only from a source that explicitly states one (§ Platform).

**A feature with 3+ in-scope UCs, or 4+ distinct cited entities, gets a `ux-brief-assembler`
dispatch first** (`agents/ux-brief-assembler.md`) — it combines that feature's UCs and the `EN-###`
entities they cite (plus `BR-###` mirrors, open hub directives, active design principles) into one
Design Brief — platform included, supplied to it the same way, never inferred — so the screens
worker starts from a pre-digested bundle instead of re-reading everything raw. It never decides a
final screen boundary, a token, a state, or the Part 4b relationship verdict — every one of those
stays the screens worker's call. Below that threshold, skip it; the worker reads `3-screens.md`
Part 1 directly.

**The Actor & Scope table is filled before a single screen is mapped** (`3-screens.md` Part 2a). It
is the input to the merge rule, not a summary written afterwards — and it is what makes the run
design for the actors a feature actually has instead of one screen fitting all of them.

The mapping that matters: **a run of consecutive steps by the same actor in the same place is one
screen**; a validation is a state, not a screen; an exception flow is a named error state. **Two UCs
landing on the same place merge only when their actors' scope agrees** — a differing volume band or
capability produces two screens, each naming its actor; differing field visibility alone stays one
screen with a `Visible to` cell. A `many` screen carries a find mechanism and its five volume states
with the real number named; a `one` screen carries neither. The screen-count bands below are **per
actor**: a feature genuinely serving two scopes lands at twice the count, and that is right. A 3–9 step
UC normally yields 1–4 screens on `web`, and 2–6 on `mobile` — the phone splits (one primary action
per screen, a long form into stepped sheets, list and detail as two screens) legitimately produce
more, smaller screens for the same steps. `both` is judged on the web band: the inventory is the
shared goal set, and a mobile layout split lives inside a row rather than adding one.

**Never invent a screen, a field, or a state.** Every one traces to a UC step, a BR, an entity field,
an existing screen pattern, or a stated preference. Grounded in none of those → an Open Question
(D3), and if the answer would change what the system *does*, it is flagged as a requirement gap for
`/bigin-transform-signal` — never written onto the UC here.

**Part 4b — the relationship model, on the few features that earn one.** Three mechanical tests: the
system *judges* rather than processes, an `EN-###` field *persists* something per-user between
sessions, and the trigger *repeats* for the same actor. Three of three → `## 7`; any miss → the
section is deleted, not left empty. It is the only home for a **trust stage**, which is longitudinal
(the same screen at relationship month 1 versus month 12) where `## 3`'s States are within-session.
A real agent feature yields **more requirement gaps than rows** here — retention, visibility, and
disclosure are almost never stated — and that is the section working (D7).

## Stage 4 — Verify: coverage and render readiness

`4-verify.md`, in the orchestrator, after every worker has reported and **before** a single prompt block
is written. It runs the one direction nothing else in this pipeline runs: **forward**, from each
requirement item to the screen and state that carries it.

```text
every non-removed S# / A# / E# of every in-scope UC        →  the screen AND STATE that carries it
every BR-### they cite that constrains what an actor
  sees or may do                                           →  the state, validation, or Visible to
every EN-### field their steps read or write                →  the element that renders it
every open hub ## Design Directives row                     →  the screen that implements it
every active DESIGN-PRINCIPLES row                          →  where it applied
```

**Grounding and Stage 6's checks cannot find an omission**, which is the whole reason this stage exists.
They run backward — every element back to the thing that licensed it — and a screen that was never drawn
has no element to trace. A spec passes all eighteen checks with an entire exception flow missing: nothing
on it was invented, because nothing on it was drawn.

Three verdicts land in a `### Coverage` table under `## 4 Flows`, re-written whole every run: `covered`
(naming the screen **and** the state), `gap → ## 6 Q<n>`, or `out of scope — <cited reason>`. An uncited
exclusion is a gap wearing a decision's clothes.

**It repairs, it does not design.** A row that under-recorded coverage a screen really has gets fixed; a
screen, state, or control that does not exist gets a `## 6` question and waits for the next Stage 3 (D3).
A pass that draws the thing it was checking for has no verdict left to give.

**Part 5 is render readiness.** A render may happen months from now, on a tool nobody has picked, run by
someone who never reads the requirements — so the spec must be sufficient input *now*: this platform's
regions, real copy and real field names, every state named, every token carrying a value, a resolvable
nav shell, a `many` screen's real scale in words, a phone screen's device facts, concrete memory rows
whenever `relationship_model: modelled`. A box that cannot be ticked from the record is a question, never
a plausible fill.

## Stage 5 — Extend the system, write the prompt blocks

Part B of `2-system.md` applies the reported candidates one at a time, in the orchestrator: dedup
first, reuse before adding, add only what is genuinely new, bump the version, changelog it. **Nothing
is ever deleted or renamed** (D1) — a screen specced last month cites that name. The same pass adds
any reported nav entries to `{nav_map_file}` — one row per screen a worker flagged as directly
menu-reachable, never one for a screen reached only through another screen.

Then the prompt blocks — **two per platform**, from the same screens and the now-final token values:
`web` or `mobile` gets Claude design + Figma Make for that platform, `both` gets all four, each
heading carrying its platform. Same screens, same states, same copy in every block; the only things
that may differ are the tool addressed and the shell/viewport. Every vault id is expanded into words
before it goes in (D6): a prompt with `UC-012 S4` in it renders that string as a heading in the
prototype.

**The blocks are written every run, unconditionally, and the run ends there.** Nobody may ever render
this feature, or they may render it in six months on a tool that does not exist today — the block is what
survives that. `5-prompt.md` Part 5 is the handoff: what the block owes `/bigin-render-design`.

## Stage 6 — Close

Stamp `absorbed:` with `UC-###@version` for **only the UCs that really got a screen row this run**,
re-stamped whole. Set each status from a live count of unchecked questions on disk. Refresh every
hub named in `features:` — `## UX Spec`, `uiux:`, directives that a screen really implements flipped
to `reflected`, questions mirrored. Then `6-close.md` Part 5's verification checks — eighteen today,
every one blocking on mismatch. Check 18 is Stage 4's: the `### Coverage` table exists, is whole, and
every `gap` row points at a question that really exists. The last three read `## 7` from disk: the `relationship_model:` flag
must match the section that is really there, every memory row must name a field that really exists,
and every gap the section found must have become a `## 6` question.

**Actor scope is verified too** — checks 15–17, read from disk: every Actor & Scope row names an
actor a UC really has and grounds all three cells; every `many` screen really carries a find
mechanism and all five volume states with the real number named, and no `one` screen carries find
machinery; and no bulk action, export, or saved view sits on a screen without a UC step or BR-###
granting it, with every one left out recorded as a requirement gap.

**Platform is verified, not assumed** — checks 13–14, read from disk like the rest: the spec's
`platform:` and its `## 1` **Platform** line hold the same value, and it is the config's (or a
per-feature override citing the source that *explicitly stated* it); and every screen spec's regions
use that platform's vocabulary, with each `Layout — Web` / `Layout — Mobile` split a real difference
rather than the same block written twice. The block count and the shell inside each block were
already checked at Stage 5 (`5-prompt.md` Part 6).

```text
mode · platform (+ any per-feature override) · method layer (never a renderer — nothing rendered)
actors per feature (scope + volume band) · actor splits · capability gaps raised
boosters used · per-feature screens · tokens added (0 removed, 0 renamed)
coverage per feature: N checked / N covered / N gaps / N out of scope · render-ready y|n
prompt blocks written (2 | 4)
nav entries added (0 removed, 0 renamed) · directives reflected · skipped
relationship: modelled|none per feature (+ gaps raised) · skipped
pending · questions (design | REQUIREMENT GAP)
next: human review → /bigin-render-design when they want a prototype (their engine, their timing)
```

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Regenerating the design system instead of extending it.** Every screen already built against it
  breaks at once, and nothing records that it happened. Same for renaming a token that looked wrong.
- **Skipping or rushing Stage 4's forward pass.** It is the only thing in this skill that can find an
  omission. Every other check — grounding, all seventeen others in Stage 6 — runs backward and passes
  cleanly on a spec missing a whole exception flow, because nothing on a screen that was never drawn
  can be traced to anything. A design reviewed as complete with a third of the flow absent is the most
  expensive clean-looking failure this pipeline produces.
- **Ticking a render-readiness box by inventing the input.** Placeholder copy, a guessed scale, a state
  nobody specified: all three make Stage 4 Part 5 pass, and all three reach the client inside a
  rendered prototype that looks specified. The render happens later, from a context that is gone.
- **Turning a coverage gap into an out-of-scope line with no citation.** It reads as a decision
  somebody made. The field the client expected then disappears with an explanation nobody gave, and the
  exclusion outlives everyone who could contradict it.
- **Designing the missing screen inside Stage 4.** The pass then has no independent verdict left: it
  drew the thing it was checking for. The gap goes in `## 6`; the screen comes from Stage 3 next run.
- **Rendering, or halting for a renderer.** Neither is this skill's any more. A prototype tool that is
  not installed must never stop a stage that reads use cases and writes markdown —
  `/bigin-render-design` checks its own engine, when a human asks it to render.
- **Stamping `absorbed:` for a UC that got no screen.** The feature reads as designed forever, and no
  future run picks it up.
- **Inventing a screen, a field, or a state.** It reaches a client looking exactly like a specified
  one. Missing detail is a question, not a plausible guess.
- **Designing one screen for two actors whose work is not the same work.** A member reading their
  own record and an administrator working ten thousand of them land on "the same place", so Part 2's
  merge rule quietly makes them one screen — and whichever actor the prototype renders for, the
  other got a product that does not fit their job. The scope comparison is what the merge must pass.
- **A `many` screen with no find machinery, or a `many` state seeded with three rows.** Both review
  as finished, because every element on them is properly grounded, and both collapse the first time
  the screen meets the client's real table. The density, the find controls, and the column behaviour
  are the whole thing the client needed to look at, and none of them appears at three rows.
- **Adding bulk delete or export because an administrator would obviously need it.** D8, and the
  data-side twin of the relationship failure below: plausible, unstated, and it reaches the client
  in a working prototype that they approve. From then on it is a requirement nobody wrote or
  costed — except this one deletes five hundred records at a time.
- **Guessing a scope cell instead of asking.** Writing `all` where no rule grants it hands an actor
  reach nobody approved, and the prototype is where they find out they have it.
- **Designing a mobile product with the web regions vocabulary.** A `nav` region on a phone screen,
  or a `tab-bar` on a web one, asks the prototype tool to build a shell the platform does not have —
  and the prompt reads perfectly right up to the moment somebody renders it.
- **Prompt blocks that disagree across platforms.** A screen in the web block and missing from the
  mobile one, or copy reworded "because it's a phone": whichever block the BA pastes, the others are
  now silently wrong. Only the tool addressed and the shell/viewport may differ — nothing else.
- **Hardcoding a colour or size in a screen spec.** The design system stops being the single source
  and the next feature drifts from this one.
- **Writing a design decision into a UC.** It bypasses the requirement review gate entirely.
- **Leaving a vault id in a prompt.** The prompt fails the only test that matters: standing alone.
- **Dropping the states from a prompt.** Prototypes come back happy-path only, and the empty and
  error screens — the ones clients argue about — never get reviewed.
- **Minting a second UX spec for a feature that has one.** The review splits and both go stale.
- **Giving every screen a nav entry.** A detail screen opened from a list is not a menu item; an
  entry for it is a second, drifting way into the same place.
- **Flipping a directive to `reflected` because it was read.** It is reflected when a screen
  implements it.
- **Letting an external pattern catalog ground a screen.** Ground 2a is a pattern *in this vault*;
  2b is one from an installed skill, and 2b alone grounds nothing. An agentic skill's memory and goal
  dashboards are whole screens — used as a source, they reach a client carrying a citation, which
  reviews as designed where an obvious guess would have been caught.
- **A relationship model over nothing stored.** No `EN-###` field means the system cannot remember
  it, so the row is a requirement gap. Filling a stage-3 autonomous cell no `BR-###` granted is the
  same error one step worse: the prototype shows the agent acting alone and the client agrees to it.
- **Leaving `## 7` in place and empty.** It reads as "the relationship was considered and there is
  none" — a claim nobody made.
- **Setting status early.** Count the open questions from disk, last, every time.
- **Reporting a render.** Nothing here renders. A closeout line saying a render was done, skipped, or
  waived describes a step that was never part of the run, and a reader takes it as evidence a prototype
  exists.

## Model

Per-feature workers run on the **session default model**, not `haiku`. Deciding how many screens a
flow needs, which state belongs to which rule, and whether an existing component fits is judgment
work — the same reason `/bigin-transform-signal` fans out on the default model.

## Additional resources

- **`references/engine-detection.md`** — the **optional** method/quality layer, and the only
  engine-shaped question left in this skill. None of it can halt anything: the provider table, how to detect each one, the install command to report when none
  is present, how the built-in method works, the optional quality boosters (agentic-relationship UX,
  design-library), the ground 2a/2b split that bounds them, the per-step `designer-skills` pattern
  references, and the optional Stage 3.5 craft-quality pass (Perception-First Design's checklist
  mode, or a generic critique skill). Read at Stage 1; the per-step and Stage 3.5 sections are read
  again by each worker at Stage 3.
- **`references/agentic-ux.md`** — the relationship model: what the agentic booster does and does not
  contribute, how the trigger is decided (and why Stage 1 cannot decide it), the five pillars mapped
  onto `## 7` and `## 3` with one clipped as out of scope, a worked example, and the five recurring
  requirement gaps. Read at Stage 1, by the orchestrator, when the skill is installed. A worker reads
  `3-screens.md` Part 4b instead — it cannot reach this directory.
- **`/bigin-render-design`'s own `references/open-design-adapter.md`** — where the Open Design tool
  contract, the probe, the install command, and the halt text live, and
  `references/prompt-contract.md` where the spec→prompt mapping moved. **This skill never reads
  either**, and that is the point: a design run has no engine to resolve.
- **`references/agent-dispatch.md`** — the per-feature worker prompt, its report contract, and the
  wave-verification checklist. Read at Stage 3, before fanning out. It also names the dispatch
  threshold for `agents/ux-brief-assembler.md` — the read-only subagent that combines a feature's
  UCs and entities into that worker's starting Design Brief. Read at Stage 3 for the `PLATFORM:`
  slot every worker prompt carries.
- **`agents/ux-brief-assembler.md`** (plugin-root `agents/`, not this skill's `references/`) — the
  named subagent dispatched per qualifying feature at Stage 3, ahead of the screens worker. It never
  writes a file and never finalizes a screen boundary; it only assembles.
