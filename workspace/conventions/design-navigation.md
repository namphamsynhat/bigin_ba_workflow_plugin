# Design Conventions — navigation and flows

The navigation map's schema, and how a user flow ties screens to the pain points they resolve.

**Read by** design stages 2, 4, and 6.

## User flows and pain points

A screen inventory says *what exists*. A **flow** says how a real person gets from a trigger to an
outcome — and it is the artifact this stage exists to get right, because it is the one a client can
recognise as their own working day or fail to.

```text
one flow  =  one user goal, for ONE actor, end to end
             entry (the trigger, in plain words)
             → the screens in order, one line each
             → the success end
             → each failure end, and the screen or state the user is left on
```

Every flow is a `## 4 Flows` entry in the UX spec, and every flow carries the two things that make it
reviewable:

```text
Resolves     the PP-### pain point(s) this journey fixes, or "—" when it serves a UC goal alone
Steps to     how many screens the actor passes through from trigger to success
goal
```

### D6 — a flow resolves something stated

```text
a UC goal                  → always sufficient. The flow delivers the UC's ## 2, end to end.
a PP-### pain point        → cite it. This is the flow saying WHY the journey is shaped this way
                             rather than some other way that also delivers the steps.
neither                    → an invented journey. It is not a flow; it is an Open Question.
```

**The pain-point register is READ-ONLY here** (`design-core.md` § Write map). A flow names the `PP-###` it resolves;
it never writes that row's `Resolved by` cell, never changes a pain point's status, and never adds
one. A pain point the flows reveal — a real friction nobody wrote down — is an Open Question owned by
the client, and `/bigin-transform-signal` is what puts it on the register.

**A pain point is not a licence to add a screen.** `PP-004: "reviewers lose track of what they
already approved"` grounds *how* the queue is ordered and *what* the flow shows on return; it does
not, on its own, ground a whole "approval history" screen nobody's UC asked for. Same line as
ground 2b in `design-grounding.md` § Grounding: it shapes a grounded thing, it does not create one.

### Flows on `both`

One flow per user goal, not one per platform. A phone that splits one web form into three sheets is
carrying the **same journey across more surfaces** — say so inside the flow's `Path` line
(`web: Details → Confirm · mobile: Details → Reviewers → Confirm`), never as a second flow. Two flows
for one goal is two journeys to keep in sync, and the second is wrong the first time a UC changes.

## The navigation map

**One** navigation map, at `{nav_map_file}`, shared by the whole vault — the menu/navigation system
for the platform or project: every persistent, directly-reachable entry point (a nav bar item, a
sidebar link, a tab, a flyout child) and the screen it opens. Two modes:

```text
{nav_map_file} absent  → BOOTSTRAP  create it from {template_nav_map}; the first screens seed it
{nav_map_file} present → EXTEND     load it, reuse its tree, ADD new entries screens actually need
```

It lives at `04-UIUX/_ux/`, **not** inside a design-system folder. Navigation is an experience
decision this skill owns end to end; a design system is a visual system somebody else supplies, and
putting the two in one directory made the first look like part of the second.

### The shell is a platform fact (`design-platform.md` § Platform)

The map's own shape follows `platform:` — one file either way, but the `## Structure` it holds differs:

```text
web     ## Structure                 a persistent sidebar / nav-bar shell. Arbitrary depth, as below.
mobile  ## Structure                 a TAB BAR — at most 5 top-level entries — plus per-screen
                                     headers and sheets. Depth below a tab is still arbitrary, but a
                                     6th tab is not a nav decision, it is an Open Question.
both    ## Structure — Web           BOTH sections, in one file, mapping the SAME feature set onto
        ## Structure — Mobile        each shell. One table per section, same columns.
```

**The five-tab cap is a real constraint, not a style preference.** A phone tab bar physically stops
being usable past five, so a sixth top-level candidate means either two features share a tab or one
belongs a level down — and which of those is right is a human call (an Open Question on this file,
owner: team), never a silent sixth row.

On `both`, an entry that exists on one shell and not the other is normal and expected: a web sidebar
can carry an admin area a phone app never surfaces. Say so in that row's `Grounded by` rather than
mirroring it onto the other shell to look symmetrical.

**Arbitrary depth, via a path id.** The map is not fixed at "group → entry" — a real IA nests as
deep as "Settings → Team → Members". One row per entry, at any depth; its `id` is a dot-path, the
parent's `id` plus one segment (`settings`, then `settings.team`, then `settings.team.members`). The
path **is** the tree: no separate level or parent column, and no cap on how deep it goes. A row can
be a pure container (a section header with children but no screen of its own — `Points to: —`), a
leaf (a screen, no children), or both. On `both`, an `id` is unique **within its own `## Structure`
section** — the same feature legitimately appears as `settings.team` on web and `more.team` on
mobile, because the two shells are two trees, not one tree rendered twice.

**Not every screen gets an entry.** A screen a user reaches directly from the menu — at whatever
depth — gets one; a screen reached only *through* another screen (a detail opened from a list, a
step inside a wizard, a modal) does not — it is reachable through its parent, and a menu entry for it
is a duplicate way in that drifts from the real IA the first time one of the two paths changes.

```text
directly reachable from the menu, on its own (top-level or nested)  → gets an entry
reached only via another screen's control                          → no entry (it is a destination,
                                                                       not a menu item)
```

**This is the vault's name for master-detail / drill-down navigation.** The plugin does not pick a
pattern off a shelf and label a screen with it — it derives the same outcome from one fact,
reachability, so it covers master-detail, wizard steps, and modals alike without a separate rule for
each. "Single menu entry, multiple views" is what a `Points to` cell holding more than one screen
name *is*: one row, one entry, and everything the row's cell lists beyond the first screen is a view
that entry's own screens open into, never a second door.

**A `Points to` cell listing several screens has an order, and the order carries meaning.** The
**first** screen named is the one the entry itself opens — the list, the landing screen, the thing a
user sees the moment they click the menu item. **Every screen after it** is reached only by a
control on a screen already in that same list (a row click into a detail, a tab, a wizard step) —
never a second entry, and never, when this map is handed to a render tool, a second persistent link
sitting beside the first in a sidebar or menu.

```text
Points to: Applications Queue, Application Review
           ^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^
           the entry opens      reached by clicking a row in Applications Queue — NOT a
           this directly        second sidebar link. Two links here is the failure this
                                 note exists to name: a client sees "Applications Queue" AND
                                 "Application Review" as siblings in the menu, when only the
                                 first was ever meant to be one.
```

Every entry is **grounded** the same way any other design decision is (`design-grounding.md` § Grounding below): a role
split traces to a `BR-###` or a UC's actors, a nesting decision traces to a stated preference, an
existing branch of the tree, or a `PP-###` the placement resolves, and a label that nothing in the
flow calls for is an Open Question, never an invented menu.

**Append-only (D1).** A screen that stops existing does not get its row deleted — see the template's
§ Removing an entry: mark it `retired`, keep the row, keep the history. Retiring a container retires
its whole subtree implicitly; its children are not re-listed. Deleting a row breaks nothing
technically, but it also erases the record of why the IA looks the way it does.

**`4-flow-review` may move an entry; it may never delete one.** Re-nesting a row (changing its `id`
to sit under a different parent) is the one structural change that pass makes, and it is still
append-only in effect: the old `id` is retired in § Removing an entry with `re-nested to <new id>` as
its reason, and the new one is added. A row that silently changes `id` breaks every screen spec
citing the old path.
