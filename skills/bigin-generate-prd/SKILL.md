---
name: bigin-generate-prd
description: This skill should be used when the user asks to "generate the PRD", "write the PRD", "create a product requirements document", "run the PRD stage", "feed the use cases into the PRD", "PRD for this feature", "which features are ready for a PRD", "refresh the PRD", or after /approve-uc has approved one or more use cases on a feature. Consolidates every approved UC-### of a feature — plus its business rules, entities, pain points, and the UX-### design already generated for it — into one business-flow PRD per feature, headlessly, by driving the BMAD create-PRD workflow in headless mode when BMAD is installed.
argument-hint: "[feature slug | UC-### | omit for every feature with approved UCs and no current PRD]"
disable-model-invocation: true
---

# Bigin Generate PRD

The **load** step of the extract → transform → load pipeline, on the document side. It takes a
feature's approved use cases and consolidates them into the document a sponsor signs:

```text
in    every UC-### on the feature at status: approved   (new, or changed since last folded)
    + its BR-### rules  + EN-### entities  + PP-### pain points
    + the UX-### design already generated for it        (screens, journeys, prototype pointer)
    + {project_file} for the engagement's own framing

out   02-PRD/PRD-<NNN> <Feature>.md — one per feature, 12 sections, business-flow-first
    + absorbed: UC-###@version        the staleness record that makes drift detectable
    + hub ## PRD + prd:               so the feature hub points at it
```

**Business flow, not technical specification.** The document states what the business needs to
happen, for whom, in what order, under which policies, and what the screens already look like. No
API, no schema, no field type, no framework, no architecture. That is the single rule everything
else in this skill serves.

**It is fully headless.** No checkpoints, no confirmation prompts, safe to call from `/bigin-run` or
an unattended batch. Unresolved decisions are carried into `§ 11 Open Business Decisions` rather than
asked — the review happens on the document afterwards.

**It never edits a requirement or a design.** UCs, BRs, entities, and UX specs are read-only (P4).
Nothing here approves anything (P5).

## The six PRD hard rules

```text
P1  Business language only. No API, schema, field type, endpoint, framework, table, token name,
    hex, or px. The test: a sentence a developer needs to implement but a business owner cannot
    confirm or deny is in the wrong document.
P2  Approved UCs only in the body. A non-approved UC is listed in § 10 Pending Scope, never
    folded into §§ 5-9 (`feature-hub.md` § Feature material).
P3  Never invent. Every line traces to a UC, a BR, an entity, a pain point, a screen, or a stated
    source. Nothing to trace → "not stated", or an Open Business Decision.
P4  Requirement and design content are READ-ONLY. This skill edits no UC, BR, entity, or UX spec.
P5  Never write status: approved. A human approves a PRD, the same way a human approves a UC.
P6  Design is QUOTED, not decided. § 9 reports the screens that exist; it never invents one, and
    never makes a visual decision.
```

Ids **are** required here — in §§ 5-7 and § Traceability — because this is an internal document and
traceability is the point. That is the opposite of a RENDER PROMPT, which `/bigin-render-design-od`
builds at render time and which may carry no ids at all: it runs in a process that has never seen
this vault. Do not carry that rule across.

## Operating modes

| Mode | Behaviour |
|---|---|
| **Create** | No PRD for this feature. Instantiate `{template_prd}`, mint the id, fold every approved UC. |
| **Refresh** (normal) | A PRD exists. Update it **in place** — same id, bump the version, re-stamp `absorbed:` whole. Never regenerate: § 11 answers and human edits to § 1 are content a regeneration destroys. |
| **Part-approved** | Some UCs approved, some not. The approved ones become the body; the rest go to § 10 Pending Scope with what each waits on. A real and useful state, not a defect. |

## Paths

| Variable | Path | Notes |
| :--- | :--- | :--- |
| `{prd_dir}` | `02-PRD/` | one per feature: `PRD-<NNN> <Feature>.md` |
| `{prd_stages_dir}` | `_bigin/stages/prd/` | `1-scope`, `2-business`, `3-flows`, `4-design`, `5-close` |
| `{template_prd}` | `_bigin/templates/prd.md` | the 12-section format — **the schema**, never composed from memory |
| `{uc_dir}` · `{br_dir}` · `{entity_dir}` | `01-Requirements/_ucs/` · `_brs/` · `_entities/` | **read-only** input |
| `{ux_dir}` | `04-UIUX/UX-<NNN> <Feature>.md` | **read-only** — § 9's only source |
| `{hub_dir}` | `01-Requirements/_features/<slug>.md` | `## PRD` + `prd:` out; `## Pain Points`, `## Notes / History` in |
| `{requirements_file}` | `01-Requirements/FEATURES.md` | the slug registry, and the chain gate |
| `{pain_points_file}` · `{entities_file}` | `01-Requirements/PAIN-POINTS.md` · `ENTITIES.md` | **read-only** registers |
| `{conventions_reference}` | `_bigin/conventions/` | read `feature-hub.md` § Feature material · `use-case.md` § Traceability chain · `runtime.md` § Absorbed · `core.md` § Status vocabularies · `questions.md` § Open Questions wording · `registers.md` § Pain Point Register |

`design-core.md` § Paths is the full table and the one a subagent reads — a `SKILL.md` lives
in the plugin install directory, which a subagent cannot reach.

Missing `_bigin/conventions/`, `_bigin/stages/prd/`, or `_bigin/templates/` → stop and say
`/bigin-new-project` must run first. Then run `version-check.md` § Workspace version check —
one `Grep` of `_bigin/system/project.md` against the installed plugin's version, compared as semver.
Behind → warn and recommend `/bigin-upgrade-project`; **ahead → stop**.

## PRD engine — drive BMAD headlessly when it is installed

```text
check, in order, and use the first that answers:
  1  BMAD create-PRD    a bmad-create-prd skill is available, or _bmad/ exists in the repo
  2  any PRD/PM plugin  a product-requirements skill in this session's skill list
  3  built-in           always available — the method in the stage guides themselves

none of 1-2 → run the built-in method and REPORT the install command in the closeout.
              Never halt to ask: this skill is headless, and the built-in method is complete.
```

BMAD's `bmad-create-prd` is a 13-step facilitated workflow that halts at an A/P/C menu on every step
and writes one product-level `prd.md`. **Headless mode means using its step files as the elicitation
checklist while answering each step from the vault instead of from a human**, auto-continuing, and
writing `{template_prd}`'s per-feature format rather than BMAD's own template.

The full contract — the step→vault-source map, what to auto-answer, what BMAD output to discard, and
the two rules that keep the substitution honest — is in **`references/bmad-headless.md`**. Read it at
Stage 1 when engine 1 or 2 is detected. Stamp `engine:` with what actually ran.

## Execution order

```text
scope = $ARGUMENTS slug or UC-###, else every {hub_dir} feature with approved UCs

1  scope      chain gate, then which approved UCs FOLD / are CURRENT / are PENDING  [1-scope.md]
2  business   §§ 1-4  summary, context, goals, actors                               [2-business.md]
3  flows      §§ 5-8  capabilities, business flows, rules, information              [3-flows.md]
4  design     §§ 9-12 screens, scope, open decisions, assumptions                   [4-design.md]
5  close      stamp absorbed, status, hubs, 8 verification checks, report            [5-close.md]
```

Run all five, in order, every invocation. **Load a stage file on reaching that stage**, not up front.

## Stage 1 — Scope

Two gates decide whether a feature gets a PRD at all:

```text
FEATURES.md Status = built        → the lightweight CR chain, which SKIPS the PRD. Skip and say so
                                    (`use-case.md` § Traceability chain). Named explicitly in
                                    $ARGUMENTS is the one exception — write it, stamp chain: cr
FEATURES.md Status = out-of-scope → skip, always, with no exception
zero approved UCs                → "nothing approved yet → /approve-uc". Do NOT write a PRD whose
                                    only content is a Pending Scope table
```

Then the four-way read per UC, from the UC's **own frontmatter** — never the hub's `## Use Cases`
table or `## Requirement Readiness` snapshot, both of which are refreshed indexes that go stale:

```text
removed                                   → DROPPED
not approved                              → PENDING   § 10 only  (P2)
approved, not in absorbed:                 → FOLD
approved, in absorbed: at an older version → FOLD      it drifted
approved, in absorbed: at same version     → CURRENT   report it, don't re-fold
```

## Stage 2 — Business framing

§§ 1-4 from every folded UC's `## 1 Context & Metadata`, the pain-point register, and
`{project_file}`. The rule that governs the whole stage is P3: a goal with no stated measure becomes
`not stated — decision needed` and an entry in § 11, never a plausible number.

## Stage 3 — Capabilities and flows

The stage the document exists for. One § 5 capability row per folded UC (the capability contract —
absent here means it will not be designed, decomposed, or built), then one § 6 flow block per UC:
the UC's `## 2` steps retold in one business voice, its `## 3` branches as "when it goes
differently", the four framing lines from § 1 including the failure post-condition a sponsor always
has an opinion about.

Translation, not reformatting: the actor/system column split collapses into a sentence the business
speaks, while the validation, the record, and the notification all survive. Dropping one of those
three is how a flow silently loses scope.

§ 7 mirrors the `BR-###` files (the BR is the source, the UC's `## 4` supplies only *where* the rule
bites). § 8 says what information the business keeps and why — never a data model.

## Stage 4 — Design, scope, open decisions

§ 9 quotes `{ux_dir}`: screens, journeys, the design intent in the client's words, a pointer to the
prototype prompts, and the design's own open questions as business-worded gaps. No design → one line
saying so, which is not a blocker. Then § 6's `Screen` column is backfilled from the UX spec's
`Serves` column, which cites `S#` ids directly — a lookup, never a guess.

§ 10 lists pending scope; § 11 pools every open decision from the UCs, the design's requirement
gaps, and whatever this run could not answer — keeping each question's **original sentence** so one
question never becomes two. § 12 takes only stated assumptions, dependencies, and constraints,
including the `## 6 Special Requirements` most upstream stages skip.

## Stage 5 — Close

Traceability table, then `absorbed:` re-stamped **whole** with `UC-###@version` for only the UCs that
really got a capability row. Status is always `draft` (P5), set from a live count of § 11 on disk.
Refresh each participating hub's `## PRD` and `prd:` — and nothing else on it. Then eight
verification checks; a mismatch is blocking.

```text
engine · per feature: PRD-### (new|updated) · capabilities · flows · rules · entities
screens folded · pending scope · CURRENT skipped · features skipped (chain: cr | nothing approved)
open decisions · verification 8/8 or failures · next
```

## Fan-out

One worker per feature past **three features** in a run — a feature's PRD is one ownership domain and
features are independent. One or two features run inline; dispatch costs more than the work. Stage 5
always runs in the orchestrator, sequentially: hubs are shared state. A worker never writes another
feature's PRD, any hub, or any requirement or design file. Prompt and report contract:
**`references/agent-dispatch.md`**.

Workers run on the **session default model**. Translating a flow into business language without
losing a validation, and deciding whether a rule has an enforcement point, is judgment work.

## Failure modes

Each produces a run that looks clean. Ordered by cost to discover later.

- **Folding a non-approved UC into the body.** The document reads as signed-off scope, and the
  approval gate it bypassed was the only thing standing between a draft and a client commitment.
- **Stamping `absorbed:` for a UC that got no capability row.** The feature reads as documented
  forever and no future run picks it up.
- **Appending to `absorbed:` instead of re-stamping it whole.** A stale `id@version` survives the
  run that should have cleared it, and the drift becomes undetectable.
- **Regenerating an existing PRD instead of updating it.** Answered decisions and a human's edits to
  § 1 vanish, with nothing recording that they existed.
- **A technical sentence in § 6.** An untranslated System Response cell turns the sponsor's document
  into one they cannot review, and the review quietly stops happening.
- **Inventing a metric, a driver, or a non-goal.** It is quoted back as a commitment, and it is
  indistinguishable from a real one once written.
- **Inventing phasing.** An MVP boundary nobody agreed to becomes a boundary the client is told they
  agreed to.
- **Describing a screen the design does not have.** It reaches a client looking exactly like a
  specified one.
- **Rewording a UC's open question in § 11.** One decision becomes two, answered inconsistently.
- **Writing a PRD for a `built` feature without saying so.** It reads as the CR chain having changed.
- **Setting status from intent.** Count § 11's unchecked lines from disk, last, every time.

## Additional resources

- **`references/bmad-headless.md`** — engine detection, the headless substitution contract, the
  BMAD-step→vault-source map, which BMAD outputs to discard, and the install command to report when
  no engine is present. Read at Stage 1.
- **`references/agent-dispatch.md`** — the per-feature worker prompt, its report contract, and the
  wave-verification checklist. Read at Stage 2, before fanning out.
