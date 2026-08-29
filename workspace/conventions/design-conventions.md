# Design Conventions — the map

The **UX** rulebook, **split into one file per concern** so a design stage loads only what it uses.
This file is the map and holds no rules of its own.

**Do not read this file to find a rule.** Read the row for your stage, then open those files
directly. A design worker handed its file list in its dispatch prompt skips this file entirely.

**This tree is deliberately separate from `conventions.md`.** That one is the **requirement**
rulebook — what a use case is, when a signal becomes a rule, who may approve scope. This one is the
**experience** rulebook:

```text
a rule about WHAT THE SYSTEM DOES        → conventions.md's files  (requirement side)
a rule about HOW A USER GETS THERE       → this tree               (experience side)
a "design rule" that decides behaviour   → it is a requirement. It is in the wrong file.
```

**There is no design system here, and no tokens.** `/bigin-generate-design` produces the
**experience** — actors, screens, states, navigation, and the flows that connect them — and says
nothing about colour, type, spacing, or component styling. A screen names a **semantic role**
(`design-screens.md` § Semantic style roles); a real design system is supplied later, by the design
team or by whichever system a render is bound to. A run that invents a palette has designed the one
thing nobody asked it for and locked the client's brand to it.

## The files

| File | Holds | Lines |
| :--- | :--- | ---: |
| `design-core.md` | the design `{variable}` table · write map · the eight hard rules · design status vocabulary · staleness | ~130 |
| `design-platform.md` | what `web`/`mobile`/`both` changes about a screen, a nav entry, a state | ~120 |
| `design-actor-scope.md` | who a screen is for, how much they hold, when one place is two screens | ~100 |
| `design-navigation.md` | the navigation map · user flows and the pain points they resolve | ~130 |
| `design-screens.md` | the UX spec · screen spec · semantic style roles | ~105 |
| `design-grounding.md` | grounding · coverage verification · open questions | ~125 |
| `design-review.md` | the flow review · the relationship model | ~110 |

## What each stage loads

`design-core.md` is unconditional — every stage below reads it, plus the files in its own row.

| Stage | Also loads |
| :--- | :--- |
| `1-scope` | `design-platform.md` |
| `2-navigation` | `design-navigation.md` · `design-platform.md` |
| `3-screens` | `design-screens.md` · `design-navigation.md` · `design-grounding.md` · `design-actor-scope.md` · `design-platform.md` |
| `4-flow-review` | `design-review.md` · `design-navigation.md` · `design-grounding.md` |
| `5-verify` | `design-grounding.md` · `design-screens.md` · `design-actor-scope.md` · `design-platform.md` |
| `6-close` | `design-navigation.md` · `design-review.md` · `design-grounding.md` · `design-actor-scope.md` · `design-platform.md` |

Stage 3 is the widest row on purpose — it is the stage that writes screens. Every other stage is
two or three small files.

## Load one stage at a time

Read the row for the stage you are running, do that stage, then compact before the next one. The
UX spec on disk is the state; these files are re-readable in seconds. Carrying stage 3's five
files into stage 6 buys nothing and costs the whole context.

## About these copies

Materialized by `/bigin-new-project` into `_bigin/conventions/` and overwritten on every re-run —
edits made here are lost. Overrides belong in `.claude/bigin-ba-workflow-plugin.local.md`.
