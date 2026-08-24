# Stage 5 — The prototype prompts: blocks that stand alone

```text
runs: orchestrator, after Stage 2 Part B has finalised every token name and Stage 4 has verified
      coverage and render readiness
in:   the UX spec's screens, states, flows, copy + the design system's real values + the nav map
      + the platform, as Stage 1 announced it (never re-read from the project config here)
out:  this platform's prompt blocks — 2 on `web`, 2 on `mobile`, 4 on `both`
never: a vault id inside a prompt body · a prompt that says "see the use case" · a concrete engine
       name anywhere in this file · a render — /bigin-render-design owns that, on a human's schedule
```

Read `{design_conventions}` § Prototype prompt, § Platform, and § Actor scope first, and
§ The relationship model when this spec's `relationship_model:` is `modelled`.

**Every block this platform calls for, every run.** The BA pastes whichever tool they have open —
and, on a two-platform product, whichever platform they are showing the client. So the count is a
platform fact, not a judgement call:

```text
platform: web     2 blocks   ## Prototype Prompt — Claude design (Web)
                             ## Prototype Prompt — Figma Make (Web)
platform: mobile  2 blocks   ## Prototype Prompt — Claude design (Mobile)
                             ## Prototype Prompt — Figma Make (Mobile)
platform: both    4 blocks   all four of the above
```

Same screens, same states, same tokens, same copy in every one of them. Two axes may differ and only
two — **by tool** (a builder wants behaviour and working HTML; a design tool wants frames, components,
variants) and **by platform** (the shell and the viewport). Nothing else. A screen present in one
block and missing from another, or copy reworded "because it's a phone", is the failure this stage
exists to prevent: whichever block the BA pastes, the others silently become wrong.

**This stage does not render, and this file names no design engine.** The blocks are the durable,
tool-portable record; turning one into something a client can look at is `/bigin-render-design`, a
separate skill a human invokes when they want it, on whichever engine they choose. So nothing here
halts for a missing tool, nothing here checks an install, and no engine has a name in this file — its
catalog, install commands, and brief→input mappings live in that skill's own
`references/design-engines.md`. A stage guide that hardcoded a tool name is the thing that makes the
next swap expensive.

**Which is exactly why the blocks are written every run, unconditionally.** Nobody may ever render
this feature, or they may render it in six months on a tool that does not exist today. The block is
what survives that: reproducible by hand, in any tool, from the words in it alone.

## Part 1 — De-identify

The prompt goes into a tool that has never seen this vault. Every id must become words.

```text
UC-012 S4     → "the step where the reviewer approves the request"
BR-007        → "a request over £5,000 needs a second approver"
EN-003.status → "the request's status: draft, submitted, approved, or rejected"
EN-009.reviewer_pattern → "what the assistant has learned about how this reviewer decides"
UX-002        → delete it. The prompt does not need to name itself.
the Actor & Scope table → words, not cells: "this screen is for an administrator, who can see every
                member in the organisation — about 10,000 of them"
"volume: many (EN-004)" → "the list holds roughly 10,000 records and grows every day"
INT-014       → delete it. Never put a client's meeting id in a prompt.
--color-action-primary: #2563eb   → keep BOTH: the name AND the value
```

`{nav_map_file}`'s entry labels and group names are already plain words — carry them in as-is, no
de-identification needed. Pull only the groups/entries these screens actually touch, never the whole
vault-wide map (a feature's prototype does not need every other feature's menu items). On `both`,
pull from `## Structure — Web` for a web block and `## Structure — Mobile` for a mobile one; the two
shells are two trees, and mixing them produces a prompt asking for a shell the platform does not have.

Grep your own draft for `UC-`, `BR-`, `EN-`, `PP-`, `UX-`, `INT-`, `PRD-`, `S1`…`S9`, `A1`, `E1`
before writing it. A hit is D6 broken. Grep **every** block, not the first one you wrote.

## Part 2 — What goes in, in this order

```text
1  what it is        one paragraph: the product, the user, what this part of it does
                     — and, when the block covers screens for MORE THAN ONE actor, say plainly who
                     each screen is for and how much they see. A tool told only "a member record
                     screen" builds one screen; told "one screen where a member sees their own
                     record, and a separate screen where an administrator searches all 10,000",
                     it builds the two the spec actually describes
2  the look          every token: name, value, and a plain-language note
                     ("action primary #2563eb — the colour every main button uses")
3  the navigation    the persistent shell these screens live inside — WHICH shell is a platform fact:
                     web:    the persistent sidebar / nav-bar shell — which entries (this feature's
                             own, plus any sibling entries needed for orientation), and which screen
                             each one opens
                     mobile: the bottom tab bar (at most 5 entries), the header each screen carries
                             for itself, and which destinations open as SHEETS rather than pages
                     either way the point is identical: the tool builds ONE shell, not one per screen
                     it improvises. On `both`, each platform's block carries ONLY its own shell —
                     never both, never a web sidebar relabelled as tabs
4  the screens       one block per screen: WHO IT IS FOR and how many records they are looking
                     at, then purpose, regions, elements, real copy. Regions come from
                     the platform's vocabulary (web: header/nav/main/aside/footer; mobile:
                     header/content/tab-bar/sheet/fab). A mobile block states the frame it builds in
                     BEFORE the first screen: a 390px-wide phone frame (390×844 for a design tool),
                     safe-area insets top and bottom, touch targets no smaller than 44×44, one
                     primary action per screen, sheets where desktop would use a modal
5  the flow          screen order, and what each button leads to
6  the states        per screen: empty, loading, error, permission, success — what each says
                     on a `many` screen, add the volume states from `## 3`: empty, a few rows, and
                     the full set at real scale. The empty and the loaded-at-scale states are the
                     two a client argues about, and a happy-path-only prototype shows neither
7  the data          realistic sample data per list, real field names from the entity — and the
                     ROW COUNT COMES FROM THE SCREEN'S VOLUME BAND (`## 3`'s Scope line):
                       one   the single record, filled in
                       few   the real handful — 3-5 rows
                       many  say the REAL SCALE in words and render the page at it: "about 10,000
                             records; show the first page of 50 with a result count and pagination
                             reading page 1 of 200". A `many` list seeded with 3 rows is the single
                             most misleading thing a prototype can show — the density, the find
                             controls, and the column behaviour are exactly what the client needs
                             to look at, and all three only appear under load
8  the rules         the behaviour the screens must show, in plain words (from the BRs)
9  what NOT to build anything out of scope that a tool would otherwise helpfully add
10 the relationship  ONLY when this spec's relationship_model: is `modelled` — from ## 7:
                     what the system remembers about the user, what it does on its own, and how
                     the user corrects or clears it. Omit the whole item otherwise.
```

Item 8 is the one people skip and the one that saves the most time.

**Items 3 and 4 are where the platform lives, and nowhere else.** Items 1, 2, 5, 6, 7, 8, 9, and 10
are the same words in every block a run writes. If a platform difference is leaking into the flow, the
states, the data, or the rules, that is a requirement difference wearing a design costume — and a UC
never forks per platform (`{design_conventions}` § Platform, D4).

**Actor scope multiplies SCREENS, never BLOCKS.** A feature serving two actors with different
scope has more screens in its inventory, and every one of them goes in the same block. The block
count stays a platform fact — 2 on `web` or `mobile`, 4 on `both` (§ Prototype prompt, Stage 6
check 8). A per-actor prompt block is a fifth artifact nobody maintains, and the moment one screen
changes the others are silently wrong.

**Never put a capability in a prompt that `## 3` does not carry.** A tool handed "a table of 10,000
members" helpfully adds select-all checkboxes, a bulk-actions bar, and an export button — and the
client reviews a prototype granting an administrator powers nobody specified (D8). Item 9, *what NOT
to build*, is where those go, by name: "no bulk selection, no export, no saved views — acting on
many records at once has not been specified."

**Item 10 is why an agent feature gets prototyped as an agent feature.** Without it the tool builds a
stateless chatbot: every screen starts from nothing, no suggestion has a reason behind it, and nothing
shows what the system knows. That is the same failure as dropping the states, one level up — the
client reviews a prototype missing the only thing that made the feature interesting.

```text
carry in from ## 7    what it remembers, in plain words + which screen shows it
                      what it does unprompted, and what it only suggests
                      the correction path: how a user fixes or clears what it learned
leave out             the trust STAGES as a timeline. A prototype is one moment, not twelve months —
                      build the stage the requirements actually granted, and say which one it is.
leave out             the Proposed Measures. They are team measurement, not a screen.
never invent          a memory, an autonomous action, or a retention promise ## 7 does not carry.
                      A prompt is the one artifact a client sees running (D7).
```

## Part 3 — Claude design blocks

Prose, addressed to a builder. It produces working HTML, so tell it about behaviour and states. Write
the block for each platform in scope — on `both`, both of them, sharing every word except the shell
and the frame.

### Web

```markdown
## Prototype Prompt — Claude design (Web)

Build a clickable prototype of <what it is>, as a desktop web app at browser width.

**Design system** — use these values everywhere, never anything else:
- <token name> — <value> — <what it is for>
...

**Navigation** — a persistent sidebar / top nav-bar shell wraps every screen below; build it once as
the app shell, not per screen. Indent to show nesting (a sub-item sits under its parent; a parent with
no screen of its own is a header only):
- <top-level item> → <screen, or "—" if it only opens a submenu>
  - <nested item> → <screen>
    - <nested-nested item> → <screen>
- <top-level item> → <screen>

**Screens** (build all <N>):
### <Screen name>
For: <who this screen is for, in plain words — "an administrator", "a member looking at their own
     record". Omit ONLY when every screen in the block serves the same one person>
Shows: <how much they are looking at — "their own record" / "the twelve requests assigned to them" /
       "all ~10,000 members, first page of 50 with a result count reading page 1 of 200">
Purpose: <one line>
Layout: <regions — header / nav / main / aside / footer> at desktop width, inside the persistent shell
Contains: <elements, with their real copy>
States: <state> — <what the user sees and reads>
Actions: <control> → <where it goes>

**Flow:** <screen> → <screen> → <screen>, and <control> → <the failure screen/state>

**Sample data:** per screen, AT ITS REAL SCALE — the single record filled in for a screen showing
one; the real handful for a few; and for a large set, say the number and render the page at it
("about 10,000 members — show the first page of 50, a result count, and pagination reading page 1
of 200"). Never three sample rows for a list that really holds thousands: the density, the find
controls, and the column behaviour are exactly what this prototype exists to show.

**Rules the prototype must show:** <plain-language rules>

**What the system remembers about the user** (only when `relationship_model: modelled`; build this
as real state carried between screens, not as static text):
- <what it remembers, in plain words> — shown on <screen> as <the element>
- It acts on its own for: <the autonomous action the rules actually granted>
- It only suggests, never acts, for: <the rest>
- The user corrects or clears it by: <the correction path>

**Do not build:** <out of scope>
```

### Mobile

```markdown
## Prototype Prompt — Claude design (Mobile)

Build a clickable prototype of <what it is>, as a phone app, rendered inside a single 390px-wide phone
frame centred on the page. Nothing lives outside that frame — no desktop chrome, no side-by-side
panels, no stretched full-width layout.

**Frame and touch rules** — these apply to every screen below:
- the app renders inside a 390px-wide phone frame; no element spans wider than the frame
- respect safe-area insets: keep content clear of the status-bar area at the top and of the tab
  bar / home-indicator area at the bottom
- every tappable control is at least 44×44, with at least 8px of separation from its neighbours
- one primary action per screen; everything else is secondary or lives in the header
- anything that would be a modal on a desktop is a bottom sheet here: it slides up over the
  content, keeps the tab bar visible, and dismisses downward
- the content area scrolls; the header and the tab bar stay put

**Design system** — use these values everywhere, never anything else:
- <token name> — <value> — <what it is for>
...

**Navigation** — a bottom tab bar, built ONCE as the app shell and shared by every screen, never
rebuilt per screen. At most 5 tabs; anything deeper is reached through a tab, not added as a sixth:
- <tab label> → <screen>
- <tab label> → <screen>

Each screen carries its own header: <the title it shows>, plus a back control on any screen reached
from another one.

Opened as a sheet rather than a tab or a page:
- <destination> → from <the control on which screen>

**Screens** (build all <N>):
### <Screen name>
For: <who this screen is for, in plain words — the same words the Web block uses>
Shows: <how much they are looking at — the same scale the Web block states>
Purpose: <one line>
Layout: <regions — header / content / tab-bar / sheet / fab> inside the 390px frame
Contains: <elements, with their real copy>
Primary action: <the one thing this screen is for>
States: <state> — <what the user sees and reads>
Actions: <control> → <where it goes, and whether it pushes a screen or opens a sheet>

**Flow:** <screen> → <screen> → <screen>, and <control> → <the failure screen/state>

**Sample data:** per screen, AT ITS REAL SCALE — the single record filled in for a screen showing
one; the real handful for a few; and for a large set, say the number and render the page at it
("about 10,000 members — show the first page of 50, a result count, and pagination reading page 1
of 200"). Never three sample rows for a list that really holds thousands: the density, the find
controls, and the column behaviour are exactly what this prototype exists to show.

**Rules the prototype must show:** <plain-language rules>

**What the system remembers about the user** (only when `relationship_model: modelled`; build this
as real state carried between screens, not as static text):
- <what it remembers, in plain words> — shown on <screen> as <the element>
- It acts on its own for: <the autonomous action the rules actually granted>
- It only suggests, never acts, for: <the rest>
- The user corrects or clears it by: <the correction path — reachable from the phone shell, not a
  settings page that does not exist>

**Do not build:** <out of scope>
```

The two blocks differ in exactly three places: the opening sentence's frame, the **Navigation** shell,
and each screen's `Layout:` line (plus the mobile block's frame-and-touch preamble and its
`Primary action:` line, which are the frame rule written out). Every screen name, every state, every
word of copy, every token, every rule, every sample row is identical.

## Part 4 — Figma Make blocks

Same content, tightened for a design tool: frames, components, and variants rather than behaviour.
Figma Make is authored here in **both** modes — it previews mobile natively at 390×844, so a mobile
prototype needs a different prompt, not a different tool.

### Web

```markdown
## Prototype Prompt — Figma Make (Web)

Create a <N>-frame desktop web prototype of <what it is>. Frames are desktop width (1440 wide).

**Styles** (create these as variables first):
- Colour: <name> = <value> — <use>
- Type: <name> = <size/weight> — <use>
- Spacing: <name> = <value>

**Components** (build once, reuse):
- <component> — variants: <list> — states: <list>

**Navigation** — the persistent sidebar / top nav-bar shell: build it once as a shared
frame/component and reuse it on every frame. Indent to show nesting — a parent item with children but
no frame of its own opens a submenu, not a screen:
- <top-level item> → frame <N>, or "opens submenu" if it has no frame of its own
  - <nested item> → frame <N>
- <top-level item> → frame <N>

**Frames:**
1. <Screen name> — for <who> — showing <how much: their own record / all ~10,000, page 1 of 200>
   — <layout in one line, in web regions: header / nav / main / aside / footer, inside
   the persistent shell> — contains <elements with copy>
   Variants: <state frames — a large set needs its empty, its loaded-at-scale, and its loading one>
...

**Prototype links:** <control on frame N> → frame M

**Content:** use this copy and data verbatim: <copy + rows AT THE REAL SCALE stated per frame —
a frame showing a large set says the real number and is drawn full, not with three placeholder rows>

**What the system knows about the user** (only when `relationship_model: modelled`; these are frame
variants, not separate screens):
- <screen> — variant "first visit" (nothing learned yet) and variant "returning" (<what it knows>)
- The suggestion element shows: <its reason, in plain words>
- The correction control: <what it says> → <what the user gets back>

**Do not add:** <out of scope>
```

### Mobile

```markdown
## Prototype Prompt — Figma Make (Mobile)

Create a <N>-frame mobile prototype of <what it is>. Every frame is a phone frame at **390×844**,
mobile-first viewport — no desktop breakpoint, no responsive variants, no wide layout.

**Frame rules** (apply to every frame):
- frame size 390×844
- safe-area insets: keep content clear of the top status-bar area and the bottom tab-bar /
  home-indicator area
- tap targets at least 44×44, with at least 8px between neighbours
- one primary action per frame
- anything a desktop design would make a modal is a bottom-sheet frame or variant instead

**Styles** (create these as variables first):
- Colour: <name> = <value> — <use>
- Type: <name> = <size/weight> — <use>
- Spacing: <name> = <value>

**Components** (build once, reuse):
- Bottom tab bar — the shared navigation component, placed on every frame, at most 5 tabs —
  variants: <one active-tab variant per tab>
- Screen header — variants: <with back control / without> — states: <list>
- <component> — variants: <list> — states: <list>

**Navigation** — the bottom tab bar, built once as a shared component and reused on every frame; the
active-tab variant changes, the component does not:
- <tab label> → frame <N>
- <tab label> → frame <N>

Sheets, not tabs: <destination> → sheet frame <N>, opened from <control on frame M>

**Frames:**
1. <Screen name> — for <who> — showing <how much: the same scale the Web block states> — 390×844 —
   <layout in one line, in phone regions: header / content / tab-bar /
   sheet / fab> — contains <elements with copy>
   Variants: <state frames — a large set needs its empty, its loaded-at-scale, and its loading one>
...

**Prototype links:** <control on frame N> → frame M (say "push" for a screen, "open sheet" for a sheet)

**Content:** use this copy and data verbatim: <copy + rows AT THE REAL SCALE stated per frame —
a frame showing a large set says the real number and is drawn full, not with three placeholder rows>

**What the system knows about the user** (only when `relationship_model: modelled`; these are frame
variants, not separate screens):
- <screen> — variant "first visit" (nothing learned yet) and variant "returning" (<what it knows>)
- The suggestion element shows: <its reason, in plain words>
- The correction control: <what it says> → <what the user gets back>

**Do not add:** <out of scope>
```

The relationship item is present in all four templates on purpose. It is a D7 surface: the one place a
prototype can promise the client a memory, an autonomy, or a retention rule nobody granted. Dropping
it from the newer mobile templates because they were written later is the same breach as never having
written it — the phone prototype is the one the client holds in their hand.

## Part 5 — Hand off to the render step, do not render

The blocks above are the record. Turning them into something a client can look at is a **separate,
human-invoked step** — `/bigin-render-design` — and this stage's whole remaining job is to leave that
step nothing to guess at.

```text
this stage      writes the blocks, ALWAYS, whatever anyone intends to render
                names the render step in the closeout as the next thing available
                checks NO install, invokes NO tool, halts for NOTHING

the render step chooses the ENGINE (the human's choice — the platform only supplies a default),
                halts if that engine is absent, renders, and records artifact POINTERS in the spec's
                ## 8. It reads this spec and the design system; it re-designs nothing

the spec        holds the blocks and, later, ## 8's pointers. NEVER the rendered contents — pasting
                generated HTML in makes the spec a second, drifting copy of something the engine owns
```

**Why the split.** Rendering is a taste-and-timing decision that belongs to the person showing the
client, not to an unattended pipeline: which tool, which platform, which feature, and when. Binding it
to this run forced one engine per platform, made a missing install stop a requirements-side stage that
needed no tool at all, and re-rendered features nobody had asked about. Splitting it means this skill
is now **fully headless with no halt of its own**, and a render is a deliberate act with a person
behind it.

**What this stage owes the render step** — verified at Stage 4 Part 5, restated here because this is
where the last of it gets written:

```text
□ every screen's regions, elements, real copy, real field names, and every state it reaches
□ every token cited by name AND value, in every block
□ this platform's nav shell, in every block
□ every `many` screen's real scale, in words, with its find controls
□ every mobile screen's device facts — frame, safe-area, tap targets, one primary action, sheets
□ `## 7`'s memory rows, concrete, whenever `relationship_model: modelled`
```

A render engine given all of that produces the spec. Given less, it produces something plausible —
and a plausible prototype is reviewed as a specified one.

## Part 6 — Check before saving

```text
□ the block count matches the platform — 2 for `web`, 2 for `mobile`, 4 for `both` — and every
  heading carries its platform suffix: `(Web)` or `(Mobile)`
□ no vault id anywhere in ANY block                                       (D6)
□ every token appears with BOTH its name and its value, in every block
□ the navigation block is checked against the right shell for its own block: a web block lists the
  sidebar / nav-bar entries; a mobile block lists the bottom tabs (at most 5), the per-screen
  headers, and which destinations open as sheets. No web sidebar in a mobile block, no tab bar in
  a web one
□ every navigation entry points at a real screen name that also appears in the Screens/Frames
  section below it, in that same block
□ every screen in ## 2 Screen Inventory appears in EVERY block
□ every state in ## 3 appears in EVERY block
□ the copy in the prompt matches the copy in the screen spec, word for word — and matches word for
  word ACROSS ALL BLOCKS. The only permitted differences between two blocks are the tool's address
  and the platform's shell and viewport
□ every mobile block states its frame and its touch rules: the 390px phone frame (390×844 for
  Figma Make), mobile-first viewport, safe-area insets, 44×44 minimum tap targets, one primary
  action per screen, sheets rather than modals
□ every screen the block covers says WHO IT IS FOR, in words, whenever the feature serves more
  than one actor — and two screens the spec split by actor appear as two screens in every block,
  never collapsed back into one
□ every `many` screen carries its REAL SCALE in words and a page rendered at it ("about 10,000
  records, page 1 of 200"), plus its find controls and its empty state. No `many` list seeded with
  three sample rows
□ no bulk selection, bulk action, export, or saved view appears in any block unless `## 3` carries
  it — and where a tool would obviously add one, item 9 names it as out of scope (D8)
□ `relationship_model: modelled` → EVERY block carries item 10, and every memory named in it
  traces to a `## 7` row (which traces to a real entity field). Nothing in any prompt promises the
  system remembers, decides, or forgets anything `## 7` does not carry (D7)
□ `relationship_model: none` → NO block mentions memory, learning, or autonomous action
□ every block is complete enough to hand to ANY render engine cold — the Part 5 handoff list, in
  the block itself, not merely somewhere in the spec. This is what `/bigin-render-design` reads,
  possibly months from now, on a tool nobody has picked yet
□ someone who has never read this vault could build it
```

A prompt failing the last line is the only real test; the others are how it fails.

## Failure modes

- **Leaving an id in.** The tool renders "UC-012 S4" as a heading on the screen.
- **Naming the token without its value.** The tool picks its own blue and the feature drifts from
  every other feature.
- **Writing "per the requirements".** The tool has no requirements. It guesses, plausibly.
- **Dropping the states.** Prototypes come back with only happy paths, and the empty and error
  screens — the ones the client actually argues about — never get reviewed.
- **Two blocks that disagree.** Whichever the BA pastes, the other becomes wrong.
- **Writing web blocks for a mobile project.** The commonest new failure, because the web block is
  the one this file used to hold: the BA pastes it, the client is shown a sidebar app for a product
  that ships on a phone, and every layout decision reviewed in that session was reviewed for the
  wrong device.
- **Blocks that disagree across platforms.** A screen in the web block and not the mobile one, a
  state rendered only on desktop, copy reworded "because it's a phone" — whichever block the BA
  pastes, the others silently become wrong, and nobody finds out until two prototypes are compared.
- **A mobile block with no phone frame and no tab bar.** The tool has no reason to think phone, so it
  builds a stretched desktop layout with a top nav and calls it done — a "mobile" prototype that has
  never been near a 390px viewport.
- **Lorem ipsum.** Real copy is the cheapest way to find out the words are wrong.
- **Leaving navigation out.** The tool then improvises its own menu per screen, and the prototype
  reads as several disconnected apps instead of one product.
- **Pasting engine-rendered artifact contents into the spec.** The spec holds the prompt blocks and,
  once someone renders, `## 8`'s pointers. Generated HTML is an output; copying it in makes the spec a
  second, drifting copy of something the engine owns, and the copy is stale the next time anything
  renders.
- **Rendering here.** This stage writes the record; `/bigin-render-design` renders, when a human asks
  for it. A render bolted back onto this stage re-imports the halt that split the two apart — and
  re-renders features nobody was asking about.
- **Writing a thinner block because "we will render it from the spec anyway".** The render may happen
  in six months, from a different tool, run by someone who never read the spec. The block is what
  stands alone; a block that leans on the spec around it has failed its only test.
- **Dropping the relationship item from the mobile templates.** They were written later, so item 10
  is the easiest thing to leave out of them — and it is a D7 surface. A phone prototype that quietly
  promises a memory nobody granted is the version the client holds in their hand.
- **Prototyping an agent feature without item 10.** It comes back a stateless chatbot, the client
  reviews the one thing the feature is not, and the review is worthless.
- **Letting the prompt promise memory the requirements never granted.** This is the most expensive
  D7 breach available: the client watches a prototype remember, decide, and act on its own, agrees
  it looks right, and nobody ever decided the system may do that.
- **Writing the trust stages in as a timeline.** The tool builds twelve months of a relationship as
  twelve screens. Build the granted stage; name it.
- **Seeding a `many` list with three sample rows.** The prototype comes back looking calm and
  spacious, the client approves the density, and the screen meets ten thousand records for the first
  time in production. The row count is not decoration — it is what the client is reviewing.
- **Letting the tool add bulk actions to a big table.** Every builder helpfully offers select-all,
  a bulk-actions bar, and an export button the moment it sees a large list. Unless `## 3` carries
  them, item 9 has to name them as out of scope — otherwise the client agrees to an administrator's
  powers nobody specified (D8).
- **Collapsing an actor split back into one screen in the prompt.** The spec correctly separated the
  member's own record from the administrator's directory, and the prompt says "a member record
  screen". Whichever one the tool builds, the other actor was never prototyped.
- **Writing a fifth prompt block for a second actor.** The block count is a platform fact, not an
  actor fact. Actors add screens inside the existing blocks; a per-actor block is an artifact nobody
  keeps in sync.
