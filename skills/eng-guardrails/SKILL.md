# Eng Guardrails

Defines a hierarchy of design guardrails for software development and standarised operations on guardrails.

Required reading:
[Architectural Decision Record Definition](./ADR_DEFINITION.md)
[ADR Example](./ADR_EXAMPLE.md)
[Functional Requirements Definition](./FR_DEFINITION.md)
[FR Example](./FR_EXAMPLE.md)
[Principles Definition](./PRINCIPLES_DEFINITION.md)

`concept Guardrail = ADR | FR | Principle`

Project and component-level guardrails are defined in `docs/` directories.

## Skill actions

- **Review code** - Read implemented code and flag Guardrail violations. Scope may be one of: PR|commit|diff|directory|component|file.
Read the plan or specification document if it is available to understand the intent of the change. Output is:
* a prioritised list of violations classified as either ADR, FR, Principles.
* new suggested guardrails, if user intent conflicts with existing guardrails
* violations/conflicts include code and doc citations including full project relative file paths.

- **Add new ADR entry** - Append a user specified decision to the ADR. Check and flag any contradictions with existing decisons.

- **Add new FR entry** - Append a user specified requirement to the FR. Check and flag any contradictions.

- **Add new Principle entry** - Append a user specified decision to the Principles. User may adjust priority via manual edits.

- **Generate from code** - Generate ADR + FR docs from existing code. Research/Explore a codebase using subagents with missing or incomplete docs. Discover and interrogate design choices, patterns, publicly exposed functionality, and implicit and explicit invariants. If the user is familiar with the codebase, use the grill-me skill to confirm your understanding, then write the missing ADR and FR docs.

- **Recommend Guardrails** - Read a coding agent conversation transcript and recommend new guardrails to capture the user's expressed intent which belong as  capture  for user approval to document. Look for instances where the user disagree with the coding agent or asked it to change design or implementation details. Inspect relevant source code to properly understand the context of the discussion. Pay particular attention when user responses sound frustrated. Recommendations should be conservative, new entries should be apply broadly to the whole project or general software development best practices, not just a specific situation.