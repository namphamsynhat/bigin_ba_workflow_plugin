# Stage 2 — Business framing: §§ 1-4 of the PRD

```text
runs: per feature (orchestrator inline, or one worker per feature)
in:   the FOLD list from Stage 1 · each folded UC's § 1 and § 5 · PAIN-POINTS.md rows for this
      feature · the hub's ## Pain Points and ## Notes / History · {project_file}
out:  §§ 1-4 written into {prd_dir}/PRD-<NNN> <Feature>.md, instantiated from {template_prd}
never: inventing a goal, a metric, a stakeholder, or a driver · reading a UC's flow yet
```

**Instantiate from `{template_prd}` first.** The template is the schema Stage 5's verification and
any future epics stage parse; a hand-composed variant is how a field a later stage reads goes
missing. Fill frontmatter as you go, `status: draft`, `version: 1.0` on creation.

An existing PRD is **updated in place** — same id, bump the version, changelog the run. Never
regenerate it from scratch: § 11's `A:` lines and any human edit to § 1's wording are content a
regeneration silently destroys.

## The one rule that governs every line in this stage

```text
P3  Every line traces to something written down. Nothing to trace → "not stated".
```

"not stated" is the correct, useful answer. It says the sources were read and the fact is genuinely
absent — which is what a sponsor needs to know. A plausible invented driver ("to improve
efficiency") is indistinguishable from a real one once it is in the document, and it will be quoted
back as a commitment.

## § 1 Executive Summary

Assemble, in this order:

1. **What this feature delivers** — synthesize the `Business Need / Goal` line from every folded
   UC's § 1 into one outcome sentence. Several UCs on one feature normally share a business need;
   say the shared one, not a list.
2. **Who it is for** — the `Primary Actor` values, deduplicated, as roles.
3. **Why now** — a stated driver only: a `PP-###` this feature resolves, a commitment or deadline in
   `{project_file}`, or an explicit client statement in a UC's § 1. No stated driver → `not stated`.

Then the summary callout: 2-3 sentences a sponsor could read alone. Write it last, from the three
lines above — not from the flows, which they will not read.

## § 2 Business Context & Problem

* **Current state, as stated** — how the business does this today. This is almost always in the
  intake, not in the UC: check the hub's `## Notes / History` and the UC's § 1 pre-conditions.
* **What makes it a problem** — cost, delay, error rate, risk, as stated. Never quantify what was
  not quantified.

The pain-point table mirrors `{pain_points_file}` rows for this feature, **by id**, read-only
(`registers.md` § Pain Point Register). `Addressed by` names the capability from § 5 that
resolves it — fill it after § 5 exists, or write `—` when no folded capability does. A `PP-###` no
capability addresses is worth one line in the report: the feature does not yet resolve a pain the
client stated.

## § 3 Goals & Success Measures

One row per business goal. The `How the business will know it worked` cell is where invention is
most tempting and most damaging:

```text
a source stated a measure           → use it verbatim, with its number
a source stated a goal, no measure  → "not stated — decision needed", and raise it in § 11
no source stated the goal at all    → the goal does not go in the table
```

`Stated by` cites the `INT-###` or the UC whose § 1 carried it.

**Non-goals** come only from an explicit exclusion — a client saying "not in this phase", a
settled decision-log row in a UC's § 5 that closed scope. Never derive a non-goal from absence.

## § 4 Actors & Stakeholders

| From | Take |
|---|---|
| each folded UC's § 1 | `Primary Actor`, `Secondary Actor(s)` |
| `{project_file}` | any named client-side or team contact's **role** |
| a UC's § 4 rule mirror | a role that only appears as a rule's approver (a reviewer, a supervisor) |

Roles, never named people — including the ones lifted from `{project_file}`'s contact tables. `Appears in` cites the UC ids the actor
shows up in, which is how a reader spots an actor who only touches one flow.

## Before moving on

Frontmatter after this stage: `id`, `type`, `title`, `status: draft`, `version`, `feature`,
`features`, `pain_points`, `sources` (unioned `INT-###` from every folded UC), `chain`, `engine`,
`owner`, `updated`. `uc:`, `brs:`, `entities:`, `uiux:`, `absorbed:`, `design_absorbed:`, and
`pending_uc:` are filled by Stages 3-5, not here — a half-filled `absorbed:` is a false "current"
claim if the run dies mid-way.
