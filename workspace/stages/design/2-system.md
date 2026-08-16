# Stage 2 — The design system: seed it first, extend it after

```text
runs: orchestrator, TWICE — Part A before the screens, Part B after them
in:   {design_principles_file} · the existing {design_system_dir} · Stage 3's reported candidates
out:  a design system the screens can cite by name, then a slightly bigger one
never: deleting a token · renaming a token · rewriting the file from scratch
```

Read `{design_conventions}` § The design system and § Token architecture first.

**Why twice.** Screens must cite tokens **by name** (D2), so the names have to exist before the
screens are written. But screens also discover new patterns. So: seed, design, then fold the new
patterns back in.

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
and writes no changelog line. That is the normal case in `extend` mode.

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

### B4. Close out the file

```text
bump {tokens_file} version
append a ## Changelog line: date · what was added · which features drove it
list new components in the tokens file's ## Components index
```

### B5. What is never allowed here

```text
delete a token or component            → forbidden (D1)
rename a token or component            → forbidden (D1)
change an existing token's VALUE       → allowed ONLY when a DESIGN-PRINCIPLES row says so;
                                         changelog it and name the row. Otherwise raise a question.
regenerate the file "to tidy it up"    → forbidden. Every screen already cites these names.
```

A token that looks wrong, duplicated, or unused becomes a line in `{tokens_file}`'s own
`## Open Questions` (owner: team) and a line in the run report. It is a **system** question, not a
feature one, so it does not go on a UX spec or a hub — and it never becomes a silent edit.

## Failure modes

- **Wiping and regenerating the design system.** Every screen already built against it breaks at
  once, and nothing in the vault records that it happened.
- **Renaming a token to a better name.** Same failure, quieter.
- **Adding a near-duplicate because dedup felt slow.** It cannot be removed later (D1), so the vault
  carries both forever.
- **Seeding a hundred tokens on bootstrap.** Tokens come from real screens; a speculative palette is
  a design nobody asked for.
- **Letting a subagent write the design system.** Two features run at once and both add `--color-warning`.
- **Bumping the version on a run that added nothing.** The changelog stops meaning anything.
