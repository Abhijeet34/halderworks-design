#!/usr/bin/env python3
"""Every test in this repository, in one command, with one exit code.

    python3 tests/run.py

The four tools in tools/ check the token set. These three check the tools: that the two
instruments are still two, that every hue the build accepts survives the second one, and that a
wrong input is actually refused rather than merely believed to be. They are adopted from the
2026-09-21 audit, which ran them against this repository and found 17 of 21 wrong inputs leaving
every tool green.

A test file nobody runs is not a check, which is the only reason this file exists: nothing in a
shell-driven repository discovers tests, so the gate has to name them. .github/workflows/
consistency.yml calls this file, and ci.yml's `checks` aggregate depends on that job.

Two diagnostics are deliberately not here, because they print rather than refuse and what they
measure belongs to another task's findings:

    python3 tests/coverage_probe.py          # which row each refusal resolved to, and by what word
    python3 tests/ident_sweep.py . HEAD      # identifiers in a tree, with a per-pattern hit count
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

SUITES = [
    ("invariants", "the two instruments are independent and still agree", "invariants.py"),
    ("hue sweep", "every hue the build accepts survives tools/contrast.py", "hue_sweep.py"),
    ("mutations", "a wrong input is refused by something", "mutation_tests.py"),
]


def main():
    failed = []
    for name, what, script in SUITES:
        print(f"\n{'=' * 78}\n== {name}: {what}\n{'=' * 78}")
        t0 = time.monotonic()
        rc = subprocess.run([sys.executable, str(HERE / script)]).returncode
        print(f"-- {name}: exit {rc} in {time.monotonic() - t0:.1f}s")
        if rc:
            failed.append(name)
    print(f"\n{len(SUITES) - len(failed)} of {len(SUITES)} suites passed")
    for name in failed:
        print(f"FAIL  tests/{dict((n, s) for n, _, s in SUITES)[name]}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
