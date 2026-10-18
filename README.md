# Agentic harness

This repo is a portable Claude Code / OpenCode setup. Copy this directory into
any project to get the same agents, skills, and model defaults automatically —
they are project-local, not system-wide.

- `agents/` — subagent definitions (`oracle`, `librarian`), top-level and
  owned by neither tool.
- `skills/` — skills, one directory per skill, also top-level.
- `.claude/` — Claude Code's view: `agents` and `skills` are symlinks into
  the top-level dirs above, plus `settings.json` for model defaults,
  permissions, and denied built-in skills/agents.
- `.opencode/` — OpenCode's view of the same `agents`/`skills` directories,
  via the same kind of symlink.
- `bin/opencode.sh` — wrapper that pins the OpenCode binary version and its
  data/DB location.
- `scripts/install-opencode.sh` — idempotent OpenCode installer.
- `scripts/new-project.sh` — scaffolds a new project directory that symlinks
  back to this repo's `agents`/`skills`/settings.
- `smoke-test/` — scripts that use `new-project.sh` to spin up a project in a
  temp directory and verify the expected agents/skills actually load there.

Editing an agent or skill: edit the file once under `agents/` or `skills/`;
both Claude Code and OpenCode pick it up automatically via symlink.
