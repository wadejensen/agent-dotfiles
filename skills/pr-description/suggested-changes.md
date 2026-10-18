# Suggested-changes PRs

A **suggested-changes PR** sits on top of another author's PR. You branch from their
branch, make the changes you would otherwise write as review comments, and target
your PR back at their branch. The original author accepts your work when they merge
it.

Use this when a change is clearer as code than as a comment, but a direct commit to a
teammate's branch would be rude and could overwrite their in-flight work.

The reader is the **original author**, not a cold reviewer. They already own the
problem and the design. This changes what the description must give them.

## What changes from a normal PR description

- **Do not restate the problem or the feature.** They wrote it. A repeat wastes their
  time.
- **Link the original PR in the first line.** State plainly that this PR only suggests
  changes to it, to merge into its branch. Set this frame first.
- **Describe the changes at a conceptual level, with reasons.** Say what you changed
  and why, not each line. The author reads the diff for the mechanics. Give them the
  intent so they can judge whether they agree.
- **Raise anything controversial early.** Name the decisions the author may reject,
  the tradeoffs, and the points to weigh before they accept. Examples are a changed
  behavior, a broken convention, or a risk you are unsure about. The author needs this
  part most. Make it easy to find.
- **Keep it shorter than a feature PR.** The shared context already exists, so most of
  a normal description is redundant. A tight bullet list of conceptual changes and a
  short "things to consider" note is often the whole description.

## Shape

1. One line. Link the original PR. State that this PR suggests changes to merge into
   its branch.
2. Bulleted conceptual changes, each with its reason. Start each bullet with the
   change in bold. Keep the list tight.
3. A short call-out of concerns or controversial points for the author, if any.

## Template
[SUGGESTED_CHANGES.md](./SUGGESTED_CHANGES.md)