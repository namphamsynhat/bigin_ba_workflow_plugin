# BR lane — drafting and updating a Business Rule

Handles signals routed to **BR**. A BR is always its own file under `{br_dir}`, never a section of a
UC and never a subsection of an entity doc. That separation is BABOK's (§ 10.47, *Use Cases and
Scenarios*): rules are captured separately so that **a rule change does not force a use-case change**,
and so one rule can govern three workflows without any of them owning it. A UC's `## 4` is a mirror of
these files, never the source.

Read `3-routing.md` § Which UC — new or update first for the shape of the read-before-deciding lookup;
the same discipline applies here.

## What belongs in a BR rather than a UC step

A UC step says what happens. A BR says under what condition it may or may not happen, or what value
must be respected while it does. The reliable test: **a BR can be violated by data or by a person, and
the system's job is to prevent or detect that violation.**

| Signal | Artifact |
|---|---|
| "Managers approve expense claims" | UC step — a behaviour in a flow |
| "Only a manager can approve a claim over 5 million" | BR — a condition on who and when |
| "Export invoices to CSV" | UC step |
| "Invoices older than 7 years are excluded from export" | BR — a policy narrowing the flow |
| "Show the running total" | UC step |
| "The total must never go negative" | BR — an invariant |

A BR that reads as a restatement of the step it constrains is a misrouted step. Fold it back into the
UC lane.

## Creating a new BR

Instantiate `{template_br}` as `{br_dir}/BR-<NNN> <Title>.md`, id from a `Grep` scan of `{br_dir}` —
its own independent sequence, unrelated to the UC numbering.

| Field | Value |
|---|---|
| `id` / `title` | `BR-<NNN>` and a short title naming what is constrained |
| `status` | `draft`. Stage 5 may move it to `needs-clarification`; nothing else here |
| `version` | `1.0` |
| `feature` | The hub's slug |
| `uc` | The `UC-###` id(s) this rule governs — **`[]` is valid and common**: a feature-level rule that no workflow owns yet keeps an empty list until one exists |
| `sources` | The `INT-###` this traces to |
| `owner` / `updated` | `team`, today |

Add the id to the hub's `br:` frontmatter list.

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

Same as the UC lane, the rule statement is **never written directly on a new or updated BR**. Stage the
proposed text into `## Discussion`, cite the `INT-###`, flip the Signal Log row to `Status: staged`,
`Destination: BR-###`, and let Stage 1 fold it in after the gate.

```
- **<INT-###>** (staged <YYYY-MM-DD>): <the signal> → proposed rule: If <condition>, then <effect>.
```

## Keeping the UC's `## 4` mirror in step

A rule that governs a workflow has to be visible from that workflow, or a reviewer reading the UC
approves a flow with an invisible constraint on it. Two facts travel to the UC — and only these two:

- the rule's **id and short statement** (copied, never re-worded into a second version of the rule);
- the **enforcement point** — which `S#` of that flow the rule bites at, or `pre-condition` /
  `post-condition` when it constrains state rather than a step. This fact exists nowhere else, so it
  is the one thing the mirror genuinely adds.

| The governed UC… | Do |
| :--- | :--- |
| is owned by the feature you were dispatched for | Stage `§ 4: add BR-###, enforced at S<n>` into that UC's `## Discussion`, in the same run |
| is owned by another `primary_feature` | Report a `cross_feature_uc_change` candidate; Stage 4 applies it (`3-lane-uc.md` § Ownership) |
| does not exist yet | Leave `uc: []`. The rule is real before the workflow is written, and a later run adds the citation |

**Never edit `## 4` directly** — the mirror is folded in like any other UC change. And never determine
an enforcement point by guessing which step "looks like" the right one: if no step in the flow enforces
the rule, that is either a missing step or a misfiled rule, and it is a question.

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
Stage 4 can promote or extend that entity (`3-lane-entity.md`) — do not write to `{entities_file}` or
`{entity_dir}` from inside a per-feature subagent.

## Updating an existing BR

An update edits the BR in place at any status, same as a UC (hard rule 7). Stage the change as
`the rule becomes: <new text>` so the fold-in is unambiguous about replacement versus addition.

A rule whose wording changes needs **no UC edit at all** — that is the whole point of keeping rules in
their own files. Only a change to which workflow it governs, or to where it is enforced, touches a UC's
`## 4`.

A BR whose constraint is dropped entirely is **not** deleted. Stage
`the rule is removed because <reason>`; the human gate resolves it, Stage 1 folds it in as a
version bump plus a `## Changelog` line, and a human sets `status: removed` if that is the outcome
(hard rule 4 — never set by this skill). Stage the matching `§ 4:` mirror removal on every UC that
listed it, so no flow keeps showing a rule that no longer applies.

## Questions and conflicts

Identical to the UC lane (`3-lane-uc.md` § Questions, and moving one to the decision log; § Conflict
with existing content), written on
the BR's own `## Open Questions`. Two rules that cannot both hold are a `conflict`, raised once,
naming both — not a silent narrowing of whichever one this run happened to touch second.
