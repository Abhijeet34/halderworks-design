#!/usr/bin/env python3
"""Build at every integer accent hue and ask the second instrument about the result.

AGENTS.md: "Taking a different accent hue is a rebuild, never a hand-pick." That makes every
hue tools/build.py accepts a shipping configuration, so every one of them is checked here rather
than the single hue this repository happens to carry. On 2026-09-21 this sweep found that 81 of
the 147 buildable hues emitted a palette tools/contrast.py refused, and that all 66 of the
remainder carried at least one pair below its bar on an exact reading - including hue 318, which
AGENTS.md and design/95-extending.md document as the worked example, at 4.4954:1 on a text pair.

The sweep is the whole point rather than a spot check: a solver that lands on its bar by
construction looks correct at one hue and is wrong at most others, and only a sweep says so.
The chart colours are the sharpest case of it. Their hues rotate with the accent while the three
semantics stay put, so a collision between a series and a state moves around the wheel with
every rebuild; each built hue is therefore also measured for chart separation.

A brand moves more than the hue, so the sweep also builds every fifth hue at four corners of the
two chroma multipliers a brand seed reaches every colour pair through, with the selected-row fill
at its lowest, and every fifth hue as a vivid brand whose key is that hue (12-brand.md#the-inputs),
and asks the second instrument about each of those too.

The hues the house set builds at are recorded below as BUILDABLE, and a change to that arc fails
the sweep: which hues a product may take is a published claim (10-color.md), so a solver change
that opens or closes one has to say so here in the same change.

    python3 tests/hue_sweep.py [repo-root]

It runs in-process rather than through subprocesses, which is what keeps 648 builds inside a CI
step's patience, at about 90 seconds.
"""
import collections
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build          # noqa: E402
import contrast       # noqa: E402


# (accentChroma, neutralChroma). The multipliers have floors and no ceilings since the vivid
# tier, so the high corners are the loudest a shipped identity asks for: accentChroma 2.5 puts the
# accent at C 0.198, the field median round 2 measured across 87 systems, and neutralChroma 6.7 is
# papertrace's cream (12-brand.md#the-inputs). The gamut clips anything past them.
CORNERS = [(ac, nc) for ac in (build.BOUNDS["accentChroma"][0], 2.5)
           for nc in (build.BOUNDS["neutralChroma"][0], 6.7)]
# A vivid brand at every fifth hue: that hue's key at quoth's Field lightness and chroma, as the
# primary, with the neutral selection, the ink ring and the dark card step, on the house accent.
VIVID = {"brandLightness": {"light": 0.8844, "dark": 0.8844}, "brandChroma": 0.1838,
         "primary": "brand", "selection": "neutral", "ring": "ink", "darkCard": "step"}
# The accent hues the house set builds at, as (first, last) runs, recorded 2026-09-28 when the
# vivid tier narrowed the ink bar to the primary fill: 155 hues. Before it, 127 built, at
# 113-115, 187-219 and 265-355.
BUILDABLE = [(100, 124), (184, 219), (265, 358)]


def runs_of(hues):
    """Consecutive integer runs, as (first, last)."""
    out = []
    for h in hues:
        if out and h == out[-1][1] + 1:
            out[-1] = (out[-1][0], h)
        else:
            out.append((h, h))
    return out


def main():
    seed = json.loads((ROOT / "tokens" / "tokens.seed.json").read_text(encoding="utf-8"))
    floors = [(e["name"], "hw-" + g, floor["bar"])
              for e in seed["color"]["tokens"]
              for floor in e.get("floors", []) for g in floor["on"]]

    tmp = Path(tempfile.mkdtemp(prefix="hw-sweep."))
    refused, built, contrast_fail, under, collisions = collections.Counter(), [], {}, {}, {}
    runs = [(str(hue), ["--accent-hue", str(hue)]) for hue in range(360)]
    for ac, nc in CORNERS:
        for hue in range(0, 360, 5):
            seed_file = tmp / f"c{ac}-{nc}-{hue}.json"
            seed_file.write_text(json.dumps({"name": "corner", "accentHue": hue,
                                             "accentChroma": ac, "neutralChroma": nc,
                                             "quietChroma": 0.3}), encoding="utf-8")
            runs.append((f"{hue} at accentChroma {ac}, neutralChroma {nc}",
                         ["--brand", str(seed_file)]))
    for hue in range(0, 360, 5):
        seed_file = tmp / f"v{hue}.json"
        seed_file.write_text(json.dumps({"name": "vivid", "brandHue": hue, **VIVID}),
                             encoding="utf-8")
        runs.append((f"a vivid key at hue {hue}", ["--brand", str(seed_file)]))
    try:
        for hue, args in runs:
            out = tmp / "h"
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = build.main(args + ["--out", str(out)])
            if rc:
                kinds = {("accent separation" if "the-three-bars-the-accent" in line else
                          "ring from border" if "from hw-border-strong in" in line else
                          "state fill from ground" if "from hw-ground in" in line else
                          "chart separation" if "hw-chart" in line else
                          "no lightness clears its floor" if "no lightness" in line else "other")
                         for line in err.getvalue().splitlines() if line.startswith("FAIL")}
                refused[" + ".join(sorted(kinds))] += 1
                continue
            built.append(hue)
            css = out / "tokens.css"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                if contrast.main(["contrast.py", str(css)]):
                    contrast_fail[hue] = [line for line in err.getvalue().splitlines()
                                          if line.startswith("FAIL")][-4:]
            # The same question asked without the tool: every floor, measured directly off the
            # emitted CSS with no tolerance, because a green run of an instrument that rounds is
            # what the old tolerance bought.
            tokens = contrast.parse_tokens(css)
            bad = [(round(r, 4), t, fg, bg, want)
                   for fg, bg, bar in floors for t in contrast.BLOCKS_CERTIFIED
                   for want in [contrast.MORE_BAR.get(bar, bar) if t.endswith("-more") else bar]
                   for r in [contrast.ratio(tokens[t]["--" + fg], tokens[t]["--" + bg])[0]]
                   if r < want]
            if bad:
                under[hue] = sorted(bad)[:4]
            collide = [f"{t} {f}" for t in contrast.BLOCKS_CERTIFIED
                       for f in contrast.separations(tokens[t])[0] + contrast.roles(tokens[t])]
            if collide:
                collisions[hue] = collide
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"hues 0..359, and every fifth hue at {len(CORNERS)} brand corners: "
          f"{sum(refused.values())} refused by build, {len(built)} built")
    for kind, n in refused.most_common():
        print(f"  refused for: {kind}: {n}")
    print(f"built and refused by tools/contrast.py: {len(contrast_fail)} of {len(built)}")
    for hue in list(contrast_fail)[:6]:
        print(f"  hue {hue}: {contrast_fail[hue][0][:150]}")
    print(f"built, and carrying a floor under its bar on an exact reading: "
          f"{len(under)} of {len(built)}")
    for hue in list(under)[:6]:
        print(f"  hue {hue}: {under[hue][0]}")
    print(f"built, and carrying a chart colour too close to a semantic, to another series, or to "
          f"its neighbour's lightness: {len(collisions)} of {len(built)}")
    for hue in list(collisions)[:6]:
        print(f"  hue {hue}: {collisions[hue][0]}")
    house = sorted(int(h) for h in built if h.isdigit())
    arc = [(a, b) for a, b in runs_of(house)]
    print(f"the house set builds at {len(house)} of 360 accent hues: "
          + ", ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in arc))
    vivid = [h for h in built if h.startswith("a vivid key")]
    print(f"a vivid key builds at {len(vivid)} of 72 hues; every one certified above")
    documented = "318"
    print(f"the worked example AGENTS.md documents, hue {documented}: "
          f"{'built' if documented in built else 'refused by build'}, "
          f"{'refused' if documented in contrast_fail else 'green'} in contrast.py, "
          f"{len(under.get(documented, []))} pairs under bar on an exact reading")

    fails = len(contrast_fail) + len(under) + len(collisions)
    if arc != BUILDABLE:
        fails += 1
        print(f"FAIL  the buildable arc is {arc}, and BUILDABLE records {BUILDABLE}. A solver "
              f"change that opens or closes a hue records it here and in 10-color.md",
              file=sys.stderr)
    if fails:
        print(f"\nFAIL  {len(contrast_fail)} buildable hue(s) emit a palette the second "
              f"instrument refuses, {len(under)} carry a pair under its bar exactly, and "
              f"{len(collisions)} carry a chart collision", file=sys.stderr)
    print(f"\n{fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
