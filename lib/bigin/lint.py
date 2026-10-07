#!/usr/bin/env python3
"""
bigin-lint — deterministic vault checks for the bigin-ba-workflow-plugin.

Two modes, one set of checks:

  --hook   Read a PostToolUse payload on stdin, work out whether the written file
           belongs to a Bigin vault, and run the TIER 1 checks scoped to it.
           Tier 1 is the invariant set: things that are never legitimately false,
           not even halfway through a stage. Clean -> silent exit 0.
           Findings -> exit 2 with the findings on stderr, which the harness feeds
           back to the agent that just made the write.

  --full   Run tier 1 AND tier 2 over the whole vault and print a report.
           Tier 2 holds the checks that ARE legitimately false mid-stage (a hub row
           flipped before the UC entry lands, a status before Stage 5 recounts), so
           they only make sense at a stage boundary. Exit 1 if anything was found.

  --self-test   Run the built-in fixtures. Every check must fire on a broken fixture
           and stay quiet on a clean one. This is not a substitute for a real-vault
           run; it only proves the parsers do what they claim.

  --hook --quiet
           The PostToolUse form the plugin's hooks.json runs (v1.9.0+): only findings about the
           file just written, at most 5 lines, no preamble. Prints nothing at all while
           BIGIN_BATCH=1 is set — the engine sets it while it applies change sets, so a
           transient mid-apply state never reaches an agent's context.

  --fix-citations [--apply]
           Find Signal Log rows whose Source cell cites a stale INT-### row number
           where the SAME row's own Notes cell already recorded the correct numbering
           (a prior correction that was never applied to the Source cell) and apply
           it. Never invents a correction — only a hint already on record, and only
           when that hint's own numbers fully resolve. Prints proposed fixes and does
           nothing else unless --apply is given.

Design rules this file holds itself to:

  * NEVER break a session. Any internal error, missing dependency, or unexpected
    payload exits 0 in --hook mode without output. A linter that can wedge a run is
    worse than no linter.
  * --hook is ADVISORY: findings go to stdout, exit 0. Mid-stage states legitimately
    break cross-file invariants for a few tool calls (a UC exists before its hub lists
    it), and a blocking hook there turns every such moment into a self-correction loop.
    The blocking gate is --full, run once at a stage boundary, where a finding is real.
  * NEVER fire outside a Bigin vault. No `_bigin/system/project.md` under the project
    root -> exit 0 immediately. The plugin's hooks are active wherever the plugin is
    enabled, which is not the same as wherever a vault exists.
  * Report at most MAX_PER_CHECK findings per check, with a count of the rest. A wall
    of output trains its reader to skip it.

Escape hatches, all environment variables:
  BIGIN_LINT_OFF=1        disable entirely (exit 0, always)
  BIGIN_LINT_BLOCKING=1   restore the pre-1.8.8 behaviour: --hook findings go to stderr
                          with exit 2, so the model is interrupted on every write
  BIGIN_LINT_DEBUG=1      print internal errors instead of swallowing them
  BIGIN_BATCH=1           the engine is mid-apply: --hook is silent

Home: lib/bigin/lint.py since v1.9.0 (`bin/bigin lint …`). hooks/bigin-lint.py is a
back-compat shim that imports this module.
"""

import glob
import json
import os
import re
import sys

MAX_PER_CHECK = 10
FRONTMATTER_BYTES = 8192

ARTIFACT_STATUSES = {
    "draft", "needs-clarification", "enriched", "approved", "consolidated", "removed",
}
SIGNAL_STATUSES = {
    "new", "held", "staged", "applied", "question", "conflict", "superseded", "rejected",
}
NOTE_STATUSES = {"raw", "needs-clarification", "in-review"}

# Retired or never-existent values worth naming explicitly when we see them, because
# each one is a documented past bug rather than a typo.
KNOWN_BAD = {
    "in-review": "retired on a UC/BR (conventions.md § Status vocabularies)",
    "duplicated": "does not exist anywhere in the vault vocabulary",
    "superseded": "not a UC/BR status — it belongs to the Signal Log vocabulary",
}

ID_DIRS = {
    "_ucs": ("UC", ARTIFACT_STATUSES),
    "_brs": ("BR", ARTIFACT_STATUSES),
    "_entities": ("EN", ARTIFACT_STATUSES),
}


# --------------------------------------------------------------------------- io

def read_text(path, limit=None):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read(limit) if limit else fh.read()
    except OSError:
        return ""


def frontmatter(path):
    """Parse the leading --- block into a dict. Values keep their raw text."""
    text = read_text(path, FRONTMATTER_BYTES)
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in (" ", "\t"):      # continuation of a comment block
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = strip_comment(value.strip())
    return out


def strip_comment(value):
    """Drop a trailing ` # comment`. Only splits on whitespace-hash, so a value
    that legitimately contains '#' (a step cite, a row number) survives."""
    m = re.search(r"\s+#", value)
    return (value[: m.start()] if m else value).strip()


def as_list(value):
    value = (value or "").strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [item.strip().strip("'\"") for item in value.split(",") if item.strip()]


# ----------------------------------------------------------------- md parsing

FENCE = re.compile(r"^\s*```")
SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")


def strip_fences(lines):
    """Yield (index, line) for lines outside fenced code blocks. Example tables
    live inside fences all over this vault's docs and must never be checked."""
    inside = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            yield i, line


def section(text, heading_re):
    """Return the lines of the '## ...' section whose heading matches, excluding
    the heading itself and stopping at the next '## '.

    Text inside HTML comments is blanked first (v1.9.0): a template comment that starts a line
    with '## Discussion' or '- [ ] Q:' is guidance, not a heading or a question — reading it as
    one is the class of bug behind the Agoyu truncation incident."""
    lines = _mask_comments(text.splitlines())
    start = None
    pattern = re.compile(heading_re)
    for i, line in enumerate(lines):
        if start is None:
            if pattern.match(line):
                start = i + 1
        elif line.startswith("## "):
            return lines[start:i]
    return lines[start:] if start is not None else []


def _mask_comments(lines):
    out, inside = [], False
    for line in lines:
        buf, i = [], 0
        while i < len(line):
            if inside:
                j = line.find("-->", i)
                if j < 0:
                    buf.append(" " * (len(line) - i))
                    i = len(line)
                else:
                    buf.append(" " * (j + 3 - i))
                    i, inside = j + 3, False
            else:
                j = line.find("<!--", i)
                if j < 0:
                    buf.append(line[i:])
                    i = len(line)
                else:
                    buf.append(line[i:j])
                    i, inside = j, True
        out.append("".join(buf).rstrip() if "".join(buf).strip() == "" else "".join(buf))
    return out


def split_cells(line):
    """Split one markdown table row into cells, honouring escaped pipes."""
    body = line.strip()
    if not body.startswith("|"):
        return None
    guarded = body.replace(r"\|", "\x00")
    parts = guarded.strip("|").split("|")
    return [p.replace("\x00", "|").strip() for p in parts]


def table_rows(lines):
    """Yield (offset, cells) for real table rows: outside fences, not separators."""
    for i, line in strip_fences(lines):
        cells = split_cells(line)
        if cells is None:
            continue
        if cells and all(SEPARATOR_CELL.match(c) for c in cells if c):
            continue
        yield i, cells


# ---------------------------------------------------------------- the checks

class Findings(object):
    def __init__(self):
        self.by_check = {}

    def add(self, check, message):
        self.by_check.setdefault(check, []).append(message)

    def total(self):
        return sum(len(v) for v in self.by_check.values())

    def for_file(self, relpath):
        """Messages that name ``relpath`` (per-file checks always lead with it)."""
        out = []
        for check in sorted(self.by_check):
            for m in self.by_check[check]:
                if relpath in m:
                    out.append("%s — %s" % (check, m))
        return out

    def render(self):
        out = []
        for check in sorted(self.by_check):
            items = self.by_check[check]
            out.append("%s (%d)" % (check, len(items)))
            for item in items[:MAX_PER_CHECK]:
                out.append("  - " + item)
            if len(items) > MAX_PER_CHECK:
                out.append("  … and %d more" % (len(items) - MAX_PER_CHECK))
        return "\n".join(out)


def hub_files(vault):
    """Hub summary files — never the split-off `<slug>.signals.md` companions."""
    return [p for p in sorted(glob.glob(os.path.join(vault, "01-Requirements", "_features", "*.md")))
            if not p.endswith(".signals.md")]


def signal_log_file(hub):
    """Where a hub's ## Signal Log lives: `<slug>.signals.md` once split (v1.12.0), else the hub."""
    split = hub[:-3] + ".signals.md"
    return split if os.path.exists(split) else hub


def ledger_open(vault):
    """{(hub slug, row)} and {artifact id} with an OPEN change set in 01-Requirements/_ledger."""
    rows, targets = set(), set()
    for path in glob.glob(os.path.join(vault, "01-Requirements", "_ledger", "*.jsonl")):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    e = json.loads(line)
                    if e.get("state") != "open":
                        continue
                    cs = e.get("changeset") or {}
                    tr = cs.get("trace") or {}
                    targets.add(((cs.get("target") or {}).get("id") or ""))
                    for r in tr.get("hub_rows") or []:
                        rows.add((tr.get("hub"), str(r)))
        except (OSError, ValueError):
            continue
    return rows, targets


def rel(vault, path):
    try:
        return os.path.relpath(path, vault)
    except ValueError:
        return path


# --- T1: ids are unique and match their filenames -------------------------

def check_ids(vault, findings):
    for subdir, (prefix, _statuses) in ID_DIRS.items():
        seen = {}
        for path in sorted(glob.glob(os.path.join(vault, "01-Requirements", subdir, "*.md"))):
            fm = frontmatter(path)
            declared = (fm.get("id") or "").strip()
            base = os.path.basename(path)
            m = re.match(r"^(%s-\d+)" % prefix, base)
            from_name = m.group(1) if m else None

            if not declared:
                findings.add("id missing", "%s has no `id:` in its frontmatter" % rel(vault, path))
                continue
            if from_name and declared != from_name:
                findings.add(
                    "id disagrees with filename",
                    "%s declares `id: %s`" % (rel(vault, path), declared),
                )
            if declared in seen:
                findings.add(
                    "duplicate id",
                    "%s is claimed by both %s and %s"
                    % (declared, rel(vault, seen[declared]), rel(vault, path)),
                )
            else:
                seen[declared] = path


# --- T2: table row shape --------------------------------------------------

def check_table_shape(vault, path, findings):
    """A malformed row shifts every column and breaks every stage that reads it.
    Never legitimately true, at any point in a run."""
    base = os.path.basename(path)
    text = read_text(path)
    if not text:
        return

    if base.startswith("INT-"):
        lines = section(text, r"^##\s+Extracted signals")
        expected, label = 8, "## Extracted signals"
    elif os.sep + "_features" + os.sep in path:
        lines = section(text, r"^##\s+Signal Log")
        expected, label = 7, "## Signal Log"
    else:
        return

    for offset, cells in table_rows(lines):
        if len(cells) != expected:
            findings.add(
                "malformed table row",
                "%s %s: a row has %d cells, expected %d — %s"
                % (rel(vault, path), label, len(cells), expected, preview(cells)),
            )


def preview(cells):
    joined = " | ".join(cells)
    return (joined[:70] + "…") if len(joined) > 70 else joined


# --- T3: hub Source cites resolve to real note rows -----------------------

CITE = re.compile(r"(INT-\d+)")


def note_row_numbers(vault, int_id):
    matches = sorted(glob.glob(os.path.join(vault, "00-Inbox", int_id + "*.md")))
    if not matches:
        return None
    rows = set()
    for line_no, cells in table_rows(section(read_text(matches[0]), r"^##\s+Extracted signals")):
        if not cells:
            continue
        first = cells[0].strip().strip("*")
        if first.isdigit():
            rows.add(int(first))
    return rows


def check_cites_resolve(vault, path, findings):
    """A cite pointing at a row number that no longer exists means a renumber
    happened upstream — and every other cite on this hub is then suspect."""
    lines = section(read_text(path), r"^##\s+Signal Log")
    cache = {}
    for offset, cells in table_rows(lines):
        if len(cells) < 4:
            continue
        row_id, source = cells[0].strip(), cells[3]
        for int_id in CITE.findall(source):
            if int_id not in cache:
                cache[int_id] = note_row_numbers(vault, int_id)
            rows = cache[int_id]
            if rows is None:
                findings.add(
                    "cite names a missing note",
                    "%s row #%s cites %s, which has no file in 00-Inbox/"
                    % (rel(vault, path), row_id, int_id),
                )
                continue
            head = re.split(r"—|--", source)[0]
            for token in re.findall(r"#(\d+)", head):
                if int(token) not in rows:
                    findings.add(
                        "cite does not resolve",
                        "%s row #%s cites %s #%s, which is not a row in that note"
                        % (rel(vault, path), row_id, int_id, token),
                    )


# --- fix mode: apply an already-known citation correction -----------------
#
# A recurring, hand-observed pattern: a Signal Log row's Source cell cites a stale
# INT-### row number (an earlier note got re-audited and its numbering shifted), and
# a PRIOR pass already worked out the correct numbering and recorded it in the same
# row's own Notes cell ("Citation correction ...: matches INT-018 #51") — but never
# applied that correction to the Source cell itself, so `check_cites_resolve` keeps
# flagging it forever. This mode closes exactly that loop: it never invents a
# correction, it only applies one a human/pipeline pass already wrote down and left
# stranded in Notes.

CORRECTION_HINT = re.compile(
    r"(?:matches|correct(?:ed)?(?:\s+current-numbering)?\s+citations?\s*(?:is|are)?)\s*"
    r"(INT-\d+)\s+((?:#\d+(?:\s*,\s*#\d+)*))",
    re.IGNORECASE,
)


def find_signal_log_bounds(lines):
    """Absolute [start, end) line range of the '## Signal Log' section, or None."""
    start = None
    for i, line in enumerate(lines):
        if start is None:
            if re.match(r"^##\s+Signal Log", line):
                start = i + 1
        elif line.startswith("## "):
            return start, i
    return (start, len(lines)) if start is not None else None


def propose_citation_fixes(vault, path):
    """Return a list of (line_no, old_line, new_line, reason) for this hub file."""
    text = read_text(path)
    if not text:
        return []
    lines = text.splitlines()
    bounds = find_signal_log_bounds(lines)
    if not bounds:
        return []
    start, end = bounds
    proposals = []
    cache = {}
    for i in range(start, end):
        cells = split_cells(lines[i])
        if cells is None or len(cells) < 4 or all(SEPARATOR_CELL.match(c) for c in cells if c):
            continue
        source, notes = cells[3], cells[-1]
        hints = {m.group(1): m.group(2) for m in CORRECTION_HINT.finditer(notes)}
        if not hints:
            continue
        new_source = source
        changed_for = []
        for int_id, replacement in hints.items():
            pos = new_source.find(int_id)
            if pos == -1:
                continue  # this hint's note isn't even cited here — nothing to fix
            if int_id not in cache:
                cache[int_id] = note_row_numbers(vault, int_id)
            rows = cache[int_id]
            if rows is None:
                continue
            replacement_nums = [int(n) for n in re.findall(r"#(\d+)", replacement)]
            if not replacement_nums or any(n not in rows for n in replacement_nums):
                continue  # the hint itself doesn't fully resolve either — don't guess

            # the cite "head" for this int_id runs from just after its own token to
            # the next em/en-dash (the note-title/date suffix) or the next INT-###
            # token, whichever comes first — that head is where its row numbers live.
            after = new_source[pos + len(int_id):]
            dash = re.search(r"—|--", after)
            next_id = re.search(r"INT-\d+", after[1:])
            boundary = min(
                dash.start() if dash else len(after),
                (next_id.start() + 1) if next_id else len(after),
            )
            head = after[:boundary]
            existing_nums = [int(n) for n in re.findall(r"#(\d+)", head)]
            if not existing_nums or all(n in rows for n in existing_nums):
                continue  # nothing broken for this int_id specifically — leave it

            rest = after[boundary:].lstrip()
            new_source = (
                new_source[:pos + len(int_id)] + " " + replacement + (" " + rest if rest else "")
            )
            changed_for.append("%s -> %s" % (int_id, replacement))
        if new_source != source:
            new_cells = list(cells)
            new_cells[3] = new_source.strip()
            new_line = "| " + " | ".join(new_cells) + " |"
            proposals.append((i, lines[i], new_line, "; ".join(changed_for)))
    return proposals


def run_fix_citations(root, apply_):
    vault = os.path.abspath(root or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if not is_vault(vault):
        sys.stdout.write("bigin-lint: %s is not a Bigin vault (no _bigin/system/project.md)\n" % vault)
        return 0

    total = 0
    for path in sorted(glob.glob(os.path.join(vault, "01-Requirements", "_features", "*.md"))):
        proposals = propose_citation_fixes(vault, path)
        if not proposals:
            continue
        text = read_text(path)
        lines = text.splitlines()
        for line_no, old_line, new_line, reason in proposals:
            total += 1
            sys.stdout.write("%s:%d  (%s)\n  - %s\n  + %s\n" % (rel(vault, path), line_no + 1, reason, old_line, new_line))
            if apply_:
                lines[line_no] = new_line
        if apply_ and proposals:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + ("\n" if text.endswith("\n") else ""))

    if total == 0:
        sys.stdout.write("bigin-lint: no already-known citation corrections found unapplied\n")
        return 0
    sys.stdout.write(
        "\nbigin-lint: %d fix(es) %s\n" % (total, "applied" if apply_ else "proposed (rerun with --apply to write them)")
    )
    return 0


# --- T4: step and flow ids are unique within a UC -------------------------

STEP_ID = re.compile(r"^\**\s*(S\d+)\s*\**$")
FLOW_HEADING = re.compile(r"^###\s+\**(A\d+|E\d+)\**\s*:")


def check_step_ids(vault, path, findings):
    text = read_text(path)
    seen = {}

    for offset, cells in table_rows(section(text, r"^##\s+2\.")):
        if not cells:
            continue
        m = STEP_ID.match(cells[0].strip())
        if m:
            note_id(seen, m.group(1), findings, vault, path, "§ 2")

    for _i, line in strip_fences(section(text, r"^##\s+3\.")):
        m = FLOW_HEADING.match(line.strip())
        if m:
            note_id(seen, m.group(1), findings, vault, path, "§ 3")


def note_id(seen, ident, findings, vault, path, where):
    if ident in seen:
        findings.add(
            "duplicate step/flow id",
            "%s: %s appears twice (%s and %s) — ids are permanent and never reused"
            % (rel(vault, path), ident, seen[ident], where),
        )
    else:
        seen[ident] = where


# --- T5: statuses come from the fixed vocabularies ------------------------

def check_statuses(vault, path, findings):
    base = os.path.basename(path)
    fm = frontmatter(path)
    status = (fm.get("status") or "").strip()

    if os.sep + "_features" + os.sep in path:
        for offset, cells in table_rows(section(read_text(path), r"^##\s+Signal Log")):
            if len(cells) < 5:
                continue
            value = cells[4].strip().lower()
            if not value or value == "status":
                continue
            if value not in SIGNAL_STATUSES:
                findings.add(
                    "illegal Signal Log status",
                    "%s row #%s has Status `%s`%s"
                    % (rel(vault, path), cells[0].strip(), cells[4].strip(), why_bad(value)),
                )
        return

    if base.startswith("INT-"):
        if status and status.lower() not in NOTE_STATUSES:
            findings.add(
                "illegal note status",
                "%s has `status: %s` (expected one of %s)"
                % (rel(vault, path), status, ", ".join(sorted(NOTE_STATUSES))),
            )
        return

    for subdir in ID_DIRS:
        if os.sep + subdir + os.sep in path:
            if status and status.lower() not in ARTIFACT_STATUSES:
                findings.add(
                    "illegal artifact status",
                    "%s has `status: %s`%s" % (rel(vault, path), status, why_bad(status.lower())),
                )
            return


def why_bad(value):
    return " — %s" % KNOWN_BAD[value] if value in KNOWN_BAD else ""


# --- T6: every `staged` hub row has its entry -----------------------------

def check_staged_has_entry(vault, findings):
    ledger_rows, ledger_targets = ledger_open(vault)
    for hub in hub_files(vault):
        slug = os.path.splitext(os.path.basename(hub))[0]
        for offset, cells in table_rows(section(read_text(signal_log_file(hub)), r"^##\s+Signal Log")):
            if len(cells) < 6 or cells[4].strip().lower() != "staged":
                continue
            dest, source = cells[5], cells[3]
            if (slug, cells[0].strip()) in ledger_rows:
                continue  # pending in the ledger (v1.10.0+), not in ## Discussion
            target = re.search(r"(UC-\d+|BR-\d+)", dest)
            if not target:
                findings.add(
                    "staged row with no destination",
                    "%s row #%s is `staged` but its Destination names no UC/BR"
                    % (rel(vault, hub), cells[0].strip()),
                )
                continue
            artifact = find_artifact(vault, target.group(1))
            if artifact is None:
                findings.add(
                    "staged row points at a missing artifact",
                    "%s row #%s names %s, which has no file"
                    % (rel(vault, hub), cells[0].strip(), target.group(1)),
                )
                continue
            discussion = "\n".join(section(read_text(artifact), r"^##\s+Discussion"))
            ints = CITE.findall(source)
            if target.group(1) in ledger_targets:
                continue
            # a drift question (v1.10.0) keeps the row staged: the change was NOT applied because the
            # text had been reworded, and an open question on the artifact cites this hub row
            art_text = read_text(artifact)
            if any(("hub row" in l and re.search(r"#%s\b" % re.escape(cells[0].strip()), l) and slug in l)
                   for l in art_text.splitlines() if OPEN_Q.match(l)):
                continue
            if ints and not any(i in discussion for i in ints):
                findings.add(
                    "staged row with nothing staged",
                    "%s row #%s says staged -> %s, but that file's ## Discussion cites none of %s"
                    % (rel(vault, hub), cells[0].strip(), target.group(1), ", ".join(ints)),
                )


def find_artifact(vault, ident):
    subdir = "_ucs" if ident.startswith("UC-") else "_brs"
    matches = sorted(glob.glob(os.path.join(vault, "01-Requirements", subdir, ident + "*.md")))
    return matches[0] if matches else None


# --- T7: status matches the live open-question count ----------------------

OPEN_Q = re.compile(r"^\s*-\s*\[\s\]\s*Q:")


def check_status_invariant(vault, findings):
    for path in sorted(glob.glob(os.path.join(vault, "01-Requirements", "_ucs", "*.md"))):
        text = read_text(path)
        lines = section(text, r"^##\s+5\.")
        still_open = []
        seen_decision_log = False
        for _i, line in strip_fences(lines):
            if re.match(r"^\s*\**\s*Decision log", line, re.I):
                seen_decision_log = True
            if not seen_decision_log and OPEN_Q.match(line):
                still_open.append(line.strip())

        status = (frontmatter(path).get("status") or "").strip().lower()
        if still_open and status not in ("needs-clarification", "removed"):
            findings.add(
                "status vs open questions",
                "%s has %d unchecked question(s) in § 5 Still open but `status: %s`"
                % (rel(vault, path), len(still_open), status or "(none)"),
            )
        if not still_open and status == "needs-clarification":
            findings.add(
                "status vs open questions",
                "%s is `needs-clarification` with no unchecked question in § 5 Still open"
                % rel(vault, path),
            )


# --- T8: features: <-> hub uc: both directions ----------------------------

def check_pointers(vault, findings):
    hub_uc = {}
    for hub in hub_files(vault):
        slug = os.path.splitext(os.path.basename(hub))[0]
        hub_uc[slug] = set(as_list(frontmatter(hub).get("uc")))

    uc_features = {}
    for path in sorted(glob.glob(os.path.join(vault, "01-Requirements", "_ucs", "*.md"))):
        fm = frontmatter(path)
        ident = (fm.get("id") or "").strip()
        if not ident:
            continue
        uc_features[ident] = set(as_list(fm.get("features")))
        for slug in uc_features[ident]:
            if slug not in hub_uc:
                findings.add(
                    "features: names a hub that doesn't exist",
                    "%s lists `%s`, which has no hub file" % (ident, slug),
                )
            elif ident not in hub_uc[slug]:
                findings.add(
                    "hub pointer missing",
                    "%s names feature `%s`, but that hub's `uc:` does not list it" % (ident, slug),
                )

    for slug, ids in hub_uc.items():
        for ident in ids:
            if ident in uc_features and slug not in uc_features[ident]:
                findings.add(
                    "hub claims a UC that doesn't name it",
                    "hub `%s` lists %s, but that UC's `features:` omits `%s`" % (slug, ident, slug),
                )


# --- T9: every anchored note row is cited once per feature ----------------

def check_note_coverage(vault, findings):
    hub_cites = {}
    for hub in hub_files(vault):
        slug = os.path.splitext(os.path.basename(hub))[0]
        for offset, cells in table_rows(section(read_text(signal_log_file(hub)), r"^##\s+Signal Log")):
            if len(cells) < 4:
                continue
            head = re.split(r"—|--", cells[3])[0]
            for int_id in CITE.findall(cells[3]):
                for token in re.findall(r"#(\d+)", head):
                    hub_cites.setdefault((int_id, int(token)), []).append(slug)

    for note in sorted(glob.glob(os.path.join(vault, "00-Inbox", "INT-*.md"))):
        fm = frontmatter(note)
        if (fm.get("kind") or "").strip() == "info":
            continue
        int_id = (fm.get("id") or "").strip() or os.path.splitext(os.path.basename(note))[0]
        for offset, cells in table_rows(section(read_text(note), r"^##\s+Extracted signals")):
            if len(cells) < 7:
                continue
            num, feature, status = cells[0].strip(), cells[5].strip(), cells[6].strip().lower()
            if not num.isdigit() or not feature or feature.lower().startswith("unresolved"):
                continue
            if status in ("rejected", "question"):
                continue
            slugs = [s.strip() for s in re.split(r"[,·/]| and ", feature) if s.strip()]
            cited = hub_cites.get((int_id, int(num)), [])
            for slug in slugs:
                hits = cited.count(slug)
                if hits == 0:
                    findings.add(
                        "note row cited by no hub row",
                        "%s #%s is anchored to `%s` but no Signal Log row on that hub cites it"
                        % (int_id, num, slug),
                    )
                elif hits > 1:
                    findings.add(
                        "note row cited twice on one hub",
                        "%s #%s is cited by %d rows on hub `%s` — expected exactly one per feature"
                        % (int_id, num, hits, slug),
                    )


# --- T11: branch points and enforcement points resolve to real steps -----

REMOVED_MARK = re.compile(r"\bremoved\b", re.I)


def check_step_references(vault, findings):
    """A ## 3 branch point or ## 4 enforcement point naming a step that does not
    exist — or one marked removed — is a real inconsistency, and it is the shape
    that survives a renumber without anything erroring."""
    for path in sorted(glob.glob(os.path.join(vault, "01-Requirements", "_ucs", "*.md"))):
        text = read_text(path)
        live, removed = set(), set()
        for offset, cells in table_rows(section(text, r"^##\s+2\.")):
            if not cells:
                continue
            m = STEP_ID.match(cells[0].strip())
            if not m:
                continue
            row = " ".join(cells)
            (removed if REMOVED_MARK.search(row) else live).add(m.group(1))
        if not live and not removed:
            continue

        for _i, line in strip_fences(section(text, r"^##\s+3\.")):
            m = re.search(r"\*\*(?:Branch point|Failure condition)[^:]*:\*\*\s*(S\d+)", line)
            if m:
                flag_ref(findings, vault, path, m.group(1), live, removed, "§ 3 branch point")

        for offset, cells in table_rows(section(text, r"^##\s+4\.")):
            if len(cells) < 3:
                continue
            for token in re.findall(r"\b(S\d+)\b", cells[2]):
                flag_ref(findings, vault, path, token, live, removed, "§ 4 enforcement point")


def flag_ref(findings, vault, path, ident, live, removed, where):
    if ident in live:
        return
    if ident in removed:
        findings.add(
            "reference to a removed step",
            "%s %s names %s, which is marked removed in § 2"
            % (rel(vault, path), where, ident),
        )
    else:
        findings.add(
            "reference to a step that does not exist",
            "%s %s names %s, which is not a step in § 2" % (rel(vault, path), where, ident),
        )


# ------------------------------------------------------------------ drivers

# --- T12: nothing sensitive is reproduced in requirement text -------------------
# Part E of the restructure plan: no e-mail addresses, key-like tokens, or internal hostnames in
# UC/BR/hub text. Describe them instead ("the configured OTP-bypass value", "the staging host").

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
KEYLIKE = re.compile(
    r"\b(?:AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abp]-[A-Za-z0-9-]{10,}"
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"
    r"|(?=[A-Za-z0-9+]*[0-9])(?=[A-Za-z0-9+]*[a-z])(?=[A-Za-z0-9+]*[A-Z])[A-Za-z0-9+]{40,}={0,2})\b")
HOSTLIKE = re.compile(
    r"\b(?:(?:10|127)\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
    r"|[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:internal|local|lan|corp|intranet)(?![.\w-]))", re.I)


def check_secrets(vault, findings):
    paths = sorted(glob.glob(os.path.join(vault, "01-Requirements", "_ucs", "*.md"))) + \
        sorted(glob.glob(os.path.join(vault, "01-Requirements", "_brs", "*.md"))) + \
        sorted(glob.glob(os.path.join(vault, "01-Requirements", "_features", "*.md")))
    for path in paths:
        text = re.sub(r"<!--.*?-->", "", read_text(path), flags=re.S)
        for label, rx in (("e-mail address", EMAIL), ("key-like token", KEYLIKE), ("internal host", HOSTLIKE)):
            m = rx.search(text)
            if m:
                shown = m.group(0)
                shown = shown[:4] + "…" if label != "internal host" else shown
                findings.add("sensitive value reproduced",
                             "%s: %s (%s) — describe it, never reproduce it" % (rel(vault, path), label, shown))


# --- T13: question-status rows have a matching question -----------------------

Q_START = re.compile(r"^\s*(is|should|which|what|does|can|confirm|whether|where|how|why|are|who|when)\b", re.I)
BEARS_ON = re.compile(r"\b(bears?\s+on|bearing\s+on|extends|restates|duplicate\s+of|cross-reference|pain-point|inferred|gap|precedence)\b", re.I)


def check_question_rows(vault, findings):
    """A Signal Log row at status question/conflict must have a matching open question
    on its hub, or on the UC/BR it names (booking-lifecycle #22 fixture)."""
    hub_qs = {}
    for hub in hub_files(vault):
        slug = os.path.splitext(os.path.basename(hub))[0]
        text = read_text(hub)
        hub_qs[slug] = [l for l in text.splitlines() if re.search(r"-\s*\[[ xX]\]\s*Q:", l)]

    art_qs = {}
    for p in sorted(glob.glob(os.path.join(vault, "01-Requirements", "_ucs", "*.md"))) + \
             sorted(glob.glob(os.path.join(vault, "01-Requirements", "_brs", "*.md"))):
        ident = os.path.basename(p).split()[0].split(".")[0]
        text = read_text(p)
        art_qs[ident] = [l for l in text.splitlines() if re.search(r"-\s*\[[ xX]\]\s*Q:", l)]

    note_qs = {}
    for p in sorted(glob.glob(os.path.join(vault, "00-Inbox", "INT-*.md"))):
        ident = os.path.basename(p).split()[0].split(".")[0]
        text = read_text(p)
        note_qs[ident] = [l for l in text.splitlines() if re.search(r"-\s*\[[ xX]\]\s*Q:", l)]

    for hub in hub_files(vault):
        slug = os.path.splitext(os.path.basename(hub))[0]
        sp = signal_log_file(hub)
        for offset, cells in table_rows(section(read_text(sp), r"^##\s+Signal Log")):
            if len(cells) < 6:
                continue
            status = cells[4].strip().lower()
            if status not in ("question", "conflict"):
                continue

            num = cells[0].strip()
            sig = cells[1].strip() if len(cells) > 1 else ""
            source = cells[3].strip() if len(cells) > 3 else ""
            dest = cells[5].strip() if len(cells) > 5 else ""
            notes = cells[6].strip() if len(cells) > 6 else ""

            if "?" in sig or "SME question" in sig or "Q-" in notes or "Q-" in sig:
                continue
            if BEARS_ON.search(notes) or BEARS_ON.search(sig) or Q_START.match(sig):
                continue

            cites = set()
            for int_id in CITE.findall(source):
                for token in re.findall(r"#(\d+)", re.split(r"—|--", source)[0]):
                    cites.add((int_id, int(token)))

            matched = False
            for q in hub_qs.get(slug, []):
                if cites and any(f"{nid} #{n}" in q or f"{nid} #{n:03d}" in q or f"#{n}" in q for nid, n in cites):
                    matched = True
                    break
                if re.search(rf"\b(?:hub\s+rows?|rows?)\s*(?:#[0-9a-z,\-–\s]*\b)?#{re.escape(num)}\b", q, re.I):
                    matched = True
                    break

            if matched:
                continue

            for aid in re.findall(r"\b(?:UC|BR)-\d+\b", dest):
                for q in art_qs.get(aid, []):
                    if cites and any(f"{nid} #{n}" in q or f"{nid} #{n:03d}" in q or f"#{n}" in q for nid, n in cites):
                        matched = True
                        break
                    if re.search(rf"\b(?:hub\s+rows?|rows?)\s*(?:#[0-9a-z,\-–\s]*\b)?#{re.escape(num)}\b", q, re.I):
                        matched = True
                        break
                if matched:
                    break

            if matched:
                continue

            for h_slug, q_list in hub_qs.items():
                if h_slug != slug:
                    for q in q_list:
                        if cites and any(f"{nid} #{n}" in q or f"{nid} #{n:03d}" in q or f"#{n}" in q for nid, n in cites):
                            matched = True
                            break
                    if matched:
                        break

            if not matched and cites:
                for nid, n in cites:
                    for q in note_qs.get(nid, []):
                        if f"#{n}" in q or f"#{n:03d}" in q:
                            matched = True
                            break
                    if matched:
                        break

            if not matched:
                findings.add(
                    "question row with no question",
                    f"{rel(vault, hub)} row #{num} is `{status}` but has no matching question on its hub or destination",
                )


# --- T8: epics and user stories (03-Epics-Stories/) ------------------------

def check_story_file(vault, path, findings):
    """Per-file: id agrees with the file name, frontmatter matches schema/{epic,story}.json, hard
    rule S1 (business language only), and every mermaid block opens with a diagram type."""
    from bigin import stories
    kind = stories.kind_of(path)
    if not kind:
        return
    r = rel(vault, path)
    fm = frontmatter(path)
    declared = (fm.get("id") or "").strip()
    m = re.match(r"^((?:EP|US)-\d+)", os.path.basename(path))
    if not declared:
        findings.add("id missing", "%s has no `id:` in its frontmatter" % r)
    elif m and declared != m.group(1):
        findings.add("id disagrees with filename", "%s declares `id: %s`" % (r, declared))
    for err in stories.schema_errors(fm, kind):
        findings.add("%s frontmatter" % kind, "%s: %s" % (r, err))
    text = read_text(path)
    for line_no, term in stories.technical_terms(text)[:5]:
        findings.add("technical wording (S1)",
                     "%s:%d uses `%s` — a story is business language only; say what the user sees or "
                     "what the business needs" % (r, line_no, term))
    for line_no, msg in stories.mermaid_errors(text):
        findings.add("mermaid block", "%s:%d %s" % (r, line_no, msg))


def check_story_links(vault, findings):
    """Cross-file: ids unique, story ↔ epic both ways, source UCs exist, pinned snapshots exist."""
    from bigin import stories
    base = os.path.join(vault, "03-Epics-Stories")
    epics, seen = {}, {}
    paths = sorted(glob.glob(os.path.join(base, "*", "EP-*.md"))) + sorted(glob.glob(os.path.join(base, "*", "US-*.md")))
    for path in paths:
        ident = (frontmatter(path).get("id") or "").strip()
        if not ident:
            continue
        if ident in seen:
            findings.add("duplicate id", "%s is claimed by both %s and %s"
                         % (ident, rel(vault, seen[ident]), rel(vault, path)))
        else:
            seen[ident] = path
        if stories.kind_of(path) == "epic":
            epics[ident] = path
    for path in paths:
        fm = frontmatter(path)
        r = rel(vault, path)
        folder = os.path.dirname(path)
        snap = (fm.get("snapshot") or "").strip().strip("'\"")
        if snap and snap != "none" and not os.path.isfile(os.path.join(folder, "_snapshot", snap, "SNAPSHOT.md")):
            findings.add("snapshot missing", "%s pins `snapshot: %s` but %s has no SNAPSHOT.md"
                         % (r, snap, rel(vault, os.path.join(folder, "_snapshot", snap))))
        if stories.kind_of(path) == "epic":
            for uc in as_list(fm.get("source_ucs")):
                if not glob.glob(os.path.join(vault, "01-Requirements", "_ucs", uc + " *.md")):
                    findings.add("pointer to a missing artifact", "%s lists source UC %s, which has no file" % (r, uc))
            for us in as_list(fm.get("stories")):
                if us not in seen:
                    findings.add("pointer to a missing artifact", "%s lists %s, which has no file" % (r, us))
            continue
        sid, epic = (fm.get("id") or "").strip(), (fm.get("epic") or "").strip()
        if epic not in epics:
            findings.add("story without its epic", "%s names epic `%s`, which has no file" % (r, epic or "—"))
            continue
        if os.path.dirname(epics[epic]) != folder:
            findings.add("story without its epic", "%s belongs to %s but sits outside that epic's folder" % (r, epic))
        if sid and sid not in as_list(frontmatter(epics[epic]).get("stories")):
            findings.add("story without its epic", "%s is not listed in %s's `stories:`" % (r, epic))


TIER1_GLOBAL = [check_ids]
TIER2 = [check_secrets, check_staged_has_entry, check_question_rows, check_status_invariant, check_pointers, check_note_coverage,
         check_step_references, check_story_links]


def tier1_for_file(vault, path, findings):
    check_table_shape(vault, path, findings)
    check_statuses(vault, path, findings)
    if os.sep + "_features" + os.sep in path:
        check_cites_resolve(vault, path, findings)
    if os.sep + "_ucs" + os.sep in path:
        check_step_ids(vault, path, findings)
    if os.sep + "03-Epics-Stories" + os.sep in path:
        check_story_file(vault, path, findings)


def is_vault(root):
    return os.path.isfile(os.path.join(root, "_bigin", "system", "project.md"))


def in_scope(vault, path):
    """Only files this linter has checks for, and never plugin-owned copies."""
    norm = os.path.normpath(path)
    for skip in (os.sep + "_bigin" + os.sep, os.sep + "_attachments" + os.sep,
                 os.sep + "templates" + os.sep, os.sep + ".git" + os.sep):
        if skip in norm:
            return False
    if not norm.endswith(".md"):
        return False
    inbox = os.path.join(vault, "00-Inbox") + os.sep
    reqs = os.path.join(vault, "01-Requirements") + os.sep
    if norm.startswith(inbox):
        return os.path.basename(norm).startswith("INT-")
    if norm.startswith(os.path.join(vault, "03-Epics-Stories") + os.sep):
        return os.sep + "_snapshot" + os.sep not in norm and os.path.basename(norm)[:3] in ("EP-", "US-")
    if norm.startswith(reqs):
        return any(os.sep + d + os.sep in norm for d in ID_DIRS) or \
            os.sep + "_features" + os.sep in norm
    return False


def run_hook(quiet=False):
    if os.environ.get("BIGIN_LINT_OFF") == "1":
        return 0
    if quiet and os.environ.get("BIGIN_BATCH") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if not path:
        return 0

    vault = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    vault = os.path.abspath(vault)
    if not is_vault(vault):
        return 0

    path = path if os.path.isabs(path) else os.path.join(vault, path)
    path = os.path.abspath(path)
    if not in_scope(vault, path) or not os.path.isfile(path):
        return 0

    findings = Findings()
    tier1_for_file(vault, path, findings)
    if quiet:
        # only what this write caused, in this file — never the vault's backlog
        mine = findings.for_file(rel(vault, path))
        if not mine:
            return 0
        lines = ["bigin-lint (advisory): %s" % m for m in mine[:5]]
        if len(mine) > 5:
            lines.append("bigin-lint: … %d more — `bin/bigin lint --full` at the stage boundary" % (len(mine) - 5))
        sys.stdout.write("\n".join(lines) + "\n")
        return 0
    for check in TIER1_GLOBAL:
        check(vault, findings)

    if not findings.total():
        return 0

    body = (
        "bigin-lint: %d invariant issue(s) after that write — ADVISORY, not a stop.\n"
        "Some of these are normal mid-stage: a new UC exists for a moment before its hub lists it,\n"
        "a row is cited before the row it cites is appended. Do NOT abandon what you were doing to\n"
        "chase them. Finish the step you are on; the stage's own `--full` gate is what blocks, and\n"
        "anything still listed there is real.\n\n%s\n"
        % (findings.total(), findings.render())
    )
    if os.environ.get("BIGIN_LINT_BLOCKING") == "1":
        sys.stderr.write(body)
        return 2
    sys.stdout.write(body)
    return 0


def run_full(root):
    vault = os.path.abspath(root or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if not is_vault(vault):
        sys.stdout.write("bigin-lint: %s is not a Bigin vault (no _bigin/system/project.md)\n" % vault)
        return 0

    findings = Findings()
    for check in TIER1_GLOBAL:
        check(vault, findings)
    for path in sorted(glob.glob(os.path.join(vault, "01-Requirements", "**", "*.md"), recursive=True)) \
            + sorted(glob.glob(os.path.join(vault, "00-Inbox", "INT-*.md"))) \
            + sorted(glob.glob(os.path.join(vault, "03-Epics-Stories", "*", "*.md"))):
        if in_scope(vault, os.path.abspath(path)):
            tier1_for_file(vault, os.path.abspath(path), findings)
    for check in TIER2:
        check(vault, findings)

    ver = "unknown"
    try:
        from bigin import __version__
        ver = __version__
    except ImportError:
        pass
    ppath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if not findings.total():
        sys.stdout.write("bigin-lint v%s (%s): clean (tier 1 + tier 2) over %s\n" % (ver, ppath, vault))
        return 0
    sys.stdout.write("bigin-lint v%s (%s): %d finding(s) over %s\n\n%s\n" % (ver, ppath, findings.total(), vault, findings.render()))
    return 1


# --------------------------------------------------------------- self-test

CLEAN_NOTE = """---
id: INT-001
type: intake
kind: requirement
status: in-review
---

## Extracted signals

| # | Type | Signal | Why | Source | Feature | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | requirement | Applicant uploads proof of income | audit trail | [00:12:03] | grant-intake | new | |
| 2 | constraint | Only PDF is accepted | file handling | [00:13:10] | grant-intake | new | |

## Open Questions
"""

CLEAN_HUB = """---
type: feature-hub
feature: grant-intake
name: Grant intake
status: committed
uc: [UC-001]
br: []
---

## Signal Log

| # | Signal | Type | Source | Status | Destination | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Proof of income** — applicant uploads it; only PDF accepted | requirement + constraint | INT-001 #1, #2 — Jane Doe 2026-08-05 | applied | UC-001 S3 | |

## Use Cases

| UC | Goal | Role | Status |
| :--- | :--- | :--- | :--- |
| UC-001 | Submit a grant application | owns | draft |
"""

CLEAN_UC = """---
id: UC-001
type: use-case
title: Submit a grant application
status: draft
version: 1.0
primary_feature: grant-intake
features: [grant-intake]
sources: [INT-001]
---

## 1. Context & Metadata

## 2. Main Success Scenario

| Step | Actor Action | System Response & Validation |
| :--- | :--- | :--- |
| **S1** | Applicant opens the form | System shows it, prefilled |
| **S3** | Applicant uploads proof of income | System accepts a PDF and records it |

## 3. Alternative & Exception Flows

### E1: Proof of income is unreadable
* **Branch point:** S3
* **Condition:** the file is not a PDF
1. System rejects it
2. **Rejoins** S3

## 4. Business Rules & Compliance Constraints

## 5. Open Questions & Decision Log

**Still open**

**Decision log**

| # | Topic | Raised by / source | Decision | Date |
| :--- | :--- | :--- | :--- | :--- |

## 6. Special Requirements & Related Information

## Discussion

## Changelog
"""


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _build(root, note=CLEAN_NOTE, hub=CLEAN_HUB, uc=CLEAN_UC, extra=None):
    _write(os.path.join(root, "_bigin", "system", "project.md"), "workspace_version: 1.6.6\n")
    _write(os.path.join(root, "00-Inbox", "INT-001.md"), note)
    _write(os.path.join(root, "01-Requirements", "_features", "grant-intake.md"), hub)
    _write(os.path.join(root, "01-Requirements", "_ucs", "UC-001 Submit a grant application.md"), uc)
    for path, text in (extra or {}).items():
        _write(os.path.join(root, path), text)
    return root


def _scan(root):
    findings = Findings()
    for check in TIER1_GLOBAL:
        check(root, findings)
    for path in sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True)):
        p = os.path.abspath(path)
        if in_scope(root, p):
            tier1_for_file(root, p, findings)
    for check in TIER2:
        check(root, findings)
    return findings


def run_self_test():
    import shutil
    import tempfile

    cases = []

    def case(name, expect, **kw):
        cases.append((name, expect, kw))

    # The clean vault must be silent. If this fails, every other result is noise.
    case("clean vault", None)

    case("malformed table row", "malformed table row",
         note=CLEAN_NOTE.replace(
             "| 2 | constraint | Only PDF is accepted | file handling | [00:13:10] | grant-intake | new | |",
             "| 2 | constraint | Only PDF is accepted | file handling | [00:13:10] | grant-intake | new |"))

    case("cite does not resolve", "cite does not resolve",
         hub=CLEAN_HUB.replace("INT-001 #1, #2 —", "INT-001 #1, #9 —"))

    case("cite names a missing note", "cite names a missing note",
         hub=CLEAN_HUB.replace("INT-001 #1, #2 —", "INT-044 #1 —"))

    case("duplicate step id", "duplicate step/flow id",
         uc=CLEAN_UC.replace("| **S1** | Applicant opens the form", "| **S3** | Applicant opens the form"))

    case("illegal artifact status", "illegal artifact status",
         uc=CLEAN_UC.replace("status: draft", "status: in-review"))

    case("illegal Signal Log status", "illegal Signal Log status",
         hub=CLEAN_HUB.replace("| applied | UC-001 S3 |", "| duplicated | UC-001 S3 |"))

    case("duplicate id across files", "duplicate id",
         extra={"01-Requirements/_ucs/UC-001 Something else.md": CLEAN_UC})

    case("id disagrees with filename", "id disagrees with filename",
         extra={"01-Requirements/_ucs/UC-007 Mismatched.md": CLEAN_UC.replace("id: UC-001", "id: UC-009")})

    case("staged row with nothing staged", "staged row with nothing staged",
         hub=CLEAN_HUB.replace("| applied | UC-001 S3 |", "| staged | UC-001 |"))

    case("status vs open questions", "status vs open questions",
         uc=CLEAN_UC.replace("**Still open**", "**Still open**\n\n- [ ] Q: Which formats count? (owner: client)\n      A:"))

    case("hub pointer missing", "hub pointer missing",
         uc=CLEAN_UC.replace("features: [grant-intake]", "features: [grant-intake, payments]",),
         extra={"01-Requirements/_features/payments.md": CLEAN_HUB
                .replace("feature: grant-intake", "feature: payments")
                .replace("uc: [UC-001]", "uc: []")
                .replace("INT-001 #1, #2", "INT-001 #1")})

    case("note row cited by no hub row", "note row cited by no hub row",
         hub=CLEAN_HUB.replace("INT-001 #1, #2 —", "INT-001 #1 —"))

    case("branch point names a missing step", "reference to a step that does not exist",
         uc=CLEAN_UC.replace("* **Branch point:** S3", "* **Branch point:** S7"))

    case("enforcement point names a removed step", "reference to a removed step",
         uc=CLEAN_UC
         .replace("| **S3** | Applicant uploads proof of income | System accepts a PDF and records it |",
                  "| **S3** | ~~Applicant uploads proof of income~~ | removed — no longer required |")
         .replace("## 4. Business Rules & Compliance Constraints\n",
                  "## 4. Business Rules & Compliance Constraints\n\n"
                  "| Rule | Statement (short) | Enforced at |\n"
                  "| :--- | :--- | :--- |\n"
                  "| BR-004 | Only PDF is accepted | S3 |\n")
         .replace("* **Branch point:** S3", "* **Branch point:** S1"))

    case("question row with no question", "question row with no question",
         hub=CLEAN_HUB.replace("| applied | UC-001 S3 |", "| question | |"))

    failures = []
    for name, expect, kw in cases:
        root = tempfile.mkdtemp(prefix="bigin-lint-selftest-")
        try:
            _build(root, **kw)
            found = _scan(root)
            keys = set(found.by_check)
            if expect is None:
                if keys:
                    failures.append("%s: expected silence, got %s" % (name, sorted(keys)))
            elif expect not in keys:
                failures.append("%s: expected check %r to fire, got %s" % (name, expect, sorted(keys) or "nothing"))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    for name, _e, _k in cases:
        sys.stdout.write("  case: %s\n" % name)
    if failures:
        sys.stdout.write("\nFAILED (%d of %d):\n" % (len(failures), len(cases)))
        for line in failures:
            sys.stdout.write("  - %s\n" % line)
        return 1
    sys.stdout.write("\nself-test: %d/%d cases pass\n" % (len(cases), len(cases)))
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--hook"
    try:
        if mode == "--hook":
            return run_hook(quiet="--quiet" in argv[2:])
        if mode == "--full":
            return run_full(argv[2] if len(argv) > 2 else None)
        if mode == "--self-test":
            return run_self_test()
        if mode == "--fix-citations":
            return run_fix_citations(argv[2] if len(argv) > 2 and argv[2] != "--apply" else None,
                                      "--apply" in argv[2:])
        sys.stderr.write(__doc__)
        return 64
    except Exception:
        if os.environ.get("BIGIN_LINT_DEBUG") == "1":
            raise
        return 0 if mode == "--hook" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
