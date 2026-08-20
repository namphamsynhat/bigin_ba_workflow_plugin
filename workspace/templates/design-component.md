---
type: design-component
name:                   # kebab-case, meaning-based: request-card, entity-picker, wizard-nav
version: 1.0
tokens: []              # every Level-2 / Level-3 token this component cites
used_by: []             # UX-### <screen> — every screen that uses it
updated:
---

# `<Component name>`

**Purpose:** `<one line — the job this component does>`

**Promoted on second use.** A pattern that appears on one screen stays in that screen's spec
(`2-system.md` § B3). Once here it is append-only (D1): add variants and states, never rename or
remove them.

## Anatomy
<!-- The parts, as semantic structure. Token names, never values (D2). -->

| Part | What it is | Token(s) | Required? |
|------|------------|----------|-----------|

## Variants
<!-- Different shapes of the same component. A variant that is really a different component gets
its own file instead. -->

| Variant | When to use | Differs by |
|---------|-------------|------------|

## States
<!-- Each state traces to something: a BR, an exception flow, an entity constraint, or a
directive. A state grounded in nothing is invented — leave it out or ask. -->

| State | Trigger | What the user sees | Grounded by |
|-------|---------|--------------------|-------------|

## Behaviour
<!-- What it does when used: what a control triggers, what it validates, what it announces to a
screen reader. Behaviour that changes what the SYSTEM does is a requirement, not a component —
raise it as a question instead. -->

## Used by
<!-- One line per screen: UX-### — <screen> — <which variant>. Refreshed whenever a new screen
adopts it. -->

## Changelog
- 1.0 (YYYY-MM-DD) — extracted from `<UX-### / screen>`, second use
