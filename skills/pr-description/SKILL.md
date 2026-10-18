---
name: generate-pr-description
description: Draft a concise, review-optimized PR title and description from the current branch diff.
---

# Generate PR Description

AI makes it cheap to produce large changes, so **review, understanding, and judgement is the bottleneck, not authoring**.
A PR description's job is to make review fast, and serve as a historical reference for why a code change was made.

A PR description gives the reviewer the **why** and the **shape of the what** so they can approve with confidence. It's an opportunity to give a primer on motivation, key concepts to contextualize the change before the reader sees the code.

Make the PR a service to its reviewers: explain the change, its boundary, the evidence behind it, and the decisions that need attention without making them reconstruct that story from the diff.

Concise yet clear beats thorough-but-verbose every time.
The diff already shows _what changed line-by-line_, don't simply restate the code changes.

If the PR is > 400 LOC change, include an indication of why it _wasn't_ split up,
e.g. "500 LOC of this diff is generated proto code", "300 LOC of this diff is tests".

**Does this PR suggest changes to someone else's open PR?** Different rules apply. The
reader already owns the problem, so most of the description below is redundant. See
[suggested-changes.md](./suggested-changes.md).

## Principles

- **Lead with the why.** What problem, incident, ticket, or constraint prompted this? A reviewer who understands the motivation reviews faster and better.
- **The what, at a high level.** Summarize the change and its shape. Not a file-by-file
  re-narration of the diff. Use bullets for multi-part changes.
- **Separate key changes from incidental changes.** Key changes alter contracts, introduce new components, or embody significant decisions. Other changes are supporting updates, small fixes, or changes to dependent files.
- **Be concise.** Explain _just enough_ for a reviewer to understand and trust the change. Cut restated code, cut marketing language, cut "this PR..." preamble. If a sentence doesn't help the reviewer decide, delete it.
- **Optimize for skimming** Tables and bold-labelled bullet pairs skim far better than prose. Use them for cases, states, and thresholds.
- **Surface what's risky or non-obvious.** Side effects, follow-ups, manual steps, things to watch. Don't bury these.
- **Link, don't paste.** Point to tickets, Slack threads, dashboards, docs for deeper context.
- **Use standard technical English.** Prefer plain, precise language, active voice, and terminology consistent with the codebase. Avoid slang, unexplained acronyms, and decorative language. See `ste-writing` skill.
- **Put mechanical / low level notes on the code, not in the description.** Anticipate questions the reviewer has while reading the code in order. Explanations for these belong in inline comments anchored on the code diff. Good for low-level detail that only matters at one line, such as "don't worry, this hunk is just a move from foo.java", or, "this helper now takes X instead of a Supplier<X>".

> Anti-pattern (common in AI-written PRs): a wall of text that restates every changed file,
> repeats the title three ways, and explains obvious code. This _adds_ review time. Don't.

> Anti-pattern (common in AI-written PRs): prose that assumes the reviewer has already read the code change. This is pointless.

## Respect the repo's template

Different repos have different PR templates and conventions — detect them, don't assume:

1. Look for a template: `.github/PULL_REQUEST_TEMPLATE.md`, `.github/pull_request_template.md`,
   or `.github/PULL_REQUEST_TEMPLATE/*.md`. If one exists, **fill its sections** rather than
   inventing your own.
2. Look for written conventions: `.cursor/rules/pull-request-conventions.mdc`, `CONTRIBUTING.md`,
   or `CLAUDE.md`. Follow them for title format and required sections.
3. **If no template exists**, use this structure:
   - Optional opening `## :train: PR train` — in no more than two sentences, explain the purpose of the entire train so the rest of the description has context.
   - Optional `Source: <link>` — link the Jira ticket or Slack thread that initiated the work. Include it only when it was actually part of the development context.
   - `## TL;DR` — one plain-English sentence in active voice. State the limitation, the required change, and the intended outcome where useful: "X did not support Y, so this updates X to achieve Z."
   - `## Context` — the background, problem, motivation, boundaries, and relevant evidence.
   - `## Changes` with `### Key changes` and `### Other changes` — describe the significant seams or decisions separately from incidental fixes and dependent-file updates. Omit `Other changes` if there are none.
   - Optional `## Reasoning` — use for large PRs with decisions reviewers need to assess. Give each decision its own `###` subheading and explain it in no more than two sentences.
   - `## Rollout / risk` — state the risk of merging, whether changes are behind a flag, and exactly what live system behavior changes. Include migration, monitoring, rollback, or manual steps when relevant. Say explicitly when there is no live behavior change.
   - Optional closing `## PR train` — list the train's PRs in order and mark the current PR. Use this when the opening train section is present.

Whatever the template, the principles above still apply to _how you fill it_.

## Title format

- Follow the repo's convention if one is documented.
- Otherwise: imperative mood, scannable, names the affected area.
  E.g. "[componentname] Add load shedding mechanism to Foo endpoint [JIRA-123]".

Omit the ticket number if you don't already know it.

## Steps

1. **Gather context** — run in parallel:
   - `git log <base>..HEAD --oneline` — commits on the branch
   - `git diff <base>...HEAD --stat` — changed-file summary
   - `git diff <base>...HEAD` — full diff
   - `git branch --show-current` — branch name
     (`<base>` is usually `origin/master` or `origin/main` — pick the repo's default branch.)
2. **Detect template & conventions** — as described above.
3. **Extract the Jira/issue key** — from the branch name (highest priority), then commits. Omit if
   none found, not every change needs a ticket.
4. **Identify affected packages/services** from the changed paths.
5. **Classify the changes** — identify changed seams, interfaces, and significant decisions as key
   changes. Treat supporting updates, small fixes, and dependent-file edits as other changes.
6. **Identify evidence and risk** — capture tests, analysis, flags, changed live behavior, rollout
   steps, monitoring, and rollback considerations supported by the diff or linked context. Never
   invent evidence, sources, rollout protections, or risk mitigations.
7. **Updating an existing PR?** Read the current description first and preserve its intent — refine,
   don't overwrite.
8. **Draft** the title and body following the content principles and the detected template.
9. **Output** in a clearly formatted markdown block the user can review and copy.

## Footer

- Never add "Generated with Claude Code" or any AI-attribution line to the description.

## Examples

_Concise default (no repo template):_

See [DEFAULT.md](./DEFAULT.md)

_Large change with key decisions:_

See [LARGE.md](./LARGE.md)

_Dependent PRs (PR train):_

See [DEPENDENT.md](./DEPENDENT.md)

_Suggested changes PRs:_

See [SUGGESTED_CHANGES.md](./SUGGESTED_CHANGES.md)
