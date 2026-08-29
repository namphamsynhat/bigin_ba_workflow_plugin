# Design Conventions — platform

What `platform: web | mobile | both` changes about a screen, a navigation entry, and a state.

**Read by** design stages 1, 2, 3, 5, and 6.

## Platform

**What is being built — a browser app, a phone app, or both.** It is the one project-wide fact that
changes the *shape* of a design without changing a single requirement, so it lives in the project
config, not in an artifact:

```text
_bigin/system/project.md  frontmatter  platform: web | mobile | both
field absent (a project initiated before the field existed)   → treat as `web`
```

`web` is the compatibility default on purpose: it is what every design run before this field produced,
so an unstamped project keeps designing exactly as it always did rather than silently changing shape.

**Read it once, at Stage 1, and pass it down.** Stage 1 announces it; Stages 2–5 and every dispatched
worker are *told* it. A worker never re-reads the project config to decide it, for the same reason it
never re-detects the method layer: two workers inferring a platform differently produces one product
with two navigation shells.

### Per-feature override — the only thing that outranks the config

A UC, a hub `## Design Directives` row, or an active `DESIGN-PRINCIPLES` row that **explicitly states
a platform for a feature** overrides the config *for that feature only*, and gets cited as its ground
like any other decision:

```text
config says `web`, a directive reads "the courier's job list is phone-only"
    → that feature designs as `mobile`, grounded by that directive row #
config says `both`, a UC's actors read "the back-office reviewer at a desk"
    → NOT an override. "At a desk" is where an actor is, not a stated platform.
nothing states a platform                → the config value, unchanged, no citation needed
```

**The bar is an explicit statement, not an inference.** Guessing "this is obviously mobile" from a
step's wording is the same failure as inventing a screen: it reaches a client as a decision somebody
made. Ambiguous → design to the config and raise an Open Question.

### The regions vocabulary, per platform

`## 3`'s `regions` line is semantic structure, never a pixel layout (`design-screens.md` § Screen spec) — but which
semantic regions *exist* is a platform fact:

```text
web     header · nav · main · aside · footer          the persistent-shell vocabulary
mobile  header · content · tab-bar · sheet · fab      the phone vocabulary
```

A `nav` region on a mobile screen, or a `tab-bar` on a web one, is the wrong vocabulary — it produces a
spec that asks a render tool to build a shell the platform does not have.

### What `both` means, exactly

**One platform-neutral requirement set, two design outputs.** This is not a compromise; it is the
plugin's own invariant (`design-core.md` § The eight design hard rules, D4) applied to platform:

```text
requirements   ONE UC set, platform-blind. A UC never forks per platform, and platform never
               becomes a UC step, a branch, or a business rule.
screens        ONE screen inventory (the same user goals), with a per-platform LAYOUT SPLIT only
               where the two genuinely differ — a shared behaviour block, then `Layout — Web` /
               `Layout — Mobile`. Identical on both → one layout line, no split.
flows          ONE flow per user goal. A phone splitting one web page into three sheets is the same
               journey on more surfaces, not a second journey (`design-navigation.md` § User flows and pain points).
nav map        ONE file, TWO structures: `## Structure — Web` and `## Structure — Mobile`, mapping
               the same feature set onto each shell (`design-navigation.md` § The navigation map).
```

**Never split the screen inventory itself.** Two inventories means two designs to keep in sync, and
the second one goes stale the first time a UC changes. The inventory is the user's goals; only the
layout is the platform's.

### Mobile stays generic

No iOS-versus-Android split at this stage. A phone screen is a phone screen: one primary action, a
tab bar, sheets. Platform-specific interaction conventions (a back gesture, a system share sheet, a
material-versus-cupertino control) are build-time decisions nothing on record has stated — an
explicit client statement about one is a `DESIGN-PRINCIPLES` row, not a design call made here.

### Rendering is a separate step

`/bigin-generate-design` produces a **specification** — actors, screens, states, real copy, the
navigation shell, the flows, and a coverage table. It renders nothing, checks for no design tool, and
has **no halt of its own**.

Turning that specification into something a client can look at is `/bigin-render-design-od`, invoked by a
human who has decided they want a prototype:

```text
/bigin-render-design-od [feature slug | UX-### ...] [--design-system <id>] [--project <name|id>]

the ENGINE is Open Design, on every platform. `platform:` decides the SHELL a render builds — a
sidebar/nav-bar at desktop width, or a 390px phone frame with a bottom tab bar — never which tool
builds it.
FOUR THINGS ARE THE HUMAN'S, and that skill asks about each it cannot already resolve:
    which features            never "everything"
    which Open Design project share an existing one, or create a new one for this vault
    which DESIGN SYSTEM       the design team's, or one from Open Design's own catalog. THIS SKILL
                              PRODUCES NONE, which is exactly why it is asked rather than defaulted.
                              DESIGN-PRINCIPLES still wins over whichever is picked
    which model               from what Open Design offers, never a hardcoded id
Open Design unreachable  → that skill retries, then hands the spec over to paste in by hand.
                           Nothing upstream ever halts
```

**Why this is not part of the design run.** Which features, which design system, and when are
timing-and-taste decisions belonging to whoever is going to sit with the client. Binding them to an
unattended pipeline re-rendered features nobody asked about, picked a brand nobody was asked about,
and — the expensive part — let a missing prototype tool stop a stage that reads use cases and writes
markdown.

**What guards against a design nobody can look at.** `5-verify` proves the spec is complete enough to
render *cold*, on any engine, months later (`design-grounding.md` § Coverage verification). A spec that passes that is a
spec a render cannot go wrong on for want of input — with the single, deliberate exception of the
visual system, which is not this skill's to supply.
