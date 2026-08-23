# Stage 2 — The design system and navigation map: seed them first, extend after

```text
runs: orchestrator, TWICE — Part A before the screens, Part B after them
in:   {design_principles_file} · the existing {design_system_dir} · Stage 3's reported candidates
      · the platform Stage 1 announced
out:  a design system + navigation map the screens can cite by name, then slightly bigger ones
never: deleting a token or nav entry · renaming either · rewriting either file from scratch
       · re-reading the project config to decide the platform
```

Read `{design_conventions}` § The design system, § Token architecture, § The navigation map, and
§ Platform first.

**The platform arrives as an instruction, not a lookup.** Stage 1 read `platform:` once and passed
it here; this stage never opens `_bigin/system/project.md` to check. It shapes two things below —
which Level-2 names have to exist (A3), and what shape the navigation map's `## Structure` takes
(A1, B4).

**Why twice.** Screens must cite tokens **by name** (D2), so the names have to exist before the
screens are written. But screens also discover new patterns — and new places a menu needs to reach.
So: seed, design, then fold the new patterns and new nav entries back in.

**Two artifacts, one rhythm.** `{nav_map_file}` lives inside `{design_system_dir}` and follows the
exact same bootstrap/extend, append-only shape as the token file — it is handled alongside it in
both parts below rather than as a separate pass.

---

## Part A — Seed (before Stage 3)

### A1. Bootstrap, or load

```text
{tokens_file} absent:
    create {design_system_dir}/
    instantiate {tokens_file} from {template_design_system}
    version 1.0

{tokens_file} present:
    read it whole (it is the shared contract)
    list every component file in {components_dir}
    NEVER overwrite it. NEVER re-instantiate the template over it.
```

Same for the nav map, same run:

```text
{nav_map_file} absent:
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
                                   not a nav decision (B4).
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
                                          default, the same way an unsuffixed prompt-block heading
                                          reads as web ({design_conventions} § The UX spec). Stamp
                                          this run's platform, then shape if the next line applies.
this run is `both`, the file holds one  → SHAPE it: suffix the existing heading `— Web`, append a
web ## Structure                          new, empty ## Structure — Mobile beside it, re-stamp
                                          platform: both
```

**Shaping adds; it never rebuilds.** No row moves, no `id` changes, no `Grounded by` is re-derived,
and nothing in the existing tree is reconsidered because a second shell now exists. Part B closes it
out (A4, B5). A populated `## Structure` is never re-shaped *into* the other platform's shell — a
project that gains a platform grows the second section (B6).

### A2. Fill `## Foundations` from what the client actually said

```text
read {design_principles_file}
take every row with Status: active
    → one Foundations line each: the principle, in the client's words, citing the row #
bootstrap  → all active rows seed the section
extend     → fold in only rows newer than {tokens_file}'s own `updated` date
```

This register is **read-only** for this stage. It holds client-stated preferences; a token this
stage invents is not a client preference and never gets written back there. Nor is a **platform
constraint** a Foundations line: a phone's touch-target minimum is not something a client said, it
is what the platform is — A3 seeds it as a token and it stops there.

### A3. Make sure the Level-2 names the screens will need exist

```text
per Foundations line, ask: does a semantic token already express this?
    yes → nothing to do
    no  → add ONE Level-2 token with a plain name and a Level-1 value under it
```

Do not pre-build a full palette. A token nobody cites is noise, and Part B is where real usage adds
the rest.

**On `mobile` and `both`, three more names have to exist** — what the platform itself constrains,
alongside A2's Foundations work:

```text
touch-target minimum   ONE Level-2 token for the smallest tappable size any control may be
mobile spacing scale   the steps a phone layout actually steps in
mobile type scale      the sizes a phone screen actually reads at
```

**These are platform constraints, not client preferences.** A thumb is the same size on every
client's phone, so the constraint arrives with the platform rather than from something somebody said.
That is why this stage may seed it with no citation, and exactly why it is **never a
`DESIGN-PRINCIPLES` row**: that register is client-stated only, and read-only here (A2). A client who
states a target size does get a row — raised by `/bigin-transform-signal`, from what they said, never
written from this stage.

The discipline does not loosen for them: still no speculative palette, still only the Level-2 names
the screens will actually need, still nothing written back to `{design_principles_file}`. On `both`,
they are seeded **alongside** the web names, never instead of them — one system carries both shells.

### A4. Nothing to say, say nothing

A run whose Foundations and semantic tokens are already correct adds nothing here, bumps no version,
and writes no changelog line. That is the normal case in `extend` mode. Same for the nav map: loading
an existing `## Structure` is not itself a change — only Part B's new entries bump its version.

The one exception is **shaping**: adding the second `## Structure` section a `both` project needs,
and suffixing the existing one (A1), changes the file even on a run that adds no rows. It gets a
version bump and a changelog line in Part B's close-out like anything else.

---

## Part B — Extend (after Stage 3 reports)

Stage 3's subagents **never write here** — they report candidates. This part applies them, one at a
time, in the orchestrator.

### B1. Dedup before adding — every single candidate

```text
per candidate token/component:
    does an existing one MEAN the same thing?         → reuse it. Tell Stage 4 the real name.
    does an existing one nearly fit, needing a variant? → add the VARIANT to the existing component
    genuinely new?                                     → add it
```

Two tokens meaning one thing is the failure this check exists for. `--color-danger` and
`--color-error` cannot both be right, and once both exist neither can be removed (D1).

### B2. Add a token

```text
Level 2 (semantic)  when it says what something MEANS      --color-action-primary
Level 3 (component) when it says where something is USED   --button-primary-bg
add the Level-1 raw value underneath if the value is new
```

Name it for its meaning, never its appearance. `--color-brand-blue` is wrong the day the brand turns
green; `--color-action-primary` never is.

### B3. Add a component

```text
appears on 2+ screens  → its own file, {components_dir}/<component>.md from {template_component}
appears on 1 screen    → leave it in that screen's spec. Promote it when a second screen wants it.
```

Second use is the trigger. Promoting on first use fills the system with things nobody shares.

### B4. Add a nav entry

```text
per reported nav candidate:
    does an existing entry already point at the same screen?  → nothing to add, tell Stage 4 the
                                                                  existing id
    is it a screen reached only through another screen?       → NOT an entry (§ Structure test in
                                                                  design-conventions.md § The
                                                                  navigation map) — decline it
    is it directly menu-reachable and genuinely new?           → mint its id and add ONE row
```

Minting the `id` — where it nests, not just whether it exists:

```text
reported parent already in ## Structure   → id = <parent id>.<new segment>
reported parent does NOT exist yet        → mint the parent container row FIRST (Points to: —),
                                             then the child under it — never skip straight to a
                                             child whose parent id nothing resolves to
no parent reported (a new top-level item) → id = <one segment>, no dot
```

A role split on the entry (who sees it) goes in that row's `Role(s)` cell, citing the `BR-###` or
the UC's actors — never invented to "look complete".

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
                                                          down? Report it, and tell Stage 4 this screen
                                                          has no menu entry yet.
the candidate nests under an existing tab               → not top-level; the cap does not apply. Mint
                                                          it under its parent as usual.
```

A phone tab bar physically stops being usable past five, so a sixth candidate means either two
features share a tab or one belongs a level down — and which of those is right is a human call,
never a silent sixth row. The cap is a platform constraint, not a style preference, and it does not
apply to a web sidebar, which nests as deep as the real IA does.

### B5. Close out the files

```text
bump {tokens_file} version
append a ## Changelog line: date · what was added · which features drove it
list new components in the tokens file's ## Components index

bump {nav_map_file} version — only if an entry was actually added, or the file was SHAPED (A1)
append its own ## Changelog line: date · entries added · which features drove them
                                  on `both`, name WHICH section each entry landed in — a line reading
                                  "added Reports" cannot be read back against two trees
                                  on a shaping run, say so: "## Structure suffixed — Web,
                                  ## Structure — Mobile added, no entries yet"
```

On `both`, close out **both** sections in the same pass, and let their row counts differ. A section
left empty because no screen this run needed a mobile menu entry is a real result — say it in the
report rather than filling it to match the other one.

### B6. What is never allowed here

```text
delete a token, component, or nav entry → forbidden (D1) — retire a nav entry instead (§ Removing
                                           an entry), never delete its row
rename a token, component, or nav entry → forbidden (D1)
change an existing token's VALUE        → allowed ONLY when a DESIGN-PRINCIPLES row says so;
                                          changelog it and name the row. Otherwise raise a question.
regenerate either file "to tidy it up"  → forbidden. Every screen already cites these names.
re-shape a populated ## Structure       → forbidden. A platform change GROWS the second section
                                          (A1); it never rewrites the first one's rows.
add a 6th tab to a phone shell          → forbidden. It is an Open Question, owner: team (B4).
```

A token or nav entry that looks wrong, duplicated, or unused becomes a line in that file's own
`## Open Questions` (owner: team) and a line in the run report. It is a **system** question, not a
feature one, so it does not go on a UX spec or a hub — and it never becomes a silent edit.

## Failure modes

- **Wiping and regenerating the design system or nav map.** Every screen already built against it
  breaks at once, and nothing in the vault records that it happened.
- **Renaming a token or nav entry to a better name.** Same failure, quieter.
- **Adding a near-duplicate because dedup felt slow.** It cannot be removed later (D1), so the vault
  carries both forever.
- **Seeding a hundred tokens, or a full menu tree, on bootstrap.** Both come from real screens; a
  speculative palette or IA is a design nobody asked for.
- **Giving a sub-screen its own nav entry.** It is reached through its parent; a second way in
  drifts from the real navigation the first time one path changes.
- **Minting a child id whose parent id resolves to nothing.** `settings.team.members` with no
  `settings.team` row is an orphan branch — check 9 in `5-close.md` exists to catch it.
- **Letting a subagent write the design system or nav map.** Two features run at once and both add
  `--color-warning`, or both add a "Reports" menu entry under different groups.
- **Bumping either version on a run that added nothing.** The changelog stops meaning anything.
- **Adding a sixth top-level entry to a mobile shell.** The cap is physical, not stylistic, and the
  sixth row can never be removed (D1) — so the tab bar is permanently unusable and the record says a
  design decided it. Two features sharing a tab, or one moving a level down, is a human call.
- **Mirroring an entry onto the other shell for symmetry.** On `both`, an entry the web sidebar
  carries and the phone app does not is the normal case. A mirrored row is an invented menu item on
  a shell nothing asked to reach it from, and it looks grounded because its twin is.
- **Minting a mobile child under a web parent.** On `both`, `id` uniqueness and parent resolution
  are per `## Structure` section. A child whose parent lives in the other tree is an orphan that
  check 9 in `5-close.md` will find, one run later.
- **Putting a `nav` region — or a sidebar row — on a mobile shell.** `header / content / tab-bar /
  sheet / fab` is the phone vocabulary; `header / nav / main / aside / footer` is the web one
  (`{design_conventions}` § Platform). The wrong vocabulary produces a prototype prompt that asks a
  tool to build a shell the platform does not have.
- **Re-shaping an existing `## Structure` into the other platform's shell.** A project that adds a
  platform grows a second section; rewriting the first one is a regenerate under a friendlier name,
  and every screen already citing those ids breaks at once.
- **Re-reading `_bigin/system/project.md` here to check the platform.** Stage 1 read it once and
  told this stage. A second reader is the one that eventually disagrees, and the vault ends up with
  a token scale for one shell and a nav tree for the other.
- **Writing a touch-target minimum into `{design_principles_file}`.** It is a platform constraint,
  not a client-stated preference. Once it is a row there it reads, forever, as something the client
  asked for — and that register is read-only from this stage regardless.
- **Skipping the mobile scales because the palette rule says "seed nothing speculative".** A touch
  target and a phone type scale are not speculation; every mobile screen this run designs cites
  them, and a screen citing a name that does not exist breaks D2.
