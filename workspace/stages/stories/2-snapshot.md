# Stage 2 — Snapshot: freeze the prototype the stories are written against

```text
runs: orchestrator (tool access: Artifact, Figma MCP, browser) — never a worker
in:   the prototype source from Stage 1 Part 6 + the UX spec's § 2 Screen Inventory
out:  03-Epics-Stories/EP-<NNN> <Feature>/_snapshot/<YYYY-MM-DD>-v<N>/  — SNAPSHOT.md, one PNG per
      screen and key state, source/ (the raw capture)
never: editing the prototype · overwriting an older snapshot folder · blocking the run
```

**Why this stage exists.** A prototype keeps changing after the stories are written. A story that links to a live
prototype silently changes meaning under the developer. Every story therefore points at a **frozen capture**: the
images and the source as they were when the story was written, plus the version they came from.

## Part 1 — Is a new capture needed?

```text
no prototype source                         → snapshot: none. Continue on the UX spec alone; add one epic
                                              § 9 question: "No prototype captured — stories carry no
                                              screen images." Never block.
latest snapshot's recorded version/hash
  equals the source's current one           → reuse it. Report "snapshot current"
otherwise                                   → new folder <today>-v<N>, N = count of folders for today + 1
```

## Part 2 — Capture, by source kind

| Source | Detect | Capture |
|---|---|---|
| **Claude Design / claude.ai artifact** | a `claude.ai/…/artifact/…` URL | `Artifact` `action: "read"` → save the HTML to `source/index.html`. Version = the artifact's last-updated time plus a SHA-256 of the HTML. Screens: one per top-level view/route/tab in the HTML; fields from `input`/`select`/`textarea` + their `label`; actions from `button`/`a`. Images: open the saved HTML in the browser (Chrome MCP `navigate` to the `file://` path, then `computer` screenshot), one per view and per visible state variant |
| **Figma / Figma Make** | a `figma.com/design/…`, `/file/…` or `/make/…` URL | `get_metadata` → `source/metadata.xml` (the frame inventory: one top-level frame = one screen). `get_design_context` per screen frame → field labels, copy, buttons. `get_screenshot` per frame, saved as PNG (or `download_assets`). Version = the file's version id / `lastModified` |
| **Open Design / plugin render** | a path under `04-UIUX/_prototypes/<run>/` | copy `index.html`, `screens/`, `RENDER.md` into `source/`. Images: the render's own screen PNGs if present, else a browser screenshot per screen. Version = the run folder name + `RENDER.md`'s `Against` |
| **Anything else** (a local HTML file, a hosted URL) | | treat as HTML: save, hash, screenshot per view |

A tool that is not connected (Figma MCP not authenticated, no browser) is reported with what to connect. The run
continues with whatever was captured; missing images become a § 8 question on each story that needed one.

Name each image `scr-<NN>-<screen-slug>[-<state>].png`, `NN` from the UX spec's § 2 order where a match exists.

## Part 3 — Map prototype screens to the design

Match every captured screen to a UX spec § 2 row (by screen name, then view id, then purpose). Record three lists:

```text
matched            prototype screen ↔ UX screen
prototype only     a screen nobody specified  → epic § 9 question: "Screen <X> is in the prototype but in no UC/UX"
design only        a specified screen the prototype lacks → epic § 9 question
```

Never resolve a mismatch by choosing a side. The use case is the requirement; the prototype is evidence of how it
looks.

## Part 4 — Write SNAPSHOT.md

```markdown
---
type: prototype-snapshot
epic: EP-<NNN>
source: <url or path>
source_kind: claude-artifact | figma | figma-make | open-design | html
source_version: <artifact updated-at | figma version id | render run>
content_hash: sha256:<…>
captured_at: <YYYY-MM-DD HH:MM>
---

| # | Screen | UX screen | State | Image |
| :--- | :--- | :--- | :--- | :--- |
| 01 | <name> | <UX § 2 name or "—"> | default | scr-01-<slug>.png |

## Gaps
- prototype only: …
- design only: …
```

A snapshot folder is **append-only**. Never edit, rename, or delete one, even to fix it — write the next version.
