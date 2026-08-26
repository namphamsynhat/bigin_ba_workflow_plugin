# The render pipeline — three roles, three contracts

Read by `/bigin-render-design` at Stage 4, and by the three agents it dispatches. It defines **what
passes between them**, so that no stage has to guess what the previous one meant.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Part 1  render-data-extractor      READ-ONLY over 01-Requirements/       │
│         UCs · BRs · ENTITIES.md → field lists, predicates, enums,        │
│         state keys, real volume numbers                                  │
└───────────────────────────┬──────────────────────────────────────────────┘
                            │  Data Model & Logic Spec  (§ below)
┌───────────────────────────▼──────────────────────────────────────────────┐
│ Part 2  render-ui-designer         NEVER opens 01-Requirements/          │
│         + the UX spec · navigation-map.md · tokens · DESIGN-PRINCIPLES   │
│         → enterprise-grade HTML/CSS/JS, human-grade copy, data-* ids     │
└───────────────────────────┬──────────────────────────────────────────────┘
                            │  rendered artifacts + a manifest of paths
┌───────────────────────────▼──────────────────────────────────────────────┐
│ Part 3  render-ui-linter           gate — verifies, sanitizes narrowly    │
│         leak scan /(UC|BR|EN|UX)-\d/ · tokens · contrast · density ·      │
│         IA vs the nav map · states · real scale · routes                  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Why three roles and not one worker

Three separate reasons, and each on its own would be enough.

```text
CONTEXT      a UC set, every BR behind it, every entity's full field list, the UX spec, the design
             system, the nav map, AND a growing HTML artifact do not fit in one working context.
             A single worker that reads all of it runs out of room exactly when it starts writing
             the part that matters — the last screens — and those come back thinnest

SAFETY       the old rule was "a render never opens a UC", because a render that reads requirements
             starts re-designing from them. Splitting the roles KEEPS that rule where it counts:
             the agent that writes UI still never sees a UC. One agent reads them, mechanically,
             for data only, and hands forward facts rather than material to re-interpret

QUALITY      extracting a field list, writing product copy, and judging contrast and density are
             three different kinds of attention. A worker doing all three does the first well and
             the third barely at all — the fidelity checks are always what gets skipped when a
             context is full and a report is due
```

**When the pipeline is worth its dispatch cost** — the same threshold discipline `agent-dispatch.md`
already applies:

```text
ALWAYS       a unified SPA build spanning 2+ specs
             a spec with 3 or more screens, or citing 2 or more entities
INLINE       below that, the orchestrator plays all three roles itself, in this order, under these
             same contracts. A 1-screen render does not need three dispatches
```

Running the roles inline is not a relaxation. The leak scan still runs, the fidelity bar still
applies, and the nav map is still the only source of navigation.

---

## The Data Model & Logic Spec

Part 1's whole output. Written to the **session scratchpad**, never into the vault — the orchestrator
supplies the exact path in the dispatch (it is a session path, not a `{variable}` in `paths.md`, so
there is nothing to resolve and nothing to invent):

```text
<session scratchpad>/render/UX-<NNN>.datamodel.md
```

Disposable by design. It is not committed, not referenced from any `## 8` row, and not read by
anything after Part 3. It exists to move facts between two agents without either of them having to
re-read `01-Requirements/`.

### It is filtered by the spec, and that filter is the safety property

The extractor is handed the spec's `## 2 Screen Inventory` and reads its `## 3` element lists first.
Everything it then finds lands in exactly one of three buckets:

```text
USED     the spec names it, and the data behind it was found       → the body sections below
UNUSED   found in an EN/BR, the spec names nothing for it          → ## Unused — NEVER rendered
GAP      the spec names it, nothing in EN/BR/UC supplies the data  → ## Gaps — BLOCKING
```

A `GAP` is never filled by the extractor and never invented by the designer. A form field the spec
shows that no entity carries is a hole in `/bigin-generate-design`'s work; inventing a type for it
here produces a prototype that validates a field which does not exist.

### The shape

````markdown
# Data Model & Logic Spec — UX-<NNN> <Feature>
spec: UX-<NNN> @ v<x> · platform: <web|mobile> · extracted: <date>

## Screens in scope
<!-- copied VERBATIM from ## 2 Screen Inventory. This is the filter, restated so the designer can
     see what was filtered against. An `out of scope` Coverage row never appears here. -->
| Screen | Actor | Volume | Real scale | Serves |

## Entities
<!-- one table per EN-### the spec's ## 3 cites -->
### EN-<NNN> <Name>  ·  status: promoted | proposed | draft
| Field | Type | Required | Format / Enum | Cardinality | Renders on (screen · element) |
<!-- Enum values are listed in their REAL declared order, spelled out in full. A `proposed` or
     `draft` status is carried forward — it grounds as a KNOWN GAP, not as settled fact. -->

## Validation
<!-- one row per BR-### a screen depends on. The predicate is checkable; the message is NOT
     written here — message copy is Stage 2's, from the spec's ## 3. -->
| BR-### | Fires on (field) | When | Predicate | Message source |
<!-- Message source: `BR text` (the rule states it) | `## 3 copy` (the spec states it) | `none`
     (nothing states it — a gap the designer reports, never fills). -->

## State keys
<!-- ONLY states the spec's ## 3 already names. Never a state the extractor thinks is needed. -->
| Screen | State (spec's own name) | Reached by | Grounded by |

## Volume
| Screen | Band | Real number | Grounded by (EN cardinality + UC step) |
<!-- "≈10,384 records, page 1 of 208" — never "several", never "many". The number IS the review. -->

## Enumerations
| Enum | Ordered values | Source | Used on |

## Unused
<!-- found, not named by the spec. A fact for a human. NEVER an input to a render. -->
| What | Source | Why it is unused |

## Gaps            ← BLOCKING
| What the spec names | On (screen · element) | Nothing supplies it because |

## Open
<!-- the spec's own ## 6 questions, verbatim. Carried, never resolved. -->
````

---

## The traceability contract

**Rule A, in full.** A rendered prototype must be traceable back to what specified it, and must carry
none of that where a human can read it.

### The vocabulary

| Attribute | Value | Attached to |
|---|---|---|
| `data-ux` | `UX-<NNN>` | the screen root |
| `data-screen` | the spec's own `## 2` screen name | the screen root |
| `data-uc` | `UC-<NNN>` | any element the spec grounds in a use case |
| `data-uc-step` | `S<n>` / `A<n>` / `E<n>` | the same element, beside `data-uc` |
| `data-br` | `BR-<NNN>` | a validation, a restriction, a role-gated control, a status derivation |
| `data-en` | `EN-<NNN>` | a field-bound input, cell, or read-only value |
| `data-field` | the entity's own field name | the same element, beside `data-en` |
| `data-state` | the spec's own state name | a state variant's root |
| `data-nav-id` | the nav map's dot-path `id` | a nav item |

Space-separate multiples (`data-uc="UC-031 UC-044"`) where an element genuinely serves two.
**Every value must resolve** to a real id in the spec, the data model, or the nav map — an invented
`data-*` value is worse than none, because it reads as verified provenance.

### Where an id may never appear

```text
text nodes          aria-label      title       alt        placeholder     value
<option> bodies     table headers   legends     tooltips   CSS content:    a user-visible URL fragment
```

`aria-label`, `title`, and `alt` are **visible** — a screen reader reads them aloud and a browser
renders them on hover. They are not a loophole.

```html
<!-- WRONG — the prototype announces itself as a document -->
<span class="badge">Pending approval (BR-014)</span>
<button aria-label="Submit request — UC-031 S4">Submit request</button>

<!-- RIGHT — same words, provenance intact, invisible -->
<span class="badge" data-br="BR-014">Pending approval</span>
<button data-uc="UC-031" data-uc-step="S4">Submit request</button>
```

### The check

`scripts/scan-traceability-leaks.sh <path>…` is the deterministic gate: it scans every visible
position for `/(UC|BR|EN|UX)-\d/`, ignores `data-*` attributes, and exits non-zero on a leak. The
designer runs it before reporting; the linter runs it as Part 3's first act and never trusts the
designer's word for it.

**Sanitizing a leak means moving the id, never rewording the copy.** If removing the id leaves the
copy saying nothing — `Status: UC-031` — that is a missing-copy finding for the designer, not a
sanitize.

---

## The navigation contract

**Rule B, in full.** `{nav_map_file}` — `04-UIUX/_design-system/navigation-map.md` — is the **single
source of truth** for navigation structure. Not the UX spec, not the engine's template, not the
screens' apparent grouping, and never a designer's sense of what a menu ought to hold.

### What the map supplies, and what must match it exactly

| Map column | Becomes | Discipline |
|---|---|---|
| `Label` | the nav item's visible text | **verbatim.** Not re-worded, not re-cased |
| `id` (dot-path) | the tree, and `data-nav-id` | `settings.team` nests under `settings`, always |
| `Order` | sibling order under the same parent | it is sibling order, never a global rank |
| `Points to (screen)` | the route | `—` is a container with no screen of its own |
| `Role(s)` | who sees the entry | a persona switcher shows it only to those roles |
| `Icon/token` | the icon | a token name, never a substituted icon set |

Plus two sections outside the table:

```text
§ Removing an entry    a row at `retired` is NOT rendered. Ever. It is history, not a menu item
§ Open Questions       an unresolved placement is NOT resolved by the render. Build what the
                       ## Structure table says and carry the question into the report
```

### Which `## Structure` to read

```text
platform: web       ## Structure                → a persistent sidebar / nav-bar shell
platform: mobile    ## Structure                → a TAB BAR, at most 5 top-level entries
platform: both      ## Structure — Web          → two trees. Build the one you were dispatched with
                    ## Structure — Mobile          An entry on one shell and not the other is
                                                   NORMAL — never mirrored for symmetry
```

### The rules that make a shell read as a product

```text
BUILT ONCE       the shell is byte-identical on every screen. A nav that shifts between screens is
                 the loudest tell that a prototype was assembled screen by screen
CURRENT MARKED   the active entry is visibly current, and its ancestors are open. A tree with no
                 current state reads as a static picture of a menu
NO PROMOTION     a screen the map gives no entry to is reached ONLY through another screen's
                 control. It is a destination, not a menu item — promoting it invents IA
NO INVENTION     a nav item the render wants and the map does not carry is REPORTED, never added.
                 It is a /bigin-generate-design gap
FIVE TABS        a phone shell holds at most 5 top-level entries. A 6th is an Open Question a human
                 was asked to settle — rendering one contradicts the answer they have not given yet
BREADCRUMB       where the map nests 3 or more deep, a breadcrumb renders the real dot-path
```

### On a unified SPA build

One shell, from the one map, shared across every participating spec's routes. The persona switcher's
entries come from the participating specs' `## 1` Actor & Scope tables; the **visibility** of each
nav item under a given persona comes from the map's `Role(s)` column. Every route the assembled app
can reach resolves inside the runtime — a route pointing at a spec nobody named for this build is not
a link, it is a gap the build should never have offered.

---

## Handoff and repair

```text
Part 1 → Part 2   the Data Model & Logic Spec path. `gaps:` non-empty is BLOCKING: the orchestrator
                  decides per screen whether to render without the field or leave it un-rendered.
                  Neither the extractor nor the designer decides that
Part 2 → Part 3   the artifact paths + the designer's report. The report is a CLAIM; Part 3 verifies
                  it and never substitutes it for a check
Part 3 → Part 2   `verdict: RE-RENDER` returns a finding list. The designer re-renders the named
                  screens only. Then the FULL scan runs again — a fix that moved an id into data-*
                  on one screen commonly left it on three
```

**Two round trips, then stop.** A finding surviving two designer→linter cycles is not a render
problem; it is a spec problem or an engine limitation. Report the screen un-rendered, with the
finding, and let a human decide — a third automated attempt produces a screen that satisfies the
linter and nobody else.

**No `## 8` row is written for a screen that did not reach `verdict: PASS`.** A render recorded as
complete with one screen wrong is the failure this whole pipeline exists to catch.
