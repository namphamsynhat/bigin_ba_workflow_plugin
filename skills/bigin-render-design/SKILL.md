---
name: bigin-render-design
description: This skill should be used when the user asks to "render the design", "render the prototype", "build the prototype", "make me a clickable prototype", "run open design", "render this with open design", "render it with frontend-design", "turn the UX spec into screens I can show the client", "prototype UX-###", "package this as a single-page app", "build one unified prototype across these roles", "give me one file for Netlify", "make it look like real production software", "make the prototype high-fidelity", "the prototype has UC ids all over it", or names a design engine to run against a finished UX spec. Renders one or more already-written UX specs into enterprise-grade prototype artifacts on the engine the human chooses — through a three-role subagent pipeline (extract the data model, design the UI, lint and sanitize it), with navigation built verbatim from the canonical navigation map and every requirement id confined to `data-*` attributes — including, when explicitly asked, a single self-contained SPA build spanning several specs. Never re-designs, never writes a requirement, and records only pointers to what it produced.
argument-hint: "[engine] [feature slug | UX-###, or several for a unified SPA build] [design system]"
disable-model-invocation: true
---

# Bigin Render Design

The **render** step, split out of `/bigin-generate-design` on purpose. It takes a UX spec that already
exists and turns it into something a client can look at:

```text
in    UX-### <Feature>.md    the screens, states, real copy, flows, the ## 4 Coverage table, and the
                             self-contained prototype prompt blocks — one spec, or several when the
                             human explicitly asks for a unified build spanning them
    + _design-system/        token names AND values, components, this platform's nav ## Structure
    + the ENGINE             the human's choice — a named argument, or the project platform's default

out   artifacts              whatever the engine produced, in the engine's own output location —
                             including, when asked, a single self-contained SPA spanning every named
                             spec (OpenDesign only — see references/design-engines.md § SPA Delivery
                             Mode)
    + ## 8 Rendered Artifacts  one appended row per render: date, engine, platform, screens, path,
                               and the UX-###@version it rendered AGAINST — on a unified build, the
                               SAME row is appended to EVERY participating spec
    + rendered: true           in the spec's frontmatter
```

**It designs nothing.** Every screen, state, field, and **label** it renders was decided by
`/bigin-generate-design` and verified by that skill's Stage 4. An engine that adds a screen, invents
copy, or picks its own colour has produced a different product — one that reaches a client looking
exactly as specified as the real thing.

**The one thing a render does author is the sample dataset** — the record *values* filling a table or
a form, generated from the extracted field types, formats, and enums (§ Stage 4). That is not a design
decision and it is not copy: every *label* is the spec's, and the values exist because a table of ten
thousand real-looking rows is what makes the screen reviewable at all. A dataset that invents a
**field**, a **status**, or a **capability** has crossed back into designing.

**It halts, deliberately, when the chosen engine is absent.** A human just asked for a prototype; the
only useful answer is the install command. Nothing is lost by stopping — the spec, the blocks, and the
coverage table were all written by a design run that needed no tool at all.

## Why this is its own skill

The halt used to live at the *front of the design run*: a required engine per platform, checked before
a single screen was designed, stopping a stage that reads use cases and writes markdown because a
prototype renderer was missing. Three things were wrong with that.

```text
the engine was bound to the platform    one engine for web, one for mobile, no choice. A BA who
                                        wanted the other one could not have it
a missing tool stopped requirements     work that needed no tool at all halted for one, on an
                                        unattended pipeline that was safe to run otherwise
renders happened on the pipeline's      features nobody had asked about got rendered; the feature
  schedule, not a person's              somebody was about to show a client waited for its turn
```

Which tool, which feature, which platform, and when are timing-and-taste decisions belonging to
whoever is going to sit with the client. So they belong to a command that person runs.

**What replaced the halt as the safeguard** is `/bigin-generate-design`'s Stage 4 (`4-verify.md`): the
design run proves the spec is complete enough to render *cold*, on any engine, months later — real
copy, every state named, every token carrying a value, a resolvable nav shell, a `many` screen's real
scale, a phone screen's device facts. A spec that passes that is one a render cannot go wrong on for
want of input.

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | the design rulebook — § Rendering is a separate step, § Write map, § Grounding, § Platform |
| `{ux_dir}` | `04-UIUX/` | **the input**, one `UX-<NNN> <Feature>.md` per feature. The only file this skill writes, and only its `## 8` + `rendered:` |
| `{design_system_dir}` | `04-UIUX/_design-system/` | **read-only here**, and the three files below live in it |
| `{tokens_file}` | `04-UIUX/_design-system/design-tokens.md` | token names AND values — **read-only** |
| `{components_dir}` | `04-UIUX/_design-system/components/` | **read-only** |
| `{nav_map_file}` | `04-UIUX/_design-system/navigation-map.md` | **the single source of truth for navigation** (§ Stage 4 rule B) — read-only |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | **read-only** — client-stated preferences, and they outrank any engine's taste |
| `{hub_dir}` | `01-Requirements/_features/` | read `<slug>.md`'s `uiux:` to find a slug's spec. **Not written** — a render changes no requirement bookkeeping |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | **read-only, by Stage 4a alone.** The entity register — field lists, types, enum values, cardinalities |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | **read-only, by Stage 4a alone, for DATA ONLY** — predicates, field types, state keys, real volume numbers, filtered by the spec's own screen inventory. **Never written.** No other stage and no other agent opens them: the agent that designs the UI never sees a requirement file, which is what keeps a render from re-designing (§ Stage 4) |

Missing `_bigin/conventions/` → stop and say `/bigin-new-project` must run first. Then
`_bigin/conventions/conventions.md` § Workspace version check, as every skill does: behind → warn and
recommend `/bigin-upgrade-project`; ahead → stop.

## Write map — narrower than any other skill in this plugin

```text
WRITE   the spec's ## 8 Rendered Artifacts    ONE APPENDED ROW per render. Never edits a prior row —
                                              the history is what makes a stale render visible
        the spec's rendered:                  false → true
        the spec's ## Changelog               one line

NEVER   ## 1-## 7 of the spec        the design. Not a screen, not a state, not a word of copy
        the prompt blocks            the record of what was specified, not of what a render made of it
        {design_system_dir}          a token an engine wanted is a /bigin-generate-design question
        anything in 01-Requirements/ including the hub. A render is not a requirement event
        the spec's status:           human-only, and a render is not a review (D5)
        the spec's absorbed:         staleness is about UCs and screens, not about renders
```

**A unified SPA build spanning several specs writes the same ## 8 row to every participating spec.**
One combined artifact, one date, one engine — but each spec named in that build is a spec whose own
history should show it shipped as part of it, so the row lands on all of them, not just the one named
first. Nothing else about the write map changes: still one ## 8 row per spec per render, still never a
prior row edited.

A token or component an engine wants and cannot find is **not** something to add here. It is a gap in
the spec, and the spec is `/bigin-generate-design`'s: report it and stop rendering that screen.

## Execution order

```text
1  resolve   which spec(s), which engine, which platform          (§ Stage 1)
2  check     is that engine installed? absent → HALT              [references/design-engines.md]
3  read      the spec, the design system, the nav ## Structure,      (§ Stage 3)
             DESIGN-PRINCIPLES active rows
4  render    the THREE-ROLE PIPELINE                               (§ Stage 4)
             4a extract   UCs · BRs · ENTITIES.md → a Data Model & Logic Spec
             4b design    spec + data model + nav map → enterprise-grade artifacts
             4c lint      leak scan · tokens · contrast · density · IA · states · scale
5  verify    what came back IS what the spec says                  (§ Stage 5)
6  record    append ## 8, flip rendered:, changelog, report        (§ Stage 6)
```

## Stage 1 — Resolve the spec, the engine, and the platform

```text
$ARGUMENTS may carry, in any order:
    an ENGINE name        `frontend-design` | `open-design` | any engine references/design-engines.md
                          documents
    a TARGET              a feature slug (→ its hub's uiux:), or a UX-### directly

target omitted   → list every {ux_dir} spec with its status, platform, and whether ## 8 shows a
                   render against its CURRENT version, and ask which. NEVER render everything: a
                   render is a deliberate act, and "all of them" is how a client gets shown a feature
                   nobody had reviewed
engine omitted   → the project platform's DEFAULT from the adapter, announced AS DEFAULTED
platform         → the SPEC'S OWN `platform:`, not the project config. A per-feature override was
                   already resolved when the screens were written, and the spec is the record of it
```

**On a `both` spec, render one platform per invocation and say which.** Rendering "both" in one call
means two engines, two sets of artifacts, and one report — and the platform whose render came back
thinner is the one nobody notices. Ask which, or render the named one and report the other as
un-rendered.

**A unified build spanning several specs is only ever a deliberate request.** The human names every
spec it spans, in the same message that asks for them combined — "these three, as one prototype",
never "everything" and never inferred from, say, all specs sharing a status. This is the same
discipline as the target-omitted case above, applied to more than one target at once: naming nothing
lists and asks, naming several without asking to combine them renders them separately, one spec at a
time, exactly as today. Only OpenDesign's SPA delivery mode can take more than one target — see
`references/design-engines.md` § SPA Delivery Mode for the design-system argument it also takes.

**A spec at `status: needs-clarification` renders, with its open questions named in the report.** Its
screens are real and its gaps are written down; refusing to render it would leave the one thing that
makes those gaps discussable — a prototype in front of a client — unavailable exactly when it is most
useful. Do not render *around* a gap: an unanswered question stays a question, and the screen it
concerns renders as the spec has it or not at all.

## Stage 2 — The engine check, and the halt

Resolve the chosen engine's install-check probe from `references/design-engines.md` and run it. Absent
→ **halt**, reporting that file's install command **verbatim** and naming the other engine as an
alternative. Render nothing, write no `## 8` row, touch no file.

**Never fall back to a different engine.** A human named a tool; quietly using another hands them a
prototype in an aesthetic they did not pick, and the `## 8` row is the only place it would show.

**Never honour `design_engine_required: false`.** That setting is retired (adapter § The retired
waiver) — here it would mean rendering nothing and reporting success.

**A unified SPA build also names a design system, and that halts the same way.** OpenDesign's SPA
delivery mode takes a design-system argument alongside the specs it spans; a name that is neither in
OpenDesign's own catalog nor the vault's own tokens halts exactly like an absent engine — nothing
rendered, no ## 8 row, on any participating spec. See `references/design-engines.md` § SPA Delivery
Mode for the halt text.

## Stage 3 — Read the spec and the design system, never the requirements

```text
{ux_dir}/UX-### …   ## 1 Design Brief incl. the Actor & Scope table · ## 2 Screen Inventory ·
                    ## 3 Screen Specs (regions, elements, real copy, States, Interactions) ·
                    ## 4 Flows + ### Coverage · ## 5 Design System Usage ·
                    ## 6 Open Questions (what NOT to treat as settled) ·
                    ## 7 Relationship Model, when relationship_model: modelled ·
                    the prompt block for this platform
{tokens_file}       every token ## 5 names, with its VALUE
{components_dir}    every component ## 5 names
{nav_map_file}      ## Structure for THIS platform — the shell, built once, shared across screens
{design_principles_file}   active rows. Ground 3, and it outranks any engine's aesthetic instinct
```

`### Coverage` is read for a reason: a row marked `out of scope` is a thing the engine must **not**
render, with the reason already written down. An engine that helpfully adds it back undoes a decision
somebody made.

**The prompt block is a fallback, not the pipeline's input.** It exists so a human can paste a spec
into Figma Make, or a render can happen cold months from now with no pipeline at all — that is what
`5-prompt.md` means by "what `/bigin-render-design` reads". When the pipeline runs, 4b renders from
`## 1`-`## 7` **directly**, because it can read them and they carry more. The block also cannot serve
as the pipeline's source for a second reason: D6 forbids any vault id in a prompt body, so a render
driven from the block alone could not emit a single `data-*` value. Read the block to confirm it agrees
with the spec; render from the spec.

**The requirement files are read at Stage 4a, by one agent, for data only** — never here, and
never by the agent that writes the UI. The spec is what says *what* the screens are; the extractor
supplies only the *data underneath* them (field types, validation predicates, enum vocabularies, state
keys, real volume numbers), filtered by this spec's own `## 2` and `## 3`. See § Stage 4.

**On a unified build, read every named spec in full before rendering anything.** Each one's ## 1 Actor
& Scope table and ## 4 Flows are what the SPA delivery mode's persona switcher and any cross-spec
handoff are allowed to draw on (§ SPA Delivery Mode) — read them once, up front, the same way a
single-spec render reads its one spec before Stage 4 starts.

## Stage 4 — Render, as three roles

One agent cannot hold a UC set, every BR behind it, every entity's field list, the spec, the design
system, the nav map, **and** a growing HTML artifact — and the part that gets thin when it runs out of
room is always the last screens and the fidelity checks. So the render runs as three roles with three
contracts, defined in `references/render-pipeline.md`:

**One naming scheme, used everywhere:** `4a` / `4b` / `4c`. Never "Part 1/2/3" and never a bare
"Stage 2" for the designer — this skill has real Stages 1-6, and a bare stage number inside a render
role points at the wrong one.

```text
4a  render-data-extractor    READ-ONLY over the requirement artifacts — the ONLY agent that opens a UC
    UCs · BRs · ENTITIES.md  →  field lists, predicates, enums, state keys, real volume numbers
                             →  a Data Model & Logic Spec, in the session scratchpad

4b  render-ui-designer       NEVER opens _ucs/ · _brs/ · _entities/ · ENTITIES.md
    + the UX spec · navigation-map.md · tokens · DESIGN-PRINCIPLES (which IS in
      01-Requirements/, and is ground 3 — the exclusion is the requirement ARTIFACTS, not the folder)
                             →  enterprise-grade artifacts, human-grade copy, ids in data-* only

4c  render-ui-linter         the gate — verifies, sanitizes narrowly, never designs
    leak scan /(UC|BR|EN|UX)-\d/ · token-only styling · contrast · density · IA vs the nav map ·
    states reachable · real scale · live routes      →  PASS | RE-RENDER | BLOCKED
```

**Run the pipeline as agents when it earns the dispatch**, and inline otherwise — the same threshold
discipline the design side uses:

```text
ALWAYS DISPATCH   a unified SPA build spanning 2+ specs  ·  a spec with 3+ screens, or citing 2+
                  entities. One extractor per spec; ONE designer even on a unified build (the shared
                  shell and persona switcher are one artifact); one linter per artifact set
INLINE            below that, play all three roles yourself, in this order, under these same
                  contracts. A one-screen render does not need three dispatches
```

Running inline is not a relaxation. The leak scan still runs, the fidelity bar still applies, and the
nav map is still the only source of navigation.

**Before dispatching, resolve the plugin's own paths and pass them in — every dispatch.** The two
references and the two scripts live in the plugin, not the vault, and `${CLAUDE_PLUGIN_ROOT}` **only
resolves in the orchestrator**: a subagent that tries it gets a literal string and reads nothing. So
resolve them here, to absolute paths, and put them in each agent's prompt:

```text
4a needs   render-pipeline.md
4b needs   render-pipeline.md · enterprise-fidelity.md · design-engines.md ·
           scan-traceability-leaks.sh
4c needs   render-pipeline.md · enterprise-fidelity.md · scan-traceability-leaks.sh ·
           check-contrast.py
```

An agent told to read a rulebook it cannot reach does not stop — it reconstructs the checklist from
memory and passes everything. Each agent is instructed to halt on a missing path for exactly that
reason; supplying the paths is what makes that instruction unnecessary.

Also pass, per dispatch — and this list is exhaustive, because each agent halts on a missing input
rather than guessing one:

```text
ALL THREE   the spec path(s) · the resolved PLATFORM · the ENGINE (proven installed at Stage 2; no
            agent re-checks it and none may fall back)
4a ALSO     the scratchpad path to write the Data Model & Logic Spec to · the spec's ## 2 Screen
            Inventory row list — that list IS the filter, so an agent that has to guess at it has
            no filter
4b ALSO     the Data Model & Logic Spec path · {tokens_file} · {components_dir} · {nav_map_file} ·
            {design_principles_file} · the artifact output location · on a SPA build, the named
            design-system package (or "the vault's own tokens")
4c ALSO     the artifact path(s) · the spec path(s) they came from · {nav_map_file} · {tokens_file} ·
            the Data Model & Logic Spec path (it resolves data-en/data-field values against it) ·
            4b's OWN REPORT, explicitly marked as a claim to verify rather than a finding
```

The per-engine brief→input mapping, the iteration shape for an engine that renders one screen per
call, and each engine's own "NEVER let it" list are all in `references/design-engines.md`. Follow that
file and improvise nothing about an engine's mechanics.

### The three rules the pipeline exists to enforce

**A · Traceability and visible copy are strictly separated.** A rendered screen carries its provenance
so it can be traced back, and carries none of it where a human can read it.

```text
GOES IN     data-ux · data-screen · data-uc · data-uc-step · data-br · data-en · data-field ·
            data-state · data-nav-id
NEVER IN    a text node · aria-label · title · alt · placeholder · value · an <option> body ·
            a table header · a legend · a tooltip · CSS content: · a user-visible URL fragment
```

`Pending approval (BR-014)` is the most common way a prototype announces itself as a document. Write
`<span class="badge" data-br="BR-014">Pending approval</span>`. `aria-label` and `title` are
**visible** — a screen reader speaks them, a browser renders them on hover — so they are not a
loophole. Full vocabulary in `references/render-pipeline.md` § The traceability contract;
`scripts/scan-traceability-leaks.sh` is the deterministic check.

**B · `navigation-map.md` is the single source of truth for navigation.** Not the spec, not the
engine's template, not what the screens seem to imply. Labels verbatim, dot-path `id` as the tree,
`Order` as sibling order, `Points to` as the route, `Role(s)` as visibility, a `retired` row never
rendered, a phone shell capped at five top-level entries. The shell is built **once** and is identical
on every screen. A nav item the render wants and the map does not carry is **reported, never added**:
it is a `/bigin-generate-design` gap. Full contract in `references/render-pipeline.md` § The
navigation contract.

**C · The roles stay split, and that is a safety property, not just a context budget.** The old rule
was "a render never opens a UC", because a render that reads requirements starts re-designing from
them. Splitting the roles keeps that rule exactly where it counts:

```text
ONE agent reads the requirements   mechanically, for data only, filtered by the spec's own ## 2/## 3
the agent that DESIGNS never does  so it still cannot re-design from a source it never sees
```

What makes 4a safe is not its restraint — it is the **filter**. Everything it finds lands in one of
three buckets, and only the first is ever rendered:

```text
USED     the spec names it, the data behind it was found        → the data model
UNUSED   found in an EN/BR, the spec names nothing for it       → reported. NEVER rendered
GAP      the spec names it, nothing supplies the data behind it → BLOCKING. Never filled, never
                                                                  invented — it is a spec hole
```

**A `GAP` does not contradict `4-verify`'s guarantee** (§ Why this is its own skill). That stage proves
the spec is sufficient **prose** input — real copy, every state named, enum values spelled out, a real
scale number. 4a converts that prose into machine-usable form, and the `GAP` bucket catches what
`4-verify` structurally cannot: **drift since it ran.** A field renamed on an entity, a BR rewritten,
an `EN-###` promoted with a different shape than the register carried when the screens were written. A
`GAP` on a freshly-verified spec is rare and worth reporting loudly; a `GAP` on a spec verified eight
months ago is the normal, expected finding, and catching it is most of why 4a exists.

### The fidelity bar

`references/enterprise-fidelity.md` — read in full by 4b before rendering, walked item-by-item by 4c —
is what makes the output read as shipped software rather than a wireframe with colour: token-only
styling, computed WCAG AA contrast, enterprise density, the always-present shell, realistic data at
the real scale, every named state actually reachable, production chrome, typography discipline,
restraint, and cross-screen consistency. Plus § The tells, which is what 4c greps for.

**That file raises the finish. It never widens the scope.** Where it and a `DESIGN-PRINCIPLES` row
disagree, the row wins: it is ground 3 and the file is ground 2b.

```text
NEVER let the engine   add a screen ## 2 does not carry                → an invented screen arrives
                                                                         looking designed, which is
                                                                         worse than an obvious guess
                       substitute placeholder copy for the real words   → copy is content, and real
                                                                         copy is how the words get
                                                                         found to be wrong
                       override a DESIGN-PRINCIPLES row with its taste  → the row is ground 3, an
                                                                         engine's aesthetic is 2b
                       rename, replace, or invent a token               → D1, and the values are in
                                                                         the spec already
                       seed a `many` list with three sample rows        → the spec names the real
                                                                         scale; that IS the review
                       add bulk select, export, or a saved view         → D8. If ## 3 does not carry
                                                                         it, the prompt block's
                                                                         "what NOT to build" does
                       promise a memory ## 7 does not carry             → D7, the most expensive
                                                                         thing a prototype can
                                                                         quietly agree to
                       print a UC/BR/EN/UX id into visible copy         → rule A. It reaches a client
                                                                         reading as a document, and
                                                                         it is the most common leak
                       invent a nav entry the map does not carry        → rule B. The map is the only
                                                                         source of navigation
                       write into 04-UIUX/ or 01-Requirements/          → artifacts land in the
                                                                         engine's own place
                       pull a spec into a unified build nobody named    → Stage 1's rule for a single
                                                                         target, applied to several at
                                                                         once: deliberate, not inferred
```

### The repair loop, and when it stops

`verdict: RE-RENDER` sends a finding list back to 4b, which re-renders the named screens only — then
the **full** scan runs again, because a fix that moved an id into `data-*` on one screen commonly left
it on three.

**Two round trips, then stop.** A finding surviving two designer→linter cycles is not a render problem
— it is a spec problem or an engine limitation. Report the screen un-rendered, with the finding, and
let a human decide. A third automated attempt produces a screen that satisfies the linter and nobody
else.

**The verdict is per screen; the artifact-level one is a roll-up.** 4c reports both — one
`screen verdict:` line per screen, plus an overall `verdict:`. Stage 6's `<N> of <N>` column and
Stage 5's per-screen check both read the per-screen line: an artifact-level `RE-RENDER` says nothing
about which screens are safe to record, and reading it as "none of them" throws away good renders while
reading it as "all of them" records a broken one.

**No `## 8` row is written for a screen that did not reach `PASS`.** A render where some screens passed
and some did not is recorded as `<passed> of <total>`, with the rest named on `un-rendered:`.

## Stage 5 — Verify the render against the spec

Stage 4c already ran the mechanical gate — the leak scan, the token scan, the computed contrast, the
density and IA checks. **This stage verifies the render against the SPEC**, which is a different
question and the one only the orchestrator can answer, because it is the only role holding both the
spec and the linter's verdict. Start by taking 4c's `verdict:` as a precondition, not as a conclusion:
anything short of `PASS` means those screens are un-rendered, whatever else checks out. Per rendered
screen:

```text
□ it is a screen ## 2 Screen Inventory names — and no screen ## 2 does not name was produced
□ every state ## 3 lists for it was rendered, not just the happy path
□ the copy is the spec's copy, word for word. No Lorem, no reworded label, no invented field
□ the tokens are the spec's values — no substituted colour, type scale, or spacing
□ the shell is this platform's shell, from {nav_map_file}: a web sidebar/nav tree, or a bottom tab
  bar of at most 5. Not the engine's improvised per-screen menu
□ a `many` screen is rendered AT the scale the spec names, with its find controls and its empty state
□ a mobile render honours the frame, safe areas, and tap targets, one primary action per screen
□ no bulk action, export, or saved view the spec does not carry
□ relationship_model: modelled → what is shown as remembered traces to a ## 7 row; nothing more
□ an `out of scope` Coverage row was NOT rendered
□ this screen's own `screen verdict:` from 4c is PASS — a RE-RENDER or BLOCKED screen is un-rendered
□ the extractor reported no unresolved `gaps:` for this screen — a screen rendered over a blocking
  gap has a field nobody can explain
```

**Two of 4c's checks are re-run here, deliberately**, and they are the only two:

```text
□ scan-traceability-leaks.sh exits clean over the artifacts
□ the shell matches {nav_map_file} ## Structure: every label verbatim, every dot-path nested as the
  map nests it, no retired row rendered, no menu entry the map does not carry
□ on a unified build: every route the assembled app can reach resolves inside the one runtime — no
  dead link out to a spec that was not part of this build
□ on a unified build: the persona/actor switcher offers only actors a participating spec's own ## 1
  names, and any cross-spec handoff traces to a ## 4 Flows row in one of the specs it spans
```

A mismatch is **not** repaired by editing the spec to match the render — the spec is the specification.
Re-render that screen with the input corrected, or report it un-rendered and say why. A render recorded
as complete while one screen came back wrong is the one failure this whole split was designed around.

## Stage 6 — Record and report

Append **one** row to the spec's `## 8 Rendered Artifacts` — never edit a prior row:

```text
| <today> | <engine> | <web|mobile> | <N> of <N> | <path / project id> | UX-###@<version> |
```

**The Engine cell carries the template, when the engine has one** — `open-design (mobile-app)`. The row
has six fixed columns and no template column, so a template recorded anywhere else is lost, and the
next person cannot tell which of a catalog's templates produced what they are looking at.

`Against` (the last column) is what makes staleness visible: a spec at v1.4 whose only render was
against v1.2 has screens nobody has ever looked at. Then `rendered: true`, one `## Changelog` line,
and:

**On a unified build, repeat this whole step once per participating spec.** Same path, same date, same
engine, in every one of them — each spec's `Against` column still names its OWN version, since the
specs a unified build spans rarely sit at the same version as each other.

```text
spec:      UX-### <Feature> — status <…>, platform <…>, version <…>
engine:    <name> (chosen | defaulted for platform <…>)
rendered:  <N> of <N> screen(s), <N> state(s) — artifacts at <path>
            (pointers only — nothing rendered was copied into the spec)
un-rendered: <screen> — <why>, or "none"
fidelity:  linter verdict PASS — leaks: clean · tokens: token-only · contrast: AA ·
           IA: matches navigation-map.md · states: <N> of <N> reachable · scale: at the real number
           <or: the items that did not pass, one line each, and which screens they cost>
repairs:   <N> designer→linter cycle(s) — <what the linter sent back>, or "none needed"
data gaps: <a field the spec shows that no entity carries> — reported, not filled (or "none")
design gaps: <a token, component, or nav entry the render needed and the spec/map does not carry>
           — reported, not invented (or "none")
blocked:   <a UC/BR/EN reference 4a could not resolve> — <why> (or "none"). Blocks the screens that
           depend on it, exactly as a data gap does
unused:    <N> entity field(s)/rule(s) found that the spec names nothing for — in the run transcript,
           not rendered and not recorded on the spec (or "none")
actors:    <the persona switcher's entries, on a unified build> | handoffs: <each one, and the ## 4
           Flows row it traces to> (or "n/a — single spec")
stale:     this render is against v<x>; the spec is at v<y> — <N> screen(s) changed since | current
open:      <N> unanswered question(s) on this spec, carried into the review: <the question>
next:      show it · re-render after /bigin-generate-design updates the spec ·
           design gaps (a token, a nav entry, a state) → /bigin-generate-design ·
           requirement gaps (a field nothing carries) → /bigin-transform-signal
```

## Failure modes

Each produces a prototype that looks right.

- **Re-designing during a render.** The engine wanted a screen, a field, or a state the spec has not
  got, and it got one. It reaches the client indistinguishable from the specified screens, and the
  spec — the thing everybody reviews against — never mentions it.
- **Falling back to another engine when the chosen one is missing.** The human picked a tool for a
  reason. A silent substitution shows up nowhere but the `## 8` row.
- **Editing the spec to match what came back.** The specification becomes a transcript of whatever the
  tool did, and the next render has nothing to be checked against.
- **Recording a render as complete with one screen wrong.** Every screen after it is reviewed on the
  assumption the set is right, and the wrong one is the one that ships.
- **Pasting rendered output into the spec.** The spec becomes a second, drifting copy of something the
  engine owns, stale the next time anything renders.
- **Editing an existing `## 8` row instead of appending.** The history is the mechanism: it is how
  anybody sees that the render everybody remembers was against a version that no longer exists.
- **Rendering every spec because no target was given.** A client gets shown a feature nobody had
  reviewed, in a session convened to look at a different one.
- **Rendering both platforms of a `both` spec in one call.** Two engines, two artifact sets, one
  report — and the thinner render is the one nobody notices.
- **Adding a token so the engine stops complaining.** The design system is append-only and it is
  `/bigin-generate-design`'s (D1). A token added here is one no screen spec cites and no future run
  expects.
- **Letting the engine's shipped design system win over `DESIGN-PRINCIPLES`.** An engine's aesthetic
  and its 151 shipped packages are ground 2b; a client-stated preference is ground 3, and 3 wins.
- **Rendering around an open question.** The gap is what a prototype is most useful for discussing.
  Render what the spec says and carry the question into the report; filling it in makes the prototype
  answer a question nobody asked it.
- **Assembling a unified build from specs nobody explicitly named for it.** The same failure as
  rendering every spec because no target was given (above), reached by a different door — a build that
  quietly pulls in "the related ones" shows a client a feature nobody asked to combine.
- **Inventing a persona-switch handoff neither participating spec's ## 1 or ## 4 describes.** It reads
  as a working cross-portal handshake in the prototype and traces to nothing in either spec.
- **Recording a unified build's ## 8 row on only one participating spec.** The others' render history
  then shows no render at all, and the next person to open one has no idea it shipped as part of
  anything.
- **A requirement id in visible copy.** `Pending approval (BR-014)`, a `UC-031` in an `aria-label`, an
  `EN-004` in a column header. The prototype stops reading as software and starts reading as a
  document about software — and it is the client, not the BA, who notices. Rule A exists because this
  is the most common leak there is, and `scripts/scan-traceability-leaks.sh` exists because catching
  it by reading is unreliable.
- **Letting the extractor's `## Unused` findings into the render.** An entity field the spec names no
  element for is not an oversight to helpfully fix — it is a decision somebody made, and rendering it
  re-designs the product from the data side, which is much harder to spot than re-designing it from
  the screen side.
- **Filling a `GAP` instead of reporting it.** The spec shows a field, no entity carries it, and
  somebody invents a type so the form validates. The prototype then validates a field that does not
  exist, and the review confirms behaviour nothing specifies.
- **The designer opening a UC "just to check something".** It is one read, it is always reasonable,
  and it puts the one agent that writes UI back in exactly the position the split was built to
  prevent. Everything it needs was extracted for it.
- **Building navigation from the screens instead of the map, or letting the shell differ between
  screens.** The screens imply a menu; the map *is* the menu — grounded, ordered, role-gated, shared
  with every other feature. Both failures are invisible screen by screen and obvious across the set.
- **Three sample rows on a screen the spec says holds ten thousand.** The client reviews a table that
  does not exist: no pagination, no sort under load, no truncation, no realistic value spread. The
  real scale *is* the review, which is why the spec was made to name a real number.
- **The linter fixing something a reviewer might have an opinion about.** Moving an id into `data-*`
  is invisible and safe. Rewording copy, adding a control, or changing a token value to make contrast
  pass is a redesign that turns the checklist green — worse than a failure, because it is silent.
- **Reporting `fidelity: all pass` without walking the checklist.** It reads exactly like a real pass,
  which is why Stage 5 checks that claim hardest.
- **A third repair cycle.** Two designer→linter round trips exhaust what automation can fix. Past
  that, the render converges on something that satisfies the linter and nobody else, and the real
  problem — a spec hole or an engine limitation — never reaches a human.

## Model

Session default, for the orchestrator and for all three pipeline agents (`model: inherit`). Mapping a
spec onto an engine's inputs, writing copy a person would have written, and judging density and
contrast are all judgment work — the same reason `/bigin-generate-design`'s workers do not run on
`haiku`. The linter looks mechanical and is not: the regex scan is, but "does this read as a finished
product" is the part that matters, and it is the part a cheaper model skips.

## Additional resources

### Reference files

- **`references/render-pipeline.md`** — the three-role contract: why the split exists and when it
  earns its dispatch, the exact shape of the Data Model & Logic Spec (and the USED/UNUSED/GAP filter
  that makes it safe), the full `data-*` traceability vocabulary with every position an id may not
  appear in, the navigation contract, and the handoff/repair loop. Read at Stage 4 by every role.
- **`references/enterprise-fidelity.md`** — the bar: ten items covering token-only styling, computed
  WCAG AA contrast, enterprise density, the always-present shell, realistic data at real scale,
  reachable states, production chrome, typography discipline, restraint, and cross-screen consistency
  — plus § The tells (what marks a prototype as a prototype) and § What this file may never be used to
  justify. Read in full by 4b before rendering, item-by-item by 4c.
- **`references/design-engines.md`** — the adapter, and the only place an engine has a name: the
  engine catalog with each one's install-check probe and exact install command, which engine is each
  platform's *default* (and why a default is never a constraint), the halt text, the spec→input
  mapping and iteration shape per engine, each engine's own "NEVER let it" list, why
  `design_engine_required: false` is retired, and what swapping or adding an engine touches. Also
  documents OpenDesign's SPA Delivery Mode — the unified, multi-spec, single-file build and its own
  design-system halt. Read at Stage 2 and again at Stage 4.

### Scripts

- **`scripts/scan-traceability-leaks.sh <path>…`** — rule A's deterministic gate. Scans rendered
  artifacts for `/(UC|BR|EN|UX)-\d/` in every visible position (text nodes, `aria-label`, `title`,
  `alt`, `placeholder`, `value`, `<option>` bodies, CSS `content:`), ignoring `data-*` where those ids
  belong. Exits `0` clean, `1` with each leak as `file:line | position | id | context`, `2` if it
  could not run. Run by 4b before reporting and by 4c as its first act.
- **`scripts/check-contrast.py`** — WCAG 2.1 ratios, computed. `<fg> <bg> …` for pairs,
  `--tokens <design-tokens.md>` to sweep every colour token against every surface token, or
  `--pairs <file>` for `name fg bg [large|ui]` lines. Exits non-zero on a failure. Contrast is a
  formula; a model asked to judge it by eye is wrong on exactly the muted-on-subtle pairings a dense
  enterprise screen is full of.

### Agents

- **`agents/render-data-extractor.md`** — Stage 4a. Read-only over `01-Requirements/`; the only agent
  in a render permitted to open a UC.
- **`agents/render-ui-designer.md`** — Stage 4b. Never opens `01-Requirements/`; inherits the full
  tool set because the engine may be an MCP server, a skill, or a CLI.
- **`agents/render-ui-linter.md`** — Stage 4c. Verifies, sanitizes narrowly, never designs.
