# Worker dispatch — one per feature (Stages 3-4 only)

```text
Agent(session default model, general-purpose, foreground)   # judgment work — not haiku
one per FEATURE SLUG                                         # an epic is one ownership domain
≤ 4 features concurrently, verify between waves
```

**Skip the worker for one or two features** — run `3-slice.md` → `4-write.md` inline.
**Stages 1, 2, 5 never run in a worker.** Capture needs the orchestrator's tools; hubs are shared state.

## Before dispatching — the orchestrator does these four things

```text
1  MINT          $BIGIN mint ep --spec <json> for a new epic. Story ids are minted AFTER the worker returns its slice
                 plan — or pre-mint a block of ids and pass them; the worker uses them in order and
                 reports the unused ones. Never let a worker mint.
2  CLASSIFY      per feature: SLICE (ids@version), CURRENT, PENDING, NOT OURS, drifted approved stories.
3  CAPTURE       Stage 2 done: the snapshot folder name, or "none".
4  NAME DESIGN   UX-###@version, or "no design yet".
```

## The prompt

```text
Write the epic and user stories for feature <slug>.

Business stories, not technical tasks. Each story is a SLICE of one approved use case (Use-Case 2.0): the
main success path first, then alternative/exception flows or rule groups. Screens come from a FROZEN
prototype snapshot; you report them, you never design them.

YOUR EPIC:        EP-<NNN> (new — create from _bigin/templates/epic.md | exists — update in place)
FOLDER:           03-Epics-Stories/EP-<NNN> <Feature>/
STORY IDS:        US-<NNN> … US-<NNN> (use in order; report unused)
UCs TO SLICE:     UC-<NNN>@<v> (new | drifted from <v>) …
UCs PENDING:      UC-<NNN> (<status>) …  → epic § 2 out-of-scope lines only
UCs NOT YOURS:    UC-<NNN> (sliced in <slug>'s epic) …
APPROVED STORIES: US-<NNN> … — DO NOT EDIT. Report any that drifted.
SNAPSHOT:         _snapshot/<folder>/ (read SNAPSHOT.md first) | none
DESIGN:           UX-<NNN>@<v> | no design yet

READ FIRST:
- _bigin/cards/story-writer.md — your card
- _bigin/stages/stories/3-slice.md, 4-write.md — in full
- _bigin/templates/epic.md, user-story.md — the schema
- each UC TO SLICE in full; every BR in its brs:; every EN in its entities:
- the UX spec §§ 2-4, if any; the snapshot's SNAPSHOT.md and images list

WRITE: only files inside YOUR FOLDER, status: draft. Leave absorbed: empty.
REPLY with ONE block:
  stories: US-### "<title>" P# slice_of … (new|updated|unchanged)
  unused ids: …
  coverage: <n>/<n> paths · folded E#: …
  open questions: <count> · drifted approved: …
```

## Wave verification (orchestrator, after each wave)

Every reported file exists · nothing outside the folder changed · no approved story's content changed ·
`$BIGIN lint --full` clean on the folder. A failure goes back to the same worker once, then the feature is parked
and reported.
