---
type: navigation-map
version: 1.0
features: []            # every feature slug that has contributed a menu entry
updated:
---

# Navigation Map

The **one** navigation map for this vault, at `04-UIUX/_design-system/navigation-map.md`. It is the
menu/navigation system for the platform: every persistent, directly-reachable entry point a user
sees in a nav bar, sidebar, or tab strip, and which screen it opens. No feature forks it.

**Append-only (D1), same as the design system.** An entry here is a real menu item a screen already
depends on being reachable. Never delete or rename one — a screen removed from the flow leaves its
entry to be closed out explicitly (see § Removing an entry), not silently dropped.

## Structure
<!-- The menu tree itself: groups, then entries under each. A group with no entries yet is fine on
bootstrap — do not pre-build a full IA. Order is the order items appear to the user. -->

| Order | Group | Entry label | Points to | Role(s) | Added by |
|-------|-------|-------------|-----------|---------|----------|

## Entry detail
<!-- One row per entry above, with what grounds it. An entry with no ground is an invented menu
item — ask instead (design-conventions.md § Grounding). -->

| Entry label | Screen (UX-###) | Grounded by | Icon/token | Notes |
|--------------|------------------|-------------|------------|-------|

## Access rules
<!-- Which role sees which group/entry, when it differs from "everyone". Cite the BR-### or the
UC's § 1 actors that draw the line — never invent a permission split. -->

| Group / entry | Visible to | Grounded by |
|----------------|------------|-------------|

## Removing an entry
<!-- A screen that no longer exists still leaves its row here (D1). Mark it instead of deleting: -->

| Entry label | Status | Since | Why |
|--------------|--------|-------|-----|
<!-- Status: active | retired — a retired row stays for history; it is never deleted. -->

## Open Questions
<!-- A menu placement, grouping, or role split that looks wrong, or that a screen's report left
ungrounded. Raised here, never resolved by a silent edit — a human decides. -->

- [ ] Q: <question> (owner: team) (ref: <entry label>)
      A:

## Changelog
- 1.0 (YYYY-MM-DD) — navigation map created
