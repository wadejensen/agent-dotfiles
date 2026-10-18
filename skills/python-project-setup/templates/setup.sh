#!/usr/bin/env bash
# Bootstraps PROJECT_NAME from a bare git clone: installs uv if needed,
# pins the Python version, and syncs the venv + lockfile.
# Safe to re-run any time (e.g. after pulling new dependencies) — it just
# brings .venv/uv.lock back in sync with pyproject.toml.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found, installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv installed but not on PATH. Add \$HOME/.local/bin to PATH and re-run this script." >&2
  exit 1
fi

echo "uv version: $(uv --version)"

# Installs the Python version pinned in pyproject.toml's requires-python /
# .python-version if it isn't already available. No-op if it is.
uv python install

# Creates .venv, generates uv.lock if missing, installs runtime + dev deps.
uv sync

echo "Setup complete. Try: ./run.sh --help  or  ./test.sh"
