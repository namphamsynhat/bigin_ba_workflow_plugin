# Stage 2 — The design system and navigation map: seed them first, extend after

```text
runs: orchestrator, TWICE — Part A before the screens, Part B after them
in:   {design_principles_file} · the existing {design_system_dir} · Stage 3's reported candidates
out:  a design system + navigation map the screens can cite by name, then slightly bigger ones
never: deleting a token or nav entry · renaming either · rewriting either file from scratch
```

Read `{design_conventions}` § The design system, § Token architecture, and § The navigation map
first.

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

{nav_map_file} present:
    read its ## Structure whole — the tree already exists, at whatever depth it has grown to;
    reuse a branch before starting a parallel one
    NEVER overwrite it. NEVER re-instantiate the template over it.
```

### A2. Fill `## Foundations` from what the client actually said

```text
read {design_principles_file}
take every row with Status: active
    → one Foundations line each: the principle, in the client's words, citing the row #
bootstrap  → all active rows seed the section
extend     → fold in only rows newer than {tokens_file}'s own `updated` date
```

This register is **read-only** for this stage. It holds client-stated preferences; a token this
stage invents is not a client preference and never gets written back there.

### A3. Make sure the Level-2 names the screens will need exist

```text
per Foundations line, ask: does a semantic token already express this?
    yes → nothing to do
    no  → add ONE Level-2 token with a plain name and a Level-1 value under it
```

Do not pre-build a full palette. A token nobody cites is noise, and Part B is where real usage adds
the rest.

### A4. Nothing to say, say nothing

A run whose Foundations and semantic tokens are already correct adds nothing here, bumps no version,
and writes no changelog line. That is the normal case in `extend` mode. Same for the nav map: loading
an existing `## Structure` is not itself a change — only Part B's new entries bump its version.

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

### B5. Close out the files

```text
bump {tokens_file} version
append a ## Changelog line: date · what was added · which features drove it
list new components in the tokens file's ## Components index

bump {nav_map_file} version — only if an entry was actually added
append its own ## Changelog line: date · entries added · which features drove them
```

### B6. What is never allowed here

```text
delete a token, component, or nav entry → forbidden (D1) — retire a nav entry instead (§ Removing
                                           an entry), never delete its row
rename a token, component, or nav entry → forbidden (D1)
change an existing token's VALUE        → allowed ONLY when a DESIGN-PRINCIPLES row says so;
                                          changelog it and name the row. Otherwise raise a question.
regenerate either file "to tidy it up"  → forbidden. Every screen already cites these names.
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
