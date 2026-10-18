Your role is to coordinate a method-docstrings writing review procedure between 3 coding agents to produce high quality comments according to the following process.

Orchestrator: You. Delegates to subagents according to procedure.
Agent 1: Wrote the original code and comments. (no direct contact).
Agent 2: Comment Writer. Blind writes new best practice comments without seeing original comments. (subagent)
Agent 3: Comment Comparer. Compares original and revised comments. Identifying critical gaps in revised present in original. (subagent)

Orchestrator and subagents must be >= Opus class model.

Orchestrator re-invokes Comment Writer agent multiple times, continuing the original session.

**Important:** Orchestrator and Comment Writer must both never read the original comments from git history to avoid bias.
Instructions should be brief. Subagents strictly receive only the information required for their own subtask.

Only the orchestrator should use comment stripping and changed docstring tools.
Subagents use the general agent.

**Input:**
A pull request url or git branch name of changes.
Optionally: the plan or specficiation doc describing to motivation or design for the code change.

**Output:**
Git commits of updated docstrings (pushed only if the branch has an upstream), or refusal.

Prerequsities:
Code must already be committed on the current branch.
Changed / uncommitted repo files unrelated to the branch changes should be ignored.
If the branch has an upstream, local must match it. With no remote / upstream, skip this check.
Refuse to run if condition not met, and ask the user to commit unsaved work.

Git exception: for the duration of this skill the orchestrator have permission to make the git commits as described below. Push only when an upstream exists.

## Process

0. *Redact comments* - Orchestrator
  - Use the `gh` CLI or git to list changed filenames only.
  - Ensure local branch matches remote, and affected files are unchanged in working tree, or abort.
  - Determine SHA: MERGE_BASE = `git merge-base HEAD origin/master` (the PR base)
  - Create a tmp dir for Comment Writer drafts.
  - Run command to redact changed docstrings and comments, and emit a report on affected methods and inline comments.
      `git diff <MERGE_BASE> -- <file1> <file2> <file3> ... \
        | <skill>/redact_polyglot.sh --output-file <tmp>/report.txt <file1> <file2> <file3> ...`
  - Git commit the redacted tree as "strip comments" (call this SHA STRIP); push if an upstream exists.
  - Invoke Comment Writer, include ONLY:
    - the tmp dir
    - command to see full redacted diff `git diff <MERGE_BASE> <STRIP> -- <file1> <file2> <file3> ...`
    - <tmp>/report.txt path
    - the paths of the source files to edit

1. Orchestrator -> Subagent call to Comment Writer
  1.a. **Understand the change and context.** - 
  - Read method-docstrings/SKILL.md
  - Read the entire code proposed change diff
  - If relevant, read the existing file contents.
  - If relevant, read the source for external callers of public methods.

  1.b **Blind first draft.**
  - Identify methods in the change whose docstrings changed. `cat <tmp>/report.txt`
  - Create a TODO item for each file with changed docstrings.
  - For each TODO:
    Write a temporary file containing:
      - succinct best-practice docstrings,
      - verbatim method signatures,
      - and no-op implementations.
  Yield.

  Example report.txt structure
  ```
  # path/to/file.py
  # redacted module level comment  <- consider writing a module docstring

  def foo(x: int) -> str:          <- signature only, consider writing its docstring

      y = 1
      # inline comment redacted marker   <- consider writing a comment here
      z = 2                              (±3 lines of real code as context)
  ```

2. Orchestrator -> Subagent call to Comment Writer
  2.a **Critical review.**
  - Create a TODO item for each file with changed docstrings.
  - For each TODO:
    - Read the first draft into context.
    - For each docstring sentence, ask:
      - What value does it add?
      - Would a reasonable engineer make a mistake if we removed it?
      - Could the reader infer that detail from elsewhere?
      - Does that part of the comment justify itself?
      - Does the overall comment justify itself?

  2.b **Second draft.**
  - Create a TODO item for each file with changed docstrings.
  - For each TODO:
    - Write a second draft with improved succinct docstrings directly to original source files.
  - commit "comments 2nd draft"
  Yield.  

3. Orchestrator -> Subagent call to Comment Checker
  3.a. **Understand the change and context.** - 
  - Read method-docstrings/SKILL.md
  - Use the `gh` CLI or git to list changed files.
  - Read the entire code proposed change
  - If relevant, read the existing file contents.
  - If relevant, read the source for external callers of public methods.

  3.b. **Compare original and draft.** 
  - Read method-docstrings/SKILL.md
  - Use git diff <commit id> to read the original comments deleted in "strip comments" commit.
  - Compare the original comments against the current draft.
  - Identify any important claims that cannot be derived from code alone.
  - **Do not anchor to the original docstrings.** If they were good, you would not have been asked to fix it.
  - We should retain a claim from the original docstring only if:
    - It states a critical contract the current draft missed.
    - According to method-docstrings/SKILL.md the information actually belongs in a comment.
    - Checked the claim is not falsifiable from code.
  - Report back a list statements worth incorporating into the next draft of comments.
  Yield.

4. Orchestrator -> Subagent call to Comment Writer
  4.a **Final draft.**
  - Skeptically consider the list of comment recommendations. Treat their author as naive.
  - Consider: does the new context add enough value to justify inclusion?
  - Only include absolutely necessary new information.
  - Prefer to err on the side of not accepting changes.
  - Edit the docstrings in the actual source files into the best version of themselves.
  - Commit (push if an upstream exists).
  Yield.

5. Orchestrator
  - Apply ASD-STE100 Simplified Technical English according to `.ste-writing/SKILL.md` to any changed comments.
  - Commit (push if an upstream exists)
  - Give the user a git diff command to produce a colorized diff showing final before and after of comment changes for human review.
  Yield.

## Tools

`redact_polyglot.sh` — wrapper that idempotently sets up this skill's venv (via `uv`) and runs `redact_polyglot.py`, which redacts changed code docs in place and writes a wording-free scope report. Works from any project this skill is symlinked into; the venv lives once, in this skill's own directory.

Usage:

git diff <base> | <skill>/redact_polyglot.sh --output-file <report_file> [file ...]

Files as args, or omit to cover every supported file the diff touches.

Supported files: `.py`, `.java`, `.sh`, `.bash`, `.ts`.

Contract:
- Strips or redacts comments from each file in place (only docs the diff touched).
- Writes <report_file> containing the method signatures, and code blocks whose docs are redacted.
- A comment deleted in the git diff is neither redacted nor reported.
