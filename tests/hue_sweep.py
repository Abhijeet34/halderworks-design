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

    python3 tests/hue_sweep.py [repo-root]

It runs in-process rather than through 507 subprocesses, which is what keeps 360 hues inside a
CI step's patience: about 13 seconds against 25.
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


def main():
    seed = json.loads((ROOT / "tokens" / "tokens.seed.json").read_text(encoding="utf-8"))
    floors = [(e["name"], "hw-" + g, floor["bar"])
              for e in seed["color"]["tokens"]
              for floor in e.get("floors", []) for g in floor["on"]]

    tmp = Path(tempfile.mkdtemp(prefix="hw-sweep."))
    refused, built, contrast_fail, under, collisions = collections.Counter(), [], {}, {}, {}
    try:
        for hue in range(360):
            out = tmp / "h"
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = build.main(["--accent-hue", str(hue), "--out", str(out)])
            if rc:
                kinds = {("accent separation" if "hw-accent at hue" in line else
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
            bad = [(round(r, 4), t, fg, bg, bar)
                   for fg, bg, bar in floors for t in ("light", "dark")
                   for r in [contrast.ratio(tokens[t]["--" + fg], tokens[t]["--" + bg])[0]]
                   if r < bar]
            if bad:
                under[hue] = sorted(bad)[:4]
            collide = [f"{t} {f}" for t in ("light", "dark")
                       for f in contrast.separations(tokens[t])[0]]
            if collide:
                collisions[hue] = collide
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"hues 0..359: {sum(refused.values())} refused by build, {len(built)} built")
    for kind, n in refused.most_common():
        print(f"  refused for: {kind}: {n}")
    print(f"built and refused by tools/contrast.py: {len(contrast_fail)} of {len(built)}")
    for hue in sorted(contrast_fail)[:6]:
        print(f"  hue {hue}: {contrast_fail[hue][0][:150]}")
    print(f"built, and carrying a floor under its bar on an exact reading: "
          f"{len(under)} of {len(built)}")
    for hue in sorted(under)[:6]:
        print(f"  hue {hue}: {under[hue][0]}")
    print(f"built, and carrying a chart colour too close to a semantic, to another series, or to "
          f"its neighbour's lightness: {len(collisions)} of {len(built)}")
    for hue in sorted(collisions)[:6]:
        print(f"  hue {hue}: {collisions[hue][0]}")
    documented = 318
    print(f"the worked example AGENTS.md documents, hue {documented}: "
          f"{'built' if documented in built else 'refused by build'}, "
          f"{'refused' if documented in contrast_fail else 'green'} in contrast.py, "
          f"{len(under.get(documented, []))} pairs under bar on an exact reading")

    fails = len(contrast_fail) + len(under) + len(collisions)
    if fails:
        print(f"\nFAIL  {len(contrast_fail)} buildable hue(s) emit a palette the second "
              f"instrument refuses, {len(under)} carry a pair under its bar exactly, and "
              f"{len(collisions)} carry a chart collision", file=sys.stderr)
    print(f"\n{fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
