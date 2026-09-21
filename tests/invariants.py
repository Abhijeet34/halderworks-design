#!/usr/bin/env python3
"""The claims about the instruments themselves, which no run of the instruments can make.

tools/build.py and tools/contrast.py each check the token set. Nothing checked the two tools
against each other, and that is where the 2026-09-21 audit found the system's central claim
failing: build.py imported contrast.py's converter, so "a disagreement one instrument checking
itself can never report" was exactly the disagreement neither could report, and the floors lived
in the same file as the values they guarded, so one edit could move a chart fill to 1.2:1 and
delete the floor that would have caught it.

Six invariants, each failing loudly rather than warning:

  1. The two converters share no code, and neither file imports the other.
  2. They still agree numerically, to a bound stated here rather than assumed.
  3. The seed's floors and tools/contrast.py's REQUIRED set are the same set of pairs.
  4. That set contains, by name, the claims the book makes in prose: six chart fills on the
     ground, the accent as text on all six surfaces, body text on all four quiet fills. Naming
     them in a third place is what stops a weakening that edits both lists at once.
  5. The counts the book prints in three places are the counts tools/build.py computes.
  6. The one environment variable that makes tests/run.py stand down is set by nothing in
     .github/workflows/, so the suite cannot be silenced into a green step.

    python3 tests/invariants.py [repo-root]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build          # noqa: E402
import contrast       # noqa: E402

# The largest disagreement the two converters are allowed on a certified pair. Measured at
# 0.00154 over the 158 pairs of the shipped set on 2026-09-21; 0.01 leaves room for a re-solve
# to move a value without anyone having to re-tune this file, and is still an order below the
# 0.011 that would let a published two-decimal ratio round to the wrong cell.
CONVERTER_BOUND = 0.01


def converters_are_independent(fails):
    """A shared converter is a second opinion from the same head."""
    b = (ROOT / "tools" / "build.py").read_text(encoding="utf-8")
    c = (ROOT / "tools" / "contrast.py").read_text(encoding="utf-8")
    for src, name, other in ((b, "build.py", "contrast"), (c, "contrast.py", "build")):
        if re.search(rf"^\s*(from {other} import|import {other})\b", src, re.M):
            fails.append(f"tools/{name} imports {other}; the two instruments must share no code")
    for fn in ("oklch_to_rgb", "luminance", "ratio_lum", "in_gamut"):
        if getattr(build, fn) is getattr(contrast, fn):
            fails.append(f"build.{fn} and contrast.{fn} are the same object")
    if build.oklch_to_rgb.__code__.co_consts == contrast.oklch_to_rgb.__code__.co_consts:
        fails.append("the two oklch_to_rgb implementations carry identical constants, so they "
                     "are one implementation in two files rather than two implementations")
    print("  independence: neither file imports the other, and 4 converter functions differ")


def converters_agree(css, fails):
    """Independent is only worth having if they still land on the same number."""
    themes = contrast.parse_tokens(css)
    worst, where = 0.0, None
    for bar, fg, bg, _ in contrast.required():
        for t in ("light", "dark"):
            a, b = themes[t][fg], themes[t][bg]
            mine = contrast.ratio(a, b)[0]
            theirs = build.ratio_lum(build.luminance(*a), build.luminance(*b))
            if abs(mine - theirs) > worst:
                worst, where = abs(mine - theirs), f"{t} {fg} on {bg}"
    if worst > CONVERTER_BOUND:
        fails.append(f"the two converters disagree by {worst:.5f} on {where}, past the "
                     f"{CONVERTER_BOUND} this file allows. One of them is wrong")
    print(f"  agreement:    max |contrast - build| = {worst:.5f} over 158 pairs "
          f"(bound {CONVERTER_BOUND}), worst at {where}")


def seed_pairs(seed):
    return {(e["name"], f"hw-{g}", float(floor["bar"]))
            for e in seed["color"]["tokens"]
            for floor in e.get("floors", [])
            for g in floor["on"]}


def certificate_pairs():
    return {(fg[2:], bg[2:], float(bar)) for bar, fg, bg, _ in contrast.required()}


def certificate_agrees(seed, fails):
    """The two declarations of what must hold are deliberately redundant, the way a ledger has
    two sides. Redundancy is only worth its cost while something refuses to let them drift."""
    a, b = seed_pairs(seed), certificate_pairs()
    for fg, bg, bar in sorted(a - b):
        fails.append(f"tokens.seed.json holds {fg} on {bg} at {bar}:1 and tools/contrast.py's "
                     f"REQUIRED does not. A floor the second instrument does not carry is a "
                     f"floor that can be deleted with the value it guards")
    for fg, bg, bar in sorted(b - a):
        fails.append(f"tools/contrast.py certifies {fg} on {bg} at {bar}:1 and the seed carries "
                     f"no such floor, so the build never solves for it")
    print(f"  certificate:  {len(a)} floors in the seed, {len(b)} pairs in contrast.REQUIRED, "
          f"{len(a & b)} in both")


# The claims the book states in prose, named here so that editing the seed and contrast.py
# together still leaves something refusing. Each entry cites the sentence it holds to.
NAMED_CLAIMS = [
    # design/10-color.md: "The six chart colours are fills rather than text, so they are held to
    # the same 3:1"
    *[(f"hw-chart-{n}", "hw-ground", 3.0) for n in range(1, 7)],
    # design/10-color.md's Light and Dark tables carry hw-accent on every surface as text
    *[("hw-accent", s, 4.5) for s in
      ("hw-ground", "hw-surface", "hw-surface-raised", "hw-surface-sunken",
       "hw-surface-hover", "hw-surface-active")],
    # design/15-color-combinations.md: "Exactly two inks may sit on a quiet fill: its own
    # semantic, or hw-text."
    *[("hw-text", f"hw-{q}-quiet", 4.5) for q in ("accent", "success", "warning", "danger")],
    *[(f"hw-{q}", f"hw-{q}-quiet", 4.5) for q in ("accent", "success", "warning", "danger")],
    # design/60-states.md: disabled text is held to the 3:1 non-text bar
    *[("hw-text-disabled", s, 3.0) for s in ("hw-ground", "hw-surface", "hw-surface-sunken")],
]


def named_claims_are_certified(seed, fails):
    cert, floors = certificate_pairs(), seed_pairs(seed)
    found = 0
    for pair in NAMED_CLAIMS:
        if pair not in cert:
            fails.append(f"the book certifies {pair[0]} on {pair[1]} at {pair[2]}:1 and "
                         f"tools/contrast.py does not require it")
        if pair not in floors:
            fails.append(f"the book certifies {pair[0]} on {pair[1]} at {pair[2]}:1 and "
                         f"tokens.seed.json carries no floor for it")
        found += pair in cert and pair in floors
    print(f"  named:        {found} of {len(NAMED_CLAIMS)} claims the book states in prose are "
          f"in both declarations")


COUNTS = {"design/10-color.md": None, "design/90-evidence.md": None,
          "design/00-brand-book.md": None, "tokens/tokens.css": None,
          "tokens/tokens.json": None}


def headline_counts_hold(seed, fails):
    """Three sentences and the generated CSS header state the same two numbers. They said 99 and
    29 while the build computed 104 and 54, and nothing anywhere compared them."""
    resolved = {}
    for theme in build.theme_ids(seed):
        resolved[theme] = build.Solver(seed, seed["seed"]["accentHue"], theme).run()
    stats = build.count_pairs(seed, resolved)
    want = (stats["text_pairs"], stats["nontext_pairs"])
    agreed = 0
    for rel in COUNTS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        t = re.search(r"(\d+) text pairs", text)
        n = re.search(r"(\d+) non-text pairs", text)
        if not (t and n):
            fails.append(f"{rel} no longer states a text-pair and a non-text-pair count")
            continue
        got = (int(t.group(1)), int(n.group(1)))
        agreed += got == want
        if got != want:
            fails.append(f"{rel} says {got[0]} text pairs and {got[1]} non-text pairs; "
                         f"tools/build.py counts {want[0]} and {want[1]}")
    print(f"  counts:       tools/build.py counts {want[0]} text and {want[1]} non-text pairs; "
          f"{agreed} of {len(COUNTS)} files that state them agree")


def the_suite_cannot_be_switched_off(fails):
    """tests/run.py stands down when HW_TESTS_ARE_THE_SUBJECT is set, so that the mutation
    harness can run the CI step body verbatim without re-entering itself. A workflow that set
    it would turn the whole suite into a step that asserts nothing and still reports green."""
    seen = 0
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        seen += 1
        if "HW_TESTS_ARE_THE_SUBJECT" in wf.read_text(encoding="utf-8"):
            fails.append(f".github/workflows/{wf.name} sets HW_TESTS_ARE_THE_SUBJECT, which "
                         f"makes tests/run.py exit 0 without running anything")
    print(f"  kill switch: none of the {seen} workflow files sets HW_TESTS_ARE_THE_SUBJECT")


def main():
    seed = json.loads((ROOT / "tokens" / "tokens.seed.json").read_text(encoding="utf-8"))
    css = ROOT / "tokens" / "tokens.css"
    fails = []
    print("invariants of the two instruments:")
    converters_are_independent(fails)
    converters_agree(css, fails)
    certificate_agrees(seed, fails)
    named_claims_are_certified(seed, fails)
    headline_counts_hold(seed, fails)
    the_suite_cannot_be_switched_off(fails)
    for f in fails:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
