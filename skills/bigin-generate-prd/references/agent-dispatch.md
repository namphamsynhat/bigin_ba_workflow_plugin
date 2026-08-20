# Worker dispatch — one per feature

```text
Agent(session default model, general-purpose, foreground)   # not haiku — this is judgment work
one per FEATURE SLUG
    → a feature's PRD is one ownership domain
    → features are independent, so they parallelize safely
≤ 4 features concurrently, verify between waves        # a failure costs one wave, not the backlog
within a feature → every folded UC written sequentially, into ONE PRD
```

**Skip the worker entirely for one or two features** — dispatch costs more than the work, and the
orchestrator can follow `2-business.md` → `3-flows.md` → `4-design.md` inline.

**Stage 5 never runs in a worker.** Hubs are shared state and `absorbed:` must be stamped against the
final file; the orchestrator closes every feature sequentially after the last wave.

## Before dispatching — the orchestrator does these five things

```text
1  MINT THE NUMBER      Grep {prd_dir} for the highest PRD-### and assign the next one per feature
                        that needs a new file. Two workers grabbing the same number is why.
                        Use the Grep TOOL, never a shell pipeline — a denied pipeline reads as
                        "no existing ids" and silently reuses one.
2  RUN THE CHAIN GATE   1-scope.md Part 2. A `built` feature is skipped, not dispatched.
3  CLASSIFY THE UCs     per feature: FOLD (with versions), CURRENT, PENDING (with status), and
                        which are owned by another feature. The worker does not re-derive this —
                        it would re-read every hub to do so.
4  NAME THE ENGINE      the detected PRD engine and one line on how to use it. When it is BMAD,
                        say which step-file directory to read the checklist from.
5  NAME THE DESIGN      the feature's UX-###@version, or "no design yet" — so a worker never goes
                        looking and never invents § 9.
```

## The prompt

The worker has no memory of this conversation. Give it the cheap known facts and point it at real
files — a paraphrase risks it trusting a stale summary over the source.

```text
Write the PRD for feature <slug>.

The output is a PRD: one per feature, 12 sections, BUSINESS FLOW not technical specification. It
consolidates the feature's APPROVED use cases (UC-###: one user goal, a numbered main flow S1,
S2 …, branch flows A1/E1 …), the business rules that govern them (BR-###), the information they
touch (EN-###), the pain points they resolve (PP-###), and the screens already designed for them
(UX-###) into the document a business sponsor signs.

YOUR PRD:            <PRD-### (new — create it from _bigin/templates/prd.md) |
                      PRD-### (exists — UPDATE IN PLACE, bump version, never regenerate)>
UCs TO FOLD:         <UC-###@1.2 (new) | UC-###@1.4 (was folded at 1.2 — it drifted)> …
UCs PENDING:         <UC-### (draft) | UC-### (needs-clarification, 2 open)> … , or "none"
                      → § 10 Pending Scope ONLY. Never a capability, a flow, or a screen.
UCs NOT YOURS:       <UC-### (carried in <slug>'s PRD)> …, or "none"
CHAIN:               <full | cr — and if cr, that a human asked for this PRD explicitly>
DESIGN:              <UX-###@<version> — fold its screens into § 9 | "no design yet — § 9 is one
                      line saying so, and § 6's Screen column is all '—'">
PRD ENGINE:          <bmad | <plugin> | built-in> — <one line on how to use it>

READ FIRST:
- _bigin/conventions/conventions.md — these sections ONLY: § Feature material, § Traceability
  chain, § Absorbed, § Status vocabularies, § Open Questions wording, § Pain Point Register
- _bigin/stages/prd/2-business.md, 3-flows.md, 4-design.md — your stage guides, in full
- _bigin/templates/prd.md — the schema. Instantiate it; never compose the sections from memory
- 01-Requirements/_features/<slug>.md — the hub: ## Pain Points, ## Notes / History (current
  state as stated), ## Use Cases
- each UC TO FOLD, in FULL: § 1 (actors, business need, trigger, pre/post-conditions incl. the
  FAILURE post-condition), § 2 steps, § 3 branches, § 4 rule mirror (for Enforced at only),
  § 5 Still open + decision log, § 6 Special Requirements
- every BR-### in those UCs' brs: — the BR FILE is the rule; the UC's § 4 only says where it bites
- every EN-### in those UCs' entities:
- 01-Requirements/PAIN-POINTS.md — this feature's rows
- 04-UIUX/UX-<NNN> …, if one exists: § 1 brief, § 2 inventory, § 4 flows, § 6 open questions
- _bigin/system/project.md — the engagement: product, client, new vs ongoing
<when the engine is BMAD:>
- <path>/steps-c/*.md — one at a time, as a CHECKLIST ONLY. Answer every step from the artifacts
  above, never from your own product judgment; auto-continue past every A/P/C menu; write nothing
  into frontmatter that _bigin/templates/prd.md does not define.

THE SIX HARD RULES:
P1  Business language only. No API, schema, field type, endpoint, framework, table, token name,
    hex, or px. Test: a sentence a developer needs but a business owner cannot confirm is wrong.
P2  Approved UCs only in §§ 5-9. Pending UCs go to § 10 and nowhere else.
P3  Never invent. No line without a source. Nothing to trace → "not stated", or § 11.
P4  READ-ONLY on every UC, BR, entity, and UX spec. You edit ONE file: your PRD.
P5  status: draft, always. Never approved.
P6  § 9 quotes the design. Never invent a screen, a state, or a visual decision.

YOU MAY WRITE EXACTLY ONE FILE: 02-PRD/PRD-<NNN> <Feature>.md, §§ 1-12 + § Traceability +
§ Changelog. Do NOT write: any hub, any other feature's PRD, any UC/BR/entity/UX file,
FEATURES.md, PAIN-POINTS.md, ENTITIES.md, absorbed:/design_absorbed: (the orchestrator stamps
those in Stage 5). Report candidates instead.
```

## The report contract

A worker returns this and nothing else. The orchestrator needs each line for Stage 5 — a prose
summary forces it to re-read the file it just paid a worker to write.

```text
FEATURE:            <slug>
PRD:                PRD-### — created | updated <old> → <new>
CAPABILITIES:       C1 <name> (UC-###) · C2 … — one line per § 5 row
FLOWS:              <n> written · <n> with branch tables · <n> with no § 3
RULES:              BR-### … , or none
INFORMATION:        EN-### … , or none  (+ any still `proposed`, not promoted)
SCREENS FOLDED:     UX-###@<version>, <n> screens, <n> § 6 steps mapped, <n> unmapped ('—')
                    | no design
PENDING SCOPE:      UC-### (<status>, waiting on <what>) … , or none
OPEN DECISIONS:     <n> total — <n> from UC § 5 · <n> design requirement gaps · <n> found this run
FINDINGS:           one line each, or "none":
                      · BR-### has no enforcement point in any folded flow
                      · BR-### contradicts BR-###
                      · PP-### no folded capability addresses
                      · design stale — UX Serves cites S# no folded UC has
                      · approved UC with live open questions (hard rule 7 reopened it)
                      · a BMAD step skipped because the vault could not answer it
NOT STATED:         which § 3 measures, § 12 subsections, or § 2 lines came back unstated
```

`FINDINGS` and `NOT STATED` are the two lines most worth having. Both are what a human scans to
decide whether the PRD is ready to take to a sponsor, and neither is recoverable from the document
alone — a `not stated` line in § 3 looks identical whether the run checked carefully or gave up.

## Wave verification — between waves, in the orchestrator

```text
1  each reported PRD file exists at 02-PRD/PRD-### <Feature>.md, with the id it was given
2  no two files carry the same feature: slug
3  every id in a report's CAPABILITIES is approved on disk   (P2, re-checked — not trusted)
4  no PENDING id appears in that file's §§ 5-9
5  status: draft in every file                                (P5)
6  no worker touched a hub, another PRD, or any requirement/design file
```

A failure blocks the next wave. Repair it in the orchestrator or re-dispatch that one feature; never
carry a failed feature into Stage 5, where `absorbed:` would stamp it as covered.
