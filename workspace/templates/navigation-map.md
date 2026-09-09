---
type: navigation-map
version: 1.0
platform: web           # web | mobile | both — COPIED from the project config
                        # (_bigin/system/project.md frontmatter; absent there reads as `web`).
                        # It decides this file's SHAPE — see `design-navigation.md` § The shell is a platform fact below.
features: []            # every feature slug that has contributed a menu entry
updated:
---

# Navigation Map

The **one** navigation map for this vault, at `04-UIUX/_ux/navigation-map.md`. It is the
menu/navigation system of the product this project is building: every persistent,
directly-reachable entry point a user sees in a nav bar, sidebar, tab strip, tab bar, or flyout, and
which screen it opens. No feature forks it.

It lives under `_ux/`, not inside a design-system folder: navigation is an **experience** decision
`/bigin-generate-design` owns end to end, and this plugin produces no design system at all — colour,
type, spacing, and components are the design team's, or are bound at render time.

**Append-only (D1).** An entry here is a real menu item a screen already depends on being reachable.
Never delete one, and never edit an `id` in place — a screen removed from the flow leaves its entry
to be closed out explicitly (see § Removing an entry), not silently dropped. A **re-nest** (Stage 4's
one structural change) adds the new row and retires the old id in that same section; it never
overwrites the old one, because every screen spec citing the old path would point at nothing.

## The shell is a platform fact

`platform:` in the frontmatter above decides what shape this file is in — **one file either way**
(`design-navigation.md` § The navigation map):

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
`questions.md` § Open Questions, § Changelog — is shared by every shape, and a row from either structure is
referenced there by its `id` plus which structure it lives in.

## Structure
<!-- ONE row per entry, at ANY depth. `id` is a dot-path: a top-level entry is one segment
("settings"); a child is its parent's id plus one segment ("settings.team",
"settings.team.members"). Depth is unlimited — the path IS the tree, so no separate Group/Level
column is needed. A row whose only job is to hold children (a section header with no screen of its
own, e.g. "settings") leaves `Points to` as "—". Order is sibling order under the same parent path,
not a global rank.

Every screen named in `Points to` carries an explicit `(Landing)` or `(Drill-down)` tag — see the
rule just below the table. A render tool then reads the cell mechanically instead of inferring which
name is the door from its position alone.

On `platform: both`, rename this heading `## Structure — Web`. On `platform: mobile`, this section
IS the phone shell — the five-tab cap below applies to it. -->

| Order | id | Label | Points to (screen) | Role(s) | Grounded by | Icon | Added by |
|-------|----|-------|---------------------|---------|-------------|------|-----------|

```text
example, three levels — Order resets per parent, it is not a global rank:
  id                     Label    Points to                                              Role     Grounded by  Order
  settings               Settings —                                                       everyone pattern <shell> 1st under root
  settings.team          Team     Team Members (Landing), Team Member Detail (Drill-down) admin    BR-009       1st under settings
  settings.billing       Billing  Billing (Landing)                                        admin    UC-040 S1    2nd under settings
  settings.team.members  Members  Members (Landing)                                        admin    UC-031 S2    1st under settings.team
```

**A `Points to` cell may list several screens — that is master-detail / drill-down, one entry
covering both.** Every screen named carries an explicit tag, so a render tool reads the cell without
guessing which name is the door:

```text
Points to: <Screen> (Landing)[, <Screen> (Drill-down)]*
```

The **first** screen named is always `(Landing)` — what the entry opens directly. Every screen after
it is `(Drill-down)` — reached only by a control on a screen already in the list (a row click into a
detail, a tab, a wizard step) — never a second row here, and never, downstream, a second persistent
link beside the first. A single-screen cell still carries its tag — `Team Members (Landing)`, never
a bare name: a render tool should never have to special-case "no tag present means Landing."

`Applications Queue (Landing), Application Review (Drill-down)` means the entry opens the queue; a
user reaches Application Review by clicking a row in it. This is the same fact each screen's own UX
spec carries in its `## 2 Screen Inventory` `Screen Type` cell (`design-screens.md` § View ID and
Screen Type) — `(Landing)` here always pairs with `Screen Type: Primary` there, and `(Drill-down)`
here always pairs with `Screen Type: Drill-down` there. The two are written in different files, by
different stages, so they are cross-checked rather than merged into one fact — Stage 6 check 19.

**Every `id` is unique within its own `## Structure` section.** On `web` or `mobile` there is one
section, so that is vault-wide. On `both` the two shells are two trees, not one tree rendered twice:
the same feature legitimately appears as `settings.team` under Web and `more.team` under Mobile, and
neither collides with the other. A child's `id` is always `<parent id>.<segment>` — the parent row
must already exist **in the same section** (append-only builds each tree top-down; a child never
arrives before its parent). `Role(s)` defaults to "everyone"; a narrower value is never invented — it
cites the `BR-###` or the UC's actors that actually draw the line (§ Grounded by, and
`design-grounding.md` § Grounding). `Grounded by` may also cite a `PP-###` for a PLACEMENT decision
(why this entry sits here rather than three levels down) — never for the entry existing, which needs
a screen a UC actually asked for.

`Icon` is a plain NAME a renderer can resolve on its own ("inbox", "calendar") or blank. Never a
token id: there is no design system in this vault to resolve one against
(`design-screens.md` § Semantic style roles).

**The phone shell's five-tab cap.** Wherever a section describes a phone shell — `## Structure` on a
`mobile` project, `## Structure — Mobile` on a `both` one — it holds **at most 5 top-level entries**,
plus per-screen headers and sheets. Depth below a tab is still arbitrary. The cap is a real
constraint, not a style preference: a phone tab bar physically stops being usable past five, so a
sixth top-level candidate means either two features share a tab or one belongs a level down — and
which of those is right is a human call. It goes in this file's `## Open Questions` (owner: team), **never a silent
sixth row.**

## Structure — Mobile
<!-- ONLY on `platform: both` — delete this whole section on `web` (there is no phone shell) and on
`mobile` (the single ## Structure above already IS the phone shell). Same columns, same dot-path id
rules, same append-only discipline, and the same `(Landing)`/`(Drill-down)` tagging as the section
above; the same feature set, mapped onto the tab bar. At most 5 top-level entries (§ the five-tab cap
above).

An entry that exists on one shell and not the other is NORMAL and expected — a web sidebar can carry
an admin area a phone app never surfaces. Say so in that row's `Grounded by` rather than mirroring it
onto the other shell to look symmetrical: a mirrored row is an invented menu item (D3). -->

| Order | id | Label | Points to (screen) | Role(s) | Grounded by | Icon | Added by |
|-------|----|-------|---------------------|---------|-------------|------|-----------|

## Removing an entry
<!-- A screen that no longer exists still leaves its row here (D1). Mark it instead of deleting.
Removing a container row (e.g. "settings") retires its whole subtree — list the container; its
children are implicitly retired with it, not listed again. On `both`, name which structure the id
belongs to (`Web` / `Mobile`) — retiring `more.team` on the phone shell says nothing about
`settings.team` on the web one. On `web` or `mobile` there is only one structure: leave that column
as "—", or drop it. -->

| Structure | id | Status | Since | Why |
|-----------|----|--------|-------|-----|
<!-- Status: active | retired — a retired row stays for history; it is never deleted.
A Stage 4 RE-NEST retires the old id here with `re-nested to <new id>` as its Why, and the new row
is added to ## Structure above. That pair is what keeps a moved entry auditable; editing the id in
place instead loses both the history and every screen spec citing the old path. -->

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
