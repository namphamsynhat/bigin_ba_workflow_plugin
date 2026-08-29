# Conventions — the map

The vault-wide rulebook, **split into one file per concern** so a stage loads only what it uses.
This file is the map and holds no rules of its own.

**Do not read this file to find a rule.** Read the row for your stage, then open those files
directly. A subagent handed its file list in its dispatch prompt skips this file entirely.

## The files

| File | Holds | Lines |
| :--- | :--- | ---: |
| `core.md` | ID scheme · frontmatter schema · status vocabularies · Obsidian-safe markdown · file naming · changelog | ~220 |
| `version-check.md` | the two precondition `Grep`s — **a skill reads this, a worker never does** | ~45 |
| `use-case.md` | what a `UC-###` is · traceability chain · summary block | ~210 |
| `feature-hub.md` | the hub's schema and tables · `FEATURES.md` feature-map format · feature material | ~340 |
| `intake.md` | intake sources · capture & the question loop · feedback handling | ~175 |
| `questions.md` | open-question wording · open-question ↔ status consistency | ~160 |
| `registers.md` | signal → artifact · signal → feature · entities · pain points · design principles · scenarios (retired) | ~330 |
| `runtime.md` | resumable unattended apply · absorbed/reprocess (Planned) · **reconciliation notes** | ~200 |

The **experience** rulebook is a separate tree with its own map: `design-conventions.md`. A rule
about *what the system does* is here; a rule about *how a user gets there* is there. They never merge.

## What each stage loads

| Stage | Loads |
| :--- | :--- |
| `/bigin-intake` | `core.md` · `intake.md` |
| `/extract-signal` | `core.md` · `feature-hub.md` · `questions.md` — plus `registers.md` **only** when a note actually holds a pain-point, entity, or design row (`agents/signal-filer.md` § Your only rulebook) |
| `/bigin-transform-signal` | `core.md` · `use-case.md` · `feature-hub.md` · `questions.md` |
| `/bigin-generate-design` | `core.md` + the `design-*.md` files its stage row names |
| `/bigin-generate-prd` | `core.md` · `feature-hub.md` § Feature material · `use-case.md` § Traceability chain · `questions.md` |
| `/enrich-feature`, `hub-bookkeeper` | `core.md` · `feature-hub.md` |
| `/sync-entities` | `core.md` · `registers.md` |
| `/approve-uc`, `/restructure-uc` | `core.md` · `use-case.md` |
| `/bigin-run`, `bigin-ba` | `runtime.md` § Reconciliation notes — for migration status, nothing else |
| any stage running unattended | `runtime.md` § Resumable unattended apply |
| every **skill**, at its precondition | `version-check.md` — and no worker ever loads it |

**Every stage that writes an artifact also reads `core.md` § Obsidian-safe markdown.** The vault is
read in Obsidian; a rule broken there silently deletes text a human was supposed to see.

**Every skill runs `version-check.md` at its precondition.** Two `Grep`s, and the `workspace >
plugin` case is a stop, not a warning. A dispatched worker never runs it — the skill that dispatched
it already did.

## Load one stage at a time

These files are sized to be read whole, one stage's worth at a time — that is the point of the
split. A run that walks several stages loads the next stage's row **after** finishing the previous
one, and does not carry the previous stage's rulebook forward. Between stages, compact: the
artifacts on disk are the state, and the rulebook that produced them is re-readable in seconds.

## About these copies

**These are materialized copies, not project data.** `/bigin-new-project` writes the whole
directory to `_bigin/conventions/` so every skill and every dispatched subagent reaches them at a
project-relative path (alongside `paths.md`, which resolves the `{variable}` names the guides in
`_bigin/stages/` use), and overwrites them on each re-run to pick up a plugin upgrade. **Edits made
here are lost on the next run.**

Project-level overrides go in `.claude/bigin-ba-workflow-plugin.local.md`, also scaffolded by
`/bigin-new-project`. It may layer optional house style on top — a `Why`-phrasing convention, a
standing feature-slug shortcut — but never contradicts the schema defined here. The schema is what
every skill's parsing and writing logic is built against, not a per-client preference.

**Sections marked Planned** describe something this plugin does not build yet. They are the target
shape new work should converge on, not documentation of something you can run. The live gap list is
in `runtime.md` § Reconciliation notes for this plugin.
