# BR lane — drafting and updating a Business Rule

Handles signals routed to **BR**. A BR is always its own file under `{br_dir}`, never a subsection
of an FR and never a subsection of an entity doc (`conventions.md` § Entity Data Model). Read
`routing.md` § New vs. update first.

## What belongs in a BR rather than an FR

An FR says what the system does. A BR says under what condition it may or may not do it, or what
value it must respect while doing it. The reliable test: **a BR can be violated by data or by a
person, and the system's job is to prevent or detect that violation.**

| Signal | Artifact |
|---|---|
| "Managers approve expense claims" | FR — a behaviour and a flow |
| "Only a manager can approve a claim over 5 million" | BR — a condition on who and when |
| "Export invoices to CSV" | FR |
| "Invoices older than 7 years are excluded from export" | BR — a policy narrowing the FR |
| "Show the running total" | FR |
| "The total must never go negative" | BR — an invariant |

A BR that reads as a restatement of the FR it constrains is a misrouted FR line. Fold it back.

## Creating a new BR

Instantiate `{template_br}` as `{br_dir}/BR-<NNN> <Title>.md`, id from a `Grep` scan of `{br_dir}` —
its own independent sequence, unrelated to the FR numbering.

| Field | Value |
|---|---|
| `id` / `title` | `BR-<NNN>` and a short title naming what is constrained |
| `status` | `draft`. Stage 5 may move it to `needs-clarification`; nothing else here |
| `version` | `1.0` |
| `feature` | The hub's slug |
| `fr` | The `FR-###` id(s) this rule constrains — **`[]` is valid and common**: a feature-level rule that no single FR owns yet keeps an empty list until one exists |
| `sources` | The `INT-###` this traces to |
| `owner` / `updated` | `team`, today |

Add the id to the hub's `br:` frontmatter list. If the BR constrains a specific FR, that FR's own
content does not change — a BR is discovered by reading the hub's `br:` list and each BR's `fr:`
citation, not by a pointer inside the FR.

## Writing the rule statement

The body's opening block is the rule itself, stated so a tester can produce a pass and a fail case
from it alone:

```
If <condition>, then <the system must | must not> <effect>.
```

- **State the condition in business terms**, not in the client's incidental phrasing. "Over 5
  million" needs its currency and whether it is inclusive; if the source did not say, that is a
  question, not a rounding decision to make here.
- **One rule per BR.** Two conditions that can be violated independently are two BRs. A compound
  rule cannot be cited cleanly by a story or tested as one assertion.
- **Never encode an unstated threshold, unit, timezone, or rounding.** These are the most common
  silently-invented details in a BR, and each one becomes a defect that traces back to a document
  the client approved. Missing → question.

Same as the FR lane, the rule statement is **never written directly on a new or updated BR**.
Stage the proposed text into `## Discussion`, cite the `INT-###`, flip the Signal Log row to
`Status: staged`, `Destination: BR-###`, and let Stage 1 fold it in after the gate.

```
- **<INT-###>** (staged <YYYY-MM-DD>): <the signal> → proposed rule: If <condition>, then <effect>.
```

## Field-level rules

A rule about a specific entity field — "a vendor's tax code must be unique", "a claim's date cannot
be in the future" — is still its own BR file. It cites the entity's fields in its own body:

```
Governs EN-004 Vendor → tax_code.
```

It does **not** become a row or a subsection inside `{entity_dir}/EN-<NNN> …md`. The entity doc's
`## Fields` table records what a field *is*; the BR records what must hold of it. Splitting them
this way is what lets one rule govern fields on two entities without either doc owning it.

When this lane produces a field-level BR, report the entity it governs to the orchestrator so
Stage 4 can promote or extend that entity (`lane-entity.md`) — do not write to `{entities_file}` or
`{entity_dir}` from inside a per-feature subagent.

## Updating an existing BR

An update edits the BR in place at any status, same as an FR (hard rule 7). Stage the change as
`the rule becomes: <new text>` so the fold-in is unambiguous about replacement versus addition.

A BR whose constraint is dropped entirely is **not** deleted. Stage
`the rule is removed because <reason>`; the human gate resolves it, Stage 1 folds it in as a
version bump plus a `## Changelog` line, and a human sets `status: removed` if that is the outcome
(hard rule 4 — never set by this skill).

## Questions and conflicts

Identical to the FR lane (`lane-fr.md` § Raising a question, § Conflict with an existing row),
written on the BR's own `## Open Questions`. Two rules that cannot both hold are a `conflict`,
raised once, naming both — not a silent narrowing of whichever one this run happened to touch
second.
