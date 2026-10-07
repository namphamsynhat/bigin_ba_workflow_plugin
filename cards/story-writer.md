# Card — Story writer (model: session default — slicing and translating for a product owner is judgement)

**In:** the dispatch block from `/bigin-generate-stories`: feature slug, `EP-###` (new or update), the story
ids to use, UCs TO SLICE (approved, with versions), PENDING / NOT YOURS UCs, approved stories (never edit),
SNAPSHOT folder or none, DESIGN `UX-###@version` or none. Read each UC in full, every BR in `brs:`, every EN
in `entities:`, the UX spec §§ 2-4, `SNAPSHOT.md`, and `_bigin/templates/{epic,user-story}.md` (the schema).
**Out:** files inside `03-Epics-Stories/EP-<NNN> <Feature>/` only, all `status: draft`, and the reply block.
`_bigin/stages/stories/3-slice.md` and `4-write.md` stay the full procedure.

## Rules
1. A story is a use-case slice: main path first (P1), then A#/E# flows or rule groups. Never one story per
   line or per screen ‹stages/stories/3-slice.md § Part 1 — Slice in this order›.
2. An E# that only shows a message on the same screen is an acceptance criterion of its parent, not a story.
3. Every S#/A#/E# lands in the epic's § 7 coverage matrix; no blank rows ‹stages/stories/3-slice.md § Part 3 — The coverage matrix›.
4. Business language only — what a person sees, does, or is told. Keep every validation, record, and
   notification the step carried ‹stages/stories/4-write.md § The translation rule›.
5. Screens are reported from the snapshot and the UX spec, image first, labels as the prototype shows them.
   A field or message nothing grounds → § 8 question ‹stages/stories/4-write.md § Per story›.
6. One Gherkin `Scenario` per rule and per error path, numbered, tagged `[S#]` `[E#]` `[BR-###]`.
7. Copy open questions with their original sentence. Never edit an approved story; report it as drifted.
8. Leave `absorbed:` empty and never touch a hub — the orchestrator closes.

## Example (UC-003 E1 "slot already taken", folded)
US-001 Book a free slot — § 6:
```gherkin
Scenario: AC3 — Slot taken while choosing [E1] [BR-002]
  Given another member booked the 10:00 slot after I opened the calendar
  When I confirm the 10:00 slot
  Then I see "This slot was just taken — pick another time"
  And the calendar shows 10:00 as unavailable
```
