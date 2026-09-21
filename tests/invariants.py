#!/usr/bin/env python3
"""The claims about the instruments themselves, which no run of the instruments can make.

tools/build.py and tools/contrast.py each check the token set. Nothing checked the two tools
against each other, and that is where the 2026-09-21 audit found the system's central claim
failing: build.py imported contrast.py's converter, so "a disagreement one instrument checking
itself can never report" was exactly the disagreement neither could report, and the floors lived
in the same file as the values they guarded, so one edit could move a chart fill to 1.2:1 and
delete the floor that would have caught it.

Seven invariants, each failing loudly rather than warning:

  1. The two converters share no code, and neither file imports the other.
  2. They still agree numerically, to a bound stated here rather than assumed.
  2a. Their two CIEDE2000 paths reproduce the published test pairs, and on every painted pair
      the house and the example brands certify, the build never reads a pair as further apart
      than the second instrument does, so the build cannot pass what contrast.py refuses.
  3. The seed's floors and tools/contrast.py's REQUIRED set are the same set of pairs.
  4. That set contains, by name, the claims the book makes in prose: six chart fills on the
     ground, the accent as text on all six surfaces, body text on all four quiet fills. Naming
     them in a third place is what stops a weakening that edits both lists at once.
  5. The counts the book prints in three places are the counts tools/build.py computes.
  6. The separation bars the maintainer decided are the bars both instruments declare.

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
# 0.00154 over the 198 pairs of the shipped set on 2026-09-21; 0.01 leaves room for a re-solve
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
    n = 2 * len(list(contrast.required()))
    print(f"  agreement:    max |contrast - build| = {worst:.5f} over {n} pairs "
          f"(bound {CONVERTER_BOUND}), worst at {where}")


# Sharma, Wu and Dalal 2005, "The CIEDE2000 color-difference formula", Table 1, pairs 1, 7, 9,
# 16, 17 and 25: a blue pair, a near-neutral pair, a pair across the hue wrap, and three others.
SHARMA = [((50, 2.6772, -79.7751), (50, 0, -82.7485), 2.0425),
          ((50, 0, 0), (50, -1, 2), 2.3669),
          ((50, 2.49, -0.001), (50, -2.49, 0.0009), 7.1792),
          ((50, 2.5, 0), (50, 0, -2.5), 4.3065),
          ((50, 2.5, 0), (73, 25, -18), 27.1492),
          ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644)]


def colour_difference_agrees(fails):
    for name, fn in (("build.ciede2000", build.ciede2000), ("contrast.de2000", contrast.de2000)):
        for a, b, want in SHARMA:
            if abs(fn(a, b) - want) > 1e-4 or abs(fn(b, a) - want) > 1e-4:
                fails.append(f"{name} gives {fn(a, b):.4f} for Sharma's {a} / {b}, which the "
                             f"paper gives as {want}")
    if build.ciede2000 is contrast.de2000:
        fails.append("build.ciede2000 and contrast.de2000 are the same object")
    files = [ROOT / "tokens" / "tokens.css", *sorted(ROOT.glob("examples/*/tokens/tokens.css"))]
    n, worst = 0, (0.0, None)
    for css in files:
        themes = contrast.parse_tokens(css)
        for t in contrast.BLOCKS_CERTIFIED:
            tok = themes[t]
            pairs = [(ours, f"--hw-{s}{suffix}") for _, ours, suffix, states, _ in
                     contrast.ACCENT_BARS for s in states]
            pairs += [("--hw-accent-ring", "--hw-border-strong")]
            pairs += [(f"--hw-{s}-quiet", "--hw-ground") for s in ("success", "warning", "danger")]
            for a, b in pairs:
                over = build.painted(tok[a], tok[b]) - contrast.painted(tok[a], tok[b])
                n += 1
                if over > worst[0]:
                    worst = (over, f"{css.relative_to(ROOT)} {t} {a} / {b}")
    if worst[0] > 0.01:
        fails.append(f"build.py reads {worst[1]} {worst[0]:.3f} CIEDE2000 further apart than "
                     f"tools/contrast.py does, so the build could pass a pair the second "
                     f"instrument refuses")
    print(f"  difference:   both CIEDE2000 paths reproduce {len(SHARMA)} Sharma pairs; over "
          f"{n} painted pairs in {len(files)} files the build is never more lenient "
          f"(largest excess {worst[0]:.3f})")


# The separation bars decided on 2026-09-21 (design/10-color.md and design/12-brand.md), named
# here as a third declaration so lowering both instruments' copies in one edit still fails.
DECIDED = {"ink": 14, "fill": 5, "ring": 17, "ringFromBorder": 14, "stateFillFromGround": 6,
           "chartSeparation": 8.0, "productSeparation": 8.0}


def bars_hold(seed, fails):
    sd = seed["seed"]
    seed_bars = {**sd["accentSeparation"], **{k: sd[k] for k in (
        "ringFromBorder", "stateFillFromGround", "chartSeparation", "productSeparation")}}
    contrast_bars = {kind: bar for kind, _, _, _, bar in contrast.ACCENT_BARS}
    contrast_bars.update(ringFromBorder=contrast.RING_FROM_BORDER,
                         stateFillFromGround=contrast.FILL_FROM_GROUND,
                         chartSeparation=contrast.CHART_SEPARATION,
                         productSeparation=contrast.PRODUCT_SEPARATION)
    for where, got in (("tokens.seed.json", seed_bars), ("tools/contrast.py", contrast_bars)):
        for k, want in DECIDED.items():
            if got.get(k) != want:
                fails.append(f"{where} holds {k} at {got.get(k)}, and the decided bar is {want}")
    print(f"  bars:         {len(DECIDED)} decided separation bars, the same in the seed and in "
          f"tools/contrast.py")


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
    # design/10-color.md: the chart colours are held to 3:1 on every surface a chart is drawn on
    *[(f"hw-chart-{n}", s, 3.0) for n in range(1, 7)
      for s in ("hw-surface", "hw-surface-raised", "hw-surface-sunken")],
    # design/75-spec-sheet.md#ruled: ink on the ruled ground is certified against its rule
    *[(fg, "hw-border", 4.5) for fg in ("hw-text", "hw-text-secondary")],
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


def main():
    seed = json.loads((ROOT / "tokens" / "tokens.seed.json").read_text(encoding="utf-8"))
    css = ROOT / "tokens" / "tokens.css"
    fails = []
    print("invariants of the two instruments:")
    converters_are_independent(fails)
    converters_agree(css, fails)
    colour_difference_agrees(fails)
    certificate_agrees(seed, fails)
    named_claims_are_certified(seed, fails)
    headline_counts_hold(seed, fails)
    bars_hold(seed, fails)
    for f in fails:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
