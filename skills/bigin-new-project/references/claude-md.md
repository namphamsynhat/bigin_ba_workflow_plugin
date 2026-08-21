# The project agent — CLAUDE.md

Runs from `/bigin-new-project` § 5.4, after the brief/proposal (§ 5.1–5.2) and, on `new`, domain
research (§ 5.3) are on record. Its job is to materialize a repo-root `CLAUDE.md` that lets *any*
Claude Code session opened in this repo — not just one running a `/bigin-*` command — pick up in
seconds what the engagement is, where the BA artifacts live, and which skill to reach for. Think of
it as the project's standing agent brief, not a second copy of `_bigin/system/project.md`.

## Why this repo's CLAUDE.md looks different from a codebase one

Most CLAUDE.md guidance (build/test/lint commands, module map, code style) assumes the repo *is*
software. This repo tracks *requirements for* software — the artifacts are UC/BR/EN markdown files,
not source, and the "commands" that matter are the plugin's slash commands, not `npm test`. Reuse the
same discipline (dense, current, pointer over prose, one clear place per fact) against a different
shape of content:

| Generic CLAUDE.md asks | This one asks |
|---|---|
| What's the build/test/lint command? | Which `/bigin-*` skill runs next, and when? |
| Where's the module map? | Where does each artifact type live, and who reads/writes it? |
| What's the code style? | What's non-negotiable about how a requirement gets recorded (traceability, no invented slugs)? |
| What are the gotchas in the code? | What's plugin-owned vs. project data, and where do overrides go? |

Keep it short — a screen or two, not a restatement of `_bigin/conventions/conventions.md`. A fact
that already lives in `project.md`, `FEATURES.md`, or the conventions file gets a pointer here, never
a duplicate copy that can drift out of sync with the source.

## What it must contain

1. **One-line identity** — client + what's being built, taken from the brief/proposal already on
   record. Not a paraphrase: the same restraint § 5.2 applies to the brief applies here.
2. **Project brief / domain grounding pointer** — one line each to `_bigin/system/project.md`'s
   `## Project Brief` and, on `new`, `_bigin/system/domain-research.md`. Don't inline the content.
3. **Workspace map** — what lives where, only the paths a session actually needs to orient itself:
   `_bigin/system/project.md` (engagement config), `00-Inbox/` (raw intake), `01-Requirements/
   FEATURES.md` (feature registry) and per-feature hubs, `PRD.md`, `prototypes/`, `epics.md`. Say what
   each is, not how it's produced — that's the conventions file's job.
4. **Skill sequence** — the `/bigin-*` commands in the order a feature normally moves through them,
   each with a one-line "when to reach for this," so a session knows the next command without reading
   every SKILL.md. Source this from the plugin's own command list, not from memory — command names
   and order can move a version faster than a CLAUDE.md gets manually corrected.
5. **Non-negotiables that outlive any one skill** — the handful of rules that matter no matter which
   command is running: every requirement traces to a stated signal, never an invented one; feature
   slugs are permanent once artifacts reference them; `_bigin/{conventions,stages,templates}` are
   plugin-owned and overwritten on every `/bigin-new-project` run — a real override belongs in
   `.claude/bigin-ba-workflow-plugin.local.md`, never edited in place.
6. **Engagement snapshot** — client and project mode (`new`/`ongoing`), pulled from `project.md`'s
   frontmatter. Enough for a session to know who the engagement is for and whether it's greenfield
   without opening a second file.

Leave out anything a generic template would ask for that doesn't apply here: there's no build/test/
lint command, no runtime environment, no package manifest. Don't pad the file to match an unrelated
template's shape.

## Action

* **Check for an existing `CLAUDE.md` at repo root first.** On `ongoing`, one is more likely than not
  — the codebase already has its own, code-focused CLAUDE.md (build commands, architecture, code
  style) from unrelated tooling or a prior `/init`. **Never overwrite it.** Add or replace a single
  delimited section instead:

  ```markdown
  <!-- BEGIN bigin-ba-workflow-plugin -->
  ...the content from "What it must contain" above...
  <!-- END bigin-ba-workflow-plugin -->
  ```

  A rerun (plugin upgrade, re-initiate) replaces only what's between those markers, the same
  overwrite-what's-plugin-owned discipline § 2 already applies to `_bigin/conventions/`. If the
  markers aren't found in an existing file, append the section at the end rather than guessing where
  it belongs.
* **No existing file** — write a new `CLAUDE.md` with the same delimited section as its whole body,
  so a later merge (this section growing a neighbor, e.g. a code-focused one added afterward) still
  has something to anchor to.
* **`ongoing` with no domain research to point to** — skip item 2's domain-research line entirely
  rather than writing a broken pointer; § 6's codebase map is deferred too, so the workspace map
  (item 3) is what carries most of the orientation weight for this mode.

## Rules

- **Pointer over prose, same rule as § 5.3's findings.** If a fact needs updating in two files when
  it changes, it'll only get updated in one. `CLAUDE.md` cites; it doesn't restate.
- **This file is read on every session's first turn, not just BA ones.** Padding it with anything
  that isn't true and useful in *every* session is a tax every future session pays — keep it to what
  actually orients a cold start.
- **Don't invent the skill sequence from memory.** Read the plugin's own `commands/` (or the
  frontmatter `description` of each `bigin-*` skill) for the current name and order rather than
  hand-typing a list that drifts the next time a command is renamed.
- **Re-running this step is expected and safe.** A plugin upgrade or a re-initiate (§ 1) regenerates
  the delimited section from whatever's now on record in `project.md` — treat it the same as § 2's
  "plugin-owned, overwritten every run" for everything between the markers, and nothing outside them.
