# The navigation contract — one entry, first screen is the door

`{nav_map_file}`'s `## Structure` is the only nav authority a render ever gets, and a `Points to`
cell holding more than one screen name is **master-detail / drill-down, not a flat list** —
`design-navigation.md` § The navigation map names it. Open Design's own agent never reads that
convention file; the assembly prompt is the only place this rule reaches it, so it has to be stated
in full every time, not gestured at.

## § What actually went wrong once

A `Points to` cell read `Applications Queue, Application Review`: one nav-map row, one menu entry,
the queue as the door and the review reached by clicking a row in it. Asked only to "follow the
navigation map," Open Design's assembly agent turned the two names into two separate sidebar
links — `Applications Queue` and `Application Review` sitting as siblings in the menu. The same
pattern repeated on every multi-screen row in that map: a 7-screen `Wallets` entry became 7 sidebar
links, a 4-screen `Vendor Management` entry became 4, including screens the map's own changelog had
already noted were reached only by a row click and deliberately given no entry of their own. Nothing
in the prompt had told the rendering agent how to read a cell with more than one name in it.

## § The block to quote

Quote this verbatim into the Step 3 assembly prompt, and into any per-feature prompt whose synced UX
spec's own `## 5 Navigation & Flow Review` names more than one screen per entry:

```text
NAVIGATION — one persistent link per navigation-map row, never one per screen.

  a navigation-map row's `Points to` cell may list several screens — that is master-detail /
  drill-down, one menu entry covering both, not a flat list of destinations.

  the FIRST screen named is what the menu entry opens directly → give it the ONE persistent
      sidebar/nav link, labelled with the row's own Label
  every screen named AFTER it is reached ONLY by a control on a screen already in that list
      (a row click into a detail, a tab, a wizard step, a "Review" button) → it gets NO sidebar
      link, NO menu item, and NO entry of its own anywhere in the nav shell

  example: `Points to: Applications Queue, Application Review` means ONE sidebar link
  ("Applications"), opening Applications Queue; Application Review is reached by clicking a row
  in the queue and never appears in the sidebar itself.

  a screen not named in ## Structure at all follows the same rule: it is reached only through
  another screen already wired in, never given a persistent link because it exists.
```

## § The gate

```bash
"$SKILL_DIR/scripts/check-navigation.py" {nav_map_file} <rendered-file-or-dir> [...]
```

Parses the nav map's `## Structure` rows and flags any rendered file where a **drill-down-only**
screen (the 2nd+ name in some row's `Points to` cell, or a screen `## Structure` never names at all)
turns up as text inside what looks like its own clickable nav element — an `<a>`/`<button>` inside a
`nav`/`sidebar`/`menu`-named container, or its own entry in a JS nav/menu data structure. It is a
**heuristic, not a hard gate** — rendered HTML shapes vary too much between runs for a certain
parse — so a finding is a "look at this" for the human reviewing the render, the same way a contrast
warning is, not an automatic fail.

| Exit | Meaning |
| :--- | :--- |
| 0 | no drill-down-only screen text found inside a nav-shaped element |
| 1 | at least one finding — review each: a page title reusing the same words is a false positive, a second sidebar link is the real failure |
| 2 | could not run — nav map or targets not found |
