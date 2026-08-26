# The Open Design adapter — the engine contract

Read by `/bigin-render-design` at Step 0, and **in full** by `render-screen-worker` and
`render-prototype-assembler`. This is the only file in the plugin where an Open Design tool has a name.

## Do we need to build an adapter? No — and here is why that matters

Open Design already *is* the adapter. Its daemon carries a runtime definition per agent CLI
(`apps/daemon/src/runtimes/defs/`), each one a data literal describing binary detection, the argument
builder, the stream format, and model discovery — roughly 25 CLIs, invoked **headlessly** with
non-interactive permission modes (`claude -p --permission-mode bypassPermissions`,
`codex exec --json`, `cursor-agent --print --output-format stream-json`, …). When a run starts it
resolves the agent, composes the prompt from the bound design system + skills, spawns the CLI in the
project directory, and parses the stream into typed events.

```text
what OD already does          spawn a CLI, manage its loop, compose the system prompt from the
                              bound design system, write files into the project, stream events
what we would gain by
building our own adapter      nothing. We would be re-implementing the thing we are calling
what we DO need               a NORMALISED CALL SEQUENCE — this file — so that every step of a
                              render calls the same tools in the same order with the same retry
                              and idempotency rules, instead of each agent improvising
```

So: **no adapter code, no process spawning from our side, no daemon HTTP calls.** Everything goes
through the MCP tools below. What follows is the sequence, and the parts of it that are easy to get
wrong.

**One consequence worth stating plainly.** Because Open Design spawns its *own* agent, the model doing
the rendering is **not** the model reading this file. Our agents write the prompt and judge the
result; Open Design's agent writes the HTML. That is the whole reason the prompt contract
(`prompt-contract.md`) is as strict as it is — it is the only channel to a process that cannot see the
vault.

---

## § Probe — is Open Design connected?

```text
1  claude mcp list
2  find a row whose server name CONTAINS "open-design", case-insensitively
       ── SUBSTRING, never an exact name. The name is whatever `od mcp install claude` registered
          on this machine and it is not guaranteed to be a fixed string
3  that row's state must read ✔ Connected
4  resolve the TOOL PREFIX from that row's server name: mcp__<server-name>__<tool>
       ── every tool below is called as <prefix>list_projects, <prefix>start_run, and so on
5  smoke-test it: call list_projects. A response proves the daemon is up, not just the row
```

**`command -v od` proves nothing.** `/usr/bin/od` is the BSD octal-dump utility and wins on `PATH` on a
stock macOS, so a resolving `od` is not evidence Open Design is installed and a bare
`od mcp install claude` typed into a terminal may run the wrong program. The CLI is not on this skill's
path anyway — the MCP server is the interface. If a CLI probe is ever wanted, it is
`od project list --json` (octal-dump errors out; Open Design returns JSON), never `command -v`.

```text
row absent           HALT. Report, do not install:
                       od mcp install claude
                     or, on a macOS desktop install, the app's Settings → MCP server snippet — the
                     project's README says to prefer it. NEVER sudo, NEVER a package manager,
                     NEVER auto-install: it is a desktop app that installs software on the machine
row present, ✘       the daemon is down. Ask the human to open the Open Design app, then retry
tools erroring       § Retry ladder
```

Then `/bigin-render-design` § The manual fallback, always — a halt still produces the prompts.

---

## § The tool surface

Every tool below takes `project` as a **UUID or a name substring**; omitted, it defaults to the
*active* project (what the human has open in the app), which **expires ~5 minutes after their last
interaction**. This skill never relies on that fallback: it resolves an explicit project id at Step 0
and passes it on every single call. A run that quietly targets "whatever was open" is a run whose
output lands somewhere nobody chose.

When a project is matched by substring the response carries `resolvedProject:{id,name}` — read it and
confirm the match was the intended one.

### Discovery

| Tool | Takes | Returns / use |
| :--- | :--- | :--- |
| `list_projects` | — | every project on this daemon. The menu for Step 0.2 |
| `resolve_project` | fuzzy name | a UUID. Use when the human typed a name |
| `get_project` | `project` | name, **bound design-system and skill ids**, `entryFile`, kind, timestamps, `resolvedDir`, `previewUrl`. This is how you read back which design system a shared project already carries |
| `get_active_context` | — | what the human has open right now, or `{active:false, hint}`. Offer as an option at Step 0.2; never assume it |
| `list_agents` | `includeUnavailable?` | **the model authority.** Installed agent CLIs by default: `id`, `name`, `version`, up to 10 sample models, `modelsCount`. `includeUnavailable:true` also lists known-but-absent agents with an `installUrl` to show the human |
| `list_skills` | — | Open Design skill ids passable to `start_run{skill, skills}`. Discovery only — **we do not run a skill, we commission Open Design to** |
| `list_plugins` | — | installed Open Design plugins, passable as `start_run{plugin, inputs}` |

### Design systems are RESOURCES, not tools

There is no `list_design_systems` tool, and looking for one and failing is how a run ends up guessing
an id. They are MCP **resources**:

```text
resources/list          →  od://design-systems/<id>/DESIGN.md   one per available system
                           od://skills/<id>/SKILL.md            (skills, same shape)
                           od://focus/active                    the active project/file, as JSON
resources/read <uri>    →  that system's DESIGN.md prose — palette, typography, voice
```

`resources/list` is backed by the daemon's `GET /api/design-systems`, scoped to the signed-in
workspace, so what it returns is what the human sees in the app. That listing **plus** the vault's own
`{tokens_file}` is the complete menu for Step 0.3, and an id outside both halts the run.

Read `od://design-systems/<id>/DESIGN.md` when the prompt needs to state the brand explicitly — but
remember `{design_principles_file}` outranks it, and say so in the prompt where they disagree.

### Projects

| Tool | Notes |
| :--- | :--- |
| `create_project{name, id?, designSystem?, skill?}` | **the design system is bound HERE**, at creation. Returns the project with its id plus a `conversationId`. `id` is derived from `name` when omitted (`[A-Za-z0-9._-]`, ≤128 chars) |
| `delete_project{project, confirm:true}` | **this skill never calls it.** Irreversible, and no render has a reason to |

Bind the design system at creation. If the human picked the vault's own tokens rather than a catalog
system, create the project **without** `designSystem` and carry the token values into the prompt
instead — that is what makes the client's brand, rather than a shipped one, the thing that renders.

### Generation

```text
start_run{
  project,        the resolved id. ALWAYS explicit
  prompt,         the whole self-contained brief — see prompt-contract.md
  agent?,         an id from list_agents. Omit to use OD's configured runtime
  model?,         a model id from that agent's catalog. Omit with agent
  skill?/skills?, an OD skill id to drive the run. Optional
  plugin?/inputs? an OD plugin. Optional
  requestId,      ← see § Idempotency. Generate ONCE per feature, reuse verbatim
  resume?         true ONLY after a paused OD Cloud run was topped up, with the ORIGINAL requestId
}                 → { runId }  immediately. The run itself has not finished
```

```text
get_run{runId}    → status: queued | running | succeeded | failed | canceled
                    + error info
                    + previewUrl    on success — a browser link to the rendered design
                    + agentMessage  the inner agent's text, reassembled. READ THIS when there is no
                                    previewUrl: it is where a clarifying question the inner agent
                                    asked instead of producing files shows up
cancel_run{runId} → request cancellation. Only when the HUMAN asks to abort
```

`previewUrl` and any studio link are **browser links for the current Open Design runtime** — they
change when Open Design restarts. The durable identity is the run's artifact reference and, for us, the
copied-back files in `{prototype_dir}`. Never record a `previewUrl` as a `## 8` artifact path.

### Reading output back

| Tool | Use |
| :--- | :--- |
| `list_files{project, since?}` | file metadata: name, path, mime, kind, size, mtime. `since=<unix-ms>` makes it a cheap change poll — take the timestamp before `start_run` and pass it after |
| `get_artifact{project, entry, include?, maxBytes?}` | **prefer this over N `get_file` calls.** Bundles the entry plus every sibling it references (HTML `<script>`/`<link>`/`<img>`/srcset, JSX imports, CSS `url()`/`@import`) to depth 3, skipping CDN and data URLs. `include:"all"` = every file; `"shallow"` = entry only. Soft-capped ~1.5 MB and 200 files, with `truncated:true` when it hits either |
| `get_file{project, path, offset?, limit?}` | one text file, `limit` lines from `offset` (defaults 0 / 2000). Long files carry an `[od:file-window …]` marker with `totalLines` so you can page. **Text mimes only** — binary errors out; use `list_files` for its metadata |
| `search_files{project, query, pattern?, max?}` | case-insensitive literal substring across text files. Useful for a targeted check, not for reading a render |
| `write_file{project, path, content}` | **this skill never calls it to produce a design.** See the ban below |

### The `write_file` ban

`write_file` and `create_artifact` exist and this skill does not use them to make a screen. Ever.

```text
the temptation   a run is 20 minutes in, status is running, mtimes have not moved. Writing the HTML
                 by hand would "just be faster"
what it costs    the entire reason this skill goes through Open Design. The design quality lives in
                 OD's composed prompt, its bound design system, and its own agent's pipeline. A
                 hand-written substitute is this session's model producing a screen and calling it a
                 render — with a ## 8 row asserting Open Design made it
the rule         unchanged mtimes during `running` is the inner agent THINKING. Wait
```

Open Design's own MCP guidance says this in as many words. The only legitimate `write_file` in a
render is a correction the human explicitly asked for after seeing the output, and even then it is
recorded as a manual edit, not as a render.

---

## § Idempotency — the `requestId` contract

```text
generate ONE canonical UUID or ULID per feature, BEFORE its first start_run
reuse it VERBATIM on every retry of that feature's run
```

- Same id + same payload → Open Design treats it as the same logical action. A lost or timed-out tool
  response can be retried safely.
- Same id + **different** payload → **rejected.** This is the safety property, not a bug: it means a
  retry cannot silently become a different run.
- **Different** id → a *second* run. You now pay for the same feature twice and get two artifacts
  racing for the same output path.

A **repair round** is a different payload and therefore a **new** `requestId` — it is a new logical
action, correcting the previous one. A **retry** of a call whose response was lost keeps the old id.
The distinction is: did the prompt change?

---

## § Poll cadence and patience

```text
poll get_run(runId) every 30-60 seconds
a run normally takes 5-30 MINUTES
status:running with unchanged file mtimes  =  the inner agent thinking, NOT a hang
between polls, say "still working" — do not go silent for half an hour
```

**Do not cancel out of impatience.** `cancel_run` is for a human who asked to abort, and for nothing
else. Every alternative to waiting — cancelling, hand-writing the file, declaring the feature failed —
costs the render its reason for existing.

**A soft ceiling, and what to do at it.** If a single run passes ~45 minutes with no file activity at
all, stop polling and *report* it as still running with its `runId`, rather than cancelling or blocking
the whole render. The other features keep going; the human decides whether to wait or abort.

---

## § Retry ladder

For a tool call that errors, not for a run that is merely slow:

```text
1  immediate retry, once            transient stdio/daemon hiccup
2  wait 10s, retry                  daemon busy or restarting
3  wait 30s, retry                  daemon restarting after an app relaunch
4  re-probe (§ Probe)               is the server still Connected at all?
5  still failing                    → /bigin-render-design § The manual fallback
```

Every retry of a `start_run` reuses the **same** `requestId` (§ Idempotency). Read calls are safe to
retry freely — Open Design's own MCP layer retries safe reads and deliberately does not replay writes.

---

## § Copy-back procedure

```text
1  before start_run:   t0 = now, in unix-ms
2  after terminal:     list_files{project, since: t0}       what THIS run produced
3                      get_artifact{project, entry: "<the screen or index file>", include: "auto"}
                       ← ONE call pulls the entry plus its CSS, JS, and images
4  write every returned file into {prototype_dir}/<run>/ preserving its relative path
5  if the bundle came back truncated:true, fall back to get_file per remaining path, paging with
   offset/limit on anything over 2000 lines
6  binary assets: get_artifact carries them; get_file will NOT. Never try to page a binary
```

Copy back **before** writing any `## 8` row. The row is a pointer to files that must already exist.

---

## § Never let it

```text
pick a design system this run did not resolve             → Step 0.3 asks; a shipped system is
                                                              somebody else's brand
be given a guessed design-system or model id              → resources/list and list_agents are the
                                                              only authorities
target the ACTIVE project by omission                     → the active context expires in ~5 minutes;
                                                              always pass the resolved id
add a screen the spec's ## 2 does not carry               → § Grounding. Report it, do not keep it
substitute placeholder copy for the real words            → copy is content, and it was decided
invent a field, a status, or a capability in the dataset  → values are authored, structure is not
write into 04-UIUX/ (beyond {prototype_dir}) or
  01-Requirements/                                        → § Write map
be cancelled because a poll looked quiet                  → 5-30 minutes is normal
be replaced by write_file when it feels slow              → § The `write_file` ban
have its previewUrl recorded as the artifact path         → it dies with the runtime; the copied-back
                                                              folder is the durable artifact
```

Open Design's daemon is loopback-only and read-only by default. Nothing here needs that relaxed, so
do not.
