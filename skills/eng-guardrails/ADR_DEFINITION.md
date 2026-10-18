An Architectural Decision Record (ADR) tracks intentional and consequential technical design decisions. An ADR entry documents a system design decision which is structural or expensive to change. They are architectural choices which should remain invariant in future, but are not obvious from reading the code itself.

Belongs in an ADR:
* Database technology, explicitly chosen libraries, rpc message serde format
* Data ownership, delivery guarantees
* Component responsibility
* System boundaries

Does not belong in an ADR:
* User-observable behavior 
* Code implementation details: variable names, method signatures, code snippets, schemas
* Functional or business requirements (requirements.md)
* Scope, milestones, sequencing, and deferred work (plan)
* Development process: test plan, implementation status
* Choices with a narrow blast radius, i.e. cheap to change
* Dates, author attribution

Rules
* Append new decisions as a numbered entry with a title and 1–2 lines of body text
* State each decision declaratively as a fact about the system. Include the reason and/or the rejected alternative where a future reader may be tempted to reverse it.

Evolving an ADR
Do not violate an ADR entry in a code change without human confirmation. ADRs are persistent guardrails for design intent. A solution which violates them indicates misalignment with the code owner's intent.
First consider alternative creative and aligned solutions.
If the architectural consequences of respecting an ADR seem worse than the impact of a proposed change, then flag the misalignment with the human collaborator for review.

Example entry
```md
## ADR-2: HTTP over a Unix domain socket
Client and server talk HTTP over a local socket. The system opens no network port, and the socket's presence advertises a running server.
```
