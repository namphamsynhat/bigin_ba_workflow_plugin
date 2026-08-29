<!-- RETIRED — nothing in this plugin instantiates this template any more.

/bigin-generate-design produces the EXPERIENCE (actors, screens, states, navigation, and the flows
between them) and no visual system at all: a screen element names a semantic ROLE from a closed list
(`design-screens.md` § Semantic style roles), and colour, type, spacing, and
components are supplied by the design team or bound at render time by /bigin-render-design-od.

Kept, unreferenced, for two reasons: a vault materialized before this change may still have files
instantiated from it under 04-UIUX/_design-system/ (nothing reads them, and nothing deletes them),
and a design team supplying their own system may want a shape to follow. Do not add to it, do not
cite it from a stage guide, and do not treat its absence as a gap. -->

---
type: design-system
version: 1.0
features: []            # every feature slug whose screens have contributed to this system
updated:
---

# Design System

The **one** design system for this vault, at `04-UIUX/_design-system/`. Every feature's screens
reference it; no feature forks it.

**Append-only (D1).** A token or component here is cited by every screen already specced against it.
Never delete one, never rename one, never regenerate this file. A token that looks wrong, duplicated,
or unused becomes an Open Question on a UX spec (owner: team) — never a silent edit.

## Foundations
<!-- The client's own stated preferences, from 01-Requirements/DESIGN-PRINCIPLES.md rows with
Status: active. One line each, in the client's words, citing the row #. This section is a MIRROR:
the register is the source, and this stage never writes back to it. -->

| # | Foundation | In the client's words | Source |
|---|------------|------------------------|--------|

## Level 1 — Raw values
<!-- A value with no meaning attached. Nothing outside this file cites a Level-1 name. -->

| Name | Value | Notes |
|------|-------|-------|

## Level 2 — Semantic tokens
<!-- What a value MEANS. This is what screen specs cite. Name for meaning, never for appearance:
--color-action-primary survives a rebrand; --color-brand-blue does not. -->

| Token | Level 1 value | Means | Added by |
|-------|---------------|-------|----------|

## Level 3 — Component tokens
<!-- Where a semantic token is USED. Cited by component specs. -->

| Token | Level 2 token | Used on | Added by |
|-------|---------------|---------|----------|

## Components
<!-- Index only — each component has its own file in components/<component>.md. A pattern is
promoted here on its SECOND use, never its first (2-system.md § B3). -->

| Component | File | Variants | Used by |
|-----------|------|----------|---------|

## Open Questions
<!-- Tokens or components that look wrong, duplicated, or unused. Raised here, never fixed here —
D1 forbids the edit, so a human decides.

Format:
- [ ] Q: <question> (owner: team) (ref: <token/component>)
      A: -->

## Changelog
- 1.0 (YYYY-MM-DD) — design system created
