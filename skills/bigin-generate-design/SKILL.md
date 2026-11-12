---
name: bigin-generate-design
description: >-
  This skill should be used when the user asks to "generate the design", "design the screens", "design the UX", "run the design stage", "load the use cases into design", "map the user flows", "review the user flow", "fix the navigation", "which features still need designing", or after /bigin-transform-signal has drafted or updated a UC. Turns every unprocessed (new or changed) UC-### plus the pain-point register and design directives into per-feature UX specs — actors, screens, states, real copy, the navigation shell, and the user flows that connect them — then runs a built-in flow review and a forward coverage check that nothing in the requirements went undesigned. It produces NO design system and NO tokens: colour, type, spacing, and components come from the design team or are bound at render time. It renders nothing — rendering is /bigin-render-design-od, invoked by a human, who can then run a perception-first-design (or similar) critique against the rendered artifact.
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
now" (Stage 6 Part 2, written by `bigin design close`).

**It is headless, with no halt at all.** No checkpoints, no confirmation prompts, no question put to a
human mid-run, and nothing that stops it before the work either. So it is unconditionally safe to call
from `/bigin-run` or an unattended batch — but not from inside the `bigin-ba` agent, which cannot dispatch
workers and never routes to design. Only a missing or ahead-of-plugin workspace stops it, as in
every skill here.

## The standard lives in the vault, not here

Each rule this skill applies has **one home**, in `_bigin/conventions/` — where a worker can read it
(a `SKILL.md` sits in the plugin install directory, which a subagent cannot reach). Open the section a
stage file cites; never work from a summary of it.

| Topic | Home |
| :--- | :--- |
| Platform: `web \| mobile \| both`, the default, a per-feature override | `design-platform.md` § Platform |
| Actor scope: whose records, how many, and when one place is two screens | `design-actor-scope.md` § Actor scope |
| User flows and the pain points they resolve | `design-navigation.md` § User flows and pain points |
| Semantic roles — the closed list that replaced tokens | `design-screens.md` § Semantic style roles |
| View ID and Screen Type | `design-screens.md` § View ID and Screen Type |
| Grounding: what may put a screen, field or state on a spec | `design-grounding.md` § Grounding |
| The eight hard rules (D1–D8), paths, the write map | `design-core.md` |

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
  evaluate, unlike the markdown spec this skill produces. This skill never invokes one.
  /bigin-render-design-od runs `perception-first-design:evaluate` once, on the assembled prototype,
  when that skill is installed (a by-eye check otherwise); anything beyond that is a human's follow-up
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

1  scope     `bigin design scope` — NEW / CHANGED / CURRENT, gates, platform   [1-scope.md]
2  nav       seed the navigation shell, shaped by the pain points     [2-navigation.md § Part A]
3  screens   ONE WORKER PER FEATURE, always: card + `bigin worklist design`
             → actor scope → inventory → specs → flows                [references/agent-dispatch.md]
             `bigin design check <slug> --phase wave` after each wave
4  review    walk every journey as the actor; improve it in place     [4-flow-review.md]
5  verify    `bigin design items` — forward coverage by id, then the
             judgement the ids cannot make, + render readiness        [5-verify.md]
6  close     extend the nav map, `bigin design close` per feature,
             the checks the engine cannot run, the report  [2-navigation.md § Part B, 6-close.md]
```

Six stages, in order, every invocation, and **no precondition ahead of them**. **Load a stage file on
reaching that stage**, not up front, and load nothing a stage file does not name: the stage files are
the procedure, and this file deliberately does not repeat them.

The run ends at a verified specification. A prototype is `/bigin-render-design-od`, whenever a human
wants one.

## What the engine does, and what stays yours

`scripts/bigin` (`python "${CLAUDE_PLUGIN_ROOT}/lib/bigin/cli.py"`, fallback `python3`) owns every
lookup in this stage. A UX spec is 40–110 KB; a model re-reading one to count questions or compare ids
is the expensive way to do it and the one that gets it wrong quietly.

| Command | Replaces |
| :--- | :--- |
| `bigin design scope [slug\|UC-###] [--run R]` | Stage 1's three-way read, the four gates, platform, mode, pain-point counts — and it reports `DRAFTED` / `resume: review` when a dead run left screens on disk |
| `bigin mint ux --count N` | grepping `04-UIUX/` for the highest id |
| `bigin worklist design <slug> --out <path>` | the worker reading every UC, BR, entity, the hub, the principles and the nav map whole |
| `bigin design check <slug> --phase wave` | the wave checklist's lookups (inventory ↔ blocks, served steps exist, roles, raw values, regions, View IDs) |
| `bigin design items <slug>` | building Stage 5's requirement item list and matching it by id |
| `bigin design close <slug> [--run R]` | stamping `absorbed:`, the status from the live question count, `nav_map:`, the hub pointer and `uiux:`, mirroring `## 6` onto the hub, the one `## Discussion` line — then the lookup checks |

**Yours, because they need a reader:** every screen boundary and flow (the worker), the flow review,
whether an unmatched requirement item is really on a screen, whether a directive is implemented,
the grounds behind an actor's scope, `## 7` against real entity fields, and each `confirm` finding
the engine hands back.

## Resume

```text
bigin run new --stage design                       → the run id, once, before Stage 1
bigin run record <run> --task screens:<slug> --status ok    after that feature's wave check passes
bigin design close <slug> --run <run>              records designed:<slug> itself
```

A run that died is resumed by starting again with the same `--run`: `bigin design scope --run <run>`
marks a closed feature `resume: done` (skip it) and a feature whose screens are on disk
`resume: review` (start it at Stage 4 — **never** dispatch its screens worker again). Without the run
id the files still say most of it: a use case with a screen row and no `absorbed:` stamp reads
`DRAFTED`, not `NEW`.

## Model

Per-feature workers run on the **session default model**, not `haiku`: how many screens a flow
needs, which state belongs to which rule, and whether a journey resolves a pain point are judgement.
The engine commands need no model at all.

## Additional resources

- **`references/agent-dispatch.md`** — the worker prompt, its report contract, the wave check. Read
  at Stage 3, before fanning out.
- **`references/method-layer.md`** — the **optional** method layer Stage 3 screens are derived
  through, its detection order and install commands, and the per-step `designer-skills` pattern
  references. Read at Stage 1; a worker never opens it.
- **`references/agentic-ux.md`** — the relationship model (`## 7`): what the booster contributes, why
  Stage 1 cannot decide the trigger, the five recurring requirement gaps. Read at Stage 1 only when
  a relationship-UX skill is installed.
- **`/bigin-render-design-od`'s `references/open-design-adapter.md`** — the Open Design contract.
  **This skill never reads it**: a design run has no engine and no design system to resolve.
