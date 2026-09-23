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

  4  every refusal stated in a rule file must NAME the inventory row that carries it

A refusal is a sentence of the form "There is no X", "This system has no X" or "No X exists".
A sentence refusing two things - "no half-width rail and no resizable splitter" - is two
refusals, and the line must name a row for them.

The refusal names its row in an HTML comment on its own line or the line below it:

    There is no green tick. <!-- covered-by: Success and pending states -->

and a sentence the patterns read as a refusal that is not one says so instead:

    <!-- not-a-refusal: this refuses a measurement, not a surface -->

This replaces a keyword heuristic, and the replacement is the finding rather than a
refinement of it. That heuristic resolved a refusal to whichever row shared a word present in
at most three rows: 2 of 23 live refusals resolved to a row about something else - HTML email
to "Accordion and disclosure" via "export", and a sentence that refuses no surface at all to
"The mixed-face headline" via "measurement" - and four ordinary phrasings of a refusal were
not read as refusals at all. A check that reports the wrong row is worse than one that reports
none, because it reports success; and a rule that must guess at prose will keep guessing,
since the prose carries no fact about which row was meant. The declaration carries it.

The patterns now only ASK for a declaration rather than supplying one, so a phrasing they miss
costs a missing demand rather than a wrong answer. A declaration that sits on no refusal is
itself a failure, which is what catches a refusal reworded out of the patterns' reach.

What a pass still does not prove: that the named row is the right row for the surface, only
that the refusal names a row that exists, in the file a reader can see it in.

  5  the cross-check manifest must name the external taxonomies and the date

The inventory's opening claims its list is derived from what a design system has to answer
rather than from what this one contains. That claim is only checkable if the lists it was
checked against are named, with their sizes and the date, so the next reader can re-run the
check instead of trusting it.

  6  every internal link and anchor in the book must resolve

Same discipline, one level down. A row that names a section is a claim; so is a link in the
prose, and the book carries hundreds of them. Every Markdown file in the repository is opened,
in whatever directory it sits, and a link is a link in all four notations Markdown offers:
inline, inline with a title, reference definition, and a raw <a href>.

  7  every claim that a surface already has an entry must resolve to a covered or partial row

Rule 4 in the other direction. Rule 4 catches a refusal the inventory never heard of; nothing
caught the opposite, a sentence saying the book ADMITTED a surface it has no entry for. Two
such sentences shipped in the first public commit - "the same argument that admitted the 404
page and the link-preview card" and "already have entries here - Pricing as a page" - and
stood through every run of this script, because a measurement of absence had been retold as a
claim of presence across three review rounds.

A claim is "admitted X", "already has an entry here - X" or "the book covers X", read across a
whole paragraph so a claim wrapped over two lines is still one claim. Each object in a list
must match one covered or partial row whose SURFACE cell carries every content word of it:
an excluded row is not an entry, and a note mentioning the word is not the surface.

  8  every published restatement of the inventory must match it

The inventory is the source of two facts the rest of the book restates by hand: how many rows
it holds, and what one row's status is. Both drifted in the same way. `README.md` and
`SKILL.md` carry the surface count twice each, only the inventory's own counts line was
checked, and one change to it took three review rounds to find three stale copies. And a
branch that solved the high-contrast theme passed every check while the book still called it
"a named gap" in three places: rule 7 catches prose claiming an entry that does not exist, and
nothing caught prose calling a surface a gap once it had one.

A count is read by its phrase, because the phrase is unambiguous: every "N surfaces",
"N inventoried surfaces", "N covered", "N partial" and "N excluded" must equal the table.
A status claim is not read by its words, because the surface it names is free prose - "one -
the high-contrast theme - is still a named gap" - and guessing a row from prose is what rule 4
gave up. So a status phrase ("named gap", "still a gap", "still partial") asks for a
declaration beside it, on its line or the next, naming the row and the status it restates:

    is still a named gap. <!-- status: A high-contrast theme is partial -->

and the declaration must name a row that exists and match its status, so moving the row fails
every sentence still restating the old one. A declaration beside no status phrase fails too.

Checked rather than derived: the copies sit in prose and in `SKILL.md`'s frontmatter, which an
agent reads raw, so deriving them would mean a writer rewriting hand-authored files and still a
check to catch a stale write. `docs/` is not swept: it is a dated record of what shipped, and
its counts are true of that day. What a pass does not prove: that the declaration describes its
sentence, and that a status claim phrased outside the patterns was read at all.

  9  every published count of the ship checklist's questions must match the checklist

The same drift one file over. The closing checklist in `80-anti-patterns.md` is numbered, and
its size is restated in words in `README.md`, `SKILL.md`, `95-extending.md`, this inventory and
the checklist's own closing paragraphs. Five questions added at once left seven copies saying
"thirty" or "30", and nothing read any of them. A count is read by its phrase - "the N questions", "all N questions", "its N
questions", "N yes-or-no questions", "an N-question checklist", in digits or words - and must
equal the number of items in the checklist, which must also run 1 to N with none skipped.

Exits non-zero, and names every failure, when any claim is unbacked.

    python3 tools/check-coverage.py [repo-root]
"""
import re
import sys
from pathlib import Path

STATUSES = {"covered", "partial", "excluded"}
ROW = re.compile(r"^\|(?P<cells>.*)\|\s*$")
# All four ways a Markdown file names a target. The first three were the only one checked
# before, which left a titled link, a reference definition and a raw anchor unread, in a
# repository whose whole claim is that its internal references resolve.
LINKS = [
    re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'(][^)]*)?\s*\)"),
    re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?"),
    re.compile(r"<a\s[^>]*href\s*=\s*[\"']([^\"']+)[\"']", re.I),
]
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
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

# A refusal names the inventory row that carries it, in a comment beside it. A comment is
# invisible in the rendered book and visible in the file a reviewer reads, which is the point:
# the fact lives where the refusal is written rather than being inferred from its words.
DECLARED = re.compile(r"<!--\s*covered-by:\s*(.+?)\s*-->")
WAIVED = re.compile(r"<!--\s*not-a-refusal:\s*(.+?)\s*-->")
COMMENT = re.compile(r"<!--.*?-->")


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

    # The numbers on it are held to the table by rule 8, with every other copy.
    if not re.search(r"\*\*\d+ surfaces, \d+ covered, \d+ partial, \d+ excluded\.\*\*", text):
        failures.append(f"{inventory.name}  the counts line is missing or reworded; it must read "
                        f"**N surfaces, N covered, N partial, N excluded.**")
    return counts, sum(counts.values()), claims


def refusals_in(path: Path):
    """(line_no, phrase) for every refusal the patterns read in one rule file."""
    for line_no, line in unfenced(path):
        line = COMMENT.sub("", line)    # a declaration is not part of the sentence it marks
        for pattern in REFUSALS:
            for m in pattern.finditer(line):
                if SUBORDINATOR.search(line[:m.start()]):
                    continue
                for phrase in SPLIT_REFUSAL.split(m.group(1).strip()):
                    if phrase.strip():
                        yield line_no, phrase.strip()


def check_refusals(book: Path, inventory: Path, claims, failures: list):
    """Rule 4. The inventory itself is excluded from the sweep: its own rows state refusals by
    design, and a row cannot be the evidence that it exists.

    A declaration is read from the refusal's own line or the one below it, because a comment
    cannot go on a heading without entering its anchor, and cannot go on its own line inside a
    table without ending the table. Where a line carries two refusals it carries the rows for
    both, and the check holds each named row to existing rather than pairing them off.
    """
    surfaces = {surface for surface, _ in claims}
    swept = resolved = waived = 0
    for path in sorted(book.glob("*.md")):
        if path.name == inventory.name:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()

        def nearby(line_no, pattern):
            window = lines[line_no - 1:line_no + 1]
            return [m.group(1) for l in window for m in pattern.finditer(l)]

        declaring = set()
        for line_no, phrase in refusals_in(path):
            if nearby(line_no, WAIVED):
                waived += 1
                declaring.add(line_no)
                continue
            swept += 1
            named = nearby(line_no, DECLARED)
            declaring.add(line_no)
            if not named:
                failures.append(
                    f"{path.name}:{line_no}  refuses {phrase!r} and names no row in "
                    f"{inventory.name}. Write the row it is covered by beside it, as "
                    f"<!-- covered-by: the row's surface, exactly --> on this line or the "
                    f"next. A refusal that is written down is coverage; a refusal that is "
                    f"not is a gap")
                continue
            unknown = [n for n in named if n not in surfaces]
            if unknown:
                failures.append(
                    f"{path.name}:{line_no}  refuses {phrase!r} and names "
                    f"{', '.join(repr(u) for u in unknown)}, which {inventory.name} has no "
                    f"row for. The surface must match a row exactly")
                continue
            resolved += 1

        # A declaration the patterns found no refusal beside is the other half of the rule:
        # reword a refusal out of their reach and the declaration is left pointing at nothing,
        # which is the one signal available that the sweep has stopped seeing a refusal.
        for n, line in enumerate(lines, 1):
            for m in DECLARED.finditer(line):
                if n not in declaring and n - 1 not in declaring:
                    failures.append(
                        f"{path.name}:{n}  declares the row {m.group(1)!r} and no refusal was "
                        f"read on this line or the one above it. Either the sentence beside it "
                        f"no longer reads as a refusal, or the declaration is stale")
    return swept, resolved, waived


ADMISSIONS = [
    re.compile(r"\badmitted\s+(?P<obj>[^.:;,]+)", re.I),
    re.compile(r"\bha(?:s|ve) (?:an? )?entr(?:y|ies) here\s*[-:]\s*"
               r"(?P<obj>[^.:;]+?)(?=\s-\s|[.:;]|$)", re.I),
    re.compile(r"\b(?:the|this) (?:book|system) (?:already )?covers\s+(?P<obj>[^.:;]+)", re.I),
]
SPLIT_LIST = re.compile(r"\s*,\s*|\s+and\s+", re.I)
# Words of three letters or more that name no surface, so "the 404 page" needs a row
# carrying "404" and "page" and not one carrying "the".
FILLER = {"the", "its", "their", "this", "that", "our", "own", "one", "two", "both", "all"}


def paragraphs(path: Path):
    """([(offset, line_no)], text) per unfenced paragraph, so a claim wrapped across a line
    break is read whole."""
    block, starts = [], []
    for n, line in [*unfenced(path), (None, "")]:
        if n is not None and line.strip():
            starts.append((sum(len(b) + 1 for b in block), n))
            block.append(plain(line.strip()))
            continue
        if block:
            yield starts, " ".join(block)
        block, starts = [], []


def plain(text: str) -> str:
    """Markdown down to the words a reader sees, less file names: a link keeps its text, a
    `.md` path is a place rather than a surface, and emphasis marks are dropped."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\S+\.md(?:#\S*)?", "", text)
    return re.sub(r"[*`]", "", text)


def check_admissions(book: Path, inventory: Path, failures: list):
    """Rule 7. The inventory is swept too: its open decisions are prose, not rows."""
    surfaces = [cells[0].lower() for _, cells in rows(inventory.read_text(encoding="utf-8"))
                if cells[1] in ("covered", "partial")]

    def carries(surface, word):
        stem = word[:-1] if word.endswith("s") and len(word) > 4 else word
        return re.search(rf"(?<![a-z0-9]){re.escape(stem)}s?(?![a-z0-9])", surface)

    swept = resolved = 0
    for path in sorted(book.glob("*.md")):
        for starts, text in paragraphs(path):
            for pattern in ADMISSIONS:
                for m in pattern.finditer(text):
                    if SUBORDINATOR.search(text[:m.start()]):
                        continue
                    line_no = max(n for off, n in starts if off <= m.start())
                    for item in SPLIT_LIST.split(m.group("obj").strip()):
                        item = re.sub(r"\s+in$", "", item.strip())  # "X in <file.md>", file gone
                        words = [w for w in re.findall(r"[a-z0-9][a-z0-9-]*", item.lower())
                                 if len(w) >= 3 and w not in FILLER]
                        if not words:
                            continue
                        swept += 1
                        if any(all(carries(s, w) for w in words) for s in surfaces):
                            resolved += 1
                            continue
                        failures.append(
                            f"{path.name}:{line_no}  claims {item!r} already has an "
                            f"entry, and no covered or partial row in {inventory.name} names "
                            f"it: no surface cell carries all of {words}. A claim of presence "
                            f"is only true if the row exists")
    return swept, resolved


COUNT = re.compile(r"\b(\d+)\**\s+(?:inventoried\s+)?(surfaces|covered|partial|excluded)\b", re.I)
# Narrow on purpose: "a gap to report" is the book's general rule, not a claim about a row.
STATUS_CLAIM = re.compile(r"\bnamed gap\b|\bstill (?:an? |)(?:open |known |)gap\b|"
                          r"\bstill (?:partial|excluded|uncovered)\b", re.I)
RESTATES = re.compile(r"<!--\s*status:\s*(.+?)\s+is\s+(covered|partial|excluded)\s*-->")
# Rule 9. A number in digits or in words up to ninety-nine, then one of the phrases the book
# uses for the checklist; "answers two questions" names no checklist and is not read.
_UNITS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen").split()
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
         "eighty": 80, "ninety": 90}
_NUM = r"(\d+|[a-z]+(?:-[a-z]+)?)"
QUESTIONS = re.compile(rf"\b(?:the|all|its)\s+{_NUM}\s+questions\b|"
                       rf"\b{_NUM}(?:-question\b|\s+yes-or-no\s+questions\b)", re.I)


def number(word: str):
    """An integer from digits or English words, or None for any other word."""
    if word.isdigit():
        return int(word)
    head, _, tail = word.lower().partition("-")
    if not tail and head in _UNITS:
        return _UNITS.index(head)
    if head in _TENS and (not tail or tail in _UNITS[1:10]):
        return _TENS[head] + (_UNITS.index(tail) if tail else 0)
    return None


def checklist_size(book: Path, failures: list):
    """The number of items in the ship checklist, which must run 1 to N."""
    path = book / "80-anti-patterns.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == "## The checklist"), None)
    if start is None:
        failures.append(f"{path.name}  has no '## The checklist' section to count")
        return 0
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
               len(lines))
    items = [int(m[1]) for l in lines[start:end] if (m := re.match(r"^(\d+)\. ", l))]
    if items != list(range(1, len(items) + 1)):
        failures.append(f"{path.name}  the checklist is numbered {items}, not 1 to {len(items)}")
    return len(items)


def check_restatements(root: Path, inventory: Path, counts: dict, total: int, questions: int,
                        failures: list):
    """Rules 8 and 9. Every count and every declared status claim, in every live Markdown file,
    against the table, and every count of the checklist's questions against the checklist."""
    want = {"surfaces": total, **counts}
    status = {cells[0]: cells[1] for _, cells in rows(inventory.read_text(encoding="utf-8"))}
    files = sorted(f for f in root.rglob("*.md") if not {".git", "node_modules"} & set(f.parts)
                   and f.relative_to(root).parts[0] != "docs")
    copies = claims = 0
    for path in files:
        name, lines = path.relative_to(root), path.read_text(encoding="utf-8").splitlines()
        claimed = set()
        # Paragraphs rather than lines, so a phrase wrapped across a line break is still read.
        for starts, text in paragraphs(path):
            for m in COUNT.finditer(text):
                line_no = max(n for off, n in starts if off <= m.start())
                copies += 1
                noun = m.group(2).lower()
                if int(m.group(1)) != want[noun]:
                    failures.append(
                        f"{name}:{line_no}  says {m.group(0)!r}, and the table in "
                        f"{inventory.name} holds {want[noun]} {noun}. Every copy of a count "
                        f"moves with the inventory")
            for m in QUESTIONS.finditer(text):
                said = number(m.group(1) or m.group(2))
                if said is None:
                    continue
                line_no = max(n for off, n in starts if off <= m.start())
                copies += 1
                if said != questions:
                    failures.append(
                        f"{name}:{line_no}  says {m.group(0)!r}, and the checklist in "
                        f"80-anti-patterns.md holds {questions} questions. Every copy of its "
                        f"size moves with it")
            for m in STATUS_CLAIM.finditer(text):
                line_no = max(n for off, n in starts if off <= m.start())
                claims += 1
                claimed.add(line_no)
                declared = [d for l in lines[line_no - 1:line_no + 1] for d in RESTATES.finditer(l)]
                if not declared:
                    failures.append(
                        f"{name}:{line_no}  restates a status ({m.group(0)!r}) and names no row. "
                        f"Write <!-- status: the row's surface, exactly is its status --> on this "
                        f"line or the next, so the sentence fails when the row moves")
                for d in declared:
                    row, said = d.group(1), d.group(2)
                    if row not in status:
                        failures.append(f"{name}:{line_no}  restates the status of {row!r}, "
                                        f"which {inventory.name} has no row for")
                    elif status[row] != said:
                        failures.append(
                            f"{name}:{line_no}  says {row!r} is {said} ({m.group(0)!r}), and "
                            f"its row in {inventory.name} says {status[row]}. The prose is "
                            f"stale: rewrite it to what the row now says")
        for n, line in enumerate(lines, 1):
            for d in RESTATES.finditer(line):
                if n not in claimed and n - 1 not in claimed:
                    failures.append(f"{name}:{n}  declares the status of {d.group(1)!r} and no "
                                    f"status claim was read on this line or the one above it")
    return copies, claims


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
    if len(body) < 7:
        failures.append(f"{inventory.name}  the cross-check manifest names fewer than six "
                        f"external lists; it holds {max(len(body) - 1, 0)}")
    if not any(ISO_DATE.search(l) for l in section):
        failures.append(f"{inventory.name}  the cross-check manifest carries no date, so a "
                        f"reader cannot tell how stale it is")
    return max(len(body) - 1, 0)


def check_links(root: Path, failures: list):
    """Rule 6. Every internal link, and every anchor inside one, across the whole repository."""
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
    swept, resolved, waived = check_refusals(book, inventory, claims, failures)
    admitted, backed = check_admissions(book, inventory, failures)
    questions = checklist_size(book, failures)
    copies, restated = check_restatements(root, inventory, counts, total, questions, failures)
    lists = check_manifest(inventory, failures)
    links = check_links(root, failures)

    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{total} surfaces checked: {counts['covered']} covered, {counts['partial']} partial, "
          f"{counts['excluded']} excluded.")
    print(f"{swept} refusals swept across the rule files, {resolved} naming a row that "
          f"exists. {waived} sentence{'' if waived == 1 else 's'} declared not to be a "
          f"refusal.")
    print(f"{admitted} claims of an existing entry swept, {backed} resolved to a row.")
    print(f"{copies} published copies of a count and {restated} status claims checked "
          f"against the table and the {questions}-question checklist.")
    print(f"{lists} external taxonomies named in the cross-check manifest.")
    print(f"{links} internal links and anchors checked.")
    print(f"{len(failures)} unbacked.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
