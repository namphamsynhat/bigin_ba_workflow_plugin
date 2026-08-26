---
name: bigin-render-design
description: This skill should be used when the user asks to "render the design", "render the prototype", "build the prototype", "make me a clickable prototype", "run open design", "render this with open design", "send these features to open design", "turn the UX specs into screens I can show the client", "prototype UX-###", "assemble the prototype", "wire the screens into one prototype", "which design system should the prototype use", or names features to render against a finished UX spec. Renders already-written UX specs into prototype screens on Open Design — one `start_run` per feature into one shared Open Design project, monitored by one subagent per feature, then a final assembly run that wires every screen into one interactive prototype from the canonical navigation map — and copies every artifact back into the vault. Never re-designs, never writes a requirement, and records only pointers to what it produced.
argument-hint: "[feature slug | UX-###, one or more] [--design-system <id>] [--project <name|id>]"
disable-model-invocation: true
---

# Bigin Render Design

The **render** step, split out of `/bigin-generate-design` on purpose. It takes UX specs that already
exist and turns them into something a client can click through:

```text
in    UX-### <Feature>.md    the screens, states, real copy, flows, the ## 4 Coverage table — one
                             spec per feature, one or many features per run
    + UC / BR / ENTITIES.md  DATA ONLY: field lists, types, enums, predicates, state keys, volumes
    + _design-system/        token VALUES, components, and the canonical navigation ## Structure
    + Open Design            ONE project, ONE design system, ONE model — all chosen before any run

out   {od_project}           N feature runs + 1 assembly run, all in the same Open Design project
    + {prototype_dir}/       every artifact COPIED BACK into the vault, so the output outlives the
                             Open Design install that made it
    + ## 8 Rendered Artifacts  one appended row per participating spec: date, project, screens, path,
                               and the UX-###@version it rendered AGAINST
    + rendered: true           in each participating spec's frontmatter
```

**It designs nothing.** Every screen, state, field, and **label** it renders was decided by
`/bigin-generate-design` and verified by that skill's Stage 4. Open Design's own agent writes the
HTML — this skill's job is to hand that agent a prompt complete enough that it has nothing left to
invent, then to check that it invented nothing anyway.

**The one thing a render does author is the sample dataset** — the record *values* filling a table or
a form, generated from the extracted field types, formats, and enums. That is not a design decision
and it is not copy: every *label* is the spec's, and the values exist because a table of ten thousand
real-looking rows is what makes the screen reviewable at all. A dataset that invents a **field**, a
**status**, or a **capability** has crossed back into designing.

## The shape of a run

One Open Design project. One design system bound to it. One model. N features fanned out as N
`start_run` calls, then one assembly run over what they produced.

```text
                    ┌─────────────────────────────────────────────┐
                    │  Open Design project (shared workspace)      │
                    │  design system bound ONCE, at Step 0         │
                    └─────────────────────────────────────────────┘
                                       │
     ┌─────────────────────┬───────────┴───────────┬─────────────────────┐
     │                     │                       │                     │
 start_run             start_run               start_run             start_run
 UX-001 Auth           UX-002 Billing          UX-003 Orders          …
 (UX + UC + BR         (…)                     (…)
  + Entities + PP)
     │                     │                       │                     │
 screens/                screens/                screens/
 ux-001-auth.html        ux-002-billing.html     ux-003-orders.html
     │                     │                       │                     │
     └─────────────────────┴───────────┬───────────┴─────────────────────┘
                                       │  every feature run terminal & verified
                    ┌──────────────────▼──────────────────┐
                    │  start_run — ASSEMBLY               │
                    │  navigation-map.md ## Structure     │
                    │  + every screen file above          │
                    └──────────────────┬──────────────────┘
                                       │
                              index.html — one interactive prototype
                                       │
                    ┌──────────────────▼──────────────────┐
                    │  copy back → {prototype_dir}/       │
                    └─────────────────────────────────────┘
```

**Why one project and not one per feature.** The design system, the token values, and the navigation
shell are vault-wide facts. Rendering each feature into its own Open Design project gives every
feature its own copy of them, and the assembly step then has to reconcile N shells that were never
meant to differ. One project means the assembler reads files that already agree.

**Why one subagent per feature and not one for all of them.** A run takes 5–30 minutes and the
monitor has to stay awake across every poll of it. One monitor holding N runs serialises what should
be concurrent and drops the tail when its context fills; one monitor per feature is the unit that
matches the unit of work.

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{design_conventions}` | `_bigin/conventions/design-conventions.md` | the design rulebook — § Rendering is a separate step, § Write map, § Grounding, § Platform |
| `{ux_dir}` | `04-UIUX/` | **the input**, one `UX-<NNN> <Feature>.md` per feature. Its `## 8` + `rendered:` are the only spec fields this skill writes |
| `{prototype_dir}` | `04-UIUX/_prototypes/` | **the output**, one folder per render: `{prototype_dir}/<YYYY-MM-DD>-<slug-or-multi>/`. Created by this skill and by nothing else |
| `{design_system_dir}` | `04-UIUX/_design-system/` | **read-only here** |
| `{tokens_file}` | `04-UIUX/_design-system/design-tokens.md` | token names AND values — **read-only** |
| `{components_dir}` | `04-UIUX/_design-system/components/` | **read-only** |
| `{nav_map_file}` | `04-UIUX/_design-system/navigation-map.md` | **the single source of truth for navigation**, and the assembly run's brief — read-only |
| `{design_principles_file}` | `01-Requirements/DESIGN-PRINCIPLES.md` | **read-only** — client-stated preferences, and they outrank any engine's taste and any design system's defaults |
| `{pain_points_file}` | `01-Requirements/PAIN-POINTS.md` | **read-only** — which states are worth rendering properly |
| `{hub_dir}` | `01-Requirements/_features/` | read `<slug>.md`'s `uiux:` to find a slug's spec. **Not written** — a render changes no requirement bookkeeping |
| `{entities_file}` | `01-Requirements/ENTITIES.md` | **read-only.** The entity register — field lists, types, enum values, cardinalities |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | **read-only, for DATA ONLY** — predicates, field types, state keys, real volume numbers, filtered by the spec's own screen inventory. **Never written** |
| `{project_file}` | `_bigin/system/project.md` | `platform:`, and the render settings this skill persists (§ Step 0) |

Missing `_bigin/conventions/` → stop and say `/bigin-new-project` must run first. Then
`_bigin/conventions/conventions.md` § Workspace version check, as every skill does: behind → warn and
recommend `/bigin-upgrade-project`; ahead → stop.

## Write map — narrower than any other skill in this plugin

```text
WRITE   {prototype_dir}/<run>/               the copied-back artifacts. THE ONLY new files a render
                                             creates in the vault
        the spec's ## 8 Rendered Artifacts   ONE APPENDED ROW per participating spec per render.
                                             Never edits a prior row — the history is what makes a
                                             stale render visible
        the spec's rendered:                 false → true
        the spec's ## Changelog              one line
        {project_file} render settings       the resolved Open Design project + design system +
                                             agent/model, so the next run does not re-ask (§ Step 0)

NEVER   ## 1-## 7 of the spec        the design. Not a screen, not a state, not a word of copy
        the prompt blocks            the record of what was specified, not of what a render made of it
        {design_system_dir}          a token an engine wanted is a /bigin-generate-design question
        anything in 01-Requirements/ including the hub. A render is not a requirement event
        the spec's status:           human-only, and a render is not a review (D5)
        the spec's absorbed:         staleness is about UCs and screens, not about renders
```

A token or component Open Design wants and cannot find is **not** something to add here. It is a gap
in the spec, and the spec is `/bigin-generate-design`'s: report it and stop rendering that screen.

## Execution order

```text
0  precondition   Open Design reachable? project? design system? model?      (§ Step 0)  ← the only
                  ↳ any of these unresolved  → ASK. Nothing runs on a guess     interactive step
1  scope          which features, which specs, which screens                 (§ Step 1)
2  prompt         one self-contained prompt per feature                      (§ Step 2)
3  fan out        one start_run + one monitoring subagent per feature        (§ Step 3)
4  assemble       one start_run over navigation-map.md + every screen        (§ Step 4)
5  copy back      artifacts → {prototype_dir}, then record                   (§ Step 5)
```

Steps 3 and 4 are a **barrier**, not a pipeline: the assembly run cannot start until every feature run
is terminal and verified, because it wires together files that must all exist. Step 3's own N runs are
concurrent.

---

## Step 0 — The precondition, and the four things it resolves

Nothing is rendered until all four are settled. Each one that cannot be resolved from the vault or the
engine is a **question to the human**, never a default picked quietly.

### 0.1 Is Open Design connected and working?

Read `references/open-design-adapter.md` § Probe. In short: an MCP server row matching `open-design`
(case-insensitive **substring** — never an exact name) in `claude mcp list`, state `✔ Connected`, and
its tools callable. The tool prefix that server exposes is what every later step calls; resolve it once
here and use it throughout.

```text
connected      → continue
row present, not connected, or tools erroring
               → RETRY per the adapter's retry ladder. Still failing → § The manual fallback
row absent     → HALT with the install command. § The manual fallback still applies
```

**Never `sudo`, never a package manager, never auto-install.** Open Design is a desktop app that
installs software on the machine; report the command and stop (`/bigin-new-project` § 7.3 draws the
same line).

### 0.2 Which Open Design project?

```text
{project_file} carries a resolved od_project        → confirm it still exists (get_project). Reuse it
the human named one (--project)                     → resolve_project / get_project it
neither                                             → ASK, offering exactly three options:
                                                        · an existing project from list_projects
                                                        · a NEW project for this vault
                                                        · the currently-active project
                                                          (get_active_context), if there is one
```

The question is **"share an existing Open Design project, or create a new one for this vault?"** — the
user's own words for it. A shared project means these screens land beside whatever else lives there and
inherit its bound design system; a new one means a clean workspace this vault owns. Both are legitimate
and the choice is not the skill's.

Creating one: `create_project{name, designSystem}` — the design system is bound **here, at creation**,
which is why 0.3 is answered before this call is made.

### 0.3 Which design system?

**This is the question the run is most likely to get wrong silently**, so it is asked explicitly.

```text
{project_file} carries a resolved od_design_system     → reuse, and say which one in the report
the human named one (--design-system)                  → verify it EXISTS before using it
the target project already has one bound (get_project) → offer it as the default, still confirmed
NONE of the above                                      → ASK, and list what is actually available
```

**List, never guess.** Open Design exposes design systems as MCP **resources**, not tools — enumerate
`resources/list` and take every `od://design-systems/<id>/DESIGN.md` entry. That listing plus the
vault's own `{tokens_file}` is the complete menu. Put both kinds in front of the human:

```text
the vault's own tokens ({tokens_file})   the client's actual brand, from /bigin-generate-design
<id> — <title>                            an Open Design catalog system
…                                         (every entry resources/list returned)
```

```text
named design system found in either place  → bind it and render
named design system in NEITHER             → HALT. Render nothing, write no ## 8 row on ANY spec,
                                               touch no spec, create no project
```

**Never guess an id into existence.** A design system id that does not resolve fails as a 404 at
`create_project`, which is the good case; the bad case is an id that happens to match something else
and renders the client's product in a stranger's brand.

**`{design_principles_file}` outranks whichever system is chosen.** An active DESIGN-PRINCIPLES row and
a catalog system's default disagree → the row wins, and Step 2 states it in the prompt as a hard
override. That is ground 3, and it is why a shipped design system is never a substitute for the
vault's tokens.

### 0.4 Which model?

**Use a model Open Design actually offers.** Call `list_agents` — it returns each installed agent CLI's
`id`, `name`, `version`, and sample models with a `modelsCount` total. Pass the chosen pair as
`start_run{agent, model}`.

```text
{project_file} carries od_agent + od_model    → confirm still present in list_agents. Reuse
exactly one agent installed, one obvious model → use it, and name it in the report
several, or an ambiguous choice                → ASK, listing what list_agents returned
list_agents returns nothing usable             → omit agent and model entirely; Open Design falls back
                                                 to its own configured runtime, which is correct
```

**Never hardcode a model id in this skill or in either agent.** The model catalog is Open Design's,
it changes under us, and a stale id fails a run 20 minutes in. `list_agents` is the only authority.

### 0.5 Persist what was resolved

Write the four resolved values into `{project_file}` so the next render does not re-ask:

```yaml
od_project:        <project id>
od_design_system:  <design system id, or "vault-tokens">
od_agent:          <agent id, or empty for Open Design's default>
od_model:          <model id, or empty>
```

A later run still **confirms** each one is still valid — a persisted project that was deleted, or a
model that left the catalog, is a stale setting, not a licence to skip the check.

---

## Step 1 — Scope: which features, and which specs

**Never "render everything".** A render is a deliberate act naming its targets, exactly as before. One
feature is the normal case; several is legitimate when the human names them.

```text
the human named slugs or UX-### ids     → those, and only those
the human named nothing                 → LIST the specs that exist with their rendered: state and
                                          ## 8 history, and ASK which. Do not pick
```

Per named target, resolve the spec: a slug → `{hub_dir}/<slug>.md`'s `uiux:` → the `UX-###` file. A
`UX-###` id → the file directly.

**A spec that halts this step:**

```text
status: needs-clarification    → its ## 6 Open Questions are unanswered. Rendering an unresolved
                                 screen produces something a client reacts to that nobody decided.
                                 HALT for that spec, name the questions, continue with the others
absorbed: behind its UCs       → the spec is stale. WARN, name the drift, and let the human choose:
                                 render the stale spec anyway, or run /bigin-generate-design first
no ## 2 Screen Inventory rows  → nothing to render. Report and skip
```

Resolve `platform:` once, from each spec's own frontmatter (absent → `web`). It decides the regions
vocabulary and the shell, and Step 2 states it explicitly in every prompt.

**Count the work and say it out loud before spending it.** N features × 5–30 minutes each, run
concurrently, plus one assembly run. Report the count and the expected wall-clock before Step 3
starts — a human who did not expect an hour should get the chance to cut the list.

---

## Step 2 — Build one self-contained prompt per feature

Read `references/prompt-contract.md` in full. It defines exactly what a feature prompt contains, in
what order, and what may never appear in one.

The prompt is assembled from **five sources**, and the combination is the whole point: Open Design's
agent never sees the vault, so anything left out is something it will invent.

```text
UX-### spec        ## 1 Design Brief · ## 2 Screen Inventory · ## 3 Screen Specs (regions, elements,
                   copy, tokens, States, Interactions) · ## 4 Flows          THE DESIGN. Verbatim
UC / BR            the steps each screen serves, the validation predicates, the error states, the
                   state keys                                                DATA AND LOGIC ONLY
ENTITIES.md /      field lists, types, formats, enum vocabularies, cardinalities, real volume
_entities/         numbers                                                   DATA ONLY
{tokens_file}      every token the screens use, by NAME **and VALUE**        the design system
+ {nav_map_file}   this platform's ## Structure — the shell, verbatim
+ {components_dir}
PAIN-POINTS.md +   which states are worth rendering properly, and the client-stated preferences that
DESIGN-PRINCIPLES  outrank the design system                                 ground 3
```

**Every vault id is expanded into words before it enters the prompt.** `UC-012 S4` becomes "the step
where the reviewer approves the request". The prompt is self-contained (D6) and the run happens in a
process that has never seen this vault.

**The single exception, and it is deliberate: the traceability attributes.** Each screen root and each
grounded element carries its ids in `data-*` attributes — `data-ux`, `data-uc`, `data-br`, `data-en`,
`data-screen`, `data-state`. The prompt instructs Open Design to emit them and tells it plainly that
those ids must appear **nowhere else**: not in a text node, not in an `aria-label`, `title`, `alt`,
`placeholder`, `value`, an `<option>` body, or a CSS `content:`. That split — machine-readable
provenance, human-invisible — is what Step 3 verifies.

**The fidelity bar goes in the prompt.** `references/enterprise-fidelity.md` § The bar is ten items the
render has to clear; state them, because an agent told only *what* to build and never *how well* builds
a wireframe with colour.

**Output path is dictated, not left to the agent**: `screens/<ux-id-lowercased>-<slug>.html`, one file
per feature, so Step 4 knows what to wire together without discovering it.

---

## Step 3 — Fan out: one `start_run` per feature, one monitor each

**Dispatch one `render-screen-worker` per feature, concurrently.** One subagent monitors exactly one
feature — that is the unit, and it never takes two.

Each worker owns the whole lifecycle of its feature:

```text
1  start_run{project, prompt, agent, model, requestId}    → runId, immediately
2  poll get_run(runId) every 30-60s until terminal        → queued | running | succeeded | failed
                                                              | canceled
3  on succeeded: list_files(since) + get_artifact         → read back what it produced
4  verify the traceability contract, both halves          → scripts/check-traceability.sh
5  verify against the spec: every ## 2 screen present, every ## 3 State reachable, no invented
   screen, no invented field, no invented capability
6  report: runId, artifact paths, screen count, findings
```

**Open Design runs take 5–30 minutes. `status: running` with unchanged file mtimes is the inner agent
thinking, not a hang.** Never cancel out of impatience, and never substitute a hand-written file for a
run that felt slow — that throws away the entire reason this skill goes through Open Design at all.
The adapter reference states the poll cadence and the retry ladder; the worker follows it exactly.

**`requestId` is generated once per feature, before the first `start_run`, and reused verbatim on any
retry.** A retry with the same id resumes the same logical run; a retry with a *different* id starts a
second one and you pay for the same feature twice. A different payload under the same id is rejected —
which is the safety property that makes the retry safe.

### The traceability check — both halves

The user-visible half and the machine-readable half fail in opposite directions, so both are checked:

```text
NEGATIVE   no /(UC|BR|EN|UX)-\d/ in any VISIBLE position          scripts/check-traceability.sh
           text nodes, aria-label, title, alt, placeholder,       exit 1 = leak
           value, <option> bodies, CSS content:
POSITIVE   every screen root carries data-ux + data-screen;       same script, --require
           every state-bearing node carries data-state            exit 1 = missing provenance
```

A **leak** is sanitized in place by the worker — move the id into the right `data-*` and leave the
human-readable words unchanged. If removing the id empties the copy, that is a missing-copy finding, not
a sanitize: send the screen back. **Missing provenance** is never sanitized by hand — it is a re-run
finding, because an id the worker invents is an id nobody grounded.

### The repair loop, and when it stops

```text
finding → re-run start_run for that feature with the finding stated as a correction, same project
       → at most TWO repair rounds
after two → STOP for that feature. Report what is still wrong, keep the artifacts, do NOT block the
            other features, and do NOT block the assembly step on it
```

Past two rounds the render converges on something that satisfies the check and nobody else, and the
real problem — a spec hole or an engine limitation — never reaches a human.

### When a feature run fails terminally

Report it, keep going. One failed feature does not cancel the others, and the assembly step runs over
whatever succeeded — an assembled prototype missing one feature is worth more than nothing, provided
the report says plainly which feature is missing and why.

---

## Step 4 — Assemble: one run over the navigation map

**A barrier.** Every feature run is terminal before this starts.

**Dispatch one `render-prototype-assembler`.** Its brief is one `start_run` in the same project, whose
prompt is built from:

```text
{nav_map_file} ## Structure    the shell and the route tree, VERBATIM. This is the single source of
                               truth for navigation and the assembler resolves nothing itself
every screens/*.html           what the feature runs produced, by path
{tokens_file}                  the same token values every feature run used
the entry-actor set            when the participating specs' ## 1 Actor & Scope tables name more than
                               one actor, an entry stage that lets a reviewer switch between them —
                               ONLY the actors and handoffs a spec's own ## 1 or ## 4 Flows names
```

Output: **one `index.html`** — client-side routing, embedded state, CSS from the token values, no
server and no external stylesheet or script. It runs from a file, which is what makes it something a
person can be handed.

Then the assembler **verifies the prototype actually works**:

```text
every nav entry in ## Structure resolves to a real screen          no dead entry
every Interactions "Goes to" target resolves inside the runtime    no dead control
every route reachable from the entry stage                         no orphan screen
no route that reaches a spec nobody named for this build            no invented reach
the shell is identical on every screen and matches ## Structure     one product, not N
the traceability contract holds on index.html too                   same script, same both halves
every ## 4 Coverage "out of scope" row is still absent              nothing crept in
```

A nav entry pointing at a feature that was **not** in this run's scope is not a broken link — it is an
entry the assembled build should render as visibly unavailable rather than as a dead click. Say which
ones in the report.

Same two-round repair ceiling as Step 3.

---

## Step 5 — Copy back, record, report

**The copy-back is not optional bookkeeping — it is the point.** Open Design's project is the engine's
storage, and an engine is an external dependency that can change, break, or be uninstalled. The vault
is what has to still have the prototype next year.

```text
{prototype_dir}/<YYYY-MM-DD>-<slug|multi>/
├── index.html                    the assembled prototype
├── screens/
│   ├── ux-001-auth.html
│   ├── ux-002-billing.html
│   └── …
├── assets/                       whatever the runs referenced (get_artifact pulls these with the
│                                 entry — prefer ONE get_artifact over N get_file calls)
└── RENDER.md                     the manifest: date · Open Design project id · design system ·
                                  agent/model · one row per feature (UX-###@version, runId, screens,
                                  findings) · the assembly runId · every unresolved finding
```

`RENDER.md` is what makes a copied-back folder self-describing. A folder of HTML with no record of
which spec version, which design system, or which model produced it is an artifact nobody can trust
six weeks later.

**Then, per participating spec** — and only per spec that actually rendered:

```text
## 8 Rendered Artifacts    ONE APPENDED ROW. Columns are fixed:
                           | Rendered | Engine | Platform | Screens | Artifacts at | Against |
                           Engine cell:  open-design (<design system id>)
                           Artifacts at: {prototype_dir}/<run>/ + the Open Design project id
                           Against:      UX-<NNN>@<its own version>
rendered: false → true
## Changelog               one line
```

**An assembled build spanning several specs writes the same row to every participating spec** — same
date, same path, same project, each spec's own `Against` version. A spec's history has to show it
shipped as part of this build, not that it rendered alone.

### The report

```text
Open Design   project <name> (<id>) · design system <id> · <agent>/<model>
Rendered      <N> features, <M> screens, in <duration>
              UX-001 Auth      ✔ 4 screens   run <id>
              UX-002 Billing   ✔ 6 screens   run <id>
              UX-003 Orders    ✘ failed      run <id> — <why>
Prototype     {prototype_dir}/<run>/index.html   · preview <previewUrl>
Findings      <every unresolved finding, or "none">
Recorded      ## 8 row + rendered: true on UX-001, UX-002
next:         open index.html · re-run a failed feature · /bigin-generate-design for a spec gap
```

**Report what actually happened.** A feature that failed, a check that was skipped, a repair round that
did not converge — all of it goes in the report, plainly. A render that reports success while a screen
is missing is worse than one that reports the failure, because the missing screen is discovered in
front of the client.

---

## The manual fallback — when the automation cannot run

Open Design unreachable after the retry ladder, or a `start_run` that will not start, does **not** end
the run empty-handed. The prompts from Step 2 already exist and they are self-contained by
construction.

```text
1  write every built prompt to {prototype_dir}/<YYYY-MM-DD>-<slug|multi>/_prompts/
       ux-001-auth.prompt.md · ux-002-billing.prompt.md · … · assembly.prompt.md
2  tell the human EXACTLY where to paste each one:
       Open Design app → the project (<name>, or create it) → bind design system <id>
       → paste one feature prompt per run, one run at a time
       → then paste assembly.prompt.md as the last run
3  write NO ## 8 row and set NO rendered: flag. Nothing rendered
4  say plainly that the automation failed, what failed, and that the prompts are the deliverable
```

The spec's own `## Prototype Prompt` blocks are the other fallback and they need no tool at all — name
them too. A missing engine has never been allowed to cost this pipeline its output, and it does not
start here.

---

## Failure modes

- **Picking a design system without asking.** The single most damaging silent failure in this skill:
  the client's brand is replaced by a stranger's and the prototype still looks finished. Step 0.3 asks,
  every time it is not already resolved.
- **Guessing a design system or model id.** A guessed id that 404s is fine. A guessed id that *resolves
  to something else* is the failure. `resources/list` and `list_agents` are the only authorities.
- **Cancelling a slow run.** `running` with unchanged mtimes is the inner agent thinking. Open Design's
  own guidance is 5–30 minutes; cancelling and hand-writing the file discards exactly what the run was
  for.
- **Retrying with a fresh `requestId`.** Starts a second run for the same feature. The id is generated
  once per feature and reused verbatim.
- **Rendering one feature per Open Design project.** N copies of a vault-wide design system, and an
  assembly step reconciling shells that should never have differed.
- **Starting assembly before every feature run is terminal.** The assembler wires files that do not
  exist yet and produces a prototype with dead routes it will report as passing.
- **Sanitizing missing provenance.** A leak is sanitized; a *missing* `data-ux` is re-run. Adding the
  attribute by hand invents a ground nobody established.
- **Skipping the copy-back.** The whole render then lives inside an engine install. Step 5 is not
  bookkeeping.
- **Reporting the assembly as working without walking the route checks.** It reads exactly like a real
  pass, which is why the checklist is enumerated rather than summarised.
- **A third repair round.** Two rounds exhaust what automation can fix; past that the real problem is a
  spec hole or an engine limitation and it needs a human.
- **Writing a `## 8` row for a feature that failed.** The row is a claim that something is there to
  look at.

## Model

Session default, for the orchestrator and for both agents (`model: inherit`). Mapping a spec onto a
prompt complete enough that nothing is left to invent, and judging whether what came back is a finished
product, are both judgment work — the same reason `/bigin-generate-design`'s workers do not run on
`haiku`. The traceability scan is mechanical and is a script; everything the agents themselves do is
not.

**This is separate from `od_model`**, which is the model *Open Design* runs its own agent on (§ Step
0.4). That one is resolved from `list_agents` and never hardcoded.

## Additional resources

### Reference files

- **`references/open-design-adapter.md`** — the engine contract, and the only place an Open Design tool
  has a name: the probe and how to resolve the MCP tool prefix by substring, the full tool surface
  (`list_projects` · `create_project` · `resolve_project` · `get_project` · `list_agents` ·
  `start_run` · `get_run` · `cancel_run` · `list_files` · `get_file` · `get_artifact`), design systems
  as *resources* rather than tools, the `requestId` idempotency contract, the poll cadence, the retry
  ladder, the copy-back procedure, and every "never let it" the engine invites. Read at Step 0 by the
  orchestrator and in full by both agents.
- **`references/prompt-contract.md`** — what a feature prompt and the assembly prompt contain, in
  order, and what may never appear in one: the five sources and their precedence, id expansion, the
  `data-*` traceability vocabulary with every position an id may not appear in, the dictated output
  paths, and the worked skeleton of both prompt kinds. Read at Step 2 and by both agents.
- **`references/enterprise-fidelity.md`** — the bar: ten items covering token-only styling, computed
  WCAG AA contrast, enterprise density, the always-present shell, realistic data at real scale,
  reachable states, production chrome, typography discipline, restraint, and cross-screen consistency —
  plus § The tells and § What this file may never be used to justify. Quoted into every prompt and
  used as the verification checklist.

### Scripts

- **`scripts/check-traceability.sh <path>… [--require]`** — the traceability contract's deterministic
  gate, both halves. Without `--require`: scans for `/(UC|BR|EN|UX)-\d/` in every visible position
  (text nodes, `aria-label`, `title`, `alt`, `placeholder`, `value`, `<option>` bodies, CSS
  `content:`), ignoring `data-*` where those ids belong. With `--require`: also fails when a screen
  root carries no `data-ux`/`data-screen`. Exits `0` clean, `1` with each finding as
  `file:line | kind | position | id | context`, `2` if it could not run.
- **`scripts/check-contrast.py`** — WCAG 2.1 ratios, computed. `<fg> <bg> …` for pairs,
  `--tokens <design-tokens.md>` to sweep every colour token against every surface token, or
  `--pairs <file>` for `name fg bg [large|ui]` lines. Exits non-zero on a failure. Contrast is a
  formula; a model asked to judge it by eye is wrong on exactly the muted-on-subtle pairings a dense
  enterprise screen is full of.

### Agents

- **`agents/render-screen-worker.md`** — Step 3. One per feature, never two. Owns one `start_run`, its
  poll loop, its read-back, its two checks, and at most two repair rounds.
- **`agents/render-prototype-assembler.md`** — Step 4. One per run, after the barrier. Owns the
  assembly `start_run` and the interactive verification of what it produced.
