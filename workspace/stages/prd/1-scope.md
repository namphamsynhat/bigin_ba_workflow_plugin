# Stage 1 — Scope: find the features whose approved use cases have no current PRD

```text
runs: orchestrator, FIRST
in:   $ARGUMENTS (a slug, a UC-###, or nothing) + FEATURES.md + every feature hub
out:  the work-list: per feature, which approved UCs FOLD, which are CURRENT,
      which are PENDING (not approved), plus the chain verdict
never: writing a PRD section · reading a whole UC yet · touching a file
```

Read `{conventions_reference}` § Feature material, § Traceability chain, and § Absorbed before this
stage. They define the eligibility test, the chain gate, and the staleness read used below.

## Part 1 — Which features are candidates

```text
$ARGUMENTS is a slug        → that feature only
$ARGUMENTS is a UC-###      → that UC's primary_feature only
$ARGUMENTS is empty         → every file in {hub_dir}
```

Read only each hub's **frontmatter** here (`uc:`, `uiux:`, `prd:`) plus its `## Use Cases` table.
Full UC bodies are Stage 3's job — a scan that opens every UC in full burns the run before a single
capability is written.

## Part 2 — The chain gate, per feature

The `FEATURES.md` row's `Status` decides whether this feature takes a PRD **at all**
(`{conventions_reference}` § Traceability chain):

| `FEATURES.md` Status | Chain | This stage |
|---|---|---|
| `proposed` · `committed` · `not-built` | **Full** — `INT → UC/BR → PRD → EP → US → UX` | in scope. `chain: full` |
| `built` | **Lightweight CR** — `INT → UC/BR → US → UX`, **skipping the PRD** | **skip, and say why.** A change to something already shipped goes straight to a story |
| `out-of-scope` | none | **skip, always.** A feature the engagement has excluded gets no PRD, even if UCs on it were approved before it was excluded. Say so — a PRD for excluded scope is the one output nobody will notice is wrong |

A `built` feature named **explicitly** in `$ARGUMENTS` is the one exception: write the PRD, stamp
`chain: cr`, and state in the report that the CR chain does not normally produce one so nobody reads
its existence as the rule changing.

A feature whose `FEATURES.md` row is missing entirely is a data problem, not a chain: stop on that
feature, name it, and leave it to `/extract-signal`, which owns the registry.

A UC whose participating features disagree on Status takes its `primary_feature`'s chain. Name the
disagreement in the report rather than resolving it silently per feature.

## Part 3 — The four-way read, per UC

```text
per candidate feature:
    ucs      = the hub's uc: list
    prd      = {prd_dir}/PRD-### for this feature  (from the hub's prd:, else Grep {prd_dir}
                                                    for feature: <slug>)
    absorbed = prd.absorbed:  or []  if no PRD yet

    per uc in ucs:
        read that UC file's FRONTMATTER only — status: and version:
        status is removed                              → DROPPED   skip silently
        status is not approved                         → PENDING   § 10, never §§ 5-9  (P2)
        approved, not in absorbed                      → FOLD      new material
        approved, in absorbed at an older version      → FOLD      it drifted since last time
        approved, in absorbed at the same version      → CURRENT   already covered
```

`status:` on the UC's own file is the authoritative gate, **not** the hub's `## Use Cases` table or
its `## Requirement Readiness` snapshot — both are refreshed indexes and both go stale
(`{conventions_reference}` § Feature Hub). Read the frontmatter.

`CURRENT` is a result, not a silence. Report it (`<slug>: 4 approved UC current, nothing to fold`)
so a human can tell "already in the PRD" from "the run never reached it".

**A feature with zero FOLD and zero CURRENT UCs has nothing approved yet.** Do not write a PRD
containing only a Pending Scope table — report `nothing approved yet → /approve-uc` and move on.
An existing PRD is still refreshed in that case if any of its already-folded UCs drifted.

## Part 4 — Three gates on a FOLD candidate, in order

| # | Gate | Fails when | Then |
|---|---|---|---|
| 1 | **has a flow** | `## 2 Main Success Scenario` has no step rows | skip this UC. An approved UC with no flow is a data problem worth naming: `approved but no main flow` |
| 2 | **has a goal** | `title:` is empty, or `level: summary` | skip. A summary-level UC is a grouping of other UCs; fold those instead, and use its title as the § 5 grouping if it helps |
| 3 | **is owned here** | this feature is not the UC's `primary_feature` | skip **in this feature's PRD** — it is carried in the owner's. Note the owner; a cross-feature UC still lists this slug in the owning PRD's `features:` |

## Part 5 — The design read

Per candidate feature, note whether a UX spec exists and at what version
(`{ux_dir}`, from the hub's `uiux:`). Do not read its body yet — Stage 4 does that.

```text
no UX spec            → § 9 is one line saying no design exists yet. NOT a blocker
UX spec exists        → Stage 4 folds its screens; record UX-###@version for design_absorbed:
UX exists but its absorbed: lacks a UC this run folds
                      → the design predates that UC. Fold what the design does cover, and report
                        the gap as `design stale → /bigin-generate-design`. Never guess a screen
```

## Part 6 — Report the work-list before writing anything

```text
per feature:  chain · FOLD (ids@version) · CURRENT (count) · PENDING (ids + status)
              DROPPED/skipped (id + which gate) · UX-###@version or "no design"
              PRD-### existing, or "new — id to mint"
```

Mint a new `PRD-###` only in the orchestrator, and only for a feature that has at least one FOLD or
CURRENT UC: `Grep` `{prd_dir}` for `PRD-\d{3}` and take the highest + 1
(`{conventions_reference}` § ID scheme — use the `Grep` tool, never a Bash `grep`/`awk` pipeline).
A feature that already has a PRD keeps its id and version-bumps; never mint a second one for the
same slug.
