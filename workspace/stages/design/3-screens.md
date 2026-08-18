# Stage 3 — Screens: turn one feature's flows into a UX spec

```text
runs: one worker per FEATURE (a subagent, or the orchestrator inline for a small run)
in:   this feature's NEW/CHANGED UCs + its BRs, entities, directives, principles
out:  {ux_dir}/UX-<NNN> <Feature>.md — brief, screen inventory, screen specs, flows
      + a report of token/component/nav candidates (this stage NEVER writes the design system)
never: an invented screen · a raw colour/size · an invented nav entry · an edit to a UC, BR, or entity
```

Read `{design_conventions}` § The UX spec, § Screen spec, § Grounding, § Open questions, and
§ The navigation map first.

---

## Part 1 — Read the brief, in this order

```text
1  the hub                     {hub_dir}/<slug>.md   → ## Design Directives (Status: open), actors
2  each UC in scope, in full   ## 1 actors/trigger/pre+post · ## 2 steps · ## 3 branches
                               ## 4 rule mirror · ## 5 Still open (these are KNOWN GAPS)
3  each BR named in ## 4       the real rule text — the mirror is short on purpose
4  each EN in the UC's entities:  the field list, types, required?, enum values
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
- **Stamping `absorbed:` yourself.** Stage 5 stamps it, after verifying the screens exist.
