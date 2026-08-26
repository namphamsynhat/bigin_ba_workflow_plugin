# The prompt contract — what Open Design is actually told

Read by `/bigin-render-design` at Step 2, and by both render agents. It defines what a **feature
prompt** and an **assembly prompt** contain, in what order, and what may never appear in one.

## Why this file is strict

Open Design spawns its own agent, in its own process, in its own project directory. **That agent
cannot see this vault.** It has no UC file, no ENTITIES.md, no design-tokens.md, no navigation map —
it has the prompt and the design system bound to the project, and nothing else.

```text
anything left OUT of the prompt   is something the agent will INVENT, plausibly and confidently, and
                                  the invented thing reaches a client looking exactly as considered
                                  as the specified thing
anything put in AS AN ID          "per UC-012 S4" is a dangling pointer. It produces either a wrong
                                  screen or a screen with "UC-012" printed on it
```

So the prompt is **self-contained** (D6, the same rule the spec's own `## Prototype Prompt` blocks
follow) and **fully expanded**. It is long. That is correct.

---

## § The five sources, and their precedence

A feature prompt is assembled from five places. When two disagree, the higher row wins, and the prompt
**says so explicitly** rather than silently resolving it.

```text
1  DESIGN-PRINCIPLES.md active rows   client-stated durable preferences. GROUND 3 — outranks the
                                      design system, the engine's taste, and the fidelity bar
2  the UX-### spec                    THE DESIGN. Screens, regions, elements, copy, states, flows.
                                      Verbatim, never paraphrased
3  {tokens_file} + {components_dir}   the token VALUES and shared components. Names alone are
   + {nav_map_file} ## Structure      useless to a process that cannot read the token file
4  UC / BR / ENTITIES.md / _entities  DATA AND LOGIC ONLY — field lists, types, formats, enums,
                                      cardinalities, validation predicates, state keys, real volumes
5  PAIN-POINTS.md rows behind a state which states are worth rendering properly
```

**Source 4 is the one that gets misused.** It enters the prompt as *facts* — "an Order has a
`status` of one of: draft, submitted, approved, rejected, shipped" — never as *material to design
from*. The screens were already decided by source 2. If source 4 carries a field no screen shows, it
does not enter the prompt; it is reported as unused. If a screen shows a field source 4 does not
carry, that is a gap to report, not a field to invent.

**Filter source 4 by the spec's own `## 2 Screen Inventory`.** A feature citing six entities whose
screens render two gets two entities' worth of data facts in its prompt. The rest is noise that
invites the agent to build something with it.

---

## § Id expansion — the single hardest rule

**No `UC-`, `BR-`, `EN-`, `PP-`, `UX-`, `INT-`, or `PRD-` id appears in the prose of a prompt.** Every
one is expanded into the words it stands for, before the prompt is built.

```text
WRONG   "The approve button implements UC-012 S4, validated by BR-018."
RIGHT   "The Approve button completes the step where a reviewer accepts a submitted request. It is
         disabled unless the request's status is 'submitted' AND the signed-in user is not the
         person who submitted it."

WRONG   "Render the states listed in § 3, per the screen inventory above."
RIGHT   "Render five states for this table: empty (no orders yet), few (3 rows), many at real scale
         (≈10,000 records, showing page 1 of 400), loading, and error."

WRONG   "Fields per EN-004."
RIGHT   "Each Order row shows: order number (text, format ORD-000000), customer name (text),
         placed date (date, DD MMM YYYY), status (one of: draft, submitted, approved, rejected,
         shipped), total (currency, 2dp)."
```

The test: **could someone who has never opened this vault build the right screen from this prompt
alone?** If any sentence needs the vault to resolve, it fails.

### The one exception — the traceability attributes

Ids **do** enter the prompt, in exactly one place: the instruction block telling Open Design to emit
`data-*` attributes. That block is machine-readable provenance, and it is quoted verbatim into every
feature prompt:

```text
TRACEABILITY — emit these attributes, and keep these ids OUT of everything a person can read.

  every screen root element      data-ux="UX-003"  data-screen="orders-list"
  every element grounded in a
    use-case step                data-uc="UC-012"  data-step="S4"
  every element a rule governs   data-br="BR-018"
  every element rendering an
    entity's field               data-en="EN-004"  data-field="status"
  every state-bearing container  data-state="empty|few|many|loading|error"

These ids MUST NOT appear anywhere a person can see or hear them: not in a text node, not in an
aria-label, title, alt, placeholder, or value attribute, not in an <option> body, not in a CSS
content: property, and not in a comment that renders. Visible copy is the human words above and
nothing else.
```

`scripts/check-traceability.sh` verifies both halves of that block after the run.

---

## § A feature prompt, in order

Nine sections. The order matters: an agent reads top-down and the constraints have to arrive before
the work.

```text
1  WHAT THIS IS          one paragraph. The product, the feature, the actor, the platform, and that
                         this is a high-fidelity prototype of an ALREADY-DESIGNED thing — nothing
                         here is open for redesign
2  HARD CONSTRAINTS      the DESIGN-PRINCIPLES active rows, stated as overrides that beat the bound
                         design system wherever they disagree. Plus: build ONLY the screens listed;
                         invent no screen, no field, no status, no capability
3  DESIGN SYSTEM         every token the screens use, by NAME and VALUE, with a plain-language note
                         on each. Shared components, described. If the vault's own tokens were
                         chosen over a catalog system, this section IS the design system
4  THE SHELL             this platform's navigation ## Structure, verbatim — entries, labels, depth,
                         order, roles. Identical on every screen. Web: header/nav/main/aside/footer.
                         Mobile: header/content/tab-bar/sheet/fab, 390px frame, safe-area insets,
                         touch-target minimums
5  SCREENS               one block per ## 2 inventory row: purpose, actor, scope, regions, the full
                         element table with copy and token names, the States table with what the
                         user sees in each, the Interactions table with where each control goes
6  DATA                  the expanded field facts from source 4, filtered to what these screens
                         render: types, formats, enum vocabularies, cardinalities, and the REAL
                         volume numbers. Plus: "generate realistic sample VALUES from these facts;
                         never invent a field, a status, or a capability"
7  FLOWS                 the ## 4 order the screens are reached in, entry → success → each failure
8  FIDELITY BAR          references/enterprise-fidelity.md § The bar, all ten items, quoted
9  TRACEABILITY + OUTPUT the attribute block above, verbatim, plus the dictated output path:
                         screens/<ux-id-lowercased>-<slug>.html — a single self-contained file, no
                         external stylesheet, no external script, no CDN
```

**Section 8 is not optional.** An agent told only *what* to build and never *how well* builds a
wireframe with colour. The fidelity bar is what separates a prototype a client mistakes for the
shipped product from one they can tell is a mock.

**Section 6's last sentence is the whole dataset rule.** Values are authored; structure is not.

---

## § The assembly prompt, in order

Built once, after every feature run is terminal. Seven sections.

```text
1  WHAT THIS IS          one paragraph: wire the existing screen files into ONE interactive
                         prototype. Redesign NOTHING — every screen is finished
2  THE SHELL             navigation ## Structure, verbatim, as the ROUTE TREE. This is the single
                         source of truth for navigation; resolve nothing independently of it
3  THE SCREENS           every screens/*.html by path, with which nav entry each one answers to
4  ENTRY STAGE           when the participating specs name more than one actor, an actor switcher —
                         ONLY the actors and handoffs a spec's own ## 1 or ## 4 Flows names. A
                         handoff neither spec describes is an invented flow
5  OUT-OF-SCOPE ENTRIES  nav entries pointing at features NOT in this run: render visibly
                         unavailable, never as a dead click, never silently removed
6  DESIGN SYSTEM         the same token values every feature run used. The shell must be identical
                         on every screen and the assembled build must not introduce a second one
7  OUTPUT + CHECKS       index.html — one self-contained file: client-side routing, embedded state,
                         CSS from the token values, no server, no external stylesheet or script.
                         Then, stated as requirements it must satisfy:
                           · every nav entry resolves to a real screen
                           · every "goes to" control resolves inside the runtime
                           · every route reachable from the entry stage
                           · no route reaching a feature outside this build's scope
                           · the traceability attribute block still holds on index.html
```

**Zero broken links.** Every route the assembled app can reach — a screen, a modal, a toast, a
cross-cutting screen more than one spec's inventory names — resolves inside the one runtime. A route
pointing at a spec that was not named for this build is not a link; it is a gap the build should never
have offered.

---

## § What may never be in a prompt

```text
a bare vault id in prose                    → § Id expansion. It is a dangling pointer
"per the spec" / "as listed above" /
  "see the use case"                        → the run happens in a process that cannot see any of it
a screen the ## 2 inventory does not carry  → § Grounding. Not the prompt's to add
a field, status, or capability no source
  carries                                   → the same rule, one level down
Lorem, placeholder copy, or "TBD"           → copy is content and it was decided
a token name with no value                  → the agent cannot read {tokens_file}
a nav entry not in ## Structure              → the nav map is the single source of truth
a raw hex or px value not from a token       → token-only styling, fidelity item 1
an instruction to "improve", "modernise",
  or "make it look better"                   → that is redesigning, and it is not this step's
an ## 4 Coverage "out of scope" row rendered
  as a working feature                       → those rows exist to stay absent
```

---

## § The self-containment test

Before a prompt is sent, one check, applied to the whole text:

```text
1  grep it for /(UC|BR|EN|PP|UX|INT|PRD)-\d/
       hits inside the TRACEABILITY block          → fine, that is the exception
       hits anywhere else                          → expand them and re-check
2  read it as somebody who has never seen this vault. Every screen buildable? Every state
   described in words? Every token carrying a value? Every field carrying a type?
3  any "see", "above", "per the", "as specified"  → resolve it inline
```

A prompt that passes this is also the prompt written to `_prompts/` when the automation fails
(`/bigin-render-design` § The manual fallback) — the fallback works precisely *because* the prompt was
built to this standard in the first place. That is not a coincidence; it is why the standard is here.
