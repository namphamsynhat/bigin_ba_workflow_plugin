#!/usr/bin/env python3
"""check-navigation.py — flags a rendered prototype that gave a drill-down screen its own nav link.

A navigation-map.md `## Structure` row's `Points to` cell can name several screens — that is
master-detail / drill-down, one menu entry covering both (`design-navigation.md` § The navigation
map). The FIRST screen named is the entry's direct destination; every screen after it is a
drill-down-only destination, reached only through a control on a screen already in that list, and
must never get a persistent nav link of its own.

This is a HEURISTIC, not a hard gate (`references/navigation-contract.md` § The gate): rendered HTML
shapes vary too much between Open Design runs for a certain parse. It flags a drill-down-only
screen's name turning up as text inside something that LOOKS like its own clickable nav element — an
<a>/<button>, an onclick/data-nav/data-goto attribute, or its own entry in a JS nav/menu array or
object literal — for a human to actually look at. A page title reusing the same words is a false
positive; a second sidebar link is the real failure this script exists to catch.

It does NOT check for a screen absent from ## Structure entirely (that would need cross-referencing
every UX spec's own Screen Inventory, out of scope for a cheap gate) — only the multi-screen-cell
case, which is the one this plugin has actually seen fail.

usage:
    check-navigation.py <navigation-map.md> <file-or-dir> [<file-or-dir> ...]

exit 0  no drill-down-only screen found inside a nav-shaped element
exit 1  at least one finding — review each one
exit 2  could not run (nav map missing, no targets, nothing to scan)
"""
import re
import sys
from pathlib import Path

TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
SEP_ROW_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")

SCAN_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".js"}

# a line that looks like it renders an interactive nav-style element
INTERACTIVE_RE = re.compile(
    r"<a\b|<button\b|href=|onclick=|data-nav=|data-goto=|data-screen=|data-go=",
    re.IGNORECASE,
)
# a line that looks like a JS nav/menu data literal: quoted strings inside [] or {}
JS_LITERAL_RE = re.compile(r"[\[{][^\[{}\]]*[\"'][^\"']+[\"'][^\[{}\]]*[\]}]")
HEADING_RE = re.compile(r"<h[1-6]\b")


def parse_nav_map(path: Path):
    """Returns the set of drill-down-only screen names: every screen after the first in a
    multi-screen `Points to` cell, across every ## Structure section."""
    lines = path.read_text(encoding="utf-8").splitlines()
    drilldown_only = set()
    in_structure = False
    header_seen = False

    for line in lines:
        if re.match(r"^#{1,3}\s+Structure\b", line):
            in_structure = True
            header_seen = False
            continue
        if line.startswith("#") and in_structure and not TABLE_ROW_RE.match(line):
            in_structure = False
            continue
        if not in_structure:
            continue

        m = TABLE_ROW_RE.match(line)
        if not m:
            continue
        if SEP_ROW_RE.match(line):
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if not header_seen:
            # first table row inside the section is the header
            header_seen = True
            continue
        if len(cells) < 4:
            continue
        points_to = cells[3]
        if points_to in ("", "—", "-"):
            continue
        screens = [s.strip() for s in points_to.split(",") if s.strip()]
        if len(screens) > 1:
            drilldown_only.update(screens[1:])

    return drilldown_only


def collect_files(targets):
    files = []
    for target in targets:
        p = Path(target)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in SCAN_SUFFIXES:
                    files.append(f)
        elif p.is_file():
            files.append(p)
        else:
            print(f"not found: {target}", file=sys.stderr)
    return files


def scan_file(path: Path, screen_names):
    findings = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return findings

    for lineno, line in enumerate(lines, start=1):
        for name in screen_names:
            if name not in line:
                continue
            if HEADING_RE.search(line) and re.search(r">\s*" + re.escape(name) + r"\s*<", line):
                continue  # a page title/heading reusing the name is not a nav link
            is_interactive = bool(INTERACTIVE_RE.search(line))
            is_quoted = f'"{name}"' in line or f"'{name}'" in line
            is_js_literal = bool(JS_LITERAL_RE.search(line)) and is_quoted
            if is_interactive or is_js_literal:
                context = line.strip()[:120]
                findings.append((path, lineno, name, context))
    return findings


def main():
    argv = sys.argv[1:]
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    nav_map_path = Path(argv[0])
    targets = argv[1:]

    if not nav_map_path.is_file():
        print(f"navigation map not found: {nav_map_path}", file=sys.stderr)
        sys.exit(2)

    drilldown_only = parse_nav_map(nav_map_path)
    if not drilldown_only:
        print(f"no multi-screen `Points to` rows in {nav_map_path} — nothing to check")
        sys.exit(0)

    files = collect_files(targets)
    if not files:
        print("nothing to scan", file=sys.stderr)
        sys.exit(2)

    all_findings = []
    for f in files:
        all_findings.extend(scan_file(f, drilldown_only))

    if all_findings:
        for path, lineno, name, context in all_findings:
            print(f"{path}:{lineno} | drill-down-only screen in a nav-shaped element | {name} | {context}")
        print("", file=sys.stderr)
        print(f"{len(all_findings)} finding(s) across {len(files)} file(s).", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  Each name above is the 2nd+ screen in some navigation-map row's `Points to` cell —",
            file=sys.stderr,
        )
        print(
            "  reachable only by clicking into the row's first screen, never its own nav link.",
            file=sys.stderr,
        )
        print(
            "  Review each: a page title or button INSIDE that first screen reusing the words is",
            file=sys.stderr,
        )
        print(
            "  fine; a second, separate entry in the sidebar/menu is the failure to send back.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"clean — no drill-down-only screen found inside a nav-shaped element ({len(files)} file(s) scanned)")
    sys.exit(0)


if __name__ == "__main__":
    main()
