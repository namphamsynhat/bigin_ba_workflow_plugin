# Card — ux-brief-assembler (model: sonnet — fast mechanical assembly)

**In:** feature slug, in-scope UCs, platform (`web | mobile | both`), optional existing UX spec path, nav map path. Read `{hub_dir}/<slug>.md`, every in-scope UC (§ 1–§ 5), cited `BR-###` rules, cited `EN-###` entities, `{design_principles_file}`, hub `## Pain Points`, `{nav_map_file}`.
**Out:** structured Design Brief JSON written to `.out.json` (or returned in response). Read-only; never touches any vault file.

## Rules
1. **Flows to candidate screens:** A run of steps by the same actor in the same place is one candidate screen; system-only step is not a screen; validation is a state; exception flow (E#) is a named error state; alternative flow (A#) or flow changing place is its own screen ‹stages/design/3-screens.md § Part 2›.
2. **Actor scope:** Surface who sees whose data, how many records (cardinality from EN), and whether anything grants acting on many — report verbatim facts only, never render a volume band or split verdict ‹stages/design/3-screens.md § Part 2a›.
3. **Candidate merges:** If two UCs land on the same place, propose a merge candidate and report whether actor data scopes agree.
4. **Known gaps:** Every unchecked question in UC `## 5` and hub `## Coverage Gaps` is quoted verbatim; never resolve or design around a gap.
5. **Pain points:** Report every unresolved `PP-###` from the hub verbatim; never assign which flow resolves which.
6. **Platform signal:** Use the platform you were handed; report any source explicitly stating a platform constraint as fact on `platform_signal`.
7. **Sibling patterns:** Grep `{ux_dir}` for keywords (`queue`, `wizard`, `approval`); inspect at most one matching spec.
8. **Relationship signals:** Surface entity fields storing per-user history/preference (material for Part 4b trigger; do not render verdict).
9. **Never write any vault file:** You have no Write/Edit permissions.

## Output Schema
```json
{
  "feature": "<slug>",
  "brief": "<summary paragraph: actors, platform, principles, directives>",
  "known_gaps": ["<verbatim gap question>"],
  "candidate_screens": [
    {"name": "<screen name>", "serves": ["UC-### S1", "..."], "entities": ["EN-###"], "pattern": "<existing pattern or none>"}
  ],
  "merges": [
    {"ucs": ["UC-###", "UC-###"], "target_screen": "<screen>", "actors": "<actor A> vs <actor B>", "scope_agrees": "yes|no|unknown"}
  ],
  "actor_scope_signals": [
    {"actor": "<actor>", "sees_whose": "<rule>", "how_many": "<cardinality>", "acts_on_many": "<rule>"}
  ],
  "nav_signal": [
    {"screen": "<screen>", "from_menu": true, "joins_branch": "<branch id>"}
  ],
  "pain_points_open": ["PP-### — <statement>"],
  "platform_signal": "<verbatim statement or none>",
  "relationship_signals": ["EN-###.<field> — <description>"],
  "existing_spec": "<summary or none>",
  "blocked": ["<unresolved references>"]
}
```
