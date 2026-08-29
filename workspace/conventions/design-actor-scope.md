# Design Conventions — actor scope

Who a screen is for, how much data they hold, and when one place is really two screens.

**Read by** design stages 3, 5, and 6.

## Actor scope — who a screen is for, and how much they hold

Platform decides the **shape** of a design. Actor scope decides its **machinery**. The two are
orthogonal, and the second is the one a design run silently gets wrong: a UC reads "the actor views
member information" identically whether that actor is one member looking at their own record or an
administrator working a directory of ten thousand. Same words, same steps, two different products —
and the run that merges them ships the member's screen to the administrator.

Three facts, per actor, per screen. Each one is **read**, never assumed:

```text
whose records   own | assigned subset | their unit's | all
                ground: a BR-### about visibility or permission, the UC's ## 1 pre-conditions, or
                        how the UC itself defines the actor
how many        one | few (a countable handful) | many (unbounded — it grows with the business)
                ground: the EN-### relationship cardinality (one Account has many Orders), a BR-###
                        stating a cap, or a UC step that says so
what they may   read one · act on one · act on MANY at once
do              ground: a UC step or a BR-###. NEVER the volume — see D8 below.
```

Unresolvable from all three grounds → the scope is an Open Question (D3), and the screen is designed
to the **narrowest** reading in the meantime. Designing wide and asking later means the client
reviews an administrator's reach that nobody granted.

### The volume band is what changes the screen

```text
one     the record itself. NO find machinery — there is nothing to find, and a search box over one
        record is an invented affordance.
few     the set, listed whole. No pagination, no search: a filter over nine rows is noise.
many    the set can never be shown whole, so the screen's real job becomes FINDING, and it needs:
          a find mechanism    search, filter, or sort — at least one
          the volume states   empty · few · many (at real scale) · loading · error
        A `many` screen written without them is a design that works only on demo data, and it
        collapses the first time it meets the client's real table.
```

The band is a fact about the data, not a guess about the actor: `many` comes from the entity's own
cardinality or a BR, and an actor whose scope is `own` over a one-per-user entity is `one` no matter
how senior they are.

### D8 — the line volume may not cross

```text
LICENSED by the volume fact itself, cited as its ground
("EN-004 — many Orders per Account · UC-030 S2"):
    search · filter · sort · pagination or infinite scroll · a result count
    the empty / many / loading / error states
    a density choice (a table rather than cards) once the set is `many`

NOT licensed by volume, ever — every one of these is a CAPABILITY:
    bulk edit · bulk delete · "select all matching this filter" · export
    an approval, assignment, or status change applied to many records at once
    a saved view, a subscription, an alert
    → no UC step and no BR-### grants it  →  a REQUIREMENT GAP in ## 6, owner: client
```

An administrator who "obviously needs bulk delete" is exactly the failure D7 catches on the agent
side: plausible, unstated, and it reaches the client looking precisely like something somebody
specified. The client agrees to it in a prototype, and from that moment it is a requirement nobody
wrote, costed, or ruled on.

### When one place is two screens

Part 2's merge rule — two UCs landing on the same place become one screen — is the rule that
produces a one-size-fits-all design. It holds only when the actors' three facts agree:

```text
same place, two actors → compare the three facts:
    the VOLUME BAND differs      → TWO screens. A one-record view and an unbounded directory share
                                   nothing but the entity; they are not one screen with a filter bar
                                   bolted on.
    the CAPABILITY differs       → TWO screens. One actor reads their own record; another works a
                                   queue and acts on what is in it.
    both agree, and only WHICH   → ONE screen. Carry the difference in the element table's
    FIELDS are visible differs     `Visible to` cell, citing the BR-### that restricts it.
```

Same discipline as the `Layout — Web` / `Layout — Mobile` split (§ What `both` means): split what
genuinely differs, and never restate one design twice. What it splits on is different — a layout
split is **one** design on two shells, an actor split is **two** designs, because the two actors are
not doing the same work.

Two screens means two `## 2` inventory rows, each with its own `Serves` naming its own actor's UC
steps, and names that make the actor legible — `Member Directory (Admin)` beside `My Profile`, never
`Member Record` written twice. It also means **two flows** (`design-navigation.md` § User flows and pain points): the two
actors are on two journeys.

### Scope is not a persona

The same warning `design-review.md` § The relationship model carries. The UCs already name the actors; actor scope asks
three questions about each of them and nothing else. It never invents a user, a job title, a
demographic, a seniority, or a "power user" nobody wrote down, and it never reasons from what such a
person would probably want. An actor no UC names is not in scope — it is an Open Question.
