# BR lane — drafting and updating a Business Rule

```text
in:   signals routed to BR
out:  a new/updated BR-### file, its rule STAGED into ## Discussion
      + the `§ 4: add BR-###, enforced at S<n>` mirror staged on each governed UC
never: a rule statement written directly · a UC's ## 4 edited directly
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

Instantiate `{template_br}` as `{br_dir}/BR-<NNN> <Title>.md`, id from a `Grep` scan of `{br_dir}` — its
own sequence, unrelated to UC numbering.

| Field | Value |
|---|---|
| `id` / `title` | `BR-<NNN>` and a short title naming what is constrained |
| `status` | `draft`. Stage 5 may move it to `needs-clarification`; nothing else here |
| `version` | `1.0` |
| `feature` | the hub's slug |
| `uc` | the `UC-###` id(s) this rule governs — **`[]` is valid and common**: a feature-level rule no workflow owns yet keeps an empty list |
| `sources` | the `INT-###` this traces to |
| `owner` / `updated` | `team`, today |

Add the id to the hub's `br:` frontmatter list.

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
STAGE it, never write it directly:
- **<INT-###>** (staged <YYYY-MM-DD>): <the signal> → proposed rule: If <condition>, then <effect>.
→ flip the Signal Log row: Status: staged, Destination: BR-###
→ Stage 1 folds it in after the gate
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
| is owned by the feature you were dispatched for | stage `§ 4: add BR-###, enforced at S<n>` into that UC's `## Discussion`, same run |
| is owned by another `primary_feature` | report a `cross_feature_uc_change`; Stage 4 applies it |
| doesn't exist yet | leave `uc: []` — the rule is real before the workflow is written |

**Never edit `## 4` directly**, and **never guess an enforcement point** by picking the step that
"looks like" the right one: if no step enforces the rule, that is either a missing step or a misfiled
rule, and it is a question.

## Field-level rules

A rule about a specific entity field — "a vendor's tax code must be unique", "a claim's date cannot be
in the future" — is still its own BR file, citing the entity in its own body:

```text
Governs EN-004 Vendor → tax_code.
```

It does **not** become a row or subsection inside `{entity_dir}`. `## Fields` records what a field *is*;
the BR records what must hold of it. That split is what lets one rule govern fields on two entities
without either doc owning it.

Report the entity to the orchestrator so Stage 4 can promote or extend it — never write to
`{entities_file}` or `{entity_dir}` from inside a per-feature subagent.

## Updating an existing BR

```text
edit in place, at ANY status                    # approval does not freeze a BR
stage it as "the rule becomes: <new text>"      # unambiguous about replacement vs addition

a wording change needs NO UC edit at all        # the whole point of separate rule files
only a change to WHICH workflow it governs, or WHERE it is enforced, touches a UC's ## 4

a dropped constraint is NOT deleted:
    stage "the rule is removed because <reason>"
    → the human gate resolves it, Stage 1 folds it in as a version bump + ## Changelog line
    → a HUMAN sets status: removed — never this skill
    → stage the matching `§ 4:` mirror removal on EVERY UC that listed it
```

## Questions and conflicts

Identical to the UC lane (`3-lane-uc.md` § Questions, § Conflict with existing content), written on the
BR's own `## Open Questions`. Two rules that cannot both hold are a `conflict`, raised once naming
both — never a silent narrowing of whichever one this run touched second.
