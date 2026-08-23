# Design engines — the adapter

Read at Stage 1 (the precondition check) and again at Stage 4 (the render step), by the
**orchestrator** only. A worker never resolves an engine — it is *told* which one is in play.

```text
our skill      composes the BRIEF        UC + entity + pain point + client design preference
                                          → screens, tokens, nav, states, real copy
the ENGINE     renders the ARTIFACT      the actual clickable/visual prototype
the PROMPTS    are the durable record    self-contained, tool-portable, outlive any engine
```

**This file is the whole seam.** Swapping an engine — a better mobile renderer ships, the web one is
deprecated, a client mandates their own tool — is an edit to *this file only*. No stage guide names an
engine; every one of them says "the platform's design engine" and resolves it here. Keep it that way:
a stage guide that hardcodes `open-design` is the thing that makes the next swap expensive.

## Engine per platform

`platform:` comes from `_bigin/system/project.md` (absent → `web`; see
`{design_conventions}` § Platform).

| `platform:` | Required engine | Role |
|---|---|---|
| `web` | **`frontend-design`** (Anthropic, first-party, `claude-plugins-official`) | quality layer active *while* the Claude-design prototype HTML is generated — it shapes the aesthetic, it does not render on its own |
| `mobile` | **OpenDesign** (`nexu-io/open-design`, Apache-2.0) | device-framed HTML screen mockups from our brief, via its `mobile-app` design template |
| `both` | **both of the above** | web screens through one, phone screens through the other |

Figma Make prompts are authored by us in every mode — Figma Make previews mobile natively at
390×844, so there is no second tool to reach for (`{design_conventions}` § Prototype prompt).

## Required means required — this stage halts

```text
platform's engine present  → Stage 1 continues
platform's engine ABSENT   → HALT before Stage 1's work-list. Report the install command.
                             Design nothing. Stamp nothing.
```

This is the **one** sanctioned halt in an otherwise headless skill. The reasoning: the engine is what
turns a spec into something a client can actually look at, and a run that quietly skipped rendering
reports a finished design that has no prototype behind it — the most expensive kind of clean-looking
failure this pipeline can produce. Better to stop with an install command than to succeed on paper.

```text
HALTED: /bigin-generate-design needs a design engine for platform `<web|mobile|both>`.

missing: <engine name>
install: <the exact command from the section below>
then:    re-run /bigin-generate-design

Nothing was designed, no UX spec was created or updated, no absorbed: was stamped.
```

**Report the install command from this file verbatim, and improvise nothing** — the same discipline
`/bigin-new-project` § 7.3 applies to MCP installs. A guessed installer either fails noisily or
installs the wrong thing.

**The recorded opt-out.** A project that deliberately runs without an engine — an offline machine, a
client who forbids third-party tooling, a BA who only ever wants the prompt blocks — sets it in
`.claude/bigin-ba-workflow-plugin.local.md`, the one file that legitimately overrides plugin
behaviour:

```markdown
## Design engine
design_engine_required: false   # run the built-in method; prompt blocks are the deliverable
```

With that set, Stage 1 reports the engine as `skipped — waived in project settings`, Stage 4 skips
its render step, and the run completes on the built-in method. This is an explicit, recorded decision
in a file a human wrote — never a silent fallback the run chose for itself when an install failed.

---

## `frontend-design` — the web engine

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

**Mapping our brief onto it.** It expects a *design brief* in prose, which is exactly what Stage 3
already produced. Hand it these, and nothing else:

| Our material | Goes in as |
|---|---|
| `## 1 Design Brief` — actors, the **Actor & Scope** table, principles applied, directives applied | the brief's subject, audience, and "the page's single job". The scope table is what makes the audience specific: an engine told "a member record screen" renders one, told "a member seeing their own record, and separately an administrator searching all ~10,000" renders the two the spec actually has |
| `## 2`'s `Volume` column + `## 3`'s `Scope` line | **the scale to render at.** A screen at `many` is rendered full — the real number named, the find controls present, the empty and loaded-at-scale states drawn. An engine given no scale renders three placeholder rows and the client reviews a table that does not exist |
| `{design_principles_file}` active rows | **the pinned visual direction.** Its own rule: "where the brief pins down a visual direction, follow it exactly — the brief's own words always win." A client-stated preference is ground 3 and outranks its aesthetic instincts, always |
| `{tokens_file}` existing token names + values | the token system it would otherwise invent. Existing tokens are **fixed input**, never a starting suggestion — D1 |
| `## 2 Screen Inventory` + `## 3` regions/elements/copy | the structure and the real content to build with |
| `## 3` States + `## 4` Flows | the behaviour and the states the HTML must actually reach |
| pain-point rows behind a state | why an empty/error state matters, so it gets designed rather than stubbed |

**What comes back:** a stronger Claude-design prototype — better typography, a real point of view,
fewer template defaults. Fold its token *naming* discipline into Stage 4's block; fold nothing else.

```text
NEVER let it     invent a screen, a field, or a state         → ground 2b only (§ Grounding)
                 override a DESIGN-PRINCIPLES row             → ground 3 always wins
                 rename or replace an existing token          → D1, append-only
                 re-pin the subject when the brief pins it     → our brief IS the pinned brief
```

Its "if the brief does not pin down what the product is, pin it yourself" instruction is the one to
watch: our brief always pins it. A run that lets the engine re-invent the subject has designed a
different product.

---

## OpenDesign — the mobile engine

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

**Mapping our brief onto it.**

| Our material | Goes in as |
|---|---|
| `## 1 Design Brief` + `## 2 Screen Inventory` | the brief it renders from, one screen at a time |
| `{tokens_file}` values + `{design_principles_file}` active rows | a `DESIGN.md` design-system package. **Prefer generating one from our tokens over selecting from its 151 shipped systems** — a shipped system is somebody else's brand, and picking one silently overrides the client's stated preferences (ground 3) |
| `## 3` regions (`header / content / tab-bar / sheet / fab`) | the screen's structure inside the device frame |
| `## 3` elements — copy, entity fields, enum values | the real content. Never `Lorem`, never invented fields |
| `## 3` States | one rendered variant per state, not just the happy path |
| `{nav_map_file}` `## Structure — Mobile` | the tab bar, built once and shared across screens |
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

**What comes back:** device-framed HTML per screen, exportable to PDF. Record where the artifacts
landed in the Stage 5 report — the *files*, never their contents pasted into the spec.

```text
NEVER let it     pick a shipped DESIGN.md over the client's stated preferences   → ground 3 wins
                 add a screen the inventory does not carry                       → § Grounding
                 substitute placeholder copy for the real words                  → copy is content
                 write into 04-UIUX/ or 01-Requirements/                         → § Write map:
                                                                                   artifacts land in
                                                                                   its own project;
                                                                                   we record pointers
```

Its daemon is loopback-only and read-only by default — nothing here needs that relaxed, so don't.

---

## Swapping an engine

Everything a swap touches is above this line. To replace one:

```text
1  rewrite that platform's row in § Engine per platform
2  rewrite its section: install-check, install command, brief→input mapping, expected output,
   and its own "NEVER let it" list
3  change NOTHING in _bigin/stages/design/ or design-conventions.md — they name no engine
4  say so in the plugin changelog; an engine change alters what a client sees, so it is not a
   silent refactor
```

If a swap ever seems to require editing a stage guide, that is the signal a stage guide leaked an
engine detail it should have delegated here — fix the leak rather than accepting the coupling.

## Relationship to `engine-detection.md`

Two different questions, deliberately kept apart:

```text
design-engines.md    (this file)  WHICH engine is REQUIRED for this platform, and the halt if absent
engine-detection.md               WHICH optional METHOD/quality layer is available to run it with —
                                  BMAD WDS, Figma MCP, the built-in method, plus the quality boosters
                                  (agentic-UX, design-library), the per-step `designer-skills`
                                  pattern references, and the Stage 3.5 craft-quality pass
```

A required engine and an optional method compose: the mobile engine renders phone screens while
`engine-detection.md`'s built-in method (or WDS's, when present) is what decided *what those screens
are*. Neither replaces the other, and only the required engine can halt a run.

## Failure modes

- **Hardcoding an engine name into a stage guide.** The one thing this file exists to prevent. The
  next swap then means finding every stage that mentioned it, and the one that gets missed keeps
  calling a tool nobody has installed.
- **Falling back silently when the required engine is missing.** The run reports a finished design
  with no prototype behind it. Halt, or be waived explicitly in project settings — never a third path
  the run picked on its own.
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
