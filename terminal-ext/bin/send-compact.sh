#!/usr/bin/env bash
# Send /compact to a named terminal in a window via terminal-ext's per-window
# Unix domain socket, without needing OS focus on that window.
#
# Usage:
#   send-compact.sh <terminal_name> [repo_path]
#
# repo_path defaults to the git root of the current directory (same
# resolution as find-window.sh), and is used to look up the socket path
# for the matching window in the registry.

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: send-compact.sh <terminal_name> [repo_path]" >&2
  exit 1
fi

terminal_name="$1"
repo_path="${2:-}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

registry_json="$("$script_dir/find-window.sh" "$repo_path" 2>&1)" || {
  echo "$registry_json" >&2
  exit 1
}

sock_path="$(echo "$registry_json" | jq -r '.socketPath' | head -n1)"

if [ -z "$sock_path" ] || [ "$sock_path" = "null" ]; then
  echo "No socketPath found in registry entry for this window" >&2
  exit 1
fi

message="$(jq -nc --arg target "$terminal_name" '{command: "sendText", target: $target, payload: "/compact"}')"

response="$(echo "$message" | nc -U "$sock_path")"
echo "$response"

if ! echo "$response" | jq -e '.ok == true' >/dev/null 2>&1; then
  exit 1
fi
