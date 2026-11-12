# Confluence / shared docs — provider detail for `/bigin-intake` Stage 2E

One INT note per page, for the page's life (`source: confluence`). The skill only **fetches**; the engine
(`bigin intake confluence`) does the section diff, the heading demotion and the high-water mark. Read tools only —
never create, edit or comment on a page.

## Watch list (`project.md`)

```yaml
confluence_pages: []    # page ids or full URLs to track, e.g. [12345, https://acme.atlassian.net/wiki/spaces/PRD/pages/67890]
confluence_labels: []   # optional: also pick up pages carrying any of these labels, e.g. [requirements]
```

Both empty → Stage 2E is skipped.

## Tools (Atlassian MCP, claude.ai connector)

Match by capability; the names have moved between connector versions. Name the missing capability if one is
absent — never fall back to WebFetch on a Confluence URL.

```text
getConfluenceContent   → one page: id, title, version number, space, body (convert to markdown if the tool
                         returns storage format; an ADF document may be passed as-is), last-modified, author
searchConfluence       → pages by label or space, with a last-modified filter:
                         label in (<confluence_labels>) AND lastmodified >= "<timeframe>"
```

For each id in `confluence_pages` (resolve a URL to its numeric id) and each page the label search returns:

## Fetch → one file, unmodified

```text
{inbox_dir}/_raw/confluence-in/<pageId>.json =
  {"id": "<pageId>", "title": "...", "version": <number>, "space": "<KEY>", "url": "<page url>",
   "updated": "YYYY-MM-DD", "author": "<last editor>", "body": "<markdown, or the ADF document>"}
```

Never trim, translate or summarise the body. (The engine keeps its own copy of the last captured body under
`{inbox_dir}/_raw/confluence/<pageId>.json` — never write there.)

## Capture

```text
BIN intake confluence --page {inbox_dir}/_raw/confluence-in/<pageId>.json
    new page          → minted INT-### (source: confluence), one `section` block per heading
    newer version     → each changed or added section appended as one block; a removed section as a `removed`
                        block (the extractor turns it into a `supersedes` row); the note returns to status: raw
    same / older      → reported "unchanged", nothing written
```

Report the action per page. A page that returns not-found is reported, never guessed at.
