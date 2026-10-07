# Stage 1 — Scope: find the features whose approved use cases have no current epic

```text
runs: orchestrator, FIRST
in:   $ARGUMENTS (a slug, a UC-###, or nothing) + FEATURES.md + every feature hub
out:  the work-list: per feature, which approved UCs SLICE, which are CURRENT, which are
      PENDING, the chain verdict, the design read, and the prototype source
never: writing a story · reading a whole UC yet · touching a file
```

Read `feature-hub.md` § Feature material, `use-case.md` § Traceability chain, and `runtime.md` § Absorbed first.

## Part 1 — Candidates

```text
$ARGUMENTS is a slug        → that feature only
$ARGUMENTS is a UC-###      → that UC's primary_feature only
$ARGUMENTS is empty         → every file in {hub_dir}
```

Read each hub's **frontmatter** only (`uc:`, `uiux:`, `epics:`, `stories:`) plus its `## Use Cases` table.

## Part 2 — The chain gate

| `FEATURES.md` Status | Chain | This stage |
|---|---|---|
| `proposed` · `committed` · `not-built` | **Full** — `INT → UC/BR → UX → approve → EP → US` | in scope |
| `built` | **Lightweight CR** — `INT → UC/BR → US → UX` | in scope, **no epic file**: stories land in the feature's standing CR epic `EP-<NNN> <Feature> — changes` (created once, then reused) |
| `out-of-scope` | none | skip, always, and say so |

A missing `FEATURES.md` row is a data problem: stop on that feature, name it, leave it to `/extract-signal`.

## Part 3 — The four-way read, per UC

From the UC file's **own frontmatter** (`status:`, `version:`, `primary_feature:`), never the hub's tables:

```text
removed                                         → DROPPED   skip silently
not approved                                    → PENDING   epic § 2 out-of-scope line only
approved, primary_feature is another slug       → NOT OURS  sliced in the owner's epic; name it
approved, not in the epic's absorbed:           → SLICE     new
approved, in absorbed: at an older version      → SLICE     drifted — re-slice, see Part 5
approved, in absorbed: at the same version      → CURRENT   report it, don't re-slice
```

A feature with zero SLICE and zero CURRENT UCs: report `nothing approved yet → /approve-uc` and move on.

## Part 4 — Gates on a SLICE candidate

| # | Gate | Fails when | Then |
|---|---|---|---|
| 1 | has a flow | `## 2` has no step rows | skip — `approved but no main flow` |
| 2 | is a user goal | `level: summary` | skip — slice its child UCs instead |
| 3 | no open question | `## 5` has an unticked `- [ ] Q:` | still slice, but every story it lands in carries the question in § 8 and cannot pass § 9 |

## Part 5 — Drift on an existing epic

An approved story whose UC drifted is **never rewritten**. Report it `drifted: US-<NNN> (UC-<NNN>@1.2 → 1.4)` and
write any *new* paths as new draft stories. A `draft` story is updated in place (same id, version bump). The human
decides whether an approved story is reopened — that is a status change, and status is human-only (S5).

## Part 6 — The design and prototype read

```text
UX spec (hub uiux:)    → record UX-###@version; Stage 4 reads §§ 2-4. None → stories still get written,
                         § 5 screen blocks come from the prototype alone, and that is reported
prototype source       → in order: $ARGUMENTS --prototype <url|path> · UX § 8 Rendered Artifacts' latest
                         row · the epic's last SNAPSHOT.md source · none
latest snapshot        → the epic's newest _snapshot/ folder, if any, and its recorded version/hash
```

## Part 7 — Report the work-list, then mint

```text
per feature: chain · SLICE (ids@version) · CURRENT · PENDING · NOT OURS · drifted approved stories
             UX-###@version or "no design" · prototype source + kind · EP-### existing or "new"
```

Mint ids only here, in the orchestrator: `$BIGIN mint ep --spec <json>` (`{title, feature, source_ucs, snapshot}`) for a new epic. Story ids are minted in Stage 3, once the
slices are known. A feature that already has an epic keeps it — never mint a second one for the same slug.
