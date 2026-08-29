# Stage 3 — Screens: turn one feature's flows into a UX spec

```text
runs: one worker per FEATURE (a subagent, or the orchestrator inline for a small run)
in:   this feature's NEW/CHANGED UCs + its BRs, entities, directives, principles
out:  {ux_dir}/UX-<NNN> <Feature>.md — brief, screen inventory, screen specs, flows
      + ## 7 Relationship Model, on a feature that passes Part 4b's trigger (most do not)
      + a report of nav candidates (this stage NEVER writes the navigation map)
never: an invented screen · a raw colour/size/token id · an invented nav entry · an invented journey
       · an edit to a UC, BR, entity, or pain point
       · a memory, autonomy, or retention rule the requirements did not state (D7)
       · one screen serving two actors whose volume band or capability differs, and no bulk action,
         export, or saved view the requirements did not grant (D8)
```

Read `design-screens.md` § The UX spec, `design-screens.md` § Screen spec, `design-screens.md` § Semantic style roles, `design-grounding.md` § Grounding,
`questions.md` § Open questions, `design-actor-scope.md` § Actor scope, `design-navigation.md` § User flows and pain points, `design-review.md` § The relationship model,
`design-navigation.md` § The navigation map, and `design-platform.md` § Platform first.

---

## Part 1 — Read the brief, in this order

```text
0  your dispatch prompt        platform: web | mobile | both — the orchestrator read the project
                               config once, at Stage 1, and passed it to you. You never open the
                               project config to check it, and you never resolve a design engine:
                               two workers inferring a platform differently produce one product
                               with two navigation shells.
1  the hub                     {hub_dir}/<slug>.md   → ## Design Directives (Status: open), actors
2  each UC in scope, in full   ## 1 actors/trigger/pre+post · ## 2 steps · ## 3 branches
                               ## 4 rule mirror · ## 5 Still open (these are KNOWN GAPS)
3  each BR named in ## 4       the real rule text — the mirror is short on purpose
                               — note any rule about WHO MAY SEE OR DO WHAT: whose records an actor
                                 reaches, and whether they may act on many at once. Part 2a's
                                 three facts are read from these, and nowhere else.
4  each EN in the UC's entities:  the field list, types, required?, enum values
                               — note any field holding per-user history, preference, pattern, or
                                 score: Part 4b's trigger turns on whether one exists
                               — note each RELATIONSHIP CARDINALITY (one Account has many Orders):
                                 it is what tells Part 2a whether an actor's set is one, few, or
                                 unbounded, and the band decides the screen's machinery
5  the hub's ## Pain Points    every row NOT resolved — PP-### and the client's own words. These
                               are what the FLOWS have to fix (Part 5), and what shapes emphasis and
                               ordering on a screen. They never create one (ground 1b)
6  {design_principles_file}    rows with Status: active
7  {nav_map_file}              its ## Structure — the tree that already exists, at whatever depth,
                               so a new entry joins an existing branch instead of starting a
                               parallel one
8  the existing UX spec, if any        you UPDATE it; you never fork it
9  ONE sibling UX spec, at most, and only when this feature needs a pattern the nav map does not
   already name — a list, a queue, an approval, a wizard. Pick it from {nav_map_file}'s
   ## Structure, which names which feature owns which branch; grep {ux_dir} for the pattern
   rather than reading specs to find out who has it. Reuse beats inventing (ground 2).
   → NEVER read every UX-*.md. At two features that is a habit; at ten it is nine specs in
     context before this feature's first screen, and the ten-feature project is the one where
     the cost lands.

There is **no design system to read** and no token file: a screen names a semantic ROLE
(`design-screens.md` § Semantic style roles), and the visual system is supplied later by a design
team or bound at render time. A worker that goes looking for `_design-system/` finds either nothing
or a stale folder nothing reads.
```

Write `## 1 Design Brief` from step 0 and steps 1–6: actors, platform, the pain points in scope, the
principles applied, the directives applied, and the known gaps (each open UC question, one line,
marked as a gap). Then fill
its **Actor & Scope** table — one row per actor the in-scope UCs name — per Part 2a below. Fill it
before you map a single screen: it is the input to Part 2's merge rule, not a summary written after.

`Platform` is **written from the dispatch slot** — the value you were told, verbatim. There is
nothing to look up and nothing to infer; "not stated" is no longer one of its values.

Reading a platform out of the UCs, the directives, and the principles is now a **per-feature
override**, and only that:

```text
a UC, a hub ## Design Directives row, or an active DESIGN-PRINCIPLES row that EXPLICITLY STATES a
platform for this feature ("the courier's job list is phone-only")
    → design this feature to the stated platform, and cite its ground — the UC step, the directive
      row #, the principle row # — like any other decision
nothing states a platform
    → the dispatched value, unchanged, no citation needed
an inference: step wording ("the courier is out on the road, so this is mobile"), where an actor
sits ("the back-office reviewer at a desk"), a device a step happens to mention
    → NOT an override. Design to the dispatched platform, and raise an Open Question in ## 6
```

**The bar is an explicit statement, not a plausible reading.** Guessing a platform from a step's
wording is the same failure as inventing a screen: it reaches the client as a decision somebody
made. Ambiguous → the dispatched platform, plus a question.

Stop reading here. A PRD, an INT note, `## Raw`, or a Signal Log row is not design input.

---

## Part 2 — Flows become screens

The UC says **what happens**. It does not say **how many screens**. This is the mapping:

```text
per UC, walk ## 2 in row order:
    a run of consecutive steps by the SAME actor in the SAME place  → ONE screen
    the actor moves to a different place or task                    → a NEW screen
    a step whose actor is the SYSTEM only                           → NOT a screen
                                                                      (it is a state, or invisible)
    a step that only validates                                      → a STATE on the current screen
    a ## 3 A-flow (alternative)                                     → usually a state or a variant
    a ## 3 E-flow (exception)                                       → an error STATE, named
    a ## 3 flow that changes place                                  → its own screen
```

Then merge across UCs — but **only after Part 2a**, which is the test the merge has to pass:

```text
two UCs whose steps land on the same place
    AND whose actors' scope agrees (Part 2a)   → ONE screen serving both. List both UCs in `serves`.
    AND whose actors' scope does NOT agree     → TWO screens. Part 2a says which.
```

Merging on "same place" alone is how one screen ends up serving a member reading their own record
and an administrator working ten thousand of them. Read Part 2a before you merge anything.

### On mobile, the same mapping splits further

Every rule above still holds on a phone — same steps, same actors, same places — but a phone surface
carries less, so a run of consecutive steps that is one web page is often several phone screens:

```text
one primary action per screen        two equal-weight actions on one phone screen → two screens,
                                     or one action plus a clearly secondary control
a long form                          → STEPPED SHEETS, one field group per step, named in order.
                                     Never one tall scrolling screen.
a table- or list-heavy screen        → a list or card feed, one record per row/card, the detail
                                     behind a tap
a side-by-side layout (list+detail)  → two screens: the list, then the detail
```

The steps do not change; the number of surfaces they need does.

Screen count sanity, per platform:

```text
web     a 3–9 step user-goal UC normally yields 1–4 screens
mobile  the same UC normally yields 2–6 — the split rules above legitimately produce MORE, SMALLER
        screens, and one phone screen answering a 7-step flow usually means a tall scrolling screen
        that should have been sheets
both    judged on the web band — the inventory is the shared goal set; a mobile layout split lives
        INSIDE a row, and never adds one
```

Over the band means states got promoted to screens. One screen for four different tasks means
screens got merged that should not be.

**Never add a screen no step needs.** No login, settings, profile, dashboard, or help screen unless a
step, a rule, or a directive puts it there. An invented screen looks exactly like a designed one.
The mobile rules divide work a step already states across more surfaces — they never license a
surface no step asked for: if you cannot name the step a phone screen delivers, it is invented, and
a phone is not an excuse.

Write the result into `## 2 Screen Inventory`:

```text
| Screen | Actor | Volume | Purpose | Serves | Entities | Key actions |
            ^ ONE role      ^ one|few|many   ^ UC-### S4, S5   ^ EN-###   ^ the real buttons
              (Part 2a)       (Part 2a)
```

`Actor` and `Volume` come from `## 1`'s Actor & Scope table, and they are what make the split
visible in the inventory itself: two rows differing in either one are two screens on purpose.

On `both` this is **ONE inventory** — the same user goals, one row per screen, never a web table and
a mobile table. Where a step genuinely needs a different number of surfaces on each platform (a web
form that must become three phone sheets), that is a **layout split inside the row**, not a second
row: name it in the row's `Purpose` cell (`web: one form · mobile: 3 sheets — details → reviewers →
confirm`) and carry the real detail in that screen's `Layout — Mobile` block (Part 3). Two
inventories means two designs to keep in sync, and the second goes stale the first time a UC
changes.

---

## Part 2a — Actor scope: whose data, how much, and when one place is two screens

Part 2 asked *what happens*. This part asks **who it happens to, and how much of it they hold** —
the axis a UC is silent on, because a UC is written to be actor-neutral. "The actor views member
information" reads identically whether the actor is one member looking at their own record or an
administrator working a directory of ten thousand. Those are not one screen with a filter bar bolted
on; they are two products, and merging them ships the member's screen to the administrator.

Read `design-actor-scope.md` § Actor scope before this part. It is the standard; this is the
procedure.

### The three facts, per actor

Fill `## 1`'s **Actor & Scope** table — one row per actor the in-scope UCs name in their `## 1`, no
more and no fewer. Every cell is **read**, never assumed:

```text
Sees whose records   own | assigned subset | their unit's | all
                     ground → a BR-### about visibility or permission · the UC's ## 1
                              pre-conditions · how the UC itself defines the actor
How many             one | few (a countable handful) | many (unbounded — it grows with the business)
                     ground → the EN-### relationship cardinality you noted in Part 1 step 4 ·
                              a BR-### stating a cap · a UC step that says so
May act on           read one · act on one · act on MANY at once
                     ground → a UC step or a BR-###. NEVER the volume (see the D8 line below).
```

Nothing on record settles a cell → write the **narrowest** reading, and raise it in `## 6`.
Designing wide and asking afterwards means the client reviews a reach nobody granted, agrees to it,
and it becomes a requirement by default.

Volume is a fact about the **data**, not a guess about the actor. An actor whose scope is `own` over
a one-per-user entity is `one` however senior they are; an actor over an entity the business adds to
every day is `many` however junior.

### The volume band decides the machinery

```text
one     the record itself. NO find machinery — a search box over one record is an invented control.
few     the set, listed whole. No pagination, no search: a filter over nine rows is noise.
many    the set can never be shown whole, so the screen's job becomes FINDING, and it must carry:
          at least one find mechanism   search · filter · sort
          the volume states             empty · few · many at real scale · loading · error
          a density fit                 a table rather than cards, once the set is `many`
        A `many` screen written without them is a design that only works on demo data — it looks
        finished in review and collapses the first time it meets the client's real table.
```

The find machinery and the volume states are **grounded by the volume fact itself**, cited like any
other ground: `EN-004 — many Orders per Account · UC-030 S2`. That is a ground-1 requirement citation
(`design-grounding.md` § Grounding), not an exception to D3.

### D8 — the line volume may not cross

```text
LICENSED by the volume fact          search · filter · sort · pagination or infinite scroll ·
                                     a result count · the volume states · a density choice

NOT licensed by volume, ever         bulk edit · bulk delete · "select all matching this filter" ·
— each is a CAPABILITY               export · an approval, assignment, or status change applied to
                                     many records at once · a saved view · a subscription or alert
    → granted by a UC step or a BR-### → design it, cite that
    → granted by neither              → a REQUIREMENT GAP: an unchecked `- [ ] Q:` in ## 6,
                                        owner: client, marked as a requirement gap. Never a design
                                        call, and never a control on the screen "because an admin
                                        would obviously need it".
```

This is D7's discipline on the data side. An administrator who "obviously needs bulk delete" is the
same failure as an agent that "obviously needs to remember": plausible, unstated, and it reaches the
client looking exactly like something somebody specified. They agree to it in a prototype, and from
that moment it is a requirement nobody wrote, costed, or ruled on — except that this one deletes
five hundred records.

### When one place is two screens

Now run Part 2's merge. Two UCs landing on the same place merge **only when their actors' three
facts agree**:

```text
the VOLUME BAND differs        → TWO screens. A one-record view and an unbounded directory share
                                 nothing but the entity: different regions, different states,
                                 different primary action, different everything the client looks at.
the CAPABILITY differs         → TWO screens. One actor reads their own record; the other works a
                                 queue and acts on what is in it.
both agree, and only WHICH     → ONE screen. Put the difference in the element table's `Visible to`
FIELDS are visible differs       cell, citing the BR-### that restricts it. Do not split.
```

Same discipline as the `Layout — Web` / `Layout — Mobile` split: split what genuinely differs, never
restate one design twice. What it splits on is different — a layout split is **one** design on two
shells; an actor split is **two** designs, because the two actors are not doing the same work.

Two screens means two inventory rows, each with its own `Actor`, its own `Volume`, and a `Serves`
naming only its own actor's UC steps — and names that make the actor legible:

```text
| Screen                 | Actor  | Volume | Serves          |
| My Profile             | Member | one    | UC-012 S1–S3    |
| Member Directory       | Admin  | many   | UC-030 S1–S2    |
| Member Record (Admin)  | Admin  | one    | UC-030 S3–S5    |

NEVER: | Member Record | Member, Admin | — | UC-012 S1–S3, UC-030 S3–S5 |
```

Note the third row: an administrator's *directory* and an administrator's *single record* are still
two screens, by the ordinary Part 2 rule — the actor moved to a different place. Actor scope adds
rows; it never removes the ones Part 2 already found.

**A split is not a licence to invent.** Each new screen still needs its own grounded steps: if you
cannot name the UC steps the administrator's screen delivers, the administrator has no UC here, and
that is an Open Question — not a screen you design on their behalf. A `many` band with no UC step
putting that actor in front of the set is the same gap.

### Screen count, after the split

The Part 2 bands (1–4 screens on `web`, 2–6 on `mobile`, per 3–9-step UC) are **per actor**. A
feature serving two actors with genuinely different scope legitimately lands at twice the count, and
that is the design being right rather than the run being over. What is still wrong is a count that
grew without an actor behind it: every extra screen names an actor in the Actor & Scope table, or it
is invented.

---

## Part 2b — Which of these screens get a nav entry

Most screens in the inventory above are **not** menu items — they are reached by clicking through
from one that is. Read `design-navigation.md` § The navigation map before this part.

```text
per screen in the inventory:
    is it reached ONLY via another screen's control (a detail from a list, a step in a wizard,
    a modal, a confirmation)?                                          → NO entry
    is it something the actor opens directly, on its own, from a menu?  → nav candidate

    for each nav candidate, where does it sit in the tree that already exists?
        joins an existing branch, at whatever depth it lives          → cite that branch (e.g.
                                                                          "under settings.team")
        needs a whole new branch (no existing container fits)         → propose one, grounded the
                                                                          same way a screen is (a
                                                                          UC/BR, an existing branch
                                                                          in {nav_map_file}, or a
                                                                          stated preference) — say
                                                                          how deep it nests and why
        which roles see it                                            → the UC's § 1 actors, or a
                                                                          BR — never guessed
```

Nesting depth is itself a grounded decision, not a default. "Settings → Team → Members" is right
when the UC actually reads as a sub-area of Team; forcing three levels because it looks tidier is an
invented information architecture the same way an invented screen is.

**A feature normally contributes 0–2 nav entries**, not one per screen. Zero is common and correct —
most of a feature's screens are steps inside a flow the actor reaches from the one entry point.

### The shell a candidate joins is a platform fact

```text
web     the tree already in {nav_map_file} — a sidebar / nav-bar shell, arbitrary depth
mobile  a TAB BAR: at most 5 top-level entries, plus per-screen headers and sheets. Depth below a
        tab is still arbitrary.
        a 6th top-level candidate is not a nav decision → report it as an Open Question on the nav
        map (owner: team): either two features share a tab, or one belongs a level down. NEVER a
        silent 6th row.
both    each candidate says WHERE THE FEATURE LIVES ON EACH SHELL — one line per shell, because the
        two shells are two trees: `settings.team` on web and `more.team` on mobile is the same
        feature, correctly named twice.
        an entry on one shell and not the other is NORMAL and grounded (a web sidebar can carry an
        admin area a phone app never surfaces) — say so in its ground. Never mirror an entry onto
        the other shell for symmetry.
```

The five-tab cap is a real constraint, not a style preference: a phone tab bar stops being usable
past five, and which of "two features share a tab" or "one belongs a level down" is right is a human
call, not a default this stage may pick.

---

## Part 3 — One screen spec per screen (`## 3`)

```text
purpose       one line
serves        UC-### S<n> …            every S# must exist and not be removed
actor         the ONE role this screen is for, from ## 1's Actor & Scope table (Part 2a). Two
              actors on one screen is legitimate ONLY when their volume band and capability agree
scope         whose records · how many · what they may do — each cited
              e.g. `all · many (EN-004, many Orders per Account) · read one, act on one (UC-030 S2)`
              many → this screen MUST carry a find mechanism and the volume states (Part 4)
              one  → it must carry neither: there is nothing to find
regions       semantic structure, never a pixel layout — and which regions EXIST is a platform fact:
                web     header · nav · main · aside · footer
                mobile  header · content · tab-bar · sheet · fab
              a `nav` region on a phone screen, or a `tab-bar` on a web one, is the wrong vocabulary:
              it asks the prototype tool to build a shell the platform does not have
elements      per element:
                what it is        heading | table | form field | button | badge | ...
                content/copy      the real words, in the client's language
                role              ONE semantic role, from the closed list in
                                  `design-screens.md` § Semantic style roles — `primary action`,
                                  `danger`, `muted`, … — or BLANK when the element carries no
                                  particular weight. NEVER a hex, a px, a font name, or a
                                  `--token` id (D2): there is no design system here to resolve one
                field             the EN-### field it renders, when it renders one
                visible to        ONLY when a BR-### restricts it to some of this screen's actors
                                  ("Admin only — BR-018"). Blank = every actor of this screen sees
                                  it. Not a place to smuggle in a second actor Part 2a would split
                grounded by       UC-### S<n> | BR-### | EN-### field | PP-### (emphasis/ordering
                                  ONLY — never existence) | pattern <name> | directive #<n>
                                  | the volume fact, for find machinery only
                                  ("EN-004 many-per-Account · UC-030 S2")
states        see Part 4
interactions  control → what happens → which screen or state comes next
```

**Fields come from the entity, not from imagination.** An `EN-###` gives you the field list, the
types, which are required, and an enum's real options — which are the dropdown's real options. An
entity still at `proposed`/`draft` is a **known gap**: use it, and say next to it that the field list
is not settled.

### Roles, and what a pain point may do to a screen

A `role` says what an element is **for**, and a design system maps the ten roles once, later. So the
only judgment here is which of the ten fits — never what it should look like:

```text
the ONE thing this screen exists for       → `primary action`. Exactly one per screen.
it deletes, cancels, or revokes            → `destructive`
it means something is wrong or overdue     → `danger`      (a state or badge, not a button)
it needs attention but is not yet wrong    → `warning`
it must be read first                      → `emphasis`
it is deliberately quiet                   → `muted`       (metadata, timestamps, helper text)
none of the above                          → LEAVE IT BLANK. Most elements are blank.
```

A screen needing a role the list does not carry raises a `## 6` question asking whether the list
should grow. Never invent an eleventh role in one spec: nothing else in the vault can map it.

**A pain point (ground 1b) can move an element, never add one.** `PP-004: "reviewers can never find
what they were working on yesterday"` legitimately puts the in-progress items first, gives them
`emphasis`, and pre-selects that filter — every one of those is ordering and weight on a screen a UC
already asked for, cited as `PP-004` alongside the UC step. What it cannot do is add a "Recent
activity" panel nothing granted: that is existence, it needs ground 1, and without it the pain point
becomes a `## 6` question instead.

### On `both` — shared behaviour, then a layout split only where they differ

Purpose, serves, elements, states, and interactions are the **same design** on both platforms: the
same words, the same entity fields, the same states, the same next screens. Only the layout differs,
and only sometimes. Write the behaviour once, then split what actually differs:

```text
### <Screen name>
purpose       one line                                                  ← shared
serves        UC-### S<n>, S<n>                                         ← shared
elements      what it is · content/copy · role · field · visible to · grounded by
                                                                        ← shared, ONE table
states        one row per reachable state (Part 4)                      ← shared, ONE table
interactions  control → what happens → next screen or state             ← shared, ONE table

the split REPLACES the single regions line, and touches nothing else:
Layout — Web      header · nav · main · aside
                  <only what differs — list and detail side by side, filters in the aside>
Layout — Mobile   header · content · tab-bar
                  <only what differs — list screen, detail on tap, filters in a sheet; a step that
                   needs several surfaces here → the sheets, named, in order>

no real layout difference → NO split. Keep the one regions line, naming the shared structure in
each platform's own vocabulary:
regions       header · main (web) / header · content (mobile)
```

A split that restates the shared block in other words is noise — and it is the first place the two
platforms drift. Split what differs; never say the same thing twice.

---

## Part 4 — States, and where each one comes from

Every screen gets the states it can actually reach. Each traces to something:

| State | Comes from |
|---|---|
| empty | a list/table whose source can legitimately be empty |
| loading | any screen that waits on the system — one per screen, not per element |
| validation-error | a `BR-###`, or an entity's required/format constraint |
| permission-denied | a `BR-###` about who may do this, or the UC's `## 1` actors |
| failure | an `E#` exception flow — one state per exception, named after it |
| success | the UC's `## 1` success post-condition |

**On a screen whose volume band is `many` (Part 2a), the set below is required, not optional** — the
volume fact grounds every one of them, cited the same way (`EN-004 many-per-Account · UC-030 S2`).
Its `empty` and `loading` rows are the **same two states** as the table above, written with what a
large set specifically has to show — they replace those rows, they do not sit beside them:

| State | What it must show |
|---|---|
| empty | the set is genuinely empty — first use, or a filter that matched nothing. Say which |
| few | a handful of records: the layout still has to read well at three rows |
| many, at real scale | **the real number**, named — "≈10,000 records, page 1 of 400". Not "several" |
| loading | the set is being fetched or a filter is being applied |
| error | the set could not be loaded — distinct from empty, and the user can retry |

The `many` row exists so the prototype gets seeded with a real number instead of three rows of
sample data. A list that was only ever reviewed at three rows hides every problem the client
actually has: what the density is, whether the find machinery is reachable, what the column widths
do, and whether the page is usable at all.

A state with no source is invented. Leave it out, or ask.

---

## Part 4b — The relationship model (`## 7`), on the few features that earn one

Most features do not. Run the trigger test; on a miss, **delete `## 7` from the spec** and move on —
an empty `## 7` claims the relationship was considered when nobody looked. Read
`design-review.md` § The relationship model before writing anything here.

### The trigger — three tests, all three from sources you already read in Part 1

```text
1  the SYSTEM JUDGES, it does not just process
     a ## 2 or ## 3 step where the system suggests, recommends, predicts, scores, ranks, drafts,
     or decides on the actor's behalf
     NOT: "the system validates" · "the system saves" · "the system sends" · "the system displays"

2  it PERSISTS something about THIS user, between sessions
     an EN-### field holding per-user history, preference, pattern, score, or learned model
     NOT: an audit log · a status field · a created/updated timestamp · a role or permission

3  the relationship REPEATS
     the UC's ## 1 trigger recurs for the SAME actor — a queue they work daily, an assistant they
     come back to
     NOT: a one-off application, signup, purchase, or onboarding

3 of 3    → MODELLED.  write ## 7, set relationship_model: modelled
any miss  → NONE.      delete ## 7, leave relationship_model: none, and name the failed test in
                       your report — a near-miss is worth a human seeing
```

Test 2 is the one that does the work. A screen with a chatbot on it, an "AI suggestions" panel fed
by nothing stored, or a report the system ranks the same way for everyone all fail it — and none of
them has a relationship to model. **Never pass a test on a plausible reading**: the step verb, the
entity field, and the trigger are either there or they are not.

### What you write, and what grounds it

Four sub-blocks (the template carries the tables). Every row is grounded per `design-grounding.md` § Grounding or it is
not a row:

```text
Relationship Context   duration · frequency · the AUTONOMY CEILING · memory sensitivity
                       ← a UC trigger/post-condition, a BR, an active principle row, a directive
                       "not stated" is a real value → a requirement gap in ## 6. Never a plausible
                       number: "users return weekly" invented here becomes a fact downstream.

Memory Architecture    what it carries between sessions · WHICH EN-### FIELD holds it · which
                       screen surfaces it · who may see, correct, or clear it
                       ← the entity field, ALWAYS. No field → not a row, a requirement gap.

Trust Map              per screen or per agent decision: what it SHOWS vs what it DOES at stage 1
                       (transparent) / 2 (selective) / 3 (autonomous), and the correction path
                       ← a BR about who may do this, a confidence/threshold rule, or an E-flow
                       Only fill a stage a BR actually GRANTS (D7). An unfilled stage 3 is the
                       correct answer when nothing granted autonomy.

Proposed Measures      at most THREE, owner team, each naming what would be observed and which row
                       above it tests. Never a requirement, never a target, never a screen.
```

A trust stage is **not** a state. `## 3`'s States table is within one session (empty, loading,
error, success). A trust stage is the same screen at relationship month 1 versus month 12 — put it
in `## 7` and, where it changes what a screen shows, note the stage next to that element in `## 3`.

### The guardrail — this is where an agentic run goes wrong

An installed relationship-UX skill hands you a pattern catalog: memory dashboards, goal dashboards,
planning canvases, preference-evolution maps, contextual timelines. Those are **whole screens**, and
they arrive with a citation, which makes an invented screen look designed.

```text
an external pattern is ground 2b (`design-grounding.md` § Grounding) — it shapes HOW something already grounded is built.
it can NEVER ground THAT a screen, field, or state exists.

"the relationship-UX skill recommends a memory dashboard"     → not a ground. Not a screen.
"UC-014 S3: the reviewer checks what the assistant learned"    → a ground. Now design that screen,
                                                                 and use the catalog for its shape.
```

Same test as Part 2's: **never invent a screen the flow never asked for**, however good the pattern.

### The gaps are the deliverable

A UC almost never states an autonomy ceiling, a retention rule, or who owns the memory. So a real
agent feature produces **more requirement gaps here than design rows** — that is this section
working, not failing. Each one goes in `## 6`, marked `requirement-gap`, and belongs to
`/bigin-transform-signal`. Write none of them onto the UC (D4).

The recurring five, all requirement gaps whenever unanswered:

```text
what may the agent do WITHOUT asking, and above what confidence?   → autonomy. A BR, or a gap.
how long is this remembered, and can the user clear it?            → retention. A BR, or a gap.
who else can see what it learned about this user?                  → visibility. A BR, or a gap.
what happens when it is WRONG — who is accountable, what is undone? → an E-flow, or a gap.
does the user know it is learning from them?                        → disclosure. A BR, or a gap.
```

## Part 4c — The flows, and the pain points they resolve

The screens are *what exists*; a flow is **how a real person gets from a trigger to an outcome**. It
is the artifact a client recognises as their working day or fails to, which is why it gets its own
part rather than being written as an afterthought at the end. Read `design-navigation.md` § User flows and pain points before this part.

```text
ONE flow per user goal, per ACTOR — never one per platform, never one per screen
    Entry        the trigger, in plain words
    Path         the screens in order
    Success      what the user is left with
    Failures     each exception → the screen or state the user is left on
    Resolves     the PP-### this journey fixes, or "—" when it serves a UC goal alone
    Steps to     how many screens the actor passes through from trigger to success
    goal
```

### D6 — a flow resolves something stated

```text
it delivers a UC's ## 2, end to end       → sufficient on its own. Every UC in scope gets a flow.
it also fixes a PP-### from Part 1 step 5 → NAME IT in `Resolves`. This is the flow saying why the
                                            journey is shaped this way rather than another way that
                                            also delivers the steps
it does neither                            → it is not a flow. It is an invented journey, and it is
                                            an Open Question in ## 6, not a row here
```

**Every open pain point on this feature's hub gets an answer here — including "no".** A `PP-###` no
flow resolves is a `## 6` question (owner: client, marked as a requirement gap when fixing it would
change what the system does), never a silent omission: `5-verify` matches every open pain point
forward to its flow, and an unanswered one surfaces there as a gap with this feature's name on it.

**Never mark the register.** `PAIN-POINTS.md` and the hub's `## Pain Points` are read-only from here
(`design-core.md` § Write map). The flow names the id; `/bigin-transform-signal` is what closes
the row.

### Two actors, two flows

The same rule Part 2a applies to screens applies to journeys. A member checking their own record and
an administrator working a directory of ten thousand are not on one journey with a filter bar in the
middle — they are two flows, each naming its own actor, each with its own `Steps to goal`.

### On `both`, still one flow

A phone that splits one web form into three sheets is carrying the **same journey across more
surfaces**. Say so inside the `Path` line — `web: Details → Confirm · mobile: Details → Reviewers →
Confirm` — never as a second flow. Two flows for one goal is two journeys to keep in sync, and the
second is wrong the first time a UC changes.

### `Steps to goal` is a number you write down, not a target

Count the screens between trigger and success and record it. It is not a budget and there is no
right value — a five-step approval that a BR requires is five steps. It exists so `4-flow-review`
has something to compare a journey against, and so a human reading two flows can see that one of
them takes four times as long as the other for no reason anybody wrote down.

## Part 5 — When you do not know

```text
grounded in a requirement | an existing pattern | a stated preference   → design it, cite the ground
grounded in none of the three                                          → ASK. Never guess. (D3)
```

Write the question on the UX spec's `## 6`:

```text
- [ ] Q: <self-contained, plain business language> (owner: client|team) (ref: UX-###)
      A:
```

```text
the answer changes how it LOOKS/FLOWS        → a design question. Owner: client (or team).
a PLATFORM question — which shell a feature  → a DESIGN question too. Owner: client (or team).
belongs on, whether a flow really works on a   It changes the SHAPE, not what the system does,
phone, whether a 6th tab or a shared one       so the UC stays platform-blind either way (D4).
a PAIN POINT no flow can resolve as the      → say which PP-### and why. It is a design question
requirements stand                             when a different journey would fix it; a REQUIREMENT
                                               GAP when nothing the system does today can.
the answer changes what the system DOES      → a REQUIREMENT GAP. Say so in the question,
                                               report it, and let /bigin-transform-signal own it.
                                               Do NOT write it onto the UC yourself (D4).
already open on the UC's ## 5                → do not re-ask it. It is already a known gap.
```

Two or three real questions per feature is healthy. Twenty means questions are being manufactured;
one means grounding is being skipped.

---

## Part 6 — Write the file

```text
no UX spec for this feature  → create {ux_dir}/UX-<NNN> <Feature>.md from {template_ux}
                               (the orchestrator gave you the number — never mint your own)
one already exists           → UPDATE IT IN PLACE: bump version, append a ## Changelog line
                               naming the UCs this run designed. Never create a second one.
```

Write `## 4 Flows` from Part 4c: per user goal, per actor — entry, path, success, failures,
`Resolves`, and `Steps to goal`. It mirrors the UC's own flow without restating its step text.

Leave `## 5 Navigation & Flow Review` with its nav rows filled and its **Flow Review table empty** —
`4-flow-review` writes those verdicts, and a worker that pre-fills them has reviewed its own work.

Set `platform:` in the frontmatter to the value you designed to — the dispatched one, or the
per-feature override — and write the same value on `## 1`'s `Platform` line, with the override's
ground cited there. One value, two places, never two answers.

Set `actors:` in the frontmatter from `## 1`'s Actor & Scope table — one entry per row,
`"<role>:<own|assigned|unit|all>:<one|few|many>"`. It is the parseable form of that table: the same
rows, in the same order, and never a role the table does not carry.

Set `relationship_model:` from Part 4b — `modelled` with `## 7` filled, or `none` with `## 7`
deleted. An **existing spec created before `## 7` existed** simply has no such section: add it if the
trigger passes now, and otherwise leave the spec without it (§ Adopting an existing UX spec below).

Leave `status: draft`. Leave `absorbed:` **empty** — the orchestrator stamps it in Stage 6, after it
has checked which UCs really got screens.

---

## Part 7 — Report, do not write

```text
DO NOT WRITE   {nav_map_file} · another feature's UX spec or hub · DESIGN-PRINCIPLES.md
               PAIN-POINTS.md or a hub's ## Pain Points · any UC, BR, or entity · FEATURES.md
REPORT INSTEAD nav candidates · cross-feature screens · unresolved pain points
```

Report lines:

```text
feature:            <slug>
platform:           web|mobile|both — source: dispatched (project config)
                    | override: <UC-### S<n> | hub directive #<n> | DESIGN-PRINCIPLES row #<n>>
ux:                 UX-### created|updated  — <N> screens (<N> new, <N> updated)
screens:            <screen> serves UC-### S<n>, S<n>  (one line each)
                    actor: <role> | volume: one|few|many <(the real number, when many)>
                    regions: <the platform's vocabulary, as specced>
                    on both, add: layout split web|mobile|none — <what differs, in a phrase>
flows:              <goal> | actor: <role> | path: <screen> → <screen> | steps to goal: <N>
                    | resolves: PP-### | — (one line each)
pain_points:        PP-### | resolved by flow: <goal> | or: NOT RESOLVED — question raised
                    (one line per open PP-### on this feature's hub; "none open" is a real result)
actor_scope:        <actor> | sees: own|assigned|unit|all | volume: one|few|many
                    | may: read one|act on one|act on many | grounded by: <BR-### | UC-### S<n> |
                      EN-### cardinality>   (one line per actor in ## 1's table)
actor_splits:       <place> → <screen A> (<actor>, <band>) + <screen B> (<actor>, <band>)
                    | split on: volume|capability   (one line each; "none" when nothing split)
capability_gaps:    <the unstated bulk/export/saved-view affordance> | asked for by: <what suggested
                    it> | NOT designed — requirement gap raised   (one line each, D8)
roles_used:         <role> | on: <screen> · <element> (one line each, from the closed list)
role_gaps:          <what needed a role the list does not carry> | on: <screen> | question raised
                    (one line each, or "none")
nav_candidates:     <entry label> | shell: web|mobile (one line per shell on both)
                    | parent: <existing id it nests under, or "new: <path>", or "top-level">
                    | points to: <screen> | role(s): <actor(s)>
                    | grounded by: <UC-### S<n> | BR-### | pattern <name>>
                    | tab-bar cap: <"6th top-level candidate — Open Question, owner team", when hit>
directives_reflected: hub row #<n> → <screen>  (one line each — only rows a screen really implements)
relationship:       modelled | none — <the test that failed, when none: judges|persists|repeats>
relationship_rows:  context <N> | memory <N> | trust <N> | measures <N>   (omit when none)
questions:          <the question>, owner client|team, kind: design|requirement-gap
designed_ucs:       UC-###@<version>  (one line each — ONLY UCs that really got screens)
blocked:            UC-### — <why, one line>
```

**The orchestrator's next move is `4-flow-review.md` and then `5-verify.md`, on what you actually
wrote.** It re-reads your spec
from disk and matches every in-scope requirement item forward to the screen and state that carries it.
So a screen that really serves `S4` must *say* it serves `S4` — an under-recorded `Serves` cell is
repaired there, but a step you skipped becomes an Open Question with your feature's name on it. The
same is true of a pain point: an open `PP-###` no flow's `Resolves` names surfaces as a gap.

**Your flows will be reviewed and may be reordered.** `4-flow-review` can change a flow's screen
order, re-point an interaction, re-nest a nav entry, and re-word copy that misleads — all in place,
all changelogged. Write the journey you actually believe is right; do not pre-empt a critique by
padding it, and do not leave a flow thin on the theory that something later will fix it.

Report what you designed; do not report coverage you did not write down.

## Failure modes

- **Inventing a screen the flow never asked for.** The most expensive mistake here: it reaches a
  client as if someone had specified it.
- **Promoting every validation to its own screen.** A ten-screen spec for a five-step flow.
- **Writing `#2563eb`, `16px`, or `--color-action-primary` into a spec.** All three are D2 broken,
  and the last one worst: it cites a design system this vault does not have, so it resolves to
  nothing and a renderer quietly picks its own. Name a semantic role, or leave the cell blank.
- **Inventing an eleventh role.** The ten are a closed list precisely so one mapping covers the
  vault. A private role is a one-screen vocabulary nobody downstream can resolve — ask instead.
- **Giving a screen two `primary action` elements.** The role means "the one thing this screen
  exists for". Two of them means the screen is two screens, or one of the two is secondary.
- **Making up form fields.** The entity has the fields. If it does not, that is a question.
- **Re-asking a question the UC already has open.** The human answers it twice and the copies drift.
- **Creating a second UX spec for a feature that has one.** The review splits and both go stale.
- **Writing the nav map from here.** Two features run at once; the second write loses.
- **Writing a flow that resolves nothing.** D6. A journey nobody asked for reads exactly like one
  somebody did, and a client walks it in a prototype believing it was specified.
- **Leaving an open pain point unanswered.** Every open `PP-###` on the hub gets a flow that names
  it or a `## 6` question saying why none does. Silence reads as "considered and fine" — and
  `5-verify` will surface it anyway, one stage later, with less context to fix it in.
- **Letting a pain point add a screen.** Ground 1b shapes ordering, emphasis, and defaults on a
  screen a UC already asked for. A "recent activity" panel grounded only in `PP-004` is an invented
  screen carrying a citation, which reviews as designed where a bare guess would have been caught.
- **Marking a pain point resolved.** The register is read-only here. Name the id in the flow and
  stop; `/bigin-transform-signal` closes the row.
- **Writing two flows for one goal on `both`.** The phone splitting a form into sheets is the same
  journey on more surfaces — one flow, the split inside its `Path`.
- **Filling the Flow Review table.** `4-flow-review` writes those verdicts. A worker that grades its
  own journeys has produced a review with nothing independent in it.
- **Proposing a nav entry for a screen reached only through another screen.** It reads as a second
  door into the same room, and the two drift the first time one changes.
- **Nesting a nav entry three levels deep because it looks tidier.** Depth is grounded like anything
  else; an ungrounded sub-group is an invented IA.
- **Writing `## 7` because the feature has AI in it.** The trigger is three mechanical tests, and
  test 2 — a real `EN-###` field holding per-user history — is the one that fails most often. A
  relationship model over nothing stored describes a relationship the system cannot have.
- **Letting a pattern catalog ground a screen.** A memory dashboard nobody asked for reaches the
  client carrying a citation, which is worse than an obvious guess: it reads as specified.
- **Filling a stage-3 autonomous cell no `BR-###` granted.** The prototype then shows the agent
  acting alone, the client sees it working, and nobody ever decided it was allowed (D7).
- **Inventing a retention or frequency figure.** "Cleared after 90 days", "users return weekly" —
  written here, they are quoted downstream as though a client said them.
- **Leaving `## 7` in place, empty, on a feature that failed the trigger.** It reads as "we looked
  and there is no relationship here" when the opposite is true.
- **Using the web regions vocabulary on a mobile screen, or the phone one on a web screen.** A `nav`
  region on a phone, a `tab-bar` on a desktop — the prototype prompt then asks a tool to build a
  shell the platform does not have.
- **Inferring a platform from step wording instead of using the dispatched value.** "The courier is
  out on the road, so this is mobile" is a guess wearing a rationale. The override bar is an explicit
  statement; anything less is an Open Question.
- **Splitting the screen inventory per platform on `both`.** Two inventories, two designs to keep in
  sync, and the second one is wrong the first time a UC changes. One inventory, layout split inside
  the row.
- **Multiplying phone screens past what the flow states.** Sheets are how a stated step is split
  across surfaces, not a licence for surfaces no step asked for — the same invented screen, arriving
  under a mobile justification.
- **Adding a 6th tab.** The cap is physical, not stylistic. A 6th top-level candidate is an Open
  Question on the nav map, owner team — never a silent row.
- **Merging two actors onto one screen because their steps land in the same place.** The single
  most common way this stage ships a wrong design: a member reading their own record and an
  administrator working ten thousand of them become one `Member Record` screen, and whichever actor
  the prototype renders for, the other one got a product that does not fit their job. Compare the
  three facts before merging (Part 2a).
- **Designing a `many` screen with no find machinery.** No search, no filter, no pagination, and a
  list state that only ever shows three sample rows. It reviews as finished and collapses on the
  client's real table — and nothing else in the run catches it, because every element on it is
  properly grounded.
- **Seeding the `many` state with three rows.** The state exists to test density, reachability, and
  column behaviour at real scale. "Several records" tests none of them; name the real number.
- **Adding bulk delete, export, or a saved view because an admin would obviously want it.** D8. It
  is a capability, not machinery: unstated means a requirement gap in `## 6`, owner client — never a
  control on the screen. The client agrees to it in the prototype and it becomes a requirement
  nobody wrote, and this one deletes five hundred records.
- **Guessing a scope cell to avoid a question.** Writing `all` where no BR grants it hands an actor
  reach nobody approved. Unresolvable → the narrowest reading, plus the question.
- **Inventing an actor.** Actor scope reads the actors the UCs already name and asks three questions
  about each. A "power user", a job title, or a seniority nobody wrote down is a persona — and a
  screen designed for one is invented scope with an invented owner.
- **Splitting a screen the client will never see split.** Two actors with the same volume band and
  the same capability, differing only in which fields they see, are ONE screen with a `Visible to`
  cell. Two near-identical specs drift the first time a shared element changes.
- **Stamping `absorbed:` yourself.** Stage 6 stamps it, after verifying the screens exist.

## Adopting an existing UX spec

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

Every spec self-heals on the next design run of its feature. A spec whose feature is never redesigned
keeps working — nothing downstream requires `## 7`, a `Platform` value, an Actor & Scope table, a
`Role` column, or a `Resolves` cell to exist. `/bigin-render-design-od` reads whichever shape it finds
and reports what it could not resolve rather than halting.
