# Principles

Principles are optional software design constraints, expressed as a series of high level "should" statements in priority order. Following a consistent set of principles leads to high quality, cohesive software, that stays aligned with developer design intent.

Always adhere to declared principles by default, where conflicts occur, follow the hierarchy of importance.

## Heirarchy of importance
* [Functional Requirements](./FR_DEFINITION.md) = MUST
* [Architectural Design Record](./ADR_DEFINITION.md) = MUST
* [Principles](./PRINCIPLES_DEFINITION.md) = SHOULD
  * Higher priority principles win over lower priority.

Principles often exist in tension with both each other, and the Functional Requirements and Architectural Decision Records. It is rarely possible to built a working useful piece of software without breaking or trading-off some principles.

It is acceptable to violate a principle in order to respect FR and ADR.
It is acceptable to violate a lower priority principle to respect a higher one.

Where conflicts occur, ask yourself:
* Is there an alternative creative solution which meets FR and ADR _and_ respects the principles?
* Can I tradeoff a lower priority principle for a higher one?
* Can I bend this principle or adhere to it's spirit rather than entirely violating it?

A project or component declares it's principles in `docs/principles.md`.

Example
```md
* Components should encapsulate implementation details from their callers.
* State manipulation operations should be explicit.
* I/O operations should occur at the edge of programs.
* AI agents should not contact any human other than their operator without explicit permission.
```

Example conflict resolution:
* A read-through cache implementation of a persistence repository interface encapsulates caching behavior from direct callers. Caching behavior remains explicit only where the caching impl is instantiated at dependency injection time.
* An API backend performs I/O to an external database mid-request to satify a functional requirement to read or write state.
* A customer service AI agent which must respond to user messages, vs a personal research agent which should not email another human to satisfy a speculative curiosity e.g. verifying store holiday opening hours, without explicit permission.
