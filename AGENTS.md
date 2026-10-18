## Placeholder. Agent to edit.
This AGENTS.md is a default placeholder.

Your first task is to ask the user what they want to build.

Once you have clear user input you must edit the preamble of this AGENTS.md file to capture a high level project description and write a TASK.md and an appropriate README.md file if it does not exist.

## Building
<eagerly fill project build commands>

## Testing
<eagerly fill project test commands>

## Ways of working
Offer to "write-plan" for new significant work items.
Once you have a plan first draft written, ask the human for feedback, offer to "grill-me".

## Ethos
Preserve the context window. Make liberal use of subagents for research and investigation.
Your session context is reserved for human interaction, decisions, and code writing.

**Always active skills, read on start:**
skills/human-comms/SKILL.md
skills/clean-the-kitchen/SKILL.md
skills/chestertons-fence/SKILL.md

Git commits are always made by a human with a short, meaningful commit message.
The human may ask you to stage changes, but you do not commit them.

---

## Memory subsystem

**Key files:**
memory/TASK.md - current work item. If absent ask the user for direction.
memory/sessions/session${N}.md - Summary of past sessions.
memory/specs/ - Current and previous specification documents for work items.

On new session / post-compaction:
1. Read the memory/TASK.md
2. Read the previous session memory file `memory/sessions/session${N}.md`.
3. Identify current session number `N+1`. Create a new empty file `touch memory/sessions/session${N+1}.md` for this session.
4. Continue implementing the task.

If the user says "wind down" or "checkpoint" use the `checkpoint` skill to persist progress
to `memory/sessions/session${N+1}.md` file, this provides the minimal information required for the next coding agent to rediscover the context need to progress this work.
