# The method layer, and the gated flow review

Read at Stage 1, by the orchestrator only. A worker never detects anything — it is **told** which
method to use, in its dispatch prompt.

**Nothing in this file may stop a run — nor may anything else in this skill.** Three questions, kept
deliberately apart:

```text
§ The method layer            WHICH optional method is available to derive the screens with — BMAD
(Stage 3)                     WDS, Figma MCP, a design plugin, or the built-in method. Every one is
                              a SILENT SKIP, or one reported install line, when absent.

§ Stage 4 — the flow review   WHETHER the JOURNEYS get critiqued. This one is GATED: no skill
(Stage 4)                     installed means the whole stage is SKIPPED, and NO ### Flow Review
                              table is written — not an empty one. Still not a halt.

open-design-adapter.md        HOW a finished spec is RENDERED into artifacts, and which DESIGN
(/bigin-render-design)        SYSTEM gets bound to it. A different skill, invoked when somebody
                              actually wants a prototype. This skill never reads that file.
```

```text
a METHOD changes HOW the screens get made.
it never changes WHAT gets written: a UX spec — actors, screens, states, real copy, semantic roles,
flows — and a navigation map. The same shape either way.

NO METHOD, AND NO BOOSTER, PRODUCES A DESIGN SYSTEM HERE. Not a palette, not a type scale, not a
component library, not a token. That is the design team's, or is bound at render time. A method
that wants to generate one is running outside this skill's contract (§ Using a method layer).
```

## § The method layer — detect, in this order, first hit wins

| # | Method | How to detect | What it is good for |
|---|---|---|---|
| 1 | **BMAD WDS (Freya)** | `Glob` for `_bmad/wds/**` in the repo, **or** a skill named `wds-*` (e.g. `wds-3-scenarios`, `wds-4-ux-design`) appears in this session's available skills | a full scenarios → design-loop method for turning a flow into pages |
| 2 | **Figma MCP** | a connected server matching `figma` in `claude mcp list`, **or** `mcp__*Figma*` tools are available | reading a **real** existing design system to sanity-check that a screen's structure is buildable in it — never to import tokens into the vault (§ Figma MCP specifically) |
| 3 | **Any design plugin** | a design/UX skill in this session's available-skills list | screen-type and interaction conventions, accessibility checks |
| 4 | **Built-in** | always | the method already written into `_bigin/stages/design/` |

Detect **once**, at Stage 1. Announce the result in the closeout. Do not re-detect per feature.

### Using BMAD WDS (Freya) specifically

WDS's Freya method is what this plugin's Design Loop was **ported from**. When WDS is present in the
current repo, read its own data files rather than working from this paragraph's summary:

```text
_bmad/wds/data/wds-glossary.md                       the Design Loop pattern: discuss → page spec →
                                                      wireframe → approve → extract
.claude/skills/wds-3-scenarios/                      Phase 3 — turning a strategic input into a
                                                      linear scenario exposing every page
.claude/skills/wds-4-ux-design/                      Phase 4 — the Design Loop itself, per page
```

| WDS phase | What it does | Lands here instead |
|---|---|---|
| Phase 3 (Scenarios) | derive a linear happy-path scenario exposing every page | `3-screens.md` Part 2's UC→screen walk, and Part 4c's flows. **A UC already is the scenario** — actors, a trigger, an ordered flow — so skip Phase 3's own elicitation entirely and feed Freya's method the UC's `## 2`/`## 3` directly. Its scenario *is* this pipeline's flow, with `Resolves` and `Steps to goal` added |
| Phase 4 (Design Loop) | discuss → page spec → wireframe → approve → iterate, **per page, with a human at every step** | `3-screens.md` Parts 3–4. Run the same sequence of thinking **headlessly, in one pass per screen**: draft the page spec and its states directly from the grounded sources (§ Grounding) instead of discussing them first, and skip the "approve" checkpoint — this skill never pauses mid-run |
| Phase 7 (Design System) | consolidate extracted tokens/components into one shared system | **out of scope, always.** This pipeline produces no design system (§ above). Freya's token extraction has nothing to write to here: a screen names a semantic ROLE instead, and the real system arrives later from the design team or at render time. Never run this phase, present or absent |
| Phase 1–2 (Product Brief, Trigger Map) | establish strategy and personas before any screen work | **out of scope, always.** The UC's `## 1` actors/trigger/pre+post-conditions already are that foundation, and the hub's `## Pain Points` already are the client's stated friction — re-eliciting either risks a persona or framing that contradicts what is on record |
| Phase 0/5/6 (Alignment sign-off, agentic dev, asset generation) | out of scope by this skill's own design — screens, flows, and navigation only | never invoked |

**Collapsing the Design Loop's checkpoints is the one real adaptation.** WDS assumes a human is
present at "approve" for every page; this skill assumes nobody is. That changes *when* review happens,
never *what* gets produced — a headless pass still grounds every decision exactly as strictly, and an
ungrounded call becomes an Open Question on `## 6` instead of a question asked out loud.

**Dropping Phase 7 is the second.** It is not a simplification of Freya's method so much as a
different division of labour: Freya extracts a design system from the pages it draws, and this
pipeline deliberately leaves that to whoever owns the brand. A run that lets Phase 7 fire anyway
produces exactly the artifact this skill was changed to stop producing.

### Using a method layer — the rules that do not bend

```text
the method supplies HOW           how to derive screens, structure a page, sequence a flow
this plugin supplies CONTRACT     where files go, what a UX spec contains, the eight hard rules
conflict → the CONTRACT wins.
```

| The method wants to… | Do this instead |
|---|---|
| write to `_bmad-output/`, `docs/ux/`, or its own tree | write to `{ux_dir}` and `{ux_system_dir}` |
| run an interactive design loop with checkpoints | run its method headlessly; this skill puts no question to a human mid-run |
| re-elicit strategy, personas, or a product brief | the UCs already have actors and goals, and the hub already has pain points. Never invent a persona |
| extract, generate, or consolidate a **design system** | **refuse.** Name a semantic role from the closed list (`{design_conventions}` § Semantic style roles). There is nowhere to write a token and nothing that would cite it |
| generate icons, images, or polished visual assets | out of scope — a render produces the visuals, against a design system a human binds |
| write code | out of scope — the spec is the terminal deliverable |

**Figma MCP specifically.** It is the one method that can see a real design system, and the temptation
is to copy it into the vault. Do not: this pipeline holds no tokens, and a mirrored copy of the
client's Figma library would be stale the first time they change it and authoritative-looking forever.
Use it to **check** — that a screen's structure maps onto components the client really has, that a
state the spec needs is expressible — and report what does not fit as an Open Question. Which design
system a prototype is actually built against is `/bigin-render-design`'s question, asked of a human.

## § Stage 4 — the flow review

**The gate.** Stage 4 runs when a review skill is installed, and is skipped, silently, when none is:

| Installed | What Stage 4 does |
|---|---|
| **Perception-First Design** (`pfd`, `perception-first-design`) | runs. The built-in walk (`4-flow-review.md` Parts 1–4) plus PFD's 5-layer checklist as Part 5. Stamp `flow_review: pfd` |
| A generic critique skill (`heuristic-evaluation`, `accessibility-audit`, `critique-visual-hierarchy`, `critique-composition`, `critique-typography`) | runs on the built-in walk, using the critique skill for Part 5 in whatever shape it offers. Stamp `flow_review: <skill>` |
| Both PFD and a generic critique skill | **PFD alone.** Its 5-layer stack already subsumes what the generic ones check, and running both duplicates the pass for no second opinion — this is a mechanical checklist, not an adversarial review |
| **Neither** | **the whole stage is SKIPPED.** Write no `### Flow Review` table — and specifically not an empty one. Stamp `flow_review: skipped`, report one install line, continue to `5-verify` |

**Why this one is gated when everything else here is a silent skip.** A flow critique run without a
method is a paragraph of plausible opinion landing in the spec as a `sound` verdict — and `sound` is
the strongest claim this pipeline makes about a journey. A skipped review says "nobody looked", which
is true and recoverable. A fabricated one says "somebody looked and it was fine", and nobody ever
looks again.

An **empty** table fails the same way with less effort behind it: `### Flow Review` with no rows reads
as "reviewed, nothing found". `6-close.md` check 17 blocks on either mismatch.

### Running Perception-First Design here specifically

PFD ships three modes, and only one belongs in this slot:

```text
Mode 1  evaluate / checklist    walks an artifact against the 5 layers, flags what fails    ← use this
Mode 2  solve / derivation      generates a solution FROM the 5 layers, bottom-up           ← never
Mode 3  analyze                 predicts consequences of a hypothetical change              ← never
```

Mode 2 and 3 both **produce** something — a requirement, a solution, a predicted consequence — from
psychology alone, with no UC, BR, entity, or pain point in the loop. That is exactly the ungrounded
design call D3 and Stage 3's grounding test exist to catch; running either here would be a critique
skill quietly promoted into a fourth ground next to the real ones. Invoke the bare checklist pass
only — read `skills/pfd/SKILL.md`'s 5-layer stack directly and walk it against the flows, the screen
specs' regions, elements, copy, and states, and the navigation shell.

**Walk it against the JOURNEY, not only the screen.** The 5 layers were written for an artifact, and
the temptation is to run them screen by screen and stop. The flows are what this stage is for:

```text
Cognitive Load          across the FLOW — how much the actor is holding at step 3 that step 1 gave
                        them and nothing has taken away. A screen can be light and a journey heavy
First Impression        the flow's ENTRY screen, and what it tells the actor about where they are
Processing Fluency      whether the same thing is called the same word at every step of the journey.
                        A control named "Submit" on one screen and "Send for review" on the next is
                        a fluency failure the per-screen pass cannot see
Perception Bias         what the ordering and emphasis of a list or a queue implies is important —
                        the layer most likely to interact with a PP-### about finding things
Decision Architecture   at each branch, whether the actor has what they need to choose, and whether
                        the default is the one the requirements actually favour
```

**Skip the corpus load.** The corpus-backed `/perception-first-design:evaluate` command (and its Tier
2 template, design-system profiles, and worked examples) is built for a live artifact — a URL, an
HTML/CSS snippet, a screenshot. A UX spec is a markdown description of screens that do not exist as a
renderable artifact yet, so there is nothing to fetch and no design-system profile to detect. Use
PFD's own "Quick PFD scan" path — the 5-layer stack directly, no corpus files, no HTML rebuild, no
`corpus/validation/mvs-results/` output.

**Skip the Insight Log.** SKILL.md marks it mandatory "every analysis," but that log lives inside the
PFD plugin's own install directory and accumulates cross-project learnings from deliberate, one-off
audits — not per-flow entries from an automated pass that can run across dozens of flows in one
invocation. Do not read or write `references/insights-log.md`, `references/learnings/`, or
`references/practitioner-corrections.md` from this pass.

**Its colour and typography heuristics have no target here.** A "2 fonts max, 3–4 accent colours"
flag is a constraint on an unbounded visual choice, and this pipeline makes none — there is no
palette, no type scale, and no token for it to bound. Skip those findings rather than inventing
something for them to apply to; a run that answers a colour-count flag has just produced the design
system this skill exists not to produce.

### Sorting a finding

Every finding, from any skill, sorts the same way (`4-flow-review.md` Part 3):

```text
ORDER, EMPHASIS, WORDING, DENSITY, a misleading label, a missing back route
    → fix it in place, cite the layer, changelog it. Nothing about WHAT the screen shows changed

ADD, REMOVE, or REORDER something the requirements never asked for
    → back through the grounding test:
      already grounded  → apply it and cite the ground
      not grounded      → an Open Question (D3), never a silent design call disguised as a
                          "best practice" fix
```

**A checklist finding is never a fourth ground.** "The audit flagged it" is ground 2b at best
(`{design_conventions}` § Grounding) — it shapes how a grounded thing is built and grounds nothing on
its own. And ground 3 always outranks it: a `DESIGN-PRINCIPLES` row the client stated wins over any
heuristic.

Run it **at most once per flow per run**. A pass re-critiquing its own fixes is scope creep with a
quality label on it.

## § Per-step pattern references — `designer-skills` (design-process plugin)

Narrower than a method: each row is read **only for the matching step**, whichever method is running
it, and treated as ground **2b** (an external pattern) — never ground 1, 1b, 2a, or 3. These keep
craft consistent; they never license a screen, field, state, or flow the sources did not already call
for.

| Built-in-method step | `designer-skills` skill | Reach for it when |
|---|---|---|
| 2 STRUCTURE · 8 FLOWS | `user-flow-diagram` | a UC's branches are hard to read straight off `## 2`/`## 3` and a diagram would settle screen boundaries or a flow's `Path` faster than re-reading twice |
| 2 STRUCTURE · 3 SCREEN TYPE | `wireframe-spec` | laying out content priority before committing to a screen type |
| 4 ELEMENTS (form screens) | `form-design` | the screen is "the actor supplies data" and field grouping or validation placement isn't obvious from the entity alone |
| 6 STATES | `loading-states`, `error-handling-ux`, `feedback-patterns`, `state-machine` | enumerating which states a control needs, once a BR or exception flow has already said one is required |
| 7 NAVIGATION | `navigation-patterns`, `information-architecture` | deciding where a new entry nests inside `{nav_map_file}`'s existing tree |

**Not listed, deliberately:** `design-token`, `color-system`, `typography-scale`, `spacing-system`.
They shape a design system, and this pipeline produces none. A screen that needs a visual decision
names a semantic role instead (`{design_conventions}` § Semantic style roles); if the role list
genuinely cannot express it, that is a `## 6` question, not a reason to reach for a token skill.

**Never** use one of these to decide *whether* a screen, field, state, or flow exists — that is
Stage 3's grounding test alone. A missing one is a silent skip, not a gap to report.

## § When nothing is installed

The built-in method is complete — it is what the stage guides describe. So:

```text
run the built-in method to completion
Stage 4: skipped, with NO ### Flow Review table written
report, in the closeout: which methods were looked for, that none was found, and ONE install line
never halt, never ask mid-run           # this skill is headless
```

**No carve-out.** Every method, pattern skill, and review skill above is optional, and its absence is
a silent skip or a single reported install line. A design run halts for nothing at all.

**Report exactly these, and nothing improvised.** A guessed installer either fails noisily or installs
the wrong thing.

| Missing | What to say |
|---|---|
| A flow-review skill | "No flow-review skill is installed, so the user journeys were not critiqued this run — only checked for coverage. Install a perception-first-design skill (or a heuristic-evaluation / accessibility-audit skill) via `/plugin marketplace`, then re-run to get a `### Flow Review` on each spec." |
| Figma MCP | "Figma is not connected. Authorize the Figma connector in claude.ai connector settings, or run `claude mcp add --transport http figma https://mcp.figma.com/mcp`, then re-run." |
| BMAD WDS | "The WDS (Freya) design module is not present. It ships with the BMAD Method installer — no install command is pinned in this plugin; install it in this repo and re-run." |
| A design plugin | "No design plugin is installed. Browse `/plugin marketplace` for a design-system or UI plugin, install one, and re-run." |

Say each **once**, in the closeout, as a next step — not as a warning per feature. The flow-review
line is the one worth surfacing first: it is the only absence that removes a whole stage.

## § The built-in method, in one page

This is what stages 2–4 already do; written out here so a reader can see it as one method.

```text
1  PAIN POINTS   read each feature's unresolved PP-### rows, in the client's own words. They are
                 what the FLOWS have to fix, and what shapes emphasis, ordering, and nav placement.
                 They never create a screen, a field, or a capability (ground 1b).

2  STRUCTURE     walk each UC's ## 2 in order.
                 same actor + same place, consecutively   → one screen
                 different place or task                  → a new screen
                 system-only step                         → not a screen
                 validation                               → a state
                 exception flow                           → a named error state
                 then merge screens two UCs both land on — ONLY where the actors' scope agrees.
                 on MOBILE the same steps need MORE, SMALLER surfaces (`3-screens.md` Part 2).

3  SCREEN TYPE   pick the plainest type the step needs, and reuse a sibling feature's version of it.
                 The catalog is per PLATFORM — a type from the other platform's list builds a shell
                 this one does not have:

                 web     many records, filterable    → list / table
                         one record, read-mostly     → detail
                         the actor supplies data     → form (a wizard only when the UC itself
                                                        splits the input across steps)
                         the actor decides yes/no    → review + disposition
                         the flow ends               → confirmation

                 mobile  many records, scanned       → feed / list (detail behind a tap)
                         one record, read-mostly     → detail
                         the actor supplies data     → form-sheet (a long form becomes stepped
                                                        sheets, named in order)
                         a destination from the      → tab root (one of at most 5)
                           tab bar
                         a multi-step input the UC   → full-screen wizard step, one per step
                           itself splits

                 both    ONE inventory, both catalogs: the same user goal picks a web type AND a
                         mobile type, never two screens

                 A type nothing in the flow calls for is a screen nobody asked for.

4  ELEMENTS      fields come from the EN-### entity: its names, types, required flags, and enum
                 values as the dropdown's real options.
                 actions come from the step's verbs.
                 copy is real words, in the client's language.

5  ROLES         one semantic role per element, from the closed list, or blank — and blank is the
                 common case. `primary action` exactly once per screen. NEVER a colour, a size, a
                 font, or a token id: there is no design system here to resolve one against, and a
                 renderer given an unresolvable name picks its own value.

6  STATES        empty · loading · validation-error · permission-denied · failure · success, each
                 traced to a BR, an exception flow, an entity constraint, or a post-condition.

7  NAVIGATION    only a screen the actor opens directly from a menu gets a nav-map entry — a
                 detail, wizard step, or modal reached through another screen does not.
                 web     the tree already in {nav_map_file}, any depth
                 mobile  a TAB BAR: at most 5 top-level entries; a 6th candidate is an Open
                         Question (owner: team), never a silent 6th row
                 both    one line per shell — two shells are two trees, so the same feature is
                         legitimately named twice

8  FLOWS         one per user goal, per actor: Entry · Path · Success · Failures · Resolves ·
                 Steps to goal. Every open PP-### is named by a flow or turned into a question.
                 A flow that resolves neither a UC goal nor a pain point is invented (D6).

9  GROUND OR ASK every decision cites a requirement, a pain point (for shape only), an existing
                 vault pattern, or a stated preference. None of those → an Open Question. This is
                 the line between a design decision and an invented requirement.
```

## Failure modes

- **Letting the method choose the output paths.** Half the design lands somewhere nothing reads, and
  the run still reports success.
- **Halting because a method, pattern skill, or review skill is missing.** The built-in method exists
  precisely so a run never dead-ends; a halt over one turns a working design stage into a blocked one.
- **Running Stage 4 with no review skill installed.** The gate is the point. A `### Flow Review` table
  written without a method records that every journey was walked and found sound when nobody walked
  one — and `sound` is the strongest claim this pipeline makes about a flow.
- **Leaving an empty `### Flow Review` table on a skip.** The same false claim with a heading on it.
  Write no table.
- **Running PFD's solve or analyze mode.** Both generate output from the 5-layer stack alone, with no
  UC, BR, entity, or pain point involved — the exact ungrounded design call Stage 3 exists to catch,
  wearing a psychology citation. Only Mode 1 belongs here.
- **Answering PFD's colour-count or typeface-count flags.** There is no palette and no type scale in
  this pipeline for them to bound. A run that "fixes" one has just invented the design system this
  skill exists not to produce.
- **Running the 5 layers screen by screen and stopping.** The screens are the easy half. Cognitive
  load across a journey, and one control called two names at two steps, are invisible to a per-screen
  pass — and they are what makes a flow feel wrong to a client who cannot say why.
- **Letting WDS Phase 7 fire, or importing Figma's tokens into the vault.** Both produce a design
  system this pipeline does not hold: Phase 7 invents one, and a Figma import mirrors the client's
  real one into a copy that is stale the first time they change it and authoritative-looking forever.
- **Re-running WDS's Phase 1–2 elicitation because the module ships it.** The UC's `## 1` and the
  hub's `## Pain Points` already are the strategic input Freya normally gathers first; re-eliciting
  risks a persona or framing that contradicts the record.
- **Waiting for WDS's "approve" checkpoint.** This skill never pauses for a human and has no halt of
  any kind. An ungrounded call becomes an Open Question, not a paused conversation.
- **Promoting an external pattern to ground 2a.** The one loophole wide enough to fit a whole screen
  through, and it closes on a distinction a hurried run will not make: 2a is *this vault*, 2b is
  *somewhere else*.
- **Repeating an install suggestion per feature.** Once, in the closeout, as a next step.
