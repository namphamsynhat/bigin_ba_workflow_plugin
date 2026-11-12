# Stage 3 — Adopting a UX spec written before the current template

```text
read:  ONLY when Stage 3 is updating an existing UX spec in an older shape (3-screens.md § Adopting an
       existing UX spec names the signs). A new spec, or one already current, never needs this file.
```

## What to change, and what to leave

`## 7 Relationship Model` was added to `{template_ux}` after some specs already existed. There is no
content to transform and nothing to migrate:

```text
spec has no ## 7, trigger passes now   → add the section, set relationship_model: modelled
spec has no ## 7, trigger misses       → leave it exactly as it is. `relationship_model:` absent
                                         reads the same as `none`.
spec HAS ## 7 from an earlier run      → update it in place like any other section. Never fork it.
```

`platform` arrived the same way, and the same shape applies. A spec written before it existed has no
`Platform` value in its `## 1 Design Brief` (or the literal words "not stated"):

```text
no Platform value                       → a `web` spec, by definition — `web` is the absent-platform
                                          default, and web is exactly what that run produced
next design run of its feature          → self-heals: write Platform from the dispatch slot
dispatched platform is now mobile|both  → still not a fork: same spec, updated in place
```

**A spec written against a design system** carries three things this pipeline no longer produces,
and all three self-heal in place — never by forking the spec:

```text
## 3 element tables with a `Token(s)` column   → rename the column `Role` and re-fill it from the
                                                 closed list (`design-screens.md` § Semantic style
                                                 roles). A cell holding `--color-action-primary` on
                                                 the submit button becomes `primary action`; a cell
                                                 holding a hex, a px, or a font name becomes the
                                                 role it was standing in for, or BLANK. Do not try
                                                 to preserve the old token name anywhere: nothing
                                                 resolves it any more.
## 5 Design System Usage                       → becomes ## 5 Navigation & Flow Review. Keep its
                                                 nav rows (they are still true); drop `Design system
                                                 version`, `Tokens used`, `Components used`, and
                                                 `Added this run`.
## Prototype Prompt — … blocks (2 or 4)        → DELETE them, all of them. /bigin-render-design-od
                                                 builds its own prompt from ## 1-## 5, the UCs, the
                                                 BRs, and the entity register, so these are a stale
                                                 second copy of the screens beside them — and they
                                                 inline token values that no longer exist anywhere.
                                                 Say so in the ## Changelog line.
frontmatter `design_system:`                   → drop the key. `nav_map:` stays.
```

`## 4 Flows` written before `Resolves` and `Steps to goal` existed carries neither: fill both this
run, per Part 4c, for every flow in the section — including flows this run did not otherwise touch.
An unfilled `Resolves` reads as "no pain point applies here", which is a claim nobody made.

`## 1`'s **Actor & Scope** table, `## 2`'s `Actor` and `Volume` columns, and `## 3`'s `Actor` /
`Scope` lines arrived the same way, and this one has real content behind it — a spec written before
them may carry a screen that quietly serves two actors with different scope:

```text
spec has no `actors:` key and no   → build both this run from the in-scope UCs' ## 1 actors, per
Actor & Scope table                  Part 2a. The absent key IS the marker of a spec written before
                                     this existed; its presence is the marker of one already
                                     migrated. The table is not a backfill of what the old run
                                     meant — it is read fresh from the requirements, like any
                                     other Part 1 input.
existing ## 2 rows, 5 columns      → add the Actor and Volume columns and fill them for every row,
                                     including rows this run did not otherwise touch: an unfilled
                                     cell reads as "no actor has been checked here", which is true
                                     and needs to stop being true.
an existing row serves two UCs     → run Part 2a's comparison on it NOW. Scope agrees → leave the
whose actors' scope DISAGREES        merged row, one actor per the table. Scope disagrees → SPLIT
                                     it into two rows this run, and say so in the ## Changelog line:
                                     it is the same correction as any other, not a fork, and the
                                     spec is still updated in place.
an existing `many` screen with no  → add them this run (Part 4). The volume fact grounded them all
find machinery or volume states      along; the earlier run had no rule telling it to look.
a bulk action or export already    → do NOT silently delete it. Check whether a UC step or BR-###
on an existing screen                grants it: granted → cite the ground and keep it. Nothing
                                     grants it → raise it as a requirement gap in ## 6 and say in
                                     the report that an ungranted capability is already on a screen
                                     a client may have seen (D8).
```

That last row is the one that matters: a capability already sitting in a spec has probably already
been prototyped, so removing it silently loses the fact that somebody was shown it. Raise it, let
`/bigin-transform-signal` settle whether it was ever meant to exist.

`## 2`'s `View ID` and `Screen Type` columns arrived the same way, and self-heal the same way:

```text
existing ## 2 rows, no View ID / Screen Type columns   → add both this run, for EVERY row including
                                                          ones this run did not otherwise touch: mint
                                                          each View ID mechanically (§ View ID and
                                                          Screen Type), and classify each Screen Type
                                                          by re-reading how it is actually reached
                                                          TODAY — its own nav-map row and tag, or the
                                                          absence of one. Never a placeholder on
                                                          either column.
a screen {nav_map_file} already tags (Landing) or       → its Screen Type is fixed by that tag:
(Drill-down)                                              Primary for (Landing), Drill-down for
                                                          (Drill-down). Wizard and Tab apply only to
                                                          a screen the nav map does not name at all.
```

Every spec self-heals on the next design run of its feature. A spec whose feature is never redesigned
keeps working — nothing downstream requires `## 7`, a `Platform` value, an Actor & Scope table, a
`Role` column, or a `Resolves` cell to exist. `/bigin-render-design-od` reads whichever shape it finds
and reports what it could not resolve rather than halting.
