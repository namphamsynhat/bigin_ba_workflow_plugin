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

## Before dispatching — assemble the brief, per feature that needs it

A feature with **3 or more in-scope UCs, or whose in-scope UCs together cite 4 or more distinct
`EN-###` entities** gets its own `ux-brief-assembler` dispatch first (same wave as, or immediately
before, its screens worker) — see `agents/ux-brief-assembler.md`. It combines that feature's UCs,
cited entities, `BR-###` rule mirrors, open hub directives, and active design principles into one
Design Brief: known gaps verbatim, a mechanical draft screen-boundary proposal (Part 2's rule
applied, never finalized), an entity field table per candidate screen, cross-UC merge candidates,
existing-pattern matches from sibling UX specs, and the raw entity-field material Part 4b's trigger
test will need later. **Its brief carries the platform too** — supplied to it in its own dispatch,
exactly as it is to the screens worker, and never inferred by it (`agents/ux-brief-assembler.md`
§ What you're handed). Below that threshold, the screens worker reads `3-screens.md` Part 1 directly
— a second dispatch to save a few inline reads costs more than it returns.

Fold the brief into the screens worker's prompt as its `READ FIRST` starting point (§ The prompt,
below) — the worker still owns confirming or adjusting every proposed screen boundary, still reads
the source UCs/entities directly whenever it needs to verify a specific claim, and still runs Part
4b's actual trigger verdict itself; the brief only removes the need to re-derive the mechanical parts
of Part 1/2 from scratch.

## Before dispatching — the orchestrator does these six things

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
5  NAME THE BOOSTERS     from engine-detection.md § Design quality boosters and § Per-step pattern
                        references: which apply this run, and whether any craft-quality-pass skill
                        (§ Stage 3.5) is installed. "none" is a valid answer for either.
                        A relationship-UX skill is installed → say so, and say that the WORKER runs
                        Part 4b's trigger test per feature. Never pre-decide `modelled` here: the
                        test needs UC step verbs and an entity field list, which Stage 1 never read
                        (agentic-ux.md § Deciding it applies).
6  RESOLVE THE PLATFORM read `platform:` ONCE, from _bigin/system/project.md's frontmatter, at
                        Stage 1 (absent → `web`). Resolve a PER-FEATURE OVERRIDE only from a source
                        that EXPLICITLY STATES a platform for that feature — a hub ## Design
                        Directives row, an active DESIGN-PRINCIPLES row — and pass the resolved
                        value, with its ground, into EVERY worker prompt. A worker never re-derives
                        it: two workers inferring a platform differently produces one product with
                        two navigation shells. (A worker that meets an explicit statement inside a
                        UC it reads still acts on it and cites it, per 3-screens.md Part 1 — an
                        explicit statement is an override; an inference from step wording or from
                        where an actor sits never is.)
                        The platform's REQUIRED ENGINE was resolved with it, at the same Stage 1
                        precondition — a worker cannot check either one: it cannot read this
                        plugin's install directory.
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
PLATFORM:            <web | mobile | both> — source: <project config | override: hub directive
                     #<n> | DESIGN-PRINCIPLES row #<n>, which states it for this feature>.
                     Use it as given; do not re-derive it and do not open the project config.
                     regions vocabulary: <web: header / nav / main / aside / footer
                                        | mobile: header / content / tab-bar / sheet / fab>
                     <on both: "ONE screen inventory — the same user goals, never a web list and a
                     mobile list. Only the LAYOUT splits, inside a screen's own block, and only
                     where the two genuinely differ. regions: BOTH vocabularies, one per layout.">
DESIGN ENGINE:       <wds | figma | <plugin> | built-in> — <one line on how to use it>
DESIGN SYSTEM:       04-UIUX/_design-system/design-tokens.md at v<x> — cite these names; propose
                     a new token only when nothing there fits.
QUALITY BOOSTERS:    <agentic-UX or design-library skill in scope, or "none"> · pattern skills
                     available this session: <list from designer-skills, or "none"> · craft-quality
                     pass: <run it after drafting, per engine-detection.md § Stage 3.5, or
                     "skip — not installed">.
RELATIONSHIP MODEL:  run Part 4b's trigger test on this feature yourself and act on the result —
                     3 of 3 → write ## 7 and set relationship_model: modelled; any miss → DELETE
                     ## 7 from the spec, leave relationship_model: none, and name the failed test.
                     <"a relationship-UX skill IS available — use it for VOCABULARY only: it is an
                     external pattern (ground 2b), so it can shape how a grounded element is built
                     and can NEVER ground that a screen, field, or state exists. Its memory/goal/
                     planning dashboards are whole screens; none of them is a ground." | "no
                     relationship-UX skill is installed — Part 4b alone is complete.">

DESIGN BRIEF:        <a ux-brief-assembler report is attached below — start there, and treat its
                     candidate_screens/merges as a DRAFT to confirm or adjust, never as settled |
                     "none assembled — read Part 1 yourself, this feature was under the dispatch
                     threshold">

READ FIRST:
- _bigin/conventions/design-conventions.md — these sections ONLY: § Paths, § Write map,
  § The eight design hard rules, § The UX spec, § Screen spec, § Grounding, § Open questions,
  § Actor scope, § The relationship model, § The navigation map
- _bigin/stages/design/3-screens.md — your stage guide, in full
- 01-Requirements/_features/<slug>.md — the hub: ## Design Directives (Status: open), actors
- each UC above, in full: § 1 actors/trigger/post-conditions, § 2 steps, § 3 branches,
  § 4 rule mirror, § 5 Still open (KNOWN GAPS — work around them, never guess past them)
- every BR-### named in those § 4 mirrors — noting any rule about WHO MAY SEE OR DO WHAT — and
  every EN-### in the UCs' entities:, noting each RELATIONSHIP CARDINALITY (one Account has many
  Orders): those two are where Part 2a's actor scope is read from, and nowhere else
- 01-Requirements/DESIGN-PRINCIPLES.md — rows with Status: active
- 04-UIUX/_design-system/design-tokens.md and components/ — what already exists
- 04-UIUX/_design-system/navigation-map.md — its ## Structure (a dot-path `id` per row, so it can
  nest arbitrarily deep — "settings", "settings.team", "settings.team.members"), so a new entry
  joins an existing branch instead of starting a parallel one
- every other 04-UIUX/UX-*.md — how a sibling feature already solved a list, a queue, an
  approval, a form. Reusing an existing pattern beats inventing a parallel one.

A DESIGN BRIEF attached above is a pre-digested starting point, not a substitute for the source —
re-read the actual UC/BR/EN whenever you need to confirm a specific detail it summarized, and never
treat its candidate screens or merges as final until you've applied Part 2's rule yourself.

FIRST, across all the UCs at once, fill § 1's ACTOR & SCOPE table (3-screens.md Part 2a): one row
per actor the UCs name in their § 1, and for each — whose records they see (own | assigned | their
unit's | all), how many (one | few | many, unbounded), and what they may do (read one | act on one |
act on MANY at once). Every cell is READ from a BR-###, a UC step, a § 1 pre-condition, or an EN-###
cardinality, and carries that ground. Nothing settles a cell → the NARROWEST reading plus a § 6
question; never the convenient one. Do this BEFORE mapping screens: it is the input to the merge
rule below, not a summary written afterwards.

THEN, one UC at a time, in the order listed:
1. Map its flow to screens (3-screens.md Part 2): consecutive steps by the same actor in the same
   place = ONE screen; a validation = a state; an exception flow = a named error state; a
   system-only step = not a screen. Merge screens two UCs both land on ONLY WHEN THEIR ACTORS'
   SCOPE AGREES (Part 2a): a differing volume band or a differing capability means TWO screens,
   each naming its own actor — a member reading their own record and an administrator working ten
   thousand of them are two products, not one screen with a filter bar. Differing only in WHICH
   FIELDS are visible → still ONE screen, with a `Visible to` cell citing the BR-### that restricts
   it.
2. Decide which of those screens gets a nav entry (Part 2b): only one the actor opens DIRECTLY from
   a menu — never a detail, a wizard step, or a modal reached through another screen. Most features
   contribute 0-2 entries, not one per screen. On MOBILE the shell is a TAB BAR of at most 5
   top-level entries: a 6th top-level candidate is an Open Question on the nav map (owner: team),
   never a silent 6th row. On BOTH, say where the feature lives on EACH shell — one line per shell,
   because the two shells are two trees; an entry on one and not the other is normal and grounded,
   never mirrored for symmetry.
3. Write the screen spec (Part 3), starting with its `Actor` and `Scope` lines from the table
   above: regions in YOUR PLATFORM'S vocabulary (web: header/nav/main/
   aside/footer · mobile: header/content/tab-bar/sheet/fab — a `nav` region on a phone screen or a
   `tab-bar` on a web one asks the tool to build a shell the platform does not have), elements, real
   copy, TOKEN NAMES, the entity field each input renders, and what grounds each element. On BOTH,
   write purpose/serves/elements/states/interactions ONCE as shared behaviour, then split only what
   actually differs into `Layout — Web` / `Layout — Mobile`; no real difference → one regions line
   in each vocabulary, no split.
4. Add the states (Part 4) — each traced to a BR, an exception flow, an entity constraint, or a
   post-condition. A screen at volume `many` ALSO carries the five volume states — empty, few, many
   AT REAL SCALE (name the real number: "≈10,000 records, page 1 of 200", never "several"),
   loading, error — plus at least one find mechanism (search, filter, or sort). All of that is
   grounded by the volume fact itself, cited like any other ground. A screen at volume `one` carries
   no find machinery: there is nothing to find.
5. Run Part 4b's trigger test (once per feature, after every UC is mapped). On a pass, write ## 7:
   Relationship Context, Memory Architecture (EVERY row names a real EN-### field — no field means
   a requirement gap, not a row), Trust Map (fill a stage 3 ONLY where a BR-### grants it — D7),
   and at most three Proposed Measures. Expect more requirement gaps than rows; each goes on § 6
   marked as a requirement gap. On a miss, delete ## 7 entirely.
6. If QUALITY BOOSTERS names a craft-quality-pass skill, run it now, on your own just-drafted
   screens only (engine-detection.md § Stage 3.5): apply a pure craft fix directly; a finding that
   would change what a screen shows or how a control behaves goes back through the grounding test —
   grounded → apply it and cite the ground, ungrounded → an Open Question, same as any other. Not
   named → skip, silently.
7. NEVER invent a screen, a field, a state, a nav entry, a threshold, or a label the sources did not
   state — and never a memory, an autonomous action, or a retention rule (D7). NEVER add a bulk
   edit, a bulk delete, a "select all matching", an export, a saved view, or a subscription that no
   UC step and no BR-### grants: volume licenses FINDING, never a CAPABILITY (D8), and an
   administrator who "obviously needs bulk delete" is a requirement gap on § 6, owner client — not
   a control you put on the screen. Missing detail is a question on § 6, not a plausible guess.

DO NOT WRITE — vault-wide or owned elsewhere, and other features run concurrently. Report
candidates instead; the orchestrator applies them:
  04-UIUX/_design-system/ (tokens AND components AND navigation-map.md) · another feature's UX spec
  or hub · 01-Requirements/DESIGN-PRINCIPLES.md · FEATURES.md
DO NOT edit any UC, BR, or entity — they are read-only here, in every section.
DO NOT fill absorbed:, do not set status: accepted, do not write any Prototype Prompt block —
the orchestrator does all three after your report.
DO set the spec's `actors:` frontmatter key from § 1's Actor & Scope table — one entry per row,
"<role>:<own|assigned|unit|all>:<one|few|many>" (e.g. ["Member:own:one", "Administrator:all:many"]).
Same rows, same order, never a role the table does not carry. Stage 5 check 15 blocks on the two
agreeing, and a spec with no `actors:` key reads as one written before actor scope existed.
Leave the spec at status: draft.

REPORT, as plain lines:
  feature:              <slug>
  platform:             web|mobile|both — source: dispatched (project config)
                        | override: <UC-### S<n> | hub directive #<n> | DESIGN-PRINCIPLES row #<n>>
  ux:                   UX-### created|updated — <N> screens (<N> new, <N> updated)
  screens:              <screen> | actor: <role> | volume: one|few|many <(real number, when many)>
                        | serves: UC-### S<n>, S<n> | states: <N> (one line each)
  actor_scope:          <actor> | sees: own|assigned|unit|all | volume: one|few|many
                        | may: read one|act on one|act on many
                        | grounded by: <BR-### | UC-### S<n> | EN-### cardinality>
                        (one line per actor in § 1's table)
  actor_splits:         <place> → <screen A> (<actor>, <band>) + <screen B> (<actor>, <band>)
                        | split on: volume|capability   (one line each, or "none")
  capability_gaps:      <the bulk/export/saved-view affordance NOT designed> | suggested by: <what
                        made it tempting> | requirement gap raised (one line each, or "none")
  tokens_used:          <existing token name> (one line each)
  token_candidates:     <proposed name> | level: 2|3 | value: <raw> | means: <meaning> | on: <screen>
  component_candidates: <name> | variants: <…> | states: <…> | used on: <screen>, <screen>
  nav_candidates:       <entry label> | shell: web|mobile (one line per shell on both — the two
                        shells are two trees) | parent: <existing id it nests under, or
                        "new: <path>", or "top-level"> | points to: <screen> | role(s): <actor(s)>
                        | grounded by: <UC-### S<n> | BR-### | pattern <name>>
                        | tab-bar cap: <"6th top-level candidate — Open Question, owner team",
                        when a mobile shell hits it>
  directives_reflected: hub row #<n> → <screen> (only rows a screen really implements)
  relationship:         modelled | none — <the failed test, when none: judges|persists|repeats>
  relationship_rows:    context <N> | memory <N> | trust <N> | measures <N> | gaps <N>
                        (omit entirely when relationship: none)
  boosters_used:        <pattern skill or craft-quality pass> | on: <screen> | why (one line each,
                        or "none")
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
5a actor scope claims     → the frontmatter `actors:` list and ## 1's Actor & Scope table hold the
                            same roles in the same bands; every actor named there really appears in
                            an in-scope UC's ## 1 (an invented actor is an invented persona, and
                            every screen built for them is invented scope); and every ## 2 row and
                            ## 3 block carries an Actor and a Volume from that table
5b the split held         → no ## 2 row serves two UCs whose actors differ in VOLUME BAND or in
                            CAPABILITY. Reported `actor_splits: none` on a feature whose Actor &
                            Scope table holds two bands is the claim to check hardest — it is the
                            one-screen-fits-all failure, and it reads as a clean report
5c many-screen machinery  → every screen at volume `many` has at least one find mechanism and all
                            five volume states, with the `many` one naming a REAL NUMBER, not
                            "several"; and no screen at volume `one` carries find machinery
5d ungranted capability   → Grep the spec for bulk, select all, export, saved view, subscribe. Any
                            hit must cite a UC step or a BR-### that really grants it; otherwise it
                            is D8 broken and belongs in ## 6 as a requirement gap, not on a screen
6  every reported nav candidate → NOT a screen reached only through another screen (re-check
                            against Part 2b's test); a violation is dropped, not applied
7  shared files untouched → git diff --stat shows NO change to 04-UIUX/_design-system/ (tokens,
                            components, AND navigation-map.md), DESIGN-PRINCIPLES.md, FEATURES.md,
                            or any file under 01-Requirements/ (the design system and nav map move
                            in Stage 4, in the orchestrator, not here)
8  absorbed: still empty  → Stage 5 stamps it, after check 1 has passed
9  relationship claim    → reported `modelled`: ## 7 exists AND carries rows, every Memory row names
                            a field that really exists in that EN-###, and no stage-3 cell is filled
                            without a real BR-### (D7). Reported `none`: ## 7 is GONE from the file,
                            not left empty. Either mismatch is blocking — Stage 5's checks 10-12
                            re-run this, and a claim that survives to there is one the orchestrator
                            has to unpick from the file rather than the report.
10 regions vocabulary    → every ## 3 block's regions line uses the vocabulary of the platform this
                            worker was DISPATCHED with — web: header/nav/main/aside/footer, mobile:
                            header/content/tab-bar/sheet/fab. A `nav` on a phone screen or a
                            `tab-bar` on a web one is the wrong shell, and the prompt built from it
                            asks a tool to build chrome the platform does not have. Grep for the
                            other platform's region names
11 one inventory on both → a `both` spec has ONE ## 2 Screen Inventory, not a web table and a mobile
                            table, and its per-platform difference lives as a `Layout — Web` /
                            `Layout — Mobile` split INSIDE a ## 3 block. Two inventories is
                            blocking: the second goes stale the first time a UC changes

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
