---
name: bigin-generate-stories
description: This skill should be used when the user asks to "generate the epics", "write the user stories", "create epics and stories", "slice the use cases into stories", "hand this feature to dev", "stories for this feature", "which features are ready for stories", "refresh the stories", "capture the prototype into the stories", or after /approve-uc has approved one or more use cases on a feature. Slices every approved UC-### of a feature — with its business rules, entities, UX-### design, and a frozen snapshot of the prototype (Claude Design / claude.ai artifact, Figma / Figma Make, or Open Design) — into one business-only epic per feature and one user story per use-case slice, each with screen flow, screen spec, flowchart, state diagram, and Gherkin acceptance criteria.
argument-hint: "[feature slug | UC-### | omit for every feature with approved UCs and no current epic] [--prototype <url|path>]"
disable-model-invocation: true
---

# Bigin Generate Stories

The **load** step that hands work to developers. It takes a feature's approved use cases and the prototype that
shows them, and writes what a development team builds from — in a language the product owner can still sign:

```text
in    every UC-### on the feature at status: approved   (new, or changed since last sliced)
    + its BR-### rules + EN-### entities + the UX-### design (screens, flows, states)
    + the prototype, captured once and FROZEN       (Claude Design · Figma / Figma Make · Open Design)
    + a legacy PRD-###, if one exists — context only

out   03-Epics-Stories/EP-<NNN> <Feature>/
        EP-<NNN> <Feature>.md     goal · story map · screen flow · lifecycles · coverage · done-when
        US-<NNN> <Title>.md       one per use-case slice: story · flow · flowchart · state changes ·
                                  screens (image + fields + actions + states) · Gherkin AC · DoR
        _snapshot/<date>-v<N>/    the prototype as it was when the stories were written
    + absorbed: UC-###@version, UX-###@version   the drift record
    + hub epics: / stories: / ## Epics & Stories
```

**Business stories, not technical tasks.** Every line describes what a person sees, does, or is told, and what
the business keeps. No interface contract, data model, system name, or technology — those are the developers' to
decide. **Fully headless:** no checkpoints; anything unanswerable lands as a § 8/§ 9 question and the review happens
on the files afterwards. **Read-only upstream:** it never edits a UC, BR, entity, UX spec, or prototype.

## Why it is built this way (market review, 2026-10)

BMAD's `bmad-create-epics-and-stories` requires an Architecture document, halts at interactive menus (headless PR
#2931 was closed), carries no screen spec or diagrams, and is being replaced by `bmad-ticket` on BMAD `main` — so
this skill does not wrap it. It borrows instead: BMAD's **coverage map** (here: every UC path → a story) and
`bmad-ticket`'s fields (`after`, Boundaries, Notes); **Use-Case 2.0** slicing (Jacobson) — a story is a slice of a
use case, main path first; **SPIDR** splitting; **Spec Kit**'s priority, *why this priority*, and *independent
test*; **Gherkin** acceptance criteria; **INVEST** and a **Definition of Ready**; **Mermaid** diagrams that render in
Obsidian, GitHub, and claude.ai.

## The six story hard rules

```text
S1  Business language only. No API, endpoint, database, schema, payload, framework, field type, or system
    name. The test: a sentence a developer needs but a product owner cannot confirm or deny is wrong here.
    `bigin lint` enforces the word list.
S2  Approved UCs only. A non-approved UC is an out-of-scope line in the epic's § 2, never a story.
S3  Never invent. Every line traces to a UC step, a BR, an entity, a UX screen, or the prototype capture.
    Nothing to trace → a § 8 question, not a plausible guess.
S4  Upstream is READ-ONLY: UCs, BRs, entities, UX specs, the prototype, earlier snapshots.
S5  Never write status: approved, and never rewrite an approved story — report it as drifted.
    /approve-story is the human's gate.
S6  Screens are CAPTURED, not designed. § 5 reports what the snapshot and the UX spec show; it never adds a
    field, a screen, or a message neither of them has.
```

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{stories_dir}` | `03-Epics-Stories/` | one folder per epic: `EP-<NNN> <Feature>/` |
| `{stories_stages_dir}` | `_bigin/stages/stories/` | `1-scope`, `2-snapshot`, `3-slice`, `4-write`, `5-close` |
| `{template_epic}` · `{template_story}` | `_bigin/templates/epic.md` · `user-story.md` | **the schema** — instantiate, never compose from memory |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | read-only |
| `{ux_dir}` | `04-UIUX/UX-<NNN> <Feature>.md` | read-only — §§ 2-4 are the screen skeleton, § 8 points at renders |
| `{prototypes_dir}` | `04-UIUX/_prototypes/` | read-only — Open Design / plugin renders |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | `epics:`, `stories:`, `## Epics & Stories` out |
| `{conventions_reference}` | `_bigin/conventions/` | `feature-hub.md` § Feature material · `use-case.md` § Traceability chain · `runtime.md` § Absorbed · `core.md` § Status vocabularies · `questions.md` § Open Questions wording |

Missing `_bigin/stages/stories/` or `_bigin/templates/epic.md` → stop: `/bigin-upgrade-project` (or
`/bigin-new-project`) must run first. Then `version-check.md` § Workspace version check: behind → warn; ahead → stop.

`$BIGIN` is `"${CLAUDE_PLUGIN_ROOT}/bin/bigin"`.

## Execution order

```text
scope = $ARGUMENTS slug or UC-###, else every {hub_dir} feature with approved UCs

1  scope      chain gate, SLICE / CURRENT / PENDING per UC, design + prototype read   [1-scope.md]
2  snapshot   capture and freeze the prototype; map its screens to the UX spec        [2-snapshot.md]
3  slice      Use-Case 2.0 slices, priorities, coverage matrix, INVEST; mint US ids   [3-slice.md]
4  write      stories, then the epic, from the templates                              [4-write.md]
5  close      8 checks, stamp absorbed:, refresh the hub, report                      [5-close.md]
```

Run all five, in order. **Load a stage file on reaching that stage**, not up front. Stages 1, 2, and 5 always run in
the orchestrator: Stage 2 needs the Artifact / Figma / browser tools, and Stage 5 touches shared hubs.

## Fan-out

One worker per feature past **two features** in a run, for Stages 3-4 only — a feature's epic is one ownership
domain. One or two features run inline. A worker never mints an id, writes a hub, captures a prototype, or touches
another feature's epic. Prompt and report contract: **`references/agent-dispatch.md`**. Driven from `/bigin-run`
only — a subagent cannot dispatch subagents.

## Failure modes

Ordered by cost to discover later.

- **Linking the live prototype instead of the snapshot.** The story changes meaning under the developer the
  next time the designer edits; nobody re-approves it.
- **One story per requirement line or per screen.** Developers get fragments no one can test end to end; the
  product owner cannot tell whether the goal is delivered.
- **A blank coverage row.** An exception flow is never built, and it surfaces in production.
- **A field the prototype shows but nothing grounds.** It gets built as if specified. It is a § 8 question.
- **Technical words in the AC.** The product owner stops reviewing; the gate quietly stops being a gate.
- **Rewriting an approved story on drift.** The signed scope changes with no signature.
- **Rewording a UC's open question.** One decision becomes two, answered inconsistently.
- **Overwriting a snapshot folder.** The evidence an approval was given against is gone.

## Additional resources

- **`references/agent-dispatch.md`** — the per-feature worker prompt and report contract. Read at Stage 3 when
  fanning out.
- **`references/prototype-sources.md`** — tool calls per prototype kind, and what to report when a tool is not
  connected. Read at Stage 2.
