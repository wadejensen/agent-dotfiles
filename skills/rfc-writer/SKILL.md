---
name: rfc-writer
description: Writes engineering RFCs as specification documents optimized for progressive disclosure. Leads with user experience, uses concrete examples, and splits large specs into numbered subpages. Use this to write engineering RFCs that will ultimately be implemented by a coding agent.
---

# rfc-writer

Assist the user in writing an engineering RFC. Output markdown that can be used by a human or agent to implement the stated goal.

## Stages

### 1. Investigation

- Ask for a detailed description of the goal. Need enough for a problem statement, goal, and definition of done. Present these back to confirm understanding.
- Ask for links to engineering files and any prior design decisions to get started.
- Use multiple oracles to investigate the codebase, focusing on relevant files and their key dependencies.
- Ask questions for clarity. Provide multiple options for key steps. Leave no stone unturned, do not accept vagueness. Use `grill-me` skill.
- Break problems down into small, known steps. Suggest improvements the user did not consider.
- Decisions can be deferred to implementation, but only when the user explicitly says so.

### 2. Creation

- Create the RFC per the structure below. Use ASCII diagrams to visualize the solution.
- **If the detailed solution exceeds ~300 lines**, split into numbered subpages in an `rfc/` directory: `00-index.md`, `01-<topic>.md`, ..., `NN-todo.md`. The index must be self-sufficient for understanding — subpages add precision.
- Include at least one concrete worked example early. Show realistic inputs/outputs with `...` for variable parts. Mockups over schemas — show what something looks like in practice rather than defining its type signature.
- Break the problem space into tasks completable by independent agents.

### 3. Review

- Use the oracle subagent to read the spec, cross-reference against any decisions log, and identify contradictions, omissions, and ambiguities. Act on recommendations, but do not consider extensions.
- Loop until the oracle reports no findings.
- If the RFC refines a prior design decision, update the decision document directly.

### 4. Finalization

- Ask for a human to review.
- Based on feedback, adjust the spec. Push back on changes that don't make sense.

## RFC Structure

### Problem Statement

The problem we are trying to solve. Terse, but detailed enough to understand without implicit context.

### Goal / Non-Goals

Bullet point lists of what we are and are not solving.

### Proposed Solution

**Lead with the user experience.** First section is a numbered walkthrough from the user's perspective — what they do, what they see, what happens. No implementation details.

Then: architecture (ASCII diagrams), pipeline/workflow walkthrough, a worked example, key design principles.

Then: detailed solution. Exhaustive specification with pointers to files, code snippets, and instructions. Break into small chunks implementable independently. Consider staging across multiple PRs. For multi-page specs, order subpages by importance to understanding — core behavior first, reference material (config, schemas) last.

### Definition of Done

What is required to mark the spec complete. Usually it means all verification checks pass and the to do list is complete.

### TODO List

Actions needed to complete the spec. Each TODO item should be small enough to fit within a single git commit, as an isolated unit of work. Mark items with whether they can be parallelized and whether a subagent can handle them. Add verification steps after every major change.

## Language & Tone

Terse, information-dense, not flowery. Dense is good — use structure (subpages, progressive disclosure) to manage complexity, not simplification. Employ standard technical english combined with real code snippets. Communicate as much information in as few words as possible without being confusing.

Challenge the user, do not be sycophantic. Think about simplicity, duplication reduction, information hiding, and code organization.
