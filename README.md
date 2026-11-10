# Agentic harness

This repo is a portable Claude Code / OpenCode setup. Copy this directory into
any project to get the same agents, skills, and model defaults automatically —
they are project-local, not system-wide.

- `agents/` — subagent definitions (`oracle`, `librarian`), top-level and
  owned by neither tool.
- `skills/` — skills, one directory per skill, also top-level.
- `.claude-plugin/` — makes this repo a Claude Code plugin (and a one-plugin
  marketplace `agent-dotfiles`) named `wj`. Claude Code loads `agents/`,
  `skills/`, and `hooks/hooks.json` from it; skills appear as
  `wj:<name>`.
- `hooks/hooks.json` — plugin hooks (the forbid-worktrees PreToolUse guard).
- `.claude/settings.json` — the one settings file for every project: model,
  env, permissions, denied built-in skills/agents, the statusline, and
  enabling the plugin. It assumes this repo lives at `~/code/agent-dotfiles`.
  A plugin cannot set the main statusline, model, or env, so these live here.
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
Claude Code reads it through the plugin (a directory marketplace, read in
place) and OpenCode through its symlinks.

One-time setup per machine: register the marketplace. The path in
`settings.json` does not register it by itself.

```sh
claude plugin marketplace add ~/code/agent-dotfiles
```

Using this setup in an existing repo without committing anything: symlink
that repo's gitignored `.claude/settings.local.json` to this repo's
settings. Check the repo's `.gitignore` covers it first.

```sh
ln -s ~/code/agent-dotfiles/.claude/settings.json <repo>/.claude/settings.local.json
```

Claude Code refuses to write through a symlinked settings file, so
local-scope writes (`/plugin` with `--scope local`, and possibly "always
allow" permission prompts) fail in that repo. Add those to this repo's
`settings.json` or to `~/.claude/settings.json` instead.
