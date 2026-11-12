# Worker dispatch — one per feature, always

```text
Agent(model: "sonnet", general-purpose, foreground)   # not haiku — judgement work; pinned so a session on another model does not change the output
one per FEATURE SLUG, for EVERY in-scope feature — including a run of one
    → a feature's UX spec + hub are one ownership domain; features parallelize safely
≤ 4 features concurrently, check each wave before the next     # a failure costs one wave
within a feature → UCs designed sequentially, into ONE UX spec
```

**There is no inline path.** A single feature still gets a worker, for two reasons. The screens guide
is the largest file in this stage and belongs in a context that is thrown away afterwards. And Stages
4 and 5 are only a review if the context running them did not write the screens: an orchestrator that
designs, reviews, verifies and closes has graded its own work four times.

A feature `bigin design scope` marks `resume: review` already has its screens on disk — **skip its
dispatch** and take it straight to the wave check below.

## Before dispatching — the orchestrator does these seven things

```text
1  MINT THE NUMBERS     `bigin mint ux --count <N>` — ONE call, N = `new UX ids needed` from
                        `bigin design scope`; assign the ids it prints in order. The engine holds the
                        id lock and remembers what it handed out. Never grep the folder for the
                        highest id: a failed or denied search reads as "no ids yet".
2  BUILD THE WORKLISTS  `bigin worklist design <slug> --out _runs/<run>/tasks/<slug>.design.in.json`
                        per feature. It carries every in-scope UC (§ 1, steps, branches, rule mirror,
                        known gaps), the rules and entities they cite, the hub's open pain points and
                        directives, the active principles, the nav tree and every sibling spec's
                        screen list. It replaces the brief a separate agent used to assemble.
3  SEED THE NAV SHELL   2-navigation.md Part A, so a worker joins the tree that already exists.
4  RESOLVE THE PLATFORM the project value comes from `bigin design scope`. A PER-FEATURE OVERRIDE
                        exists only where a hub ## Design Directives row or an active
                        DESIGN-PRINCIPLES row EXPLICITLY STATES one — both are in the worklist. Pass
                        the resolved value and its ground to the worker; it never re-derives it.
5  NAME THE METHOD      the detected METHOD layer and one line on how to use it. There is no render
                        engine in a design run — do not name one.
6  NAME THE PATTERN     from method-layer.md § Per-step pattern references: which apply this run.
   SKILLS               "none" is a valid answer. Never a flow-review skill — Stage 4 is the
                        orchestrator's. A relationship-UX skill is installed → say so; the WORKER
                        runs the trigger test (agentic-ux.md § Deciding it applies).
7  RESOLVE OWNERSHIP    a cross-feature UC is designed ONLY in its primary_feature's spec. The
                        worklist's `other_use_cases` already says which are NOT YOURS.
```

## The prompt

The worker has no memory of this conversation. Give it the facts only the orchestrator has, and point
it at files for everything else — a rule paraphrased here is a second copy that drifts from its home.

```text
Design the screens for feature <slug>.

YOUR UX SPEC:    <UX-### (new — create it from _bigin/templates/ux-spec.md)
                 | 04-UIUX/UX-### <Feature>.md (exists — update it in place)>
PLATFORM:        <web | mobile | both> — source: <project config | override: hub directive #<n> |
                 DESIGN-PRINCIPLES row #<n>, which states it for this feature>. Use it as given.
DESIGN METHOD:   <wds | figma | <plugin> | built-in> — <one line on how to use it>. Not a renderer:
                 nothing in this run renders.
PATTERN SKILLS:  <list, or "none"> · relationship-UX skill: <available — vocabulary only, it can
                 never ground that a screen, field or state exists | not installed>

READ, in this order, and nothing else up front:
1. <abs path>/cards/design-screens.md      — YOUR CARD: the rules you can break, one worked example
2. <abs path>/<slug>.design.in.json        — YOUR WORKLIST: the whole requirement input. Every
   use case to design is under `use_cases` (state NEW or CHANGED); `other_use_cases` are not yours.
   Every open pain point under `pain_points` gets a flow whose `Resolves` names it, or a § 6
   question saying why none does.
3. _bigin/stages/design/3-screens.md       — the procedure. Parts 1–7, in order.
   Updating a spec that predates this version → also 3-screens-adopt.md.
   Your Part 4b trigger test passes 3 of 3 → also 3-screens-relationship.md, then write ## 7.
Open a UC, BR or EN file only to confirm ONE detail the worklist summarised. Open ONE sibling spec
only to reuse a pattern its `sibling_screens` entry names. Open a `_bigin/conventions/` section only
when the card or the procedure cites it.

WRITE exactly one file: your UX spec. Leave it at status: draft, absorbed: untouched, § 5's
### Flow Review table EMPTY (Stage 4 writes it — do not grade your own journeys), and set `actors:`
from § 1's Actor & Scope table, one "<role>:<own|assigned|unit|all>:<one|few|many>" per row.
DO NOT WRITE the navigation map, another feature's spec or hub, DESIGN-PRINCIPLES.md,
PAIN-POINTS.md, FEATURES.md, or any UC, BR, entity or pain-point row. Report candidates instead.

REPORT only what is NOT in your spec — the orchestrator reads the spec itself, by script:
  feature:              <slug> — UX-### created|updated
  platform_override:    none | <hub directive #<n> | DESIGN-PRINCIPLES row #<n> | UC-### S<n>>
  nav_candidates:       <entry label> | shell: web|mobile | parent: <existing id | "new: <path>" |
                        "top-level"> | points to: <screen> (Landing)[, <screen> (Drill-down)]*
                        | role(s): <actor(s)> | grounded by: <UC-### S<n> | BR-### | pattern>
                        (one line per shell on `both`; a 6th top-level mobile entry is an Open
                        Question, owner team — say so instead of proposing it)
  capability_gaps:      <the bulk/export/saved-view affordance NOT designed> — question raised
  directives_reflected: hub row #<n> → <screen>   (only rows a screen really implements)
  relationship:         modelled | none — failed <judges|persists|repeats>
  pattern_skills_used:  <skill> | on: <screen or flow> | why        (or "none")
  blocked:              UC-### — <why, one line>                    (or "none")
```

## Checking the wave

After each wave, before the next. This catches the failure that matters: a worker reporting screens
it never wrote, which Stage 6 would then stamp into `absorbed:`.

```text
per feature in the wave:
  bigin design check <slug> --phase wave
      BLOCK    → a real mismatch. One scoped repair worker (below), re-run the check, move on.
      confirm  → open ONLY the block it names and decide; most are fine and say why.
  then, from the worker's REPORT (the script cannot see these):
      every nav candidate is a screen the actor opens DIRECTLY from a menu — never one reached only
        through another screen (3-screens.md Part 2b). A violation is dropped, not applied.
      `git diff --stat` shows NO change to the nav map, DESIGN-PRINCIPLES.md, PAIN-POINTS.md,
        FEATURES.md or anything under 01-Requirements/.
  bigin run record <run> --task screens:<slug> --status ok        # what a resumed run reads
```

What the script checks, so nobody re-does it by eye: every inventory row has a spec block and the
reverse; every served step exists in its use case and is not removed; every Role is on the closed
list, one primary action per screen; no hex, px, font name or `--token`; regions in the dispatched
platform's vocabulary; `actors:` equals the Actor & Scope table; every screen has an Actor and a
Volume; a `many` screen has a find mechanism; View IDs are present and unique across every spec;
Screen Types are one of the four and agree with the nav map; no `## Prototype Prompt`; the
relationship flag matches `## 7` on disk.

```text
Repair 04-UIUX/UX-<NNN> <Feature>.md.

`bigin design check` reports: <the BLOCK line(s), verbatim>.
Read _bigin/cards/design-screens.md, the part of _bigin/stages/design/3-screens.md the finding is
about, and <slug>.design.in.json. Fix ONLY what the finding names. Do not add a screen, do not touch
any other block, do not write the navigation map, do not edit a UC, do not fill absorbed:.
Report what you changed.
```

## Cross-feature screens

```text
a UC in two features' hubs  → designed once, in primary_feature's UX spec
the participant's worker    → sees it under `other_use_cases` as NOT YOURS, designs nothing for it
`bigin design close`        → writes the ## UX Spec pointer + uiux: on EVERY hub in the spec's features:
```
