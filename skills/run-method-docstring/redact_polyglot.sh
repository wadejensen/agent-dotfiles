#!/usr/bin/env bash
# Wrapper for redact_polyglot.py: idempotently ensures this skill's venv is
# set up (via uv), then runs the tool. Safe to invoke from any project that
# symlinks this skill in — the venv lives once, alongside this script's real
# (symlink-resolved) location, not per-project.
#
# Usage: git diff <base> | redact_polyglot.sh --output-file <report> [file ...]
set -euo pipefail

main() {
  local skill_dir
  skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

  if [[ ! -d "$skill_dir/.venv" ]]; then
    uv sync --project "$skill_dir" >&2
  fi

  uv run --project "$skill_dir" python "$skill_dir/redact_polyglot.py" "$@"
}

main "$@"
