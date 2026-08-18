# Design Conventions

The **design** rulebook: what a screen spec is, what a token is, what a prototype prompt may contain.

**This file is deliberately separate from `conventions.md`.** That file is the **requirement**
rulebook — what a use case is, when a signal becomes a rule, who may approve scope. This one is the
**design** rulebook. They never merge:

```text
a rule about WHAT THE SYSTEM DOES        → conventions.md          (requirement side)
a rule about HOW A SCREEN LOOKS/READS    → this file               (design side)
a "design rule" that decides behaviour   → it is a requirement. It is in the wrong file.
```

Read only the sections your stage needs.

| Stage | Sections |
|---|---|
| `1-scope` | Paths · Write map · Design status · Staleness |
| `2-system` | The design system · Token architecture · The navigation map |
| `3-screens` | The UX spec · Screen spec · Grounding · Open questions · The navigation map |
| `4-prompt` | Prototype prompt |
| `5-close` | Design status · Write map · Staleness · The navigation map |

## Paths

Project-relative, from the repo root.

**Design side — this stage owns these.**

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{ux_dir}` | `04-UIUX/` | one spec per feature: `UX-<NNN> <Feature>.md` |
| `{design_system_dir}` | `04-UIUX/_design-system/` | **one, vault-wide**, shared by every feature |
| `{tokens_file}` | `04-UIUX/_design-system/design-tokens.md` | the token file |
| `{components_dir}` | `04-UIUX/_design-system/components/` | one `<component>.md` per shared component |
| `{nav_map_file}` | `04-UIUX/_design-system/navigation-map.md` | the vault's menu/navigation system |
| `{design_stages_dir}` | `_bigin/stages/design/` | `1-scope`, `2-system`, `3-screens`, `4-prompt`, `5-close` |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | this file |
| `{template_ux}` | `_bigin/templates/ux-spec.md` | |
| `{template_design_system}` | `_bigin/templates/design-system.md` | |
| `{template_component}` | `_bigin/templates/design-component.md` | |
| `{template_nav_map}` | `_bigin/templates/navigation-map.md` | |

**Requirement side — inputs. Read them; do not rewrite them.**

| Variable | Path | What design takes from it |
| :--- | :--- | :--- |
| `{uc_dir}` | `01-Requirements/_ucs/` | the flow the screens serve — `## 2` steps, `## 3` branches |
| `{br_dir}` | `01-Requirements/_brs/` | validations and error states |
| `{entity_dir}` | `01-Requirements/_entities/` | the fields a form actually has |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | client-stated durable preferences |
| `{hub_dir}` | `01-Requirements/_features/` | `## Design Directives` in, `## UX Spec` out |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | the slug registry |

Missing `_bigin/conventions/`, `_bigin/stages/design/`, or `_bigin/templates/` → stop and say
`/bigin-new-project` must run first. A subagent that cannot read its stage guide still writes a
screen, just one following no rule.

## Write map — what design may touch

```text
WRITE   {ux_dir}                      the UX spec (create, or update in place)
        {design_system_dir}           tokens + components — ADD ONLY
        {nav_map_file}                menu entries — ADD ONLY (part of {design_system_dir})
        hub ## UX Spec                link + status
        hub uiux:                     the UX-### id
        hub ## Design Directives      Status: open → reflected, on rows a screen really implements
        hub ## Open Questions / Gates design questions
        hub ## Notes / History · ## Changelog   one line each

READ    every path in the requirement table above

NEVER   a UC's ## 1-## 6 · a BR's rule statement · an EN field list
        DESIGN-PRINCIPLES.md          (client-stated only — research findings are not client words)
        a hub's Signal Log · ## Requirement Readiness · status: · uc: · br:
        FEATURES.md
```

**One sanctioned exception.** When a UC is **not** `approved`, append **one** line to its
`## Discussion` citing the UX spec as supporting visual evidence. Nothing else, ever, and nothing at
all on an `approved` UC.

## The six design hard rules

```text
D1  The design system is APPEND-ONLY. Never delete or rename a token, component, or nav entry.
D2  A screen spec names TOKENS, never raw values. No hex, no px, no font name.
D3  Every screen, element, and state is GROUNDED (see § Grounding). Ungrounded → a question.
D4  Requirement content is READ-ONLY. Design never edits a UC, a BR, or an entity.
D5  Never write status: accepted. A human accepts a design; an agent never does.
D6  A prototype prompt STANDS ALONE. No UC-/BR-/EN-/PP-/UX-/INT- id inside the prompt body.
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

The design system files carry **no** status. They are versioned and append-only instead.

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

## The UX spec

`{ux_dir}/UX-<NNN> <Feature>.md`, `type: uiux`, from `{template_ux}`. **One per feature** — never a
second one for a feature that already has one; a re-run updates it in place (bump `version`, append
a `## Changelog` line).

A **cross-feature UC** is designed once, in the UX spec of its `primary_feature`. Every other slug
in the UC's `features:` gets the same `## UX Spec` pointer on its hub. Same write-ownership rule the
UC itself follows.

Sections: `## 1 Design Brief` · `## 2 Screen Inventory` · `## 3 Screen Specs` · `## 4 Flows` ·
`## 5 Design System Usage` · `## 6 Open Questions` · `## Prototype Prompt — Claude design` ·
`## Prototype Prompt — Figma Make` · `## Changelog`.

## The design system

**One** design system, at `{design_system_dir}`, shared by the whole vault. Two modes:

```text
{tokens_file} absent  → BOOTSTRAP  create it from {template_design_system}; the first screens seed it
{tokens_file} present → EXTEND     load it, reuse it, ADD what is genuinely new
```

Extend means: reference an existing token or component **first**; add only when nothing there fits;
dedup before adding so two names never mean the same thing; bump `version` and append a
`## Changelog` line naming this run's features.

**Never delete, never rename** (D1) — a screen built last month cites that name. A token that looks
wrong or duplicated becomes an Open Question owned by the team, never a silent edit.

## Token architecture — three levels

```text
Level 1  raw        --color-blue-600: #2563eb          a value with no meaning
Level 2  semantic   --color-action-primary: L1 blue-600  what it MEANS      ← screens use these
Level 3  component  --button-primary-bg: L2 action-primary  where it is used ← components use these
```

A screen spec cites Level 2 or Level 3 by **name**. A raw value in a screen spec is D2 broken: the
value now lives in two places and the next screen drifts from it.

## The navigation map

**One** navigation map, at `{nav_map_file}`, shared by the whole vault — the menu/navigation system
for the platform or project: every persistent, directly-reachable entry point (a nav bar item, a
sidebar link, a tab, a flyout child) and the screen it opens. Same two modes as the design system:

```text
{nav_map_file} absent  → BOOTSTRAP  create it from {template_nav_map}; the first screens seed it
{nav_map_file} present → EXTEND     load it, reuse its tree, ADD new entries screens actually need
```

**Arbitrary depth, via a path id.** The map is not fixed at "group → entry" — a real IA nests as
deep as "Settings → Team → Members". One row per entry, at any depth; its `id` is a dot-path, the
parent's `id` plus one segment (`settings`, then `settings.team`, then `settings.team.members`). The
path **is** the tree: no separate level or parent column, and no cap on how deep it goes. A row can
be a pure container (a section header with children but no screen of its own — `Points to: —`), a
leaf (a screen, no children), or both.

**Not every screen gets an entry.** A screen a user reaches directly from the menu — at whatever
depth — gets one; a screen reached only *through* another screen (a detail opened from a list, a
step inside a wizard, a modal) does not — it is reachable through its parent, and a menu entry for it
is a duplicate way in that drifts from the real IA the first time one of the two paths changes.

```text
directly reachable from the menu, on its own (top-level or nested)  → gets an entry
reached only via another screen's control                          → no entry (it is a destination,
                                                                       not a menu item)
```

Every entry is **grounded** the same way any other design decision is (§ Grounding below): a role
split traces to a `BR-###` or a UC's actors, a nesting decision traces to a stated preference or an
existing branch of the tree, and a label that nothing in the flow calls for is an Open Question,
never an invented menu.

**Append-only (D1).** A screen that stops existing does not get its row deleted — see the template's
§ Removing an entry: mark it `retired`, keep the row, keep the history. Retiring a container retires
its whole subtree implicitly; its children are not re-listed. Deleting a row breaks nothing
technically, but it also erases the record of why the IA looks the way it does.

## Screen spec — semantic structure only

One entry per screen in `## 3`:

```text
purpose      one line: what the user achieves here
serves       UC-<NNN> S<n>, S<n> …   the steps this screen delivers
regions      header / nav / main / aside / footer — semantic HTML elements
elements     per element: what it is · the content or copy · the token(s) it uses
             · the entity field it renders, when it renders one
states       empty · loading · validation-error · permission-denied · success
             each from a BR, an exception flow, or an entity's required fields — never invented
interactions what each control does, and which screen or state it leads to
```

**Copy is content, not styling** — real words a user reads, in the client's language, not `Lorem`.

## Grounding — the test that keeps design out of the requirements

Every non-trivial decision (a screen existing, a field appearing, a state, a nav grouping) traces to
exactly one of:

```text
1  a REQUIREMENT   a UC step / branch, a BR, or an EN field         → cite the id
2  a PATTERN       an existing screen or component in this vault    → name it
3  a PREFERENCE    a DESIGN-PRINCIPLES row or a hub directive       → cite the row #
```

None of the three → **it is not yours to settle**. Write an Open Question (D3). An invented screen
is scope nobody asked for, and it looks exactly like a designed one.

An entity that is still `proposed`/`draft` grounds a decision as a **known gap**, not settled fact —
say so next to the field list rather than treating it as final.

## Open questions

Design questions live on the UX spec's `## 6`, and are mirrored on the hub's
`## Open Questions / Gates`. Same sentence in both places — a re-worded mirror reads as a second
question, gets answered twice, and can never be paired back up.

```text
- [ ] Q: <self-contained question, plain business language> (owner: client|team) (ref: UX-###)
      A:
```

Never copy a question that is already open on the UC's `## 5`. If the answer would change **what the
system does** rather than how it looks, say so in the question and in the report: it is a
requirement gap, and `/bigin-transform-signal` owns it.

## Prototype prompt

Two blocks per UX spec, from the same screens: **Claude design** and **Figma Make**. Both must be
self-contained (D6) — pasteable into a tool that has never seen this vault.

```text
inline    the token values (with a plain-language note on each), the screen list, per-screen
          structure and copy, the flow order, the states, the sample data
expand    every vault id into words: "UC-012 S4" → "the step where the reviewer approves the request"
omit      nothing the tool needs; a prompt that says "per the use case" produces the wrong screen
```

Keep the two blocks consistent — same screens, same tokens, same copy. They differ only in how each
tool likes to be addressed, not in what is being asked for.
