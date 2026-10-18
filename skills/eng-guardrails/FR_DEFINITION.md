A functional requirements document (FR) records the externally observable behavior of a system. A person can check each requirement by using or watching the system from outside. An engineer could rebuild the behavior in any language from the FR and the ADR alone.

Belongs in an FR:
* Behavior that a user, an external system, or an operator can observe
* Data the system stores and access patterns
* Limits, timings, and guarantees a person can check
* Settings the user can change
* Behavior tied to one external system, client, or platform

Does not belong in an FR:
* Mechanisms and implementation details: transport, endpoints, exit codes, process ids, file, table, or column names
* Rationale and design choices (ADR)
* Scope, milestones, sequencing, and deferred work (plan)
* Development process: tests, verifiers, tooling
* Behavior the user did not ask for

Rules
* Start with a Terms section. Define each term once, then use it the same way everywhere.
* Group requirements in numbered sections. Write each as one numbered statement: an actor, "must", and an observable effect. Use short, active sentences.
* Requirements must read timelessly. Mark optional behavior "(Nice to have)".
* Every requirement must be tracable to something the user said. If the intended behavior is unclear, ask followup questions. Do not invent behavior.

Ask yourself:
Could someone check the behvaior from outside?
Would a rebuild lose behavior a user cares about without it?
If not, cut it.

Example entry
```md
5.4 The system must show a warning when the user presses a pressed button. The warning must say that undo is not available yet.
```
