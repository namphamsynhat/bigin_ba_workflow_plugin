#!/usr/bin/env python3
"""check-contrast.py — WCAG 2.1 contrast ratios for /bigin-render-design's fidelity gate.

Contrast is a formula, and a model asked to judge it by eye is wrong on exactly the pairings a
dense enterprise screen is full of: muted text on a subtle surface. Compute it.

usage:
    check-contrast.py <fg> <bg> [<fg> <bg> ...]        # colour pairs
    check-contrast.py --tokens <file.md>               # every colour token, pairwise vs surfaces
                                                      # (the BOUND design system's DESIGN.md, or a
                                                      #  token file the design team supplied — the
                                                      #  vault itself holds no design system)
    check-contrast.py --pairs <file>                   # one "name fg bg [large|ui]" per line

Colours: #rgb, #rrggbb, #rrggbbaa (alpha ignored — composite it yourself first), or "r,g,b".

Thresholds (references/enterprise-fidelity.md § The bar, item 2):
    body text                        >= 4.5:1
    large text (>=18pt / 14pt bold)  >= 3.0:1
    UI boundaries / focus rings      >= 3.0:1

exit 0  every pair passes      exit 1  a pair fails      exit 2  bad input
"""
import re
import sys


def parse(c):
    c = c.strip()
    if "," in c:
        parts = [int(p) for p in c.split(",")]
        if len(parts) != 3:
            raise ValueError(c)
        return tuple(parts)
    h = c.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) == 8:
        h = h[:6]
    if len(h) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(c)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def chan(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = luminance(parse(fg)), luminance(parse(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def report(label, fg, bg, kind="body"):
    need = 3.0 if kind in ("large", "ui") else 4.5
    r = ratio(fg, bg)
    ok = r >= need
    print("%-7s %-34s %s on %s = %5.2f:1  (needs %.1f:1, %s)"
          % ("PASS" if ok else "FAIL", label, fg, bg, r, need, kind))
    return ok


def read_tokens(path):
    """Pull `--token-name: #value` or a markdown table's `| name | #value |` out of a token file."""
    found = {}
    with open(path) as fh:
        for line in fh:
            for name, val in re.findall(r"(--[a-zA-Z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", line):
                found[name] = val
            m = re.match(r"\s*\|\s*`?([a-zA-Z0-9._-]+)`?\s*\|.*?(#[0-9a-fA-F]{3,8})", line)
            if m:
                found[m.group(1)] = m.group(2)
    return found


def main(argv):
    if not argv:
        print(__doc__)
        return 2

    if argv[0] == "--tokens":
        if len(argv) < 2:
            print("--tokens needs a file (the bound design system's DESIGN.md, or the design "
                  "team's token file — the vault holds no design system)", file=sys.stderr)
            return 2
        tokens = read_tokens(argv[1])
        if not tokens:
            print("no colour tokens found in %s" % argv[1], file=sys.stderr)
            return 2
        surfaces = {n: v for n, v in tokens.items()
                    if re.search(r"bg|background|surface|canvas|paper", n, re.I)}
        texts = {n: v for n, v in tokens.items()
                 if re.search(r"text|fg|foreground|ink|label|muted|secondary", n, re.I)}
        if not surfaces or not texts:
            print("could not tell surfaces from text colours by name — pass pairs explicitly",
                  file=sys.stderr)
            return 2
        ok = True
        for tn, tv in sorted(texts.items()):
            for sn, sv in sorted(surfaces.items()):
                ok &= report("%s / %s" % (tn, sn), tv, sv)
        return 0 if ok else 1

    if argv[0] == "--pairs":
        if len(argv) < 2:
            print("--pairs needs a file", file=sys.stderr)
            return 2
        ok = True
        with open(argv[1]) as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw or raw.startswith("#") and " " not in raw:
                    continue
                parts = raw.split()
                if len(parts) < 3:
                    continue
                name, fg, bg = parts[0], parts[1], parts[2]
                kind = parts[3] if len(parts) > 3 else "body"
                ok &= report(name, fg, bg, kind)
        return 0 if ok else 1

    if len(argv) % 2:
        print("colour pairs come two at a time: <fg> <bg>", file=sys.stderr)
        return 2

    ok = True
    for i in range(0, len(argv), 2):
        ok &= report("pair %d" % (i // 2 + 1), argv[i], argv[i + 1])
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ValueError as e:
        print("not a colour: %s" % e, file=sys.stderr)
        sys.exit(2)
