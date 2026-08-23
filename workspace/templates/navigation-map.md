---
type: navigation-map
version: 1.0
platform: web           # web | mobile | both — COPIED from the project config
                        # (_bigin/system/project.md frontmatter; absent there reads as `web`).
                        # It decides this file's SHAPE — see § The shell is a platform fact below.
features: []            # every feature slug that has contributed a menu entry
updated:
---

# Navigation Map

The **one** navigation map for this vault, at `04-UIUX/_design-system/navigation-map.md`. It is the
menu/navigation system of the product this project is building: every persistent,
directly-reachable entry point a user sees in a nav bar, sidebar, tab strip, tab bar, or flyout, and
which screen it opens. No feature forks it.

**Append-only (D1), same as the design system.** An entry here is a real menu item a screen already
depends on being reachable. Never delete or rename one — a screen removed from the flow leaves its
entry to be closed out explicitly (see § Removing an entry), not silently dropped.

## The shell is a platform fact

`platform:` in the frontmatter above decides what shape this file is in — **one file either way**
(design-conventions.md § The navigation map):

```text
web     ## Structure                 a persistent sidebar / nav-bar shell. Arbitrary depth.
mobile  ## Structure                 a TAB BAR — at most 5 top-level entries — plus per-screen
                                     headers and sheets. Depth below a tab is still arbitrary.
both    ## Structure — Web           BOTH sections, in this one file, one table each, SAME columns,
        ## Structure — Mobile        mapping the SAME feature set onto each shell.
```

On `web` or `mobile`, keep the single `## Structure` heading below and delete
`## Structure — Mobile`. On `both`, rename `## Structure` to `## Structure — Web` and keep
`## Structure — Mobile` as the second section. Everything after them — § Removing an entry,
§ Open Questions, § Changelog — is shared by every shape, and a row from either structure is
referenced there by its `id` plus which structure it lives in.

## Structure
<!-- ONE row per entry, at ANY depth. `id` is a dot-path: a top-level entry is one segment
("settings"); a child is its parent's id plus one segment ("settings.team",
"settings.team.members"). Depth is unlimited — the path IS the tree, so no separate Group/Level
column is needed. A row whose only job is to hold children (a section header with no screen of its
own, e.g. "settings") leaves `Points to` as "—". Order is sibling order under the same parent path,
not a global rank.

On `platform: both`, rename this heading `## Structure — Web`. On `platform: mobile`, this section
IS the phone shell — the five-tab cap below applies to it. -->

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

**Every `id` is unique within its own `## Structure` section.** On `web` or `mobile` there is one
section, so that is vault-wide. On `both` the two shells are two trees, not one tree rendered twice:
the same feature legitimately appears as `settings.team` under Web and `more.team` under Mobile, and
neither collides with the other. A child's `id` is always `<parent id>.<segment>` — the parent row
must already exist **in the same section** (append-only builds each tree top-down; a child never
arrives before its parent). `Role(s)` defaults to "everyone"; a narrower value is never invented — it
cites the `BR-###` or the UC's actors that actually draw the line (§ Grounded by, and
design-conventions.md § Grounding).

**The phone shell's five-tab cap.** Wherever a section describes a phone shell — `## Structure` on a
`mobile` project, `## Structure — Mobile` on a `both` one — it holds **at most 5 top-level entries**,
plus per-screen headers and sheets. Depth below a tab is still arbitrary. The cap is a real
constraint, not a style preference: a phone tab bar physically stops being usable past five, so a
sixth top-level candidate means either two features share a tab or one belongs a level down — and
which of those is right is a human call. It goes in § Open Questions (owner: team), **never a silent
sixth row.**

## Structure — Mobile
<!-- ONLY on `platform: both` — delete this whole section on `web` (there is no phone shell) and on
`mobile` (the single ## Structure above already IS the phone shell). Same columns, same dot-path id
rules, same append-only discipline as the section above; the same feature set, mapped onto the tab
bar. At most 5 top-level entries (§ the five-tab cap above).

An entry that exists on one shell and not the other is NORMAL and expected — a web sidebar can carry
an admin area a phone app never surfaces. Say so in that row's `Grounded by` rather than mirroring it
onto the other shell to look symmetrical: a mirrored row is an invented menu item (D3). -->

| Order | id | Label | Points to (screen) | Role(s) | Grounded by | Icon/token | Added by |
|-------|----|-------|---------------------|---------|-------------|------------|-----------|

## Removing an entry
<!-- A screen that no longer exists still leaves its row here (D1). Mark it instead of deleting.
Removing a container row (e.g. "settings") retires its whole subtree — list the container; its
children are implicitly retired with it, not listed again. On `both`, name which structure the id
belongs to (`Web` / `Mobile`) — retiring `more.team` on the phone shell says nothing about
`settings.team` on the web one. On `web` or `mobile` there is only one structure: leave that column
as "—", or drop it. -->

| Structure | id | Status | Since | Why |
|-----------|----|--------|-------|-----|
<!-- Status: active | retired — a retired row stays for history; it is never deleted. -->

## Open Questions
<!-- A menu placement, nesting depth, or role split that looks wrong, or that a screen's report
left ungrounded. Raised here, never resolved by a silent edit — a human decides. A sixth top-level
candidate on a phone shell always lands here (§ the five-tab cap), as does a feature that seems to
belong on one shell but not the other.

Format:
- [ ] Q: <question> (owner: team) (ref: <id>[, <Web|Mobile> — on `both`])
      A: -->

## Changelog
- 1.0 (YYYY-MM-DD) — navigation map created
