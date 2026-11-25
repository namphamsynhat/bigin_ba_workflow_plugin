---
name: handoff
description: Writes the build pack of a feature - its approved use cases, rules, data, screens, acceptance scenarios and open items - as one folder a development plugin or coding agent can build an MVP from. Only a person can run this.
argument-hint: "<feature slug> [folder in the code repository]"
disable-model-invocation: true
---

# Hand a feature to the build

Make one folder that a coding agent can build from, without the vault.
Read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` first.

## Steps

1. **Write the pack.** Run `bigin pack <feature>`. It copies the approved use cases, their rules, the
   entities, the design and the prototype into `05-handoff/<feature>/`, word for word, and lists the
   open items. Never retype what it copies.
   - It leaves out a use case that is not approved or is held by an open question. Tell the person
     which, and why. To include one, they approve it first, or give a working answer at review.
   - A proposal the client has not confirmed does not stop the pack. It is listed in `open-items.md`.
2. **Write `acceptance.md`** in the pack folder: the scenarios the build must pass.
   - One scenario for the main flow of each use case, one per other flow, one per rule, one per error path.
   - Gherkin, in business words, tagged with what it proves: `[UC-001 S2] [BR-003]`.
   - A scenario that rests on an assumption or an unconfirmed proposal is tagged `[may change]`.
   - Write only what the use cases and rules say. A gap is not filled here: name it in your report.
   - First line: `Built from: <the built_from list in the pack's README.md>`.
3. **Get a second reading.** Give `acceptance.md` to the `spec-reviewer` agent, with the pack's
   `use-cases.md` as its source. Fix what it finds.
4. **Copy it to the code.** If the person named a folder, or `handoff_path` is set in `bigin.md`, run
   `bigin pack <feature> --to <folder>`. No folder → leave the pack in the vault and say where it is.
5. **Report:** the pack path, what is in it, what was left out, the proposals and assumptions the
   build rests on, and the line to give the development plugin:
   "Read `<folder>/<feature>/README.md` and build this feature."

## Rules

- The pack is the only thing this plugin writes outside the vault, and only when the person asks.
  Never write code, and never edit a file the build made.
- The pack is generated. A change is made in the vault, then the pack is written again.
  `bigin status` reports a pack that is older than its use cases.
- For an MVP, hand over use cases, not stories. The development plugin slices the work itself.
- What the client says after trying the MVP comes back through `/bigin-ba:intake`.
