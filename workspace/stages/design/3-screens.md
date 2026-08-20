# Stage 3 — Screens: turn one feature's flows into a UX spec

```text
runs: one worker per FEATURE (a subagent, or the orchestrator inline for a small run)
in:   this feature's NEW/CHANGED UCs + its BRs, entities, directives, principles
out:  {ux_dir}/UX-<NNN> <Feature>.md — brief, screen inventory, screen specs, flows
      + ## 7 Relationship Model, on a feature that passes Part 4b's trigger (most do not)
      + a report of token/component/nav candidates (this stage NEVER writes the design system)
never: an invented screen · a raw colour/size · an invented nav entry · an edit to a UC, BR, or entity
       · a memory, autonomy, or retention rule the requirements did not state (D7)
```

Read `{design_conventions}` § The UX spec, § Screen spec, § Grounding, § Open questions,
§ The relationship model, and § The navigation map first.

---

## Part 1 — Read the brief, in this order

```text
1  the hub                     {hub_dir}/<slug>.md   → ## Design Directives (Status: open), actors
2  each UC in scope, in full   ## 1 actors/trigger/pre+post · ## 2 steps · ## 3 branches
                               ## 4 rule mirror · ## 5 Still open (these are KNOWN GAPS)
3  each BR named in ## 4       the real rule text — the mirror is short on purpose
4  each EN in the UC's entities:  the field list, types, required?, enum values
                               — note any field holding per-user history, preference, pattern, or
                                 score: Part 4b's trigger turns on whether one exists
5  {design_principles_file}    rows with Status: active
6  {tokens_file} + {components_dir}   what already exists, so you cite instead of invent
7  {nav_map_file}              its ## Structure — the tree that already exists, at whatever depth,
                               so a new entry joins an existing branch instead of starting a
                               parallel one
8  the existing UX spec, if any        you UPDATE it; you never fork it
9  every other UX-*.md in {ux_dir}     how a sibling feature already solved a list, a queue,
                                       an approval, a wizard. Reuse beats inventing (ground 2).
```

Write `## 1 Design Brief` from steps 1–5: actors, platform, the principles applied, the directives
applied, and the known gaps (each open UC question, one line, marked as a gap).

Stop reading here. A PRD, an INT note, `## Raw`, or a Signal Log row is not design input.

---

## Part 2 — Flows become screens

The UC says **what happens**. It does not say **how many screens**. This is the mapping:

```text
per UC, walk ## 2 in row order:
    a run of consecutive steps by the SAME actor in the SAME place  → ONE screen
    the actor moves to a different place or task                    → a NEW screen
    a step whose actor is the SYSTEM only                           → NOT a screen
                                                                      (it is a state, or invisible)
    a step that only validates                                      → a STATE on the current screen
    a ## 3 A-flow (alternative)                                     → usually a state or a variant
    a ## 3 E-flow (exception)                                       → an error STATE, named
    a ## 3 flow that changes place                                  → its own screen
```

Then merge across UCs:

```text
two UCs whose steps land on the same place → ONE screen serving both. List both UCs in `serves`.
```

Screen count sanity: a 3–9 step user-goal UC normally yields **1–4 screens**. Ten screens from one UC
means states got promoted to screens. One screen for four different tasks means screens got merged
that should not be.

**Never add a screen no step needs.** No login, settings, profile, dashboard, or help screen unless a
step, a rule, or a directive puts it there. An invented screen looks exactly like a designed one.

Write the result into `## 2 Screen Inventory`:

```text
| Screen | Purpose | Serves | Entities | Key actions |
                     ^ UC-### S4, S5   ^ EN-###   ^ the real buttons
```

---

## Part 2b — Which of these screens get a nav entry

Most screens in the inventory above are **not** menu items — they are reached by clicking through
from one that is. Read `{design_conventions}` § The navigation map before this part.

```text
per screen in the inventory:
    is it reached ONLY via another screen's control (a detail from a list, a step in a wizard,
    a modal, a confirmation)?                                          → NO entry
    is it something the actor opens directly, on its own, from a menu?  → nav candidate

    for each nav candidate, where does it sit in the tree that already exists?
        joins an existing branch, at whatever depth it lives          → cite that branch (e.g.
                                                                          "under settings.team")
        needs a whole new branch (no existing container fits)         → propose one, grounded the
                                                                          same way a screen is (a
                                                                          UC/BR, an existing branch
                                                                          in {nav_map_file}, or a
                                                                          stated preference) — say
                                                                          how deep it nests and why
        which roles see it                                            → the UC's § 1 actors, or a
                                                                          BR — never guessed
```

Nesting depth is itself a grounded decision, not a default. "Settings → Team → Members" is right
when the UC actually reads as a sub-area of Team; forcing three levels because it looks tidier is an
invented information architecture the same way an invented screen is.

**A feature normally contributes 0–2 nav entries**, not one per screen. Zero is common and correct —
most of a feature's screens are steps inside a flow the actor reaches from the one entry point.

---

## Part 3 — One screen spec per screen (`## 3`)

```text
purpose       one line
serves        UC-### S<n> …            every S# must exist and not be removed
regions       header · nav · main · aside · footer   (semantic HTML, not a pixel layout)
elements      per element:
                what it is        heading | table | form field | button | badge | ...
                content/copy      the real words, in the client's language
                token(s)          BY NAME, from {tokens_file}. Never a hex, px, or font name (D2)
                field             the EN-### field it renders, when it renders one
                grounded by       UC-### S<n> | BR-### | EN-### field | pattern <name> | directive #<n>
states        see Part 4
interactions  control → what happens → which screen or state comes next
```

**Fields come from the entity, not from imagination.** An `EN-###` gives you the field list, the
types, which are required, and an enum's real options — which are the dropdown's real options. An
entity still at `proposed`/`draft` is a **known gap**: use it, and say next to it that the field list
is not settled.

---

## Part 4 — States, and where each one comes from

Every screen gets the states it can actually reach. Each traces to something:

| State | Comes from |
|---|---|
| empty | a list/table whose source can legitimately be empty |
| loading | any screen that waits on the system — one per screen, not per element |
| validation-error | a `BR-###`, or an entity's required/format constraint |
| permission-denied | a `BR-###` about who may do this, or the UC's `## 1` actors |
| failure | an `E#` exception flow — one state per exception, named after it |
| success | the UC's `## 1` success post-condition |

A state with no source is invented. Leave it out, or ask.

---

## Part 4b — The relationship model (`## 7`), on the few features that earn one

Most features do not. Run the trigger test; on a miss, **delete `## 7` from the spec** and move on —
an empty `## 7` claims the relationship was considered when nobody looked. Read
`{design_conventions}` § The relationship model before writing anything here.

### The trigger — three tests, all three from sources you already read in Part 1

```text
1  the SYSTEM JUDGES, it does not just process
     a ## 2 or ## 3 step where the system suggests, recommends, predicts, scores, ranks, drafts,
     or decides on the actor's behalf
     NOT: "the system validates" · "the system saves" · "the system sends" · "the system displays"

2  it PERSISTS something about THIS user, between sessions
     an EN-### field holding per-user history, preference, pattern, score, or learned model
     NOT: an audit log · a status field · a created/updated timestamp · a role or permission

3  the relationship REPEATS
     the UC's ## 1 trigger recurs for the SAME actor — a queue they work daily, an assistant they
     come back to
     NOT: a one-off application, signup, purchase, or onboarding

3 of 3    → MODELLED.  write ## 7, set relationship_model: modelled
any miss  → NONE.      delete ## 7, leave relationship_model: none, and name the failed test in
                       your report — a near-miss is worth a human seeing
```

Test 2 is the one that does the work. A screen with a chatbot on it, an "AI suggestions" panel fed
by nothing stored, or a report the system ranks the same way for everyone all fail it — and none of
them has a relationship to model. **Never pass a test on a plausible reading**: the step verb, the
entity field, and the trigger are either there or they are not.

### What you write, and what grounds it

Four sub-blocks (the template carries the tables). Every row is grounded per § Grounding or it is
not a row:

```text
Relationship Context   duration · frequency · the AUTONOMY CEILING · memory sensitivity
                       ← a UC trigger/post-condition, a BR, an active principle row, a directive
                       "not stated" is a real value → a requirement gap in ## 6. Never a plausible
                       number: "users return weekly" invented here becomes a fact downstream.

Memory Architecture    what it carries between sessions · WHICH EN-### FIELD holds it · which
                       screen surfaces it · who may see, correct, or clear it
                       ← the entity field, ALWAYS. No field → not a row, a requirement gap.

Trust Map              per screen or per agent decision: what it SHOWS vs what it DOES at stage 1
                       (transparent) / 2 (selective) / 3 (autonomous), and the correction path
                       ← a BR about who may do this, a confidence/threshold rule, or an E-flow
                       Only fill a stage a BR actually GRANTS (D7). An unfilled stage 3 is the
                       correct answer when nothing granted autonomy.

Proposed Measures      at most THREE, owner team, each naming what would be observed and which row
                       above it tests. Never a requirement, never a target, never a screen.
```

A trust stage is **not** a state. `## 3`'s States table is within one session (empty, loading,
error, success). A trust stage is the same screen at relationship month 1 versus month 12 — put it
in `## 7` and, where it changes what a screen shows, note the stage next to that element in `## 3`.

### The guardrail — this is where an agentic run goes wrong

An installed relationship-UX skill hands you a pattern catalog: memory dashboards, goal dashboards,
planning canvases, preference-evolution maps, contextual timelines. Those are **whole screens**, and
they arrive with a citation, which makes an invented screen look designed.

```text
an external pattern is ground 2b (§ Grounding) — it shapes HOW something already grounded is built.
it can NEVER ground THAT a screen, field, or state exists.

"the relationship-UX skill recommends a memory dashboard"     → not a ground. Not a screen.
"UC-014 S3: the reviewer checks what the assistant learned"    → a ground. Now design that screen,
                                                                 and use the catalog for its shape.
```

Same test as Part 2's: **never invent a screen the flow never asked for**, however good the pattern.

### The gaps are the deliverable

A UC almost never states an autonomy ceiling, a retention rule, or who owns the memory. So a real
agent feature produces **more requirement gaps here than design rows** — that is this section
working, not failing. Each one goes in `## 6`, marked `requirement-gap`, and belongs to
`/bigin-transform-signal`. Write none of them onto the UC (D4).

The recurring five, all requirement gaps whenever unanswered:

```text
what may the agent do WITHOUT asking, and above what confidence?   → autonomy. A BR, or a gap.
how long is this remembered, and can the user clear it?            → retention. A BR, or a gap.
who else can see what it learned about this user?                  → visibility. A BR, or a gap.
what happens when it is WRONG — who is accountable, what is undone? → an E-flow, or a gap.
does the user know it is learning from them?                        → disclosure. A BR, or a gap.
```

## Part 5 — When you do not know

```text
grounded in a requirement | an existing pattern | a stated preference   → design it, cite the ground
grounded in none of the three                                          → ASK. Never guess. (D3)
```

Write the question on the UX spec's `## 6`:

```text
- [ ] Q: <self-contained, plain business language> (owner: client|team) (ref: UX-###)
      A:
```

```text
the answer changes how it LOOKS/READS        → a design question. Owner: client (or team).
the answer changes what the system DOES      → a REQUIREMENT GAP. Say so in the question,
                                               report it, and let /bigin-transform-signal own it.
                                               Do NOT write it onto the UC yourself (D4).
already open on the UC's ## 5                → do not re-ask it. It is already a known gap.
```

Two or three real questions per feature is healthy. Twenty means questions are being manufactured;
one means grounding is being skipped.

---

## Part 6 — Write the file

```text
no UX spec for this feature  → create {ux_dir}/UX-<NNN> <Feature>.md from {template_ux}
                               (the orchestrator gave you the number — never mint your own)
one already exists           → UPDATE IT IN PLACE: bump version, append a ## Changelog line
                               naming the UCs this run designed. Never create a second one.
```

Fill `## 4 Flows` last: per UC, entry → screens in order → success end and failure ends, one line
each, mirroring the UC's own flow without restating its steps.

Set `relationship_model:` from Part 4b — `modelled` with `## 7` filled, or `none` with `## 7`
deleted. An **existing spec created before `## 7` existed** simply has no such section: add it if the
trigger passes now, and otherwise leave the spec without it (§ Adopting an existing UX spec below).

Leave `status: draft`. Leave `absorbed:` **empty** — the orchestrator stamps it in Stage 5, after it
has checked which UCs really got screens.

---

## Part 7 — Report, do not write

```text
DO NOT WRITE   {tokens_file} · {components_dir} · {nav_map_file} · another feature's UX spec/hub
               DESIGN-PRINCIPLES.md · any UC, BR, or entity · FEATURES.md
REPORT INSTEAD token candidates · component candidates · nav candidates · cross-feature screens
```

Report lines:

```text
feature:            <slug>
ux:                 UX-### created|updated  — <N> screens (<N> new, <N> updated)
screens:            <screen> serves UC-### S<n>, S<n>  (one line each)
tokens_used:        <existing token name> (one line each)
token_candidates:   <proposed name> | level: 2|3 | value: <raw> | why: <what it means> | on: <screen>
component_candidates: <name> | variants: … | states: … | used on: <screen>, <screen>
nav_candidates:     <entry label> | parent: <existing id it nests under, or "new: <path>", or "top-level">
                    | points to: <screen> | role(s): <actor(s)>
                    | grounded by: <UC-### S<n> | BR-### | pattern <name>>
directives_reflected: hub row #<n> → <screen>  (one line each — only rows a screen really implements)
relationship:       modelled | none — <the test that failed, when none: judges|persists|repeats>
relationship_rows:  context <N> | memory <N> | trust <N> | measures <N>   (omit when none)
questions:          <the question>, owner client|team, kind: design|requirement-gap
designed_ucs:       UC-###@<version>  (one line each — ONLY UCs that really got screens)
blocked:            UC-### — <why, one line>
```

## Failure modes

- **Inventing a screen the flow never asked for.** The most expensive mistake here: it reaches a
  client as if someone had specified it.
- **Promoting every validation to its own screen.** A ten-screen spec for a five-step flow.
- **Hardcoding `#2563eb` because the token did not exist yet.** Propose the token and cite its name.
- **Making up form fields.** The entity has the fields. If it does not, that is a question.
- **Re-asking a question the UC already has open.** The human answers it twice and the copies drift.
- **Creating a second UX spec for a feature that has one.** The review splits and both go stale.
- **Writing the design system or nav map from here.** Two features run at once; the second write loses.
- **Proposing a nav entry for a screen reached only through another screen.** It reads as a second
  door into the same room, and the two drift the first time one changes.
- **Nesting a nav entry three levels deep because it looks tidier.** Depth is grounded like anything
  else; an ungrounded sub-group is an invented IA.
- **Writing `## 7` because the feature has AI in it.** The trigger is three mechanical tests, and
  test 2 — a real `EN-###` field holding per-user history — is the one that fails most often. A
  relationship model over nothing stored describes a relationship the system cannot have.
- **Letting a pattern catalog ground a screen.** A memory dashboard nobody asked for reaches the
  client carrying a citation, which is worse than an obvious guess: it reads as specified.
- **Filling a stage-3 autonomous cell no `BR-###` granted.** The prototype then shows the agent
  acting alone, the client sees it working, and nobody ever decided it was allowed (D7).
- **Inventing a retention or frequency figure.** "Cleared after 90 days", "users return weekly" —
  written here, they are quoted downstream as though a client said them.
- **Leaving `## 7` in place, empty, on a feature that failed the trigger.** It reads as "we looked
  and there is no relationship here" when the opposite is true.
- **Stamping `absorbed:` yourself.** Stage 5 stamps it, after verifying the screens exist.

## Adopting an existing UX spec

`## 7 Relationship Model` was added to `{template_ux}` after some specs already existed. There is no
content to transform and nothing to migrate:

```text
spec has no ## 7, trigger passes now   → add the section, set relationship_model: modelled
spec has no ## 7, trigger misses       → leave it exactly as it is. `relationship_model:` absent
                                         reads the same as `none`.
spec HAS ## 7 from an earlier run      → update it in place like any other section. Never fork it.
```

Every spec self-heals on the next design run of its feature. A spec whose feature is never redesigned
keeps working — nothing downstream requires `## 7` to exist.
