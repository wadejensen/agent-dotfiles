#!/usr/bin/env bash
# Runs PROJECT_NAME's CLI with sensible defaults for local use.
# Extra args are forwarded, so `./run.sh --quiet` overrides the default.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

exec uv run PACKAGE_NAME --verbose "$@"
