#!/usr/bin/env python3
"""Identifier sweep over a git tree-ish, with a per-pattern hit count so a pattern that
matched nothing is visible rather than read as a clean result.

A DIAGNOSTIC, not a gate. The count per pattern is the feature: the audit's first sweep used
\\b under `git grep -E` on macOS, where it matched nothing and returned six lines that read
exactly like a clean result. The control pattern must hit AGENTS.md, so a sweep that reports
nothing anywhere has reported that it is broken.

    python3 tests/ident_sweep.py <repo> <tree-ish> [--show]
"""
import re, subprocess, sys
repo, tree = sys.argv[1], sys.argv[2]
show = "--show" in sys.argv
PATTERNS = {
    "home path": r"/Users/|/home/[a-z]|/private/|/var/folders|(?<![\w.])/tmp/|~/\.",
    "fleet tooling": r"firstmate|crewmate|secondmate|treehouse|herdr|no-mistakes|lavish|bearings|\bcaptain\b|\bfm[-/][a-z]",
    "model or vendor": r"claude|codex|chatgpt|\bgpt\b|gpt-\d|copilot|\bcursor\b(?! ?:| under|-)|gemini|anthropic|openai|\bllm",
    "email or host": r"[\w.+-]+@[\w-]+\.[\w.]+|macbook|\.local\b|localhost|127\.0\.0\.1|192\.168\.|\b10\.\d+\.\d+\.\d+",
    "other house products": r"\bquoth\b|\bgates\b",
    "agent (control: must hit AGENTS.md)": r"\bagents?\b",
}
files = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", tree],
                       capture_output=True, text=True, check=True).stdout.splitlines()
# This file's own source is every pattern below, written out. Left in, it adds one hit to five
# of the six categories and makes the counts read as five leaks that are not there.
SELF = "tests/ident_sweep.py"
files = [f for f in files if f != SELF]
print(f"{tree}: {len(files)} files")
for label, pat in PATTERNS.items():
    rx, hits = re.compile(pat, re.I), []
    for f in files:
        blob = subprocess.run(["git", "-C", repo, "show", f"{tree}:{f}"], capture_output=True).stdout
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append((f, n, line.strip()[:170]))
    byfile = {}
    for f, n, l in hits:
        byfile[f] = byfile.get(f, 0) + 1
    print(f"\n[{label}] {len(hits)} lines in {len(byfile)} files")
    if show or label in ("home path", "fleet tooling", "model or vendor", "email or host"):
        for f, n, l in hits[:60]:
            print(f"  {f}:{n}: {l}")
    else:
        print("  " + ", ".join(f"{f}({c})" for f, c in sorted(byfile.items())))
