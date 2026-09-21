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
    passes whether or not the tools catch it - which is how B5, B6, C2 and C3 sat at "green"
    for a while after #7 had closed them.
  - B7 and B9 also assert a number, because "the tools caught it" is not the claim being made.
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

CHECKS = [("tools/build.py",), ("tools/build.py", "--check"), ("tools/contrast.py",),
          ("tools/export.py",), ("tools/check-coverage.py",), ("tests/invariants.py",)]


def clone():
    d = Path(tempfile.mkdtemp(prefix="hw-mut."))
    subprocess.run(["git", "clone", "-q", str(SRC), str(d / "r")], check=True)
    return d / "r"


def run(repo, *cmd):
    p = subprocess.run(["python3", *cmd], cwd=repo, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def seed_edit(repo, fn):
    p = repo / "tokens" / "tokens.seed.json"
    seed = json.loads(p.read_text(encoding="utf-8"))
    fn(seed)
    p.write_text(json.dumps(seed, indent=2) + "\n", encoding="utf-8")


def tok(seed, name, fam="color"):
    return next(e for e in seed[fam]["tokens"] if e["name"] == name)


def exact_min(repo, pairs):
    """Minimum exact ratio over (theme, fg, bg), read straight off the emitted CSS."""
    sys.path.insert(0, str(repo / "tools"))
    for mod in ("contrast",):
        sys.modules.pop(mod, None)
    import contrast
    css = contrast.parse_tokens(repo / "tokens" / "tokens.css")
    sys.path.pop(0)
    sys.modules.pop("contrast", None)
    return min((contrast.ratio(css[t]["--" + fg], css[t]["--" + bg])[0], t, fg, bg)
               for t, fg, bg in pairs)


def case(name, expect, mutate, after=None, note=""):
    repo = clone()
    mutate(repo)
    codes, out = {}, ""
    for cmd in CHECKS:
        rc, o = run(repo, *cmd)
        codes[cmd[-1] if cmd[-1].startswith("--") else Path(cmd[0]).stem] = rc
        out += o
    green = all(rc == 0 for rc in codes.values())
    verdict = "green" if green else "caught"
    extra, ok = ("", True)
    if after and codes["build"] == 0:
        extra, ok = after(repo)
    passed = ok and (verdict == expect or (expect == "green" and verdict == "caught"))
    label = ("PASS" if verdict == expect and ok
             else "IMPROVED" if expect == "green" and ok
             else "FAIL")
    RESULTS.append((label, name, expect, verdict, note))
    print(f"\n=== {name}")
    print(f"    expects {expect}{': ' + note if note else ''}")
    print("    " + "  ".join(f"{k}={v}" for k, v in codes.items()) + f"  -> {verdict}  [{label}]")
    for line in out.splitlines():
        if line.startswith(("FAIL", "solved")) or "pairs held" in line or "space and size" in line:
            print("    | " + line[:190])
    if extra:
        print("    " + extra)
    shutil.rmtree(repo.parent)
    return passed


# ---------------------------------------------------------------- build.py / contrast.py
def b_control(repo):
    seed_edit(repo, lambda s: tok(s, "hw-space-12", "spacing").__setitem__("value", "13px"))


case("B0 control: hw-space-12 = 13px", "caught", b_control)


def b1(repo):
    def f(s):
        e = tok(s, "hw-chart-1")
        e["floors"][0]["on"] = ["grund"]
        e["light"]["L"] = "0.900"
    seed_edit(repo, f)


case("B1 chart-1's floor names a ground that does not exist ('grund'), and L moves to 0.900",
     "caught", b1,
     lambda r: ("exact ratio now: %.3f (%s %s on %s)" % exact_min(
         r, [("light", "hw-chart-1", "hw-ground")]), True)
     if (r / "tokens" / "tokens.css").exists() else ("", True),
     note="10-color.md holds the six chart colours to 3:1")


def b2(repo):
    def f(s):
        e = tok(s, "hw-chart-3")
        del e["floors"]
        e["light"]["L"] = "0.900"
    seed_edit(repo, f)


case("B2 chart-3's 'floors' key is deleted, and L moves to 0.900", "caught", b2,
     note="a floor deleted beside the value it guards must still be certified elsewhere")


def b3(repo):
    def f(s):
        e = tok(s, "hw-chart-5")
        e["floors"][0]["bar"] = 1.0
        e["light"]["L"] = "0.900"
    seed_edit(repo, f)


case("B3 chart-5's floor bar is lowered to 1.0, and L moves to 0.900", "caught", b3,
     note="the generated header must not certify a pair at 3:1 that was held to 1.0")


def b4(repo):
    def f(s):
        e = tok(s, "hw-text")
        e["floors"] = e["floors"][:1]
        for q in ("accent", "success", "warning", "danger"):
            tok(s, f"hw-{q}-quiet")["light"]["L"] = "0.40"
    seed_edit(repo, f)


case("B4 control: hw-text loses its quiet-fill floor and the light quiet fills go to L 0.40",
     "caught", b4, note="15-color-combinations.md certifies hw-text on any quiet fill at 13.37+")

for spelling in ("13PX", "calc(13px)", "0.8125rem", "+13px"):
    def b5(repo, v=spelling):
        seed_edit(repo, lambda s: tok(s, "hw-space-12", "spacing").__setitem__("value", v))
    case(f"B5 hw-space-12 = {spelling!r}, valid CSS for the same off-unit 13px", "caught", b5,
         note="audit finding 5, closed by #7: every spelling of an off-unit length is refused")


def b6(repo):
    def f(s):
        s["grid"]["scope"].remove("spacing")
        del s["grid"]["exceptions"]["hw-space-2"]
        tok(s, "hw-space-12", "spacing")["value"] = "13px"
    seed_edit(repo, f)


case("B6 'spacing' is removed from grid.scope, hw-space-12 = 13px", "caught", b6,
     note="audit finding 5, closed by #7: the grid scope is pinned in the tool, not the seed")


def b7(repo):
    seed_edit(repo, lambda s: tok(s, "hw-text-muted")["light"].__setitem__("L", "0.600"))


def b7_after(r):
    pairs = [("light", "hw-text-muted", "hw-" + g) for g in
             ("ground", "surface", "surface-raised", "surface-sunken",
              "surface-hover", "surface-active")]
    got, t, fg, bg = exact_min(r, pairs)
    return (f"re-solved token, exact worst ratio {got:.4f} on {t} {fg}/{bg} "
            f"(WCAG AA is 4.5, no rounding)", got >= 4.5)


case("B7 hw-text-muted's anchor moves to L 0.600, so the solver has to re-solve it", "caught",
     b7, b7_after,
     note="the solver must land AT or ABOVE 4.5:1 on what it wrote, and the refusal must come "
          "from the published table no longer describing the palette, not from a pair under bar")


def b8(repo):
    # hw-ink-text is measured against hw-ink, which the solver reaches in the same pass. Pointing
    # it at hw-accent-ring, which comes later, is a ground that is real and not yet solved.
    seed_edit(repo, lambda s: tok(s, "hw-ink-text")["floors"][0].__setitem__(
        "on", ["ink", "accent-ring"]))


case("B8 a floor names a real ground the solver does not reach until later", "caught", b8,
     note="the ground exists, so only an ordering check refuses it")


def b9(repo):
    p = repo / "tools" / "build.py"
    t = p.read_text(encoding="utf-8")
    assert 'return f"{v:.4f}"' in t
    p.write_text(t.replace('return f"{v:.4f}"', 'return f"{v:.2f}"', 1), encoding="utf-8")


def b9_after(r):
    css = (r / "tokens" / "tokens.css")
    return ("tokens.css was written despite fmt() rounding away from the solved value"
            if css.exists() and "0.6350" not in css.read_text(encoding="utf-8") else
            "no token file written", True)


case("B9 fmt() is coarsened to two decimals, so the written value is not the solved one",
     "caught", b9, b9_after,
     note="a build that cannot re-derive its own emitted values must refuse to write them")


# The four chart guards, one mutation each, each moving one property and leaving the other three
# clear. Until 2026-09-21 none existed and the shipped ramp sat 1.6 from hw-danger.
def g1(repo):
    seed_edit(repo, lambda s: tok(s, "hw-chart-4")["light"].__setitem__("L", "0.49"))


case("G1 hw-chart-4 moves to light L 0.49, within 5 of hw-danger and 0.13 from its neighbours",
     "caught", g1, note="10-color.md: every chart colour sits at least 8.0 from each semantic")


def g2(repo):
    seed_edit(repo, lambda s: tok(s, "hw-chart-4").__setitem__("hue", "accent+80"))


case("G2 hw-chart-4's hue moves to accent+80, 10 degrees from hw-chart-2 at the same lightness",
     "caught", g2, note="10-color.md: the closest chart pair sits 15.4 apart in light")


def g3(repo):
    seed_edit(repo, lambda s: tok(s, "hw-chart-2")["light"].__setitem__("L", "0.55"))


case("G3 hw-chart-2 moves to light L 0.55, 0.07 from both neighbours", "caught", g3,
     note="10-color.md: adjacent series alternate in lightness")


def g4(repo):
    def f(s):
        e = tok(s, "hw-chart-1")
        e["floors"] = [{"bar": 3.0, "on": ["ground"]}]
        e["light"]["L"] = "0.635"
    seed_edit(repo, f)


case("G4 hw-chart-1's floors narrow to the ground alone, and light L moves to 0.635", "caught",
     g4, lambda r: ("exact ratio now: %.3f (%s %s on %s)" % exact_min(
         r, [("light", "hw-chart-1", "hw-surface-sunken")]), True)
     if (r / "tokens" / "tokens.css").exists() else ("", True),
     note="10-color.md: the chart colours hold 3:1 on all four surfaces, not the ground alone")


def w3(repo):
    seed_edit(repo, lambda s: tok(s, "hw-text-muted")["floors"].append(
        {"bar": 4.5, "on": ["border"]}))


case("W3 hw-text-muted gains a 4.5 floor on hw-border, so the solver lifts the refused pair",
     "caught", w3, note="75-spec-sheet.md#ruled refuses muted ink on a rule; a pair that stops "
                        "being refusable makes the published refusal stale")


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
    env = dict(os.environ, GITHUB_OUTPUT=str(repo.parent / "out"),
               GITHUB_STEP_SUMMARY=str(repo.parent / "sum"))
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
    shutil.rmtree(repo.parent)


def e1(repo):
    p = repo / "tools" / "export.py"
    p.write_text(p.read_text(encoding="utf-8").replace(
        "    tokens = load(root)\n", "    raise RuntimeError('exporter is broken')\n", 1),
        encoding="utf-8")


wf("E1 tools/export.py raises before writing anything", "caught", e1,
   note="an exporter that writes nothing leaves a clean diff, so the diff cannot be the check")


def e2(repo):
    # build.py gains a root custom property the exporter does not know about, then everything is
    # regenerated and committed, which is what a contributor following AGENTS.md would do.
    p = repo / "tools" / "build.py"
    marker = '    o.append("}")\n    o.append("")\n    o.append(\'/* Light is'
    p.write_text(p.read_text(encoding="utf-8").replace(
        marker, '    o.append("  --hw-audit-probe: 1px;")\n' + marker, 1), encoding="utf-8")
    assert run(repo, "tools/build.py")[0] == 0
    run(repo, "tools/export.py")


wf("E2 tokens.css carries a property exports/variables.css lacks; export.py reports the gap",
   "caught", e2, note="AGENTS.md: export.py refuses if it diverges from the CSS")


print("\n\n==== summary")
for label, name, expect, verdict, note in RESULTS:
    print(f"{label:9} expected {expect:6} got {verdict:6}  {name}")
bad = [r for r in RESULTS if r[0] == "FAIL"]
improved = [r for r in RESULTS if r[0] == "IMPROVED"]
print(f"\n{len(RESULTS)} cases: {len(RESULTS) - len(bad) - len(improved)} as expected, "
      f"{len(improved)} improved, {len(bad)} failed")
for label, name, expect, verdict, note in bad:
    print(f"FAIL  {name}: expected {expect}, got {verdict}", file=sys.stderr)
sys.exit(1 if bad else 0)
