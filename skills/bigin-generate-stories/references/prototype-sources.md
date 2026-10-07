# Prototype sources — how Stage 2 captures each kind

Load the tools you need in **one** `ToolSearch` call before capturing. Everything captured lands in
`_snapshot/<YYYY-MM-DD>-v<N>/`; the live prototype is never linked from a story.

## Claude Design / claude.ai artifact

```text
detect      claude.ai/artifact/<id> · claude.ai/code/artifact/<uuid>
read        Artifact(action: "read", url: <url>)  → raw HTML for the person's own artifact
            (someone else's artifact returns a summary, not HTML: capture what it gives, mark
             source_kind: claude-artifact-summary, and add a § 9 question asking for edit access or an export)
save        source/index.html  (+ any published files listed by Artifact(action:"list", scope:"files"))
version     the artifact's last-updated time + sha256 of the HTML
images      browser: open file://<abs path>/source/index.html, screenshot each view; switch views by the
            prototype's own navigation (tabs, links, buttons) — never by editing the HTML
```

A Claude Design **handoff bundle** (HTML/CSS/JS + per-state screenshots + README) supplied as a folder or zip is
treated like Open Design: copy into `source/`, reuse its screenshots as the images.

## Figma / Figma Make

```text
detect      figma.com/design/<key>/… · figma.com/file/<key>/… · figma.com/make/<key>/…
inventory   get_metadata(fileKey, nodeId of the page)  → source/metadata.xml; top-level frames = screens
details     get_design_context(fileKey, nodeId) per screen frame  → labels, copy, controls
            (keep only what the business sees; the returned code is discarded, never quoted — S1)
images      get_screenshot(fileKey, nodeId) per frame → scr-<NN>-<slug>.png
            (download_assets when screenshots must be saved as files)
version     the file's version / lastModified, as returned
```

Figma not authenticated → report `connect Figma: run the Figma MCP authenticate tool`, continue without images.

## Open Design / plugin render

```text
detect      a path under 04-UIUX/_prototypes/<run>/, or UX § 8's latest row
copy        index.html, screens/, RENDER.md → source/
images      the render's own screen images if present, else a browser screenshot per screen
version     <run folder> + RENDER.md "Against" (UX-###@version)
```

## No browser available

Save the source and write SNAPSHOT.md with an `Image` column of `—`. Each story's § 5 keeps its field, action,
and state tables from the source, and § 8 carries: "Screen image not captured — no browser in this run."
