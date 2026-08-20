---
name: bigin-generate-design
description: This skill should be used when the user asks to "generate the design", "design the screens", "run the design stage", "load the use cases into design", "make a prototype prompt", "give me a Claude design prompt", "give me a Figma Make prompt", "update the design system", "which features still need designing", or after /bigin-transform-signal has drafted or updated a UC. Turns every unprocessed (new or changed) UC-### plus the design principles and directives into per-feature screen specs, a durable vault-wide design system, and two self-contained prototype prompts.
argument-hint: "[feature slug | UC-### | omit for every feature that needs designing]"
---

# Bigin Generate Design

The **load** step of the extract → transform → load pipeline, on the design side. It takes use cases
that have **no current design** and produces the three things a prototype needs:

```text
in    UC-###  (new, or changed since it was last designed)
    + DESIGN-PRINCIPLES.md rows + each hub's ## Design Directives
    + BR-### states  + EN-### fields

out   UX-### per feature      screen inventory + screen specs + flows
                               + ## 7 Relationship Model, on a feature that earns one
    + _design-system/         one vault-wide, append-only token/component system
                               + navigation-map.md — the platform's menu/navigation system
    + two prototype prompts   Claude design and Figma Make, self-contained
```

This skill is the **procedure**. `{design_conventions}` is the **standard** — a rulebook kept
deliberately separate from the requirement one, because a rule about how a screen looks must never
end up deciding what the system does.

**It never edits a requirement.** UCs, BRs, and entities are read-only here (D4). The one exception
is a single `## Discussion` line on a non-approved UC saying "screens exist now" (Stage 5 Part 4).

**It is fully headless.** No checkpoints, no confirmation prompts. Safe to call from `/bigin-ba` or
an unattended batch. The review happens on the artifacts afterwards, not mid-run.

## Operating modes

| Mode | Behaviour |
|---|---|
| **Bootstrap** | `04-UIUX/_design-system/design-tokens.md` is absent. The first screens create it. |
| **Extend** (normal) | The design system exists. Load it, reuse it, **add** what is genuinely new. Never replace it. |
| **Design-only** | A feature with no UC but with open `## Design Directives` rows. Screens from the directives, empty `absorbed:`, no flows. |

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | the design rulebook — paths, the seven hard rules, statuses, grounding, the relationship model |
| `{design_stages_dir}` | `_bigin/stages/design/` | `1-scope`, `2-system`, `3-screens`, `4-prompt`, `5-close` |
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

## Design engine — use one if it is installed

```text
check, in order, and use the first that answers:
  1  BMAD WDS (Freya)   `_bmad/wds/` in the repo, or a wds-*-ux-design skill is available
  2  Figma MCP          a connected figma server (its tools can read a real design system)
  3  any design plugin  a design/UX skill in this session's skill list
  4  built-in           always available — the method in the stage guides themselves

none of 1-3 → run the built-in method and REPORT the install command in the closeout.
              Never halt to ask: this skill is headless, and the built-in method is complete.
```

Full detection, install commands, and how to hand work to an engine: **`references/engine-detection.md`**,
which also covers optional **quality boosters** layered on top of whichever engine is chosen — an
agentic-relationship-UX skill for features that are genuinely about an ongoing AI-agent relationship,
a design-library skill for a non-generic starting palette on bootstrap, per-step `designer-skills`
pattern references for STRUCTURE/ELEMENTS/TOKENS/STATES/NAVIGATION, and an optional Stage 3.5
craft-quality pass — Perception-First Design's checklist mode (Mode 1 only, never its solve or
analyze modes) when installed, or a generic heuristic-evaluation/accessibility-audit/critique-*
skill otherwise — a worker runs on its own drafted screens before reporting. None replaces the
engine; all are read only when they actually apply, and skipped silently when not installed.

The agentic booster is the one with a real output surface: a feature that passes Stage 3's
**relationship trigger** gets a `## 7 Relationship Model` — the memory, autonomy, and trust the
requirements already imply, plus the gaps they never settled. See **`references/agentic-ux.md`**.

## Execution order

```text
scope = $ARGUMENTS slug or UC-###, else every {hub_dir} feature

1  scope     which UCs are NEW / CHANGED / CURRENT, per feature      [1-scope.md]
2  system    seed the design system so screens can cite token names  [2-system.md § Part A]
3  screens   per feature: brief → screen inventory → screen specs    [3-screens.md]
4  prompt    fold in new tokens, then write both prompts             [2-system.md § Part B, 4-prompt.md]
5  close     stamp absorbed, set status, refresh hubs, verify, report [5-close.md]
```

Run all five, in order, every invocation. **Load a stage file on reaching that stage**, not up front.

## Stage 1 — Scope

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
map). It is the menu/navigation system for the platform: seed its `## Structure` from whatever tree
already exists — a dot-path `id` per row, so it nests to whatever depth the real IA needs, not a
fixed two levels. Part B is where screens add the entries a real flow actually needs.

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
```

**A feature with 3+ in-scope UCs, or 4+ distinct cited entities, gets a `ux-brief-assembler`
dispatch first** (`agents/ux-brief-assembler.md`) — it combines that feature's UCs and the `EN-###`
entities they cite (plus `BR-###` mirrors, open hub directives, active design principles) into one
Design Brief, so the screens worker starts from a pre-digested bundle instead of re-reading
everything raw. It never decides a final screen boundary, a token, a state, or the Part 4b
relationship verdict — every one of those stays the screens worker's call. Below that threshold,
skip it; the worker reads `3-screens.md` Part 1 directly.

The mapping that matters: **a run of consecutive steps by the same actor in the same place is one
screen**; a validation is a state, not a screen; an exception flow is a named error state. A 3–9 step
UC normally yields 1–4 screens.

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

## Stage 4 — Extend the system, then write both prompts

Part B of `2-system.md` applies the reported candidates one at a time, in the orchestrator: dedup
first, reuse before adding, add only what is genuinely new, bump the version, changelog it. **Nothing
is ever deleted or renamed** (D1) — a screen specced last month cites that name. The same pass adds
any reported nav entries to `{nav_map_file}` — one row per screen a worker flagged as directly
menu-reachable, never one for a screen reached only through another screen.

Then both prompt blocks, from the same screens and the now-final token values. Every vault id is
expanded into words before it goes in (D6): a prompt with `UC-012 S4` in it renders that string as a
heading in the prototype.

## Stage 5 — Close

Stamp `absorbed:` with `UC-###@version` for **only the UCs that really got a screen row this run**,
re-stamped whole. Set each status from a live count of unchecked questions on disk. Refresh every
hub named in `features:` — `## UX Spec`, `uiux:`, directives that a screen really implements flipped
to `reflected`, questions mirrored. Then the twelve verification checks; a mismatch is blocking. The
last three read `## 7` from disk: the `relationship_model:` flag must match the section that is
really there, every memory row must name a field that really exists, and every gap the section found
must have become a `## 6` question.

```text
mode · engine · boosters used · per-feature screens · tokens added (0 removed, 0 renamed)
prompts written · nav entries added (0 removed, 0 renamed) · directives reflected · skipped
relationship: modelled|none per feature (+ gaps raised) · skipped
pending · questions (design | REQUIREMENT GAP) · next
```

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Regenerating the design system instead of extending it.** Every screen already built against it
  breaks at once, and nothing records that it happened. Same for renaming a token that looked wrong.
- **Stamping `absorbed:` for a UC that got no screen.** The feature reads as designed forever, and no
  future run picks it up.
- **Inventing a screen, a field, or a state.** It reaches a client looking exactly like a specified
  one. Missing detail is a question, not a plausible guess.
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

## Model

Per-feature workers run on the **session default model**, not `haiku`. Deciding how many screens a
flow needs, which state belongs to which rule, and whether an existing component fits is judgment
work — the same reason `/bigin-transform-signal` fans out on the default model.

## Additional resources

- **`references/engine-detection.md`** — the provider table, how to detect each one, the install
  command to report when none is present, how the built-in method works, the optional quality
  boosters (agentic-relationship UX, design-library), the ground 2a/2b split that bounds them, the
  per-step `designer-skills` pattern references, and the optional Stage 3.5 craft-quality pass
  (Perception-First Design's checklist mode, or a generic critique skill). Read at Stage 1; the
  per-step and Stage 3.5 sections are read again by each worker at Stage 3.
- **`references/agentic-ux.md`** — the relationship model: what the agentic booster does and does not
  contribute, how the trigger is decided (and why Stage 1 cannot decide it), the five pillars mapped
  onto `## 7` and `## 3` with one clipped as out of scope, a worked example, and the five recurring
  requirement gaps. Read at Stage 1, by the orchestrator, when the skill is installed. A worker reads
  `3-screens.md` Part 4b instead — it cannot reach this directory.
- **`references/agent-dispatch.md`** — the per-feature worker prompt, its report contract, and the
  wave-verification checklist. Read at Stage 3, before fanning out. It also names the dispatch
  threshold for `agents/ux-brief-assembler.md` — the read-only subagent that combines a feature's
  UCs and entities into that worker's starting Design Brief.
- **`agents/ux-brief-assembler.md`** (plugin-root `agents/`, not this skill's `references/`) — the
  named subagent dispatched per qualifying feature at Stage 3, ahead of the screens worker. It never
  writes a file and never finalizes a screen boundary; it only assembles.
