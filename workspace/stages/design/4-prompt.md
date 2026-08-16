# Stage 4 — The prototype prompts: two blocks that stand alone

```text
runs: orchestrator, after Stage 2 Part B has finalised every token name
in:   the UX spec's screens, states, flows, copy + the design system's real values
out:  ## Prototype Prompt — Claude design   and   ## Prototype Prompt — Figma Make
never: a vault id inside a prompt body · a prompt that says "see the use case"
```

Read `{design_conventions}` § Prototype prompt first.

**Both blocks, every run.** The BA pastes whichever tool they have open. Same screens, same tokens,
same copy in both — they differ only in how each tool likes to be addressed.

## Part 1 — De-identify

The prompt goes into a tool that has never seen this vault. Every id must become words.

```text
UC-012 S4     → "the step where the reviewer approves the request"
BR-007        → "a request over £5,000 needs a second approver"
EN-003.status → "the request's status: draft, submitted, approved, or rejected"
UX-002        → delete it. The prompt does not need to name itself.
INT-014       → delete it. Never put a client's meeting id in a prompt.
--color-action-primary: #2563eb   → keep BOTH: the name AND the value
```

Grep your own draft for `UC-`, `BR-`, `EN-`, `PP-`, `UX-`, `INT-`, `PRD-`, `S1`…`S9`, `A1`, `E1`
before writing it. A hit is D6 broken.

## Part 2 — What goes in, in this order

```text
1  what it is        one paragraph: the product, the user, what this part of it does
2  the look          every token: name, value, and a plain-language note
                     ("action primary #2563eb — the colour every main button uses")
3  the screens       one block per screen: purpose, regions, elements, real copy
4  the flow          screen order, and what each button leads to
5  the states        per screen: empty, loading, error, permission, success — what each says
6  the data          3-5 rows of realistic sample data per list, real field names from the entity
7  the rules         the behaviour the screens must show, in plain words (from the BRs)
8  what NOT to build anything out of scope that a tool would otherwise helpfully add
```

Item 8 is the one people skip and the one that saves the most time.

## Part 3 — Claude design block

Prose, addressed to a builder. It produces working HTML, so tell it about behaviour and states.

```markdown
## Prototype Prompt — Claude design

Build a clickable prototype of <what it is>.

**Design system** — use these values everywhere, never anything else:
- <token name> — <value> — <what it is for>
...

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

**Frames:**
1. <Screen name> — <layout in one line> — contains <elements with copy>
   Variants: <state frames>
...

**Prototype links:** <control on frame N> → frame M

**Content:** use this copy and data verbatim: <copy + sample rows>

**Do not add:** <out of scope>
```

## Part 5 — Check before saving

```text
□ no vault id anywhere in either block                                    (D6)
□ every token appears with BOTH its name and its value
□ every screen in ## 2 Screen Inventory appears in both blocks
□ every state in ## 3 appears in both blocks
□ the copy in the prompt matches the copy in the screen spec, word for word
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
