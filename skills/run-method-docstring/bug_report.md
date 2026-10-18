# Bug: redact_polyglot report leaks original comment text from nearby comments

## Summary

`report.txt` must never contain the original text of a redacted comment. It does
when two touched comments are close together but not on consecutive lines. Each
comment gets its own context window, and each window redacts only its own
comment. So a nearby touched comment inside the ±3-line context is printed
verbatim, even though the tool redacts it in the source file.

Impact: the Comment Writer agent must write comments blind. A leak lets it see
the original wording, which defeats the purpose of the `run-method-docstring`
process. We first saw this in a real run, where 3 of 66 original comment lines
leaked into the report.

## Repro

```bash
#!/usr/bin/env bash
set -euo pipefail
TOOL=/path/to/.claude/skills/run-method-docstring/redact_polyglot.sh
D="$(mktemp -d)"; cd "$D"
git init -q && git commit -q --allow-empty -m base
cat > a.ts <<'EOF'
export const A = 1; // SECRET_A original comment
const MID = 5;
const B = 2; // SECRET_B original comment

export interface Event {
  id: string;
  // SECRET_C original comment
  name: string;
  /** SECRET_D original docstring */
  payload: unknown;
}
EOF
git add a.ts && git commit -q -m add
git diff HEAD~1 -- a.ts | "$TOOL" --output-file report.txt a.ts
grep -n SECRET a.ts        || echo "OK: source fully redacted"
grep -n SECRET report.txt  && echo "BUG: report leaks original text"
```

### Actual report.txt

```
# a.ts

export const A = 1; // inline comment redacted marker
const MID = 5;
const B = 2; // SECRET_B original comment              <-- leak

export const A = 1; // SECRET_A original comment       <-- leak
const MID = 5;
const B = 2; // inline comment redacted marker
...
  // inline comment redacted marker
  name: string;
  /** SECRET_D original docstring */                   <-- leak
  payload: unknown;

  id: string;
  // SECRET_C original comment                         <-- leak
  name: string;
  // inline comment redacted marker
```

`a.ts` itself is redacted correctly. Only the report leaks.

Control case: touched comments on consecutive lines (no code line between them)
do not leak. `comment_blocks` groups them into one block, so they share a window.

## Root cause

`redact_polyglot.py`, `comment_window()` (around lines 656–702):

- `changed_starts` is built only from `for comment in block`, which holds the
  comments of this window's own block.
- Any other line in the `start..end` context window falls through to
  `rendered.append(line)` and is copied verbatim.
- A touched comment in a different block that falls inside this window is
  therefore printed with its original text.

`build_report` documents "Untouched neighbor comments … render verbatim". That
is fine for untouched comments, but the code also renders *touched* neighbors
verbatim.

## Expected behaviour

- **Invariant:** no line of `report.txt` contains the original text of any
  comment or doc that the tool redacts in the source.
- Each window renders every touched comment inside its range as the marker,
  whichever block the comment belongs to.

## Suggested fix

Build the redaction map (`changed_starts`) from **all** touched inline comments
in the file, not just the window's block. For example, compute it once in
`build_report` and pass it into `comment_window`. Rendering windows from the
already redacted source would also work, but redacted docs collapse lines, so
the row numbers would need remapping.

Optional cleanup: windows that overlap or touch print the same lines twice (see
the A/B and C/D output above). Merging overlapping windows into one would remove
the duplication and make leaks of this kind structurally impossible.

## Acceptance test

Add a test to `tests/` that:
1. runs the tool on the fixture above (and an equivalent `.py`, `.java` and `.sh`
   fixture, since `comment_window` is shared), and
2. asserts that no `SECRET_` token appears in the report, and
3. asserts that the source file is redacted as before (no regression).
