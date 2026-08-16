# Stage 1 — Scope: find the use cases that have no current design

```text
runs: orchestrator, FIRST
in:   $ARGUMENTS (a slug, a UC-###, or nothing) + every feature hub
out:  the work-list: per feature, which UCs are NEW, which are CHANGED, which are CURRENT
never: designing anything · reading a whole UC yet · touching a file
```

Read `{design_conventions}` § Staleness before this stage. It defines the three-way read below.

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

## Part 5 — Mode

```text
{tokens_file} absent  → BOOTSTRAP   Stage 2 creates the design system
{tokens_file} present → EXTEND      Stage 2 loads it and adds to it
```

Announce the mode in the report. On `BOOTSTRAP`, two or more features make a better first design
system than one — but one is allowed; just say the system will be thin.

## Part 6 — Print the work-list, then keep going

This stage is **headless**. Print the work-list and continue — no confirmation, no halt.

```text
work-list:
  <slug>  UX-### (existing | new)  — UC-003 NEW, UC-007 CHANGED (1.2 → 1.4), UC-009 CURRENT
  <slug>  design-only             — 3 open directive(s)
  skipped <slug>/UC-###           — <gate that failed>
mode: bootstrap | extend (design system v<x>)
```

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
