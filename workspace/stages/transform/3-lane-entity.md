# Entity lane — entity promotion, and what a subagent must hand back

Handles the entity destination: a data field or entity a signal describes. `{entities_file}` and
`{entity_dir}` are **vault-wide**, so this is never executed inside a per-feature subagent — a subagent
reports its candidates and the orchestrator applies them in Stage 4, sequentially (`SKILL.md`
§ Stage 3).

Most runs touch no entity. Never promote one speculatively.

This file also carries the report shape for the *other* thing a subagent may not write: a change to a
UC owned by a different feature (§ Cross-feature flows).

## What a subagent reports

Per candidate, enough for the orchestrator to act without re-reading the feature:

```text
entity: <name> | fields: <field>:<type>:<required?> … | source: <INT-###> | referenced_by: UC-###/BR-###
cross_feature_uc_change: <UC-### | new> | owner: <primary_feature slug | proposed slug> |
                         change: <the staged text, exactly as it would appear in ## Discussion> |
                         from_feature: <the slug this subagent was dispatched for> | source: <INT-###>
```

## Entity — promoting a proposed row

`extract-signal` files a `proposed` row in `{entities_file}` when a signal reveals a data field or
entity. It never creates an `EN-###` document. This lane promotes that row **once a UC step or a BR
actually references the entity** — that reference is what makes the entity real enough to model.

An entity described in a signal but referenced by nothing yet stays `proposed`. Promoting it early
produces a doc nobody cites and a `## Fields` table nobody maintains.

To promote:

1. Match the entity against `{entities_file}` first. A near-match — plural, a synonym, a
   department's local name for the same thing — is the **same entity**, extended, not a second one.
   When two rows turn out to name one entity, do not merge them silently: raise a question naming
   both and leave both rows.
2. Instantiate `{template_entity}` as `{entity_dir}/EN-<NNN> <Entity>.md`, id from a `Grep` scan of
   `{entity_dir}` (its own independent sequence).
3. Frontmatter: `kind` is `actor` (someone who acts), `data` (something tracked), or `system` (an
   external service). `status: draft` once the doc exists — `proposed` means "row only, no doc",
   and `approved` is a human's call at a UC/BR review gate. `features:` lists **every** slug whose
   UC/BR references it, not just the one being processed.
4. Fill `## Fields`, one row per field. `Source` cites the Signal Log row, or the `UC-### S<n>`/`BR-###` that
   introduced the field — never "from the meeting".
5. Fill `## Relationships` only for relationships an artifact actually states. A plausible foreign
   key nobody mentioned is a modelling invention.
6. Update `{entities_file}`'s row to point at the new doc, and add
   `- EN-### <Name> (<status>)` to the `## Entities` section of **every** referencing feature's
   hub, plus that hub's `entities:` frontmatter list.

**Extending an existing entity** follows the same steps from 4 onward, plus the referencing
feature's hub if it is not already listed. A field that contradicts one already in the table is a
question, not an overwrite.

### Field-level rules stay in `{br_dir}`

A rule about a field — uniqueness, a range, a format, an immutability constraint — is its own
`BR-###` file citing the entity's fields, never a subsection or an extra column here
(`conventions.md` § Entity Data Model). The `## Fields` table records what a field *is*; the BR
records what must hold of it. `3-lane-br.md` § Field-level rules covers the BR side.

The same entity appearing on several features' hubs is expected and is not duplication to fix — it
is the point of a shared entity id.

## Cross-feature flows — a UC, not a register row

**There is no scenario lane any more.** A flow that crosses features is one `UC-###` whose
`features:` lists every slug it touches, and the retired `SCN-###` register was an approximation of
exactly that — a step sequence with no actors, no branches, no rules, and no review gate
(`conventions.md` § Business Scenarios (retired)).

What survives from that register is the reason it was sequential. A cross-feature UC is written by
**one** subagent — `primary_feature`'s — and its pointers land on hubs that other subagents may have
already finished with. So:

| Situation | Who writes it |
| :--- | :--- |
| The UC's `primary_feature` is the slug this subagent was dispatched for | The subagent, normally |
| The UC belongs to another feature, or doesn't exist and the goal is another feature's actor's | **Report** a `cross_feature_uc_change` (§ What a subagent reports); Stage 4 applies it |
| The `## Use Cases` pointer + `uc:` list on each *participating* hub | Always Stage 4, sequentially — never Stage 3 |

A UC recorded on only its primary feature's hub is worse than none: it reads as complete while the
other features have no idea they are part of it. Stage 4 Part 1 step 4 is where that gets fixed, every
run.

When a cross-feature flow reveals that a participating feature contributes a step nobody has
described, that is a signal-shaped gap worth a question on that feature's hub — never a step invented
from the narration of the flow.

## Ordering, and why it is sequential

Stage 4 writes `{entities_file}`, `{entity_dir}`, `{design_principles_file}`, cross-feature UC changes,
and every participating hub's pointers — one write at a time. The registers are vault-wide singletons
or shared sequences: two concurrent promotions would `Grep` the same highest id and mint `EN-007`
twice, and two concurrent appends would lose one row. Per-feature parallelism is safe precisely
because it stops at the hub boundary — keep it there.
