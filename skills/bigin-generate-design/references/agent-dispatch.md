# Worker dispatch — one per feature

```text
Agent(session default model, general-purpose, foreground)   # not haiku — this is judgment work
one per FEATURE SLUG
    → a feature's UX spec + hub are one ownership domain
    → features are independent, so they parallelize safely
≤ 4 features concurrently, verify between waves        # a failure costs one wave, not the backlog
within a feature → UCs designed sequentially, into ONE UX spec
```

**Skip the worker entirely for one or two features** — dispatch costs more than the work, and the
orchestrator can follow `3-screens.md` inline.

## Before dispatching — the orchestrator does these four things

```text
1  MINT THE NUMBER      Grep {ux_dir} for the highest UX-### and assign the next one per feature
                        that needs a new spec. Two workers grabbing the same number is why.
                        Use the Grep TOOL, never a shell pipeline — a denied pipeline reads as
                        "no existing ids" and silently reuses one.
2  SEED THE SYSTEM      2-system.md Part A, so token names exist before screens cite them.
3  RESOLVE OWNERSHIP    a cross-feature UC is designed ONLY in its primary_feature's spec.
                        Name it explicitly in both workers' prompts — the owner designs it,
                        the participant does not.
4  NAME THE ENGINE      pass the detected engine and one line on how to use it.
```

## The prompt

The worker has no memory of this conversation. Give it the cheap known facts and point it at real
files — a paraphrase risks it trusting a stale summary over the source.

```text
Design the screens for feature <slug>.

The output is a UX SPEC (UX-###): one per feature, holding a design brief, a screen inventory, a
screen spec per screen, the flows, and its open questions. Screens serve USE CASE steps: a UC-###
is one user goal with a numbered main flow (S1, S2 …) and branch flows (A1, E1 …). Screens cite
DESIGN TOKENS BY NAME, never raw values.

YOUR UX SPEC:        <UX-### (new — create it) | UX-### (exists — update it in place)>
UCs TO DESIGN:       <UC-### (NEW) | UC-### (CHANGED 1.2 → 1.4)> …
UCs NOT YOURS:       <UC-### (designed in <slug>'s spec)> …, or "none"
DESIGN ENGINE:       <wds | figma | <plugin> | built-in> — <one line on how to use it>
DESIGN SYSTEM:       04-UIUX/_design-system/design-tokens.md at v<x> — cite these names; propose
                     a new token only when nothing there fits.

READ FIRST:
- _bigin/conventions/design-conventions.md — these sections ONLY: § Paths, § Write map,
  § The six design hard rules, § The UX spec, § Screen spec, § Grounding, § Open questions,
  § The navigation map
- _bigin/stages/design/3-screens.md — your stage guide, in full
- 01-Requirements/_features/<slug>.md — the hub: ## Design Directives (Status: open), actors
- each UC above, in full: § 1 actors/trigger/post-conditions, § 2 steps, § 3 branches,
  § 4 rule mirror, § 5 Still open (KNOWN GAPS — work around them, never guess past them)
- every BR-### named in those § 4 mirrors, and every EN-### in the UCs' entities:
- 01-Requirements/DESIGN-PRINCIPLES.md — rows with Status: active
- 04-UIUX/_design-system/design-tokens.md and components/ — what already exists
- 04-UIUX/_design-system/navigation-map.md — its ## Structure (a dot-path `id` per row, so it can
  nest arbitrarily deep — "settings", "settings.team", "settings.team.members"), so a new entry
  joins an existing branch instead of starting a parallel one
- every other 04-UIUX/UX-*.md — how a sibling feature already solved a list, a queue, an
  approval, a form. Reusing an existing pattern beats inventing a parallel one.

THEN, one UC at a time, in the order listed:
1. Map its flow to screens (3-screens.md Part 2): consecutive steps by the same actor in the same
   place = ONE screen; a validation = a state; an exception flow = a named error state; a
   system-only step = not a screen. Merge screens two UCs both land on.
2. Decide which of those screens gets a nav entry (Part 2b): only one the actor opens DIRECTLY from
   a menu — never a detail, a wizard step, or a modal reached through another screen. Most features
   contribute 0-2 entries, not one per screen.
3. Write the screen spec (Part 3): regions, elements, real copy, TOKEN NAMES, the entity field
   each input renders, and what grounds each element.
4. Add the states (Part 4) — each traced to a BR, an exception flow, an entity constraint, or a
   post-condition.
5. NEVER invent a screen, a field, a state, a nav entry, a threshold, or a label the sources did not
   state. Missing detail is a question on § 6, not a plausible guess.

DO NOT WRITE — vault-wide or owned elsewhere, and other features run concurrently. Report
candidates instead; the orchestrator applies them:
  04-UIUX/_design-system/ (tokens AND components AND navigation-map.md) · another feature's UX spec
  or hub · 01-Requirements/DESIGN-PRINCIPLES.md · FEATURES.md
DO NOT edit any UC, BR, or entity — they are read-only here, in every section.
DO NOT fill absorbed:, do not set status: accepted, do not write either Prototype Prompt block —
the orchestrator does all three after your report.
Leave the spec at status: draft.

REPORT, as plain lines:
  feature:              <slug>
  ux:                   UX-### created|updated — <N> screens (<N> new, <N> updated)
  screens:              <screen> | serves: UC-### S<n>, S<n> | states: <N> (one line each)
  tokens_used:          <existing token name> (one line each)
  token_candidates:     <proposed name> | level: 2|3 | value: <raw> | means: <meaning> | on: <screen>
  component_candidates: <name> | variants: <…> | states: <…> | used on: <screen>, <screen>
  nav_candidates:       <entry label> | parent: <existing id it nests under, or "new: <path>", or
                        "top-level"> | points to: <screen> | role(s): <actor(s)>
                        | grounded by: <UC-### S<n> | BR-### | pattern <name>>
  directives_reflected: hub row #<n> → <screen> (only rows a screen really implements)
  questions:            <the question> | owner: client|team | kind: design|requirement-gap
  designed_ucs:         UC-###@<version> (ONLY UCs that really got screen rows)
  blocked:              UC-### — <why, one line>
```

## Verifying the wave

After each wave, before the next. Check the wave's **claims** — do not re-design anything. This
catches the failure that matters: a worker reporting screens it never wrote, which Stage 5 would then
stamp into `absorbed:`, making the feature read as designed forever.

```text
per feature in the wave:
1  the UX spec exists at the number you minted, and holds ## 2 rows matching the reported count
2  every reported screen  → a ## 3 block exists for it, with elements, states, and interactions
3  every `serves` S#      → exists in that UC's ## 2 and is not marked removed
4  no raw value           → Grep the spec for "#" hex codes, "px", and font names. Any hit is D2
                            broken and must be replaced with a token name (or a candidate)
5  every question         → an unchecked "- [ ] Q:" in ## 6, and not already open on the UC's ## 5
6  every reported nav candidate → NOT a screen reached only through another screen (re-check
                            against Part 2b's test); a violation is dropped, not applied
7  shared files untouched → git diff --stat shows NO change to 04-UIUX/_design-system/ (tokens,
                            components, AND navigation-map.md), DESIGN-PRINCIPLES.md, FEATURES.md,
                            or any file under 01-Requirements/ (the design system and nav map move
                            in Stage 4, in the orchestrator, not here)
8  absorbed: still empty  → Stage 5 stamps it, after check 1 has passed

mismatch → BLOCKING. Dispatch one scoped repair worker, re-check that feature, then move on.
```

```text
Repair 04-UIUX/UX-<NNN> <Feature>.md.

Its ## 2 Screen Inventory lists "<screen>" but ## 3 has no spec block for it. The screen serves
UC-<NNN> S<n>. Read _bigin/stages/design/3-screens.md Parts 3-4 and 01-Requirements/_ucs/
UC-<NNN> <Title>.md, then write ONLY that block: regions, elements (with token names and the
entity field each renders), states, interactions, and what grounds each.

Do not add a screen, do not touch any other block, do not write the design system, do not edit
the UC, and do not fill absorbed:. Report the block you added.
```

## Cross-feature screens

```text
a UC in two features' hubs  → designed once, in primary_feature's UX spec
the participant's worker    → told "UC-### is designed in <slug>'s spec", designs nothing for it
the orchestrator (Stage 5)  → writes the ## UX Spec pointer + uiux: on BOTH hubs
```

A participant hub with no pointer is the failure here: that feature reads as having no design, and
the next run puts it back on the work-list with nothing to do.
