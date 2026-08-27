# Stage 1 — Scope: find the use cases that have no current design

```text
runs: orchestrator, FIRST
in:   $ARGUMENTS (a slug, a UC-###, or nothing) + every feature hub
out:  the work-list: per feature, which UCs are NEW, which are CHANGED, which are CURRENT
    + the project's platform, read once here and passed to every later stage and worker
    + each feature's open pain-point COUNT (a count — the statements are Stage 2's input)
never: designing anything · reading a whole UC yet · touching a file · looking for a design system
```

Read `{design_conventions}` § Staleness and § Platform before this stage. They define the three-way
read below and the one project-wide fact this stage resolves for the whole run.

## Part 1 — Which features are candidates

```text
$ARGUMENTS is a slug        → that feature only
$ARGUMENTS is a UC-###      → that UC's primary_feature only
$ARGUMENTS is empty         → every file in {hub_dir}
```

Read only each hub's **frontmatter** here (`uc:`, `uiux:`) plus its `## Design Directives` row count.
Full UC bodies are Stage 3's job — a scan that reads every UC in full burns the run before a single
screen is written.

## Part 2 — The three-way read, per UC

```text
per candidate feature:
    ucs      = the hub's uc: list
    ux       = {ux_dir}/UX-### for this feature   (from the hub's uiux:, else Grep {ux_dir}
                                                   for feature: <slug>)
    absorbed = ux.absorbed:  or []  if no UX yet

    per uc in ucs:
        live = that UC file's frontmatter version        # read the frontmatter, not the hub table
        uc not in absorbed                → NEW
        uc in absorbed at an older version → CHANGED
        uc in absorbed at the same version → CURRENT
```

`CURRENT` is a result, not a silence. Report it (`<slug>: 3 UC current, nothing to redesign`) so a
human can tell "already designed" from "the run never got there".

## Part 3 — Four gates, in order, stopping at the first failure

Per UC marked `NEW` or `CHANGED`:

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

## Part 5 — Mode, and the platform

Two project-wide facts get settled here, once, before any feature is looked at.

```text
{nav_map_file} absent  → BOOTSTRAP   Stage 2 creates the navigation map
{nav_map_file} present → EXTEND      Stage 2 loads its tree and adds to it
```

Announce the mode in the report. On `BOOTSTRAP`, two or more features make a better first navigation
tree than one — but one is allowed; just say the shell will be thin.

**Mode is about navigation and nothing else.** There is no design system in this pipeline and no
token file to look for: colour, type, spacing, and components are supplied later by a design team or
bound at render time (`{design_conventions}` § Rendering is a separate step). A run that goes looking
for `_design-system/` is reading for a vault shape this plugin stopped producing.

Then read `platform:` from `_bigin/system/project.md`'s frontmatter — **once, here, for the whole
run** (`{design_conventions}` § Platform):

```text
platform: web | mobile | both   → that value, announced as STATED
key absent                      → web, the compatibility default. Announce it as DEFAULTED, never
                                  as a stated value (§ Adopting an existing project config below)
a value that is none of the three → treat as web, announce it as defaulted, and name the bad value
                                  in the report. Never guess which of the three a typo meant
```

`web` is the compatibility default on purpose: it is what every design run before this field existed
produced, so an unstamped project keeps designing exactly as it always did rather than silently
changing shape mid-engagement.

**Announce it alongside the mode, then pass it down.** Stages 2–6 and every worker this run
dispatches are *told* the platform in their instructions. No later stage and no worker re-reads the
project config to decide it — two workers inferring a platform differently produces one product with
two navigation shells, and neither of them looks wrong on its own.

Part 5 establishes the **project default** only. A per-feature override — a UC, a hub `## Design
Directives` row, or an active `DESIGN-PRINCIPLES` row that *explicitly states* a platform for that
feature — is resolved in Stage 3, per feature, against the UC bodies this stage deliberately does
not read (Part 1). This stage neither hunts for one nor pre-empts one, and a hub's directive row
**count** is not evidence of one.

## Part 5b — Note the pain points, do not read them yet

Per candidate feature, count the rows in its hub's `## Pain Points` section that are **not** resolved.
A count, on the work-list line — nothing more. The statements themselves are Stage 2's and Stage 3's
input (`{design_conventions}` § User flows and pain points), and reading them here costs the same
context the Part 1 rule exists to protect.

The count earns its place because it is what a human scans the work-list for: a feature carrying six
open pain points and one UC is a feature whose flows matter more than its screen count, and that is
visible here or nowhere.

## Part 6 — Print the work-list, then keep going

This stage is **headless, with no exception.** Print the work-list and continue — no confirmation, no
question, and **no halt at all**. There used to be one: a required design engine, checked here, that
stopped the whole run when it was absent. Rendering is now `/bigin-render-design`, a separate skill a
human invokes when they want a prototype, so the tool this stage does not use can no longer stop the
work this stage does. Nothing in this skill renders, so nothing in this skill needs a renderer.

```text
work-list:
  <slug>  UX-### (existing | new)  platform: web  pp: 3 open  — UC-003 NEW, UC-007 CHANGED (1.2 → 1.4), UC-009 CURRENT
  <slug>  design-only              platform: web  pp: 0 open  — 3 open directive(s)
  skipped <slug>/UC-###                                       — <gate that failed>
mode: bootstrap | extend (navigation map v<x>)
platform: web | mobile | both (stated | defaulted)
method: <wds | figma | <plugin> | built-in>          # the OPTIONAL method layer, never a renderer
flow review: <pfd | <critique skill> | skipped — not installed>
```

`platform:` sits on the announcement line **and** on every work-list line, and the repetition is the
point: at this stage every line carries the project default, so a Stage 3 per-feature override
prints in exactly this shape against exactly one slug. A human then sees *which* feature diverged
and why, instead of holding one global value in their head and diffing it against prose further down
the run.

## Failure modes

- **Trusting the hub's `## Use Cases` table for a version.** It is a snapshot. Read the UC file's own
  frontmatter, every time.
- **Treating a missing `absorbed:` as "current".** No `absorbed:` means nothing was ever designed —
  that is `NEW`, the loudest case in the list.
- **Designing a UC from the wrong feature.** Gate 3 exists because two features would otherwise both
  draw the same screens, and the second one to run would look like the design changed.
- **Skipping a `needs-clarification` UC.** Its flow is real; its gaps are questions. Design what is
  stated and ask about the rest.
- **Reading every UC in full at this stage.** Scope is a frontmatter question.
- **Inferring the platform from how a UC or a directive is worded.** "The courier scans the parcel"
  reads phone-shaped and states nothing; "at a desk" says where an actor is, not what is being
  built. The platform comes from the config, and only an *explicit* statement overrides it — later,
  in Stage 3, cited as that feature's ground. An inferred platform reaches the client as a decision
  somebody made.
- **Letting a worker re-derive the platform.** It is read once, here, and passed down. A worker that
  opens `_bigin/system/project.md` to check for itself is the second reader that eventually
  disagrees with the first, and the product gets two navigation shells.
- **Treating an absent `platform:` as a reason to ask.** This skill is headless and may be running
  unattended from `/bigin-ba`. Absent means `web`, announced as defaulted, and reported as something
  to stamp — the question belongs to `/bigin-upgrade-project`, where a human is present.
- **Announcing a defaulted platform as a stated one.** `web` because nobody said and `web` because
  the client said are the same design and completely different facts; collapsing them means nobody
  ever comes back to stamp the config.
- **Halting for anything.** A missing UC flow, an unclear directive, an ungrounded screen, an
  uninstalled design tool: every one of those is a skip, an Open Question, or somebody else's step.
  This skill has no halt, and re-introducing one turns an unattended pipeline into one that waits.
- **Checking for a render engine here.** It was a real precondition once, and removing it was the
  point of splitting rendering out: a stage that reads use cases and writes markdown was stopping
  because a prototype tool was not installed. `/bigin-render-design` checks its own engine, when a
  human asks it to render.
- **Naming a design tool, or pasting an install command, into this guide.** Every stage guide is
  engine-agnostic. The install commands live in `/bigin-render-design`'s own adapter, and a copy
  here is the copy that goes stale.
- **Checking for a design system or a token file.** There is none, by design: the visual system is
  the design team's or the render engine's (`{design_conventions}` § Rendering is a separate step).
  A run that keys its mode on `_design-system/` reads a vault shape this plugin no longer produces,
  reports `bootstrap` forever, and tells Stage 2 to seed something nothing will ever cite.
- **Reading the pain-point statements here.** Part 5b wants a count. The statements are what Stage 2
  shapes the flows against and Stage 3 grounds an emphasis with — pulling them into the orchestrator
  now spends the context the whole fan-out exists to protect, twice.

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
outside the design stage's write map (`{design_conventions}` § Write map: `{ux_dir}`,
`{nav_map_file}`, and named hub sections — nothing else). A design run that stamped the config
would be writing a project-wide decision nobody stated, from a run nobody was watching, into the one
file every other skill reads as settled fact. Defaulting is recoverable and says so in its own
report line; a stamp is not, and the next reader has no way to tell it from something the client
said.

**Idempotent.** A config that already carries `platform:` — at any of the three values — is skipped
entirely, in both branches. This section fires on an absent key only, never on a value it happens to
disagree with.
