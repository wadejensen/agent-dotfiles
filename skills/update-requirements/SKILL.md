Review a coding agent conversation history, identify undocumented requirements and architectural decisions, and record them.

1. Read conversation transcript and list files changed.
2. Identify existing specification documents for the application.
3. Look for changed decisions, constraints, expected invariants, or where code produced did not meet user expectations and correction was required. These indicate possible undocumented requirements or decisions.
4. Update requirements.md and ADR.md to match user intent.

Read the code itself only where additional context is required to inform

Ask yourself, if we deleted the code, could a human or coding agent read requirements.md and ADR.md and successfully re-create the entire application in a different programming language and satisfy all of the user's expected application behaviors?
If not, document it.

What does belong in requirements.md:
* Externally observable behaviors of the system
* Features the system must provide
* How the user interacts with the system

What does NOT belong in requirements.md:
* code implementation details, e.g. coding style preferences, library choice, variable names, performance optimisations.

What does belong in ADR.md:
* Expensive/foundational or hard to change technical choices e.g. Postgres over Mongo, cache key design, 
* Responsibilities of new components / abstractions
* Invariants/expectations about the system design or component design which should hold in the future but are not directly enforced in code. E.g. "the application processes a single file at a time", "services must communicate over a binary rpc protocol with typed message schemas".

What does NOT belong in ADR.md:
* Code implementation details. e.g. prefer strategy pattern over deeply nested code branching
* Functional requirements. e.g. UX must provide a notifications settings panel for marketing opt-out.
