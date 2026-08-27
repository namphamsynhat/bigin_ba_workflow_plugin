# Stage 2 — The navigation map: seed it first, extend it after

```text
runs: orchestrator, TWICE — Part A before the screens, Part B after them
in:   the existing {nav_map_file} · each in-scope feature's open ## Pain Points rows
      · Stage 3's reported nav candidates · the platform Stage 1 announced
out:  a navigation shell the screens can join, then a slightly bigger one
never: deleting a nav entry · renaming one · rewriting the file from scratch
       · re-reading the project config to decide the platform
       · a token, a colour, a type scale, or a component — none of those exist in this pipeline
```

Read `{design_conventions}` § The navigation map, § User flows and pain points, and § Platform first.

**The platform arrives as an instruction, not a lookup.** Stage 1 read `platform:` once and passed
it here; this stage never opens `_bigin/system/project.md` to check. It decides one thing below —
what shape the navigation map's `## Structure` takes (A1, B3).

**Why twice.** A screen worker needs the tree that already exists so a new entry joins a branch
instead of starting a parallel one — so the map is loaded before the screens. But screens are also
what *discover* new places a menu has to reach. So: seed, design, then fold the new entries back in.

**There is no design system in this stage, and no Part for one.** Colour, type, spacing, and
components are supplied by a design team or bound at render time
(`{design_conventions}` § Rendering is a separate step). What this stage owns is where a user can
**go**, which is an experience decision this pipeline makes end to end.

---

## Part A — Seed (before Stage 3)

### A1. Bootstrap, or load

```text
{nav_map_file} absent:
    create {ux_system_dir}/
    instantiate {nav_map_file} from {template_nav_map}
    version 1.0
    stamp its frontmatter platform: with the value Stage 1 announced
    shape its ## Structure section(s) for that platform, per the template's own
        § The shell is a platform fact

{nav_map_file} present:
    read its ## Structure whole — the tree already exists, at whatever depth it has grown to;
    reuse a branch before starting a parallel one
    NEVER overwrite it. NEVER re-instantiate the template over it.
```

**The shell is a platform fact** (`{design_conventions}` § The navigation map → "The shell is a
platform fact"). One file either way; what differs is the `## Structure` it holds:

```text
web     ## Structure               the sidebar / nav-bar shell. Arbitrary depth, as today.
mobile  ## Structure               a TAB BAR — at most 5 top-level entries — plus per-screen headers
                                   and sheets. Depth below a tab is still arbitrary; a 6th tab is
                                   not a nav decision (B3).
both    ## Structure — Web         BOTH sections, in ONE file, one table each, same columns,
        ## Structure — Mobile      mapping the SAME feature set onto each shell.
```

`{template_nav_map}` ships both headings, and its own § The shell is a platform fact says which to
keep and which to delete at instantiation. Do that there; do not re-derive it here.

**On load, the file already has a shape**, and its frontmatter `platform:` records which one:

```text
stamped platform: matches this run's    → nothing to shape. Load the tree and continue.
no platform: in the frontmatter at all  → the map predates the field. An unsuffixed ## Structure is
                                          the WEB shell by definition — `web` is the absent-platform
                                          default. Stamp this run's platform, then shape if the next
                                          line applies.
this run is `both`, the file holds one  → SHAPE it: suffix the existing heading `— Web`, append a
web ## Structure                          new, empty ## Structure — Mobile beside it, re-stamp
                                          platform: both
```

**Shaping adds; it never rebuilds.** No row moves, no `id` changes, no `Grounded by` is re-derived,
and nothing in the existing tree is reconsidered because a second shell now exists. Part B closes it
out (B4). A populated `## Structure` is never re-shaped *into* the other platform's shell — a
project that gains a platform grows the second section (B5).

### A2. Read the open pain points, per in-scope feature

Stage 1 counted them; this is where the statements get read. Per feature on the work-list, take its
hub's `## Pain Points` rows that are **not** resolved:

```text
PP-###  |  the statement, in the client's own words  |  which feature carries it
```

**They are read here so the shell is shaped around them, not bolted on afterwards.** A pain point
like "reviewers can never find what they were working on yesterday" is a navigation fact before it is
a screen fact — it says something has to be reachable in one move, and the tree either allows that or
it does not.

```text
what a pain point may do HERE     say a destination must be directly reachable rather than nested
                                  three deep · say two features belong in one place because the
                                  client works them together · rank sibling order

what it may NEVER do              create a nav entry pointing at a screen no UC asked for. That is
                                  ground 1b, and 1b alone grounds nothing
                                  ({design_conventions} § Grounding)
```

**The register is read-only** (`{design_conventions}` § Write map). This stage cites a `PP-###`; it
never marks one resolved, never edits a statement, and never adds a row.

Nothing to read — a feature with no open pain points — is normal and common. Say so once in the
report; it is not a gap.

### A3. Do not pre-build the tree

The shell that exists after Part A is whatever was already there, plus nothing. **Part B is where
real screens add the entries a real flow turns out to need.** A speculative IA — a Dashboard, a
Settings group, a Reports section seeded because products usually have them — is an invented
navigation, unremovable once written (D1), and every one of those entries reaches a client looking
like a decision somebody made.

### A4. Nothing to say, say nothing

Loading an existing `## Structure` is not itself a change: no version bump, no changelog line. That
is the normal case in `extend` mode.

The one exception is **shaping**: adding the second `## Structure` section a `both` project needs,
and suffixing the existing one (A1), changes the file even on a run that adds no rows. It gets a
version bump and a changelog line in Part B's close-out like anything else.

---

## Part B — Extend (after Stage 3 reports)

Stage 3's subagents **never write here** — they report candidates. This part applies them, one at a
time, in the orchestrator.

### B1. Dedup before adding — every single candidate

```text
per candidate entry:
    does an existing entry already point at the same screen?   → nothing to add. Tell Stage 5 the
                                                                 existing id
    does an existing branch already cover this area?           → nest under it; never start a
                                                                 parallel branch beside it
    genuinely new?                                              → add it
```

Two entries into one screen is the failure this check exists for. Both are correct the day they are
written, neither can be removed (D1), and they drift the first time one of the two paths changes.

### B2. Which screens even get an entry

```text
per reported nav candidate:
    is it a screen reached only through another screen?       → NOT an entry (§ Structure test in
                                                                design-conventions.md § The
                                                                navigation map) — decline it, and
                                                                say so in the report
    is it directly menu-reachable and genuinely new?          → mint its id and add ONE row
```

**A feature normally contributes 0–2 entries**, not one per screen. Zero is common and correct.

### B3. Mint the id, and place the row

Where it nests, not just whether it exists:

```text
reported parent already in ## Structure   → id = <parent id>.<new segment>
reported parent does NOT exist yet        → mint the parent container row FIRST (Points to: —),
                                             then the child under it — never skip straight to a
                                             child whose parent id nothing resolves to
no parent reported (a new top-level item) → id = <one segment>, no dot
```

A role split on the entry (who sees it) goes in that row's `Role(s)` cell, citing the `BR-###` or
the UC's actors — never invented to "look complete". A `PP-###` that argued for the placement goes in
`Grounded by` beside whatever grounded the entry's existence — a pain point never grounds the entry
by itself (A2).

**Which `## Structure` the row goes in** — asked before the `id`, on `both`:

```text
web     the single ## Structure
mobile  the single ## Structure
both    the section for the shell the candidate was reported against. A web-only admin area lands in
        ## Structure — Web alone, and that is a complete, correct outcome — not half a job.
```

**An entry on one shell and absent from the other is normal**, and its `Grounded by` says why.
Mirroring it into the other section so the two look symmetrical invents a menu item on a shell
nothing asked to reach it from: ungrounded (D3), and unremovable once written (D1). Two sections are
two trees, not one tree rendered twice.

`id` uniqueness follows the same line: an `id` is unique **within its own `## Structure` section**,
so one feature legitimately sits at `settings.team` on web and `more.team` on mobile. The minting
rules above apply **per section** — a parent row must already exist in the *same* section as its
child, and a row in the web tree never resolves a mobile child's parent.

**Five top-level entries is a hard cap on a mobile shell** — `mobile`'s `## Structure`, or `both`'s
`## Structure — Mobile`:

```text
fewer than 5 top-level entries, candidate is top-level  → add it
already 5, and the candidate is top-level               → do NOT add a 6th row. Raise an Open Question
                                                          on {nav_map_file} (owner: team): do two of
                                                          these share a tab, or does one belong a level
                                                          down? Report it, and tell Stage 6 this screen
                                                          has no menu entry yet.
the candidate nests under an existing tab               → not top-level; the cap does not apply. Mint
                                                          it under its parent as usual.
```

A phone tab bar physically stops being usable past five, so a sixth candidate means either two
features share a tab or one belongs a level down — and which of those is right is a human call,
never a silent sixth row. The cap is a platform constraint, not a style preference, and it does not
apply to a web sidebar, which nests as deep as the real IA does.

### B4. Close out the file

```text
bump {nav_map_file} version — only if an entry was actually added or RE-NESTED (Stage 4), or the
                              file was SHAPED (A1)
append a ## Changelog line: date · entries added · which features drove them
                            on `both`, name WHICH section each entry landed in — a line reading
                            "added Reports" cannot be read back against two trees
                            on a shaping run, say so: "## Structure suffixed — Web,
                            ## Structure — Mobile added, no entries yet"
                            on a run where Stage 4 re-nested a row, name the old id and the new one
```

On `both`, close out **both** sections in the same pass, and let their row counts differ. A section
left empty because no screen this run needed a mobile menu entry is a real result — say it in the
report rather than filling it to match the other one.

### B5. What is never allowed here

```text
delete a nav entry                      → forbidden (D1) — retire it instead (§ Removing an entry),
                                          never delete its row
rename a nav entry's id                 → forbidden (D1) as a silent edit. A RE-NEST by Stage 4 is
                                          the one sanctioned change, and it retires the old id
                                          explicitly rather than overwriting it
regenerate the file "to tidy it up"     → forbidden. Every screen spec already cites these ids.
re-shape a populated ## Structure       → forbidden. A platform change GROWS the second section
                                          (A1); it never rewrites the first one's rows.
add a 6th tab to a phone shell          → forbidden. It is an Open Question, owner: team (B3).
seed a token, a colour, or a component  → there is nowhere to write one and nothing to cite it.
                                          A screen needing a visual decision names a semantic ROLE
                                          ({design_conventions} § Semantic style roles)
```

An entry that looks wrong, duplicated, or unused becomes a line in this file's own `## Open Questions`
(owner: team) and a line in the run report. It is a **system** question, not a feature one, so it does
not go on a UX spec or a hub — and it never becomes a silent edit.

## Failure modes

- **Wiping and regenerating the navigation map.** Every screen spec citing an id breaks at once, and
  nothing in the vault records that it happened.
- **Renaming an id to a better one.** Same failure, quieter. Stage 4's re-nest is the only sanctioned
  id change, and it retires the old row rather than overwriting it.
- **Seeding a full menu tree on bootstrap.** The IA comes from real screens; a speculative one is a
  navigation nobody asked for, and D1 means it is there forever.
- **Giving a sub-screen its own nav entry.** It is reached through its parent; a second way in
  drifts from the real navigation the first time one path changes.
- **Minting a child id whose parent id resolves to nothing.** `settings.team.members` with no
  `settings.team` row is an orphan branch — `6-close.md`'s navigation check exists to catch it.
- **Letting a subagent write the navigation map.** Two features run at once and both add a "Reports"
  menu entry under different groups.
- **Bumping the version on a run that added nothing.** The changelog stops meaning anything.
- **Adding a sixth top-level entry to a mobile shell.** The cap is physical, not stylistic, and the
  sixth row can never be removed (D1) — so the tab bar is permanently unusable and the record says a
  design decided it.
- **Mirroring an entry onto the other shell for symmetry.** On `both`, an entry the web sidebar
  carries and the phone app does not is the normal case. A mirrored row is an invented menu item on
  a shell nothing asked to reach it from, and it looks grounded because its twin is.
- **Minting a mobile child under a web parent.** On `both`, `id` uniqueness and parent resolution
  are per `## Structure` section. A child whose parent lives in the other tree is an orphan.
- **Re-shaping an existing `## Structure` into the other platform's shell.** A project that adds a
  platform grows a second section; rewriting the first one is a regenerate under a friendlier name.
- **Re-reading `_bigin/system/project.md` here to check the platform.** Stage 1 read it once and
  told this stage. A second reader is the one that eventually disagrees.
- **Letting a pain point mint a nav entry on its own.** `PP-004` says finding yesterday's work is
  hard; it does not say a "Recent activity" screen exists. Ground 1b shapes placement, never
  existence — the entry needs a screen a UC actually asked for, or it is an Open Question.
- **Marking a pain point resolved from here.** The register is the requirement side's. A flow that
  fixes one says so in the UX spec; `/bigin-transform-signal` is what closes the row.
- **Looking for a design system to seed.** There is none. A run that reports `bootstrap` because
  `_design-system/` is missing has keyed its mode on a folder this plugin stopped producing, and
  every later stage inherits the wrong mode.

## Adopting an existing navigation map

**Trigger:** `04-UIUX/_design-system/navigation-map.md` exists and `{nav_map_file}`
(`04-UIUX/_ux/navigation-map.md`) does not. The map used to live inside a design-system folder this
pipeline no longer produces; the file itself is unchanged apart from where it sits and one column.

```text
old path present, new path absent   → MOVE it: 04-UIUX/_design-system/navigation-map.md
                                      → 04-UIUX/_ux/navigation-map.md
                                      Content moves verbatim. No row is re-derived, no id changes,
                                      no `Grounded by` is reconsidered.
                                      Then: drop the `Icon/token` column heading to `Icon` and clear
                                      any cell holding a `--token` name — a token id resolves to
                                      nothing in a vault with no design system, and a renderer given
                                      one picks its own icon anyway. An icon NAME ("inbox",
                                      "calendar") is content and stays.
                                      Append one ## Changelog line: moved from _design-system/,
                                      Icon/token → Icon (<YYYY-MM-DD>).
both paths present                  → the new one wins. Do NOT merge. Report the stale copy at the
                                      old path and leave it untouched — a human deletes it, because
                                      only they can tell which of two divergent trees is live.
neither present                     → not an adoption. It is a BOOTSTRAP (A1).
new path present, old absent        → already adopted. Skip entirely.
```

**Leave `04-UIUX/_design-system/` alone otherwise.** A vault that has `design-tokens.md` and
`components/` in it keeps them: they are a record of what earlier runs specced against, and a design
team may well want to read them before supplying a real system. Nothing in this pipeline reads them
any more, and nothing here deletes them. Report the folder as no-longer-read, once, and move on.
