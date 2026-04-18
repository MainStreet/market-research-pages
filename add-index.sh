#!/usr/bin/env bash
# add-index.sh — Drop the universal index.html landing page into folder(s).
#
# The root index.html is the canonical template; this script copies it
# into any folder that needs one. Since the template is self-aware
# (derives its folder path from window.location), no editing is needed.
#
# Usage:
#   ./add-index.sh <folder> [<folder> ...]     Add to specific folders
#   ./add-index.sh --all                       Add to every folder missing one
#   ./add-index.sh --all --force               Overwrite existing index.html too
#                                              (useful after template updates)
#   ./add-index.sh -h | --help

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TEMPLATE="$REPO_ROOT/index.html"
FORCE=0

usage() {
  sed -n '2,13p' "$0" | sed 's/^# //; s/^#//'
  exit "${1:-0}"
}

if [ $# -eq 0 ]; then usage 1; fi

args=()
for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=1 ;;
    -h|--help)  usage 0 ;;
    *)          args+=("$arg") ;;
  esac
done

if [ ! -f "$TEMPLATE" ]; then
  echo "Error: template not found at $TEMPLATE" >&2
  exit 1
fi

add_one() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    echo "Skip (not a dir): $dir" >&2
    return
  fi
  local abs
  abs="$(cd "$dir" 2>/dev/null && pwd)" || { echo "Skip (bad dir): $dir" >&2; return; }
  if [ "$abs" = "$REPO_ROOT" ]; then
    echo "Skip (repo root — that IS the template): $dir/index.html"
    return
  fi
  if [ -f "$dir/index.html" ] && [ "$FORCE" -eq 0 ]; then
    echo "Skip (exists): $dir/index.html"
    return
  fi
  cp "$TEMPLATE" "$dir/index.html"
  echo "Wrote: $dir/index.html"
}

if [ "${args[0]:-}" = "--all" ]; then
  while IFS= read -r dir; do
    add_one "$dir"
  done < <(find "$REPO_ROOT" -type d \
           -not -path '*/.git*' \
           -not -path '*/.claude*' \
           -not -path '*/node_modules*')
else
  for folder in "${args[@]}"; do
    add_one "$folder"
  done
fi
