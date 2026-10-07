# Stage 4 — Write: the epic and its stories, from the templates

```text
runs: orchestrator for ≤ 2 features, else the per-feature worker
in:   the slice plan + minted ids + the sources Stage 3 read + SNAPSHOT.md
out:  EP-<NNN> <Feature>.md and one US-<NNN> <Title>.md per story, all status: draft
never: absorbed: or hub edits (Stage 5) · a sentence nothing written supports · technical vocabulary
```

Instantiate `{template_epic}` and `{template_story}` — the templates are the schema; never compose sections from
memory. Write stories first, the epic last (its § 3, § 4, § 7 summarise the stories).

## The translation rule (S1)

The use case's "System Response & Validation" column is written for completeness, not for a reader. Translate it
into what a **person can see happen**: a message, a screen, a record that now shows up somewhere, a notification
someone receives. Keep every validation, record, and notification — dropping one drops scope. A sentence a
developer needs but a product owner cannot confirm or deny does not belong (`bigin lint` flags the word list).

## Per story

| Section | Source | Rule |
|---|---|---|
| § 1 Story | UC § 1 actor + Business Need; the slice plan | *so that* is the business value, never "so that the system …" |
| § 2 Flow | UC § 2 / § 3 rows of this slice | keep `S#`/`A#`/`E#` ids; one business voice |
| § 3 Flowchart | § 2 of this story | every decision is a `{diamond}`, every user-visible exit a `[/parallelogram/]`; ≤ 15 nodes — bigger means the slice is too big |
| § 4 State Changes | EN-### status values + UC post-conditions | only transitions this story causes; none → the one-line "No record changes status" |
| § 5 Screens | SNAPSHOT.md image + prototype capture + UX § 3 element/state/interaction tables | image first, relative path into `_snapshot/<folder>/`. Field labels and copy **as the prototype shows them**. Rule and message columns from the BR and the UC; a prototype message that contradicts a BR → § 8 question, quote both |
| § 6 Acceptance Criteria | UC validations, E# flows (incl. folded ones), BR statements | one `Scenario` per rule and per error path, numbered, tagged `[S#]` `[E#]` `[BR-###]`. Given = a business situation, When = a user action or a time event, Then = something observable |
| § 7 Boundaries | UC pre-conditions, other UCs on the same screens | what must not change |
| § 8 Notes | UC § 5 still-open questions touching this slice; Stage 2 gaps; anything this run could not answer | copy questions with their **original sentence** |
| § 9 DoR | — | leave unticked; the reviewer ticks |

Frontmatter: `snapshot:` = the folder used; `absorbed:` is left to Stage 5.

## The epic

| Section | Source |
|---|---|
| § 1 | UC § 1 Business Need of every source UC + the hub's `## Pain Points` |
| § 2 | the slice plan; PENDING and NOT OURS UCs from Stage 1 as out-of-scope lines |
| § 3 Story Map | backbone = the main-path story's step groups; rows = P1/P2/P3 |
| § 4 Screen Flow | UX § 4 Flows (`Path` lines) + § 3 Interactions (`Goes to`), one `flowchart LR`; then the screen table with snapshot images. No UX spec → from the prototype's navigation, and say so in § 9 |
| § 5 Lifecycle | per entity with a status field: its full set of values from the EN file, transitions from every source UC |
| § 6 / § 7 | from the stories just written |
| § 8 Done When | the source UCs' success post-conditions, as checks |
| § 9 | every story's still-open questions, de-duplicated by sentence, plus Stage 2's gaps |

## Mermaid rules (renders in Obsidian, GitHub, claude.ai)

Node ids are plain `a1`, `s3`, `e1`; labels go in brackets and are quoted when they contain punctuation:
`s3["Choose a slot (09:00–17:00)"]`. First line inside the fence is `flowchart TD|LR` or `stateDiagram-v2`. No
styling, no click handlers, no subgraph deeper than one level.
