---
name: resolving-merge-conflicts
description: Plan and execute merge conflict resolution by producing a structured merge plan before touching code. Use when asked to merge a branch, resolve conflicts, rebase onto master, or check for merge compatibility.
---

# Skill: Resolving Merge Conflicts

## The workflow

```
1. DETECT    determine whether conflicts exist (stop early if none)
2. PLAN      produce a structured merge plan (merge.md)
3. EXECUTE   resolve conflicts following the plan
4. VERIFY    no conflict markers remain + tests pass
```

**Guiding principle:** Plan before touching code. The merge plan forces you to understand _why_ each side diverged before choosing a resolution.

## Phase 1 — DETECT

```bash
git fetch origin
git merge --no-commit --no-ff origin/master
# exit 0 → clean, skip to merge commit
# exit 1 → conflicts exist, continue to Phase 2
git merge --abort
```

If clean, report to the human and ask whether to proceed. If the human only asked to _check_, stop here.

## Phase 2 — PLAN

Produce `merge.md` in a tmp directory. **Read the full incoming commits and your branch state before writing** — not just the conflict markers.

There are two categories of conflict to address:

- **Mechanical conflicts** — literal git conflict markers in files. These are visible and enumerable.
- **Logical conflicts** — incoming changes that break functionality on your branch even though they merged cleanly. A new method signature on master means your branch's clean-merged call sites now pass stale arguments. A renamed constant means your branch's new code references something that no longer exists. These are invisible to git and more dangerous.

Both categories must appear in the plan.

### Structure of merge.md

```markdown
# Merge Plan: <branch> ← <target>

## Overview

How many incoming commits touch conflicting areas, what they did
(the intent), whether conflicts are structural or semantic.

## Mechanical Conflicts

### 1. `path/to/file.ext`

**Nature:** What each side did and why they conflict.
**Resolution:** Concrete strategy — which side to take as base,
what to port from the other, any adaptations needed.

## Logical Conflicts
Files that merged cleanly but whose assumptions are now broken by
incoming changes. For each: what broke, what needs updating, why
git couldn't detect it.

## Resolution Steps
Numbered steps covering both mechanical and logical fixes. Specific
enough that another agent could follow them without project context.

## Risk Assessment
Low / Medium / High — with justification.
```

### Plan guidelines

- **Name the commits** that caused the conflict (SHA + one-line summary).
- **Be concrete.** "Take master's approach" is too vague. Name signatures, methods, constants.
- **Call out transitive impacts** — resolving file A may invalidate assumptions in file B that merged cleanly (this is a logical conflict).
- **Check all clean-merged files** that import from or call into conflicting files. These are where logical conflicts hide.

## Phase 3 — EXECUTE

```bash
git merge origin/master
```

Resolve each file following the plan's Resolution Steps. For each mechanical conflict: read markers, apply resolution, remove markers, `git add`. Then fix logical conflicts in the clean-merged files.

```bash
grep -r '<<<<<<<' . || echo "Clean"
git commit --no-edit
```

## Phase 4 — VERIFY

1. **Compile / syntax check** — catch obvious breakage
2. **Unit tests** — run the project's test suite, record command + pass count
3. **Grep for conflict markers** — `grep -r '<<<<<<< ' .`

If tests fail, determine whether the failure is caused by the merge (fix it) or pre-existing on the incoming branch (note it, don't block).

## Self-check

- [ ] Merge plan covers both mechanical and logical conflicts
- [ ] No conflict markers remain (`grep -r '<<<<<<<'` clean)
- [ ] Unit tests pass (record command + count)
- [ ] Pre-existing failures documented as such
