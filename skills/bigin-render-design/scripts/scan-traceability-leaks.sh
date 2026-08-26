#!/usr/bin/env bash
# scan-traceability-leaks.sh — Rule A enforcement for /bigin-render-design.
#
# Scans rendered prototype artifacts for requirement ids matching /(UC|BR|EN|UX)-\d/ appearing in
# any VISIBLE position. Ids in data-* attributes are where they belong and are ignored.
#
#   usage:  scan-traceability-leaks.sh <file-or-dir> [<file-or-dir> ...]
#   exit 0  clean
#   exit 1  leaks found (each printed as  file:line | position | matched-id | context)
#   exit 2  could not run (no input, nothing to scan)
#
# A clean exit does NOT prove the positive half of the contract — that every screen root carries
# data-ux/data-screen, etc. The linter verifies that by hand. See references/render-pipeline.md
# § The traceability contract.

set -uo pipefail

ID_RE='(UC|BR|EN|UX)-[0-9]'

if [ "$#" -eq 0 ]; then
  echo "usage: scan-traceability-leaks.sh <file-or-dir> [...]" >&2
  exit 2
fi

files=()
for target in "$@"; do
  if [ -d "$target" ]; then
    while IFS= read -r f; do files+=("$f"); done < <(
      find "$target" -type f \( -name '*.html' -o -name '*.htm' -o -name '*.jsx' -o -name '*.tsx' \
        -o -name '*.vue' -o -name '*.svelte' -o -name '*.css' -o -name '*.js' \) 2>/dev/null
    )
  elif [ -f "$target" ]; then
    files+=("$target")
  else
    echo "not found: $target" >&2
  fi
done

if [ "${#files[@]}" -eq 0 ]; then
  echo "nothing to scan" >&2
  exit 2
fi

leaks=0

emit() { printf '%s:%s | %s | %s | %s\n' "$1" "$2" "$3" "$4" "$5"; leaks=$((leaks + 1)); }

for f in "${files[@]}"; do
  # Strip data-* attribute VALUES only (the legal home for an id), keeping everything else intact
  # and keeping line numbers stable, then look for what is left.
  while IFS= read -r hit; do
    lineno=${hit%%:*}
    line=${hit#*:}

    stripped=$(printf '%s' "$line" | sed -E 's/data-[a-zA-Z0-9-]+=("[^"]*"|'"'"'[^'"'"']*'"'"')//g')

    printf '%s' "$stripped" | grep -Eq "$ID_RE" || continue

    matched=$(printf '%s' "$stripped" | grep -Eo "$ID_RE[0-9]*" | head -1)
    context=$(printf '%s' "$line" | sed -E 's/^[[:space:]]+//' | cut -c1-100)

    position="text node"
    case "$stripped" in
      *aria-label=*)  position="aria-label"  ;;
      *placeholder=*) position="placeholder" ;;
      *title=*)       position="title"       ;;
      *alt=*)         position="alt"         ;;
      *value=*)       position="value"       ;;
      *content:*)     position="css content" ;;
      *"<option"*)    position="option label";;
      *label=*)       position="label"       ;;
    esac

    emit "$f" "$lineno" "$position" "$matched" "$context"
  done < <(grep -nE "$ID_RE" "$f" 2>/dev/null)
done

if [ "$leaks" -gt 0 ]; then
  echo "" >&2
  echo "$leaks traceability leak(s). Move each id into the correct data-* attribute and leave the" >&2
  echo "human-readable words unchanged. If removing the id empties the copy, that is a missing-copy" >&2
  echo "finding for the designer, not a sanitize. See references/render-pipeline.md." >&2
  exit 1
fi

echo "clean — no requirement id in any visible position (${#files[@]} file(s) scanned)"
exit 0
