# Entity lane — entity promotion and cross-feature scenarios

Handles the two cross-feature destinations: a data field or entity a signal describes, and an
end-to-end flow that spans more than one feature. Both write to **vault-wide registers**, so
neither is executed inside a per-feature subagent — a subagent reports its candidates and the
orchestrator applies them in Stage 4, sequentially (`SKILL.md` § Stage 3).

Most runs touch neither. Never promote an entity or mint a scenario speculatively.

## What a subagent reports

Per candidate, enough for the orchestrator to act without re-reading the feature:

```text
entity: <name> | fields: <field>:<type>:<required?> … | source: <INT-###> | referenced_by: FR-###/BR-###
scenario: <one-line flow> | features: <slug> → <slug> → <slug> | this_feature_step: <N> | source: <INT-###>
```

## Entity — promoting a proposed row

`extract-signal` files a `proposed` row in `{entities_file}` when a signal reveals a data field or
entity. It never creates an `EN-###` document. This lane promotes that row **once an FR or BR
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
   and `approved` is a human's call at an FR/BR review gate. `features:` lists **every** slug whose
   FR/BR references it, not just the one being processed.
4. Fill `## Fields`, one row per field. `Source` cites the Signal Log row or the FR/BR that
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
records what must hold of it. `lane-br.md` § Field-level rules covers the BR side.

The same entity appearing on several features' hubs is expected and is not duplication to fix — it
is the point of a shared entity id.

## Business Scenario — a flow that crosses features

`{scenarios_file}` is a **single register**, one row per scenario, not one file per scenario.

The bar is high, and worth applying literally: a scenario is a sequence **a human would narrate as
one story**, whose steps land in different features. "This feature calls that feature's API" is an
implementation detail, not a scenario. "A scholarship switch triggers a wallet adjustment, which
notifies the student" is one.

To create or update a row:

1. `Grep` `{scenarios_file}` for the highest `SCN-###` and increment. Create the file from
   `{template_scenarios}` if it does not exist.
2. Write the `Steps` cell as `<feature>: <what happens>`, in order — the register is the only place
   the full sequence is written out.
3. Add `- SCN-### <name> (step N of M)` to the `## Business Scenarios` section of **every**
   participating feature's hub, each with its own step number. A scenario recorded on only the
   feature being processed is worse than none: it looks complete while the other features have no
   idea they are part of it.
4. When a later signal extends a scenario, update the register row and re-check every hub pointer —
   step numbers shift when a step is inserted, so `(step 2 of 4)` on a hub becomes stale silently.

Set the Signal Log row to `Status: applied`, `Destination: SCN-###`.

A scenario is not an FR. Each participating feature still needs its own FR covering its own step;
the scenario annotates how those chains compose (`conventions.md` § Business Scenarios). When a
scenario reveals that a feature's step has no FR at all, that is a signal-shaped gap worth a
question on that feature's hub — not an FR minted from the scenario's narration.

## Ordering, and why it is sequential

Stage 4 writes `{entities_file}`, `{entity_dir}`, `{scenarios_file}`, and `{design_principles_file}`
one write at a time. All four are vault-wide singletons or shared sequences: two concurrent
promotions would `Grep` the same highest id and mint `EN-007` twice, and two concurrent register
appends would lose one row. Per-feature parallelism is safe precisely because it stops at the hub
boundary — keep it there.

Hub pointer sections (`## Entities`, `## Business Scenarios`) are written in the same sequential
pass, because a cross-feature write touches hubs that other subagents may have just finished with.
