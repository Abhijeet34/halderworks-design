#!/usr/bin/env python3
"""The claims about the instruments themselves, which no run of the instruments can make.

tools/ramps.py writes every colour and tools/contrast.py certifies it. Nothing in either run
checks the two tools against each other, and that is where the 2026-09-21 audit found the
system's central claim failing for the solver they replaced: it imported contrast.py's
converter, so "a disagreement one instrument checking itself can never report" was exactly the
disagreement neither could report.

Four invariants, each failing loudly rather than warning:

  1. The two converters share no code, and neither file imports the other.
  2. They still agree numerically, to a bound stated here rather than assumed, on every step
     floor of every brand the house builds.
  3. The second instrument's CIEDE2000 reproduces the published test pairs.
  4. The separation bars the maintainer decided are the bars tools/contrast.py declares.

    python3 tests/invariants.py [repo-root]
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import contrast       # noqa: E402
import ramps          # noqa: E402

# The largest disagreement the two converters are allowed on a certified pair. The solver's
# converter was measured at 0.00154 against this one over 198 pairs on 2026-09-21; 0.01 leaves
# room for a rebuild to move a value without re-tuning this file, and is still an order below
# the 0.011 that would let a two-decimal ratio round to the wrong cell.
CONVERTER_BOUND = 0.01


def converters_are_independent(fails):
    """A shared converter is a second opinion from the same head."""
    c = (ROOT / "tools" / "contrast.py").read_text(encoding="utf-8")
    r = (ROOT / "tools" / "ramps.py").read_text(encoding="utf-8")
    for src, name, other in ((c, "contrast.py", "ramps"), (r, "ramps.py", "contrast")):
        if re.search(rf"^\s*(from {other} import|import {other})\b", src, re.M):
            fails.append(f"tools/{name} imports {other}; the two instruments must share no code")
    for fn in ("luminance", "in_gamut"):
        if getattr(ramps, fn) is getattr(contrast, fn):
            fails.append(f"ramps.{fn} and contrast.{fn} are the same object")
    if set(ramps.oklch_to_lin.__code__.co_consts) & set(contrast.LMS_TO_XYZ[0]):
        fails.append("ramps.py's converter carries contrast.py's LMS_TO_XYZ constants, so they "
                     "are one implementation in two files rather than two implementations")
    print("  independence: neither instrument imports the other, and their converters share no "
          "constant")


def converters_agree(fails):
    """Independent is only worth having if they still land on the same number."""
    worst, where, n = 0.0, None, 0
    for path in sorted((ROOT / "ramps" / "tokens").glob("*.tokens.css")):
        for theme, rs in ramps.parse(path.read_text(encoding="utf-8")).items():
            for step, (_, span) in ramps.FLOORS.items():
                grounds = [r[i] for r in rs.values() for i in span]
                for r in rs.values():
                    for g in grounds:
                        mine = contrast.ratio(r[step], g)[0]
                        y1, y2 = ramps.luminance(*r[step])[0], ramps.luminance(*g)[0]
                        theirs = (max(y1, y2) + 0.05) / (min(y1, y2) + 0.05)
                        n += 1
                        if abs(mine - theirs) > worst:
                            worst, where = abs(mine - theirs), f"{path.name} {theme} {r[step]}"
    if worst > CONVERTER_BOUND:
        fails.append(f"the two converters disagree by {worst:.5f} on {where}, past the "
                     f"{CONVERTER_BOUND} this file allows. One of them is wrong")
    print(f"  agreement:    max |contrast - ramps| = {worst:.2e} over {n} floored pairs "
          f"(bound {CONVERTER_BOUND}), worst at {where}")


# Sharma, Wu and Dalal 2005, "The CIEDE2000 color-difference formula", Table 1, pairs 1, 7, 9,
# 16, 17 and 25: a blue pair, a near-neutral pair, a pair across the hue wrap, and three others.
SHARMA = [((50, 2.6772, -79.7751), (50, 0, -82.7485), 2.0425),
          ((50, 0, 0), (50, -1, 2), 2.3669),
          ((50, 2.49, -0.001), (50, -2.49, 0.0009), 7.1792),
          ((50, 2.5, 0), (50, 0, -2.5), 4.3065),
          ((50, 2.5, 0), (73, 25, -18), 27.1492),
          ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644)]


def colour_difference_holds(fails):
    for a, b, want in SHARMA:
        for x, y in ((a, b), (b, a)):
            if abs(contrast.de2000(x, y) - want) > 1e-4:
                fails.append(f"contrast.de2000 gives {contrast.de2000(x, y):.4f} for Sharma's "
                             f"{x} / {y}, which the paper gives as {want}")
    print(f"  difference:   contrast.de2000 reproduces {len(SHARMA)} Sharma pairs both ways")


# The separation bars decided on 2026-09-21 (design/10-color.md), and the chart and status-text
# bars of 2026-10-02, named here as a second declaration so lowering contrast.py's copy still fails.
DECIDED = {"FILL_FROM_STATE": 5, "PRIMARY_FROM_DANGER": 14, "RING_FROM_DANGER": 17,
           "RING_FROM_BORDER": 14, "FILL_FROM_GROUND": 6, "CHART_APART": 14,
           "STATE_FROM_TEXT": 14}


def bars_hold(fails):
    for name, want in DECIDED.items():
        if getattr(contrast, name, None) != want:
            fails.append(f"tools/contrast.py holds {name} at {getattr(contrast, name, None)}, and "
                         f"the decided bar is {want}")
    print(f"  bars:         {len(DECIDED)} decided separation bars, as tools/contrast.py "
          f"declares them")


def main():
    fails = []
    print("invariants of the two instruments:")
    converters_are_independent(fails)
    converters_agree(fails)
    colour_difference_holds(fails)
    bars_hold(fails)
    for f in fails:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
