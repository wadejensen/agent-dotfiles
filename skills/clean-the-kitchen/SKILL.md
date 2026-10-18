## Cleaning the Kitchen

Before you add new functionality, picture the change you are going to make and where you are going to put it. Does the conceptual framework of this new behavior slot tidily into the conceptual framework of the area of the code where you will be adding it?

If not, is there a refactor of the current behavior that would make it trivial to implement the new functionality?
Ask yourself:
What new abstraction or framing of the problem would allow new functionality to be elegantly encapsulated alongside existing functionality?

If such a reconceptualizing is called for, suggest it to the user. If the user approves, abandon the current change, get to a clean working state, and, on a new branch, perform a refactoring. "Clean the kitchen before you make dinner." Then pause and consult the user, and begin again only after alignment.
