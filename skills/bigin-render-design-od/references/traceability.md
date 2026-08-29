# The traceability contract — provenance in attributes, never in copy

A rendered prototype has to carry machine-readable provenance back to the vault, and it has to carry
**none of it where a person can see it**. Those are the two halves of one contract, and
`scripts/check-traceability.sh` is the deterministic gate for both.

This file survives the retirement of the fully-expanded prompt contract. `/bigin-render-design-od`
hands Open Design the real vault files rather than a nine-section brief, so the id-expansion rules
that governed that brief no longer apply — but the attribute vocabulary below still does, because it
is what the checker enforces and what `## 8 Rendered Artifacts` traces against.

## § The block to quote

Quote this verbatim into every feature prompt and into the assembly prompt. It is the one place ids
legitimately enter a prompt:

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

## § The gate

```bash
"$SKILL_DIR/scripts/check-traceability.sh" <file-or-dir> [<file-or-dir> …] [--require]
```

| Half | What it asserts |
| :--- | :--- |
| **Positive** | the `data-*` attributes above are present. `--require` makes their absence a failure rather than a warning |
| **Negative** | no `/(UC\|BR\|EN\|UX)-\d/` appears in any **visible** position — text nodes, `aria-label`, `title`, `alt`, `placeholder`, `value`, `<option>` bodies, CSS `content:` |

A negative-half failure is never a warning. An id a client can read is a leaked internal reference,
and the render is not deliverable until it is gone.
