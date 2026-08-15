# Entity lane — promotion, and what a subagent hands back

```text
{entities_file} and {entity_dir} are VAULT-WIDE
    → NEVER executed inside a per-feature subagent
    → a subagent REPORTS candidates; the orchestrator applies them in Stage 4, sequentially

most runs touch no entity. NEVER promote one speculatively.
```

This file also carries the report shape for the *other* thing a subagent may not write: a change to a
UC owned by a different feature (§ Cross-feature flows).

## What a subagent reports

Enough for the orchestrator to act without re-reading the feature:

```text
entity: <name> | fields: <field>:<type>:<required?> … | source: <INT-###> |
        referenced_by: UC-###/BR-###

cross_feature_uc_change: <UC-### | new> | owner: <primary_feature slug | proposed slug> |
                         change: <the staged text, exactly as it would appear in ## Discussion> |
                         from_feature: <the slug this subagent was dispatched for> |
                         source: <INT-###>
```

## Promoting a proposed row

`/extract-signal` files a `proposed` row in `{entities_file}` when a signal reveals a data field or
entity. It never creates an `EN-###` document.

**Promote only once a UC step or a BR actually references the entity** — that reference is what makes
it real enough to model. An entity described in a signal but referenced by nothing stays `proposed`;
promoting early produces a doc nobody cites and a `## Fields` table nobody maintains.

```text
1  MATCH against {entities_file} first
   a near-match — plural, a synonym, a department's local name — is the SAME entity, EXTENDED
   two rows that turn out to name one entity → raise a question naming both, leave both rows.
   Never merge silently.
2  instantiate {template_entity} as {entity_dir}/EN-<NNN> <Entity>.md
   id from a Grep scan of {entity_dir} (its own sequence)
3  frontmatter:
     kind:     actor (someone who acts) | data (something tracked) | system (an external service)
     status:   draft once the doc exists
               (`proposed` = row only, no doc · `approved` = a human's call at a review gate)
     features: EVERY slug whose UC/BR references it, not just the one being processed
4  ## Fields — one row per field. Source cites the Signal Log row, or the UC-### S<n> / BR-###
   that introduced the field — never "from the meeting"
5  ## Relationships — ONLY relationships an artifact actually states.
   A plausible foreign key nobody mentioned is a modelling invention.
6  point {entities_file}'s row at the new doc, and add
     - EN-### <Name> (<status>)
   to the ## Entities section of EVERY referencing feature's hub, plus that hub's entities: list

EXTENDING an existing entity → the same steps from 4 onward, plus the referencing hub if not listed
   a field contradicting one already in the table is a QUESTION, not an overwrite
```

### Field-level rules stay in `{br_dir}`

A rule about a field — uniqueness, a range, a format, immutability — is its own `BR-###` citing the
entity's fields, never a subsection or extra column here. `## Fields` records what a field *is*; the BR
records what must hold of it. `3-lane-br.md` § Field-level rules covers the BR side.

The same entity on several features' hubs is expected, not duplication to fix — it is the point of a
shared entity id.

## Cross-feature flows — a UC, not a register row

**There is no scenario lane any more.** A flow crossing features is one `UC-###` whose `features:` lists
every slug it touches. The retired `SCN-###` register was an approximation of exactly that — a step
sequence with no actors, branches, rules, or review gate.

What survives from it is the reason it was sequential: a cross-feature UC is written by **one**
subagent, and its pointers land on hubs other subagents may have already finished with.

| Situation | Who writes it |
| :--- | :--- |
| the UC's `primary_feature` is your dispatched slug | the subagent, normally |
| the UC belongs to another feature, or doesn't exist and the goal is another feature's actor's | **report** a `cross_feature_uc_change`; Stage 4 applies it |
| the `## Use Cases` pointer + `uc:` list on each *participating* hub | **always Stage 4**, sequentially — never Stage 3 |

A UC recorded on only its primary feature's hub is **worse than none**: it reads as complete while the
other features have no idea they are part of it. Stage 4 Part 1b fixes that, every run.

When a cross-feature flow reveals that a participating feature contributes a step nobody described,
that is a signal-shaped gap worth a question on that feature's hub — never a step invented from the
narration of the flow.

## Why Stage 4 is sequential

```text
Stage 4 writes {entities_file}, {entity_dir}, {design_principles_file}, cross-feature UC changes,
and every participating hub's pointers — ONE WRITE AT A TIME

→ the registers are vault-wide singletons or shared sequences
→ two concurrent promotions Grep the same highest id and mint EN-007 TWICE
→ two concurrent appends lose one row

per-feature parallelism is safe precisely because it STOPS AT THE HUB BOUNDARY. Keep it there.
```
