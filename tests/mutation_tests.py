#!/usr/bin/env python3
"""Make the system genuinely wrong, then see which tool notices.

Adopted from the 2026-09-21 security and technical audit, which ran these cases against this
repository and found that 17 of 21 wrong inputs left every tool green - 16 of them against a
claim the book or AGENTS.md makes. A check nobody has watched fail is a check nobody has
tested, and until this file landed no test existed for any refusal the system depends on.

Each case clones the repository into a fresh temporary directory, applies one mutation, runs
every check the CI workflow runs, and compares the verdict against what the case expects.
Nothing in the source repository is touched.

    python3 tests/mutation_tests.py [repo-root]

A case declares "caught" or "green", and the exit code is the point:

  - expected "caught" and the tools stayed green  -> FAIL. Something the book claims is not
    checked by anything.
  - expected "green" and the tools caught it      -> reported as IMPROVED, not as a failure.
    A case expects green only where the gap is real, named and accepted: C1's four refusal
    phrasings, which #7 chose not to chase because rule 4 now asks for a `covered-by`
    declaration rather than guessing a row, so a phrasing it misses costs a missing demand
    rather than a wrong answer; and C4, a limit check-coverage.py's own docstring discloses. When a change closes one, its case reports IMPROVED and its
    expectation must be flipped to "caught" in the same change, because a green expectation
    passes whether or not the tools catch it.

The cases against the solver tools/build.py retired with it; the brand file, the roster, the
ramps file a brand emits and the vendored faces each have theirs below.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
RESULTS = []

# The example brands CI builds, certifies and exports on every change.
BRANDS = ("quoth", "papertrace", "pointback")
CHECKS = [("ramps", ("tools/ramps.py", "--check")), ("contrast", ("tools/contrast.py",)),
          ("export", ("tools/export.py",)),
          *[(f"export-{b}", ("tools/export.py", f"examples/{b}")) for b in BRANDS],
          ("faces", ("tools/faces.py", "--vendored")),
          ("check-coverage", ("tools/check-coverage.py",)),
          ("invariants", ("tests/invariants.py",)),
          ("distinct", ("tools/distinct.py",))]


def clone():
    d = Path(tempfile.mkdtemp(prefix="hw-mut."))
    subprocess.run(["git", "clone", "-q", str(SRC), str(d / "r")], check=True)
    return d / "r"


def run(repo, *cmd):
    p = subprocess.run(["python3", *cmd], cwd=repo, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def case(name, expect, mutate, note="", by=None, says=()):
    """`by` names a check, or a tuple of checks, that must be among those refusing, where WHICH
    tool catches it is the claim: the second instrument measuring a file on its own, say. `says`
    names phrases the refusal must contain, where WHICH rule refuses is the claim. Every case
    also asserts a clean refusal rather than an unhandled crash: a crash exits non-zero too, so
    "caught" alone does not tell the two apart."""
    repo = clone()
    mutate(repo)
    codes, out = {}, ""
    for key, cmd in CHECKS:
        rc, o = run(repo, *cmd)
        codes[key] = rc
        out += o
    verdict = "green" if all(rc == 0 for rc in codes.values()) else "caught"
    extra, ok = "", True
    for b in ((by,) if isinstance(by, str) else by or ()):
        if codes[b] == 0:
            extra, ok = (extra + f" {b} did not refuse it, and the case requires it to").strip(), False
    if "Traceback" in out:
        extra, ok = (extra + " a tool printed a traceback instead of a clean refusal").strip(), False
    for phrase in ((says,) if isinstance(says, str) else says):
        if phrase not in out:
            extra, ok = (extra + f" no refusal says {phrase!r}").strip(), False
    label = ("PASS" if verdict == expect and ok
             else "IMPROVED" if expect == "green" and ok else "FAIL")
    RESULTS.append((label, name, expect, verdict, note))
    print(f"\n=== {name}")
    print(f"    expects {expect}{': ' + note if note else ''}")
    print("    " + "  ".join(f"{k}={v}" for k, v in codes.items()) + f"  -> {verdict}  [{label}]")
    for line in out.splitlines():
        if line.startswith("FAIL"):
            print("    | " + line[:190])
    if extra:
        print("    " + extra)
    shutil.rmtree(repo.parent)


def edit_json(repo, rel, fn):
    p = repo / rel
    data = json.loads(p.read_text(encoding="utf-8"))
    fn(data)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def edit_text(repo, rel, old, new):
    p = repo / rel
    text = p.read_text(encoding="utf-8")
    assert old in text, (rel, old)
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def rebuilt(repo):
    """What a contributor following AGENTS.md runs after editing a brand file."""
    assert run(repo, "tools/ramps.py")[0] == 0


# ---------------------------------------------------------------- the brand file and its ramps
case("R0 control: the house brand file is untouched", "green", lambda r: None)

case("R1 papertrace's accent hue moves to 262 and the ramps file is not rebuilt", "caught",
     lambda r: edit_json(r, "ramps/brands/papertrace.json",
                         lambda b: b["hues"]["accent"].__setitem__("hue", 262)),
     by="ramps", says="papertrace.tokens.css is stale")

case("R2 papertrace.tokens.css is hand-edited to a cream ground", "caught",
     lambda r: edit_text(r, "ramps/tokens/papertrace.tokens.css",
                         "--hw-gray-1: oklch(0.985 0.005 250);", "--hw-gray-1: oklch(0.985 0.030 85);"),
     by="ramps", says="papertrace.tokens.css is stale")

case("R3 quoth.tokens.css is hand-edited to radii 6/6/14 and a 3px icon stroke", "caught",
     lambda r: [edit_text(r, "ramps/tokens/quoth.tokens.css", old, new) for old, new in (
         ("--hw-radius-sm: 4px;", "--hw-radius-sm: 6px;"),
         ("--hw-radius-md: 7px;", "--hw-radius-md: 6px;"),
         ("--hw-radius-lg: 12px;", "--hw-radius-lg: 14px;"),
         ("--hw-icon-stroke: 1.5px;", "--hw-icon-stroke: 3px;"))],
     by="contrast", says=("radii 6px 6px 14px are none of the house's registers",
                          "--hw-icon-stroke is 3px"),
     note="the second instrument holds a brand's shape to the house registers on its own")

case("R4 pointback.tokens.css gains a role in its brand block", "caught",
     lambda r: edit_text(r, "ramps/tokens/pointback.tokens.css", "  --hw-icon-stroke: 2px;",
                         "  --hw-icon-stroke: 2px;\n  --hw-accent-text: oklch(0.5 0.1 230);"),
     by="contrast", says="--hw-accent-text is in the brand block",
     note="95-extending.md: a brand names inputs, never a token")

case("R5 quoth's brand file names a display face the roster does not carry", "caught",
     lambda r: edit_json(r, "ramps/brands/quoth.json",
                         lambda b: b["faces"].__setitem__("display", "Bricolage Grotesk")),
     by="ramps", says="faces.display 'Bricolage Grotesk' is not a roster face")

case("R6 quoth's brand file sets --hw-accent directly", "caught",
     lambda r: edit_json(r, "ramps/brands/quoth.json",
                         lambda b: b.__setitem__("--hw-accent", "oklch(0.6 0.1 255)")),
     by="ramps", says="unknown key '--hw-accent'")

case("R7 quoth's mono names a proportional face", "caught",
     lambda r: edit_json(r, "ramps/brands/quoth.json",
                         lambda b: b["faces"].__setitem__("mono", "Archivo")),
     by="ramps", says="faces.mono 'Archivo' is not one of IBM Plex Mono, Martian Mono")

case("R8 papertrace takes the moulded register and is rebuilt", "green",
     lambda r: (edit_json(r, "ramps/brands/papertrace.json",
                          lambda b: b.__setitem__("shape", "moulded")), rebuilt(r)),
     note="a register the roster carries is a rebuild, never a refusal; the exports follow on "
          "the next tools/export.py, and the workflow's drift check holds that")

# ---------------------------------------------------------------- the face roster
case("T1 a roster face is relicensed from the OFL", "caught",
     lambda r: edit_json(r, "ramps/roster.json",
                         lambda x: x["faces"]["Figtree"].__setitem__("licence", "Fontshare-FFL")),
     by="ramps", says="a roster face is OFL-1.1 and nothing else",
     note="20-type.md#the-licence-rule: every roster face is OFL, from 90-evidence.md's survey")

case("T2 a roster face drops its licence text", "caught",
     lambda r: edit_json(r, "ramps/roster.json",
                         lambda x: x["faces"]["Martian Mono"].pop("licenceText")),
     by="ramps", says="'Martian Mono' is self-hosted and names no ['licenceText']",
     note="20-type.md#a-brands-faces: a self-hosted face pins its file and the licence beside it")

case("T3 the house default names a face the roster does not carry", "caught",
     lambda r: edit_json(r, "ramps/roster.json",
                         lambda x: x["default"]["faces"].__setitem__("sans", "Public Sans Next")),
     by="ramps", says="faces.sans 'Public Sans Next' is not a roster face")

# ---------------------------------------------------------------- the vendored faces
def append_bytes(rel):
    def f(repo):
        with (repo / rel).open("ab") as fh:
            fh.write(b"\0")
    return f


case("F1 a vendored face's file gains one byte", "caught",
     append_bytes("fonts/archivo/archivo-latin-wdth-normal.woff2"),
     by="faces", says="and the roster pins",
     note="the roster pins every vendored file by sha256")

case("F2 IBM Plex Mono's OFL.txt is normalised to LF line endings", "caught",
     lambda r: (r / "fonts/ibm-plex-mono/OFL.txt").write_bytes(
         (r / "fonts/ibm-plex-mono/OFL.txt").read_bytes().replace(b"\r\n", b"\n")),
     by="faces", says="fonts/ibm-plex-mono/OFL.txt has sha256",
     note=".gitattributes keeps fonts/ byte for byte; the licence text is pinned at its upstream "
          "sha256")

case("F3 fonts.css loads Literata from a CDN", "caught",
     lambda r: edit_text(r, "fonts/fonts.css", 'url("literata/literata-latin-opsz-normal.woff2")',
                         'url("https://fonts.gstatic.com/s/literata/v1/x.woff2")'),
     by="faces", says=("loads https://fonts.gstatic.com", "never loads literata/"),
     note="no request off the page's own origin for a house face")

case("F4 a face file lands in fonts/ with no roster entry", "caught",
     lambda r: (r / "fonts/archivo/Archivo-Bold.woff2").write_bytes(b"wOF2"),
     by="faces", says="fonts/archivo/Archivo-Bold.woff2 is in no roster entry")


# ---------------------------------------------------------------- check-coverage.py
def cov_edit(repo, fn):
    p = repo / "design" / "05-coverage.md"
    p.write_text(fn(p.read_text(encoding="utf-8")), encoding="utf-8")


def c0(repo):
    with (repo / "design" / "35-layout.md").open("a") as fh:
        fh.write("\nThere is no zoetrope carousel.\n")


case("C0 control: a rule file gains 'There is no zoetrope carousel.'", "caught", c0)

for phrase in ("This system does not ship a zoetrope carousel.", "A zoetrope carousel is refused.",
               "We exclude the zoetrope carousel.", "Zoetrope carousels are out of scope."):
    def c1(repo, phrase=phrase):
        with (repo / "design" / "35-layout.md").open("a") as fh:
            fh.write("\n" + phrase + "\n")
    case(f"C1 a rule file gains the refusal {phrase!r}", "green", c1,
         note="a residual #7 chose and documents: a phrasing rule 4 misses is a missing demand")


def c2(repo):
    with (repo / ".github" / "PULL_REQUEST_TEMPLATE.md").open("a") as fh:
        fh.write("\nSee [the rules](../design/does-not-exist.md).\n")
    (repo / "exports" / "README.md").write_text("[gone](../design/nope.md)\n", encoding="utf-8")


case("C2 a dead link in .github/PULL_REQUEST_TEMPLATE.md and in a new exports/README.md",
     "caught", c2, note="audit finding 8, closed by #7: the link check opens every Markdown file")


def c3(repo):
    with (repo / "README.md").open("a") as fh:
        fh.write('\n[titled](design/nope.md "a title")\n\n[ref style][x]\n\n'
                 '[x]: design/also-nope.md\n\n<a href="design/nope-3.md">html</a>\n')


case("C3 README.md gains a titled link, a reference-style link and an <a href>, all dead",
     "caught", c3, note="audit finding 8, closed by #7: titled, reference and <a href> links are read")


def c4(repo):
    def f(text):
        lines = text.splitlines(keepends=True)
        i = next(n for n, line in enumerate(lines) if line.startswith("|") and "| covered |" in line)
        cells = lines[i].split("|")
        heads = sorted(re.findall(r"^#+ (.+)$",
                                  (repo / "design" / "00-brand-book.md").read_text(encoding="utf-8"),
                                  re.M))
        cells[3] = " `00-brand-book.md#" + heads[0].lower().replace(" ", "-") + "` "
        lines[i] = "|".join(cells)
        return "".join(lines)
    cov_edit(repo, f)


case("C4 a covered row is re-pointed at an unrelated section that exists", "green", c4,
     note="a limit the tool's own docstring discloses: it proves a section exists, not that it answers")


def c5(repo):
    """One more covered row and a counts line that moved with it, as a real inventory change
    does; README.md is the copy left behind."""
    def f(text):
        text = re.sub(r"\*\*(\d+) surfaces, (\d+) covered",
                      lambda m: f"**{int(m[1]) + 1} surfaces, {int(m[2]) + 1} covered", text)
        row = next(l for l in text.splitlines() if "| covered |" in l)
        return text.replace(row, row + "\n| Zoetrope carousel |" + row.split("|", 2)[2], 1)
    cov_edit(repo, f)
    p = repo / "SKILL.md"
    p.write_text(re.sub(r"\b(\d+)(\**\s+(?:inventoried\s+)?surfaces)",
                        lambda m: f"{int(m[1]) + 1}{m[2]}", p.read_text(encoding="utf-8")),
                 encoding="utf-8")


case("C5 the inventory gains a row, and README.md keeps the old surface count", "caught", c5,
     note="#10 found three stale copies in three review rounds; rule 8 holds every copy")


def c6(repo):
    """A true status claim is written against a partial row, then the row moves to covered with
    the counts line moving with it, and the claim is left as it was."""
    inv = (repo / "design" / "05-coverage.md").read_text(encoding="utf-8")
    # A partial row that names a section, so moving it to covered is otherwise a valid row.
    surface = re.search(r"^\| ([^|]+?) \| partial \| `[^`]+#[^`]+` \|", inv, re.M)[1]
    with (repo / "design" / "35-layout.md").open("a") as fh:
        fh.write(f"\n{surface} is still a named gap. <!-- status: {surface} is partial -->\n")

    def f(text):
        text = re.sub(r"\*\*(\d+) surfaces, (\d+) covered, (\d+) partial",
                      lambda m: f"**{m[1]} surfaces, {int(m[2]) + 1} covered, {int(m[3]) - 1} partial",
                      text)
        return text.replace(f"| {surface} | partial |", f"| {surface} | covered |")
    cov_edit(repo, f)


case("C6 a partial row becomes covered, and prose declared against it still calls it a named gap",
     "caught", c6, note="#11 rebased green while the book still called the high-contrast theme a gap")


def c7(repo):
    """The checklist gains a question, numbered in turn, and SKILL.md keeps the old count."""
    p = repo / "design" / "80-anti-patterns.md"
    text = p.read_text(encoding="utf-8")
    last = max(int(n) for n in re.findall(r"^(\d+)\. ", text, re.M))
    line = next(l for l in text.splitlines() if l.startswith(f"{last}. "))
    p.write_text(text.replace(line, line + f"\n{last + 1}. Is this a zoetrope carousel?", 1),
                 encoding="utf-8")


case("C7 the ship checklist gains a question, and SKILL.md keeps the old count", "caught", c7,
     by="check-coverage", says="Every copy of its size moves with it",
     note="rule 9: five questions added at once left seven copies of the old count unread")


# ---------------------------------------------------------------- the CI workflow's own body
def workflow_block(repo):
    """The `run every check` step body of consistency.yml, extracted verbatim and dedented.

    ci.yml and maintenance.yml both call that file, so this is the body a merge depends on."""
    lines = (repo / ".github" / "workflows" / "consistency.yml").read_text(
        encoding="utf-8").splitlines()
    i = next(n for n, line in enumerate(lines) if line.strip() == "id: collect")
    start = next(n for n in range(i, len(lines)) if lines[n].strip() == "run: |") + 1
    body = []
    for line in lines[start:]:
        if line.strip() and not line.startswith(" " * 10):
            break
        body.append(line[10:])
    return "\n".join(body)


def wf(name, expect, mutate, note=""):
    repo = clone()
    mutate(repo)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam",
                    "mutation", "--no-verify"], cwd=repo, check=True)
    # RUNNER_TEMP too: the step keeps every failing check's full output under it, and in CI
    # the runner's own would collect this deliberately broken clone's logs into the real
    # consistency-logs artifact.
    env = dict(os.environ, GITHUB_OUTPUT=str(repo.parent / "out"),
               GITHUB_STEP_SUMMARY=str(repo.parent / "sum"), RUNNER_TEMP=str(repo.parent))
    direct, dout = run(repo, "tools/export.py")
    subprocess.run(["git", "checkout", "-q", "--", "."], cwd=repo)
    # The extracted body calls tests/run.py, which calls this file, which would clone and run the
    # body again, once per case, for ever. This clone is disposable and thrown away with
    # shutil.rmtree below, so overwriting its uncommitted copy of tests/run.py with a stand-in
    # that prints and exits 0 breaks the recursion without touching the real repository or the
    # real test file; the checkout above already restored every tracked file, so this write is
    # the last thing that happens to the clone before the body runs.
    (repo / "tests" / "run.py").write_text(
        "#!/usr/bin/env python3\n"
        "print('tests/run.py: standing in for the suite under mutation.')\n", encoding="utf-8")
    p = subprocess.run(["bash", "-e", "-c", workflow_block(repo)], cwd=repo, env=env,
                       capture_output=True, text=True)
    verdict = "green" if p.returncode == 0 else "caught"
    label = "PASS" if verdict == expect else ("IMPROVED" if expect == "green" else "FAIL")
    RESULTS.append((label, name, expect, verdict, note))
    print(f"\n=== {name}\n    expects {expect}{': ' + note if note else ''}")
    tail = dout.strip().splitlines()[-1][:160] if dout.strip() else ""
    print(f"    tools/export.py run directly: exit {direct}: {tail}")
    print(f"    consistency.yml 'run every check' step under bash -e: exit {p.returncode}"
          f"  -> {verdict}  [{label}]")
    # A step that aborts before writing its outputs is its own defect: maintenance.yml reads
    # `failed` to decide whether to open an issue, so an absent output is a failure nobody hears.
    gh_out = repo.parent / "out"
    flag = re.findall(r"failed=(\d)", gh_out.read_text(encoding="utf-8")) if gh_out.exists() else []
    if flag:
        print(f"    GITHUB_OUTPUT failed={flag[-1]}")
    else:
        print("    GITHUB_OUTPUT: the step wrote no `failed` output at all")
        RESULTS[-1] = ("FAIL", name, expect, verdict + " (no output written)", note)
    # GitHub refuses a job summary past 1024k and then shows none of it.
    summary = repo.parent / "sum"
    size = summary.stat().st_size if summary.exists() else 0
    print(f"    GITHUB_STEP_SUMMARY: {size:,d} bytes")
    if size > 100_000:
        RESULTS[-1] = ("FAIL", name, expect, f"{verdict} (summary {size:,d} bytes)", note)
    shutil.rmtree(repo.parent)


def e1(repo):
    p = repo / "tools" / "export.py"
    p.write_text(p.read_text(encoding="utf-8").replace(
        "        src = sources(root)\n", "        raise RuntimeError('exporter is broken')\n", 1),
        encoding="utf-8")


wf("E1 tools/export.py raises before writing anything", "caught", e1,
   note="an exporter that writes nothing leaves a clean diff, so the diff cannot be the check")


def e2(repo):
    # A brand file is edited and its ramps rebuilt, as AGENTS.md says, and the exports are left as
    # they were: the step's drift check is the only thing that sees an export behind its source.
    p = repo / "ramps" / "brands" / "pointback.json"
    brand = json.loads(p.read_text(encoding="utf-8"))
    brand["iconStroke"] = "1.75px"
    p.write_text(json.dumps(brand, indent=2) + "\n", encoding="utf-8")
    assert run(repo, "tools/ramps.py")[0] == 0


wf("E2 a brand file is rebuilt and its exports are not regenerated; the drift check reports it",
   "caught", e2, note="AGENTS.md: regenerating exports/ leaves nothing in git status --porcelain")


def e3(repo):
    # A check whose failure prints more rows than the report keeps: tests/run.py's own failure
    # was 1 MB. Its report must still be written, with failed=1, and stay a summary.
    p = repo / "tools" / "distinct.py"
    p.write_text("import sys\nfor i in range(5000):\n    print(f'FAIL  row {i}')\nsys.exit(1)\n",
                 encoding="utf-8")


wf("E3 a check fails with 5,000 FAIL rows; the step still reports it and writes failed=1",
   "caught", e3, note="past 40 rows, grep | head under pipefail used to end the step unreported")
for label, name, expect, verdict, note in RESULTS:
    print(f"{label:9} expected {expect:6} got {verdict:6}  {name}")
bad = [r for r in RESULTS if r[0] == "FAIL"]
improved = [r for r in RESULTS if r[0] == "IMPROVED"]
print(f"\n{len(RESULTS)} cases: {len(RESULTS) - len(bad) - len(improved)} as expected, "
      f"{len(improved)} improved, {len(bad)} failed")
for label, name, expect, verdict, note in bad:
    print(f"FAIL  {name}: expected {expect}, got {verdict}", file=sys.stderr)
sys.exit(1 if bad else 0)
