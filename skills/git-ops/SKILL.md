---
name: git-ops
description: Git conventions how to commit, branch, update PRs, and get a PR ready to merge. Use when committing, pushing, branching, updating a PR against master, running searches in the repo.
---

# Git Operations

The repo has hundreds of thousands of files, so `grep`, `find`, and
`git log`-style history commands can be far slower than normal. Scout the specific
directories of interest first.
Do not blindly perform global searches over the entire repo.

## Commits and branches

- **Name branches `$author-$component-$feature-description`** — e.g.
  `wade-webserver-connection-pool-increase`.
- **Prefer small atomic commits** - they make human step-by-step review easier.
- **Commit discipline (what goes in a code PR).** Stage only the work-item source
  files plus `memory/DECISIONS.md` and `memory/learnings.md`. Do **not** commit
  sessions, compactions, memory files.
- **Always `git add` explicit paths.** Name the specific files or directories you intend to stage (e.g. `git add path/to/file.sh path/to/dir/`). **Never** use `git add -A`, `git add .`, or `git add -u`. The working tree routinely carries unrelated dirty and untracked state which should not be committed. After staging, run `git diff --cached --name-only` and confirm the list is exactly what you meant.
- **Never** force-push, amend commits, or run `git clean -fd` (it destroys untracked
  state from other work). None of this is needed: PRs squash-merge into master and
  GitHub retains the branch history if it's ever wanted.
- Don't clean up local branches — maintenance is automated.

## Pushing

- Push with `bin/git-push` (same arguments as `git push`), not bare `git push`.
- Never use `--no-verify`.
- Commit or stash tracked changes first.

## Merging

- PRs are **squash-merged**, always a manual step requiring operator and colleague
  review. **Agents never merge PRs directly.**
- Update a PR against latest master with a **merge commit, never a rebase.**
- Master is busy — assume new commits have landed since you last checked.

## Common requests

- **"Checkout latest master" / "start a new task"** → first check whether the PR
  you were working on has merged (`gh pr view <branch> --json state`), then checkout
  master and pull latest, it may have progressed.
- **"Get this PR ready for merge"** → run these skills in order:
  1. `resolving-merge-conflicts` — ensure the branch is mergeable.
  2. `method-docstrings` — improve the code comments.
  3. `pr-description` — improve the PR description.
  4. Check for review-bot comments (`gh pr view <n> --json comments`; also
     `gh api repos/{owner}/{repo}/pulls/<n>/comments` for inline threads). Evaluate
     each on its merits. Automated review bots catche real issues, but are infamous for raising false positives, so neither dismiss nor blindly apply. If one looks worth acting on, do **not** autofix: explain the gap and why you'd fix it to the operator first, and let them decide. Human judgement is the gate.

## Surfacing the PR

When a PR is close to merge-ready or the operator may want to inspect it, end each
reply with a line of the form `PR: <url>` — the full URL as plain text, which the
TUI auto-detects and makes cmd+click-able.

Don't seek the user's opinion on how to sequence changes in separate commits.
Follow instructions if given, otherwise make best practice commits that are pragmatic and understandable, atomic commits are only a nice to have.
