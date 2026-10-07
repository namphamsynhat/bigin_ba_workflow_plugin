# Guide — `user-story.md` (all the writing guidance, kept out of every instance)

An instantiated story carries ONE comment, `<!-- guide: _bigin/templates/user-story.guide.md -->`. Agents never
read this file — they read their card (`cards/story-writer.md`). People read it when writing or reviewing by hand.

## What a story is here

A **use-case slice** (Use-Case 2.0): one path through an approved use case that delivers value on its own, plus
the screens it runs on and the tests that prove it. Never one story per requirement line, never one story per
screen. The order of slicing:

1. **The main success scenario first** — the thinnest end-to-end path, P1.
2. **Then one story per alternative/exception flow, or per group of rules** (SPIDR: Paths, Interface, Data,
   Rules). An `E#` that only shows an error message on the same screen is folded into its parent story's
   acceptance criteria instead of becoming a story.
3. **Spikes are not stories here** — an unknown is a § 8 question.

A developer and a product owner must both be able to read the whole story without opening the use case. That
is the test of every section.

## Frontmatter

```yaml
id: US-             # minted by `bigin mint US` — vault-global, never reused
title:              # what the user gets, as a short active phrase ("Book a free slot")
status: draft       # draft | approved — approved is human-only (/approve-story)
version: 1.0
epic:               # EP-### this story belongs to; that epic's stories: lists it
priority: P1        # P1 | P2 | P3 — P1 is the main path; § 1 says why
slice_of: []        # "UC-003 S1–S6", "UC-003 A2", "UC-003 E1" — the use-case paths this story delivers
rules: []           # BR-### ids its acceptance criteria test
screens: []         # UX spec screen names / view ids this story runs on
entities: []        # EN-### ids whose information it shows or changes
after: []           # US-### that must be delivered first — only a real dependency, never "nice order"
snapshot: none      # the epic's _snapshot/ folder the screens below were captured from — PINNED: a later
                    # capture never rewrites an approved story's images; it reports the story as drifted
absorbed: []        # UC-###@version, UX-###@version — re-stamped whole each run
```

## Sections

* **§ 1 Story** — role / capability / value, in the client's words. *Why this priority* and the *Independent
  test* come from Spec Kit: if you cannot write the independent test, the slice is not independent — merge it.
* **§ 2 Flow** — the slice's steps quoted from the use case, keeping their `S#`/`A#`/`E#` ids, rewritten into one
  business voice. Every validation, record, and notification the step carried survives.
* **§ 3 Flowchart** — Mermaid `flowchart TD`: the trigger, the steps, every decision, every exit the user sees.
* **§ 4 State Changes** — a `stateDiagram-v2` fragment for the record(s) this story moves. None → write
  `No record changes status in this story.` and drop the diagram.
* **§ 5 Screens** — one block per screen, image first. The image comes from the epic's `_snapshot/`; the field,
  action, and state tables come from the prototype capture and the UX spec's § 3. Kinds are business kinds (text,
  number, date, choice, yes-no, file) — never a data type. A field the prototype shows but no use case or entity
  grounds is a § 8 question, not a row someone builds on faith.
* **§ 6 Acceptance Criteria** — Gherkin, one `Scenario` per rule and per error path, numbered `AC1…`, each tagged
  with what it proves: `[S3]`, `[E1]`, `[BR-004]`. Given/When/Then describe what a person can see, not what a
  system stores.
* **§ 7 Boundaries** — what must not change (from `bmad-ticket`): an existing behaviour, another role's view.
* **§ 8 Notes** — open questions (copied with their original sentence), decisions, assumptions.
* **§ 9 Definition of Ready** — ticked by the reviewer, not the generator. The stage only unticks.

## Words that do not belong in a story

API, endpoint, database, SQL, JSON, HTTP, REST, GraphQL, schema, microservice, backend, frontend, payload,
foreign/primary key, UUID, webhook, cron. `bigin lint` flags them. Rewrite the sentence as what the user or the
business observes.
