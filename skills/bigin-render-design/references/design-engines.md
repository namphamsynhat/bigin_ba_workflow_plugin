# Design engines — the adapter

Read by `/bigin-render-design`, and by nothing else. `/bigin-generate-design` no longer reads this
file at all: it renders nothing, so it needs no renderer and cannot halt for one.

```text
/bigin-generate-design   composes the SPEC          UC + entity + pain point + client design
                                                     preference → screens, tokens, nav, states, real
                                                     copy, and the self-contained prompt blocks
THIS skill + an ENGINE   renders the ARTIFACT       the actual clickable/visual prototype
the PROMPT BLOCKS        are the durable record     self-contained, tool-portable, outlive any engine
```

**This file governs the ENGINE only.** *How* a render is produced — the three-role subagent pipeline,
the `data-*` traceability contract, the navigation map as the single source of navigation, and the
enterprise-fidelity bar — is in `render-pipeline.md` and `enterprise-fidelity.md`, and applies to
**every** engine documented here. An engine's own "NEVER let it" list below is additional to those,
never instead of them.

**This file is the whole seam.** Swapping an engine — a better mobile renderer ships, the web one is
deprecated, a client mandates their own tool — is an edit to *this file only*. No design stage guide
names an engine; every one of them says "the render step" and stops there. Keep it that way: a stage
guide that hardcodes `open-design` is the thing that makes the next swap expensive.

## The engine is the human's choice; the platform only supplies a default

```text
/bigin-render-design [engine] [feature slug | UX-###]

engine named        → that engine renders, whatever the project's platform is. A BA who wants
                      OpenDesign for a web product, or `frontend-design` for a phone product, says so
                      and gets it. Record which engine ran in the spec's ## 8
engine omitted      → the DEFAULT for the project's platform, from the table below, announced as
                      defaulted so nobody mistakes it for a choice somebody made
```

A default is a convenience, never a constraint. The old design run bound one engine to each platform
and halted without it; that coupling is gone, and reinstating it — refusing OpenDesign on `web`,
say — takes the choice back off the person who is about to sit with the client.

| `platform:` | Default engine | Why it is the default there |
|---|---|---|
| `web` | **`frontend-design`** (Anthropic, first-party, `claude-plugins-official`) | quality layer active *while* the Claude-design prototype HTML is generated — it shapes the aesthetic, it does not render on its own |
| `mobile` | **OpenDesign** (`nexu-io/open-design`, Apache-2.0) | device-framed HTML screen mockups from the spec, via its `mobile-app` design template |
| `both` | **ask for one** — `both` has no single default | render one platform per invocation, naming the engine each time. A `both` project rendering "everything" silently is how one platform's screens go unreviewed |

`platform:` comes from `_bigin/system/project.md` (absent → `web`; see `{design_conventions}`
§ Platform), and on a per-feature override the **spec's own** `platform:` wins — it is the value that
feature's screens were actually written against.

Figma Make prompts are authored by `/bigin-generate-design` in every mode and need no engine here:
they are pasted into Figma Make by a human, which previews mobile natively at 390×844
(`{design_conventions}` § Prototype prompt).

## The chosen engine is required — this skill halts

```text
chosen engine present  → render
chosen engine ABSENT   → HALT. Report the install command from this file, VERBATIM. Render nothing,
                         write no ## 8 row, touch no spec
```

**This skill is allowed to halt, and it is the right place for the halt to live.** A human just asked
for a prototype; if the tool that makes one is not installed, the only useful answer is the install
command. Nothing is lost by stopping — the spec, the blocks, and the coverage table are all already
on disk, written by a design run that needed no tool at all.

That is the whole reason this step was split out. The halt used to sit at the *front of the design
run*, where it stopped a stage that reads use cases and writes markdown because a prototype renderer
was missing — a design nobody had asked to see yet, blocked on a tool nobody needed yet.

```text
HALTED: /bigin-render-design needs <engine name>, and it is not installed.

missing: <engine name>
install: <the exact command from the section below>
then:    re-run /bigin-render-design <engine> <slug>

or:      /bigin-render-design <the other engine> <slug>   — the choice is yours; the spec is
                                                             engine-neutral and either can render it

Nothing was rendered, no ## 8 row was written, no spec was touched.
```

**Report the install command from this file verbatim, and improvise nothing** — the same discipline
`/bigin-new-project` § 7.3 applies to MCP installs. A guessed installer either fails noisily or
installs the wrong thing.

**There is no waiver, and there is nothing to waive.** A project that never wants to render simply
never runs this skill: `/bigin-generate-design` completes on its own, and the prompt blocks are the
deliverable. The old `design_engine_required: false` setting existed only to stop a *design* run
halting for a *render* tool, and with the two separated it has nothing left to do — see
§ The retired waiver.

---

## `frontend-design` — the web default

**What it actually is.** A *guidance* skill, not a renderer: prose that shapes how UI gets built —
aesthetic direction, a compact token plan (4–6 named hex values, 2+ type roles, a layout concept, one
signature element), a brainstorm→plan→critique→build→critique loop, and an explicit anti-generic
calibration (it names the three looks AI design defaults to, so it can avoid them). It ships no tools.

So its role here is a **quality layer over the Claude-design block**, not a separate output path.

```text
install-check   is a skill named `frontend-design` in this session's available-skills list?
install         /plugin install frontend-design@claude-plugins-official
                (the official marketplace is configured by default; if not:
                 /plugin marketplace add anthropics/claude-plugins-official)
```

**Mapping the spec onto it.** It expects a *design brief* in prose, which is exactly what the UX spec
already is. Hand it these sections of `{ux_dir}/UX-<NNN> <Feature>.md`, and nothing else:

| Spec material | Goes in as |
|---|---|
| `## 1 Design Brief` — actors, the **Actor & Scope** table, principles applied, directives applied | the brief's subject, audience, and "the page's single job". The scope table is what makes the audience specific: an engine told "a member record screen" renders one, told "a member seeing their own record, and separately an administrator searching all ~10,000" renders the two the spec actually has |
| `## 2`'s `Volume` column + `## 3`'s `Scope` line | **the scale to render at.** A screen at `many` is rendered full — the real number named, the find controls present, the empty and loaded-at-scale states drawn. An engine given no scale renders three placeholder rows and the client reviews a table that does not exist |
| `{design_principles_file}` active rows | **the pinned visual direction.** Its own rule: "where the brief pins down a visual direction, follow it exactly — the brief's own words always win." A client-stated preference is ground 3 and outranks its aesthetic instincts, always |
| `{tokens_file}` existing token names + values | the token system it would otherwise invent. Existing tokens are **fixed input**, never a starting suggestion — D1 |
| `## 2 Screen Inventory` + `## 3` regions/elements/copy | the structure and the real content to build with |
| `## 3` States + `## 4` Flows | the behaviour and the states the HTML must actually reach |
| pain-point rows behind a state | why an empty/error state matters, so it gets designed rather than stubbed |

**What comes back:** a stronger Claude-design prototype — better typography, a real point of view,
fewer template defaults. Record it as a `## 8` pointer. Nothing it produces goes back into the spec's
prompt blocks: those are the record of what was specified, not of what a render happened to make of
it.

**Rendering a mobile spec with it is legitimate**, and it is one of the reasons the engine choice moved
to the human. Hand it the spec's mobile facts — the 390px frame, the bottom tab bar, safe-area insets,
44×44 tap targets — the same way any other input is handed over, and check the result actually honours
them. It has no phone frame of its own, so a spec that did not carry those facts gets a stretched
desktop layout; `4-verify` Part 5 is what made sure the spec carries them.

```text
NEVER let it     invent a screen, a field, or a state         → ground 2b only (§ Grounding)
                 override a DESIGN-PRINCIPLES row             → ground 3 always wins
                 rename or replace an existing token          → D1, append-only
                 re-pin the subject when the brief pins it     → the spec IS the pinned brief
                 write into 04-UIUX/ or 01-Requirements/      → § Write map. Only the ## 8 pointer
```

Its "if the brief does not pin down what the product is, pin it yourself" instruction is the one to
watch: the spec always pins it. A run that lets the engine re-invent the subject has rendered a
different product.

---

## OpenDesign — the mobile default

**What it actually is.** A local-first desktop app (macOS/Windows) plus an `od` CLI and a **stdio MCP
server**, Apache-2.0, at `github.com/nexu-io/open-design`. Its rendering-template catalog is what
matters here: `mobile-app` (mode `prototype`, scenario `design`) produces an **iPhone 15 Pro / Pixel
framed** app mockup. `mobile-onboarding` covers splash / value-prop / sign-in. It reads `DESIGN.md`
design-system packages for brand-consistent rendering, and exports HTML / PDF.

```text
install-check   an MCP server row matching `open-design` (case-insensitive substring) in
                `claude mcp list`, state ✔ Connected
                — plus, when the CLI is on PATH, `od project list --json` succeeding

install         od mcp install claude
                or:  curl -fsSL https://open-design.ai/install.sh | sh -s claude
                (install.sh is a thin wrapper around the same command)

the app itself  the desktop app ships via DMG / Homebrew cask; the MCP server comes with it
```

> **`od` name collision — check this before reporting a missing binary.** `/usr/bin/od` is the BSD
> octal-dump utility and wins on PATH on a stock macOS. So `command -v od` resolving proves *nothing*,
> and a bare `od mcp install claude` in a terminal may run the wrong program. Probe with
> `od project list --json` (octal-dump errors out; OpenDesign returns JSON), and on a macOS desktop
> install prefer the app's **Settings → MCP server** snippet over the bare command — the project's own
> README says so explicitly.

**Match the MCP server row by substring, case-insensitively, never by exact name** — same rule
`/bigin-new-project` § 7.1 applies to every provider, for the same reason.

**Rendering a WEB spec with it is legitimate.** Its catalog is not only phone templates — pick the one
that matches the spec's platform at run time, from the MCP server's own template listing or the desktop
app's template picker, and **record which template you used** in the `## 8` row. Do not guess a
template name out of this file: `mobile-app` and `mobile-onboarding` are the two verified here, and a
web render's template is whatever that catalog actually offers on the day. A wrong template name fails
noisily, which is the good case; the bad case is a template that renders something plausible in the
wrong shell.

**Mapping the spec onto it.**

| Spec material | Goes in as |
|---|---|
| `## 1 Design Brief` + `## 2 Screen Inventory` | the brief it renders from, one screen at a time |
| `{tokens_file}` values + `{design_principles_file}` active rows | a `DESIGN.md` design-system package. **Prefer generating one from the vault's own tokens over selecting from its 151 shipped systems** — a shipped system is somebody else's brand, and picking one silently overrides the client's stated preferences (ground 3) |
| `## 3` regions — mobile `header / content / tab-bar / sheet / fab`, web `header / nav / main / aside / footer` | the screen's structure inside the frame. Use the vocabulary the spec actually carries; it is the platform its screens were written for |
| `## 3` elements — copy, entity fields, enum values | the real content. Never `Lorem`, never invented fields |
| `## 3` States | one rendered variant per state, not just the happy path |
| `{nav_map_file}`'s `## Structure` for the spec's platform | the shell, built once and shared across screens — the mobile tab bar, or the web sidebar/nav tree on a web render |
| pain-point rows behind a state | which states are worth rendering properly |
| `## 7` Relationship Model, when `modelled` | what the app shows as remembered — a real variant, not static text (D7) |

**It renders one screen per artifact, so the wrapper iterates.** Loop the feature's screens, one
render call each, then read the results back:

```text
per screen in ## 2 Screen Inventory:
    render it via the `mobile-app` template, with that screen's spec + the shared tab bar
then:
    od project list --json                          find the project
    od files list <project-id> --json               find what it produced
    od files read <project-id> <relative-path>      read an artifact back
```

**What comes back:** framed HTML per screen, exportable to PDF. Record where the artifacts landed as a
`## 8` row — the *paths*, never their contents pasted into the spec.

```text
NEVER let it     pick a shipped DESIGN.md over the client's stated preferences   → ground 3 wins
                 add a screen the inventory does not carry                       → § Grounding
                 substitute placeholder copy for the real words                  → copy is content
                 write into 04-UIUX/ or 01-Requirements/                         → § Write map:
                                                                                   artifacts land in
                                                                                   its own project;
                                                                                   we record pointers
                 pick a template by guessing its name from this file              → read the catalog
```

Its daemon is loopback-only and read-only by default — nothing here needs that relaxed, so don't.

### SPA Delivery Mode — a unified build spanning several specs

A second OUTPUT mode on this same engine, for when the human asks to see several specs together as one
client-facing package — a cross-role walkthrough, a client-review link, a build meant for a static
host — rather than one spec's screens rendered on their own. **Never inferred.** Exactly like Stage 1's
single-target rule, a unified build is a deliberate request naming every spec it spans; "render
everything" is still not a thing this skill does, however many specs exist.

```text
trigger        the human names two or more specs (feature slugs or UX-### ids) AND asks for them
               combined — one build, one link, one file to hand over or deploy
architecture   one self-contained `index.html`: client-side routing, an embedded state manager, and
               CSS built from one design system's token VALUES — the whole thing runs with no server
               and no external stylesheet or script dependency
```

**The design system is named the same way the engine is — a human choice, never a default.** Point it
at `{tokens_file}` (the vault's own tokens — what this mode uses when nobody names another) or at a
package OpenDesign's own catalog actually carries. **Read the catalog to confirm a named package is
really there; never guess a name into existence** — the same discipline § Rendering a WEB spec with it
already applies to a template name.

```text
chosen system found (catalog, or the vault's own tokens)   → render
chosen system ABSENT from both                             → HALT. Render nothing, write no ## 8 row
                                                               on ANY participating spec, touch no spec
```

```text
HALTED: /bigin-render-design's SPA delivery mode needs a design system named "<name>", and it is
neither in OpenDesign's catalog nor this vault's own tokens.

available:  <what the catalog actually lists>  ·  or the vault's own tokens ({tokens_file})
then:       re-run naming one of those, or drop the design-system argument to use the vault's tokens

Nothing was rendered, no ## 8 row was written, no spec was touched.
```

**Mapping several specs onto one build.**

| Spec material (per participating spec) | Goes in as |
|---|---|
| `## 1 Design Brief` incl. the Actor & Scope table | one entry in the build's persona/actor set — see below |
| `## 2 Screen Inventory` + `## 3` regions/elements/copy/States | that spec's own routes inside the shared runtime, mapped the same way a single-spec render maps them (§ Mapping the spec onto it, above) |
| `## 4 Flows` + `### Coverage` | which routes this spec's screens actually link to, and which `out of scope` rows still must NOT appear |
| `{tokens_file}` values, or the named catalog package | the ONE shared token set every participating spec's screens render with — not each spec's own, if they differ |
| `{nav_map_file}`'s `## Structure` | the shell — built once, shared across every participating spec's screens, same as any other render |

**Zero broken links.** Every route the assembled app can reach — a screen, a modal, a toast, a
cross-cutting screen more than one participating spec's `## 2 Screen Inventory` names — resolves inside
the one runtime. A route pointing at a spec that was not named for this build is not a link; it is a
gap the build should never have offered.

**An actor-switch entry stage, when the participating specs name more than one actor.** If their `## 1`
Actor & Scope tables name different actors, the assembled build's entry stage lets a reviewer switch
between them, so a flow that hands off from one spec's actor to another's can be walked end to end.
**Only the actors and handoffs a participating spec's own `## 1` or `## 4 Flows` actually name** — a
handoff neither spec describes is an invented flow, the same failure § Grounding already names for an
invented screen.

**Static-host manifest files, when the engine can produce them.** Alongside `index.html`, files a
static host needs to serve it (a redirects file, a host config) may come back too — record them in the
same `## 8` pointer as any other artifact. They are OpenDesign's own output, the same as the framed
per-screen HTML above; § Write map still applies, and none of it is copied into `04-UIUX/`.

**Recording spans every participating spec.** One build, but every spec it renders gets its own `## 8`
row — same path, same date, same engine, each spec's own `Against` version — because a spec's render
history has to show it shipped as part of this build, not that it rendered alone (`/bigin-render-design`
§ Stage 6).

```text
NEVER let it     pull in a spec nobody named for this build                  → deliberate, not inferred
                 invent a persona-switch or handoff neither spec's ## 1 or
                 ## 4 describes                                              → § Grounding
                 pick a design system off its own shelf when the human
                 named the vault's tokens, or the reverse                    → ground 3, the human's
                                                                                 choice wins
                 leave a route the assembled app can reach dead-ending
                 outside the runtime                                         → the zero-broken-links
                                                                                 rule above
                 write into 04-UIUX/ or 01-Requirements/                     → § Write map: artifacts
                                                                                 land in its own project
```

---

## Swapping an engine

Everything a swap touches is above this line. To replace one:

```text
1  rewrite its row in § The engine is the human's choice (if it is a platform default)
2  rewrite its section: install-check, install command, spec→input mapping, expected output,
   and its own "NEVER let it" list
3  add a new engine by adding a section — it does not have to be any platform's default to be
   choosable. `/bigin-render-design <name>` reaches anything this file documents
4  change NOTHING in _bigin/stages/design/, design-conventions.md, or /bigin-generate-design —
   none of them names an engine, and the design side no longer reads this file at all
5  say so in the plugin changelog; an engine change alters what a client sees, so it is not a
   silent refactor
```

If a swap ever seems to require editing a stage guide, that is the signal a stage guide leaked an
engine detail it should have delegated here — fix the leak rather than accepting the coupling.

## The retired waiver

`.claude/bigin-ba-workflow-plugin.local.md`'s `design_engine_required: false` is **dead**, and a
project still carrying the line is not broken — the line simply has nothing to switch off. It existed
for exactly one purpose: to stop a *design* run halting for a *render* tool. Design runs no longer
check for a render tool, so there is nothing to waive.

The behaviour it used to buy is now the default: run `/bigin-generate-design` and stop. The prompt
blocks are the deliverable, and an offline machine or a client who forbids third-party tooling just
never invokes this skill. **Do not read that key, and do not honour it here** — a "waived" render
would mean rendering nothing while reporting success, which is the exact failure the old waiver was
carefully scoped to avoid.

## Relationship to `engine-detection.md`

Two different questions, in two different skills, deliberately kept apart:

```text
design-engines.md    (this file, /bigin-render-design)  WHICH engine RENDERS, chosen by the human,
                                                        and the halt when that engine is absent
engine-detection.md  (/bigin-generate-design)           WHICH optional METHOD/quality layer decided
                                                        WHAT THE SCREENS ARE — BMAD WDS, Figma MCP,
                                                        the built-in method, plus the quality
                                                        boosters (agentic-UX, design-library), the
                                                        per-step `designer-skills` references, and
                                                        the Stage 3.5 craft-quality pass
```

They **compose across the two skills**: the method layer decided what the screens are, weeks before an
engine here renders them. Neither replaces the other, and the method layer can halt nothing — its
absence is a silent skip, because the built-in method is complete.

## Failure modes

- **Hardcoding an engine name into a design stage guide.** The one thing this file exists to prevent.
  The next swap then means finding every stage that mentioned it, and the one that gets missed keeps
  calling a tool nobody has installed.
- **Falling back to another engine when the chosen one is missing.** A human named a tool; silently
  rendering on a different one hands them a prototype in an aesthetic they did not pick, and the
  `## 8` row is the only place it shows. Halt with the install command and name the alternative — the
  choice is theirs to make again, not yours to make for them.
- **Honouring `design_engine_required: false` here.** It would mean rendering nothing and reporting
  success — the failure the setting itself existed to prevent (§ The retired waiver).
- **Refusing an engine because it is not this platform's default.** The default is a convenience. A BA
  who asks for OpenDesign on a web project has made a choice, and taking it back off them is what
  splitting this step out was meant to stop.
- **Guessing an install command.** `/bigin-new-project` § 7.3's rule, verbatim: a wrong installer
  either fails noisily or installs something that is not the engine.
- **Letting an engine's own design system override the client's.** 151 shipped `DESIGN.md` packages
  and an aesthetic point of view are both ground **2b** — external patterns. A `DESIGN-PRINCIPLES`
  row is ground 3, and ground 3 wins every time (§ Grounding).
- **Treating `command -v od` as proof.** It resolves to the BSD octal-dump binary on a stock macOS.
  The probe is `od project list --json`.
- **Pasting rendered artifact contents into the UX spec.** The spec holds the *pointer* and the
  prompt blocks; generated HTML is an output, and copying it in makes the spec a second, drifting
  copy of something the engine owns.
- **Letting the engine choose the output paths.** Same failure `engine-detection.md` already names:
  half the design lands somewhere nothing reads and the run still reports success.
- **Rendering a SPA delivery mode build without a named design system.** Silently defaulting to one of
  OpenDesign's 151 shipped packages is the same ground-3-loses failure as any other engine picking its
  own aesthetic — halt and ask, or use the vault's own tokens explicitly.
- **Recording a unified build's `## 8` row on only one of the specs it spans.** The others' render
  history then shows no render at all, and the next person to open one has no idea it shipped as part
  of a combined build.
- **Letting a unified build's persona switcher invent a handoff neither participating spec describes.**
  It reads as a working cross-portal handshake in the prototype and traces to nothing any spec says.
