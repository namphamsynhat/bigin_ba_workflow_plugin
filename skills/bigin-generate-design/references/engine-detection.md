# Design engine — detect it, use it, or report how to install it

Read at Stage 1, by the orchestrator only. A worker never detects anything — it is **told** which
engine to use, in its dispatch prompt.

```text
an ENGINE changes HOW the screens get made.
it never changes WHAT gets written: a UX spec, a design system, two prompts, the same shape either way.
```

## Detect, in this order, and stop at the first hit

| # | Engine | How to detect | What it is good for |
|---|---|---|---|
| 1 | **BMAD WDS (Freya)** | `Glob` for `_bmad/wds/**` in the repo, **or** a skill named `wds-*` (e.g. `wds-3-scenarios`, `wds-4-ux-design`, `wds-7-design-system`) appears in this session's available skills | a full scenarios → design-loop → design-system method, and a token architecture this plugin's own rules were modelled on |
| 2 | **Figma MCP** | a connected server matching `figma` in `claude mcp list`, **or** `mcp__*Figma*` tools are available | reading a **real** existing design system (variables, components, libraries) instead of inventing tokens; pushing screens into Figma |
| 3 | **Any design plugin** | a design/UX skill in this session's available-skills list (a design-system, UI, or wireframe skill) | token and component conventions, accessibility checks |
| 4 | **Built-in** | always | the method already written into `_bigin/stages/design/` |

Detect **once**, at Stage 1. Announce the result in the closeout. Do not re-detect per feature.

## Using an engine — the rules that do not bend

```text
the engine supplies METHOD          how to derive screens, name tokens, structure a system
this plugin supplies CONTRACT       where files go, what a UX spec contains, the six hard rules
conflict → the CONTRACT wins.
```

Concretely:

| The engine wants to… | Do this instead |
|---|---|
| write to `_bmad-output/`, `docs/ux/`, or its own tree | write to `{ux_dir}` and `{design_system_dir}` |
| run an interactive design loop with checkpoints | run its method headlessly; this skill never halts |
| re-elicit strategy, personas, or a product brief | the UCs already have actors and goals. Never invent a persona; use the roles on record, or a neutral one ("the reviewer") |
| create a fresh design system per run | extend the one at `{design_system_dir}` (D1) |
| generate icons, images, or polished visual assets | out of scope — the prototype prompt produces the visuals |
| write code | out of scope — the prompts are the terminal deliverable |

**Figma MCP specifically.** When it is the engine, read the real design system first
(`get_variable_defs`, `get_design_context`, `search_design_system`, `get_libraries`) and seed
`{tokens_file}` from **those** names and values rather than inventing parallel ones. A token that
already exists in the client's Figma library and is re-invented here guarantees drift.

## Design quality boosters — optional, layered on top of whichever engine runs

These never replace the engine or the built-in method above — they are consulted **in addition**,
and only when they actually apply. Neither changes the CONTRACT: output is still a UX spec, a design
system (tokens/components/nav map), and two prompts, written to the usual paths.

| Booster | Check for it | Use it when | Never |
|---|---|---|---|
| **Agentic UX design** — a relationship-centric-interfaces skill (e.g. `agentic-ux-design-relationship-centric-interfaces`) in this session's available skills | is it in the skill list? | the feature being designed is genuinely about an ongoing AI-agent relationship — memory carried across sessions, trust that deepens over time, collaborative planning with an agent — not just any screen with a chatbot in it | invoke it for an ordinary CRUD form, dashboard, or list. That skill is explicit that it is for relationship-centric design only, on request — a generic UI task is out of its scope even here |
| **A design-library skill** — a catalog of real-brand design references (e.g. a `design-library` skill shipping a library of DESIGN.md-style brand files) in this session's available skills | is it in the skill list? | Stage 2 is bootstrapping (`{tokens_file}` absent) and `{design_principles_file}` has few or no active rows — there is nothing client-stated to seed Foundations from, and a palette invented from nothing reads as generic | a client preference or an existing token already answers the question — a real DESIGN-PRINCIPLES row always outranks a library reference (§ The design system: Foundations is the client's own words, never research) |

Using either: read the skill's own instructions for how to invoke it, treat what it returns as one
more **PATTERN** input to Stage 3's grounding test (§ Grounding, ground 2) — never as a client
preference (ground 3) and never as a requirement (ground 1). Say which booster was used, and why, in
the closeout, the same way the chosen engine is named.

## Per-step pattern references — `designer-skills` (design-process plugin)

Narrower than a booster above: each row is read **only for the matching step**, whichever engine is
running it, and treated as ground 2 (a **PATTERN**) in Stage 3's grounding test — never ground 3 (a
preference) and never ground 1 (a requirement). These exist to keep craft consistent; they never
license a screen, field, or state the sources didn't already call for.

| Built-in-method step | `designer-skills` skill | Reach for it when |
|---|---|---|
| 2 STRUCTURE | `user-flow-diagram` | a UC's branches are hard to read straight off `## 2`/`## 3` and a diagram would settle screen boundaries faster than re-reading the flow twice |
| 2 STRUCTURE · 3 SCREEN TYPE | `wireframe-spec` | laying out content priority and component placement before committing to a screen type |
| 4 ELEMENTS (form screens) | `form-design` | the screen is "the actor supplies data" and field grouping or validation placement isn't obvious from the entity alone |
| 5 TOKENS | `design-token`, `color-system`, `typography-scale`, `spacing-system` | `{tokens_file}` is missing a Level 2/3 name a screen needs and nothing existing fits — a naming *convention*, never a value invented in place of a stated preference |
| 6 STATES | `loading-states`, `error-handling-ux`, `feedback-patterns`, `state-machine` | enumerating which states a control needs, once a BR or exception flow has already said one is required |
| 7 NAVIGATION | `navigation-patterns`, `information-architecture` | deciding where a new entry nests inside `{nav_map_file}`'s existing tree |

**Never** use one of these to decide *whether* a screen, field, or state exists — that decision is
Stage 3's grounding test alone. A pattern skill only shapes how something already grounded gets
built, and only if it is actually installed in this session — absent is a silent skip, not a gap to
report in the closeout the way a missing engine is.

## Stage 3.5 — an optional craft-quality pass

Runs after a worker drafts a feature's screens, before it reports. `agent-dispatch.md`'s wave
verification checks **structure** — ids resolve, token names exist, a question is really unchecked —
but nothing today checks whether the result reads as good UX. Headless, same as everything else in
this skill: no checkpoint, no question put to a human mid-run.

```text
consult, on the worker's OWN just-drafted screens only, whichever of these is installed:
    heuristic-evaluation                    general pass, any screen
    accessibility-audit                     contrast, labeling, focus order
    critique-visual-hierarchy /
    critique-composition / critique-typography    one screen looks off and the cause isn't obvious

a pure craft fix (spacing, contrast, a redundant label, hierarchy)
    → apply it directly to the screen spec being drafted, same worker, before reporting
    → no Open Question, no report line — nothing here changed WHAT the screen shows

a finding that would change what the screen must show or how a control must behave
    → it is no longer craft, it is back to Stage 3's grounding test:
      already grounded  → apply it and cite the ground
      not grounded      → an Open Question (D3), same as any other ungrounded decision — never a
                          silent design call disguised as a "best practice" fix
```

**Never** let a critique skill's finding license a new screen, field, or state on its own — "the
audit flagged it" is not one of Stage 3's three grounds (§ Grounding). Run this at most once per
screen per run; a worker re-critiquing its own fixes in a loop is scope creep, not quality. None of
these skills installed → skip the pass silently; it was always optional.

## When nothing is installed

The built-in method is complete — it is what the five stage guides describe. So:

```text
run the built-in method to completion
report, in the closeout: which engines were looked for, that none was found, and ONE install line
never halt, never ask mid-run           # this skill is headless
```

**Report exactly these, and nothing improvised** — the same discipline `/bigin-new-project` § 7.3
uses. A guessed installer either fails noisily or installs the wrong thing.

| Engine | What to say |
|---|---|
| Figma MCP | "Figma is not connected. Authorize the Figma connector in claude.ai connector settings, or run `claude mcp add --transport http figma https://mcp.figma.com/mcp`, then re-run." |
| BMAD WDS | "The WDS (Freya) design module is not present. It ships with the BMAD Method installer — no install command is pinned in this plugin; install it in this repo and re-run." |
| A design plugin | "No design plugin is installed. Browse `/plugin marketplace` for a design-system or UI plugin, install one, and re-run." |

Say it **once**, in the closeout, as a next step — not as a warning per feature.

## The built-in method, in one page

This is what stages 2–4 already do; it is written out here so a reader can see it as one method.

```text
1  FOUNDATIONS   take the client's active DESIGN-PRINCIPLES rows as the whole visual brief.
                 Nothing else is a stated preference. Silence is not permission to invent a brand.

2  STRUCTURE     walk each UC's ## 2 in order.
                 same actor + same place, consecutively   → one screen
                 different place or task                  → a new screen
                 system-only step                         → not a screen
                 validation                               → a state
                 exception flow                           → a named error state
                 then merge screens that two UCs both land on.

3  SCREEN TYPE   pick the plainest type the step needs, and reuse a sibling feature's version of it:
                 many records, filterable         → list / table
                 one record, read-mostly          → detail
                 the actor supplies data          → form (one screen; a wizard only when the UC
                                                    itself splits the input across steps)
                 the actor decides yes/no         → review + disposition
                 the flow ends                    → confirmation
                 A type nothing in the flow calls for is a screen nobody asked for.

4  ELEMENTS      fields come from the EN-### entity: its names, its types, its required flags,
                 its enum values as the dropdown's real options.
                 actions come from the step's verbs.
                 copy is real words, in the client's language.

5  TOKENS        cite an existing token by name. Nothing fits → propose ONE, named for meaning
                 (--color-action-primary, not --color-blue). Extract a component on its SECOND use.

6  STATES        empty · loading · validation-error · permission-denied · failure · success,
                 each traced to a BR, an exception flow, an entity constraint, or a post-condition.

7  NAVIGATION    only a screen the actor opens directly from a menu gets a nav-map entry — a
                 detail, wizard step, or modal reached through another screen does not.

8  GROUND OR ASK every decision cites a requirement, an existing pattern, or a stated preference.
                 None of the three → an Open Question. This is the line between a design decision
                 and an invented requirement.
```

## Failure modes

- **Letting the engine choose the output paths.** Half the design lands somewhere nothing reads, and
  the run still reports success.
- **Halting because no engine is installed.** The built-in method exists precisely so a run never
  dead-ends; a halt turns a working design stage into a blocked one.
- **Inventing tokens while a real Figma library is connected.** The client already has these values;
  a parallel set guarantees a rebuild later.
- **Running an engine's interactive loop.** It waits for a human that an unattended run does not have.
- **Repeating the install suggestion per feature.** Once, in the closeout, as a next step.
- **Letting a craft-quality finding invent a requirement.** "The accessibility audit flagged it" is
  not a ground (§ Grounding) — an ungrounded finding is an Open Question, exactly like any other
  ungrounded decision, never a fix applied on the critique skill's authority alone.
