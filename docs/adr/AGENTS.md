Architectural Decision Records for the <insert domain> domain are stored in [ADR.md](./ADR.md).

## Human authorship
Engineers are expected to write new ADR entries manually, they encode critical, long-lived decisions, and are at most 1-3 lines in length.

## Agent usage
Agents should treat the `adr/` directory as read-only.

Implementing agents must not violate an ADR entry in a code change without human confirmation. ADRs are persistent guardrails for design intent. A solution which violates them indicates misalignment with the code owner's intent.

First, consider alternative creative and solutions aligned to ADR _intent_.
Then, if the consequences of respecting an ADR are likely worse than the impact of a proposed violation, flag the misalignment with the human collaborator. They should consider pausing the work item to either reassess their approach or re-evaluate the ADR.

## Writing and editing ADRs
See [review.md](./review.md).
