---
type: conventions
updated: <YYYY-MM-DD>
---

# Project Conventions

Optional project-specific overrides for `/bigin-intake`, `/extract-signal`, and
`/bigin-new-project`'s domain research step. Anything written here takes precedence over the
plugin's built-in defaults in `_bigin/stages/extract/2-extraction.md` (extraction), `3-filing.md`
(anchoring and filing), and `skills/bigin-new-project/references/domain-research.md` (domain
research method). Leave a section empty to fall back to those defaults.

## Domain research method

<!-- How /bigin-new-project § 5.3 should research a new project's domain, instead of its built-in
WebSearch-based method (skills/bigin-new-project/references/domain-research.md). Leave blank for
the built-in method. To delegate instead:
  skill: <installed-skill-name>       — dispatched headlessly via the Skill tool
  agent: <subagent-type>              — dispatched via one Agent call
-->

## Why phrasing

<!-- House style for how a Signal Log `Why` cell should be worded/punctuated, if this client's
team wants something more specific than "quote the source, plain sentence, or `not stated`." -->

## Standing feature mappings

<!-- Signals that should never raise an `unresolved` anchoring question because they always map
to one obvious slug — e.g. a keyword or product name this client uses that isn't otherwise
recognizable from the FEATURES.md row alone. -->

| Signal pattern | Feature slug |
| --- | --- |

## Other overrides

<!-- Anything else project-specific that `/bigin-intake` or `/extract-signal` should honor over
the plugin defaults. -->
