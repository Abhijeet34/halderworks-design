#!/usr/bin/env python3
"""Emit tokens/tokens.json and tokens/tokens.css from tokens/tokens.seed.json.

Three files of this book used to name this script as the thing that emits both token files and
refuses to write unless the contrast matrix holds, while it did not exist: it had been written
in a scratch tree that was discarded. A published instruction nobody can run is worse than a
missing feature, so this is that script.

The architecture is a seed and an algorithm, which is the shape Ant Design ships and which
90-evidence.md measures: 47 seed values to 443 derived tokens there, a hue and a set of
lightness anchors to 33 solved colours here. The solver is the half 95-extending.md promises
and could not deliver - a product that wants its own accent hue regenerates, it does not
hand-pick.

    python3 tools/build.py                    # rebuild in place from the seed
    python3 tools/build.py --accent-hue 318   # a different accent, fully re-solved
    python3 tools/build.py --check            # emit nothing; fail if the files are stale
    python3 tools/build.py --brand examples/papertrace/brand.seed.json   # a full brand, solved
    python3 tools/build.py --extend examples/quoth/quoth.seed.json   # a product's own colour, solved

What the build does, in order:

  1. Resolve every token's hue. Neutrals and the accent family follow the accent hue seed,
     because 10-color.md's stated reason for the neutrals carrying a trace of it is that the
     accent should look native to the palette. The six chart hues are the accent plus a fixed
     rotation. The three semantics do not move: a green that means "passed" cannot follow a
     brand decision.
  2. Refuse a hue whose accent ink, selected-row fill or focus ring paints closer than the
     recorded CIEDE2000 bar to a semantic it could be mistaken for. 10-color.md records 14, 5
     and 17 as those three bars ("The three bars the accent is held to"), measured on the 8-bit
     value a display receives. This is that test made executable, which is what 95-extending.md's
     "a product cannot take hue 150" needs to be true rather than merely written. The chart
     colours rotate with the accent and the semantics do not, so they are held to their own
     8.0 oklab bar against each state, to it against each other, and to an alternating
     lightness between neighbours.
  3. Clamp chroma to the in-gamut maximum at each token's lightness and hue. An out-of-gamut
     oklch triple is simply not the colour the token file claims, and 90-evidence.md records a
     warning at chroma 0.12 shipping exactly that way.
  4. Re-solve lightness for any token whose contrast floor no longer holds, by binary search,
     staying as close to the seed anchor as the floor permits. Rotating a hue at fixed
     lightness moves WCAG luminance, so this is not a formality. Every candidate is measured
     in the quantized form fmt() will write, and the target is the bar plus MARGIN rather than
     the bar itself.
  5. Refuse an off-unit space or size value that is not a declared grid exception, and
     refuse a declared exception whose value has since moved back onto the unit. 32-rhythm.md
     is what that check makes checkable.
  6. Solve the whole set again with every 4.5:1 floor raised to 7:1 and every 3:1 floor to
     4.5:1, for @media (prefers-contrast: more), from the per-role targets the seed carries
     where a plain raise would push two roles onto one value.
  7. Re-measure every floor against the formatted strings, immediately before writing them,
     by reading the generated CSS back. A build that cannot re-derive its own output does not
     write it.
  8. Refuse to write anything if a floor, the grid, a separation, a role step or that
     re-measurement still fails.

The principle the whole file is built to: MEASURE THE ARTIFACT, NEVER THE INTENT. Until
2026-09-21 it did the opposite - the solver kept the acceptable lightness nearest the anchor,
which put a re-solved token at bar - 0.005 by construction, fmt() then rounded it to four
decimals, and the rounded value went to disk without being measured again. 81 of the 147 hues
this script agreed to build emitted a palette tools/contrast.py refused.

Why the output is byte-identical to the committed files at the shipped hue: the committed
files are what this script emits from the seed, including the three tokens it re-solves there
because the target is the bar plus MARGIN. That is not a replay - it runs the same code path -
and `--check` reproducing both files byte for byte is the regression that proves the seed and
the shipped files agree.

The seed's contrast floors and this script are one instrument. tools/contrast.py is a second,
and two things make it independent rather than a second reading of this one. It shares no line
of arithmetic: the converter below inverts the original Oklab matrices, while contrast.py uses
the CSS Color 4 reference path. And it declares the pairs it requires in its own file rather
than reading the seed, so a floor cannot be weakened in the same edit as the value it guards.
Neither held until 2026-09-21: this file imported contrast.py's converter, so a conversion error
would have passed both, and the floors lived beside the values, so one seed edit could move a
chart fill to 1.2:1 and delete the floor that would have caught it with every tool still green.
"""
import argparse
import copy
import itertools
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9

# How far above its bar a re-solved pair is placed. Every term it has to cover is measured
# rather than guessed, against the shipped set on 2026-09-21: rounding the emitted lightness to
# four decimals moves a ratio by at most 0.00265, and the largest disagreement between this
# file's converter and tools/contrast.py's reference path over the 198 certified pairs is
# 0.00154. 0.03 is eleven times the first and nineteen times the second. Quantization to 8-bit
# is not in this budget because it is measured directly instead, in meets().
MARGIN = 0.03

# How far past stateFillFromGround a re-solved state fill is placed, in CIEDE2000. The build reads
# every 8-bit rounding and tests/invariants.py holds it to never read a pair more than 0.01 further
# apart than tools/contrast.py does, so 0.2 is twenty times the disagreement it has to cover.
FILL_MARGIN = 0.2

# The lightness a press step moves a vivid fill toward its label: hover one step, pressed two.
PRESS_STEP = 0.03

# The two bars this system recognises: WCAG 2.2 SC 1.4.3 for text and SC 1.4.11 for a control
# boundary. A floor outside this set is a typo or a weakening, and either way it is refused
# rather than silently counted as the lower one.
NON_TEXT_BAR, AA_BAR = 3.0, 4.5

# What a reader who asks for more contrast gets: every text floor raised to the 7:1 of WCAG 2.2
# SC 1.4.6, and every non-text floor to 4.5:1. 1.4.11 has no enhanced level, so the non-text bar
# is raised to the next one this system already recognises rather than to a number invented here.
AAA_BAR = 7.0


def raised(bar):
    return max(bar, AAA_BAR) if bar >= AA_BAR else AA_BAR

# How far inside the sRGB boundary the chroma clamp stops. max_chroma() explains the number.
GAMUT_MARGIN = 0.005


# --- the converter -------------------------------------------------------------------------
# This file owns its arithmetic. It used to import the four functions below from contrast.py,
# so the "second instrument" ran the same code on a different input and a conversion error
# would have passed both. This path inverts the original Oklab matrices; contrast.py uses the
# CSS Color 4 reference path. Two implementations that agree are evidence, one called twice is
# not, and tests/invariants.py measures how far apart they are allowed to be.

M1 = ((0.8189330101, 0.3618667424, -0.1288597137),
      (0.0329845436, 0.9293118715, 0.0361456387),
      (0.0482003018, 0.2643662691, 0.6338517070))
M2 = ((0.2104542553, 0.7936177850, -0.0040720468),
      (1.9779984951, -2.4285922050, 0.4505937099),
      (0.0259040371, 0.7827717662, -0.8086757660))
XYZ_TO_LRGB = ((3.2409699419045226, -1.5373831775700939, -0.4986107602930034),
               (-0.9692436362808796, 1.8759675015077202, 0.0415550574071756),
               (0.0556300796969936, -0.2039769588889765, 1.0569715142428784))


def inv3(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return [[(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]


M1inv, M2inv = inv3(M1), inv3(M2)


def oklch_to_rgb(L, C, h_deg):
    """oklch -> oklab -> LMS' -> LMS -> XYZ(D65) -> sRGB. The XYZ step is not optional:
    omitting it silently returns a plausible-looking colour with the wrong hue."""
    h = math.radians(h_deg)
    lab = (L, C * math.cos(h), C * math.sin(h))
    lms = [sum(M2inv[i][j] * lab[j] for j in range(3)) ** 3 for i in range(3)]
    xyz = [sum(M1inv[i][j] * lms[j] for j in range(3)) for i in range(3)]
    lin = [sum(XYZ_TO_LRGB[i][j] * xyz[j] for j in range(3)) for i in range(3)]
    return [12.92 * u if u <= 0.0031308
            else (1.055 * (abs(u) ** (1 / 2.4)) * (1 if u >= 0 else -1) - 0.055) for u in lin]


def in_gamut(L, C, h, eps=1e-3):
    """eps absorbs a white-point mismatch between the original Oklab M1 and the sRGB matrix:
    pure white, oklch(1 0 198), comes back as 1.000186 through these three matrices, while the
    real out-of-gamut defect 90-evidence.md records, a warning at chroma 0.12, sits at -0.1185
    on blue. 1e-3 is a quarter of a 1/255 channel step and two orders below that defect, so it
    absorbs the former and still fails the latter. contrast.py's reference path returns white
    as exactly 1.0 and needs no such allowance, which is the difference showing its face."""
    return all(-eps <= v <= 1 + eps for v in oklch_to_rgb(L, C, h))


def luminance_rgb(rgb):
    def lin(c):
        c = min(max(c, 0.0), 1.0)
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def luminance(L, C, h):
    return luminance_rgb(oklch_to_rgb(L, C, h))


# How far this file's converter and tools/contrast.py's may put one channel apart. Measured at
# 0.00070 over the 18,560 values the hue sweep emitted on 2026-09-21; 1e-3 is in_gamut's quarter
# step. A channel that close to a rounding boundary is one the other converter may round the
# other way, and at hue 243 that turned 4.504:1 here into 4.497:1 there.
CHANNEL_DISAGREEMENT = 1e-3


def rgb8(L, C, h):
    """Every 8-bit sRGB value a display may receive for this colour. A channel within
    CHANNEL_DISAGREEMENT of a rounding boundary is taken both ways, because the second
    instrument may land on either side of it."""
    options = []
    for v in oklch_to_rgb(L, C, h):
        x = min(max(v, 0.0), 1.0) * 255
        near = abs(x - math.floor(x) - 0.5) < CHANNEL_DISAGREEMENT * 255
        options.append({math.floor(x), math.ceil(x)} if near else {round(x)})
    return list(itertools.product(*options))


def luminance8(L, C, h):
    """(lowest, highest) luminance of the 8-bit sRGB value a display receives, which is what a
    hex-based checker is handed."""
    lums = [luminance_rgb([c / 255 for c in rgb]) for rgb in rgb8(L, C, h)]
    return min(lums), max(lums)


def ratio_lum(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def ratio8(a, b):
    """The worst 8-bit ratio between two luminance8() ranges. A pair that clears its bar on
    floats and reads 2.999 in hex, on either converter, is not certified."""
    return min(ratio_lum(x, y) for x in a for y in b)


# --- painted colour difference ------------------------------------------------------------
# The accent is held apart from the three states by CIEDE2000 on the 8-bit value a display
# receives, measured on each element the accent paints; 10-color.md owns the bars and their
# calibration, in "The three bars the accent is held to". This path is this file's own: linear sRGB to XYZ through the inverse of the
# matrix above, and CIEDE2000 as Sharma, Wu and Dalal 2005 state it. tools/contrast.py carries a
# second implementation, and tests/invariants.py holds both to the published test pairs.

LRGB_TO_XYZ = inv3(XYZ_TO_LRGB)
WHITE = [sum(row) for row in LRGB_TO_XYZ]


def lab_of(rgb, seen=None):
    """CIELAB, D65, of one 8-bit sRGB triple, or of what a dichromat sees of it when `seen` is
    one of DICHROMACY's matrices."""
    lin = [(c / 255) / 12.92 if c / 255 <= 0.04045 else ((c / 255 + 0.055) / 1.055) ** 2.4
           for c in rgb]
    if seen:
        lin = [min(max(sum(seen[i][j] * lin[j] for j in range(3)), 0.0), 1.0) for i in range(3)]
    f = [v ** (1 / 3) if v > (6 / 29) ** 3 else v / (3 * (6 / 29) ** 2) + 4 / 29
         for v in (sum(LRGB_TO_XYZ[i][j] * lin[j] for j in range(3)) / WHITE[i]
                   for i in range(3))]
    return 116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])


def ciede2000(lab1, lab2):
    (L1, a1, b1), (L2, a2, b2) = lab1, lab2
    c7 = ((math.hypot(a1, b1) + math.hypot(a2, b2)) / 2) ** 7
    g = 1.5 - 0.5 * math.sqrt(c7 / (c7 + 25 ** 7))
    c1, c2 = math.hypot(a1 * g, b1), math.hypot(a2 * g, b2)
    h1 = math.degrees(math.atan2(b1, a1 * g)) % 360 if c1 else 0.0
    h2 = math.degrees(math.atan2(b2, a2 * g)) % 360 if c2 else 0.0
    dh = 0.0 if c1 * c2 == 0 else (h2 - h1 + 180) % 360 - 180
    hbar = h1 + h2 if c1 * c2 == 0 else (
        (h1 + h2) / 2 if abs(h1 - h2) <= 180 else (h1 + h2 + (360 if h1 + h2 < 360 else -360)) / 2)
    lbar, cbar = (L1 + L2) / 2 - 50, (c1 + c2) / 2
    cos = [math.cos(math.radians(n * hbar + d)) for n, d in ((1, -30), (2, 0), (3, 6), (4, -63))]
    t = 1 - 0.17 * cos[0] + 0.24 * cos[1] + 0.32 * cos[2] - 0.20 * cos[3]
    dl = (L2 - L1) / (1 + 0.015 * lbar ** 2 / math.sqrt(20 + lbar ** 2))
    dc = (c2 - c1) / (1 + 0.045 * cbar)
    dhh = 2 * math.sqrt(c1 * c2) * math.sin(math.radians(dh / 2)) / (1 + 0.015 * cbar * t)
    rt = (-2 * math.sqrt(cbar ** 7 / (cbar ** 7 + 25 ** 7))
          * math.sin(math.radians(60 * math.exp(-((hbar - 275) / 25) ** 2))))
    return math.sqrt(dl ** 2 + dc ** 2 + dhh ** 2 + rt * dc * dhh)


def painted(a, b):
    """The smallest CIEDE2000 between two oklch colours on any 8-bit value a display may
    receive for each. A pair that clears its bar on one rounding and not the other is not
    certified, for the reason ratio8() gives."""
    return min(ciede2000(lab_of(x), lab_of(y)) for x in rgb8(*a) for y in rgb8(*b))


# Machado, Oliveira and Fernandes 2009 at severity 1.0, applied to linear sRGB. What a dichromat
# sees of a product colour is reported and never refused on, because the house's own states
# collapse under it too and are told apart by their words (10-color.md).
DICHROMACY = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900))}


def dichromat_painted(a, b):
    """(CIEDE2000, kind): the closest two oklch colours come for any of the three dichromacies."""
    return min((ciede2000(lab_of(x, m), lab_of(y, m)), kind) for kind, m in DICHROMACY.items()
               for x in rgb8(*a) for y in rgb8(*b))


# --- colour helpers ------------------------------------------------------------------------

def max_chroma(L, h, hi=0.45):
    """The largest chroma at this lightness and hue that is in gamut by GAMUT_MARGIN, to 1e-4.

    Bisection rather than a formula: the sRGB gamut boundary in OKLCH has no closed form, and
    an analytic approximation that is wrong by a thousandth ships a colour the file does not
    claim - which is the defect this whole step exists to stop.

    The reserve is the price of having two converters rather than one. Measured over 120 hues at
    49 lightnesses, this file's matrices and the CSS Color 4 reference path tools/contrast.py
    uses disagree by up to 0.0036 of a channel near the boundary, and a chroma clamped to this
    file's own edge lands up to 0.0041 outside the gamut the second instrument measures - which
    is how a chart fill at oklch(0.545 0.0937 208) came to sit at red +0.000293 here and
    -0.000312 there. Backing off costs about 1.3 of a 1/255 step of saturation, and only on a
    colour that was pinned to the boundary anyway.
    """
    def inside(C):
        return all(GAMUT_MARGIN <= v <= 1 - GAMUT_MARGIN for v in oklch_to_rgb(L, C, h))

    if not inside(0.0):
        # The grey axis itself is at or past an edge here, so there is no chroma to add. White
        # is the case that reaches this: oklch(1 0 198) is in gamut and has no room beside it.
        return 0.0
    lo = 0.0
    while hi - lo > 1e-4:
        mid = (lo + hi) / 2
        if inside(mid):
            lo = mid
        else:
            hi = mid
    return lo


def oklab(L, C, h):
    r = math.radians(h)
    return (L, C * math.cos(r), C * math.sin(r))


def separation(a, b):
    """Oklab distance times 100, which is the unit 10-color.md's hue table is stated in."""
    x, y = oklab(*a), oklab(*b)
    return 100 * math.sqrt(sum((x[i] - y[i]) ** 2 for i in range(3)))


def fmt(v, like):
    """Keep the seed's own decimal places when the value did not move, so a rebuild at the
    shipped hue reproduces the committed file rather than reformatting every line of it."""
    if abs(v - float(like)) < EPS:
        return like
    return f"{v:.4f}"


GRID = 1e-4  # fmt() writes four decimals, so this is the resolution of the emitted file


def snap(v, up):
    """Round to the grid fmt() writes, in a chosen direction rather than to nearest.

    A solved lightness snaps AWAY from its grounds and a chroma snaps DOWN, so the rounding
    step can only add contrast and can only move further inside the gamut. Rounding to nearest
    is how a value that cleared its bar as a float shipped as a string that does not."""
    n = v / GRID
    return (math.ceil(n - 1e-6) if up else math.floor(n + 1e-6)) * GRID


def written(v, like):
    """The number a browser reads back out of the file, which is the only number worth
    measuring. Every candidate this build considers goes through here first."""
    return float(fmt(v, like))


# --- the seed ------------------------------------------------------------------------------

def load_seed(path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_hue(expr, accent, neutral=None):
    """A token's hue: a number, the accent, the accent plus a rotation, or the neutral hue,
    which is the accent's unless a brand names its own (12-brand.md#neutral-hue)."""
    if expr == "accent":
        return accent % 360
    if expr == "neutral":
        return (accent if neutral is None else neutral) % 360
    if isinstance(expr, str) and expr.startswith("accent+"):
        return (accent + int(expr[len("accent+"):])) % 360
    # Whole degrees, as every hue input is: int() alone would truncate 59.78 to 59 and ship a
    # colour the seed never named.
    if isinstance(expr, float) and not expr.is_integer():
        raise ValueError(f"hue {expr} is not a whole number of degrees")
    return int(expr) % 360


def neutral_hue(seed, accent):
    n = seed["seed"].get("neutralHue", "accent")
    return accent if n == "accent" else n


def theme_ids(seed):
    return [t["id"] for t in seed["themes"]]


# --- the solve -----------------------------------------------------------------------------

def solve_order(tokens):
    """Grounds and fills first, then every floored token, then the roles settled from others: a
    label picks one of two inks and may move its fill, a press follows its fill, and an alias
    copies. Everything else is measured against the first group, so it must exist before."""
    oklch = [e for e in tokens if e["kind"] == "oklch"]

    def settled(e):
        return e.get("role") in ("press", "label", "alias")
    return ([e for e in oklch if not settled(e) and not e.get("floors")]
            + [e for e in oklch if not settled(e) and e.get("floors")]
            + [e for e in oklch if settled(e)])


class UnsolvedGround(Exception):
    """A floor measured against a ground the solver has not produced yet.

    It used to be a `continue`, which took the pair out of the check and out of the count at
    once: a floor whose ground was misspelt disappeared, the build stayed green, and the only
    trace was a number in the generated header falling by two."""


class Solver:
    """Resolves one theme's colour tokens: hue, then chroma clamp, then lightness."""

    def __init__(self, seed, accent, theme, more=False):
        self.seed, self.accent, self.theme, self.more = seed, accent, theme, more
        self.neutral = neutral_hue(seed, accent)
        self.label = f"{theme}, more contrast" if more else theme
        self.solved = {}      # short name -> (L, C, h)
        self.lums = {}        # short name -> (float luminance, 8-bit luminance)
        self.notes = []
        self.failures = []

    def short(self, name):
        return name[len("hw-"):]

    def entries(self):
        return [e for e in self.seed["color"]["tokens"] if e["kind"] == "oklch"]

    def order(self):
        return solve_order(self.entries())

    def anchor(self, entry):
        """A role that the raised bars would push onto its neighbour carries its own target."""
        return entry.get("contrastMore", {}).get(self.theme, entry[self.theme]) if self.more \
            else entry[self.theme]

    def floors(self, entry):
        return [dict(f, bar=raised(f["bar"])) for f in entry.get("floors", [])] if self.more \
            else entry.get("floors")

    def meets(self, L, C, h, floors, margin=0.0):
        """(ok, worst_ratio, worst_ground), on both readings of every pair.

        A pair has to clear its bar plus `margin` on the float value and clear the bar itself on
        the 8-bit value a display receives, because a ratio that is 3.006 in floats and 2.999 in
        hex is not a ratio a third-party checker will agree about."""
        worst, where, ok = None, None, True
        lum, lum8 = luminance(L, C, h), luminance8(L, C, h)
        for floor in floors:
            bar = floor["bar"]
            for g in floor["on"]:
                if g not in self.lums:
                    raise UnsolvedGround(
                        f"floor names --hw-{g}, which is not a solved colour at this point in "
                        f"the {self.label} pass")
                gl, gl8 = self.lums[g]
                r = ratio_lum(lum, gl)
                if worst is None or r < worst:
                    worst, where = r, g
                if r < bar + margin or ratio8(lum8, gl8) < bar:
                    ok = False
        return ok, worst, where

    def ground_pull(self, floors):
        """Mean luminance of the grounds this token is checked against, which decides whether
        solving means darkening or lightening."""
        lums = [self.lums[g][0] for floor in floors for g in floor["on"]]
        return sum(lums) / len(lums) if lums else 0.5

    def candidate(self, L, C0, h, anchor, darken):
        """The (L, C) this lightness becomes in the file. Nothing else is ever measured: the
        solver works on the strings fmt() will write, so the value that clears the bar and the
        value that ships are one number rather than two that round apart."""
        Lq = written(snap(L, up=not darken), anchor["L"])
        return Lq, written(snap(min(C0, max_chroma(Lq, h)), up=False), anchor["C"])

    def solve_one(self, entry):
        h = resolve_hue(entry["hue"], self.accent, self.neutral)
        anchor = self.anchor(entry)
        L0, C0 = float(anchor["L"]), float(anchor["C"])
        C = min(C0, max_chroma(L0, h))
        floors = self.floors(entry)

        if not floors:
            return L0, C, h, (abs(C - C0) > EPS)

        if self.meets(L0, C, h, floors, MARGIN)[0]:
            return L0, C, h, (abs(C - C0) > EPS)

        # Move away from the grounds. Contrast is monotonic in that direction, so the nearest
        # acceptable lightness is a bisection over the side the token is already on. The target
        # is bar + MARGIN rather than the bar: a value solved to land exactly on its bar is a
        # value that rounding, a second converter or an 8-bit display can each take below it.
        darken = luminance(L0, C, h) < self.ground_pull(floors)
        lo, hi = (0.0, L0) if darken else (L0, 1.0)
        best = None
        for _ in range(60):
            mid = (lo + hi) / 2
            Lq, Cq = self.candidate(mid, C0, h, anchor, darken)
            if self.meets(Lq, Cq, h, floors, MARGIN)[0]:
                best = (Lq, Cq)
                # keep searching back toward the anchor
                if darken:
                    lo = mid
                else:
                    hi = mid
            else:
                if darken:
                    hi = mid
                else:
                    lo = mid
        if best is None:
            _, worst, where = self.meets(L0, C, h, floors)
            self.failures.append(
                f"{entry['name']} ({self.label}): no lightness at hue {h} clears its floor with "
                f"{MARGIN} to spare; worst {worst:.3f} on --hw-{where}")
            return L0, C, h, True
        L, C = best
        self.notes.append(
            f"{entry['name']} ({self.label}): re-solved L {L0:.4f} -> {L:.4f}, "
            f"C {C0:.4f} -> {C:.4f} at hue {h}")
        return L, C, h, True

    def put(self, name, value):
        self.solved[self.short(name)] = value
        self.lums[self.short(name)] = (luminance(*value), luminance8(*value))

    def lift_state_fill(self, entry, L, C, h):
        """A state's quiet fill that sits closer than stateFillFromGround to a tinted ground takes
        chroma until it clears, before the separation check refuses it. Lightness stays: the
        fill's own inks are solved against it afterwards, and chroma is what a tinted ground took
        away (12-brand.md#neutral-hue-and-chroma)."""
        bar = self.seed["seed"]["stateFillFromGround"]
        ground = self.solved["ground"]
        if painted((L, C, h), ground) >= bar:
            return C
        anchor = self.anchor(entry)
        top = written(snap(max_chroma(L, h), up=False), anchor["C"])
        if painted((L, top, h), ground) < bar + FILL_MARGIN:
            return C
        lo, hi = C, top
        for _ in range(40):
            mid = min(written(snap((lo + hi) / 2, up=True), anchor["C"]), top)
            if painted((L, mid, h), ground) >= bar + FILL_MARGIN:
                hi = mid
            else:
                lo = mid
        self.notes.append(f"{entry['name']} ({self.label}): chroma {C:.4f} -> {hi:.4f} to clear "
                          f"{bar} from hw-ground")
        return hi

    def solve_label(self, entry):
        """A label on a vivid fill is hw-text or hw-ink-text, whichever clears higher on the fill.
        If neither clears on the fill and each of its press steps, the fill moves away from the
        label, to the nearest lightness where it does: a vivid fill is the brand's to name, a
        label is the reader's to read."""
        fe = next(x for x in self.entries() if x["name"] == entry["of"])
        presses = sorted((x for x in self.entries()
                          if x.get("role") == "press" and x["of"] == entry["of"]),
                         key=lambda x: x["step"])
        anchor = self.anchor(fe)
        L0, _, h = self.solved[self.short(fe["name"])]
        C0 = float(anchor["C"])
        floors = self.floors(entry)
        fill_lum = luminance(*self.solved[self.short(fe["name"])])
        label = max((self.solved["text"], self.solved["ink-text"]),
                    key=lambda v: ratio_lum(luminance(*v), fill_lum))
        toward = 1 if luminance(*label) > fill_lum else -1

        def place(L):
            self.put(fe["name"], (L, written(snap(min(C0, max_chroma(L, h)), up=False),
                                             anchor["C"]), h))
            for p in presses:
                # a press moves toward the label and snaps back away from it, so rounding can
                # only add contrast
                Lp = min(max(L + toward * PRESS_STEP * p["step"], 0.0), 1.0)
                Lp = written(snap(Lp, up=toward < 0), self.anchor(p)["L"])
                self.put(p["name"], (Lp, written(snap(min(C0, max_chroma(Lp, h)), up=False),
                                                 self.anchor(p)["C"]), h))
            return self.meets(*label, floors, MARGIN)[0]

        if not place(L0):
            away = -toward
            lo, hi = (L0, 1.0) if away > 0 else (0.0, L0)
            best = None
            for _ in range(60):
                mid = (lo + hi) / 2
                Lq = written(snap(mid, up=away > 0), anchor["L"])
                if place(Lq):
                    best = Lq
                    lo, hi = (lo, mid) if away > 0 else (mid, hi)
                else:
                    lo, hi = (mid, hi) if away > 0 else (lo, mid)
            if best is None:
                _, worst, where = self.meets(*label, floors)
                self.failures.append(f"{entry['name']} ({self.label}): no lightness of "
                                     f"{fe['name']} at hue {h} lets hw-text or hw-ink-text clear "
                                     f"{floors[0]['bar']}:1; worst {worst:.3f} on --hw-{where}")
                place(L0)
            else:
                place(best)
                self.notes.append(f"{fe['name']} ({self.label}): moved L {L0:.4f} -> {best:.4f} "
                                  f"so its label clears")
        self.put(entry["name"], label)

    def run(self):
        for e in self.order():
            role = e.get("role")
            if role == "press":
                continue  # placed by the label of its fill
            if role == "label":
                self.solve_label(e)
            elif role == "alias":
                self.put(e["name"], self.solved[self.short(e["of"])])
            else:
                L, C, h, _ = self.solve_one(e)
                if e["name"] in STATE_FILLS:
                    C = self.lift_state_fill(e, L, C, h)
                self.put(e["name"], (L, C, h))
        out = {e["name"]: self.solved[self.short(e["name"])] for e in self.entries()}
        for name, (L, C, h) in out.items():
            if not in_gamut(L, C, h):
                self.failures.append(f"{name} ({self.label}): oklch({L} {C} {h}) is outside sRGB")
        return out


PX = re.compile(r"^(-?\d+(?:\.\d+)?)px$")
# The families the unit governs, pinned here rather than read from the seed: a seed that can
# narrow the scope can switch the rule off for whatever it drops, and the rhythm claim is the
# tool's to make.
GRID_SCOPE = ("spacing", "layout", "density", "icon")
# The values in those families that are not px lengths at all, so the unit cannot govern them.
# Named one by one for the same reason, and matched on their spelling as well as their name.
NOT_LENGTHS = {"hw-columns": "a count of columns",
               "hw-measure-ui": "a measure in characters",
               "hw-measure-prose": "a measure in characters"}
NOT_LENGTH = re.compile(r"^\d+(?:\.\d+)?(?:ch)?$")


def check_grid(seed):
    """Every space and size value is on the unit, or is a named exception with a reason.

    Rhythm was the one property this system could nearly prove and did not state. It has a
    spacing scale, a type ramp and a line-height set, and nothing anywhere said how the three
    relate - so "on the grid" was a habit rather than a checkable claim, and six values had
    drifted off it with four of the six unexplained.

    Two directions, because a list of exceptions rots in both: an off-unit value that is not
    declared is a drift, and a declared exception whose value has moved back onto the unit is a
    stale line that makes the next drift look legitimate.
    """
    g = seed.get("grid")
    if not g:
        return ["tokens.seed.json carries no grid block, so no rhythm claim is checkable"]
    unit, declared, bad = g["unit"], dict(g["exceptions"]), []
    if tuple(g["scope"]) != GRID_SCOPE:
        bad.append(f"grid.scope is {list(g['scope'])} and this check governs {list(GRID_SCOPE)}. "
                   f"The scope is the tool's, because a seed that can narrow it can switch the "
                   f"rule off for whatever it drops")
    seen, on_unit = set(), 0
    for fam in GRID_SCOPE:
        for e in seed[fam]["tokens"]:
            raw = e["value"]
            m = PX.match(raw) if isinstance(raw, str) else None
            if not m:
                # Refused rather than skipped. `13PX`, `calc(13px)`, `0.8125rem`, `+13px` and a
                # bare `13` are all the same off-unit length to a browser and none of them is a
                # lowercase Npx, so a check that skips what it cannot parse proves nothing about
                # the values it did not read.
                if e["name"] in NOT_LENGTHS and NOT_LENGTH.match(str(raw)):
                    continue
                bad.append(f"{e['name']} is {raw!r}, which is not a lowercase Npx. Every value "
                           f"in {fam} is a length the {unit}px unit governs, so a spelling this "
                           f"check cannot read is refused: write it as Npx, or name the token in "
                           f"tools/build.py's NOT_LENGTHS with what it is instead")
                continue
            value = float(m.group(1))
            if value % unit == 0:
                on_unit += 1
                if e["name"] in declared:
                    seen.add(e["name"])
                    bad.append(f"{e['name']} is a declared grid exception at {value:g}px, which "
                               f"is on the {unit}px unit. Remove the exception rather than "
                               f"leaving a line that excuses the next drift")
                continue
            seen.add(e["name"])
            if e["name"] not in declared:
                bad.append(f"{e['name']} is {value:g}px, off the {unit}px unit, and is not a "
                           f"declared exception. Put it on the unit or name it in "
                           f"grid.exceptions with the reason it cannot be")
            elif not declared[e["name"]].strip():
                bad.append(f"{e['name']} is a grid exception with no reason given")
    for name in declared:
        if name not in seen:
            bad.append(f"{name} is named in grid.exceptions and is not an off-unit value in "
                       f"scope; the entry names nothing")
    return bad


def grid_stats(seed):
    g = seed["grid"]
    on = off = 0
    for fam in GRID_SCOPE:
        for e in seed[fam]["tokens"]:
            m = PX.match(e["value"]) if isinstance(e["value"], str) else None
            if m:
                if float(m.group(1)) % g["unit"] == 0:
                    on += 1
                else:
                    off += 1
    return on, off


# The one licence a roster face may carry (20-type.md#the-licence-rule): SIL OFL 1.1 is the only
# one checked that lets a sold Mac app, iOS, Windows, a self-hosted site and static art all ship
# the same file, subset and converted. Pinned here for GRID_SCOPE's reason.
FACE_LICENCE = "OFL-1.1"
FACE_FILE_FIELDS = ("source", "licence", "sha256", "xHeight", "licenceText", "licenceSha256",
                    "upstream", "formats")
FACE_FORMATS = ("ttf", "otf", "woff", "woff2")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
STRETCH = re.compile(r"^\d+(?:\.\d+)?%$")


def check_roster(seed):
    """Every roster face is either a self-hosted OFL file pinned by sha256, with its licence
    text, its upstream and the formats that upstream ships, or a system stack that loads
    nothing; and each house type family sets a face the roster carries."""
    faces, bad = seed["brand"]["faces"], []
    for name, f in faces.items():
        if f.get("delivery") == "system":
            extra = [k for k in FACE_FILE_FIELDS if k in f]
            if extra:
                bad.append(f"roster face {name!r} is a system stack and names {extra}; a system "
                           f"face loads no file, so it pins none")
        elif f.get("delivery") != "self-hosted":
            bad.append(f"roster face {name!r} has delivery {f.get('delivery')!r}, not "
                       f"'self-hosted' or 'system'")
        else:
            missing = [k for k in FACE_FILE_FIELDS if k not in f]
            if missing:
                bad.append(f"roster face {name!r} is self-hosted and names no {missing}")
            elif f["licence"] != FACE_LICENCE:
                bad.append(f"roster face {name!r} is licensed {f['licence']!r}; a roster face "
                           f"is {FACE_LICENCE} and nothing else (20-type.md#the-licence-rule)")
            elif not (SHA256.match(str(f["sha256"])) and SHA256.match(str(f["licenceSha256"]))):
                bad.append(f"roster face {name!r} pins a sha256 that is not 64 hex digits")
            elif not re.search(r"\.(ttf|otf)$", f["source"]):
                bad.append(f"roster face {name!r} cites {f['source']}, which is not a TTF or "
                           f"OTF: tools/faces.py reads metrics from an sfnt file only")
            elif not (isinstance(f["formats"], list) and f["formats"]
                      and set(f["formats"]) <= set(FACE_FORMATS)):
                bad.append(f"roster face {name!r} lists formats {f['formats']!r}, not a "
                           f"non-empty list drawn from {', '.join(FACE_FORMATS)}")
        if "stretch" in f and not STRETCH.match(str(f["stretch"])):
            bad.append(f"roster face {name!r} has stretch {f['stretch']!r}, not a percentage")
        if f.get("style", "italic") != "italic":
            bad.append(f"roster face {name!r} has style {f['style']!r}; the one style a roster "
                       f"entry may name is italic")
    for family, stack in seed["type"]["families"].items():
        if not any(f["stack"] == stack for f in faces.values()):
            bad.append(f"the house {family} family sets {stack.split(',')[0]}, which no roster "
                       f"face carries")
    return bad


def face_declarations(face):
    """The CSS a roster entry adds beside its family: a width on a width axis, an italic."""
    return " ".join(f"{prop}: {face[k]};" for k, prop in (("stretch", "font-stretch"),
                                                          ("style", "font-style")) if k in face)


def check_floors(seed):
    """Every floor names a real ground, at a bar this system recognises, in an order the solver
    can actually satisfy.

    None of the three used to be checked. `meets` skipped a ground it had not solved, so a floor
    reading `"on": ["grund"]` removed the pair from the check and from the generated header's
    count in the same edit, and `count_pairs` filed any bar under 4.5 as "held to 3:1" whatever
    it said, so lowering a bar to 1.0 still printed the 3:1 claim.
    """
    names = {e["name"] for e in seed["color"]["tokens"]}
    bad = []
    position = {}
    for i, e in enumerate(solve_order(seed["color"]["tokens"])):
        position[e["name"]] = i
    for e in seed["color"]["tokens"]:
        for floor in e.get("floors", []):
            bar = floor["bar"]
            if bar != NON_TEXT_BAR and bar < AA_BAR:
                bad.append(f"{e['name']} carries a floor at {bar}:1, which is neither the "
                           f"{NON_TEXT_BAR}:1 of WCAG SC 1.4.11 nor at least the {AA_BAR}:1 of "
                           f"SC 1.4.3. A bar between the two certifies nothing this system "
                           f"claims")
            for g in floor["on"]:
                if f"hw-{g}" not in names:
                    bad.append(f"{e['name']} carries a floor on --hw-{g}, which is not a token "
                               f"in this seed. Fix the name or remove the floor; it cannot be "
                               f"skipped")
                elif position.get(f"hw-{g}", -1) >= position.get(e["name"], 0):
                    bad.append(f"{e['name']} is measured against --hw-{g}, which the solver "
                               f"reaches no earlier than {e['name']} itself. Move the ground "
                               f"ahead of it in tokens.seed.json")
    return bad


CHARTS = [f"hw-chart-{n}" for n in range(1, 7)]
STATES = ("success", "warning", "danger")
STATE_FILLS = tuple(f"hw-{s}-quiet" for s in STATES)
# What the brand paints, and the state colours each element must never be mistaken for. Each is
# held to the state drawn in the same form: the primary fill to hw-danger, because a destructive
# confirm is the one state drawn as a filled button; the selected-row fill to every state's quiet
# fill, because it is the one accent element with no second channel; the ring to hw-danger, the
# one state drawn as a border around a control. The accent ink is no longer held to the states:
# every state carries a glyph and a word (15-color-combinations.md), and shipped products run an
# accent 2.5 from their own error red without confusion (10-color.md#the-three-bars).
# Each element is the vivid tier's token where the set declares one, and the house's otherwise.
ACCENT_ELEMENTS = (("primary", ("hw-primary", "hw-ink"), "", ("danger",)),
                   ("fill", ("hw-select", "hw-accent-quiet"), "-quiet", STATES),
                   ("ring", ("hw-accent-ring",), "", ("danger",)))
# The neutrals a selection fill is compared with: one no more chromatic than the most chromatic of
# these is not a hue, so it cannot be read as a state and the fill bar does not apply to it.
NEUTRAL_SURFACES = ("hw-ground", "hw-surface", "hw-surface-raised", "hw-surface-sunken",
                    "hw-surface-hover", "hw-surface-active", "hw-border")


def is_neutral(t, name):
    return t[name][1] <= max(t[n][1] for n in NEUTRAL_SURFACES) + EPS


def check_separation(seed, blocks):
    """The accent's three painted elements stay clear of the states, in CIEDE2000 on 8-bit
    values; the focus ring stays clear of a control's own edge; each state's quiet fill stays
    clear of the ground it sits on; every chart colour stays clear of every semantic and of
    each other; and adjacent series alternate in lightness. Run on the emitted values of every
    certified block, because a re-solve or a chroma clamp moves a colour after its anchor."""
    sd = seed["seed"]
    bars, step = sd["accentSeparation"], sd["minChartNeighbourDeltaL"]
    bad = []
    for block, t in blocks.items():
        for kind, names, suffix, states in ACCENT_ELEMENTS:
            ours = next(n for n in names if n in t)
            if kind == "fill" and ours == "hw-select" and is_neutral(t, ours):
                continue
            for sem in states:
                d = painted(t[ours], t[f"hw-{sem}{suffix}"])
                if d < bars[kind]:
                    bad.append(f"the {kind}, {ours} at hue {t[ours][2]:g}, sits {d:.1f} from "
                               f"hw-{sem}{suffix} in {block}, below the {bars[kind]} CIEDE2000 "
                               f"this system requires "
                               f"(10-color.md#the-three-bars-the-accent-is-held-to)")
        d = painted(t["hw-accent-ring"], t["hw-border-strong"])
        if d < sd["ringFromBorder"]:
            bad.append(f"hw-accent-ring sits {d:.1f} from hw-border-strong in {block}, below the "
                       f"{sd['ringFromBorder']} that tells a focused control from its own edge "
                       f"(12-brand.md#the-focus-ring)")
        for sem in STATES:
            d = painted(t[f"hw-{sem}-quiet"], t["hw-ground"])
            if d < sd["stateFillFromGround"]:
                bad.append(f"hw-{sem}-quiet sits {d:.1f} from hw-ground in {block}, below the "
                           f"{sd['stateFillFromGround']} that keeps a status fill off the ground "
                           f"(12-brand.md#neutral-hue-and-chroma)")
        bar = sd["chartSeparation"]
        for name in CHARTS:
            for sem in STATES:
                d = separation(t[name], t[f"hw-{sem}"])
                if d < bar:
                    bad.append(f"{name} at hue {t[name][2]:g} sits {d:.1f} from hw-{sem} in "
                               f"{block}, below the {bar} this system requires "
                               f"(10-color.md#the-contrast-matrix)")
        for i, a in enumerate(CHARTS):
            for b in CHARTS[i + 1:]:
                d = separation(t[a], t[b])
                if d < bar:
                    bad.append(f"{a} sits {d:.1f} from {b} in {block}, below {bar}")
            if i + 1 < len(CHARTS):
                dl = abs(t[a][0] - t[CHARTS[i + 1]][0])
                if dl < step:
                    bad.append(f"{a} and {CHARTS[i + 1]} differ by {dl:.3f} in lightness in "
                               f"{block}, below the {step} adjacent series keep")
    return bad


def check_roles(seed, blocks):
    """Each step of a role ladder stays a visible step in every block.

    The solver keeps the acceptable lightness nearest a token's anchor, so two roles pushed
    toward one bar land on one value: raising the floors to 7:1 put hw-text-secondary and
    hw-text-muted both at L 0.4355. A ladder whose rungs coincide is one role under two names."""
    ladder, step = seed["seed"]["roleLadder"], seed["seed"]["minRoleStep"]
    bad = []
    for block, t in blocks.items():
        for a, b in zip(ladder, ladder[1:]):
            d = abs(t[a][0] - t[b][0])
            if d < step:
                bad.append(f"{a} and {b} are {d:.4f} apart in lightness in {block}, below the "
                           f"{step} that keeps them two roles")
    return bad


# --- emitters ------------------------------------------------------------------------------

def more_key(theme):
    return f"{theme}-more"


def anchor_of(entry, block):
    """The seed anchor a block's value was solved from, whose decimals fmt() keeps."""
    if block.endswith("-more"):
        theme = block[:-len("-more")]
        return entry.get("contrastMore", {}).get(theme, entry[theme])
    return entry[block]


def value_string(L, C, h, entry, block):
    anchor = anchor_of(entry, block)
    return f"oklch({fmt(L, anchor['L'])} {fmt(C, anchor['C'])} {h})"


def build_tokens_json(seed, resolved):
    """tokens.json is the seed with colour resolved and the build's own inputs dropped: it is
    what every other tool reads, and a consumer has no use for a contrast floor."""
    ids = theme_ids(seed)
    doc = {"name": seed["name"], "version": seed["version"]}
    colours = []
    for e in seed["color"]["tokens"]:
        if e["kind"] == "literal":
            value = e["value"]
        else:
            value = {t: value_string(*resolved[t][e["name"]][:3], e, t) for t in ids}
        entry = {"name": e["name"], "value": value, "usage": e["usage"],
                 "state": e["state"], "introduced": e["introduced"]}
        if "notFor" in e:
            entry["notFor"] = e["notFor"]
        colours.append(entry)
    doc["color"] = {"themes": seed["themes"], "note": seed["color"]["note"], "tokens": colours}
    for fam in ("type", "spacing", "radius", "shadow", "duration", "easing",
                "layout", "density", "icon", "zIndex", "stroke"):
        doc[fam] = seed[fam]
    return json.dumps(doc, indent=2) + "\n"


SCALAR_FAMILIES = ["spacing", "radius"]
THEMED_FAMILIES = ["shadow"]
LAYOUT_FAMILIES = ["layout", "density", "icon", "zIndex", "stroke"]

CSS_TAIL = '''
/* Touch. On a coarse pointer the control IS the target, so --hw-control-h rebinds to the 44px
   pointer floor. This composes with density: a compact list keeps 32px rows for reading while
   its controls stay hittable, because a row is scanned and a control is hit. */
@media (pointer: coarse) {
  :root { --hw-control-h: var(--hw-row-h); }
}

/* Compact density. One attribute, and it moves vertical rhythm and control height only:
   type size, colour, alignment and horizontal padding are identical in both settings, so a
   column of numbers still lines up against the same column in the other density. */
[data-density="compact"] {
  --hw-control-h: var(--hw-control-h-sm);
  --hw-row-h: var(--hw-row-h-compact);
  --hw-cell-pad-y: var(--hw-cell-pad-y-compact);
  --hw-field-pad-y: var(--hw-field-pad-y-compact);
}

/* Type styles as classes, so a screen names a step rather than restating four properties. */
'''

CSS_MOTION = '''
/* Reduced motion removes movement, not feedback. Collapsing every transition to none makes a
   state change read as a broken control; only the movement is the accommodation. */
@media (prefers-reduced-motion: reduce) {
  :root {
    --hw-duration-instant: 1ms;
    --hw-duration-fast: 100ms;
    --hw-duration-base: 100ms;
    --hw-duration-slow: 100ms;
  }
  *, *::before, *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    transition-property: opacity, color, background-color, border-color, outline-color !important;
    scroll-behavior: auto !important;
  }
}
'''


def build_tokens_css(seed, resolved, accent, stats, brand="house"):
    """`brand` names the set in the header, which is how tools/contrast.py tells the house file,
    whose ratios the book publishes, from a brand's or a rebuild's, whose ratios it does not."""
    ids = theme_ids(seed)
    n_text = stats["text_pairs"]
    n_nontext = stats["nontext_pairs"]
    step = seed["seed"].get("cardStep")
    card_line = "" if step is None else (
        f"\n\n   Dark cards: stepped, --hw-surface {step}:1 over --hw-ground and --hw-border"
        f"\n   {step}:1 over --hw-surface in dark, with no shadow.")
    o = []
    o.append(f"""/* {seed['name']} - token definitions.
   Brand: {brand}.
   Generated from tokens/tokens.seed.json by tools/build.py, which solves every colour against
   its contrast floor in the same run and refuses to emit if one does not hold.
   Do not hand-edit this file or tokens/tokens.json; edit the seed and rebuild.

   {n_text} text pairs, both themes, 0 below WCAG AA 4.5:1.
   {n_nontext} non-text pairs (control boundary, focus ring, chart fills, disabled) held to
   3:1, 0 below it. Every one re-measured on these strings, on the float value and on the
   8-bit value a display receives, after they were formatted and before they were written.
   {len(seed['color']['tokens'])} colour tokens, {len(resolved[ids[0]])} of them solved in oklch, 0 outside sRGB.
   Accent hue {accent % 360}.

   Under @media (prefers-contrast: more) the same pairs are solved again from the same seed:
   {n_text} text pairs held to WCAG AAA 7:1 and {n_nontext} non-text pairs to 4.5:1, 0 below
   either, measured the same two ways.{card_line} */
""")
    o.append(":root {")
    for fam in SCALAR_FAMILIES:
        for e in seed[fam]["tokens"]:
            o.append(f"  --{e['name']}: {e['value']};")
    for key, stack in seed["type"]["families"].items():
        o.append(f"  --hw-font-{key}: {stack};")
    for fam in ("duration", "easing"):
        for e in seed[fam]["tokens"]:
            o.append(f"  --{e['name']}: {e['value']};")
    for g in seed["type"]["groups"]:
        for s in g["styles"]:
            o.append(f"  --hw-text-{s['name']}: {s['fontSize']};")
            o.append(f"  --hw-leading-{s['name']}: {s['lineHeight']};")
            o.append(f"  --hw-tracking-{s['name']}: {s.get('letterSpacing', '0')};")
            o.append(f"  --hw-weight-{s['name']}: {s['fontWeight']};")
    o.append("")
    o.append("  /* Layout, density, icon, layering and line weight: everything that makes the")
    o.append("     system able to lay out a page rather than only paint one. */")
    for fam in LAYOUT_FAMILIES:
        for e in seed[fam]["tokens"]:
            o.append(f"  --{e['name']}: {e['value']};")
    o.append("}")
    o.append("")
    o.append('/* Light is the default. Dark applies on an explicit [data-theme="dark"], and on the media')
    o.append("   query when the page has made no explicit choice. Both are written out rather than derived")
    o.append("   so a token can be read without running a calculation. */")

    def colour_block(theme, indent="  "):
        """Everything whose value depends on the theme. Colour is most of it; the two shadow
        tokens are the rest, and they ship dark values that three prose files used to say did
        not exist. Emitting them from the same place is what stops that recurring."""
        lines = []
        for e in seed["color"]["tokens"]:
            if e["kind"] == "literal":
                v = e["value"][theme] if isinstance(e["value"], dict) else e["value"]
            else:
                v = value_string(*resolved[theme][e["name"]][:3], e, theme)
            lines.append(f"{indent}--{e['name']}: {v};")
        for fam in THEMED_FAMILIES:
            for e in seed[fam]["tokens"]:
                v = e["value"][theme] if isinstance(e["value"], dict) else e["value"]
                lines.append(f"{indent}--{e['name']}: {v};")
        return lines

    o.append(':root, [data-theme="light"] {')
    o += colour_block(ids[0])
    o.append("}")
    for theme in ids[1:]:
        o.append("")
        o.append(f'[data-theme="{theme}"] {{')
        o += colour_block(theme)
        o.append("}")
    o.append("")
    o.append("@media (prefers-color-scheme: dark) {")
    o.append('  :root:not([data-theme="light"]) {')
    o += colour_block(ids[-1], indent="    ")
    o.append("  }")
    o.append("}")
    o.append("")
    o.append("/* More contrast, for a reader who has asked for it: every oklch colour re-solved")
    o.append("   with each 4.5:1 floor raised to 7:1 and each 3:1 floor to 4.5:1. Literal colours")
    o.append("   and shadows do not move, so they are not repeated here. */")

    def more_block(theme, indent):
        return [f"{indent}--{e['name']}: "
                f"{value_string(*resolved[more_key(theme)][e['name']][:3], e, more_key(theme))};"
                for e in seed["color"]["tokens"] if e["kind"] == "oklch"]

    o.append("@media (prefers-contrast: more) {")
    o.append('  :root, [data-theme="light"] {')
    o += more_block(ids[0], "    ")
    o.append("  }")
    for theme in ids[1:]:
        o.append(f'  [data-theme="{theme}"] {{')
        o += more_block(theme, "    ")
        o.append("  }")
    o.append("}")
    o.append("")
    o.append("@media (prefers-contrast: more) and (prefers-color-scheme: dark) {")
    o.append('  :root:not([data-theme="light"]) {')
    o += more_block(ids[-1], "    ")
    o.append("  }")
    o.append("}")
    o.append(CSS_TAIL.rstrip("\n"))
    face = seed["type"].get("faceDeclarations", {})
    for g in seed["type"]["groups"]:
        for s in g["styles"]:
            n, fam = s["name"], s["family"]
            o.append(f".hw-{n} {{ font-family: var(--hw-font-{fam}); "
                     f"font-size: var(--hw-text-{n});")
            o.append(f"  line-height: var(--hw-leading-{n}); "
                     f"letter-spacing: var(--hw-tracking-{n});")
            adjust = seed["type"].get("sansSizeAdjust") if fam == "sans" else None
            o.append(f"  font-weight: var(--hw-weight-{n});"
                     + (f" {face[fam]}" if fam in face else "")
                     + (f" font-size-adjust: {adjust};" if adjust else "") + " }")
    if "quote" in seed["type"]["families"]:
        o.append("/* The quote face sets the words a person said or wrote, inside a step class,")
        o.append("   at the house x-height so it sits on the line beside the text face. */")
        o.append(".hw-quote { font-family: var(--hw-font-quote);"
                 + (f" {face['quote']}" if "quote" in face else "")
                 + f" font-size-adjust: {seed['type']['quoteSizeAdjust']}; }}")
    o.append(CSS_MOTION.rstrip("\n"))
    return "\n".join(o) + "\n"


# --- the matrix report ---------------------------------------------------------------------

def count_pairs(seed, resolved):
    """Every pair the seed asserts, counted by bar, so the header states what was verified
    rather than a number somebody typed.

    check_floors has already refused any bar that is neither of the two, so the split here is
    total rather than a fallback: nothing lands in the 3:1 column because it failed to be 4.5."""
    text = nontext = 0
    for theme in theme_ids(seed):
        solved = {n[len("hw-"):] for n in resolved[theme]}
        for e in seed["color"]["tokens"]:
            for floor in e.get("floors", []):
                n = sum(1 for g in floor["on"] if g in solved)
                if floor["bar"] >= AA_BAR:
                    text += n
                elif floor["bar"] == NON_TEXT_BAR:
                    nontext += n
                else:
                    raise ValueError(f"{e['name']}: bar {floor['bar']} reached count_pairs; "
                                     f"check_floors should have refused it")
    return {"text_pairs": text, "nontext_pairs": nontext}


CSS_TOKEN = re.compile(r"^\s*--([a-z][a-z0-9]*-[a-z0-9-]+):\s*oklch\(([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\)\s*;")


MORE = "@media (prefers-contrast: more)"
EMITTED_BLOCKS = {
    (None, ':root, [data-theme="light"]'): "light",
    (None, '[data-theme="dark"]'): "dark",
    ("@media (prefers-color-scheme: dark)", ':root:not([data-theme="light"])'): "media-dark",
    (MORE, ':root, [data-theme="light"]'): "light-more",
    (MORE, '[data-theme="dark"]'): "dark-more",
    (MORE + " and (prefers-color-scheme: dark)", ':root:not([data-theme="light"])'):
        "media-dark-more",
}


def parse_emitted(css):
    """Read the colour blocks back out of the CSS text this build is about to write.

    Deliberately a second reader rather than a record of what the solver decided: it is the only
    way a value written into the wrong theme block, a token dropped by an emitter change, or a
    dark block that has drifted from its media-query copy becomes visible."""
    blocks = {name: {} for name in EMITTED_BLOCKS.values()}
    cur, media = None, None
    for line in css.splitlines():
        s = line.strip()
        if s.startswith("@media"):
            media = s[:-1].strip()
            continue
        if s.endswith("{"):
            cur = EMITTED_BLOCKS.get((media, s[:-1].strip()))
            continue
        if s.startswith("}"):
            if cur is None:
                media = None
            cur = None
            continue
        m = CSS_TOKEN.match(line)
        if m and cur:
            blocks[cur][m.group(1)] = tuple(float(m.group(i)) for i in (2, 3, 4))
    return blocks


def verify_emitted(css, seed):
    """Re-measure every floor against the strings this build is about to write.

    This is the step whose absence made everything else provisional: the solver worked in
    floats, fmt() rounded them to four decimals, and the rounded value reached disk without ever
    being measured again, so a pair could be certified at 3.0001 and ship at 2.9994. Here the
    bar is the published one with no margin and no tolerance, on the float value and on the
    8-bit value a display receives, and a build that cannot re-derive its own output refuses to
    write it.
    """
    blocks = parse_emitted(css)
    names = certified_blocks(seed)
    bad = check_separation(seed, {b: blocks[b] for b in names})
    bad += check_roles(seed, {b: blocks[b] for b in names})
    bad += check_card_step(seed, blocks)
    for block in names:
        for e in seed["color"]["tokens"]:
            bad += floor_failures(e, block, blocks[block], blocks[block])
    return bad + media_copies_differ(seed, blocks)


def check_card_step(seed, blocks):
    """darkCard: step, re-measured on the CSS about to be written, both dark blocks."""
    step = seed["seed"].get("cardStep")
    bad = []
    for block in ([] if step is None else [b for b in certified_blocks(seed) if "dark" in b]):
        t = blocks[block]
        for fg, bg in (("hw-surface", "hw-ground"), ("hw-border", "hw-surface")):
            r = ratio_lum(luminance(*t[fg]), luminance(*t[bg]))
            r8 = ratio8(luminance8(*t[fg]), luminance8(*t[bg]))
            if r < step or r8 < step:
                bad.append(f"{fg} sits {r:.3f}:1 ({r8:.3f} at 8-bit) over {bg} in {block}, below "
                           f"the {step}:1 dark card step (12-brand.md#the-dark-card-step)")
    return bad


def certified_blocks(seed):
    return [b for t in theme_ids(seed) for b in (t, more_key(t))]


def floor_failures(e, block, fgs, grounds):
    """Every floor of one token, measured on the parsed CSS at the published bar, no margin."""
    bad = []
    for floor in e.get("floors", []):
        bar = raised(floor["bar"]) if block.endswith("-more") else floor["bar"]
        for g in floor["on"]:
            fg, bg = fgs.get(e["name"]), grounds.get(f"hw-{g}")
            if fg is None or bg is None:
                bad.append(f"{e['name']} on --hw-{g} ({block}): the emitted CSS does "
                           f"not declare both tokens in that block")
                continue
            r = ratio_lum(luminance(*fg), luminance(*bg))
            r8 = ratio8(luminance8(*fg), luminance8(*bg))
            if r < bar or r8 < bar:
                bad.append(f"{e['name']} on --hw-{g} ({block}): the value about to be "
                           f"written measures {r:.3f} ({r8:.3f} at 8-bit), below its "
                           f"{bar}:1 floor")
    return bad


def media_copies_differ(seed, blocks):
    last = theme_ids(seed)[-1]
    return [f"the {media} block about to be written differs from {block}"
            for media, block in (("media-dark", last), ("media-dark-more", more_key(last)))
            if blocks[media] != blocks[block]]


# --- a product's own colour ---------------------------------------------------------------
# A product declares a colour the house has no opinion about in a seed of its own, and this
# build solves it against the house set rather than letting the product hand-pick it.
# 95-extending.md#a-colour-of-the-products-own owns the rule; the numbers below are the house's,
# and a product seed can add to them but has no field that lowers them.

# The six surfaces a mark can land on. A product colour is drawn on a house surface, and nothing
# stops a component putting it on any of them, so every one carries a floor.
PRODUCT_SURFACES = ("ground", "surface", "surface-raised", "surface-sunken", "surface-hover",
                    "surface-active")
# The colours a product colour must never be mistaken for: the three states and the accent,
# which is selection and focus. A seed may name more; it cannot name fewer. The states are held
# to both of the seed's product bars, everything else to the hue-and-chroma guard alone.
PRODUCT_APART = ("hw-success", "hw-warning", "hw-danger", "hw-accent")
PRODUCT_STATES = PRODUCT_APART[:3]
NAMESPACE = re.compile(r"^[a-z][a-z0-9]*$")


def hue_chroma_separation(a, b):
    """Oklab distance times 100 with lightness left out: the guard that keeps a state shifted in
    lightness, a maroon or a salmon at hue 27, refused after it has cleared CIEDE2000 on
    lightness alone."""
    x, y = oklab(*a), oklab(*b)
    return 100 * math.hypot(x[1] - y[1], x[2] - y[2])


def finite_number(x):
    """x as a float if it is one, or parses cleanly to one, and is neither infinite nor NaN.
    None otherwise. A bool is never a number here: True is not 1 in a colour anchor."""
    if isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def anchor_leaf_errors(name, label, anchor):
    """A theme anchor is an object with an L in 0..1 and a C at least 0, each a finite number
    or a numeric string, the way the seed writes them today."""
    if not isinstance(anchor, dict):
        return [f"{name} has {label} anchor {anchor!r}, which is not an object"]
    bad = []
    L = finite_number(anchor.get("L"))
    if L is None:
        bad.append(f"{name} has {label} anchor L {anchor.get('L')!r}, which is not a finite "
                   f"number")
    elif not 0.0 <= L <= 1.0:
        bad.append(f"{name} has {label} anchor L {L!r}, which is not between 0 and 1")
    C = finite_number(anchor.get("C"))
    if C is None:
        bad.append(f"{name} has {label} anchor C {anchor.get('C')!r}, which is not a finite "
                   f"number")
    elif C < 0.0:
        bad.append(f"{name} has {label} anchor C {C!r}, which is negative")
    return bad


def hue_expr_ok(hue):
    try:
        resolve_hue(hue, 0)
    except (TypeError, ValueError, OverflowError):
        return False
    return True


def extension_shape(seed, ext):
    """Every way a product seed's raw JSON cannot be trusted, checked once at the boundary so
    the solving code after it can index the seed freely."""
    if not isinstance(ext, dict):
        return [f"the product seed is {ext!r}, not a JSON object"]
    bad = []
    if not isinstance(ext.get("namespace"), str):
        bad.append(f"namespace {ext.get('namespace')!r} is not a string")
    color = ext.get("color")
    if not isinstance(color, dict):
        bad.append(f"color {color!r} is not an object")
        return bad
    tokens = color.get("tokens")
    if not isinstance(tokens, list) or not tokens:
        bad.append(f"color.tokens {tokens!r} is not a non-empty list of colour token entries")
        return bad
    for e in tokens:
        if not isinstance(e, dict) or not isinstance(e.get("name"), str):
            bad.append(f"a colour token entry {e!r} is not an object with a string name")
            continue
        name = e["name"]
        if not hue_expr_ok(e.get("hue")):
            bad.append(f"{name} has hue {e.get('hue')!r}, which is neither a whole number of "
                       f"degrees nor accent+N")
        for t in theme_ids(seed):
            bad += anchor_leaf_errors(name, t, e.get(t, {}))
        more = e.get("contrastMore", {})
        if not isinstance(more, dict):
            bad.append(f"{name} has contrastMore {more!r}, which is not an object")
        else:
            for t in theme_ids(seed):
                if t in more:
                    bad += anchor_leaf_errors(name, f"contrastMore.{t}", more[t])
        floors = e.get("floors", [])
        if not isinstance(floors, list):
            bad.append(f"{name} has floors {floors!r}, which is not a list")
        else:
            for floor in floors:
                if not isinstance(floor, dict):
                    bad.append(f"{name} carries a floor {floor!r} that is not an object")
                    continue
                bar = floor.get("bar")
                if not (isinstance(bar, (int, float)) and not isinstance(bar, bool)
                        and math.isfinite(bar)):
                    bad.append(f"{name} carries a floor with bar {bar!r}, which is not a "
                               f"finite number")
                on = floor.get("on", [])
                if not (isinstance(on, list) and all(isinstance(g, str) for g in on)):
                    bad.append(f"{name} carries a floor on {on!r}, which is not a list of "
                               f"house colour names")
        apart = e.get("apart", [])
        if not (isinstance(apart, list) and all(isinstance(a, str) for a in apart)):
            bad.append(f"{name} has apart {apart!r}, which is not a list of house colour "
                       f"names")
    return bad


def check_extension(seed, ext):
    """Refuse a product seed before anything is solved from it."""
    shape = extension_shape(seed, ext)
    if shape:
        return shape
    ns = ext["namespace"]
    if not NAMESPACE.match(ns) or ns == "hw":
        return [f"namespace {ns!r} is not a product's own prefix. It is one lowercase word, "
                f"the product's name, and never hw"]
    house = {e["name"]: e for e in seed["color"]["tokens"]}
    solved = {n for n, e in house.items() if e["kind"] == "oklch"}
    bad = []
    for e in ext["color"]["tokens"]:
        name = e["name"]
        if name.startswith("hw-") or name in house:
            bad.append(f"{name} is a house token, and a product can never redefine an hw- token "
                       f"(95-extending.md#a-products-own-namespace). Name it --{ns}-something")
            continue
        if not name.startswith(f"{ns}-"):
            bad.append(f"{name} is outside the {ns}- namespace this seed declares")
        if e.get("kind") != "oklch":
            bad.append(f"{name} is kind {e.get('kind')!r}; only an oklch colour is solved")
        grounds = set()
        for floor in e.get("floors", []):
            if floor["bar"] != NON_TEXT_BAR and floor["bar"] < AA_BAR:
                bad.append(f"{name} carries a floor at {floor['bar']}:1, which is neither the "
                           f"{NON_TEXT_BAR}:1 of WCAG SC 1.4.11 nor at least the {AA_BAR}:1 of "
                           f"SC 1.4.3")
                continue
            for g in floor["on"]:
                if f"hw-{g}" not in solved:
                    bad.append(f"{name} carries a floor on --hw-{g}, which is not a solved house "
                               f"colour")
            grounds |= set(floor["on"])
        missing = [g for g in PRODUCT_SURFACES if g not in grounds]
        if missing:
            bad.append(f"{name} carries no floor on --hw-{', --hw-'.join(missing)}. A product "
                       f"colour can land on any of the six surfaces, so it holds at least "
                       f"{NON_TEXT_BAR}:1 on every one")
        apart = e.get("apart", [])
        bad += [f"{name} is held apart from {a}, which is not a solved house colour"
                for a in apart if a not in solved]
        bad += [f"{name} is not held apart from {a}. Every product colour stays clear of the "
                f"three states and the accent, so a seed can name more of them but never fewer"
                for a in PRODUCT_APART if a not in apart]
    return bad


def build_extension_css(seed, ext, solved, accent, source, brand="house"):
    ids = theme_ids(seed)

    def block(b, indent):
        return [f"{indent}--{e['name']}: {value_string(*solved[b][e['name']], e, b)};"
                for e in ext["color"]["tokens"]]

    o = [f"""/* {ext['namespace']} - the product's own colour tokens.
   Load after the house tokens.css, never instead of it.
   Generated from {source} by tools/build.py --extend, against the {brand} set at accent hue {accent % 360}.
   Do not hand-edit this file; edit the seed and rebuild.

   Every token clears each of its floors on the float value and at 8-bit, sits at least
   {seed['seed']['productFromState']} CIEDE2000 at 8-bit from hw-success, hw-warning and hw-danger, and at least
   {seed['seed']['productHueChroma']} in hue and chroma from every house colour its seed holds it apart from,
   in both themes and under prefers-contrast: more. */""",
         ':root, [data-theme="light"] {', *block(ids[0], "  "), "}"]
    for theme in ids[1:]:
        o += ["", f'[data-theme="{theme}"] {{', *block(theme, "  "), "}"]
    o += ["", "@media (prefers-color-scheme: dark) {", '  :root:not([data-theme="light"]) {',
          *block(ids[-1], "    "), "  }", "}", "", "@media (prefers-contrast: more) {",
          '  :root, [data-theme="light"] {', *block(more_key(ids[0]), "    "), "  }"]
    for theme in ids[1:]:
        o += [f'  [data-theme="{theme}"] {{', *block(more_key(theme), "    "), "  }"]
    o += ["}", "", "@media (prefers-contrast: more) and (prefers-color-scheme: dark) {",
          '  :root:not([data-theme="light"]) {', *block(more_key(ids[-1]), "    "), "  }", "}"]
    return "\n".join(o) + "\n"


def verify_extension(house_css, ext_css, seed, ext):
    """(failures, report): every product floor and separation, re-measured on the two files as
    they will be written, the house one supplying the grounds."""
    house, prod = parse_emitted(house_css), parse_emitted(ext_css)
    de_bar, hc_bar = seed["seed"]["productFromState"], seed["seed"]["productHueChroma"]
    why = "this system requires (95-extending.md#a-colour-of-the-products-own)"
    bad, report = [], []
    for block in certified_blocks(seed):
        for e in ext["color"]["tokens"]:
            bad += floor_failures(e, block, prod[block], house[block])
            fg = prod[block].get(e["name"])
            if fg is None:
                continue
            if not in_gamut(*fg):
                bad.append(f"{e['name']} ({block}): oklch{fg} is outside sRGB")
            seps = sorted((hue_chroma_separation(fg, house[block][a]), a) for a in e["apart"])
            bad += [f"{e['name']} at hue {fg[2]:g} sits {d:.1f} from {a} in hue and chroma in "
                    f"{block}, below the {hc_bar} {why}" for d, a in seps if d < hc_bar]
            des = sorted((painted(fg, house[block][a]), a) for a in PRODUCT_STATES)
            bad += [f"{e['name']} at hue {fg[2]:g} sits {d:.1f} CIEDE2000 from {a} at 8-bit in "
                    f"{block}, below the {de_bar} {why}" for d, a in des if d < de_bar]
            cvd = min((*dichromat_painted(fg, house[block][a]), a) for a in PRODUCT_STATES)
            lum, lum8 = luminance(*fg), luminance8(*fg)
            ratios = [(ratio_lum(lum, luminance(*house[block][f"hw-{g}"])),
                       ratio8(lum8, luminance8(*house[block][f"hw-{g}"])), g)
                      for floor in e["floors"] for g in floor["on"]]
            r, r8, g = min(ratios)
            report.append(f"{e['name']:14} {block:11} oklch({fg[0]:g} {fg[1]:g} {fg[2]:g})  "
                          f"worst {r:.3f}:1 on --hw-{g} ({min(x[1] for x in ratios):.3f} at "
                          f"8-bit), {des[0][0]:.1f} CIEDE2000 from {des[0][1]}, "
                          f"{seps[0][0]:.2f} in hue and chroma from {seps[0][1]}; "
                          f"{cvd[1]} sees {cvd[0]:.1f} from {cvd[2]}, reported")
    return bad + media_copies_differ(seed, prod), report


def extend(seed, accent, solvers, house_css, a):
    """--extend: solve a product seed against the house set and write its one file."""
    path = Path(a.extend)
    try:
        ext = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        failures = [f"{path} could not be read: {exc.strerror or exc}"]
    except json.JSONDecodeError as exc:
        failures = [f"{path} is not valid JSON: {exc}"]
    else:
        failures = check_extension(seed, ext)
    if failures:
        for f in failures:
            print("FAIL  " + f, file=sys.stderr)
        print(f"\nrefusing to solve {path.name}: {len(failures)} check(s) failed",
              file=sys.stderr)
        return 1
    solved = {}
    for block, s in solvers.items():
        s.failures, s.notes = [], []
        solved[block] = {e["name"]: s.solve_one(e)[:3] for e in ext["color"]["tokens"]}
        failures += s.failures
        for n in s.notes:
            print("solved  " + n)
    css = build_extension_css(seed, ext, solved, accent, path.name, getattr(a, "label", "house"))
    bad, report = verify_extension(house_css, css, seed, ext)
    failures += bad
    for line in report:
        print(line)
    if failures:
        for f in failures:
            print("FAIL  " + f, file=sys.stderr)
        print(f"\nrefusing to write: {len(failures)} check(s) failed", file=sys.stderr)
        return 1
    target = (Path(a.out) if a.out else path.parent) / f"{ext['namespace']}.tokens.css"
    if a.check:
        stale = not target.exists() or target.read_text(encoding="utf-8") != css
        print(f"{'FAIL  ' if stale else ''}{target.name} is{' not' if stale else ''} what "
              f"{path.name} builds",
              file=sys.stderr if stale else sys.stdout)
        return 1 if stale else 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(css, encoding="utf-8")
    print(f"{len(ext['color']['tokens'])} {ext['namespace']} colour token(s) solved in "
          f"{len(solved)} blocks against accent hue {accent % 360}, 0 below a floor, 0 closer "
          f"than {seed['seed']['productFromState']} CIEDE2000 to a state or "
          f"{seed['seed']['productHueChroma']} in hue and chroma to a colour held apart.\n"
          f"  {target.name} {len(css):7,d} bytes")
    return 0


# --- the brand tier -------------------------------------------------------------------------
# A product's identity is a brand seed: twenty-three bounded inputs this build applies to a copy of
# the house seed before solving that copy with the code above, so a brand is a rebuild and never
# a hand-pick, and every brand ships the house's token names. 12-brand.md owns the rule. The
# numeric bounds are pinned here rather than in the seed, for GRID_SCOPE's reason: a seed that
# can widen a bound can switch the rule off.

BRAND_INPUTS = ("accentHue", "accentChroma", "accentLightness", "quietChroma", "ring",
                "neutralHue", "neutralChroma", "shape", "iconStroke", "display", "text",
                "brandHue", "brandLightness", "brandChroma", "primary", "selection",
                "groundLightness", "darkCard", "mono", "quote", "displayFrom", "displayScale",
                "sunkenDepth")
# The chroma multipliers keep a floor and have no ceiling: the sRGB gamut clips each colour, and
# the measured bars refuse what the gamut admits and a reader would misread
# (12-brand.md#the-inputs). The ceilings they replace were 1.3 and 4.0, and nothing had tested
# either; the second refused a cream ground the stateFillFromGround bar certifies once its state
# fills re-solve.
BOUNDS = {"accentChroma": (0.3, None), "quietChroma": (0.3, 1.0), "neutralChroma": (0.0, None)}
# groundLightness, per theme. The light floor is quoth's putty (D-039, L 0.925) with room for a
# darker putty; below 0.92 the prefers-contrast: more tier cannot keep hw-text-secondary and
# hw-text-muted two roles on the sunken surface. The ceiling is the house surface's own 1.000
# less the 0.022 the house keeps between ground and surface. Dark mirrors the same reasons.
GROUND_BOUNDS = {"light": (0.92, 0.985), "dark": (0.13, 0.22)}
# sunkenDepth, per theme: how far hw-surface-sunken sits under the ground, so a paper pane can sit
# in a deeper chassis (D-055 in quoth's record). The floor is the house's own step, so the input
# only deepens a well. In light, Field builds at 0.08 and at 0.081 its raised-contrast chart ramp
# closes; in dark nothing is drawn under the well, and 0.13, the lowest dark ground, keeps every
# admitted well at or above black (12-brand.md#sunken-depth).
SUNKEN_BOUNDS = {"light": (0.020, 0.08), "dark": (0.034, 0.13)}
# groundLightness slides every colour of its theme by the ground's own offset before the solver
# runs, so every relationship the house measured between them is kept and only the residue is
# re-solved. Moving the ground alone was tried first: the inks re-solved by different amounts, the
# text ladder closed to 0.0587 against the 0.06 it keeps, and the semantics climbed onto the chart
# series, which do not re-solve, to 3.8 against the 8.0 they keep. Two groups stay: the ink family,
# a control and its label solved to each other rather than to the ground, and the vivid tier's
# fills, whose lightness is the brand's own input.
NOT_SLID = ("hw-ink", "hw-ink-hover", "hw-ink-active", "hw-ink-text")


def slides(e):
    return e["kind"] == "oklch" and e["name"] not in NOT_SLID and not e.get("role")
# darkCard: step (D-040 in quoth's record, 12-brand.md#the-dark-card-step): in the dark theme a
# card is told from the page by a lighter surface and a visible border, never a shadow, so
# hw-surface is solved to CARD_STEP over hw-ground and hw-border to CARD_STEP over hw-surface.
# 1.2 is the smallest round step above every dark card step recorded as failing to separate
# (1.094, 1.107, 1.111, 1.116) and above the house's own raised step, 1.169.
CARD_STEP = 1.2
PRIMARY_FAMILY = {"ink": ("hw-ink", "hw-ink-hover", "hw-ink-active", "hw-ink-text"),
                  "brand": ("hw-brand", "hw-brand-hover", "hw-brand-active", "hw-on-brand")}
PRIMARY_ALIASES = ("hw-primary", "hw-primary-hover", "hw-primary-active", "hw-on-primary")
# accentChroma scales the accent family. accentLightness moves the ink and its hover, in all four
# blocks, by the brand's offset from the house accent: moved in the default blocks alone, a deep
# warm accent is pulled back onto hw-warning by the 7:1 re-solve under prefers-contrast: more.
ACCENT_FAMILY = ("hw-accent", "hw-accent-hover", "hw-accent-ring")
ACCENT_INK = ("hw-accent", "hw-accent-hover")
# displayFrom: the first step set in the display face. title-1 is the step a screen names itself
# with, so a product whose identity is its display voice carries it into the product itself
# (20-type.md#a-brands-faces). displayScale multiplies the two display steps only, to whole px:
# every step below them was derived from the text face's x-height and stays where it is.
DISPLAY_FROM = ("display-2", "title-1")
DISPLAY_SCALES = (0.9, 1.0, 1.25)
DISPLAY_STEPS = ("display-1", "display-2")


def brand_errors(seed, brand):
    """Every way a brand seed cannot be trusted, checked once at the boundary."""
    if not isinstance(brand, dict):
        return [f"the brand seed is {brand!r}, not a JSON object"]
    kit = seed["brand"]
    bad = [f"{k!r} is not a brand input. A brand seed names {', '.join(BRAND_INPUTS)}, and "
           f"nothing else; a house token is never set by name (95-extending.md)"
           for k in brand if k not in BRAND_INPUTS + ("name", "note")]
    name = brand.get("name")
    if not (isinstance(name, str) and NAMESPACE.match(name) and name != "hw"):
        bad.append(f"name {name!r} is not a product's own name: one lowercase word, never hw")
    for k in ("accentHue", "neutralHue", "brandHue"):
        v = brand.get(k, 0)
        if isinstance(v, bool) or not isinstance(v, int) or not 0 <= v < 360:
            bad.append(f"{k} {v!r} is not a whole number of degrees from 0 to 359")
    for k, (lo, hi) in BOUNDS.items():
        v = finite_number(brand.get(k, 1.0)) if not isinstance(brand.get(k), str) else None
        if v is None or v < lo or (hi is not None and v > hi):
            span = f"{lo} to {hi}" if hi is not None else f"at least {lo}"
            bad.append(f"{k} {brand.get(k)!r} is not {span} times the house anchors "
                       f"(12-brand.md#the-inputs)")

    def per_theme(k, bounds, what="one lightness"):
        v = brand[k]
        if not (isinstance(v, dict) and set(v) == set(theme_ids(seed))
                and all(finite_number(x) is not None and not isinstance(x, str)
                        and bounds[t][0] <= x <= bounds[t][1] for t, x in v.items())):
            span = ", ".join(f"{t} {a} to {b}" for t, (a, b) in bounds.items())
            bad.append(f"{k} {v!r} is not {what} for each theme, {span}")
    for k in ("accentLightness", "brandLightness"):
        if k in brand:
            per_theme(k, {t: (1e-4, 1 - 1e-4) for t in theme_ids(seed)})
    if "groundLightness" in brand:
        per_theme("groundLightness", GROUND_BOUNDS)
    if "sunkenDepth" in brand:
        per_theme("sunkenDepth", SUNKEN_BOUNDS, "one step of lightness under the ground")
    if "brandChroma" in brand:
        v = brand["brandChroma"]
        if isinstance(v, str) or finite_number(v) is None or v <= 0:
            bad.append(f"brandChroma {v!r} is not a chroma above 0; it is absolute, and the sRGB "
                       f"gamut clips it at the fill's lightness")
    if ("brandLightness" in brand) != ("brandChroma" in brand):
        bad.append("brandLightness and brandChroma name the vivid fill together; a seed names "
                   "both or neither (12-brand.md#the-vivid-tier)")
    for k in ("brandHue", "primary", "selection"):
        if k in brand and "brandLightness" not in brand:
            bad.append(f"{k} is a vivid-tier input, and this seed names no brandLightness and "
                       f"brandChroma to open the tier with (12-brand.md#the-vivid-tier)")
    for k, allowed in (("ring", ("accent", "ink")), ("shape", tuple(kit["registers"])),
                       ("iconStroke", tuple(kit["iconStrokes"])),
                       ("display", tuple(kit["faces"])), ("text", tuple(kit["faces"])),
                       ("quote", tuple(kit["faces"])),
                       ("mono", tuple(n for n, f in kit["faces"].items() if f.get("monospaced"))),
                       ("primary", ("ink", "brand")), ("selection", ("accent", "neutral")),
                       ("darkCard", ("house", "step")), ("displayFrom", DISPLAY_FROM),
                       ("displayScale", DISPLAY_SCALES)):
        if k in brand and (isinstance(brand[k], bool) or brand[k] not in allowed):
            bad.append(f"{k} {brand[k]!r} is not one of {', '.join(map(repr, allowed))}")
    return bad


def anchors(entry):
    """(theme, anchor) for every lightness and chroma anchor a token carries, both tiers."""
    for t in ("light", "dark"):
        yield t, entry[t]
    for t, anchor in entry.get("contrastMore", {}).items():
        yield t, anchor


def house_face(seed, family):
    """The roster name of the face a house type family sets."""
    return next(n for n, f in seed["brand"]["faces"].items()
                if f["stack"] == seed["type"]["families"][family])


def open_vivid(s, brand):
    """Append the vivid tier's tokens to a brand copy of the seed, their fills at the lightness
    and chroma the brand names, and point the primary aliases and the selection fill."""
    kit = s["brand"]["vivid"]
    tokens = {e["name"]: e for e in s["color"]["tokens"]}
    for name, floors in kit["floors"].items():
        tokens[name]["floors"] = tokens[name].get("floors", []) + copy.deepcopy(floors)
    family = dict(zip(PRIMARY_ALIASES, PRIMARY_FAMILY[brand.get("primary", "ink")]))
    for e in copy.deepcopy(kit["tokens"]):
        if e["hue"] == "accent":
            e["hue"] = brand.get("brandHue", brand.get("accentHue", s["seed"]["accentHue"]))
        if e.get("role") in ("fill", "press"):
            for t in theme_ids(s):
                e[t] = {"L": f"{brand['brandLightness'][t]:.4f}",
                        "C": f"{brand['brandChroma']:.4f}"}
        elif e["name"] == "hw-brand-quiet":
            for t in theme_ids(s):
                e[t]["C"] = f"{min(float(e[t]['C']), brand['brandChroma']):.4f}"
        elif e["name"] == "hw-select" and brand.get("selection", "accent") == "accent":
            quiet = tokens["hw-accent-quiet"]
            e["hue"] = quiet["hue"]
            e.update({t: dict(quiet[t]) for t in theme_ids(s)})
        if e["name"] in family:
            e["of"] = family[e["name"]]
        s["color"]["tokens"].append(e)


def slide(L, offset):
    return f"{min(max(float(L) + offset, 0.0), 1.0):.4f}"


def lift_cards(s):
    """darkCard: step. Lift the dark surfaces above the ground by the smallest amount that puts
    hw-surface CARD_STEP over hw-ground, then hw-border CARD_STEP over the lifted surface, each on
    the float value and at 8-bit, and slide every colour drawn on them by the same lift, for the
    reason slides() gives. The solver measures these tokens as grounds, so the step is fixed here,
    before it runs, and re-measured on the written CSS by verify_emitted."""
    tok = {e["name"]: e for e in s["color"]["tokens"]}
    h = resolve_hue("neutral", s["seed"]["accentHue"], neutral_hue(s, s["seed"]["accentHue"]))

    def value(name, lift):
        L = min(float(tok[name]["dark"]["L"]) + lift, 1.0)
        return L, min(float(tok[name]["dark"]["C"]), max_chroma(L, h)), h

    def lift_over(name, under, start):
        lift = start
        while lift < 1.0:
            a, b = value(name, lift), under
            if (ratio_lum(luminance(*a), luminance(*b)) >= CARD_STEP + MARGIN
                    and ratio8(luminance8(*a), luminance8(*b)) >= CARD_STEP):
                return lift
            lift += GRID
        return lift
    surface = lift_over("hw-surface", value("hw-ground", 0.0), 0.0)
    border = lift_over("hw-border", value("hw-surface", surface), surface)
    for e in s["color"]["tokens"]:
        if e["name"] == "hw-border":
            e["dark"]["L"] = slide(e["dark"]["L"], border)
        elif slides(e) and e["name"] not in ("hw-ground", "hw-surface-sunken"):
            for theme, anchor in anchors(e):
                if theme == "dark":
                    anchor["L"] = slide(anchor["L"], surface)
    s["seed"]["cardStep"] = CARD_STEP


def apply_brand(seed, brand):
    """A copy of the house seed with one brand's inputs applied; nothing else changes."""
    s = copy.deepcopy(seed)
    kit, sd = s["brand"], s["seed"]
    sd["accentHue"] = brand.get("accentHue", sd["accentHue"])
    sd["neutralHue"] = brand.get("neutralHue", sd["neutralHue"])
    s["name"] = f"{seed['name']}, {brand['name']} brand"
    if "brandLightness" in brand:
        open_vivid(s, brand)
    house = {e["name"]: e for e in seed["color"]["tokens"]}
    offset = {t: v - float(house["hw-accent"][t]["L"])
              for t, v in brand.get("accentLightness", {}).items()}
    for e in s["color"]["tokens"]:
        if e["kind"] != "oklch":
            continue
        k = (brand.get("neutralChroma", 1.0) if e["hue"] == "neutral" else
             brand.get("accentChroma", 1.0) if e["name"] in ACCENT_FAMILY else
             brand.get("quietChroma", 1.0) if e["name"] == "hw-accent-quiet"
             or (e["name"] == "hw-select" and e["hue"] == "accent") else 1.0)
        for theme, anchor in anchors(e):
            if k != 1.0:
                anchor["C"] = f"{float(anchor['C']) * k:.4f}"
            if offset and e["name"] in ACCENT_INK:
                anchor["L"] = f"{min(max(float(anchor['L']) + offset[theme], 0.0), 1.0):.4f}"
    ground = {t: L - float(house["hw-ground"][t]["L"])
              for t, L in brand.get("groundLightness", {}).items()}
    for e in s["color"]["tokens"]:
        if ground and slides(e):
            for theme, anchor in anchors(e):
                anchor["L"] = slide(anchor["L"], ground[theme])
    tok = {e["name"]: e for e in s["color"]["tokens"]}
    for t, depth in brand.get("sunkenDepth", {}).items():
        was = tok["hw-surface-sunken"][t]["L"]
        tok["hw-surface-sunken"][t]["L"] = slide(tok["hw-ground"][t]["L"], -depth)
        # Every colour darker than the well moves down with it, for the reason slides() gives:
        # moving the well alone closed hw-text-muted on hw-text-secondary to 0.0487 and left
        # hw-select 0.001 under the well, a selected rail row nobody could see.
        drop = float(tok["hw-surface-sunken"][t]["L"]) - float(was)
        for e in s["color"]["tokens"]:
            if drop and slides(e) and e["name"] != "hw-surface-sunken":
                for theme, anchor in anchors(e):
                    if theme == t and float(anchor["L"]) < float(was):
                        anchor["L"] = slide(anchor["L"], drop)
    if "ring" in brand:
        # "accent": the ring is the accent ink itself, as a product whose focus ring is its one
        # colour draws it. "ink": the ring takes the text ink, so it is as visible as the most
        # visible neutral and leaves hue to the states. Either way it is still solved to its
        # own floors and held to its own bars.
        ring, source = (next(e for e in s["color"]["tokens"] if e["name"] == n)
                        for n in ("hw-accent-ring",
                                  "hw-accent" if brand["ring"] == "accent" else "hw-text"))
        ring["hue"] = source["hue"]
        ring.update({t: dict(source[t]) for t in theme_ids(s)})
        ring.pop("contrastMore", None)
        if "contrastMore" in source:
            ring["contrastMore"] = copy.deepcopy(source["contrastMore"])
    for e in s["radius"]["tokens"]:
        e["value"] = kit["registers"][brand.get("shape", "house")].get(e["name"], e["value"])
    for e in s["icon"]["tokens"]:
        if e["name"] == "hw-icon-stroke" and "iconStroke" in brand:
            e["value"] = brand["iconStroke"]
    declared = {}
    for family, key in (("display", "display"), ("sans", "text"), ("mono", "mono"),
                        ("quote", "quote")):
        if key in brand:
            s["type"]["families"][family] = kit["faces"][brand[key]]["stack"]
            decl = face_declarations(kit["faces"][brand[key]])
            if decl:
                declared[family] = decl
    if declared:
        s["type"]["faceDeclarations"] = declared
    house_x = kit["faces"][house_face(seed, "sans")]["xHeight"]
    if brand.get("text", house_face(seed, "sans")) != house_face(seed, "sans"):
        # 20-type.md: a text face other than the house's is held to the house x-height.
        s["type"]["sansSizeAdjust"] = house_x
    if "quote" in brand:
        s["type"]["quoteSizeAdjust"] = house_x
    first = [st["name"] for g in s["type"]["groups"] for st in g["styles"]].index(
        brand.get("displayFrom", "display-2"))
    scale = brand.get("displayScale", 1.0)
    for i, st in enumerate(st for g in s["type"]["groups"] for st in g["styles"]):
        if i <= first:
            st["family"] = "display"
        if st["name"] in DISPLAY_STEPS and scale != 1.0:
            st["fontSize"] = f"{round(float(st['fontSize'][:-2]) * scale)}px"
    if brand.get("darkCard") == "step":
        lift_cards(s)
    return s


def load_brand(path, seed):
    """(failures, brand) for a brand seed file."""
    try:
        brand = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [f"{path} could not be read: {exc.strerror or exc}"], None
    except json.JSONDecodeError as exc:
        return [f"{path} is not valid JSON: {exc}"], None
    return brand_errors(seed, brand), brand


def lightness_held(seed, brand, resolved):
    """A brand's accentLightness is a lightness the floors already accept, or it is refused:
    the solver would otherwise move it silently, and an input the build discards is a claim
    the file does not keep."""
    bad = []
    accent = next(e for e in seed["color"]["tokens"] if e["name"] == "hw-accent")
    for t, want in brand.get("accentLightness", {}).items():
        got = resolved[t]["hw-accent"][0]
        if abs(got - float(accent[t]["L"])) > EPS:
            bad.append(f"accentLightness {t} {want} does not clear hw-accent's floors at hue "
                       f"{resolved[t]['hw-accent'][2]:g}; the nearest lightness that does is "
                       f"{got:.4f} (12-brand.md#accent-lightness)")
    return bad


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path(path.name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--accent-hue", type=int, default=None,
                    help="override the seed's accent hue and re-solve the whole set")
    ap.add_argument("--brand", metavar="SEED", default=None,
                    help="solve the whole set under a product's brand seed and write it to "
                         "tokens/ beside that seed unless --out is given")
    ap.add_argument("--check", action="store_true",
                    help="emit nothing; exit non-zero if the committed files are stale")
    ap.add_argument("--out", default=None, help="write into this directory instead of tokens/")
    ap.add_argument("--extend", metavar="SEED", default=None,
                    help="solve a product's own colour seed against the house set, or the "
                         "--brand set, and write only <namespace>.tokens.css, beside the seed "
                         "unless --out is given")
    a = ap.parse_args(argv)

    seed, brand = load_seed(ROOT / "tokens" / "tokens.seed.json"), None
    a.label = "house"
    if a.brand:
        failures, brand = load_brand(Path(a.brand), seed)
        if a.accent_hue is not None:
            failures.append("--accent-hue and --brand together: a brand seed names its own hue")
        if failures:
            for f in failures:
                print("FAIL  " + f, file=sys.stderr)
            print(f"\nrefusing to solve {Path(a.brand).name}: {len(failures)} check(s) failed",
                  file=sys.stderr)
            return 1
        seed = apply_brand(seed, brand)
        a.label = f"{brand['name']}, from {rel(a.brand)}"
    accent = a.accent_hue if a.accent_hue is not None else seed["seed"]["accentHue"]
    if not a.brand and accent % 360 != seed["seed"]["accentHue"]:
        a.label = f"house, rebuilt at accent hue {accent % 360}"

    # The floors are checked before anything is solved against them: a solver that has already
    # skipped a misnamed ground cannot report it afterwards.
    failures = check_floors(seed) + check_grid(seed) + check_roster(seed)
    if failures:
        for f in failures:
            print("FAIL  " + f, file=sys.stderr)
        print(f"\nrefusing to solve: {len(failures)} check(s) failed", file=sys.stderr)
        return 1

    resolved, notes, more_notes, solvers = {}, [], [], {}
    for theme in theme_ids(seed):
        for more in (False, True):
            s = Solver(seed, accent, theme, more)
            key = more_key(theme) if more else theme
            resolved[key], solvers[key] = s.run(), s
            (more_notes if more else notes).extend(s.notes)
            failures += s.failures
    if brand:
        failures += lightness_held(seed, brand, resolved)

    stats = count_pairs(seed, resolved)
    js = build_tokens_json(seed, resolved)
    css = build_tokens_css(seed, resolved, accent, stats, a.label)
    failures += verify_emitted(css, seed)

    if a.extend and not failures:
        return extend(seed, accent, solvers, css, a)
    for n in notes + more_notes:
        print("solved  " + n)
    if failures:
        for f in failures:
            print("FAIL  " + f, file=sys.stderr)
        print(f"\nrefusing to write: {len(failures)} check(s) failed", file=sys.stderr)
        return 1

    out = Path(a.out) if a.out else (Path(a.brand).parent / "tokens" if a.brand
                                      else ROOT / "tokens")
    out.mkdir(parents=True, exist_ok=True)
    targets = {"tokens.json": js, "tokens.css": css}

    if a.check:
        stale = [n for n, text in targets.items()
                 if not (out / n).exists() or (out / n).read_text(encoding="utf-8") != text]
        for n in stale:
            print(f"FAIL  {rel(out / n)} is not what the seed builds", file=sys.stderr)
        print(f"\n{len(targets) - len(stale)} of {len(targets)} token files match the seed.")
        return 1 if stale else 0

    for n, text in targets.items():
        (out / n).write_text(text, encoding="utf-8")

    n_col = len(seed["color"]["tokens"])
    print(f"{a.label}: accent hue {accent % 360}; {n_col} colour tokens solved across "
          f"{len(theme_ids(seed))} themes, {len(notes)} re-solved.")
    print(f"{stats['text_pairs']} pairs held to WCAG AA 4.5:1 and "
          f"{stats['nontext_pairs']} to 3:1, 0 below bar. 0 outside sRGB.")
    print(f"prefers-contrast: more: the same {stats['text_pairs']} pairs held to AAA "
          f"{AAA_BAR}:1 and {stats['nontext_pairs']} to {AA_BAR}:1, {len(more_notes)} of "
          f"{2 * sum(1 for e in seed['color']['tokens'] if e['kind'] == 'oklch')} values "
          f"re-solved, 0 below bar.")
    on, off = grid_stats(seed)
    print(f"{on} space and size values on the {seed['grid']['unit']}px unit, "
          f"{off} off it and all {off} declared with a reason.")
    for n in targets:
        print(f"  {rel(out / n)}  {len(targets[n]):7,d} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
