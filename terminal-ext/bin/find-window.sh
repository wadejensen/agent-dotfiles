#!/usr/bin/env bash
# Find which open Cursor/VS Code window (registered by terminal-ext) has a
# workspace folder matching the given repo path, and list its terminals.
#
# Usage:
#   find-window.sh [repo_path]
#
# Defaults repo_path to the git root of the current directory, or the
# current directory if not in a git repo. Prints one JSON object per
# matching window to stdout.

set -euo pipefail

REGISTRY_DIR="$HOME/.terminal-ext/windows"

repo_path="${1:-}"
if [ -z "$repo_path" ]; then
  repo_path="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
repo_path="$(cd "$repo_path" && pwd)"

if [ ! -d "$REGISTRY_DIR" ]; then
  echo "No registry directory found at $REGISTRY_DIR (is terminal-ext installed and active in any window?)" >&2
  exit 1
fi

found=0
for f in "$REGISTRY_DIR"/*.json; do
  [ -e "$f" ] || continue
  if jq -e --arg repo "$repo_path" \
    '.workspaceFolders | any(. == $repo)' \
    "$f" >/dev/null 2>&1; then
    jq . "$f"
    found=1
  fi
done

if [ "$found" -eq 0 ]; then
  echo "No window found with workspace folder: $repo_path" >&2
  exit 1
fi
