#!/usr/bin/env bash
# Type-checks then runs unit tests. Fails fast on type errors so they
# don't hide behind a green pytest run.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Running mypy..."
uv run mypy src tests

echo "Running pytest..."
uv run pytest "$@"
