# Prototype

One HTML file per feature. It must open by double-click, with no server and no internet.

## Build rules

- A single `.html` file: inline CSS and JavaScript, no external files, fonts or libraries.
- One `<section>` per screen, one visible at a time. Buttons and links move between screens.
- Each screen has `data-screen="<Screen name>"`. Each element that comes from a requirement has
  `data-source="UC-003 S2"` or `data-source="BR-004"`. An assumed element has `data-source="assumed"`.
- Follow the `platform` in `bigin.md`: a desktop layout for `web`, a phone-width frame for `mobile`.
- Show each state the design file lists (empty, loading, error, success) with a small state switch
  at the top of the screen.
- Use realistic sample data in the client's own terms. Never real names, emails or account numbers.
- Plain look: system font, greys and one accent colour, good contrast, visible focus.

## Review bar

Add one bar above the screens, for reviewers:

- the design id and version, and a screen picker
- a "Show sources" switch that outlines each element and prints its `data-source` next to it, with
  assumed elements in a different outline

## Check before you finish

- [ ] Every screen in the design file is in the prototype, and no extra screen exists
- [ ] Every flow line of the design can be clicked through from start to end
- [ ] Every interactive element has a `data-source`
- [ ] The file opens with no console error
