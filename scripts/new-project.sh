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

Every file in this repo's bin/ is symlinked into the project's bin/
(existing names are left alone, linked files are gitignored), and
.envrc gets "PATH_add bin" for direnv.

The pre-push hook (blocks pushes of commits carrying agent attribution;
use bin/git-push to scrub them) is symlinked into this repo and into
the new project, if each is a git repo.

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

# Symlink the pre-push attribution check into a repo's hooks dir. Skips
# non-repos and never replaces an existing, different pre-push hook.
install_pre_push_hook() {
  local repo="$1" hooks
  hooks="$(git -C "$repo" rev-parse --path-format=absolute --git-path hooks 2>/dev/null)" || {
    echo "Note: $repo is not a git repo; skipped pre-push hook (rerun after git init)" >&2
    return 0
  }
  mkdir -p "$hooks"
  if [[ -e "$hooks/pre-push" && "$(realpath "$hooks/pre-push" 2>/dev/null)" != "$(realpath "$REPO_ROOT/bin/pre-push-check")" ]]; then
    echo "Note: $hooks/pre-push already exists; left unchanged" >&2
    return 0
  fi
  ln -sfn "$REPO_ROOT/bin/pre-push-check" "$hooks/pre-push"
}

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
ln -s "$REPO_ROOT/bin/forbid-worktrees.sh" "$PROJECT_PATH/.claude/forbid-worktrees.sh"

ln -s "$REPO_ROOT/agents" "$PROJECT_PATH/.opencode/agent"
ln -s "$REPO_ROOT/skills" "$PROJECT_PATH/.opencode/skills"

cp "$REPO_ROOT/AGENTS.md" "$PROJECT_PATH/AGENTS.md"
ln -s AGENTS.md "$PROJECT_PATH/CLAUDE.md"

cp -R "$REPO_ROOT/memory" "$PROJECT_PATH/memory"
cp -R "$REPO_ROOT/docs" "$PROJECT_PATH/docs"

# Symlink each of this repo's bin/ files into the project's bin/. An existing
# bin/ dir is fine; an existing name is never replaced.
mkdir -p "$PROJECT_PATH/bin"
LINKED_BIN=()
for src in "$REPO_ROOT"/bin/*; do
  name="$(basename "$src")"
  if [[ -e "$PROJECT_PATH/bin/$name" || -L "$PROJECT_PATH/bin/$name" ]]; then
    echo "Note: bin/$name already exists in the project; left unchanged" >&2
    continue
  fi
  ln -s "$src" "$PROJECT_PATH/bin/$name"
  LINKED_BIN+=("bin/$name")
done

# Put bin/ on PATH via direnv, without clobbering an existing .envrc.
grep -qxF "PATH_add bin" "$PROJECT_PATH/.envrc" 2>/dev/null || echo "PATH_add bin" >> "$PROJECT_PATH/.envrc"

touch "$PROJECT_PATH/.gitignore"
for entry in ".claude/" ".opencode/" "${LINKED_BIN[@]+"${LINKED_BIN[@]}"}"; do
  grep -qxF "$entry" "$PROJECT_PATH/.gitignore" || echo "$entry" >> "$PROJECT_PATH/.gitignore"
done

install_pre_push_hook "$REPO_ROOT"
install_pre_push_hook "$PROJECT_PATH"

echo "Project ready at $PROJECT_PATH"
