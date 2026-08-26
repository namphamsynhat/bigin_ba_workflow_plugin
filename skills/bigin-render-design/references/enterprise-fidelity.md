# Enterprise fidelity — the bar a render has to clear

Read by `render-ui-designer` (in full, before rendering) and by `render-ui-linter` (as its checklist).
The goal of a render is a prototype a client mistakes for the shipped product. Everything below is
what separates that from a wireframe with colour.

**None of this licenses a design decision.** Every screen, field, state, and word was decided by
`/bigin-generate-design`. This file governs *how well the specified thing is built*, never *what gets
built*. Where it and a `DESIGN-PRINCIPLES` row disagree, the row wins — it is ground 3, and this file
is ground 2b.

---

## § The bar

Ten items. The designer self-checks them before reporting; the linter verifies each one and reports a
skipped item as skipped, never as a pass.

### 1 · Token-only styling

Every colour, type size, weight, spacing value, radius, border, and shadow comes from
`{tokens_file}`, by name, with that file's value. No raw hex, no raw `px` on a spacing or type
property, no named font family the token system does not carry.

A value the render needs and the token file does not have is a **gap to report**, not a token to add:
the design system is append-only and it is `/bigin-generate-design`'s (D1).

### 2 · Contrast — WCAG AA, computed

```text
body text and any text under 18pt / 14pt bold   ≥ 4.5:1
large text, icons, and UI boundaries            ≥ 3:1
a focus indicator against BOTH the component and its background   ≥ 3:1
```

Computed against the token pair actually rendered, with `scripts/check-contrast.py` — never
eyeballed, and never assumed from a token's name. A muted-on-subtle pairing is where this fails, and
it fails on precisely the secondary text a dense enterprise screen is full of.

A failing pair is reported with its ratio. It is **not** fixed by changing a token value.

### 3 · Density — enterprise, not marketing

Enterprise software is dense, because its users live in it all day and need to see more at once.

```text
table / list row height     32–44px. Not 64, not 72
control height              32–40px for the standard size
section padding             16–24px on a data surface. 48–80px is a marketing page
gutter between fields       one scale, applied everywhere — 8px grid or the token scale, no ad hoc
line-height on dense text   1.4–1.5. 1.8 is an article
max-width on a data screen  none. A data table centred in a 720px column is a landing page
```

The tell is not any single number — it is **inconsistency**. One scale, applied to every screen.

### 4 · The shell, always present and always identical

The persistent navigation from `navigation-map.md` renders on every screen, byte-identical, with the
current entry marked and its ancestors open. A page header carries the screen title and its single
primary action; secondary actions sit beside it, visually subordinate. Where the nav map nests three
or more deep, a breadcrumb renders the real dot-path.

See `render-pipeline.md` § The navigation contract — the map is the only source, and none of this is
the designer's call.

### 5 · Realistic data, at the real scale

The single highest-leverage item on this list.

```text
COUNT      the spec's real number. "≈10,384 records · page 1 of 208" with a working pagination
           footer, sortable column affordances, and the find controls the spec names
VARIETY    realistic distribution — different lengths, a few long values that wrap or truncate,
           some empty optional fields, statuses spread across the real enum rather than all one
DOMAIN     plausible records for THIS product's domain, generated from the extractor's types,
           formats, and enums. Real-looking names, real-format ids, real date ranges, real amounts
           with the right currency and precision, real-looking email domains
NUMBERS    tabular numerals, right-aligned, consistent precision, thousands separators
DATES      one format, product-wide, and relative time only where the product would really use it
```

Ten thousand records are rendered as ten thousand: a full first page, real pagination, and a total
count. Not ten rows with a "10,384" label above them.

### 6 · Every named state, rendered *and reachable*

Every state the spec's `## 3` names — empty, loading, error, loaded, and any state the flows reach —
exists in the artifact and can be **arrived at**, by a real interaction or by an explicit state
switcher in the prototype's own chrome. A state drawn once in a corner of a style page is not
rendered.

An empty state carries its real copy and its real next action, not a grey box. A validation error
renders on the field, in the spec's words, with the error styling and an accessible association. A
loading state is the real skeleton of the real layout, not a spinner over blank space.

### 7 · The chrome production software actually has

```text
status              semantic badges/pills from the token system, one visual language product-wide
row actions         where the spec grants them — never invented, never a bulk action (D8)
find controls       on every `many` screen: the search, filter, and sort the spec names
disabled states     rendered as disabled, with the reason available where the spec supplies one
focus rings         visible on every interactive element, keyboard-reachable, in tab order
empty optionals     an em dash or the product's own convention — never a blank cell
truncation          long values truncate with the full value available, never overflow the layout
tooltips            where the spec calls for them, on hover AND focus
```

### 8 · Typography discipline

The spec's type tokens only. At most four sizes on a single surface. One weight axis for hierarchy,
not four. Numeric columns in tabular figures. Text left-aligned, numbers right-aligned, headers
matching their column's alignment. Sentence case or title case — one of them, product-wide.

### 9 · Restraint

Gradients, glassmorphism, heavy shadows, animated heroes, decorative illustration, and emoji-as-icons
appear **only** where a `DESIGN-PRINCIPLES` row asks for them. The default enterprise register is
flat, quiet, and high-signal. Motion is functional — a state transition, a disclosure — under 200ms,
and it respects `prefers-reduced-motion`.

### 10 · Consistency across screens

The same padding scale, the same button hierarchy, the same empty-state pattern, the same table
shape, the same badge language, on every screen. A prototype's screens are almost always
individually fine and collectively obviously assembled; this is the item that catches that, and it
can only be checked by looking at the screens **together**.

---

## § The tells

What marks a prototype as a prototype. The linter greps for these; the designer should never emit
one.

```text
COPY        Lorem ipsum · "Item 1", "Item 2" · "Button", "Click here", "Label" · "John Doe",
            "Jane Smith" · test@test.com, user@example.com · "Some description here" ·
            a heading that names the component instead of the content
DATA        exactly three sample rows · every row identical but for a number · every status the
            same value · every date the same date · a "10,384" total above ten rows
LAYOUT      a data table centred in a narrow column · marketing whitespace on a dense screen ·
            a grey box where an image belongs · double scrollbars · a nav that differs per screen ·
            inconsistent corner radii or shadow depths between screens
STYLE       raw hex in the artifact · a font family the token system does not name · a colour
            picked to look right rather than named · an icon set the design system does not carry
BEHAVIOUR   a dead link · a control that does nothing on click · alert() · a filter that does not
            filter · a sort that does not sort · a state reachable only by editing the source
TRACE       any of /(UC|BR|EN|UX)-\d/ in visible copy — see render-pipeline.md § The traceability
            contract. This one is deterministic and has its own script
```

---

## § What this file may never be used to justify

The fidelity bar raises the finish. It never widens the scope.

```text
NEVER   a screen ## 2 does not carry, because the IA "obviously needs" one
        a field, column, or control the spec does not carry, because the table looks sparse
        bulk select, export, or a saved view, because enterprise software usually has them — D8:
          volume licenses FINDING, never a CAPABILITY, and "obviously needed" is a requirement gap
        a state the spec does not name, because a real product would have it
        a nav entry the map does not carry, because the shell looks thin
        anything shown as remembered, learned, or personalised that ## 7 does not carry — D7
        a token invented so a value could be named — D1, append-only, and not this skill's file
        copy invented to fill a heading the spec left empty
```

Each of those reaches a client looking exactly as specified as the real thing, which is strictly
worse than an obvious guess. Every one of them is a **report line**, not a render decision.
