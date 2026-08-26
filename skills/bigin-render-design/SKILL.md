---
name: bigin-render-design
description: This skill should be used when the user asks to "render the design", "render the prototype", "build the prototype", "make me a clickable prototype", "run open design", "render this with open design", "render it with frontend-design", "turn the UX spec into screens I can show the client", "prototype UX-###", "package this as a single-page app", "build one unified prototype across these roles", "give me one file for Netlify", or names a design engine to run against a finished UX spec. Renders one or more already-written UX specs into prototype artifacts on the engine the human chooses — including, when explicitly asked, a single self-contained SPA build spanning several specs — never re-designing, never touching a requirement, and recording only pointers to what it produced.
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

**It designs nothing.** Every screen, state, field, and word it renders was decided by
`/bigin-generate-design` and verified by that skill's Stage 4. An engine that adds a screen, invents
copy, or picks its own colour has produced a different product — one that reaches a client looking
exactly as specified as the real thing.

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
| `{ux_dir}` | `04-UIUX/UX-<NNN> <Feature>.md` | **the input.** The only file this skill writes, and only its `## 8` + `rendered:` |
| `{design_system_dir}` | `04-UIUX/_design-system/` | `design-tokens.md` + `components/` + `navigation-map.md` — **read-only here** |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | **read-only** — client-stated preferences, and they outrank any engine's taste |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | read `uiux:` to find a slug's spec. **Not written** — a render changes no requirement bookkeeping |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | **never read, never written.** The spec already absorbed them; re-reading them here is how a render starts re-designing |

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
1  resolve   which spec(s), which engine, which platform        (§ Stage 1)
2  check     is that engine installed? absent → HALT            [references/design-engines.md]
3  read      the spec, the design system, the nav ## Structure   (§ Stage 3)
4  render    map the spec onto the engine's inputs, iterate      [references/design-engines.md]
5  verify    what came back IS what the spec says                (§ Stage 5)
6  record    append ## 8, flip rendered:, changelog, report      (§ Stage 6)
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

## Stage 3 — Read the spec, and only the spec

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

Read nothing from `01-Requirements/_ucs/`, `_brs/`, or `_entities/`. Everything the render needs was
absorbed into the spec, and a render that opens a UC has started designing.

**On a unified build, read every named spec in full before rendering anything.** Each one's ## 1 Actor
& Scope table and ## 4 Flows are what the SPA delivery mode's persona switcher and any cross-spec
handoff are allowed to draw on (§ SPA Delivery Mode) — read them once, up front, the same way a
single-spec render reads its one spec before Stage 4 starts.

## Stage 4 — Render

The per-engine brief→input mapping, the iteration shape for an engine that renders one screen per
call, and each engine's own "NEVER let it" list are all in `references/design-engines.md`. Follow that
file and improvise nothing.

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
                       write into 04-UIUX/ or 01-Requirements/          → artifacts land in the
                                                                         engine's own place
                       pull a spec into a unified build nobody named    → Stage 1's rule for a single
                                                                         target, applied to several at
                                                                         once: deliberate, not inferred
```

## Stage 5 — Verify the render against the spec

The engine is an external tool with its own opinions, so what came back is checked before it is
recorded. Per rendered screen:

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
stale:     this render is against v<x>; the spec is at v<y> — <N> screen(s) changed since | current
open:      <N> unanswered question(s) on this spec, carried into the review: <the question>
next:      show it · re-render after /bigin-generate-design updates the spec ·
           requirement gaps → /bigin-transform-signal
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

## Model

Session default. Mapping a spec onto an engine's inputs and checking what came back against the spec
is judgment work — the same reason `/bigin-generate-design`'s workers do not run on `haiku`.

## Additional resources

- **`references/design-engines.md`** — the adapter, and the only place an engine has a name: the
  engine catalog with each one's install-check probe and exact install command, which engine is each
  platform's *default* (and why a default is never a constraint), the halt text, the spec→input
  mapping and iteration shape per engine, each engine's own "NEVER let it" list, why
  `design_engine_required: false` is retired, and what swapping or adding an engine touches. Also
  documents OpenDesign's SPA Delivery Mode — the unified, multi-spec, single-file build and its own
  design-system halt. Read at Stage 2 and again at Stage 4.
