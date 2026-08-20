---
type: navigation-map
version: 1.0
features: []            # every feature slug that has contributed a menu entry
updated:
---

# Navigation Map

The **one** navigation map for this vault, at `04-UIUX/_design-system/navigation-map.md`. It is the
menu/navigation system for the platform: every persistent, directly-reachable entry point a user
sees in a nav bar, sidebar, tab strip, or flyout, and which screen it opens. No feature forks it.

**Append-only (D1), same as the design system.** An entry here is a real menu item a screen already
depends on being reachable. Never delete or rename one — a screen removed from the flow leaves its
entry to be closed out explicitly (see § Removing an entry), not silently dropped.

## Structure
<!-- ONE row per entry, at ANY depth. `id` is a dot-path: a top-level entry is one segment
("settings"); a child is its parent's id plus one segment ("settings.team",
"settings.team.members"). Depth is unlimited — the path IS the tree, so no separate Group/Level
column is needed. A row whose only job is to hold children (a section header with no screen of its
own, e.g. "settings") leaves `Points to` as "—". Order is sibling order under the same parent path,
not a global rank. -->

| Order | id | Label | Points to (screen) | Role(s) | Grounded by | Icon/token | Added by |
|-------|----|-------|---------------------|---------|-------------|------------|-----------|

```text
example, three levels — Order resets per parent, it is not a global rank:
  id                      Label     Points to  Role    Grounded by  Order (among its siblings)
  settings                Settings  —          everyone  pattern <shell>   1st under root
  settings.team           Team      UX-014     admin     BR-009            1st under settings
  settings.billing        Billing   UX-020     admin     UC-040 S1         2nd under settings
  settings.team.members   Members   UX-015     admin     UC-031 S2         1st under settings.team
```

**Every `id` is unique, vault-wide.** A child's `id` is always `<parent id>.<segment>` — the parent
row must already exist in this table (append-only builds the tree top-down; a child never arrives
before its parent). `Role(s)` defaults to "everyone"; a narrower value is never invented — it cites
the `BR-###` or the UC's actors that actually draw the line (§ Grounded by, and
design-conventions.md § Grounding).

## Removing an entry
<!-- A screen that no longer exists still leaves its row here (D1). Mark it instead of deleting.
Removing a container row (e.g. "settings") retires its whole subtree — list the container; its
children are implicitly retired with it, not listed again. -->

| id | Status | Since | Why |
|----|--------|-------|-----|
<!-- Status: active | retired — a retired row stays for history; it is never deleted. -->

## Open Questions
<!-- A menu placement, nesting depth, or role split that looks wrong, or that a screen's report
left ungrounded. Raised here, never resolved by a silent edit — a human decides.

Format:
- [ ] Q: <question> (owner: team) (ref: <id>)
      A: -->

## Changelog
- 1.0 (YYYY-MM-DD) — navigation map created
