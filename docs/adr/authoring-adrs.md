# Architectural Decision Records

## Definition
An Architectural Decision Record (ADR) documents structural, long-lived technical design decisions. They are consequential system design choices which should remain invariant in future. They are expensive to change, but are often not obvious from reading the code itself.

An ADR should not describe user-observable behavior. Software architecture is about the hidden and opinionated choices we make in system design to deliver functional and maintainable software. They matter to us as developers, but the user will never see them.

## Decisions that deserve an ADR
* Database technology, explicitly chosen libraries, rpc message serde format
* Data ownership, delivery guarantees
* Component responsibility
* System boundaries and dependencies

## What an ADR is not 
* Functional or business requirements
* Scope, milestones, sequencing, and deferred work
* Development process: test plan, implementation status
* Choices with a narrow blast radius, i.e. cheap to change

## Writing ADRs
* Append new decisions as a numbered entry with a title, 1–2 lines of body text.
* State each decision declaratively as a fact about the system, in eternal present tense*.
* Include the reason for the ADR and/or the rejected alternative where a future reader may be tempted to reverse it.
* [Optional] Link an external ADR Proposal artefact that captures the background context, rationale, tradeoffs, spiking and discussion prior to ADR approval.

Example entry
```md
## ADR-002: Event buffer
The server process synchronously writes events to SQLite as an append only, persistent local buffer. Events written to SQLite survive server restarts. Events are flushed periodically to a remote store by an exporter process.
[Proposal doc](go.to/ADR-002)
```

*Eternal present tense means write your ADR as if it was an inevitable law of the universe. It is not a suggestion, it is not a plan, it is not a future looking requirement, i.e. "the system must x". It is a statement of _fact_: "the system does x" or "the system has x property". It is this way today, and always will be in future.

Even if in reality, an ADR may evolve, or it's just not implemented yet! ADRs can be forward looking, then implementation just becomes a state resolution loop towards the stated design.

## Review
Before requesting human review, ask an agent to skeptically review new ADR entries according to [review.md](./review.md).
Use an agent with a fresh context window to avoid confirmation bias.
