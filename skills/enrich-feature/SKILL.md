---
name: enrich-feature
description: Manually re-run domain research for one feature — the automatic pass `/extract-signal` § Step 2a already ran the moment this feature's hub was first created. Use this when the feature's scope has changed materially since that run, when the automatic run failed or was skipped (no research method resolved, a dispatch error, offline), or when a human just wants fresher grounding before drafting use cases. Never runs against a feature with no hub yet — that's what § Step 2a is for.
argument-hint: "<feature-slug>"
---

# Enrich Feature — manual domain-research refresh

Feature-level domain research is automatic now: the moment `/extract-signal` § Step 2a
(`_bigin/stages/extract/3-filing.md`) creates a feature's hub for the first time, it researches that
feature's stated scope and writes the first `## Domain Research` entry. This skill is the manual
re-run of that same pass, for later — scope changed enough that the original grounding is stale, or
that first run never landed a usable result.

```text
in:   a feature slug with an existing hub ({hub_dir}/<slug>.md)
out:  a new full report at 01-Requirements/_research/<slug>/domain-research.md, and one new entry
      appended to the hub's ## Domain Research section
never: touch a UC/BR file, promote an EN-### entity, or run against a slug with no hub yet
```

## What to do when invoked

1. **Resolve the slug.** `$ARGUMENTS`, or ask which feature if not given. If `{hub_dir}/<slug>.md`
   doesn't exist, stop and say so — there's no feature to research yet; point at `/extract-signal`,
   which creates the hub (and runs the first research pass) the moment a signal anchors to this slug.
2. **Gather the input.** Read the hub's H1 one-line description and its `## Notes / History` for
   what the feature has come to mean since the last research pass (not just its original one-line
   scope) — the same "what the feature has actually come to mean beats a one-line registry row"
   principle `3-filing.md` § Step 1 already uses for anchoring.
3. **Ask why, briefly, if not already stated.** A refresh should have a reason — scope changed, the
   automatic pass failed, or it's simply been a while and the human wants a check. One short
   question is enough; don't block on it if the invocation already said why.
4. **Run the research.** Read `_bigin/conventions/domain-research-method.md` for the dispatch
   mechanics. Scope is "the `<feature-name>` feature," input text is what § 2 gathered.
5. **Write the findings**, same shape as the automatic pass:
   - Full report: `01-Requirements/_research/<slug>/domain-research.md` — a **new** file if the
     automatic pass never wrote one (research skipped/failed at registration), otherwise append a
     dated section to the existing report rather than overwriting it — the earlier grounding is
     still a record of what was known at the time.
   - One new entry on the hub's `## Domain Research`: `- **<date>** — <the reason from § 3> —
     <one-line summary> ([full report](01-Requirements/_research/<slug>/domain-research.md))`.
6. **Report** what changed — new findings that update or contradict the earlier grounding are worth
   surfacing explicitly, not just appending quietly.

## Rules

- **Append-only**, same discipline as the Signal Log and every other permanent-id table in this
  plugin: a refresh adds an entry, it never rewrites or removes an earlier one.
- **Never promotes an entity** — that's `/sync-entities`'s job, even if research surfaces a new one;
  note it and let a normal signal carry it through instead.
- **Never touches `## 1`–`## 6` on any UC**, `## Entities`, `## Requirement Readiness`, or
  `## Business Scenarios` — this skill's whole footprint is the hub's `## Domain Research` section
  and the `01-Requirements/_research/<slug>/` report.
- **An unattended run records findings with no human call attached** where the automatic pass would
  have asked one — same "record, don't adjudicate" rule `agents/bigin-ba.md` § Working unattended
  states elsewhere.
