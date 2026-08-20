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

## Using BMAD WDS (Freya) specifically — the real method, headlessly

WDS is not a generic "engine" entry to acknowledge and move past — its Freya method is what this
plugin's own token architecture and Design Loop were **ported from**, the same porting relationship
`/bigin-generate-prd` has to BMAD's PM workflow. (An earlier, human-present `/design` command in this
plugin's lineage ported WDS Phases 3/4/7 the same way, but interactively, with a checkpoint per page;
`bigin-generate-design` is that same port made headless — the mapping below is how.) When WDS is
actually present in the current repo, read its own data files rather than working from this
paragraph's summary of them — they are the discipline this skill's stage guides were written to
match:

```text
_bmad/wds/data/design-system/token-architecture.md   the Level 1/2/3 raw→semantic→component split —
                                                      identical in spirit to design-conventions.md
                                                      § Token architecture; read WDS's version when
                                                      present, since it may carry naming detail this
                                                      plugin's own copy compresses
_bmad/wds/data/wds-glossary.md                       the Design Loop pattern itself: discuss → page
                                                      spec → wireframe → approve → extract tokens
.claude/skills/wds-3-scenarios/  (or wherever the    Phase 3 — how Freya turns a strategic input into
  installed wds-3-scenarios skill lives)             a linear scenario exposing every page
.claude/skills/wds-4-ux-design/                      Phase 4 — the Design Loop itself, per page
.claude/skills/wds-7-design-system/                  Phase 7 — consolidating extracted tokens into
                                                      one shared system
```

**The mapping onto this skill's own stages — WDS supplies the method, this skill's stages still own
the output shape and the write paths (§ Using an engine, below):**

| WDS phase | What it does | Lands here instead |
|---|---|---|
| Phase 3 (Scenarios) | derive a linear happy-path scenario exposing every page, from a strategic input (Product Brief + Trigger Map) | `3-screens.md` Part 2's UC→screen walk. **A UC already is the scenario** — it has actors, a trigger, and an ordered flow — so skip Phase 3's own elicitation entirely; do not re-derive a scenario from scratch when the UC on disk already is one. Feed Freya's scenario method the UC's `## 2`/`## 3` directly. |
| Phase 4 (Design Loop) | discuss → page spec → wireframe → approve → iterate → extract tokens, **per page, with a human at every step** | `3-screens.md` Parts 3–4 (screen spec + states) and Stage 4's token extraction. Run the same sequence of thinking **headlessly, in one pass per screen**: draft the page spec and its states directly from the grounded sources (§ Grounding) instead of discussing them with a human first, skip the "approve" checkpoint (this skill never halts — the human reviews the finished `UX-###` afterward, not mid-loop), and extract tokens on the same "second use" discipline Freya uses (the first screen or two that need a color/spacing decision seed the token; the next screen that needs the same thing cites it by name instead of inventing a sibling) |
| Phase 7 (Design System) | consolidate extracted tokens/components into one shared system | Stage 2 (seed) and Stage 4 (extend) exactly as already described in `SKILL.md` — WDS's consolidation discipline (dedup, never rename, version + changelog) is what `2-system.md` and D1 already encode. Nothing extra to port here beyond confirming the token levels match. |
| Phase 1–2 (Product Brief, Trigger Map) | establish strategy and personas before any screen work starts | **out of scope, always.** The UC's `## 1` actors/trigger/pre+post-conditions already are that foundation — re-eliciting it duplicates work an approved (or in-review) requirement already did, and risks a persona or strategic framing that contradicts what the UC actually says. Never run these phases, present or absent. |
| Phase 0/5/6 (Alignment sign-off, agentic dev, asset generation) | out of scope by this skill's own design — wireframes + tokens only, no code, no polished visual assets | never invoked, whether or not the installed WDS module ships them |

**Collapsing the Design Loop's checkpoints is the one real adaptation.** WDS assumes a human is
present at "approve" for every page; this skill assumes nobody is. That difference changes *when*
review happens, never *what* gets produced — a headless pass through discuss→spec→wireframe→extract
still has to ground every decision exactly as strictly as an interactive one would (§ Grounding), and
an ungrounded call that a live human would have caught mid-loop becomes, here, an Open Question on
`## 6` instead of a question asked out loud. Do not read "headless" as license to skip a step; it
only means the step's output is a written artifact instead of a paused conversation.

**If the installed WDS module's own skill files (`wds-3-scenarios`, `wds-4-ux-design`,
`wds-7-design-system`) disagree with the mapping above on some point of method** (a naming detail, a
sequencing nuance token-architecture.md states more precisely than this table does), the installed
files win — this table exists to tell you *which* of them to read for *which* part of the job, not to
override them.

## Using an engine — the rules that do not bend

```text
the engine supplies METHOD          how to derive screens, name tokens, structure a system
this plugin supplies CONTRACT       where files go, what a UX spec contains, the seven hard rules
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
| **Agentic UX design** — a relationship-centric-interfaces skill (e.g. `agentic-ux-design-relationship-centric-interfaces`) in this session's available skills | is it in the skill list? | a feature in scope passes the **relationship trigger** — the system judges rather than processes, an `EN-###` field persists something per-user between sessions, and the trigger recurs for the same actor. Three of three, tested per feature in `3-screens.md` Part 4b. Its output is `## 7 Relationship Model` | fire it on "the feature has AI in it". A chatbot screen, a suggestions panel fed by nothing stored, and a report ranked the same for everyone all fail the trigger — and none has a relationship to model. **Its pattern library is whole-screen-shaped; treating it as a source is how an invented screen arrives with a citation.** Full guidance: **`agentic-ux.md`** |
| **A design-library skill** — a catalog of real-brand design references (e.g. a `design-library` skill shipping a library of DESIGN.md-style brand files) in this session's available skills | is it in the skill list? | Stage 2 is bootstrapping (`{tokens_file}` absent) and `{design_principles_file}` has few or no active rows — there is nothing client-stated to seed Foundations from, and a palette invented from nothing reads as generic | a client preference or an existing token already answers the question — a real DESIGN-PRINCIPLES row always outranks a library reference (§ The design system: Foundations is the client's own words, never research) |

Using either: read the skill's own instructions for how to invoke it, then treat what it returns as an
**EXTERNAL PATTERN** — ground **2b** in `design-conventions.md` § Grounding. Never a client preference
(ground 3), never a requirement (ground 1), and never a **vault** pattern (2a):

```text
2a a pattern already in THIS vault     can ground THAT a screen, field, or state exists
2b a pattern from an installed skill   can only shape HOW something already grounded gets built
2b alone                               → not a ground. An Open Question, or a requirement gap.
```

The distinction is not pedantry. 2a is evidence this product already works that way; 2b is evidence
only that the pattern exists somewhere. A catalog used as 2a produces a screen nobody asked for
*carrying a citation* — which reviews as designed, where an obvious guess would have been caught.

Say which booster was used, and why, in the closeout, the same way the chosen engine is named.

## Per-step pattern references — `designer-skills` (design-process plugin)

Narrower than a booster above: each row is read **only for the matching step**, whichever engine is
running it, and treated as ground **2b** (an **external pattern**) in Stage 3's grounding test — never
ground 3 (a preference), never ground 1 (a requirement), and never ground 2a (a vault pattern). These
exist to keep craft consistent; they never license a screen, field, or state the sources didn't
already call for.

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
    perception-first-design (pfd)           5-layer scan — cognitive load, first impression,
                                             processing fluency, perception bias, decision
                                             architecture — any screen; strongest where the flag is
                                             literal (a 3rd typeface, a 5th accent color, spacing that
                                             skips a token) rather than a UX judgment call
    heuristic-evaluation                    general pass, any screen
    accessibility-audit                     contrast, labeling, focus order
    critique-visual-hierarchy /
    critique-composition / critique-typography    one screen looks off and the cause isn't obvious

both PFD and a generic critique skill installed → run PFD alone; its 5-layer stack already subsumes
what the generic ones check (hierarchy, contrast, composition), and running both duplicates the pass
for no second opinion — this is a mechanical checklist, not an adversarial review.

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

### Running Perception-First Design here specifically

PFD ships three modes, and only one belongs in this slot:

```text
Mode 1  evaluate / checklist    walks an artifact against the 5 layers, flags what fails    ← use this
Mode 2  solve / derivation      generates a solution FROM the 5 layers, bottom-up           ← never
Mode 3  analyze                 predicts consequences of a hypothetical change              ← never
```

Mode 2 and 3 both **produce** something — a requirement, a solution, a predicted consequence — from
psychology alone, with no UC, BR, or entity in the loop. That is exactly the ungrounded design call
D3 and Stage 3's grounding test exist to catch; running either here would be a critique skill quietly
promoted into a fourth ground next to the real three (§ Grounding). Invoke the bare checklist pass
only — read `skills/pfd/SKILL.md`'s 5-layer stack directly and walk it against the screen spec's
regions, elements, copy, states, and the token names/values already chosen for it.

**Skip the corpus load.** The corpus-backed `/perception-first-design:evaluate` command (and its
Tier 2 template, design-system profiles, and worked-examples) is built for a live artifact — a URL it
fetches, an HTML/CSS snippet, a screenshot. A screen spec here is a markdown description of a screen
that does not exist as a renderable artifact yet, so there is nothing to fetch and no design-system
profile to detect. Use PFD's own "Quick PFD scan" path (SKILL.md § Corpus-Backed Evaluation) — the
5-layer stack directly, no corpus files, no HTML rebuild step, no `corpus/validation/mvs-results/`
output.

**Skip the Insight Log.** SKILL.md marks it mandatory "every analysis," but that log lives inside the
PFD plugin's own install directory and is meant to accumulate cross-project learnings from deliberate,
one-off audits — not a per-screen entry from an automated pass that can run across dozens of screens
in one invocation. Writing here pollutes a shared plugin file with noise that was never meant for it.
Do not read or write `references/insights-log.md`, `references/learnings/`, or
`references/practitioner-corrections.md` from this pass.

Sorting a finding into craft-vs-grounded still runs layer by layer: Cognitive Load and Processing
Fluency findings (a screen holding more open fields than the flow needs at once, a typeface or accent
color count above what the design system already restrains itself to, spacing that skips an existing
token) are craft — fixed in place, same as any other critique-skill finding. A First-Impression,
Perception-Bias, or Decision-Architecture finding that would add, remove, or reorder something the UC
never asked for is not craft; it goes back through the grounding test like anything else Stage 3.5
surfaces. And a "2 fonts max, 3-4 colors" flag is a constraint on an *unbounded* choice this skill was
about to make on its own — it never overrides a token value the client's own DESIGN-PRINCIPLES row
already set (ground 3 always outranks a checklist heuristic).

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
- **Running PFD's solve or analyze mode as the craft-quality pass.** Both generate output from the
  5-layer stack alone, with no UC, BR, or entity involved — the exact ungrounded design call Stage 3
  exists to catch, just wearing a psychology citation. Only Mode 1 (evaluate/checklist) belongs here.
- **Loading PFD's corpus, or writing its Insight Log, from this pass.** The corpus-backed evaluate
  path is built for a live URL/HTML/screenshot this pass never has; the Insight Log lives in the
  plugin's own directory and is for deliberate one-off audits, not a per-screen entry from a run that
  may touch dozens of screens.
- **Promoting an external pattern to ground 2a.** The one loophole wide enough to fit a whole screen
  through, and it closes on a distinction a hurried run will not make on its own: 2a is *this vault*,
  2b is *somewhere else*.
- **Re-running WDS's Phase 1–2 elicitation because the module ships it.** The UC's `## 1` already is
  the strategic input Freya normally gathers first; re-eliciting it risks a persona or framing that
  contradicts the requirement on record instead of designing from it.
- **Waiting for WDS's "approve" checkpoint.** This skill never halts. Draft the page spec, wireframe,
  and token extraction in one headless pass per screen, grounded exactly as strictly as an
  interactive pass would be — an ungrounded call becomes an Open Question, not a paused conversation.
