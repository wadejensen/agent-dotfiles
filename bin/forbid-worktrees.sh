#!/usr/bin/env bash
# PreToolUse hook: forbid worktrees. Blocks Bash git-worktree commands, the
# EnterWorktree / ExitWorktree tools, and Agent calls with isolation=worktree.
# Exit 2 sends stderr back to the agent as the error.
set -euo pipefail

main() {
  python3 -c '
import json, re, sys

event = json.load(sys.stdin)
tool = event.get("tool_name", "")
tool_input = event.get("tool_input") or {}
command = tool_input.get("command", "")

# git, any global options (-C <dir>, -c k=v, --flag), then worktree.
git_worktree = re.compile(
    r"(^|[;&|(`]|\$\()\s*git(\s+(-[Cc]|--git-dir|--work-tree)\s+\S+|\s+-\S+)*\s+worktree(\s|$)"
)

forbidden = (
    tool in ("EnterWorktree", "ExitWorktree")
    or (tool == "Bash" and git_worktree.search(command))
    or (tool == "Agent" and tool_input.get("isolation") == "worktree")
)
if forbidden:
    sys.stderr.write(
        "Blocked: worktree usage is forbidden in this project. "
        "Do not create, enter, or manage worktrees: no git worktree commands, "
        "no EnterWorktree / ExitWorktree, no Agent isolation=worktree. "
        "Work in the current checkout; if you think a worktree is needed, "
        "stop and ask the user.\n"
    )
    sys.exit(2)
'
}

main
