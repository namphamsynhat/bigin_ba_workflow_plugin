---
name: design
description: Produces the design for a feature from its approved use cases - a screen list, screen details, flows, and one clickable HTML prototype a person can open and review. Use after use cases are approved, when a design is stale, or when asked for screens, a UX spec, a mockup or a prototype.
argument-hint: "[feature slug | UX-### | omit for every feature waiting]"
---

# Design a feature

Turn the use cases into screens, then into a prototype people can click through.
Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

## Steps

1. **Scope.** `bigin status $ARGUMENTS` lists approved use cases with no design, and stale designs.
   One design file per feature. Read the feature's use cases, rules, entities, `design` signals, and
   `platform` in `bigin.md`. A proposal the client has not confirmed does not stop the design: build
   it as proposed. A draft use case may be designed only when the person asks for it.
2. **Create or open the design:** `bigin new ux "<Feature name>" --feature <slug>`, or the existing
   `UX-###` file.
3. **Turn flows into screens:**
   - Steps by the same actor in the same place are one screen.
   - A step only the system performs is not a screen.
   - A validation is a state of a screen. An error flow is a named error state.
   - Every entity field a step uses appears on a screen.
4. **Write the design file:** the `Screens` table (the `Serves` column holds `UC-003 S1–S3`), the
   details of each screen, and one flow line per use case.
5. **Build the prototype**, following [prototype.md](prototype.md), at
   `02-design/prototypes/<slug>.html`. Put the path in `prototype:`.
6. **Mark what is proposed.** In the prototype and the screen details, mark each part built on an
   unconfirmed proposal with a small note: `Proposed — to confirm`. The client reviews exactly these.
7. **List what you added.** Every screen, field or action no use case, rule or signal asked for goes
   under `## Assumptions` with its reason. These are the team's own decisions: no question for them.
8. **Stamp it:** `built_from: [UC-003@2, …]` with each use case's current version. On an update, raise
   `version` and add a Changelog line.
9. **Get a second reading** from the `spec-reviewer` agent: is every step of every use case on a
   screen, and is anything on a screen that no source asked for?
10. **Report** the file, the prototype path, the open questions and the proposals shown as proposed. A person reviews with
   `/bigin-ba:approve UX-###`.

## Rules

- Requirements are read-only here. If the design shows a gap in what the system does, sort it as rules
  section 5 says, on the design, with `(ref: UC-003)` for a question. Do not edit the use case.
- Keep it plain: layout and behaviour, not brand. No invented colours, logos or copy that sounds final.
