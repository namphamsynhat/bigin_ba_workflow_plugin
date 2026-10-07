# Guide — `epic.md` (all the writing guidance, kept out of every instance)

An instantiated epic carries ONE comment, `<!-- guide: _bigin/templates/epic.guide.md -->`. Agents never read
this file — they read their card (`cards/story-writer.md`). People read it when writing or reviewing by hand.

## What an epic is here

One epic per feature: the **approved use cases whose `primary_feature` is that feature**, sliced into stories.
It is the overview a reviewer reads first — what the business gets, in what order, on which screens, under
which rules — before opening any one story. It is never a technical design: no system names, no data model,
no interface contract (`/bigin-generate-stories` hard rule S1).

```text
03-Epics-Stories/
  EP-<NNN> <Feature>/
    EP-<NNN> <Feature>.md        ← this file
    US-<NNN> <Title>.md          ← one per story (user-story.md)
    _snapshot/<YYYY-MM-DD>-v<N>/ ← the frozen prototype capture the stories were written against
```

A feature too big for one readable epic (more than ~10 stories, or use cases with unrelated actors) is a
§ 9 question — "split EP-<NNN> per use case?" — never a split the stage makes on its own.

## Frontmatter

```yaml
id: EP-             # minted by `bigin mint EP` — never by hand, never reused
title:              # the OUTCOME as a short active phrase ("Members book their own slots"), not a module name
status: draft       # draft | approved — approved is human-only (/approve-story), and only once every story is
version: 1.0        # bumped by every run that changes the body; a human edit bumps it too
feature:            # the ONE FEATURES.md slug that owns this epic
features: []        # every slug its use cases touch, owner first
source_ucs: []      # UC-### ids sliced here — approved ones only
absorbed: []        # UC-###@version, UX-###@version (and PRD-###@version if a legacy PRD was read) —
                    # re-stamped WHOLE every run; the drift record (`runtime.md` § Absorbed)
snapshot: none      # the _snapshot/ folder name the stories were written against, or none
stories: []         # US-### ids, in story-map order
after: []           # EP-### ids that must be delivered first, only when a use case says so
```

## Sections

* **§ 1 Goal & Outcome** — from the use cases' § 1 Business Need and the feature's pain points. A measure that
  is not written anywhere is `not stated — decision needed` plus a § 9 question, never a plausible number.
* **§ 2 Scope** — in scope is one line per slice; out of scope names what a reader would expect and where it
  lives (another epic, a later release, a non-approved UC still in draft).
* **§ 3 Story Map** — Jeff Patton's map. Columns are the use case's main-flow step groups in order (the
  backbone); rows are priority bands. Reading the P1 row left to right must tell the thinnest end-to-end story.
* **§ 4 Screen Flow** — one Mermaid `flowchart LR`, screens as nodes, user actions as edge labels, built from
  the UX spec's § 4 Flows and § 3 Interactions. Under it, one row per screen pointing at its snapshot image.
* **§ 5 Lifecycle** — one Mermaid `stateDiagram-v2` per entity whose status the use cases change, built from the
  entity's status values and the use cases' post-conditions. No entity changes status → delete the section's
  body and write `No record changes status in this epic.`
* **§ 6 Business Rules** — every `BR-###` the stories enforce, with the stories that test it.
* **§ 7 Coverage Matrix** — every `S#`, `A#`, `E#` of every source use case, each mapped to a story. A row with
  no story is a defect the close stage blocks on; a step deliberately left out says `out of scope — <why>`.
* **§ 8 Done When** — 3–6 checks a product owner can run by using the product.
* **§ 9** — questions keep their original sentence when copied from a use case, so one question never
  becomes two.

## Reading tips for reviewers

Read § 1, § 3, § 4 first — the epic should make sense from those three alone. Then open stories in P1 order.
