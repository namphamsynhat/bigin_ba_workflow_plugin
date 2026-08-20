# Stage 4 — The prototype prompts: two blocks that stand alone

```text
runs: orchestrator, after Stage 2 Part B has finalised every token name
in:   the UX spec's screens, states, flows, copy + the design system's real values + the nav map
out:  ## Prototype Prompt — Claude design   and   ## Prototype Prompt — Figma Make
never: a vault id inside a prompt body · a prompt that says "see the use case"
```

Read `{design_conventions}` § Prototype prompt first, and § The relationship model when this spec's
`relationship_model:` is `modelled`.

**Both blocks, every run.** The BA pastes whichever tool they have open. Same screens, same tokens,
same copy in both — they differ only in how each tool likes to be addressed.

## Part 1 — De-identify

The prompt goes into a tool that has never seen this vault. Every id must become words.

```text
UC-012 S4     → "the step where the reviewer approves the request"
BR-007        → "a request over £5,000 needs a second approver"
EN-003.status → "the request's status: draft, submitted, approved, or rejected"
EN-009.reviewer_pattern → "what the assistant has learned about how this reviewer decides"
UX-002        → delete it. The prompt does not need to name itself.
INT-014       → delete it. Never put a client's meeting id in a prompt.
--color-action-primary: #2563eb   → keep BOTH: the name AND the value
```

`{nav_map_file}`'s entry labels and group names are already plain words — carry them in as-is, no
de-identification needed. Pull only the groups/entries these screens actually touch, never the whole
vault-wide map (a feature's prototype does not need every other feature's menu items).

Grep your own draft for `UC-`, `BR-`, `EN-`, `PP-`, `UX-`, `INT-`, `PRD-`, `S1`…`S9`, `A1`, `E1`
before writing it. A hit is D6 broken.

## Part 2 — What goes in, in this order

```text
1  what it is        one paragraph: the product, the user, what this part of it does
2  the look          every token: name, value, and a plain-language note
                     ("action primary #2563eb — the colour every main button uses")
3  the navigation     the persistent menu/nav shell these screens live inside: which entries
                     (this feature's own, plus any sibling entries needed for orientation),
                     and which screen each one opens — so the tool builds ONE shell, not one
                     per screen it improvises
4  the screens       one block per screen: purpose, regions, elements, real copy
5  the flow          screen order, and what each button leads to
6  the states        per screen: empty, loading, error, permission, success — what each says
7  the data          3-5 rows of realistic sample data per list, real field names from the entity
8  the rules         the behaviour the screens must show, in plain words (from the BRs)
9  what NOT to build anything out of scope that a tool would otherwise helpfully add
10 the relationship  ONLY when this spec's relationship_model: is `modelled` — from ## 7:
                     what the system remembers about the user, what it does on its own, and how
                     the user corrects or clears it. Omit the whole item otherwise.
```

Item 8 is the one people skip and the one that saves the most time.

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

## Part 3 — Claude design block

Prose, addressed to a builder. It produces working HTML, so tell it about behaviour and states.

```markdown
## Prototype Prompt — Claude design

Build a clickable prototype of <what it is>.

**Design system** — use these values everywhere, never anything else:
- <token name> — <value> — <what it is for>
...

**Navigation** — this persistent menu wraps every screen below; build it once, not per screen. Indent
to show nesting (a sub-item sits under its parent; a parent with no screen of its own is a header
only):
- <top-level item> → <screen, or "—" if it only opens a submenu>
  - <nested item> → <screen>
    - <nested-nested item> → <screen>
- <top-level item> → <screen>

**Screens** (build all <N>):
### <Screen name>
Purpose: <one line>
Layout: <regions>
Contains: <elements, with their real copy>
States: <state> — <what the user sees and reads>
Actions: <control> → <where it goes>

**Flow:** <screen> → <screen> → <screen>, and <control> → <the failure screen/state>

**Sample data:** <a small realistic table>

**Rules the prototype must show:** <plain-language rules>

**What the system remembers about the user** (only when `relationship_model: modelled`; build this
as real state carried between screens, not as static text):
- <what it remembers, in plain words> — shown on <screen> as <the element>
- It acts on its own for: <the autonomous action the rules actually granted>
- It only suggests, never acts, for: <the rest>
- The user corrects or clears it by: <the correction path>

**Do not build:** <out of scope>
```

## Part 4 — Figma Make block

Same content, tightened for a design tool: frames, components, and variants rather than behaviour.

```markdown
## Prototype Prompt — Figma Make

Create a <N>-frame prototype of <what it is>.

**Styles** (create these as variables first):
- Colour: <name> = <value> — <use>
- Type: <name> = <size/weight> — <use>
- Spacing: <name> = <value>

**Components** (build once, reuse):
- <component> — variants: <list> — states: <list>

**Navigation** (build once as a shared frame/component, reuse on every screen). Indent to show
nesting — a parent item with children but no frame of its own opens a submenu, not a screen:
- <top-level item> → frame <N>, or "opens submenu" if it has no frame of its own
  - <nested item> → frame <N>
- <top-level item> → frame <N>

**Frames:**
1. <Screen name> — <layout in one line> — contains <elements with copy>
   Variants: <state frames>
...

**Prototype links:** <control on frame N> → frame M

**Content:** use this copy and data verbatim: <copy + sample rows>

**What the system knows about the user** (only when `relationship_model: modelled`; these are frame
variants, not separate screens):
- <screen> — variant "first visit" (nothing learned yet) and variant "returning" (<what it knows>)
- The suggestion element shows: <its reason, in plain words>
- The correction control: <what it says> → <what the user gets back>

**Do not add:** <out of scope>
```

## Part 5 — Check before saving

```text
□ no vault id anywhere in either block                                    (D6)
□ every token appears with BOTH its name and its value
□ the navigation block lists every entry this feature added or touches, each pointing at a
  real screen name that also appears in the Screens/Frames section below it
□ every screen in ## 2 Screen Inventory appears in both blocks
□ every state in ## 3 appears in both blocks
□ the copy in the prompt matches the copy in the screen spec, word for word
□ `relationship_model: modelled` → both blocks carry item 10, and every memory named in it traces
  to a `## 7` row (which traces to a real entity field). Nothing in the prompt promises the system
  remembers, decides, or forgets anything `## 7` does not carry (D7)
□ `relationship_model: none` → neither block mentions memory, learning, or autonomous action
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
- **Lorem ipsum.** Real copy is the cheapest way to find out the words are wrong.
- **Leaving navigation out.** The tool then improvises its own menu per screen, and the prototype
  reads as several disconnected apps instead of one product.
- **Prototyping an agent feature without item 10.** It comes back a stateless chatbot, the client
  reviews the one thing the feature is not, and the review is worthless.
- **Letting the prompt promise memory the requirements never granted.** This is the most expensive
  D7 breach available: the client watches a prototype remember, decide, and act on its own, agrees
  it looks right, and nobody ever decided the system may do that.
- **Writing the trust stages in as a timeline.** The tool builds twelve months of a relationship as
  twelve screens. Build the granted stage; name it.
