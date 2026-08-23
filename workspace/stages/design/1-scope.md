# Stage 1 — Scope: find the use cases that have no current design

```text
runs: orchestrator, FIRST
in:   $ARGUMENTS (a slug, a UC-###, or nothing) + every feature hub
out:  the work-list: per feature, which UCs are NEW, which are CHANGED, which are CURRENT
    + the project's platform, read once here and passed to every later stage and worker
never: designing anything · reading a whole UC yet · touching a file
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
{tokens_file} absent  → BOOTSTRAP   Stage 2 creates the design system
{tokens_file} present → EXTEND      Stage 2 loads it and adds to it
```

Announce the mode in the report. On `BOOTSTRAP`, two or more features make a better first design
system than one — but one is allowed; just say the system will be thin.

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

**Announce it alongside the mode, then pass it down.** Stages 2–5 and every worker this run
dispatches are *told* the platform in their instructions. No later stage and no worker re-reads the
project config to decide it — two workers inferring a platform differently produces one product with
two navigation shells, and neither of them looks wrong on its own.

Part 5 establishes the **project default** only. A per-feature override — a UC, a hub `## Design
Directives` row, or an active `DESIGN-PRINCIPLES` row that *explicitly states* a platform for that
feature — is resolved in Stage 3, per feature, against the UC bodies this stage deliberately does
not read (Part 1). This stage neither hunts for one nor pre-empts one, and a hub's directive row
**count** is not evidence of one.

## Part 5b — The engine precondition

The platform decided in Part 5 names a **required design engine**. Resolve it and check it here,
before the work-list:

```text
read the skill's references/design-engines.md § Engine per platform
    → which engine(s) this platform requires, each one's install-check probe, each one's command

the platform's engine present  → continue. Report it: `engine: <name> ✔`
the platform's engine ABSENT   → HALT. Report that file's install command VERBATIM, design nothing,
                                 print no work-list, stamp nothing
.claude/bigin-ba-workflow-plugin.local.md carries `design_engine_required: false`
                               → continue, reporting the engine as
                                 `skipped — waived in project settings`
```

**Never name an engine, and never reproduce an install command, in this guide.** The adapter is the
only place an engine has a name; this stage says "the platform's design engine" and resolves it
there, which is what keeps an engine swap a one-file edit. A command copied into a stage guide is
the copy that goes stale, and a guessed command either fails noisily or installs the wrong thing.

The **orchestrator** does this. It runs in the plugin's own context, so it can read the skill's
`references/`; a dispatched **worker** cannot, and never resolves an engine itself — it is *told*
which one is in play, the same way it is told the platform.

**Why an otherwise headless skill is allowed to stop, here and nowhere else.** The engine renders
the artifact a client actually looks at. A run that quietly skipped rendering reports a finished
design with no prototype behind it — a clean-looking failure that survives review, which is worse
than not having run. Every other gap in this pipeline becomes an Open Question; this one becomes a
halt, and the only way past it is a line a human wrote in a settings file, never a fallback the run
chose for itself.

## Part 6 — Print the work-list, then keep going

This stage is **headless**. Print the work-list and continue — no confirmation, no halt. Part 5b's
engine check is the one exception, and it has already either passed or stopped the run.

```text
work-list:
  <slug>  UX-### (existing | new)  platform: web    — UC-003 NEW, UC-007 CHANGED (1.2 → 1.4), UC-009 CURRENT
  <slug>  design-only              platform: web    — 3 open directive(s)
  skipped <slug>/UC-###                             — <gate that failed>
mode: bootstrap | extend (design system v<x>)
platform: web | mobile | both (stated | defaulted)
engine: <name> ✔ | skipped — waived in project settings
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
- **Halting for anything but the missing engine.** A missing UC flow, an unclear directive, an
  ungrounded screen: all of those are skips and Open Questions. Part 5b is the only stop in this
  skill, and widening it turns an unattended pipeline into one that waits.
- **Naming an engine, or pasting its install command, into this guide.** Every stage guide is
  engine-agnostic so that swapping one is an edit to the adapter alone. The mention that gets missed
  in the next swap keeps calling a tool nobody has installed.

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
`{design_system_dir}`, and named hub sections — nothing else). A design run that stamped the config
would be writing a project-wide decision nobody stated, from a run nobody was watching, into the one
file every other skill reads as settled fact. Defaulting is recoverable and says so in its own
report line; a stamp is not, and the next reader has no way to tell it from something the client
said.

**Idempotent.** A config that already carries `platform:` — at any of the three values — is skipped
entirely, in both branches. This section fires on an absent key only, never on a value it happens to
disagree with.
