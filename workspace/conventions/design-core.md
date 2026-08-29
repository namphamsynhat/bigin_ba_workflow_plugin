# Design Conventions — core

The design `{variable}` table, the write map, the eight hard rules, the design status vocabulary,
and what "unprocessed" means. **Every** design stage reads this file and nothing else by default.

The rest of the experience rulebook is split into siblings loaded per stage — see
`design-conventions.md` for the map.

## Paths

Project-relative, from the repo root.

**Experience side — this stage owns these.**

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{ux_dir}` | `04-UIUX/` | one spec per feature: `UX-<NNN> <Feature>.md` |
| `{ux_system_dir}` | `04-UIUX/_ux/` | the **one, vault-wide** UX system: navigation and the flow spine. Not a design system — it holds no colour, type, spacing, or component styling |
| `{nav_map_file}` | `04-UIUX/_ux/navigation-map.md` | the vault's menu/navigation system |
| `{prototype_dir}` | `04-UIUX/_prototypes/` | rendered prototypes copied back out of Open Design, one folder per render: `<YYYY-MM-DD>-<slug\|multi>/`. Written by `/bigin-render-design-od` and by nothing else — **no design stage touches it** |
| `{design_stages_dir}` | `_bigin/stages/design/` | `1-scope`, `2-navigation`, `3-screens`, `4-flow-review`, `5-verify`, `6-close` |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | this file |
| `{template_ux}` | `_bigin/templates/ux-spec.md` | |
| `{template_nav_map}` | `_bigin/templates/navigation-map.md` | |

**Requirement side — inputs. Read them; do not rewrite them.**

| Variable | Path | What design takes from it |
| :--- | :--- | :--- |
| `{uc_dir}` | `01-Requirements/_ucs/` | the flow the screens serve — `## 2` steps, `## 3` branches |
| `{br_dir}` | `01-Requirements/_brs/` | validations and error states |
| `{entity_dir}` | `01-Requirements/_entities/` | the fields a form actually has |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | the `PP-###` register — **what the flows exist to fix** (`design-navigation.md` § User flows and pain points) |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | client-stated durable preferences |
| `{hub_dir}` | `01-Requirements/_features/` | `## Design Directives` and `## Pain Points` in, `## UX Spec` out |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | the slug registry |

Missing `_bigin/conventions/`, `_bigin/stages/design/`, or `_bigin/templates/` → stop and say
`/bigin-new-project` must run first. A subagent that cannot read its stage guide still writes a
screen, just one following no rule.

**A design system, if this vault has one, is not on either list.** A design team may drop one
anywhere they like; nothing in this skill reads it, writes it, or requires it. Which system a
prototype is rendered against is `/bigin-render-design-od`'s question, asked of a human, at render time.

## Write map — what design may touch

```text
WRITE   {ux_dir}                      the UX spec (create, or update in place) — except `## 8
                                      Rendered Artifacts`, which only /bigin-render-design-od writes
        {nav_map_file}                menu entries — ADD ONLY
        hub ## UX Spec                link + status
        hub uiux:                     the UX-### id
        hub ## Design Directives      Status: open → reflected, on rows a screen really implements
        hub ## Open Questions / Gates design questions
        hub ## Notes / History · ## Changelog   one line each

READ    every path in the requirement table above

NEVER   a UC's ## 1-## 6 · a BR's rule statement · an EN field list
        DESIGN-PRINCIPLES.md          (client-stated only — research findings are not client words)
        PAIN-POINTS.md                the register is the requirement side's. A flow that resolves a
                                      pain point says so in the UX spec; it never writes the row's
                                      `Resolved by` cell, and never adds a pain point of its own
        a hub's Signal Log · ## Pain Points · ## Requirement Readiness · status: · uc: · br:
        FEATURES.md
        _bigin/system/project.md      the engagement config, INCLUDING platform: — design READS it
                                      (`design-platform.md` § Platform) and never writes it. An unstamped config is
                                      reported and defaulted, never stamped from here: stamping it
                                      is /bigin-upgrade-project's job, with a human present to
                                      answer (1-scope.md § Adopting an existing project config).
```

**One sanctioned exception.** When a UC is **not** `approved`, append **one** line to its
`## Discussion` citing the UX spec as supporting visual evidence. Nothing else, ever, and nothing at
all on an `approved` UC.

## The eight design hard rules

```text
D1  The navigation map is APPEND-ONLY. Never delete or rename an entry — retire it.
D2  A screen spec names a SEMANTIC ROLE, never a value and never a token id. No hex, no px, no font
    name, no `--color-*` (see `design-screens.md` § Semantic style roles).
D3  Every screen, element, state, and flow is GROUNDED (see `design-grounding.md` § Grounding). Ungrounded → a question.
D4  Requirement content is READ-ONLY. Design never edits a UC, a BR, an entity, or a pain point.
D5  Never write status: accepted. A human accepts a design; an agent never does.
D6  A user flow must RESOLVE SOMETHING STATED — a UC goal, or a `PP-###` pain point it names. A
    flow that resolves nothing on record is an invented journey (see `design-navigation.md` § User flows and pain points).
D7  A relationship model never grants MEMORY, AUTONOMY, or RETENTION the requirements did not
    state. What an agent keeps, decides alone, or forgets is behaviour — a requirement gap, never
    a design call (see `design-review.md` § The relationship model).
D8  An actor's DATA SCOPE and VOLUME are read from the requirements, never assumed — and volume
    licenses FINDING machinery only, never a CAPABILITY. Acting on many records at once is
    behaviour: a requirement gap, never a design call (see `design-actor-scope.md` § Actor scope).
```

## Design status vocabulary

Its own list, unrelated to the UC/BR one.

| Status | Meaning |
|---|---|
| `draft` | screens exist, written by the design stage. The resting state. |
| `needs-clarification` | ≥ 1 unchecked `- [ ] Q:` in the spec's `## 6 Open Questions`. |
| `accepted` | a human reviewed the screens and said yes. **Human-only** (D5). |
| `superseded` | replaced by another `UX-###`. Rare — updates land in place. |

**The invariant:** zero unchecked `- [ ] Q:` in `## 6` ⟺ status is not `needs-clarification`; any
unchecked line ⟺ status **is** `needs-clarification`. Set it **last**, from a live count of the
section on disk — never from what the run intended.

The navigation map carries **no** status. It is versioned and append-only instead.

## Staleness — what "unprocessed" means

A UX spec's `absorbed:` list is the record. Each entry is `UC-<NNN>@<version>`, read from that UC's
frontmatter at the moment it was designed.

```text
per feature, per UC in the hub's uc: list:
    UC not in absorbed:                     → NEW      design it
    UC in absorbed: at an OLDER version     → CHANGED  redesign its screens
    UC in absorbed: at the same version     → CURRENT  skip, and say so
```

`sources:` can never go stale, so it can never answer this. `absorbed:` is **re-stamped whole every
run** — it describes what the spec reflects **now**, not what some earlier pass folded in.

**Only stamp a UC that actually got screens this run.** A run that designs 6 of 10 UCs stamps 6,
leaves 4 off, and stays `needs-clarification` naming them. A spec that stamps what it did not design
reads as finished forever.
