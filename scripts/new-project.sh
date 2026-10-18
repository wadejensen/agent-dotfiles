#!/usr/bin/env bash
# Scaffold a new project wired up with this repo's shared Claude Code /
# OpenCode agents, skills, and settings via symlinks — edits to this repo
# are picked up by every project created with this script.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: new-project.sh --path <directory>

Creates (or wires up) a project directory with this harness's agents,
skills, and settings, shared via symlinks back into this repo. Both
Claude Code (.claude/) and OpenCode (.opencode/) are configured, and
both are added to the project's .gitignore since they're symlinks
into this shared repo, not project-owned files.

AGENTS.md is copied (not symlinked) into the project so it can be
edited per-project, and CLAUDE.md is symlinked to it locally. A
memory/ scaffold (sessions/, specs/, gitignored) is copied in too.

A docs/ scaffold (empty adr.md, functional-requirements.md, and
principles.md, plus an AGENTS.md pointing at the eng-guardrails
skill) is copied in so the project can record its guardrails.

Required:
  --path <dir>   Directory for the new project. Created if it doesn't
                 exist. Refuses to run if it already has a .claude,
                 .opencode, AGENTS.md, CLAUDE.md, memory, or docs
                 directory.

Options:
  -h, --help     Show this help text.

Example:
  scripts/new-project.sh --path ~/code/my-new-app
EOF
}

PROJECT_PATH=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      [[ $# -ge 2 ]] || { echo "Error: --path requires a value" >&2; usage; exit 1; }
      PROJECT_PATH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument '$1'" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$PROJECT_PATH" ]]; then
  echo "Error: --path is required" >&2
  usage
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$PROJECT_PATH"
PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"

if [[ -e "$PROJECT_PATH/.claude" || -e "$PROJECT_PATH/.opencode" || -e "$PROJECT_PATH/AGENTS.md" || -e "$PROJECT_PATH/CLAUDE.md" || -e "$PROJECT_PATH/memory" || -e "$PROJECT_PATH/docs" ]]; then
  echo "Error: $PROJECT_PATH already contains a .claude, .opencode, AGENTS.md, CLAUDE.md, memory, or docs directory" >&2
  exit 1
fi

mkdir -p "$PROJECT_PATH/.claude" "$PROJECT_PATH/.opencode"

ln -s "$REPO_ROOT/agents" "$PROJECT_PATH/.claude/agents"
ln -s "$REPO_ROOT/skills" "$PROJECT_PATH/.claude/skills"
ln -s "$REPO_ROOT/.claude/settings.json" "$PROJECT_PATH/.claude/settings.json"
ln -s "$REPO_ROOT/bin/statusline.sh" "$PROJECT_PATH/.claude/statusline.sh"

ln -s "$REPO_ROOT/agents" "$PROJECT_PATH/.opencode/agent"
ln -s "$REPO_ROOT/skills" "$PROJECT_PATH/.opencode/skills"

cp "$REPO_ROOT/AGENTS.md" "$PROJECT_PATH/AGENTS.md"
ln -s AGENTS.md "$PROJECT_PATH/CLAUDE.md"

cp -R "$REPO_ROOT/memory" "$PROJECT_PATH/memory"
cp -R "$REPO_ROOT/docs" "$PROJECT_PATH/docs"

touch "$PROJECT_PATH/.gitignore"
for entry in ".claude/" ".opencode/"; do
  grep -qxF "$entry" "$PROJECT_PATH/.gitignore" || echo "$entry" >> "$PROJECT_PATH/.gitignore"
done

echo "Project ready at $PROJECT_PATH"
