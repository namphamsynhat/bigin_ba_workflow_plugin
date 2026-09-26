# BR lane — drafting and updating a Business Rule

```text
in:   signals routed to BR (from the route worklist)
out:  change sets: create_br / set_rule / append_rule_clause on the BR, mirror_br on each governed UC
never: editing a BR or UC file · a rule statement typed into a UC's ## 4
```

A BR is **always its own file** under `{br_dir}` — never a section of a UC, never a subsection of an
entity doc. That separation is BABOK's (§ 10.47): rules are captured separately so **a rule change does
not force a use-case change**, and so one rule can govern three workflows without any of them owning
it. A UC's `## 4` is a mirror of these files, never the source.

## BR or UC step?

**Test: a BR can be violated by data or by a person, and the system's job is to prevent or detect that
violation.** A UC step says what happens; a BR says under what condition it may happen, or what value
must hold while it does.

| Signal | Artifact |
|---|---|
| "managers approve expense claims" | UC step — a behaviour in a flow |
| "only a manager can approve a claim over 5 million" | BR — a condition on who and when |
| "export invoices to CSV" | UC step |
| "invoices older than 7 years are excluded from export" | BR — a policy narrowing the flow |
| "show the running total" | UC step |
| "the total must never go negative" | BR — an invariant |

A BR that reads as a restatement of the step it constrains is a **misrouted step**. Fold it back into
the UC lane.

## Creating a new BR

A `create_br` change set with a `key` and `create`: `title` (what is constrained), `feature` (the hub's
slug), `uc` (the UC id(s) it governs — **`[]` is valid and common**: a feature-level rule no workflow owns
yet), `sources`, `statement`. The engine mints the id (its own sequence) under the lock, writes the file
from `{template_br}`, adds it to the hub's `br:` list, and resolves `new:<key>` in the same batch — so a
`mirror_br` with `br: "new:<key>"` can link it at once. Status is `draft`; `bigin status` moves it later.

## Writing the rule statement

```text
If <condition>, then <the system must | must not> <effect>.
```

Stated so a tester can produce a pass case and a fail case from it alone.

- **Condition in business terms**, not the client's incidental phrasing. "Over 5 million" needs its
  currency and whether it is inclusive; if the source didn't say, that is a **question**, not a
  rounding decision to make here.
- **One rule per BR.** Two conditions violable independently are two BRs — a compound rule can't be
  cited cleanly by a story or tested as one assertion.
- **Never encode an unstated threshold, unit, timezone, or rounding.** The most common
  silently-invented details in a BR, and each becomes a defect tracing back to a document the client
  approved. Missing → question.

```text
new rule        → create_br   create.statement: "If <condition>, then <effect>."
changed rule    → set_rule    text: the whole new statement · anchor.sha: the worklist's statement sha
added clause    → append_rule_clause   text: the clause, as a full sentence
decision needed → the same set with gate: {question, owner, blocks: true} — it waits in the ledger
```

## Keeping the UC's `## 4` mirror in step

A rule governing a workflow must be visible from that workflow, or a reviewer approves a flow with an
invisible constraint on it. **Exactly two facts travel to the UC:**

- the rule's **id and short statement** — copied, never re-worded into a second version of the rule;
- the **enforcement point** — which `S#` the rule bites at, or `pre-condition` / `post-condition` when
  it constrains state rather than a step. This fact exists nowhere else, so it is what the mirror
  genuinely adds.

| The governed UC… | Do |
| :--- | :--- |
| exists (on any feature) | a `mirror_br` set on that UC: `br`, `enforced_at` — the engine copies the statement and adds the UC to the BR's `uc:` |
| doesn't exist yet | nothing — `uc: []`; the rule is real before the workflow is written |

**Never guess an enforcement point** by picking the step that "looks like" the right one: if no step
enforces the rule, that is a missing step or a misfiled rule, and it is a question. A wording change needs
no UC set at all — `bigin mirror br` refreshes every mirror from the BR.

## Field-level rules

A rule about a specific entity field — "a vendor's tax code must be unique", "a claim's date cannot be
in the future" — is still its own BR file, citing the entity in its own body, by its `EN-###` id once
one exists, otherwise by name against `{entities_file}`'s `proposed` row:

```text
Governs EN-004 Vendor → tax_code.        # once EN-004 exists
Governs the Vendor entity → tax_code.    # before it does
```

It does **not** become a row or subsection inside `{entity_dir}`. `## Fields` records what a field *is*;
the BR records what must hold of it. That split is what lets one rule govern fields on two entities
without either doc owning it.

Never write to `{entities_file}` or `{entity_dir}`, and never
report this as a candidate for the orchestrator to promote — **entity promotion doesn't happen in
this skill any more.** A `proposed` row stays a row until `/sync-entities` promotes it, run once a UC
or one of its BRs is actually approved and confirmed to reference it (`registers.md` § Entity Data Model).

## Updating an existing BR

```text
at ANY status                                   # approval does not freeze a BR
rewording / narrowing → set_rule (the whole new statement, anchor.sha from the worklist)
an extra clause       → append_rule_clause
a change to WHICH workflow it governs or WHERE → mirror_br on the UC(s) concerned

a dropped constraint is NOT deleted and NOT set removed here:
    add_question to the BR proposing the removal (owner: team), gated or not
    → a HUMAN sets status: removed; then the UC mirrors are dropped by /restructure-uc or a human
```

## Questions and conflicts

Identical to the UC lane (`3-lane-uc.md` § Questions, § Conflict with existing content), as `add_question`
sets targeting the BR (its `## Open Questions`). Two rules that cannot both hold are a `conflict`, raised once naming
both — never a silent narrowing of whichever one this run touched second.
