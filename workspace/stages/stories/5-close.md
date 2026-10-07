# Stage 5 — Close: verify, stamp, refresh the hub, report

```text
runs: orchestrator, LAST, one feature at a time — hubs are shared state
in:   every file Stages 2-4 wrote this run
out:  absorbed: stamped, the hub's epics:/stories: and ## Epics & Stories refreshed, the report
never: setting status: approved · editing a UC, BR, entity, UX spec, or snapshot
```

## Part 1 — Verification (a failure is blocking: fix it, then re-run the check)

| # | Check | How |
|---|---|---|
| 1 | Coverage complete | `$BIGIN coverage --stage stories --list` reports no uncovered `S#`/`A#`/`E#` |
| 2 | Business language | `$BIGIN lint --full` raises no banned-term finding on these files |
| 3 | Diagrams parse | lint's Mermaid header check passes; every fence is closed |
| 4 | Every story is in its epic | each `US-###` `epic:` names this epic, and the epic's `stories:` lists it |
| 5 | Every AC is tagged | each `Scenario:` line in § 6 carries at least one `[S#]`, `[A#]`, `[E#]`, or `[BR-###]` |
| 6 | Images resolve | every `![](_snapshot/…)` path exists — or `snapshot: none` and § 8 says so |
| 7 | Approved stories untouched | `git diff` / content compare: no file at `status: approved` changed this run |
| 8 | Status | every file written this run is `status: draft` |

## Part 2 — Stamp

`absorbed:` re-stamped **whole** on the epic and on each story written or updated: `UC-<NNN>@<version>` for the UCs
really sliced into it, `UX-<NNN>@<version>` for the design read. Never append. A legacy `PRD-###` read as context is
stamped too, so its drift is visible.

## Part 3 — Refresh the hub

On the feature's hub, and nothing else on it: frontmatter `epics:` and `stories:`, and the `## Epics & Stories`
section — one row per story:

```markdown
| Story | Priority | Slice of | Status |
| :--- | :--- | :--- | :--- |
| [[US-001 Book a free slot]] | P1 | UC-003 S1–S6 | draft |
```

## Part 4 — Report

```text
per feature: EP-### (new|updated) · stories new / updated / unchanged · drifted approved stories
             snapshot (new <folder> | reused | none) + gaps · open questions · verification 8/8
next: review the epic and stories, then /approve-story <US-###…> (or the whole EP-###)
```

## Adopting an existing PRD

`PRD-###` is retired (`core.md` § Prefixes). A vault that still has `02-PRD/` files keeps them, frozen. This stage
may read a feature's PRD for § 1 goals and § 11 decisions, as **context only**, and stamps `PRD-<NNN>@<version>` in
`absorbed:` when it does. It never writes a PRD.

## Adopting an existing EP

A vault with hand-written epics (a flat `03-Epics-Stories/epics.md`, or stories nested in one file) is left alone.
The first run on such a feature mints a new `EP-###` folder, lists the old file under the epic's § 9 Decisions as
`superseded by EP-<NNN> — kept for history`, and never deletes or rewrites it (hard rule 1).
