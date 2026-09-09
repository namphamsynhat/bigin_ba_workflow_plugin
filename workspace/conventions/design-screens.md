# Design Conventions — the UX spec and its screens

What the `UX-###` file holds, what a screen spec is, the semantic style roles that replaced design
tokens, and the View ID / Screen Type each screen carries.

**Read by** design stages 2, 3, 5, and 6.

## Semantic style roles — what replaced tokens

A screen spec says what an element **is for**, never what it looks like. One word, from a closed
list, in the element table's `Role` cell:

```text
primary action    the one thing this screen exists for
secondary action  a real action, not the main one
destructive       deletes, cancels, or revokes something
danger            a state or badge that means something is wrong or overdue
warning           something needs attention but is not yet wrong
success           something completed
info              neutral supporting information
emphasis          content that must be read first
muted             present, deliberately quiet — metadata, timestamps, helper text
default           carries no particular weight (leave blank; `default` is the absence of a role)
```

**A role is a design-system-independent fact.** "This is the primary action" stays true whichever
brand, palette, or component library is bound later — which is the whole reason it survives where a
token name would not. Whoever supplies the design system maps the ten roles once; nothing in the
vault has to change.

```text
ALLOWED     `primary action` · `danger` · `muted`
FORBIDDEN   `#2563eb` · `16px` · `Inter Semibold` · `--color-action-primary` · `btn-primary`
            → all four are D2 broken. The first three pin a value nobody stated; the last two cite a
              system this vault does not have, so nothing resolves them and a renderer picks its own
```

A screen that needs a **role the list does not carry** does not get a new role invented for it. It is
an Open Question (owner: team) asking whether the list should grow — a private eleventh role is a
one-screen vocabulary nobody else can map.

**Layout, density, and hierarchy are not roles.** "Three columns", "compact table", "above the fold"
belong in `regions` and the element order, where they already are.

## The UX spec

`{ux_dir}/UX-<NNN> <Feature>.md`, `type: uiux`, from `{template_ux}`. **One per feature** — never a
second one for a feature that already has one; a re-run updates it in place (bump `version`, append
a `## Changelog` line).

A **cross-feature UC** is designed once, in the UX spec of its `primary_feature`. Every other slug
in the UC's `features:` gets the same `## UX Spec` pointer on its hub. Same write-ownership rule the
UC itself follows.

`## 1 Design Brief` carries an **Actor & Scope** table — one row per actor the in-scope UCs name,
with the three `design-actor-scope.md` § Actor scope facts and what grounds each. It is what stops the run designing one
screen for two actors whose work is not the same work.

Sections: `## 1 Design Brief` · `## 2 Screen Inventory` · `## 3 Screen Specs` · `## 4 Flows`
*(carrying `### Coverage` — `design-grounding.md` § Coverage verification)* · `## 5 Navigation & Flow Review` ·
`## 6 Open Questions` · `## 7 Relationship Model` *(conditional — `design-review.md` § The relationship model)* ·
`## 8 Rendered Artifacts` *(pointers only, and written by `/bigin-render-design-od` alone — absent
until somebody renders)* · `## Changelog`.

**The spec ends at `## 8`.** There are no prototype-prompt blocks: `/bigin-render-design-od` builds its
own prompt from these sections, the UCs, the BRs, and the entity register, so a second hand-written
copy of the same screens was a drifting duplicate of the thing beside it. A spec written before this
change carries `## Prototype Prompt — …` headings; they are harmless and self-heal on that feature's
next design run (`3-screens.md` § Adopting an existing UX spec).

`## 7` is **appended after `## 6`, never inserted before it.** Renumbering `## 6 Open Questions`
would silently invalidate every hub mirror, stage guide, and verification check that cites it by
number — the section list is append-only for the same reason the navigation map is (D1).

## View ID and Screen Type

Two more facts about each screen, both written once in `## 2 Screen Inventory` and copied verbatim
into the matching `## 3` screen spec — so a render tool reads them off the spec directly and never
derives, slugifies, or guesses either one.

### View ID

A stable, kebab-case identifier, mechanically derived and never invented:

```text
view_id = "<feature slug>-<screen name, lower-cased, non-alphanumeric runs collapsed to one '-'>"

e.g. feature "applications", screen "Application Review"   → applications-application-review
     feature "settings-team", screen "Members"              → settings-team-members
```

The feature-slug prefix is what keeps it unique across the whole vault without a registry — two
features can each legitimately have a "Detail" screen, and their `view_id`s never collide. It never
changes once minted, the same discipline a nav-map `id` follows (D1's logic applied to a screen): a
screen renamed on a later run keeps its `view_id`, because a render tool, a prior prototype's
`data-screen` attribute (`bigin-render-design-od`'s `references/traceability.md`), and any prompt
already written against it all cite the old one.

### Screen Type

One value from a closed list of four, read off how the screen is actually reached — never assigned
to make the inventory table look complete:

```text
Primary      the screen a navigation-map entry opens DIRECTLY — the first name in some
             `{nav_map_file}` row's `Points to` cell, tagged `(Landing)` there
             (`design-navigation.md` § The navigation map). One per nav entry.
Drill-down   reached ONLY via a control on a screen already in the inventory — a row click into a
             detail, a "view" button, a confirmation step. Most Drill-down screens have no nav-map
             row at all; a few are the 2nd+ name in an existing entry's `Points to` cell, tagged
             `(Drill-down)` there. Either way, it never gets a menu item of its own.
Wizard       one step of a linked, ordered sequence toward a single goal — the STEPPED SHEETS
             `3-screens.md` Part 2 already produces on mobile for a long form, or an equivalent
             multi-step web form. A Wizard screen cannot stand alone; it is meaningless without the
             steps before it.
Tab          one of several PARALLEL views of the SAME place, switched by an in-screen tab control,
             never a menu — "Overview / Activity / Files" on one record. Grounded the same way any
             screen boundary is (`design-grounding.md` § Grounding: a UC step, a BR, or an existing
             pattern) — never invented to organize content that could just as well be one screen. A
             screen with an ordinary tab strip that stays lightweight content-in-place is not split
             into rows at all; only a tab complex enough to earn its own element table, states, and
             flows becomes its own `Tab`-typed row.
```

A `(Landing)`-tagged name in the nav map and a `Screen Type: Primary` row in the owning spec are the
SAME fact, written in two files by two different stages — Stage 2 tags the nav map, Stage 3 types the
inventory row, and neither reads the other's write. `6-close.md` check 19 is what confirms they still
agree; a mismatch there means one of the two stages is looking at a screen that has since moved.

**Never invent a fifth type.** A screen that does not cleanly read as one of the four is a `## 6`
question (owner: team) asking whether the list should grow — the same discipline § Semantic style
roles applies to an eleventh role.

## Screen spec — semantic structure only

One entry per screen in `## 3`:

```text
view_id      copied verbatim from this screen's ## 2 row (§ View ID and Screen Type) — never
             re-derived here, and never changed once minted
screen_type  copied verbatim from this screen's ## 2 row — Primary | Drill-down | Wizard | Tab
purpose      one line: what the user achieves here
serves       UC-<NNN> S<n>, S<n> …   the steps this screen delivers
actor        the ONE role this screen is for (`design-actor-scope.md` § Actor scope). Two actors whose volume band or
             capability differs get two screens, not one screen serving both
scope        whose records · how many · what they may do — each cited
             (e.g. `all · many (EN-004 many-per-Account) · read one, act on one — UC-030 S2`)
regions      web:    header / nav / main / aside / footer      — semantic HTML elements
             mobile: header / content / tab-bar / sheet / fab  — the phone vocabulary
             (`design-platform.md` § Platform. On `both`, a shared behaviour block plus a `Layout — Web` /
              `Layout — Mobile` split, ONLY where the two actually differ)
elements     per element: what it is · the content or copy · its semantic ROLE (§ Semantic style
             roles), when it carries one
             · the entity field it renders, when it renders one
             · `Visible to`, ONLY when a BR-### restricts that element to some of the screen's
               actors — blank means every actor of this screen sees it
states       empty · loading · validation-error · permission-denied · success
             each from a BR, an exception flow, or an entity's required fields — never invented
             a screen whose volume band is `many` additionally carries the VOLUME states —
             empty · few · many at real scale · loading · error — grounded by the volume fact
             itself (`design-actor-scope.md` § Actor scope, D8)
interactions what each control does, and which screen or state it leads to
```

**Copy is content, not styling** — real words a user reads, in the client's language, not `Lorem`.
