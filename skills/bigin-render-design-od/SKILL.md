---
name: bigin-render-design-od
description: Renders finished UX specs into one interactive prototype on Open Design. Syncs vault markdown (UX spec, UCs, BRs, entities) into an Open Design project, replacing stale copies, then runs one start_run per feature and assembles them into a single prototype. Invoked by a human when they ask to "render the prototype", "generate the design via Open Design", "sync features to Open Design", or "assemble the demo prototype" — never on the plugin's own initiative.
argument-hint: "[feature-slug ... | --all]"
disable-model-invocation: true
---

# Bigin Render Design — Open Design

Syncs requirement artifacts from the vault (`01-Requirements/`, `04-UIUX/`) into an Open Design
project and runs `start_run` per feature, then assembles the results into one prototype.

This skill hands Open Design's agent the real vault files via `@`-mention rather than a
fully-expanded prompt — the brief stays short, and the files stay the source of truth. (The earlier
`bigin-render-design`, which built a nine-section expanded brief and fanned out per screen, was
deleted in 1.8.7 along with its `render-screen-worker` and `render-prototype-assembler` agents.)

## Invoking the scripts

Both scripts live inside this skill, and the working directory at run time is the **vault**, not this
directory. Always call them by absolute path:

```bash
SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/bigin-render-design-od"
```

`${CLAUDE_PLUGIN_ROOT}` does not resolve inside a subagent. Expand it here, in the main session, and
pass the resolved absolute path to `render-feature-od-worker` — never the variable.

## Precondition

Run the preflight first. It answers every question below from disk in one call — no `list_projects`,
no `list_agents`, no resource listing, and so no precondition traffic in context:

```bash
python3 "$SKILL_DIR/scripts/check_setup.py"
```

It reports, and exits non-zero on any halt:

| It prints | Which settles |
| :--- | :--- |
| the `open-design` MCP row, connected, and its `mcp__<server>__` tool prefix | **1. Installed and connected.** Not connected → report the install, stop, never auto-install (§ Probe in the adapter) |
| every project — id, name, bound design system, last touched | **2. Which project.** Ask which one; its id is `od_project` for every MCP call after this |
| every installed design-system id, and the app default | **3. Which design system.** Ask which one. Never guess |
| every installed agent and its configured model | **4. Which model.** One obvious choice → use it. Ambiguous → ask. None usable → omit `agent`/`model` and let Open Design use its own runtime |
| the `od_*` already in `_bigin/system/project.md`, each marked still-valid or stale | **5. What not to re-ask.** Reuse what is still valid; re-ask anything marked stale |

Persist whatever the human answers back into `_bigin/system/project.md` (`od_project`,
`od_design_system`, `od_agent`, `od_model`) so the next render starts from it.

To read a design system's actual prose before writing a prompt — palette, typography, voice — the
catalog is exposed as MCP **resources**, not tools. Use `ListMcpResourcesTool` to enumerate and
`ReadMcpResourceTool` on `od://design-systems/<id>/DESIGN.md`. There is no `list_design_systems`
tool, and hunting for one is how a run ends up guessing an id.

## Workflow

Scope is whatever feature slugs the user names, or every feature hub with `--all`. Nothing renders
without a named scope.

### Step 1 — Sync

```bash
python3 "$SKILL_DIR/scripts/sync_feature.py" <slug> [<slug> ...] [--project <name>]
python3 "$SKILL_DIR/scripts/sync_feature.py" --all [--project <name>]
```

Copies each feature's UX doc, UCs, BRs, and entities into the Open Design project, overwriting
any stale copy and renaming each to a space-free name an `@`-mention can address. Prints the target
project's id and one ready-to-use prompt per feature — that printed list is the scope the rest of
this run acts on.

The feature hub itself is read (its frontmatter names the UCs/BRs/entities/UX doc in scope) but
never copied or `@`-mentioned: it carries unrefined raw material — Signal Log rows, open pain
points, internal ids — that is not something a screen may ground in (only UCs, BRs, and entities
are grounded inputs), and letting the render agent browse it risks a leaked internal reference the
Step 4 traceability check exists to catch.

### Step 2 — One worker per feature, one at a time

For each synced feature, in order — never two dispatched at once — spawn one
`render-feature-od-worker` and wait for it to finish before spawning the next. It turns the printed
prompt into a `start_run`, polls it to completion, and reports back.

### Step 3 — Assemble

```bash
python3 "$SKILL_DIR/scripts/sync_feature.py" --nav-map [--project <name>]
```

Then start one more run in the same project:

```text
Pull all the design features into the full demo prototype. Follow the navigation map for the
navigation of all actors or portals.
navigation map: @navigation-map.md
```

### Step 4 — Verify

Once the copy-back in Step 5 has files on disk, gate them deterministically — these are cheap, and
they catch the two failures a human eye misses:

```bash
"$SKILL_DIR/scripts/check-traceability.sh" "{prototype_dir}/<run>/" --require
"$SKILL_DIR/scripts/check-contrast.py" --tokens <the bound design system's tokens>
```

A leaked `UC-`/`BR-`/`EN-`/`UX-` id in visible copy is never a warning — it is an internal reference
a client can read, and the render is not deliverable until it is gone.

Open Design also often displays blank right after an assembly run finishes. Run the
`perception-first-design:evaluate` skill against the result; if that skill is not installed, open the
`previewUrl` and check by eye instead — never skip the check. If it looks blank or broken, send one
more run asking Open Design to fix the display, then check again.

### Step 5 — Report

Pull the generated design back into `04-UIUX/_prototypes/<date>-<slug>/` (§ Copy-back procedure in
the adapter). For each feature that rendered, append a row to its spec's `## 8 Rendered Artifacts`
and flip `rendered:` to `true` (`design-core.md` § Write map). Then report what was updated and generated — which
features rendered, and the prototype's path.

## Key instructions

Every prompt this skill sends — per feature and at assembly — carries these:

- Render self-contained HTML: inlined styles and scripts, no external stylesheet or script.
- Ground every input, validation rule, and state in the attached use cases and business rules.
- Follow the bound design system for every visual decision.
- Emit the `data-*` provenance attributes, and never print a UC-, BR-, EN-, or UX- id anywhere a
  user can read it — the block to quote is `references/traceability.md` § The block to quote.

This skill collects data and hands it to Open Design; it does not prescribe a fidelity bar of its
own. Density, chrome, and visual polish are whatever the **bound design system** (SMB, enterprise, or
startup) specifies — never a fixed assumption this skill bakes in.

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{ux_dir}` | `04-UIUX/` | one `UX-<NNN> <Feature>.md` per feature |
| `{prototype_dir}` | `04-UIUX/_prototypes/` | output — one folder per render |
| `{nav_map_file}` | `04-UIUX/_ux/navigation-map.md` | Step 3's single source of truth |
| `{hub_dir}` | `01-Requirements/_features/` | `<slug>.md` — what Step 1 syncs |
| `{project_file}` | `_bigin/system/project.md` | this skill's `od_*` settings |

## Write map

```text
WRITE   {prototype_dir}/<run>/                the copied-back artifacts
        spec's ## 8 Rendered Artifacts        one appended row per render
        spec's rendered:                      false → true
        {project_file} od_* settings          so the next render doesn't re-ask

NEVER   ## 1-## 7 of any spec, or anything else in 01-Requirements/    not this skill's to touch
        a design system, anywhere in the vault                        the bound system is the
                                                                       whole visual answer
```

## Failure modes

- Calling a script by a relative path — the cwd is the vault, so `scripts/…` resolves to nothing.
- Passing `${CLAUDE_PLUGIN_ROOT}` to a subagent unexpanded, where it does not resolve.
- Guessing a design system or project id instead of asking or confirming one.
- Dispatching feature workers concurrently instead of one at a time.
- Treating a blank post-assembly canvas as a failed render instead of running Step 4 first.
- Skipping the copy-back into `{prototype_dir}` and leaving the render only inside Open Design.
- Cancelling a run that's merely quiet — 5–30 minutes per run is normal.

## Resources

- **`scripts/check_setup.py`** — the Precondition preflight. `--json` for machine output,
  `--design-systems` for ids alone, `--no-mcp` to skip the (slow) `claude mcp list` probe.
- **`scripts/sync_feature.py`** — Step 1 and Step 3's sync.
- **`scripts/od_common.py`** — the discovery helpers both scripts share. Not run directly.
- **`scripts/check-traceability.sh <path>… [--require]`** — Step 4's gate. Positive half: the
  `data-*` attributes are present. Negative half: no vault id sits anywhere visible.
- **`scripts/check-contrast.py`** — WCAG 2.1 ratios, computed. `<fg> <bg> …` for pairs,
  `--tokens <file>` for a whole palette, `--pairs <file>` for a named list.
- **`references/open-design-adapter.md`** — the engine contract: § Probe, § The tool surface,
  § Idempotency (`requestId`), § Poll cadence, § Retry ladder, § Copy-back procedure, and the
  `write_file` ban. Read it when a run misbehaves or an MCP call needs its exact shape.
- **`references/traceability.md`** — the provenance block to quote into every prompt, and what the
  checker asserts about it.
- **`agents/render-feature-od-worker.md`** (plugin root, not this skill) — Step 2's per-feature worker.
