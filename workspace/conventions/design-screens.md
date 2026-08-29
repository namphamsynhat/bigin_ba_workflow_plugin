# Design Conventions — the UX spec and its screens

What the `UX-###` file holds, what a screen spec is, and the semantic style roles that replaced
design tokens.

**Read by** design stages 3 and 5.

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

## Screen spec — semantic structure only

One entry per screen in `## 3`:

```text
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
