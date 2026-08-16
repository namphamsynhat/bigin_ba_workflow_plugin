# Paths — the `{variable}` table every stage file resolves against

The stage guides in `_bigin/stages/` refer to vault locations by `{variable}` rather than by literal
path. This file is where those resolve. It is the **only** path table a dispatched subagent needs: a
skill's own `SKILL.md § Paths` lives inside the plugin install directory, which a subagent has no way to
reach.

All paths are **project-relative** — resolve them from the repo root, the working directory every skill
and subagent runs in.

## Vault locations

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{inbox_dir}` | `00-Inbox/` | Raw intake, one `INT-<NNN>.md` per capture. `_attachments/` is skipped when scanning. |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | The feature slug registry. Everything anchors to a row here. |
| `{hub_dir}` | `01-Requirements/_features/` | One Feature Hub per slug: `{hub_dir}/<slug>.md`. |
| `{uc_dir}` | `01-Requirements/_ucs/` | One Use Case per file: `{uc_dir}/UC-<NNN> <Title>.md`. **The requirement artifact** — one user goal, its flow, its branches, its rules mirror, its open questions. |
| `{br_dir}` | `01-Requirements/_brs/` | One Business Rule per file: `{br_dir}/BR-<NNN> <Title>.md`. Cites the UC(s) it governs in `uc: []`. |
| `{entity_dir}` | `01-Requirements/_entities/` | One promoted entity per file: `{entity_dir}/EN-<NNN> <Entity>.md`. |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | Proposed `EN-###` register — candidates, before promotion. |
| `{fr_dir}` | `01-Requirements/_frs/` | **Retired, read-only.** Pre-UC `FR-<NNN> <Title>.md` files. Nothing writes here any more; a UC that took one over carries it in `absorbs:` and the FR carries `absorbed_by:` (`_bigin/stages/transform/3-lane-uc.md` § Adopting an existing FR). Absent in a vault created after the UC migration. |
| `{scenarios_file}` | `01-Requirements/SCENARIOS.md` | **Retired, read-only.** Pre-UC `SCN-###` cross-feature register. A cross-feature flow is now one `UC-###` whose `features:` lists every slug it touches. Existing rows stay, marked superseded by the UC that absorbed them. |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | Canonical `PP-###` register. Each hub mirrors its own rows from here. |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | Durable, cross-cutting design constraints. |

`{entities_file}`, `{pain_points_file}`, and `{design_principles_file}` are **vault-wide**. A per-feature
subagent never writes them — it reports candidates and the orchestrator applies them sequentially in
Stage 4 (`_bigin/stages/transform/4-sync.md`). The same restriction covers a **UC owned by another
feature**: a `UC-###` is written only by its `primary_feature`'s subagent
(`_bigin/stages/transform/3-lane-uc.md` § Ownership).

## Rulebook and stage procedures

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{conventions_reference}` | `_bigin/conventions/conventions.md` | The rulebook. Read the sections your stage needs — it has a stage table at the top. Never read it whole. |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | **The design rulebook, deliberately separate** — screens, tokens, prototype prompts. It carries **its own** `{variable}` table (`{ux_dir}`, `{design_system_dir}`, `{template_ux}`, …), so a design-stage worker resolves paths there, not here. Nothing in this file governs design, and nothing in that file governs requirements. |
| `{paths_reference}` | `_bigin/conventions/paths.md` | This file. |
| `{stages_dir}` | `_bigin/stages/` | `extract/`, `transform/`, and `design/` — one numbered file per stage. The `design/` guides resolve against `{design_conventions}` § Paths. |
| `{conventions_file}` | `.claude/bigin-ba-workflow-plugin.local.md` | Optional per-project overrides. A plugin **setting**, not project data — hence `.claude/`. Absent is normal; fall back to built-in defaults per blank section. |

## Templates

`{template_*}` resolves to `_bigin/templates/<name>.md`:

| Variable | File |
| :--- | :--- |
| `{template_intake}` | `_bigin/templates/intake.md` |
| `{template_hub}` | `_bigin/templates/feature-hub.md` |
| `{template_feature_map}` | `_bigin/templates/feature-map.md` |
| `{template_uc}` | `_bigin/templates/use-case.md` |
| `{template_br}` | `_bigin/templates/br.md` |
| `{template_entity}` | `_bigin/templates/entity.md` |
| `{template_entities}` | `_bigin/templates/entities-register.md` |
| `{template_fr}` | `_bigin/templates/fr.md` — **retired**, kept so an absorbed FR still parses |
| `{template_scenarios}` | `_bigin/templates/scenario-register.md` — **retired**, same reason |
| `{template_pain_points}` | `_bigin/templates/pain-points-register.md` |
| `{template_design_principles}` | `_bigin/templates/design-principles-register.md` |
| `{template_project}` | `_bigin/templates/project.md` |

**Instantiate from the template, never compose an artifact from memory.** The template *is* the schema
the next stage parses; a hand-written variant is how a field a later stage reads goes missing.

## When a path doesn't exist

- **A register or template file is missing** — create it from its template (registers) or stop and say
  `/bigin-new-project` must run first (templates, `_bigin/conventions/`, `_bigin/stages/`).
- **`_bigin/conventions/` or `_bigin/stages/` is missing entirely** — stop. Do not improvise the rule you
  cannot read. A subagent that can't load its stage guide still produces an artifact, just one following
  no rule, and reports success.
