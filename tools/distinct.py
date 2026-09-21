#!/usr/bin/env python3
"""How far apart two brands paint, pair by pair, read from their emitted token files.

A report, not a gate. It prints, for every pair of files, the CIEDE2000 between the four colours
that carry a brand across a screen - the ground, the accent ink, the selected-row fill and the
focus ring - in each theme on the 8-bit value, and whether the display and text faces differ.
It refuses one case only: two sets whose every one of those colours sits under 2.3, the CIELAB
just-noticeable difference, in both themes, with the same two faces. That pair is one brand
built twice, and nothing a reader sees could tell the products apart but their names.

No score and no bar beyond that, because the one proposed was tested against rendered pixels
and failed both ways: it passed a pair that renders as the house with another serif, and
refused the pair that renders most different (12-brand.md#telling-brands-apart). Whether two
brands read as two is a render looked at, not a number.

    python3 tools/distinct.py tokens/tokens.css examples/*/tokens/tokens.css
"""
import itertools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contrast  # noqa: E402

TERMS = (("ground", "--hw-ground"), ("accent", "--hw-accent"),
         ("fill", "--hw-accent-quiet"), ("ring", "--hw-accent-ring"))
JND = 2.3


def read(path):
    text = Path(path).read_text(encoding="utf-8")
    m = contrast.BRAND_LINE.search(text)
    root = contrast.root_values(path)
    face = {k: re.split(r"\s*,\s*", root[f"--hw-font-{k}"])[0].strip('"')
            for k in ("display", "sans")}
    return (m.group(1).split(",")[0] if m else Path(path).parent.name,
            contrast.parse_tokens(path), face)


def main(argv):
    if len(argv) < 3:
        print("usage: distinct.py FILE FILE [FILE...]", file=sys.stderr)
        return 2
    sets = [read(p) for p in argv[1:]]
    print(f"{'pair':26} " + " ".join(f"{k:>11}" for k, _ in TERMS)
          + "   display  text   (CIEDE2000 light/dark)")
    twins = []
    for (na, ta, fa), (nb, tb, fb) in itertools.combinations(sets, 2):
        d = {k: [contrast.painted(ta[t][tok], tb[t][tok]) for t in ("light", "dark")]
             for k, tok in TERMS}
        same = {k: fa[k] == fb[k] for k in fa}
        print(f"{na + ' / ' + nb:26} "
              + " ".join(f"{v[0]:5.1f}/{v[1]:<5.1f}" for v in d.values())
              + f"   {'same' if same['display'] else 'differ':7} "
              + f"{'same' if same['sans'] else 'differ'}")
        if all(x < JND for v in d.values() for x in v) and all(same.values()):
            twins.append(f"{na} and {nb}: every brand colour under {JND} in both themes and "
                         f"the same faces, which is one brand built twice")
    for t in twins:
        print("FAIL  " + t, file=sys.stderr)
    n = len(sets) * (len(sets) - 1) // 2
    print(f"\n{n} pairs, {len(twins)} indistinguishable")
    return 1 if twins else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
