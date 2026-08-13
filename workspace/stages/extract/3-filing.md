# Filing rules

The rule set the `extract-signal` **filing** subagent follows. Its input is a note whose
`## Extracted signals` table is already complete and already audited against the source. Its job is to
anchor each row to a feature, file the anchored rows onto that feature's hub grouped by functional theme,
mirror what belongs in a vault-wide register, raise a question for anything that can't be anchored, and
set the note's status.

**Never open `## Raw`, a transcript, or an attachment.** The table is the record; extraction (stage 2,
`_bigin/stages/extract/2-extraction.md`) and the source audit already established what the source says.
Re-reading raw material here re-opens a judgment that was made by a stronger model with the source
properly segmented, and any disagreement this stage produced would silently overwrite it.

`{variable}` names resolve in `_bigin/conventions/paths.md`. Read `_bigin/conventions/conventions.md`
§ ID scheme, § Feature Hub, § Signal → feature mapping, § Open Questions wording, § Pain Point Register,
§ Design Principles Register, § Entity Data Model — those sections only.
`.claude/bigin-ba-workflow-plugin.local.md`, if present, overrides anything here (e.g. a standing list of
features that never raise an anchoring question).

## Scope: what this stage writes

| May write | Never writes |
|---|---|
| The table's `Feature`, `Status`, `Notes` columns; the note's `## Open Questions` and `status`/`tags` frontmatter | Any `FR-###` content — no `## Discussion`, no FR-side question copy, no FR status change |
| A feature hub's `## Signal Log`, `## Pain Points`, and its `sources`/`updated` frontmatter | Any `EN-###` document, or a hub's `## Entities`/`## Requirement Readiness`/`## Business Scenarios` |
| `{pain_points_file}`, `{entities_file}`, `{design_principles_file}` register rows | A `{requirements_file}` row — a new slug is a human's call (§ Never guess) |
| | The `#`, `Type`, `Signal`, or `Why` of any table row — stage 2 owns those |

A Signal Log row's `Status`, on a freshly-filed signal, is one of exactly four values:

| Value | When |
|---|---|
| `new` | The default, and the overwhelming majority of rows. Anchored to a feature, queued for whatever folds it into an FR next. **Whether that feature already has an FR is irrelevant — don't check.** |
| `question` | The signal *is* an open question, or a `concern` that needs a call before anything can be built from it, or a row the source audit could not support. |
| `conflict` | It contradicts an existing Signal Log row on the same hub. Cite the earlier row's `#` in `Notes`; never guess which wins. |
| `rejected` | Its feature's `{requirements_file}` row is `status: out-of-scope`. `Notes: out-of-scope — skipped`. |

**`held`, `staged`, `applied`, and `superseded` describe a signal's relationship to an FR — this stage
has no relationship to an FR, so it never writes them.** Retiring that judgment call is deliberate: a
prior design asked this stage to guess between `held` (anchored, no FR yet) and `staged` (queued against
an existing FR), and an unattended batch got it wrong across dozens of signals from one call, stranding
them silently. There is one unprocessed value now — `new`.

## Anchoring a signal to a feature

1. **Check `declared_features` first.** It's a floor, not a ceiling: every row is still matched
   independently, including against features beyond what the human declared at capture. A declared slug is
   settled — never re-question it. A declared slug that ends up with no signal anchored to it is reported
   as a mismatch, not deleted and not justified with a manufactured signal. A declared slug that looks
   like a near-miss of an existing row (typo, plural, hyphenation) is flagged in the report — never
   silently remapped, never minted as a near-duplicate.
2. **Match against `{requirements_file}`.** A signal maps to the feature whose scope it actually
   describes, not the one it happened to be adjacent to.
3. **A row whose feature is `status: out-of-scope`** gets `Status: rejected`, `Notes: out-of-scope —
   skipped` — filed and closed, not raised as a question.
4. **Never guess.** More than one plausible slug → `Feature: unresolved — candidates: a | b`. None →
   `unresolved — none found`, with a suggested new slug in the question. Either way it is a `question`
   row and a `## Open Questions` line, and **never a new `{requirements_file}` row** — a slug is
   permanent and everything downstream anchors to it, so minting one is a human's call.
5. **One signal, one feature.** A signal that genuinely spans two features is filed to both hubs, and its
   `Feature` cell names both — the row itself is never split or duplicated, since stage 2 owns the table's
   rows.
6. **Do not look at whether the matched feature already has an FR.** That check is exactly the judgment
   call § Scope retired.

## Filing to the Feature Hub

An anchored row files onto `{hub_dir}/<slug>.md`'s `## Signal Log`, grouped by functional theme (§ below),
creating the hub from `{template_hub}` if the slug has no hub yet. Filing is **additive only** — never
edit or remove an existing row while filing a new one. Everything else in the hub
(`## Notes / History`, `## Requirement Readiness`, `## Domain Research`, `## Business Scenarios`,
`## Entities`, `## PRD`, `## Epics & Stories`, `## UX Spec`) belongs to later stages.

### Consolidating into themed hub rows

The hub's Signal Log is the working register, not a second copy of the note's table, and it is **grouped
by functional theme**: this note's rows describing the same functional theme file as **one hub row
carrying all of their detail**, not one row each.

Why: three note rows reading "age is computed from date of birth", "the cut-off is 1 September", and
"under-18s need guardian consent" are one requirement conversation — *age eligibility*. Filed as three
rows they get qualified three times, routed three times, and drafted into three overlapping FR lines.
Filed as one row they are one unit of work with nothing dropped.

**What counts as one theme.** The test: *would a drafter write these into one requirement statement?* If
the answer is two independent requirements, they are two themes. Adjacency in the note is not a theme,
and sharing a feature slug is not a theme.

| Merge | Don't merge |
|---|---|
| Rows describing one rule, flow, or decision from different angles — the calculation, its cut-off date, the legal constraint on it | Rows a drafter would write as two independent requirements, however adjacent in the transcript |
| A requirement and the constraint that qualifies *that same* requirement | A constraint that governs the whole feature rather than this one rule |
| Several field-level details of the same form, screen, or record | Two different screens that happened to come up in the same breath |

**Never merge across:**

- **Notes or runs.** A themed row covers one `INT-###`, filed in one run. An earlier row is never
  reopened, rewritten, or extended — history is append-only. When this note's theme continues one already
  on the hub, the new row cites it: `Notes: extends #<n>`.
- **`Status`.** Only `new` rows consolidate. A `question`, `conflict`, or `rejected` signal always files
  as its own row, so its status, its `## Open Questions` mirror, and its rejection reason stay 1:1.
- **The design boundary.** A presentation-only signal never merges with a behavioural one — they route
  down different lanes, and the design lane skips the approval gate
  (`_bigin/stages/transform/3-routing.md` § The design boundary test).
- **A contradiction.** Two signals that disagree are a `conflict`, not a theme.

**A theme of one is normal** — most notes produce a mix of themed rows and single-signal rows. Never
stretch two unrelated signals into a theme to make the table shorter; an over-merged row is worse than a
long log, because the detail a drafter needs is now buried in a row that reads like one ask.

The Signal Log's columns are `# | Signal | Type | Source | Status | Destination | Notes`:

| Column | Rule |
|---|---|
| `#` | One hub-local `#` per row — one per theme, not one per signal. Permanent, never renumbered or deleted. A signal that conflicts with or supersedes an earlier row gets its own new row; update the OLD row's `Status` + `Notes` to point at it, never rewrite history in place. |
| `Signal` | `**<Theme>** — <detail>; <detail>; <detail>`. A short theme name, then every member's claim as its own clause, in the note's row order. **Consolidation is grouping, not summarizing**: no clause is compressed away, and no clause says more than its own note row did. A theme of one is just that row's `Signal` text, no theme prefix needed. |
| `Type` | The member types, in catalog order, joined with ` + ` — e.g. `requirement + constraint`. A theme of one keeps its plain single value. |
| `Source` | `<INT-###> #<n>, #<n>, #<n> — <the note row's own Source cite>`, e.g. `INT-014 #3, #5, #7 — Jane Doe 2026-08-05`. The `#`s are the note's row numbers. This cite is the traceability that replaces one-row-per-signal, and it is what verification confirms — a themed row without it is unfollowable. |
| `Status` | `new` / `question` / `conflict` / `rejected` — never anything else (§ Scope). A themed row is always `new`, since nothing else consolidates. |
| `Destination` | Leave blank. This stage never stages a signal into an FR's discussion. |
| `Notes` | `extends #<n>` when this theme continues an existing hub row; the `PP-###`/entity/design-principle ids its members minted; otherwise blank. |

Worked through, the three age-eligibility rows land as one:

```text
note INT-014 ## Extracted signals (raw record — unchanged, three rows)
  #3 requirement  age is computed from date of birth
  #5 decision     the cut-off is 1 September
  #7 constraint   under-18s need guardian consent

hub  enrolment-eligibility ## Signal Log (one themed row)
| # | Signal | Type | Source | Status | Destination | Notes |
| 7 | **Age eligibility** — age is computed from date of birth; the cut-off is 1 September; under-18s need guardian consent | requirement + constraint + decision | INT-014 #3, #5, #7 — Jane Doe 2026-08-05 | new | | |
```

**Registers are unaffected.** Consolidation is a Signal Log shape only, and it never collapses a register
row. Each `pain-point` member still mints its own `PP-###`; each entity/field member still gets its own
`{entities_file}` row; each durable design constraint still gets its own `{design_principles_file}` row.
The themed row cites those ids in `Notes`.

**Hub frontmatter.** Creating a hub: `feature: <slug>`, `name: <Feature column from
{requirements_file}>`, `status: <that row's Status, mirrored once>`, `sources: [<INT-###>]`,
`updated: <today>`; leave `fr`, `code_areas`, `prd`, `epics`, `stories`, `uiux`, `entities` at template
defaults. Filing to an existing hub: add this `INT-###` to `sources` if absent, bump `updated`, touch
nothing else — a human or later run may have advanced those fields past what this stage knows.

## Registers a signal also writes to

Vault-wide, non-FR registers — a signal shouldn't wait for an FR to be on record.

| Signal shape | Also write |
|---|---|
| `pain-point` | A new `PP-###` in `{pain_points_file}` (create from `{template_pain_points}` if missing; next id scanned vault-wide from that file) plus a mirrored row in the hub's `## Pain Points` (same fields, minus `Feature`). Both copies stay identical. |
| A data field or entity attribute | Match an existing `{entities_file}` row first; a genuinely new one gets a `proposed` row there (create from `{template_entities}` if missing) — **never an `EN-###` document**. No hub section is touched. |
| A durable, cross-cutting design/brand/tone/accessibility/interaction/content preference, not scoped to one feature | A row in `{design_principles_file}` (create from `{template_design_principles}` if missing) — **in addition to** the signal's normal Signal Log filing, not instead of it. Don't call a preference durable when it's plainly scoped to one feature. |

A field table extracted as one row per field produces one `{entities_file}` row per field. Filing them as
a single summarizing entity row undoes the count stage 2 was made to protect.

## Raising a question instead of guessing

A row that fails anchoring, or a `requirement`/`feedback` row whose `Why` is `not stated`, gets a line
under the note's `## Open Questions`:

```
- [ ] Q: <what's missing — the feature slug, or the stated reason> (owner: client|team) ↦ —
      A:
```

- `↦ —` because no FR exists yet to fold this into; a later stage rewrites it to `↦ FR-###`.
- `owner: client` when only the client can answer (missing rationale, ambiguous scope). `owner: team` for
  an internal call (which feature, whether it's in scope).
- Keep the ask recognizably the row's own sentence — don't re-draft it as a second, differently-worded
  ambiguity that can't be paired back to its row. Plain language, no vault vocabulary (`signal`, `slug`,
  `anchor`) for a client-owned question; `(a)/(b)/(c)` once there are three or more options.
- Tag the note `needs-review` and set `status: needs-clarification`.
- A human resolves it by writing the answer — for an anchoring question, the resolved slug, minting a
  `proposed` `{requirements_file}` row first if the scope is genuinely new — into the `A:` line and
  ticking the box. The next run treats the note as a fold-in.

Never re-raise a question already answered elsewhere on the note.

## Before finalizing a note

**Gate the status flip on every touched hub actually being written.** A note whose status flips to
`in-review` drops out of every future scan — if a hub write never landed, that signal is now invisible
everywhere. Re-open or grep each `{hub_dir}/<slug>.md` touched this run and confirm it cites this
`INT-###` before setting the note's status. If turns are running short, finish every pending hub write
first, in order; if the run genuinely can't finish, don't finalize — report which slugs are done versus
pending.

Then, every time:

- **Every table row's `#` appears in exactly one hub row's `Source` cite**, or the row is marked
  `unresolved`/`rejected` with a reason. None missing, none cited twice. This is the check that catches a
  signal lost inside a consolidation, and it replaces comparing row counts (the two counts no longer
  match by design).
- No themed row's `Signal` cell drops a member's claim, and no clause says more than its own note row.
- Count `requirement`/`feedback` rows whose `Why` is `not stated`, and count the companion questions
  raised for them — **the two numbers must match.**
- Every `question`/`concern` row has a mirror line in `## Open Questions`.
- Every `pain-point` row has a `PP-###` in both `{pain_points_file}` and the hub's `## Pain Points`.
- Status: `in-review` if every `## Open Questions` box is checked, `needs-clarification` if any is not.

## Partial fold-ins

A note can come back with some questions answered and others still open. Harvest what was answered —
anchor the rows it unblocks, file them, tick those boxes — and leave the rest parked
`needs-clarification`. Waiting for every box on a note before harvesting any answer strands the answered
ones behind the slowest question on the page.
