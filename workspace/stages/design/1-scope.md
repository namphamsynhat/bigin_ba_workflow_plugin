# Stage 1 — Scope: find the use cases that have no current design

```text
runs: orchestrator, FIRST
in:   $ARGUMENTS (a slug, a UC-###, or nothing) → `bigin design scope`
out:  the work-list: per feature, which UCs are NEW, which are CHANGED, which are CURRENT
    + the project's platform, read once here and passed to every later stage and worker
    + each feature's open pain-point COUNT (a count — the statements are Stage 2's input)
never: designing anything · reading a whole UC yet · touching a file · looking for a design system
```

Read `design-core.md` § Staleness and `design-platform.md` § Platform before this stage. They define the three-way
read below and the one project-wide fact this stage resolves for the whole run.

## Part 1 — Run the scan

```text
bigin run new --stage design                 once — the run id every later command takes
bigin design scope [<slug> | UC-###] --run <run>
```

One command, and the whole of Parts 2–5b below: it reads every candidate hub's `uc:` list, compares
each use case's **live frontmatter version** against the owning UX spec's `absorbed:`, applies the four
gates, counts each hub's open pain points and directives, and reads the platform and the mode. Print
what it prints and continue. **Do not re-do it by hand, and do not open a UC or a UX spec at this
stage** — the parts below say what its output *means*, so you can explain a line, not so you can
recompute it.

## Part 2 — The states it reports

```text
NEW       the use case is on no absorbed: list                       → design it
CHANGED   absorbed at an older version (1.2 → 1.4)                   → redesign its screens
CURRENT   absorbed at the live version                               → skip, and SAY SO
DRAFTED   NOT absorbed, but a ## 2 row of the spec already serves it → a run died between Stage 3
          and Stage 6. Its screens are on disk: resume at Stage 4, never dispatch its worker again
resume: review | done   (with --run) this run already wave-checked, or closed, that feature
```

`CURRENT` is a result, not a silence: a human has to be able to tell "already designed" from "the run
never got there". `ux.stale:` (`bigin cascade`) lists exactly the `CHANGED` ones — a cross-check.

## Part 3 — The four gates behind a `skipped` line

Applied by the scan, in order, stopping at the first failure:

| # | Gate | Fails when | Then |
|---|---|---|---|
| 1 | **has a flow** | `## 2 Main Success Scenario` has no step rows | skip this UC — there is nothing to design. Name it: `no main flow yet → /bigin-transform-signal` |
| 2 | **has a goal** | `title:` is empty, or `level: summary` | skip. A summary-level UC is a group of other UCs; design those instead |
| 3 | **is owned here** | this feature is not the UC's `primary_feature` | skip **in this feature** — it is designed in the owner's UX spec. Note the owner |
| 4 | **is not removed** | `status: removed` | skip silently |

A UC parked at `needs-clarification` **passes** every gate. Its open questions become known gaps in
the brief (Stage 3), not a reason to refuse to design. Say which ones in the report.

## Part 4 — Design-only features

A feature can have **no UC at all** and still be in scope:

```text
no UC  +  ≥1 hub ## Design Directives row with Status: open   → IN SCOPE (design-only)
no UC  +  no open directive                                    → OUT of scope, skip silently
```

A design-only feature gets a UX spec with a `## 1 Design Brief` and `## 3 Screen Specs` for whatever
the directives describe, an empty `absorbed:`, and no `## 4 Flows`. **Never mint a placeholder UC**
to give this stage something to key on.

## Part 5 — Mode, platform, pain points: what the last lines mean

```text
mode: bootstrap | extend      keyed on {nav_map_file} and nothing else. There is no design system in
                              this pipeline and no token file to look for
                              (`design-platform.md` § Rendering is a separate step).
platform: <v> (stated)        project.md says web | mobile | both
platform: web (defaulted)     the key is absent, or holds a bad value (named on the line). `web` is
                              what every run before the field existed produced. Announce it as
                              DEFAULTED, never as stated, and never ask — this skill is headless
pp: <N> open                  a COUNT per feature. The statements are Stage 2's and Stage 3's input
new UX ids needed: <N>        the argument for `bigin mint ux --count <N>` at Stage 3
```

The platform here is the **project default**. A per-feature override exists only where a hub
`## Design Directives` row or an active `DESIGN-PRINCIPLES` row *explicitly states* one; it is resolved
at Stage 3 from the worklist, and never inferred from how a step is worded. Every later stage and
every worker is *told* the platform — none re-reads the project config.

## Part 6 — Print the work-list, then keep going

**Headless, with no exception**: print the scan's output, add the method line, and continue. No
confirmation, no question, no halt — a missing flow, an unclear directive or an uninstalled design
tool is a skip, an Open Question, or somebody else's step. Nothing in this skill renders, so nothing
here checks for a renderer.

```text
<the output of `bigin design scope`, verbatim>
method: <wds | figma | <plugin> | built-in>          # the OPTIONAL method layer, never a renderer
```

## Failure modes

- **Recomputing the scan by reading hubs and UCs.** It costs the context the fan-out exists to
  protect, and a hand comparison is where a `CHANGED` gets read as `CURRENT`.
- **Dispatching a screens worker for a `DRAFTED` or `resume: review` feature.** Its screens exist; a
  second worker redesigns them and the first set's questions are orphaned.
- **Skipping a `needs-clarification` use case.** It passes every gate: its flow is real, its gaps are
  questions. Design what is stated and ask about the rest.
- **Inferring the platform from wording.** "The courier scans the parcel" reads phone-shaped and
  states nothing. Only an explicit statement overrides the config.
- **Announcing a defaulted platform as a stated one.** Same design, different fact — and nobody comes
  back to stamp the config.
- **Looking for a design system, a token file, or a render engine.** None is part of this run.

## Adopting an existing project config

**Trigger:** `_bigin/system/project.md` has no `platform:` key in its frontmatter — every project
initiated before the field existed. There is nothing to transform: the field is either **stated** by
a human or **defaulted** by a run, and which of the two is possible depends entirely on whether a
human is present.

**Run from `/bigin-upgrade-project`.** A human is there, so ask — once:

```text
AskUserQuestion, one question, three options:  "What is this project building?"
    web     a browser app                    (the default, and what this project has designed as)
    mobile  a phone app
    both    both, from one platform-blind requirement set
→ stamp `platform: <answer>` into the frontmatter, alongside `project_mode:`; refresh `updated:`
→ append one ## Changelog line, in that file's own shape:
      - `platform: <answer>` stamped — stated by the human (<YYYY-MM-DD>)
```

Nothing else in the config is touched, and no design work runs off the back of the answer — the next
`/bigin-generate-design` reads the stamped value at Part 5 like any other project.

**Hit mid-design-run.** `/bigin-generate-design` is headless and must never ask:

```text
→ default to web, and run the whole design stage at web
→ announce it as `platform: web (defaulted)`, never as a stated value
→ report that the config should be stamped, and name /bigin-upgrade-project as where that happens
→ write NOTHING to _bigin/system/project.md
```

**That last line is why this section has two branches at all.** `_bigin/system/project.md` is
outside the design stage's write map (`design-core.md` § Write map: `{ux_dir}`,
`{nav_map_file}`, and named hub sections — nothing else). A design run that stamped the config
would be writing a project-wide decision nobody stated, from a run nobody was watching, into the one
file every other skill reads as settled fact. Defaulting is recoverable and says so in its own
report line; a stamp is not, and the next reader has no way to tell it from something the client
said.

**Idempotent.** A config that already carries `platform:` — at any of the three values — is skipped
entirely, in both branches. This section fires on an absent key only, never on a value it happens to
disagree with.
