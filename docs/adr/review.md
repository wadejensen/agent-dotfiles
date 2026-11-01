**Task:**
Skeptically review a new or existing ADR entry to identify writing quality issues, and reject entries which do not belong as an ADR.

**In scope:**
ADR validity and writing quality.

**Out of scope:**
Critical assessment of the substance of the design decision itself.

**Restriction**
If you are the agent who wrote, designed, or implemented this ADR, you must refuse to review due to the risk of confirmation bias.

**Instructions:**
Critically assess the ADR against [authoring-adrs.md](./authoring-adrs.md)
(required reading), and ask yourself the following questions:

**Validity**
* What is the decision being made?
* Does the decision actually merit being recorded as an ADR?
* Does the new ADR conflict with any existing ADRs?

**Style**
* Is the ADR written in eternal present tense, i.e. a timeless statement of fact?
* Does the ADR follow the correct format?

**Reader ergonomics**
* Is ADR self-contained and self-explanatory to a person new to this domain?
* Is the ADR written unambiguously, such that a future human or coding agent can easily adhere to it?
* Does the ADR contain redundant prose which could be removed without impacting a sophisticated reader's understanding?
* Could the ADR be rewritten to be expresse

**Relevance:**
Does the ADR contain additional information inappropriate in an ADR?
* Descriptions of user-observable behavior
* Business context or background information
* Ticket or work item reference ids
* Descriptions of functional requirements
* References to functional requirement items
* Implementation plans
* Milestone scope or sequencing
* Claims about low level code implementation details
* References to specific source code files, class names, variables or code details.

Respond with a prioritised list of findings including:
* Decision accepted/rejected as a valid ADR
* Conflicts
* Suggested writing improvements
* Any violations found
