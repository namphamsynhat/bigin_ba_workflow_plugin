# Agentic UX — the relationship model, and how the booster earns its place

Read at **Stage 1**, by the orchestrator, when a relationship-centric-interfaces skill is installed.

```text
this file is ORCHESTRATOR-FACING          how to decide it applies, what to tell a worker, how to verify
3-screens.md Part 4b is WORKER-FACING     the procedure itself, materialized where a subagent can read it
`design-review.md` § The relationship model is the CONTRACT   what ## 7 is, what grounds each row
```

A worker never reads this file — a `SKILL.md` and its `references/` live in the plugin install
directory, which a subagent cannot reach. Everything a worker needs is in the materialized stage
guide. Duplicating the procedure here is how the two drift.

## What the booster is for, stated honestly

An installed agentic-UX skill contributes **one** thing this plugin could not otherwise produce: a
vocabulary for the part of an agent feature's design that is **longitudinal** — what the system
carries between sessions, and what it may do unprompted as a relationship matures.

```text
it contributes    a way to SAY the relationship the requirements already imply
it does NOT       discover that the product should have memory, autonomy, or a dashboard
```

The second line is the whole risk. That skill ships a pattern library of memory dashboards, goal
dashboards, planning canvases, preference-evolution maps, and contextual timelines — all of which are
**whole screens**. Applied as a source, they produce a feature nobody specified, carrying a citation
that makes it read as designed. That is the most expensive failure this skill has (`SKILL.md`
§ Failure modes), arriving through the front door.

So the booster is bounded by grounding, not by good intentions:

```text
an external pattern is ground 2b (`design-grounding.md` § Grounding)
    → it shapes HOW something already grounded by a requirement, a vault pattern, or a stated
      preference gets built
    → it can NEVER ground THAT a screen, field, or state exists
```

## Deciding it applies — the orchestrator's two questions

### 1. Is the skill installed?

A relationship-centric-interfaces skill (e.g. `agentic-ux-design-relationship-centric-interfaces`) in
this session's available-skills list. Absent → skip silently. Unlike a missing **engine**, a missing
booster is not reported as an install suggestion: `## 7` is written from the stage guide either way,
and the skill only sharpens the vocabulary.

### 2. Does any feature in scope pass the trigger?

Stage 1 reads frontmatter only, so it **cannot** answer this — the trigger needs UC step verbs, an
entity field list, and a trigger line. Three consequences:

```text
Stage 1     records only that the booster is AVAILABLE
dispatch    tells each worker to run Part 4b's trigger test itself, per feature
Stage 5     verifies the outcome from disk (checks 10-12) — never from the worker's report
```

For the orchestrator's own inline runs (one or two features), the test is `3-screens.md` Part 4b:
the system judges rather than processes, **and** an `EN-###` field persists something per-user between
sessions, **and** the trigger recurs for the same actor. Three of three, or `none`.

Test 2 fails most often and is the one worth trusting. A chatbot screen, an "AI suggestions" panel fed
by nothing stored, and a report ranked identically for everyone all fail it — and none of them has a
relationship to model.

## The five pillars, mapped onto artifacts that already exist

The agentic skill is organised around five pillars. Four map onto this vault; one does not. Mapping
them explicitly is what stops a worker inventing a home for each.

| Pillar | Where it lands here | What grounds it |
|---|---|---|
| **1 Memory** | `## 7` Memory Architecture, plus the `## 3` elements that surface it | an `EN-###` field, always. No field → a requirement gap |
| **2 Trust evolution** | `## 7` Trust Map — the one pillar with no existing home, because a trust stage is longitudinal and `## 3` States is within-session | a `BR-###` granting the autonomy, or an `E#` exception flow. An ungranted stage 3 stays empty |
| **3 Relationship architecture** | `## 7` Relationship Context — duration, frequency, autonomy ceiling, memory sensitivity | a UC trigger/post-condition, a BR, an active principle row, a hub directive |
| **4 Systems that plan their own path** | mostly **requirement gaps**. "The agent constructs its own workflow" is behaviour, not layout | a UC step, or it is a gap for `/bigin-transform-signal` |
| **5 New success metrics** | `## 7` Proposed Measures — three, owner team, and **nothing further** | out of design's scope by construction: instrumentation is behaviour |

Pillar 5 is deliberately clipped. Trust scores, delegation comfort, and month-6-vs-month-1
comparisons are product measurement; a design stage that specifies them has started specifying what
gets built. Three proposed measures, team-owned, and the conversation moves to whoever owns metrics.

## What good output looks like

A worked shape, not a template to copy — the real rows come from the real UC.

```text
feature: review-queue     UC-014 "the reviewer clears the day's flagged requests"
                          EN-009.reviewer_pattern  (per-user, learned)   BR-021 (confidence ≥ 0.9)

trigger      judges ✓ (S3: "the assistant ranks the queue by likely decision")
             persists ✓ (EN-009.reviewer_pattern)
             repeats ✓ (## 1 trigger: "each working morning")          → MODELLED

memory       "how this reviewer has decided similar requests"
               ← EN-009.reviewer_pattern | surfaced on: Review Queue (the ordering, and the
                 "why this is first" affordance) | controlled by: the reviewer (BR-021)

trust        Review Queue · ordering
               stage 1  shows the reason beside every row
               stage 2  shows it only where confidence is below the threshold  ← BR-021
               stage 3  (empty — no rule grants acting without the reviewer)
               correction: the reviewer reorders, and says why            ← UC-014 A2

gaps → ## 6  how long is a reviewer's pattern kept, and can they clear it?      (requirement gap)
             who else may see what the assistant learned about a reviewer?      (requirement gap)
             does the reviewer know their decisions train the ordering?         (requirement gap)
```

Three rows, three gaps. **That ratio is normal and correct.** A UC states what the system does with
the memory; it almost never states retention, visibility, or disclosure. A relationship model that
produces rows and no gaps has quietly answered all three itself.

## The recurring five gaps

Every real agent feature raises these, and a UC has almost never settled them. Each is a requirement
gap in `## 6` unless a `BR-###` answers it:

```text
autonomy     what may it do WITHOUT asking, and above what confidence?
retention    how long is this kept, and can the user clear it?
visibility   who else sees what it learned about this user?
recovery     what happens when it is WRONG — what is undone, who is accountable?
disclosure   does the user know it is learning from them?
```

Routing them correctly is the booster's highest-value output — considerably higher than any screen it
helps shape. They surface *before* a prototype exists, which is the only point at which they are cheap:
once a client has watched a prototype remember and decide, the answers have been set by a demo.

## Invoking the skill

Read its own instructions for how it wants to be invoked, then treat everything it returns as ground
2b. It announces itself ("I'm using the Relationship Design skill…") — that announcement is for a
human in a live session and has no place in a UX spec or a closeout.

Its own `when_to_use` is explicit that it is for relationship-centric design **on request**, not
general UI work. Part 4b's trigger is this plugin's mechanical version of that same boundary; when
the trigger misses, the skill is out of scope even though it is installed.

Say in the closeout which features it applied to and why — the same way the chosen engine is named.

## Failure modes

- **Treating the pattern library as a source.** A memory dashboard reaches the client carrying a
  citation. An obvious guess gets caught in review; a cited invention does not.
- **Firing on "it has AI in it".** The trigger is three mechanical tests against a step verb, an
  entity field, and a trigger line. A feature that merely displays a model's output has no
  relationship to model.
- **Filling a stage-3 autonomous cell nothing granted.** The prototype shows the agent acting alone,
  the client agrees it looks right, and no one ever decided the system may do that (D7).
- **Writing the five gaps as design questions.** They change what the system does, so they are
  requirement gaps owned by `/bigin-transform-signal` — mislabelled, they get answered by whoever is
  reviewing screens.
- **Specifying pillar 5 past three proposed measures.** A design stage that defines trust scores and
  tracking events has started specifying behaviour under a metrics heading.
- **Duplicating Part 4b into this file.** A worker cannot read this file. Two copies of one procedure
  means the copy nobody reads is the one that stays correct.
