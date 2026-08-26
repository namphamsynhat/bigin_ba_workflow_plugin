#!/usr/bin/env bash
# check-traceability.sh — the traceability contract's deterministic gate, both halves.
#
# NEGATIVE half (always): no requirement id matching /(UC|BR|EN|UX)-\d/ may appear in any VISIBLE
#   position — text nodes, aria-label, title, alt, placeholder, value, <option> bodies, CSS
#   content:. Ids inside data-* attributes are where they belong and are ignored.
#
# POSITIVE half (--require): every screen root must carry data-ux AND data-screen. An artifact with
#   clean visible copy and no provenance at all passes the negative half trivially, which is exactly
#   the failure --require exists to catch.
#
#   usage:  check-traceability.sh <file-or-dir> [<file-or-dir> ...] [--require]
#   exit 0  clean
#   exit 1  findings (each printed as  file:line | kind | position | id | context)
#   exit 2  could not run (no input, nothing to scan)
#
# See references/prompt-contract.md § The one exception for the attribute vocabulary.

set -uo pipefail

ID_RE='(UC|BR|EN|UX)-[0-9]'

require=0
targets=()
for arg in "$@"; do
  case "$arg" in
    --require) require=1 ;;
    *)         targets+=("$arg") ;;
  esac
done

if [ "${#targets[@]}" -eq 0 ]; then
  echo "usage: check-traceability.sh <file-or-dir> [...] [--require]" >&2
  exit 2
fi

files=()
for target in "${targets[@]}"; do
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

findings=0
emit() { printf '%s:%s | %s | %s | %s | %s\n' "$1" "$2" "$3" "$4" "$5" "$6"; findings=$((findings + 1)); }

# ── NEGATIVE half — an id in a position a person can read ────────────────────────────────────────
for f in "${files[@]}"; do
  while IFS= read -r hit; do
    lineno=${hit%%:*}
    line=${hit#*:}

    # Strip data-* attribute VALUES only (the legal home for an id), keeping everything else intact
    # and keeping line numbers stable, then look at what is left.
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

    emit "$f" "$lineno" "leak" "$position" "$matched" "$context"
  done < <(grep -nE "$ID_RE" "$f" 2>/dev/null)
done

# ── POSITIVE half — provenance actually present ──────────────────────────────────────────────────
if [ "$require" -eq 1 ]; then
  for f in "${files[@]}"; do
    case "$f" in
      *.html|*.htm|*.jsx|*.tsx|*.vue|*.svelte) ;;
      *) continue ;;
    esac

    has_ux=$(grep -cE 'data-ux=' "$f" 2>/dev/null || true)
    has_screen=$(grep -cE 'data-screen=' "$f" 2>/dev/null || true)

    if [ "${has_ux:-0}" -eq 0 ]; then
      emit "$f" "0" "missing" "screen root" "data-ux" "no data-ux anywhere in this artifact"
    fi
    if [ "${has_screen:-0}" -eq 0 ]; then
      emit "$f" "0" "missing" "screen root" "data-screen" "no data-screen anywhere in this artifact"
    fi

    # A screen carrying named states must say which node is in which state.
    if grep -Eqi 'data-state=|class="[^"]*\b(empty|loading|error)\b' "$f" 2>/dev/null; then
      if [ "$(grep -cE 'data-state=' "$f" 2>/dev/null || true)" -eq 0 ]; then
        emit "$f" "0" "missing" "state container" "data-state" \
          "state-like markup present but no data-state attribute"
      fi
    fi
  done
fi

if [ "$findings" -gt 0 ]; then
  echo "" >&2
  echo "$findings traceability finding(s) across ${#files[@]} file(s)." >&2
  echo "" >&2
  echo "  leak     move the id into the correct data-* attribute and leave the human-readable" >&2
  echo "           words unchanged. If removing the id empties the copy, that is a MISSING-COPY" >&2
  echo "           finding for the render, not a sanitize — send the screen back." >&2
  echo "  missing  NEVER add the attribute by hand. An id you invent is an id nobody grounded." >&2
  echo "           This is a re-run finding: state it as a correction and start a new run." >&2
  echo "" >&2
  echo "See references/prompt-contract.md § The one exception." >&2
  exit 1
fi

if [ "$require" -eq 1 ]; then
  echo "clean — no id in any visible position, provenance present (${#files[@]} file(s) scanned)"
else
  echo "clean — no id in any visible position (${#files[@]} file(s) scanned)"
fi
exit 0
