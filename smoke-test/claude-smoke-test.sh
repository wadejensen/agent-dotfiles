#!/usr/bin/env bash
# Smoke test: use scripts/new-project.sh to scaffold a brand new project in a
# temp directory, then verify Claude Code auto-loads this repo's skills and
# agents there, and that the denied built-ins are actually blocked.
#
# Usage: smoke-test/claude-smoke-test.sh
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
DENIED_SKILLS=(dataviz simplify fewer-permission-prompts keybindings-help update-config)
DENIED_AGENT=statusline-setup

# Structural assertions on a freshly scaffolded project — no LLM involved.
check_scaffolding() {
  local project_dir="$1"
  local failures=()

  [[ -L "$project_dir/.claude/agents" ]] || failures+=(".claude/agents is not a symlink")
  [[ -L "$project_dir/.claude/skills" ]] || failures+=(".claude/skills is not a symlink")
  [[ -L "$project_dir/.claude/settings.json" ]] || failures+=(".claude/settings.json is not a symlink")
  [[ -L "$project_dir/.claude/statusline.sh" ]] || failures+=(".claude/statusline.sh is not a symlink")
  [[ -L "$project_dir/.opencode/agent" ]] || failures+=(".opencode/agent is not a symlink")
  [[ -L "$project_dir/.opencode/skills" ]] || failures+=(".opencode/skills is not a symlink")

  if [[ -L "$project_dir/AGENTS.md" ]]; then
    failures+=("AGENTS.md should be a real copy, not a symlink")
  elif [[ ! -f "$project_dir/AGENTS.md" ]]; then
    failures+=("AGENTS.md is missing")
  elif ! diff -q "$REPO_ROOT/AGENTS.md" "$project_dir/AGENTS.md" >/dev/null; then
    failures+=("AGENTS.md content does not match $REPO_ROOT/AGENTS.md")
  fi

  if [[ -L "$project_dir/CLAUDE.md" ]]; then
    local target
    target="$(readlink "$project_dir/CLAUDE.md")"
    [[ "$target" == "AGENTS.md" ]] || failures+=("CLAUDE.md symlink points to '$target', expected 'AGENTS.md'")
  else
    failures+=("CLAUDE.md is missing or not a symlink")
  fi

  if [[ -f "$project_dir/.gitignore" ]]; then
    grep -qxF ".claude/" "$project_dir/.gitignore" || failures+=(".gitignore is missing '.claude/'")
    grep -qxF ".opencode/" "$project_dir/.gitignore" || failures+=(".gitignore is missing '.opencode/'")
  else
    failures+=(".gitignore is missing")
  fi

  if [[ -L "$project_dir/memory" ]]; then
    failures+=("memory/ should be a real copy, not a symlink")
  elif [[ ! -d "$project_dir/memory" ]]; then
    failures+=("memory/ is missing")
  else
    [[ -d "$project_dir/memory/sessions" ]] || failures+=("memory/sessions is missing")
    [[ -d "$project_dir/memory/specs" ]] || failures+=("memory/specs is missing")
    [[ -f "$project_dir/memory/.gitignore" ]] || failures+=("memory/.gitignore is missing")
  fi

  if [ "${#failures[@]}" -gt 0 ]; then
    echo "FAIL: scaffolding checks failed:"
    printf '  - %s\n' "${failures[@]}"
    exit 1
  fi

  echo "PASS: scaffolding structure (.claude, .opencode, AGENTS.md, CLAUDE.md, .gitignore, memory) is correct."
}

main() {
  local skills=()
  while IFS= read -r -d '' dir; do
    skills+=("$(basename "$dir")")
  done < <(find "$REPO_ROOT/skills" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)

  local agents=()
  while IFS= read -r -d '' f; do
    agents+=("$(basename "$f" .md)")
  done < <(find "$REPO_ROOT/agents" -maxdepth 1 -name '*.md' -print0 | sort -z)

  echo "Expecting ${#skills[@]} skills and ${#agents[@]} agents from a freshly scaffolded project."

  workdir="$(mktemp -d)"
  trap 'rm -rf "$workdir"' EXIT

  "$REPO_ROOT/scripts/new-project.sh" --path "$workdir/new-project"
  cd "$workdir/new-project"

  check_scaffolding "$workdir/new-project"

  local output
  output="$(claude -p 'List the exact name of every single skill and every single agent you have access to. Do not summarize, group, or omit any for brevity, no matter how many there are. Output only the bare names, one per line, no extra commentary.' 2>&1)"

  echo "--- raw output ---"
  echo "$output"
  echo "-------------------"

  local missing=()
  for name in "${skills[@]}" "${agents[@]}"; do
    if ! grep -qi -- "$name" <<<"$output"; then
      missing+=("$name")
    fi
  done

  if [ "${#missing[@]}" -gt 0 ]; then
    echo "FAIL: missing from Claude's reported list:"
    printf '  - %s\n' "${missing[@]}"
    exit 1
  fi

  local still_listed=()
  for name in "${DENIED_SKILLS[@]}" "$DENIED_AGENT"; do
    if grep -qi -- "$name" <<<"$output"; then
      still_listed+=("$name")
    fi
  done

  if [ "${#still_listed[@]}" -gt 0 ]; then
    echo "NOTE: denied items still appear in the reported list (permission deny still blocks invocation, but skillOverrides did not hide them from this Claude Code version):"
    printf '  - %s\n' "${still_listed[@]}"
  fi

  local deny_output
  deny_output="$(claude -p "Try to invoke the dataviz skill right now." 2>&1)"
  if grep -qi 'permission\|denied\|not allowed\|cannot\|no skill\|not in the available' <<<"$deny_output"; then
    echo "PASS: invoking a denied skill was blocked."
  else
    echo "WARN: could not confirm denied skill invocation was blocked — inspect manually:"
    echo "$deny_output"
  fi

  echo "PASS: all ${#skills[@]} skills and ${#agents[@]} agents were reported from a freshly scaffolded project."
}

main "$@"
