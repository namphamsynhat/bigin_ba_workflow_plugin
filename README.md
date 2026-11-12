# Bigin BA Workflow Plugin

A Claude Code plugin for the BA, Dev and QC team. AI does the heavy work: it reads client communication and
writes use cases, rules, designs and stories. People review it **fast**: short cards show what changes and
which lines the AI assumed. Then devs build from a pack their coding agent can read.

**Who does what**

| Role | Owns |
|---|---|
| BA / PO | intake, use-case approval, story approval, checking the estimate |
| Dev | the estimate, the code, one PR per story |
| QC | the acceptance criteria tests, the regression list |
| Dev lead | reviews an estimate only when the BA says it is too high |

---

## Install

```
/plugin install bigin-ba-workflow-plugin --marketplace namphamsynhat/bigin_ba_workflow_plugin
```

Older Claude Code: `/plugin marketplace add namphamsynhat/bigin_ba_workflow_plugin`, then
`/plugin install bigin-ba-workflow-plugin@bigin-ba-workflow`.

Once per project: run **`/bigin-new-project`**. It creates the workspace (the "vault") and asks for the
project settings. After a plugin update, run **`/bigin-upgrade-project`**.

---

## The workflow, step by step

```
 1 Capture ─► 2 Extract ─► 3 Use cases ─► 4 Approve UC ─► 5 Design ─► 6 Stories
                                                                          │
 9 Build ◄── 8 Estimate ◄── 7 Approve stories + 15-minute walkthrough ◄──┘
```

**Tip:** if you are not sure what runs next, use **`/bigin-run`**. It reads the vault, picks the next step
and keeps going until something needs a human.

### 1. Capture — BA, every morning
**`/bigin-intake`** saves new meetings, emails, Jira tickets, Confluence pages or a typed note into
`00-Inbox/`, unchanged. A Jira ticket is tracked: later sweeps add only its new comments.

### 2. Extract — BA
**`/extract-signal`** reads each new note, pulls out every requirement, files it under its feature, and
writes an **Analysis** on the note: which features and use cases it touches, what it contradicts, and what
is unclear.
- A request the client takes back: `scripts/bigin note withdraw INT-### --reason "…"`.
- A whole feature dropped: `scripts/bigin feature withdraw <feature> --reason "…"`.

### 3. Use cases — BA
**`/bigin-transform-signal`** turns the filed requirements into use cases (`UC-###`) and business rules
(`BR-###`). It never guesses: a missing fact becomes an **open question**.
- Answer the questions in the file, then run `/bigin-run` (or say "process UC-00X").
- Questions for the client: `scripts/bigin questions pack`, then send the file from `06-Outbox/`.
- Client-friendly view to share: **`/client-view`**.
- A use case that grew too big: **`/restructure-uc`**.

### 4. Approve use cases — BA / PO
**`/approve-uc UC-###`** once it has no open questions. Later, run **`/sync-entities`** to update the
data dictionary.

### 5. Design — BA / designer
**`/bigin-generate-design`** writes the screens and user flows (`UX-###`), then **`/bigin-render-ux-frame`**
and **`/bigin-assemble-prototype`** build a clickable prototype.

### 6. Stories — BA
**`/bigin-generate-stories`** cuts approved use cases into epics and user stories (`EP-###`, `US-###`),
each with acceptance criteria and frozen screenshots of the prototype. A change to an approved story
becomes a new **delta story**; the approved one is never rewritten.

### 7. Approve stories and walk through — BA + Dev + QC
**`/approve-story EP-###`** shows the **dev cards**: one short page per screen (and per back-end process
with no screen). Each card has:
- **Before → After** for every change, with the client request it came from
- the rules on that screen, what is out of scope, open questions, acceptance criteria titles
- **AI assumed (check these!)**: lines no client request asked for. Review these first.
- **Unchanged but affected**: what QC should regression-test

Then hold a **15-minute call** (BA + Dev + QC) on the cards and the prototype. Confirm or reject every
"AI assumed" line. A confirmed one becomes a story § 8 *Decision*; a rejected one becomes a question or a
new intake note.

| Command | Gives you |
|---|---|
| `scripts/bigin card EP-### --write` | `_cards.md` — the cards for the call |
| `scripts/bigin card EP-### --for jira --write` | `_jira.md` — paste-ready text per story. **A human copies it into Jira**; the plugin never posts to Jira |

To make the stories step write the cards automatically, set `dev_card: on` in `_bigin/system/project.md`.

### 8. Estimate — Dev, checked by BA
1. `scripts/bigin card EP-### --estimate` creates `_estimate.md`: one section per card, one row per change
   or acceptance criterion.
2. The **dev** fills in Task, Hours (with AI) and Notes. Add more task lines under a row by leaving Key
   blank. Use your coding agent's plan step on the build pack (step 9) to find the tasks.
3. The **BA** checks the sheet row by row against the cards:
   - a task with no card row → extra scope, or a misunderstanding
   - a card row with no task → missed scope
4. Only if the BA still finds the total too high does the **dev lead** review it.

Running `--estimate` again keeps every line the dev wrote. It only adds new rows and moves rows whose
source is gone under **Source removed**.

### 9. Build — Dev
`scripts/bigin card US-### --for agent --write` creates `_build/US-###.md`, one self-contained file per
story: the story, its use-case steps, the full rule text, entity fields and prototype files. Give it to
your coding agent (Claude Code). The rules inside:
- put `US-###@version` in the PR title
- name each test after its acceptance criterion, e.g. `US-004 AC3 — Slot taken`
- stop and ask when the pack does not answer something

QC checks that every acceptance criterion has a test with its name.

---

## Rules for everyone

- **Plain English.** Short sentences (≤ 25 words), one term for one thing. `bigin lint` gives advice
  when a story text is too long.
- **One story ≈ one PR ≈ one dev-day.** Lint gives advice above 8 acceptance criteria or 3 screens.
- **Never edit engine-made files** (`_cards.md`, `_estimate.md` scope rows, `_build/`, `_jira.md`).
  Fix the story, use case or design, and run the command again.
- **Check before trusting.** If a line has no source, it is in "AI assumed". Nobody approves without
  reviewing that list.

## Useful commands

| Command | What it does |
|---|---|
| `/bigin-run` | Do the next step |
| `scripts/bigin digest --for ba\|client\|dev` | What came in, changed, was decided, is waiting |
| `scripts/bigin questions` | Every open question, its age and what it blocks |
| `scripts/bigin impact INT-###` | What one request touches across the vault |
| `scripts/bigin lint` | Check the vault |

## More detail

- [USER_GUIDE.md](USER_GUIDE.md) — every skill and command in depth
- [docs/PIPELINE.md](docs/PIPELINE.md) — the full pipeline reference (stages, engine, configuration)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the plugin is built
- [docs/MIGRATION.md](docs/MIGRATION.md) — what changed in each version
