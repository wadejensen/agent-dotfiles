#!/usr/bin/env bash
# Claude Code statusline: reads the per-turn JSON payload on stdin and prints
# a single display line (model, cwd, context window usage, cost).
set -euo pipefail

main() {
  local payload
  payload="$(cat)"

  local model dir used_pct cost_usd cost
  model="$(jq -r '.model.display_name // "unknown"' <<<"$payload")"
  dir="$(jq -r '.workspace.current_dir // "."' <<<"$payload")"
  used_pct="$(jq -r 'if .context_window.used_percentage then (.context_window.used_percentage | tostring) + "%" else "?" end' <<<"$payload")"
  cost_usd="$(jq -r '.cost.total_cost_usd // ""' <<<"$payload")"
  cost=""
  [[ -n "$cost_usd" ]] && cost="$(printf '$%.2f' "$cost_usd")"

  printf '%s | %s | ctx %s%s\n' "$model" "${dir##*/}" "$used_pct" "${cost:+ | $cost}"
}

main
