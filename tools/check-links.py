#!/usr/bin/env python3
"""Every internal link and anchor in every Markdown file in the repository must resolve.

A link is a claim that a file, or a section of one, exists. Every Markdown file is opened, in
whatever directory it sits, and a link is read in all four notations Markdown offers: inline,
inline with a title, a reference definition, and a raw <a href>. An anchor is resolved against
the target's headings with GitHub's slug. A link inside a fenced code block is documentation of
a path rather than a path, and a link with a scheme is a source, which check-sources.py probes.

Exits non-zero, and names every failure, when a link does not resolve.

    python3 tools/check-links.py [repo-root]
"""
import re
import sys
from pathlib import Path

# The first notation was the only one checked once, which left a titled link, a reference
# definition and a raw anchor unread.
LINKS = [
    re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'(][^)]*)?\s*\)"),
    re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?"),
    re.compile(r"<a\s[^>]*href\s*=\s*[\"']([^\"']+)[\"']", re.I),
]


def slug(heading: str) -> str:
    """GitHub's heading anchor: lowercase, drop anything but word characters, spaces and
    hyphens, then spaces to hyphens. Inline code and links are stripped first."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def unfenced(path: Path):
    """(line_no, line) for every line outside a fenced code block."""
    fenced = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield n, line


def headings(path: Path) -> set:
    return {slug(line.lstrip("#").strip()) for _, line in unfenced(path)
            if line.startswith("#")}


def check_links(root: Path, failures: list) -> int:
    files = sorted(f for f in root.rglob("*.md")
                   if ".git" not in f.parts and "node_modules" not in f.parts)
    cache, checked = {}, 0
    for path in files:
        for line_no, line in unfenced(path):
            for target in [t for pat in LINKS for t in pat.findall(line)]:
                if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("//"):
                    continue
                checked += 1
                fname, _, anchor = target.partition("#")
                dest = path if not fname else (path.parent / fname).resolve()
                where = path.relative_to(root)
                if not dest.exists():
                    failures.append(f"{where}:{line_no}  links to {target}, and "
                                    f"{fname} does not exist")
                    continue
                if not anchor:
                    continue
                if dest not in cache:
                    cache[dest] = headings(dest)
                if anchor not in cache[dest]:
                    failures.append(f"{where}:{line_no}  links to {target}, and "
                                    f"{dest.name} has no such section")
    return checked


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
    failures = []
    checked = check_links(root, failures)
    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"{checked} internal links and anchors checked, {len(failures)} unresolved.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
