#!/usr/bin/env python3
"""Fixture runner for redact_polyglot.sh.

Each dir under cases/ holds before.<ext>, after.<ext>, expected.<ext> (the
redacted after) and expected_report.txt. The runner diffs before->after, copies
after into a temp dir, runs the wrapper with the diff on stdin, and compares the
edited source and the report.

Usage: run_tests.py [--update] [case ...]
  --update  write expected.* / expected_report.txt from the tool's actual output
            (review the result by hand before committing).
"""

import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "redact_polyglot.sh"
CASES = HERE / "cases"


def run_case(case: Path, update: bool) -> str | None:
    """Return None on pass, or a failure description."""
    before = next(case.glob("before.*"))
    ext = before.suffix
    after = case / f"after{ext}"
    expected_src = case / f"expected{ext}"
    expected_report = case / "expected_report.txt"
    rel = f"src/{case.name}{ext}"

    diff = "".join(
        difflib.unified_diff(
            before.read_text().splitlines(keepends=True),
            after.read_text().splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
            n=3,
        )
    )

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        target = work / rel
        target.parent.mkdir(parents=True)
        shutil.copyfile(after, target)
        report = work / "report.txt"
        proc = subprocess.run(
            [str(TOOL), "--output-file", str(report), rel],
            input=diff, text=True, cwd=work, capture_output=True,
        )
        if proc.returncode != 0:
            return f"tool exited {proc.returncode}: {proc.stderr.strip()}"
        actual_src = target.read_text()
        actual_report = report.read_text()

    if update:
        expected_src.write_text(actual_src)
        expected_report.write_text(actual_report)
        return None

    problems = []
    for label, text in (("source", actual_src), ("report", actual_report)):
        if "SECRET_" in text:
            leaked = [ln for ln in text.splitlines() if "SECRET_" in ln]
            problems.append(f"{label} leaks original text: {leaked}")
    for label, want_path, got in (
        ("source", expected_src, actual_src),
        ("report", expected_report, actual_report),
    ):
        want = want_path.read_text()
        if want != got:
            problems.append(
                f"{label} mismatch:\n"
                + "".join(difflib.unified_diff(
                    want.splitlines(keepends=True), got.splitlines(keepends=True),
                    "expected", "actual"))
            )
    return "\n".join(problems) or None


def main() -> int:
    args = sys.argv[1:]
    update = "--update" in args
    names = [a for a in args if a != "--update"]
    cases = sorted(p for p in CASES.iterdir() if p.is_dir() and (not names or p.name in names))
    failed = 0
    for case in cases:
        result = run_case(case, update)
        if result is None:
            print(f"{'UPDATED' if update else 'PASS'}  {case.name}")
        else:
            failed += 1
            print(f"FAIL  {case.name}\n{result}")
    print(f"\n{len(cases) - failed}/{len(cases)} ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
