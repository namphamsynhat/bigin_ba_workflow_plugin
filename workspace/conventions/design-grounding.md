# Design Conventions — grounding, coverage, and open questions

The test that keeps design out of the requirements, the coverage check that is the only thing
able to find an omission, and how a design-stage question is written.

**Read by** design stages 3, 4, and 5.

## Grounding — the test that keeps design out of the requirements

Every non-trivial decision (a screen existing, a field appearing, a state, a flow's shape, a nav
grouping) traces to exactly one of:

```text
1  a REQUIREMENT   a UC step / branch, a BR, or an EN field         → cite the id
1b a PAIN POINT    a PP-### on the register                          → cite the id. It grounds HOW a
                                                                       flow is shaped, never THAT a
                                                                       screen exists (§ User flows)
2a a VAULT PATTERN an existing screen in this vault                  → name it
2b an EXTERNAL     a pattern from an installed design/UX skill       → name the skill and the pattern
   PATTERN
3  a PREFERENCE    a DESIGN-PRINCIPLES row or a hub directive        → cite the row #
```

**2a and 2b are not interchangeable.** A vault pattern is evidence that this product already works
that way. An external pattern is only evidence that the pattern exists somewhere:

```text
2a can ground THAT a screen, field, or state exists — a sibling feature already ships it here
2b can only shape HOW something already grounded by 1, 2a, or 3 gets built
2b ALONE                → not a ground. It is an Open Question, or a requirement gap.
```

An external catalog that grounds existence is how a whole screen nobody asked for arrives carrying a
citation. The citation makes it *look* grounded, which is strictly worse than an obvious guess.

**1b behaves like 2b, not like 1.** A pain point is real, client-stated, and on the register — but it
states a *problem*, not a system behaviour. It grounds a flow's ordering, a screen's emphasis, a nav
placement, a default. It never grounds a new screen, field, capability, or state on its own; that
needs ground 1, or it is a requirement gap.

None of the above → **it is not yours to settle**. Write an Open Question (D3). An invented screen
is scope nobody asked for, and it looks exactly like a designed one.

An entity that is still `proposed`/`draft` grounds a decision as a **known gap**, not settled fact —
say so next to the field list rather than treating it as final.

**A volume fact is ground 1, and it grounds finding machinery only.** An `EN-###` relationship
cardinality cited with the UC step that puts an actor in front of that set ("EN-004 — many Orders
per Account · UC-030 S2") grounds search, filters, sort, pagination, and the volume states — the
machinery without which the screen only works on demo data. It never grounds a capability: bulk
action, export, or a saved view needs its own UC step or BR-###, or it is a requirement gap
(`design-actor-scope.md` § Actor scope, D8).

## Coverage verification — the only check that can find an omission

Grounding above runs **backward**: every element on a screen back to the thing that licensed it. It
is what stops the design inventing scope, and it is completely blind to the opposite failure — a step,
a rule, a field, or a whole exception flow that nobody drew. A screen that was never drawn has no
element to trace, so every backward check passes on a spec with a third of the requirement missing.

`5-verify` runs the **forward** direction, once, per design run:

```text
every non-removed S# / A# / E# of every in-scope UC        →  the screen AND STATE that carries it
every BR-### they cite that constrains what an actor
  sees or may do                                           →  the state, validation, or Visible to
every EN-### field their steps read or write                →  the element that renders it
every PP-### this feature's hub carries, still open         →  the flow that resolves it
every open hub ## Design Directives row                     →  the screen that implements it
every active DESIGN-PRINCIPLES row                          →  where it applied
```

Three verdicts, and no fourth:

```text
covered                          the screen and the state, both named (for a PP-###: the FLOW and
                                 where in it). A `covered` verdict over an empty cell is the table
                                 claiming a coverage nobody checked
gap → ## 6 Q<n>                  genuinely not designed. A design question (owner: team), or a
                                 REQUIREMENT GAP (owner: client) when the answer would change what
                                 the system DOES — /bigin-transform-signal's, never written on the UC
out of scope — <cited reason>    excluded by something ON RECORD, and the record is cited. An
                                 exclusion with nothing behind it is a gap wearing a decision's
                                 clothes, and the field the client expected vanishes with an
                                 explanation nobody made
```

The table lives in the spec (`## 4 Flows` → `### Coverage`), is re-written **whole** every run — the
same rule `absorbed:` follows, for the same reason — and is verified on disk by `6-close`'s coverage
check.

**It repairs; it does not design.** An item a screen plainly carries whose row failed to say so gets
the row fixed. An item nothing carries gets a question. Adding the missing screen, state, or control is
a `3-screens` dispatch on the next run — a verification pass that draws the thing it was checking for
has no independent verdict left to give (D3).

**Render readiness is verified in the same pass**, and it is the safeguard that replaced the old
required-engine halt (`design-platform.md` § Rendering is a separate step). A render may happen months later, on a tool
nobody has picked, run by someone who never read the requirements — so the spec must be sufficient
input *now*: this platform's regions, real copy and real field names, every state named, every element
carrying a role or deliberately carrying none, the nav shell resolvable, a `many` screen's real scale
in words, a phone screen's device facts. A box that cannot be ticked from the record is a question,
never a plausible fill: a render engine given a gap produces something convincing, and a convincing
prototype is reviewed as a specified one.

**The visual system is the one thing render readiness does not check.** No colour, type scale, or
component library is expected in the spec, because this skill produces none — the design system is
bound at render time (`design-platform.md` § Rendering is a separate step). A spec is render-ready without one.

## Open questions

Design questions live on the UX spec's `## 6`, and are mirrored on the hub's
`## Open Questions / Gates`. Same sentence in both places — a re-worded mirror reads as a second
question, gets answered twice, and can never be paired back up.

```text
- [ ] Q: <self-contained question, plain business language> (owner: client|team) (ref: UX-###)
      A:
```

Never copy a question that is already open on the UC's `## 5`. If the answer would change **what the
system does** rather than how it looks or flows, say so in the question and in the report: it is a
requirement gap, and `/bigin-transform-signal` owns it.
