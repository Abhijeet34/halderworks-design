#!/usr/bin/env python3
"""Verify the book's internal claims: the coverage inventory, its refusals, and its links.

A coverage inventory that nobody checks decays into a list of things somebody once intended,
which is the failure it exists to prevent. So every row is treated as a claim:

  1  covered   the named file must exist AND contain the named section
  2  partial   the same, where a section is named, and it must say what is missing
  3  excluded  it must give a reason

Those three check the inventory against the book. They cannot check the book against the
inventory, and that asymmetry had a measured cost: `35-layout.md` refused a resizable splitter
with a stated reason, an external pattern set carries `windowsplitter` as one of thirty
patterns, and the inventory had no row for it for three rounds. Seven of eight refusals
stated in rule files reached the inventory and one escaped, into exactly the class of gap the
inventory exists to report.

  4  every refusal stated in a rule file must resolve to an inventory row

A refusal is a sentence of the form "There is no X", "This system has no X" or "No X exists".
A sentence refusing two things - "no half-width rail and no resizable splitter" - is two
refusals and each must resolve on its own.

Resolving means one inventory row carries a content word of that refusal which is
DISTINCTIVE: present in at most MAX_ROWS rows of 141. A common word cannot resolve anything,
and that threshold is the whole strength of the rule rather than a detail. Measured on the
first version of this check, which accepted any match: deleting the Window splitter row left
the sweep at 22 of 22 resolved, because "rail" appears in several unrelated rows. The check
built to catch that leak did not catch it. With the threshold it does.

What a pass still does not prove: that the row it matched is the RIGHT row. The failure names
the words it looked for, so a reader can check.

  5  the cross-check manifest must name the external taxonomies and the date

The inventory's opening claims its list is derived from what a design system has to answer
rather than from what this one contains. That claim is only checkable if the lists it was
checked against are named, with their sizes and the date, so the next reader can re-run the
check instead of trusting it.

  6  every internal link and anchor in the book must resolve

Same discipline, one level down. A row that names a section is a claim; so is a link in the
prose, and the book carries hundreds of them across three directories.

Exits non-zero, and names every failure, when any claim is unbacked.

    python3 tools/check-coverage.py [repo-root]
"""
import re
import sys
from pathlib import Path

STATUSES = {"covered", "partial", "excluded"}
ROW = re.compile(r"^\|(?P<cells>.*)\|\s*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
# A word present in more rows than this is too common to be evidence that a refusal was
# considered. Three is the widest value at which "rail" stops resolving the splitter.
MAX_ROWS = 3
# A refusal sentence can carry more than one refused object.
SPLIT_REFUSAL = re.compile(r"\s+(?:and|or)\s+no\s+", re.I)
# "...when there is no error" and "where this system has no answer" are conditionals, not
# decisions about scope. A subordinator immediately before the phrase is what tells them
# apart, and without this the sweep reports two sentences that refuse nothing.
SUBORDINATOR = re.compile(r"\b(?:when|where|if|unless|while|because|once|whenever|whether|"
                          r"since|though|although)\W*$", re.I)

# A refusal, and the object it refuses, up to the first punctuation that ends the clause.
REFUSALS = [
    re.compile(r"\bthere (?:is|are) no\s+([^.:;,\n]+)", re.I),
    re.compile(r"\bthis system has no\s+([^.:;,\n]+)", re.I),
    re.compile(r"\bno\s+([^.:;,\n]+?)\s+exists\b", re.I),
]

# Words that carry no subject. Anything left after this and shorter than four characters is
# not distinctive enough to resolve a row on.
STOPWORDS = {
    "a", "an", "the", "and", "or", "not", "in", "on", "of", "for", "to", "it", "its", "this",
    "that", "here", "there", "with", "from", "as", "at", "by", "is", "are", "be", "been",
    "has", "have", "than", "then", "other", "second", "third", "own", "one", "two", "three",
    "more", "less", "any", "every", "all", "only", "still", "yet", "today", "such", "no",
    "system", "systems", "thing", "things", "way", "ways", "case", "cases", "kind", "kinds",
    "part", "parts", "point", "place", "line", "lines", "file", "files", "book", "them",
    "we", "our", "ours", "you", "your", "they", "their", "which", "what", "when", "where",
    "because", "also", "does", "do", "done", "made", "make", "makes", "here", "beside",
    "into", "over", "under", "about", "after", "before", "between", "within", "without",
}


def slug(heading: str) -> str:
    """GitHub's heading anchor: lowercase, drop anything but word characters, spaces and
    hyphens, then spaces to hyphens. Inline code and links are stripped first."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def unfenced(path: Path):
    """(line_no, line) for every line outside a fenced code block. A refusal inside a code
    fence is a sample, and a link inside one is documentation of a path rather than a path."""
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


def rows(text: str):
    """Yield (line_no, [cells]) for body rows of any four-column pipe table, skipping the head
    and the rule. A table with a different column count is not an inventory table."""
    for n, line in enumerate(text.splitlines(), 1):
        m = ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group("cells").split("|")]
        if len(cells) != 4:
            continue
        if set(cells[1].replace(" ", "")) <= {"-", ":"} and cells[1]:
            continue
        if cells[1].lower() in ("status",):
            continue
        yield n, cells


def content_words(phrase: str):
    phrase = re.sub(r"`([^`]*)`", r"\1", phrase)
    out = []
    for w in re.findall(r"[a-z][a-z-]*", phrase.lower()):
        if len(w) >= 4 and w not in STOPWORDS:
            out.append(w)
    return out


def check_inventory(inventory: Path, book: Path, failures: list):
    """Rules 1 to 3, plus the counts line, which is what stops the header drifting from the
    table it describes."""
    text = inventory.read_text(encoding="utf-8")
    cache, counts, claims = {}, {s: 0 for s in STATUSES}, []

    # A pipe inside a note splits the row into five cells and it silently stops being a row.
    # Three rows vanished that way when this inventory grew to 141, and only the counts line
    # caught it - which it would not have done had the header been written after the table.
    parsed = {n for n, _ in rows(text)}
    for n, line in enumerate(text.splitlines(), 1):
        if n in parsed or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any(c in STATUSES for c in cells):
            failures.append(f"{inventory.name}:{n}  carries a status and does not parse as a "
                            f"four-column row ({len(cells)} cells). An escaped pipe in a note "
                            f"does this, and the row stops being counted")

    for line_no, (surface, status, where, note) in rows(text):
        if status not in STATUSES:
            failures.append(f"{inventory.name}:{line_no}  {surface!r}: status {status!r} is not "
                            f"one of {sorted(STATUSES)}")
            continue
        counts[status] += 1
        claims.append((surface, note))

        if status in ("partial", "excluded") and not note.strip():
            failures.append(f"{inventory.name}:{line_no}  {surface!r}: {status} with no "
                            f"{'reason' if status == 'excluded' else 'note saying what is missing'}")

        if status == "covered" and not where.strip():
            failures.append(f"{inventory.name}:{line_no}  {surface!r}: covered but names nowhere")
            continue
        if not where.strip():
            continue

        ref = where.strip().strip("`")
        fname, _, anchor = ref.partition("#")
        target = book / fname
        if not target.exists():
            failures.append(f"{inventory.name}:{line_no}  {surface!r}: names {fname}, "
                            f"which does not exist")
            continue
        if not anchor:
            failures.append(f"{inventory.name}:{line_no}  {surface!r}: names {fname} with no "
                            f"section")
            continue
        if fname not in cache:
            cache[fname] = headings(target)
        if anchor not in cache[fname]:
            failures.append(f"{inventory.name}:{line_no}  {surface!r}: names {fname}#{anchor}, "
                            f"and {fname} has no such section")

    total = sum(counts.values())
    declared = re.search(r"\*\*(\d+) surfaces, (\d+) covered, (\d+) partial, (\d+) excluded\.\*\*",
                         text)
    if not declared:
        failures.append(f"{inventory.name}  the counts line is missing or reworded; it must read "
                        f"**N surfaces, N covered, N partial, N excluded.**")
    else:
        want = (total, counts["covered"], counts["partial"], counts["excluded"])
        got = tuple(int(g) for g in declared.groups())
        if want != got:
            failures.append(f"{inventory.name}  the counts line says {got} but the table holds "
                            f"{want} (surfaces, covered, partial, excluded)")
    return counts, total, claims


def check_refusals(book: Path, inventory: Path, claims, failures: list):
    """Rule 4. The inventory itself is excluded from the sweep: its own rows state refusals by
    design, and a row cannot be the evidence that it exists."""
    index = [(surface, (surface + " " + note).lower()) for surface, note in claims]

    def rows_carrying(word):
        return [surface for surface, blob in index if word in blob]

    swept = resolved = 0
    for path in sorted(book.glob("*.md")):
        if path.name == inventory.name:
            continue
        for line_no, line in unfenced(path):
            for pattern in REFUSALS:
                for m in pattern.finditer(line):
                    if SUBORDINATOR.search(line[:m.start()]):
                        continue
                    for phrase in SPLIT_REFUSAL.split(m.group(1).strip()):
                        words = content_words(phrase)
                        if not words:
                            continue
                        swept += 1
                        hit = None
                        for w in words:
                            carriers = rows_carrying(w)
                            if 1 <= len(carriers) <= MAX_ROWS:
                                hit = (w, carriers[0])
                                break
                        if hit:
                            resolved += 1
                        else:
                            seen = {w: len(rows_carrying(w)) for w in words}
                            failures.append(
                                f"{path.name}:{line_no}  refuses {phrase!r} and no row in "
                                f"{inventory.name} carries a distinctive word from it. Rows "
                                f"carrying each word: {seen}; a word needs 1 to {MAX_ROWS}. "
                                f"A refusal that is written down is coverage; a refusal that "
                                f"is not is a gap")
    return swept, resolved


def check_manifest(inventory: Path, failures: list):
    """Rule 5. The manifest is the section whose heading names the cross-check."""
    lines = inventory.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines)
                  if l.startswith("#") and "cross-check" in l.lower()), None)
    if start is None:
        failures.append(f"{inventory.name}  has no cross-check manifest section. The opening "
                        f"claims the list is derived from what a design system must answer; "
                        f"that is only checkable if the lists it was checked against are named")
        return 0
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
               len(lines))
    section = lines[start:end]
    body = [l for l in section if ROW.match(l) and not set(l.replace("|", "").replace(" ", "")) <= {"-", ":"}]
    if len(body) < 6:
        failures.append(f"{inventory.name}  the cross-check manifest names fewer than five "
                        f"external lists; it holds {max(len(body) - 1, 0)}")
    if not any(ISO_DATE.search(l) for l in section):
        failures.append(f"{inventory.name}  the cross-check manifest carries no date, so a "
                        f"reader cannot tell how stale it is")
    return max(len(body) - 1, 0)


def check_links(root: Path, failures: list):
    """Rule 6. Every internal link, and every anchor inside one, across the whole repository."""
    files = sorted([*(root / "design").glob("*.md"), *(root / "docs").glob("*.md"), *root.glob("*.md")])
    cache, checked = {}, 0
    for path in files:
        for line_no, line in unfenced(path):
            for target in LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("//"):
                    continue
                checked += 1
                fname, _, anchor = target.partition("#")
                dest = path if not fname else (path.parent / fname).resolve()
                if not dest.exists():
                    failures.append(f"{path.name}:{line_no}  links to {target}, and "
                                    f"{fname} does not exist")
                    continue
                if not anchor:
                    continue
                if dest not in cache:
                    cache[dest] = headings(dest)
                if anchor not in cache[dest]:
                    failures.append(f"{path.name}:{line_no}  links to {target}, and "
                                    f"{dest.name} has no such section")
    return checked


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
    book = root / "design"
    inventory = book / "05-coverage.md"
    if not inventory.exists():
        print(f"FAIL  {inventory} does not exist", file=sys.stderr)
        return 2

    failures = []
    counts, total, claims = check_inventory(inventory, book, failures)
    swept, resolved = check_refusals(book, inventory, claims, failures)
    lists = check_manifest(inventory, failures)
    links = check_links(root, failures)

    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{total} surfaces checked: {counts['covered']} covered, {counts['partial']} partial, "
          f"{counts['excluded']} excluded.")
    print(f"{swept} refusals swept across the rule files, {resolved} resolved to a row.")
    print(f"{lists} external taxonomies named in the cross-check manifest.")
    print(f"{links} internal links and anchors checked.")
    print(f"{len(failures)} unbacked.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
