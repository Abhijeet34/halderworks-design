#!/usr/bin/env python3
"""What tools/check-coverage.py's rule 4 actually matched, and whether its anchors are GitHub's.

A DIAGNOSTIC, not a gate: it prints and never refuses, because what it measures is audit
finding 8 - rule 4 resolves a refusal to a row by a content word, and two of the 23 live
refusals resolve to an unrelated row - and that finding belongs to another task. Asserting on
its output here would fix the shape of a fix somebody else is still choosing, which is why
tests/run.py runs the three suites that refuse, and leaves this one to be read.

    python3 tests/coverage_probe.py [repo-root]
"""
import importlib.util, re, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cc", root / "tools" / "check-coverage.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
book, inv = root / "design", root / "design" / "05-coverage.md"
fails = []
_, _, claims = cc.check_inventory(inv, book, fails)
index = [(s, (s + " " + n).lower()) for s, n in claims]

print("== rule 4: the row each refusal resolved to, and whether the match is a whole word")
n = sub_only = 0
for path in sorted(book.glob("*.md")):
    if path.name == inv.name:
        continue
    for ln, line in cc.unfenced(path):
        for pat in cc.REFUSALS:
            for m in pat.finditer(line):
                if cc.SUBORDINATOR.search(line[:m.start()]):
                    continue
                for phrase in cc.SPLIT_REFUSAL.split(m.group(1).strip()):
                    for w in cc.content_words(phrase):
                        rows = [s for s, b in index if w in b]
                        if 1 <= len(rows) <= cc.MAX_ROWS:
                            whole = [s for s, b in index if re.search(rf"\b{re.escape(w)}\b", b)]
                            n += 1
                            tag = "" if whole else "   <-- SUBSTRING ONLY"
                            sub_only += 0 if whole else 1
                            print(f"  {path.name}:{ln} refuses {phrase[:48]!r:52} via {w!r:14} -> row {rows[0][:44]!r}{tag}")
                            break
print(f"  {n} resolved, {sub_only} by a substring that is not a whole word in the row")

print("\n== rule 4 sensitivity: delete each inventory row in turn (counts line corrected) and re-run rule 4")
text = inv.read_text()
lines = text.splitlines()
row_lines = [ln for ln, _ in cc.rows(text)]
detected = 0; resolving_rows = set()
for ln in row_lines:
    kept = [l for i, l in enumerate(lines, 1) if i != ln]
    cl = [(c[0], c[3]) for _, c in cc.rows("\n".join(kept)) if c[1] in cc.STATUSES]
    f = []
    cc.check_refusals(book, inv, cl, f)
    if f:
        detected += 1
print(f"  {len(row_lines)} rows; deleting a row is noticed by rule 4 for {detected} of them")

print("\n== rule 6: the tool's slug() against GitHub's anchor algorithm, for every heading")
def gh_slug(h):
    h = re.sub(r"`([^`]*)`", r"\1", h); h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)
    h = h.strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)      # github-slugger: drop punctuation, keep each space
    return h.replace(" ", "-")
diff = 0; dup = 0
files = sorted([*(root / "design").glob("*.md"), *(root / "docs").glob("*.md"), *root.glob("*.md")])
for p in files:
    seen = {}
    for _, line in cc.unfenced(p):
        if line.startswith("#"):
            h = line.lstrip("#").strip()
            a, b = cc.slug(h), gh_slug(h)
            if b in seen:
                dup += 1
            seen[b] = 1
            if a != b:
                diff += 1
                print(f"  {p.relative_to(root)}: {h[:60]!r}: tool {a!r} / GitHub {b!r}")
print(f"  {diff} headings where the two differ; {dup} duplicate headings within one file (GitHub suffixes -1)")

print("\n== rule 6 scope: Markdown files the link check never opens")
checked = {p.resolve() for p in files}
import subprocess
allmd = [root / f for f in subprocess.run(["git", "-C", str(root), "ls-files", "*.md"], capture_output=True, text=True).stdout.split()]
for p in allmd:
    if p.resolve() not in checked:
        links = [t for _, l in cc.unfenced(p) for t in cc.LINK.findall(l) if not re.match(r"^[a-z][a-z0-9+.-]*:", t)]
        dead = [t for t in links if not (p.parent / t.partition("#")[0]).exists()]
        print(f"  {p.relative_to(root)}: {len(links)} internal links, {len(dead)} dead {dead[:4]}")
print(f"  {len(allmd)} tracked Markdown files, {len(checked & {p.resolve() for p in allmd})} opened by the link check")
