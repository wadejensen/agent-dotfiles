---
name: method-docstrings
description: Rewrite method, class, and module docstrings so they state the caller-facing contract, not the implementation. Use when asked to improve, review, or clean up docstrings for changed methods in a diff, or when a PR touches Python docstrings that need to read as a succinct behavior model.
---

# Method Docstrings

Give the reader a succinct, encapsulated mental model of method behavior, so they can call the method correctly without reading or understanding the implementation.

## Best practices

**Good**

- State the contract and behavior this method provides to the caller, not the implementation.
- Make the narrowest and briefest claim possible.
- Reads organically, as plain English written by a human.
- State any expectation or requirement for input parameters not already expressed by the signature.
- State any constraint or limitation the caller should know before using the method.
- Stays accurate if the implementation is refactored later.
- Standalone. Makes logical sense when read in isolation of the code.
- The best comment is no comment: prefer self-documenting code.

**Anti-patterns**

- Do not leak or explain internal implementation details.
- Do not express knowledge of the method's callers.
- Do not make claims about behavior more specific than the caller needs.
- Do not document trivial methods.
- Do not directly reference ids from requirement / specification / rfc documents.

**Parameters**

- Document a parameter only when its name and type do not already tell the reader its meaning.
- Document only the subset of parameters that need explanation.
- Exception: if more than half the parameters need docstrings, include the rest with an empty description for consistency.
- Include an example value where the expected structure is not clear from the name and type, e.g. `Map<String, String> arg`.
