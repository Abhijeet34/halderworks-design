#!/usr/bin/env python3
"""Re-derive and verify this system's contrast claims from tokens/tokens.css.

This is the SECOND instrument, and two things make it one rather than a second reading of the
first. It shares no line of arithmetic with tools/build.py: the conversion here is the CSS
Color 4 reference path (w3c/csswg-drafts css-color-4/conversions.js, OKLab_to_LMS, LMS_to_XYZ
and XYZ_to_lin_sRGB as exact rationals), which is what a browser implements, while build.py
inverts the original Oklab matrices. And the pairs it requires are declared here, not read from
tokens/tokens.seed.json, so a floor cannot be weakened in the same edit as the value it guards.
Until 2026-09-21 neither held: build.py imported this file's converter, and the seed carried the
floors, so deleting a floor and moving its value was one edit that no tool refused.

The principle both instruments are built to: MEASURE THE ARTIFACT, NEVER THE INTENT. A number
that was not re-measured in the exact form it will ship has not been certified.

It runs four passes and exits non-zero if any fails:

  1. Every ratio the book publishes, re-derived. The tables in 15-color-combinations.md are
     parsed cell by cell rather than transcribed, so a published number that stops being true
     is a failure here instead of a sentence nobody re-measured. A converter that cannot
     reproduce the existing table cannot certify a new pair either, and this caught a real bug:
     omitting the XYZ step returns a plausible-looking colour with the wrong hue, and it put the
     light ground at #F2F8FF instead of #F6F8F8.
  2. REQUIRED: every pair this system certifies, against WCAG AA 4.5:1 for text and 1.4.11's
     3:1 for a control boundary. No tolerance, three decimals, and each pair is measured twice:
     on the unquantized value and on the 8-bit sRGB value a display receives, because a pair
     that clears 3:1 on floats and reads 2.999 in hex is not a pair any third-party checker
     will agree about. The @media (prefers-contrast: more) blocks are held to the same pairs at
     7:1 and 4.5:1.
  3. The accent is told apart from the three states on each element it paints, in CIEDE2000 on
     the 8-bit value a display receives: its ink, the selected-row fill, and the focus ring
     against the error border. The ring is told apart from a control's own edge, and each state's
     quiet fill from the ground. The six chart colours are told apart from the three semantics
     and from each other, and neighbours alternate in lightness; a chart hue is the accent plus a
     fixed rotation while the semantics stay put, so a collision moves around the wheel with
     every rebuild. The text roles keep a visible lightness step, which raising the floors once
     erased. A brand's shape register and icon stroke are one of the house's own.
  4. Every colour token is inside sRGB, and each dark block a user with no explicit choice
     actually gets, through a prefers-color-scheme query, is identical to the explicit one. That
     copy used to be discarded as a duplicate, which is a guess about a file this tool is here
     to stop guessing about.

  Pass 1 is measured on the house set, which the file's header names as `Brand: house.`. Run
  against a brand's set or a rebuild at another hue - `tools/build.py --brand` or
  `--accent-hue N` - the published ratios no longer describe that palette, so pass 1 reports
  itself skipped and names the brand rather than failing rows that were never claimed about it.
  Until the brand tier it recognised the house by hue 198, which held a brand that kept 198
  with other neutrals to ratios it never claimed. Passes 2 to 4 always run; they are the
  certificate.

  Pass 5 runs only with --extend: a product's own colour tokens, from the file tools/build.py
  --extend wrote beside the product's seed, held to what this file requires of any product
  colour and to any higher bar the seed claims.

    python3 tools/contrast.py [tokens.css] [--extend product.seed.json [--extend-css file]]
"""
import argparse
import json
import math
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- the converter: the CSS Color 4 reference path -----------------------------------------
# Exact rationals for XYZ -> linear sRGB, as conversions.js carries them. The measurable
# difference from build.py's inverted-matrix path is small and it is the point: white comes back
# as exactly 1.000000 here and as 1.000186 there, which is a white-point mismatch rather than
# the round-off the old comment in this file claimed.

OKLAB_TO_LMS = ((1.0, 0.3963377773761749, 0.2158037573099136),
                (1.0, -0.1055613458156586, -0.0638541728258133),
                (1.0, -0.0894841775298119, -1.2914855480194092))
LMS_TO_XYZ = ((1.2268798758459243, -0.5578149944602171, 0.2813910456659647),
              (-0.0405757452148008, 1.1122868032803170, -0.0717110580655164),
              (-0.0763729366746601, -0.4214933324022432, 1.5869240198367816))
XYZ_TO_LIN_SRGB = tuple(tuple(float(x) for x in row) for row in (
    (F(12831, 3959), F(-329, 214), F(-1974, 3959)),
    (F(-851781, 878810), F(1648619, 878810), F(36519, 878810)),
    (F(705, 12673), F(-2585, 12673), F(705, 667))))


def _mul(m, v):
    return [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]


def oklch_to_rgb(L, C, h_deg):
    """oklch -> oklab -> LMS -> XYZ(D65) -> linear sRGB -> gamma-encoded sRGB, in 0..1."""
    h = math.radians(h_deg)
    lab = (L, C * math.cos(h), C * math.sin(h))
    lms = [x ** 3 for x in _mul(OKLAB_TO_LMS, lab)]
    lin = _mul(XYZ_TO_LIN_SRGB, _mul(LMS_TO_XYZ, lms))

    def gamma(u):
        s = -1 if u < 0 else 1
        u = abs(u)
        return s * (12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055)
    return [gamma(u) for u in lin]


def in_gamut(L, C, h, eps=1e-6):
    """The reference path returns white as exactly 1.0, so eps here only absorbs floating-point
    noise rather than a white-point error. The real out-of-gamut defect 90-evidence.md records,
    a warning at chroma 0.12, sits at -0.1185 on blue and is five orders above this."""
    return all(-eps <= v <= 1 + eps for v in oklch_to_rgb(L, C, h))


def quantize(rgb):
    """The 8-bit sRGB value a display receives, which is what a hex-based checker is given."""
    return [round(min(max(c, 0.0), 1.0) * 255) / 255 for c in rgb]


def luminance_rgb(rgb):
    def lin(c):
        c = min(max(c, 0.0), 1.0)
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def luminance(L, C, h):
    return luminance_rgb(oklch_to_rgb(L, C, h))


def ratio_lum(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def ratio(fg, bg):
    """(float ratio, 8-bit ratio). Both are reported because a pair can clear its bar on one
    and miss it on the other, and the system claims both."""
    a, b = oklch_to_rgb(*fg), oklch_to_rgb(*bg)
    return (ratio_lum(luminance_rgb(a), luminance_rgb(b)),
            ratio_lum(luminance_rgb(quantize(a)), luminance_rgb(quantize(b))))


def hexof(L, C, h):
    return "#" + "".join("%02X" % round(min(max(v, 0), 1) * 255) for v in oklch_to_rgb(L, C, h))


# --- painted colour difference: CIEDE2000 on the 8-bit value --------------------------------
# linear sRGB -> XYZ is conversions.js's lin_sRGB_to_XYZ, as exact rationals, and D65 is its
# white; build.py derives both from the inverse of its own matrix instead. The difference formula
# is Sharma, Wu and Dalal 2005, written here in their numbered steps, and tests/invariants.py
# holds this and build.py's to the paper's own test pairs.

LIN_SRGB_TO_XYZ = tuple(tuple(float(x) for x in row) for row in (
    (F(506752, 1228815), F(87881, 245763), F(12673, 70218)),
    (F(87098, 409605), F(175762, 245763), F(12673, 175545)),
    (F(7918, 409605), F(87881, 737289), F(1001167, 1053270))))
D65 = (0.3127 / 0.3290, 1.0, (1.0 - 0.3127 - 0.3290) / 0.3290)


def lab(fg):
    """CIELAB (D65) of an oklch triple as the display receives it, quantized to 8 bits."""
    xyz = _mul(LIN_SRGB_TO_XYZ, [_lin(c) for c in quantize(oklch_to_rgb(*fg))])
    eps, kappa = 216 / 24389, 24389 / 27
    f = [v ** (1 / 3) if v > eps else (kappa * v + 16) / 116 for v in
         (xyz[0] / D65[0], xyz[1] / D65[1], xyz[2] / D65[2])]
    return (116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2]))


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def de2000(lab1, lab2):
    (L1, a1, b1), (L2, a2, b2) = lab1, lab2
    # (1) a' and C' and h', with the chroma-dependent G stretch of the a axis
    cmean = (math.sqrt(a1 * a1 + b1 * b1) + math.sqrt(a2 * a2 + b2 * b2)) / 2
    G = 0.5 * (1 - math.sqrt(cmean ** 7 / (cmean ** 7 + 6103515625)))
    p1, p2 = complex(a1 * (1 + G), b1), complex(a2 * (1 + G), b2)
    C1, C2 = abs(p1), abs(p2)
    h1 = math.degrees(math.atan2(p1.imag, p1.real)) % 360 if C1 else 0.0
    h2 = math.degrees(math.atan2(p2.imag, p2.real)) % 360 if C2 else 0.0
    # (2) the three differences
    dL, dC = L2 - L1, C2 - C1
    if C1 * C2 == 0:
        dh = 0.0
    elif abs(h2 - h1) <= 180:
        dh = h2 - h1
    else:
        dh = h2 - h1 - 360 if h2 > h1 else h2 - h1 + 360
    dH = 2 * math.sqrt(C1 * C2) * math.sin(math.radians(dh) / 2)
    # (3) the weighting functions at the pair's mean
    Lm, Cm = (L1 + L2) / 2, (C1 + C2) / 2
    if C1 * C2 == 0:
        hm = h1 + h2
    elif abs(h1 - h2) <= 180:
        hm = (h1 + h2) / 2
    else:
        hm = (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm))
         + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.2 * math.cos(math.radians(4 * hm - 63)))
    SL = 1 + (0.015 * (Lm - 50) ** 2) / math.sqrt(20 + (Lm - 50) ** 2)
    SC, SH = 1 + 0.045 * Cm, 1 + 0.015 * Cm * T
    RC = 2 * math.sqrt(Cm ** 7 / (Cm ** 7 + 6103515625))
    RT = -RC * math.sin(math.radians(2 * 30 * math.exp(-(((hm - 275) / 25) ** 2))))
    return math.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2
                     + RT * (dC / SC) * (dH / SH))


def painted(a, b):
    return de2000(lab(a), lab(b))


TOKEN_RE = re.compile(r"^\s*(--[a-z][a-z0-9]*-[a-z0-9-]+):\s*oklch\(([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\)\s*;")


# (media query, selector) -> block. A selector means nothing without the query it sits in: the
# light selector appears twice, once plain and once under prefers-contrast, and reading the
# second as the first would certify the high-contrast values as the default ones.
MORE = "@media (prefers-contrast: more)"
BLOCKS = {
    (None, ':root, [data-theme="light"]'): "light",
    (None, '[data-theme="dark"]'): "dark",
    ("@media (prefers-color-scheme: dark)", ':root:not([data-theme="light"])'): "media-dark",
    (MORE, ':root, [data-theme="light"]'): "light-more",
    (MORE, '[data-theme="dark"]'): "dark-more",
    (MORE + " and (prefers-color-scheme: dark)", ':root:not([data-theme="light"])'):
        "media-dark-more",
}


def parse_tokens(path):
    """Return {'light': {...}, 'dark': {...}, 'media-dark': {...}, and the three -more blocks}.

    Every colour block, including both media-query copies of dark: pass 4 checks each against
    the explicit block rather than assuming it is a duplicate."""
    themes = {name: {} for name in BLOCKS.values()}
    cur, media = None, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("@media"):
            media = s[:-1].strip()
            continue
        if s.endswith("{"):
            cur = BLOCKS.get((media, s[:-1].strip()))
            continue
        if s.startswith("}"):
            if cur is None:
                media = None
            cur = None
            continue
        m = TOKEN_RE.match(line)
        if m and cur:
            themes[cur][m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    return themes


# --- what this system certifies ------------------------------------------------------------
# The certificate lives here and nowhere else in this file's reach. tokens.seed.json carries the
# same set as solver targets, and tests/invariants.py fails if the two ever disagree: two
# declarations that must match is deliberate redundancy, the same reason a ledger has two sides.
# It held 158 pairs where the list it replaced held 112, and 77 cells of
# design/15-color-combinations.md were certified by nothing at all. The chart fills on the three
# surfaces beside the ground and the ruled ground's two permitted inks took it to 198.

AA, NON_TEXT = 4.5, 3.0
# prefers-contrast: more raises text to WCAG 2.2 SC 1.4.6's 7:1. SC 1.4.11 has no enhanced level,
# so a non-text pair is raised to 4.5:1, the next bar this file already holds.
MORE_BAR = {AA: 7.0, NON_TEXT: AA}

SURFACES = ["--hw-ground", "--hw-surface", "--hw-surface-raised", "--hw-surface-sunken",
            "--hw-surface-hover", "--hw-surface-active"]
QUIET = ["--hw-accent-quiet", "--hw-success-quiet", "--hw-warning-quiet", "--hw-danger-quiet"]
SEMANTICS = ["accent", "success", "warning", "danger"]


def required():
    """(bar, foreground, background, what relies on it), every pair the book certifies.

    Grouped by the claim each group answers, so a reader can check the list against the prose
    rather than against the seed. 99 pairs per theme, 198 over the two."""
    for s in SURFACES:
        yield AA, "--hw-text", s, "body copy, label, legend, read-only value"
        yield AA, "--hw-text-secondary", s, "helper text"
        yield AA, "--hw-text-muted", s, "placeholder, character count"
        yield NON_TEXT, "--hw-border-strong", s, "input, select, textarea, switch, slider rail, panel edge"
        yield NON_TEXT, "--hw-ink", s, "checked box, radio dot, switch on, slider fill"
        yield NON_TEXT, "--hw-accent-ring", s, "focus ring on a form control"
        # 10-color.md: the accent and the three semantics are readable text on every surface.
        # This subsumes their non-text uses - hw-danger as an error field border was listed
        # separately at 3:1, which is a weaker claim about the same pair.
        for sem in SEMANTICS:
            yield AA, f"--hw-{sem}", s, f"{sem} text, and its border where it draws one"
    # 15-color-combinations.md certifies body text on any quiet fill, and each semantic on its own.
    for q in QUIET:
        yield AA, "--hw-text", q, "body copy inside a quiet fill"
    for sem in SEMANTICS:
        yield AA, f"--hw-{sem}", f"--hw-{sem}-quiet", f"{sem} summary block"
    # 60-states.md: disabled text is exempt from AA and is still held to the non-text bar.
    for s in ("--hw-ground", "--hw-surface", "--hw-surface-sunken"):
        yield NON_TEXT, "--hw-text-disabled", s, "disabled field text"
    yield AA, "--hw-ink-text", "--hw-ink", "check glyph, switch thumb"
    yield AA, "--hw-ink-text", "--hw-ink-active", "check glyph on a pressed control"
    # 10-color.md: the six chart colours are held to the same 3:1 as a control boundary, on
    # every surface a chart is drawn on rather than on the page ground alone.
    for n in range(1, 7):
        for s in SURFACES[:4]:
            yield NON_TEXT, f"--hw-chart-{n}", s, f"chart series {n} on {s[5:]}"
    # 75-spec-sheet.md#ruled: ink on the ruled ground can land on a rule, so it is certified
    # against --hw-border, the ground's worst pixel.
    for fg in ("--hw-text", "--hw-text-secondary"):
        yield AA, fg, "--hw-border", "ink permitted on the ruled ground"


def refused():
    """(bar, foreground, background, why), pairs the book refuses because they fall BELOW the bar.

    A published refusal is a claim too: if a re-solve lifted this pair over 4.5:1 the book would
    go on refusing a pair that now passes, and nothing would say so."""
    yield AA, "--hw-text-muted", "--hw-border", "75-spec-sheet.md#ruled refuses muted ink on a rule"


# The bars, declared here rather than read from the seed, for the same reason the pairs are.
# The accent is held apart from the states on each element it paints, in CIEDE2000 on the 8-bit
# value (10-color.md, "The three bars the accent is held to"): its ink from every state ink, the
# selected-row fill from every state's quiet fill, and the focus ring from hw-danger, the one
# state drawn as a border around a control. The ring is also held apart from hw-border-strong, the control's own edge, and every
# state's quiet fill from hw-ground (12-brand.md). A chart colour is an ink, held to one bar in
# oklab distance times 100 against each semantic and each other series, and neighbours alternate
# in lightness: 0.12 of lightness is a separation of 12 on its own, so neighbours stay apart
# where hue is lost, in greyscale print or to a reader who cannot see it.
ACCENT_BARS = (("ink", "--hw-accent", "", ("success", "warning", "danger"), 14),
               ("fill", "--hw-accent-quiet", "-quiet", ("success", "warning", "danger"), 5),
               ("ring", "--hw-accent-ring", "", ("danger",), 17))
RING_FROM_BORDER, FILL_FROM_GROUND = 14, 6
CHART_SEPARATION, NEIGHBOUR_DL = 8.0, 0.12
CHARTS = [f"--hw-chart-{n}" for n in range(1, 7)]


def separation(a, b, lightness=True):
    """Oklab distance times 100 between two oklch triples. Without lightness it is the distance
    in hue and chroma alone, which pass 5 holds a product colour to."""
    (L1, C1, h1), (L2, C2, h2) = a, b
    da = C1 * math.cos(math.radians(h1)) - C2 * math.cos(math.radians(h2))
    db = C1 * math.sin(math.radians(h1)) - C2 * math.sin(math.radians(h2))
    return 100 * math.hypot(L1 - L2 if lightness else 0.0, da, db)


def separations(tokens):
    """(failures, closest chart pair, worst painted distance per bar), for one block."""
    bad, closest, worst = [], None, {}
    for kind, ours, suffix, states, bar in ACCENT_BARS:
        for sem in states:
            d = painted(tokens[ours], tokens[f"--hw-{sem}{suffix}"])
            worst[kind] = min(worst.get(kind, d), d)
            if d < bar:
                bad.append(f"{ours}, the accent's {kind}, sits {d:.1f} from --hw-{sem}{suffix}, "
                           f"below {bar} CIEDE2000: an accent that reads as a state")
    d = painted(tokens["--hw-accent-ring"], tokens["--hw-border-strong"])
    worst["ring-border"] = d
    if d < RING_FROM_BORDER:
        bad.append(f"--hw-accent-ring sits {d:.1f} from --hw-border-strong, below "
                   f"{RING_FROM_BORDER} CIEDE2000: a focused control that reads as a bordered one")
    for sem in SEMANTICS[1:]:
        d = painted(tokens[f"--hw-{sem}-quiet"], tokens["--hw-ground"])
        worst["fill-ground"] = min(worst.get("fill-ground", d), d)
        if d < FILL_FROM_GROUND:
            bad.append(f"--hw-{sem}-quiet sits {d:.1f} from --hw-ground, below "
                       f"{FILL_FROM_GROUND} CIEDE2000: a status fill that sinks into the ground")
    for fg in CHARTS:
        for sem in SEMANTICS[1:]:
            d = separation(tokens[fg], tokens[f"--hw-{sem}"])
            if d < CHART_SEPARATION:
                bad.append(f"{fg} sits {d:.1f} from --hw-{sem}, below {CHART_SEPARATION}: a "
                           f"series colour that reads as a state")
    for i, a in enumerate(CHARTS):
        for b in CHARTS[i + 1:]:
            d = separation(tokens[a], tokens[b])
            if closest is None or d < closest[0]:
                closest = (d, a, b)
            if d < CHART_SEPARATION:
                bad.append(f"{a} sits {d:.1f} from {b}, below {CHART_SEPARATION}")
        if i + 1 < len(CHARTS):
            dl = abs(tokens[a][0] - tokens[CHARTS[i + 1]][0])
            if dl < NEIGHBOUR_DL:
                bad.append(f"{a} and {CHARTS[i + 1]} are adjacent series {dl:.3f} apart in "
                           f"lightness, below {NEIGHBOUR_DL}")
    return bad, closest, worst


# A brand's shape and stroke, one of the house's own (12-brand.md). Three radii bound to three
# roles, child never larger than parent, is what a register guarantees; a free triple does not.
REGISTERS = {"crisp": ("2px", "3px", "6px"), "house": ("4px", "6px", "10px"),
             "soft": ("6px", "8px", "14px")}
ICON_STROKES = ("1.5px", "1.75px", "2px")
DECLARATION = re.compile(r"^\s*(--hw-[a-z0-9-]+):\s*([^;]+);")


def root_values(path):
    """The declarations of the file's one unconditional :root block, the theme-free tokens."""
    out, inside = {}, False
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() == ":root {":
            inside = True
        elif inside and line.strip().startswith("}"):
            break
        elif inside and DECLARATION.match(line):
            m = DECLARATION.match(line)
            out[m.group(1)] = m.group(2).strip()
    return out


def geometry(path):
    """(failures, register name) for the shape and stroke a file declares."""
    root = root_values(path)
    radii = tuple(root.get(f"--hw-radius-{s}") for s in ("sm", "md", "lg"))
    register = next((n for n, r in REGISTERS.items() if r == radii), None)
    bad = [] if register else [f"radii sm/md/lg are {'/'.join(map(str, radii))}, which is none of "
                               f"the registers " + ", ".join(f"{n} {'/'.join(r)}"
                                                            for n, r in REGISTERS.items())]
    stroke = root.get("--hw-icon-stroke")
    if stroke not in ICON_STROKES:
        bad.append(f"--hw-icon-stroke is {stroke}, which is none of {', '.join(ICON_STROKES)}")
    return bad, f"{register or 'none'}, stroke {stroke}"


BRAND_LINE = re.compile(r"^\s*Brand: (.+)\.$", re.M)


# The text roles, most prominent first, and the smallest lightness step the default themes keep
# between two of them (0.062 light, 0.068 dark, secondary to muted). Raising the floors pushes
# neighbouring roles toward one bar, and a step under this is one role under two names.
ROLE_LADDER, ROLE_STEP = ["--hw-text", "--hw-text-secondary", "--hw-text-muted"], 0.06
BLOCKS_CERTIFIED = ["light", "dark", "light-more", "dark-more"]


def roles(tokens):
    return [f"{a} and {b} are {abs(tokens[a][0] - tokens[b][0]):.4f} apart in lightness, "
            f"below the {ROLE_STEP} that keeps them two roles"
            for a, b in zip(ROLE_LADDER, ROLE_LADDER[1:])
            if abs(tokens[a][0] - tokens[b][0]) < ROLE_STEP]


# --- pass 1: every ratio the book publishes -------------------------------------------------

TABLES = ["15-color-combinations.md", "10-color.md"]

CELL = re.compile(r"\*{0,2}([0-9]+\.[0-9]+)\*{0,2}$")
COLUMN = re.compile(r"`([a-z0-9-]+)`|^on ([a-z0-9-]+)$")
PAIR_CELL = re.compile(r"^`(hw-[a-z0-9-]+)` on `(hw-[a-z0-9-]+)`$")
TWO_THEME_TOKEN = re.compile(r"^\| `(hw-[a-z0-9-]+)` \| \*{0,2}([0-9.]+)\*{0,2} \| \*{0,2}([0-9.]+)\*{0,2} \|$")
TWO_THEME_PAIR = re.compile(r"^\| `(hw-[a-z0-9-]+)` on `(hw-[a-z0-9-]+)` \| ([0-9.]+) \| ([0-9.]+) \|$")

# Ratios the book states in a sentence rather than in a table, each with the file and line it is
# written on. They are listed rather than parsed because a sentence has no column to key on, and
# they are listed at all because an unguarded published number is the defect this pass exists to
# stop: until 2026-09-21 the chart ratios below, and the disabled table in 60-states.md, were
# certified by nothing.
PROSE = [
    # 15-color-combinations.md:99, 106, and the fill-is-not-a-boundary paragraph at :129
    ("light", "--hw-accent", "--hw-ink", 3.30),
    ("dark", "--hw-accent", "--hw-ink", 3.07),
    ("light", "--hw-border", "--hw-surface", 1.30),
    ("light", "--hw-surface", "--hw-surface-sunken", 1.129),
    ("dark", "--hw-surface", "--hw-surface-sunken", 1.115),
    # 10-color.md:72-74, the focus ring against the surface closest to it in lightness
    ("light", "--hw-accent-ring", "--hw-surface-sunken", 3.05),
    ("dark", "--hw-accent-ring", "--hw-surface-raised", 3.05),
    ("light", "--hw-accent-ring", "--hw-surface-raised", 3.44),
    ("dark", "--hw-accent-ring", "--hw-surface-sunken", 3.70),
    # 10-color.md:78-80 and the table in 70-data-display.md#charts, the six chart fills against
    # each ground and against each theme's worst surface
    *[(t, f"--hw-chart-{i}", f"--hw-{g}", v)
      for t, g, row in (("light", "ground", [3.29, 8.13, 3.62, 8.41, 3.43, 7.55]),
                        ("light", "surface-sunken", [3.10, 7.66, 3.41, 7.93, 3.24, 7.12]),
                        ("dark", "ground", [8.54, 13.62, 7.84, 13.37, 8.18, 14.14]),
                        ("dark", "surface-raised", [7.31, 11.65, 6.71, 11.44, 7.00, 12.10]))
      for i, v in enumerate(row, 1)],
    # 75-spec-sheet.md#ruled, ink on the ruled ground, certified against its rule
    *[(t, f"--hw-{fg}", "--hw-border", v)
      for fg, row in (("text", (12.17, 11.84)), ("text-secondary", (5.23, 5.06)),
                      ("text-muted", (4.01, 3.89)))
      for t, v in zip(("light", "dark"), row)],
    # 60-states.md:75-76, the disabled text table
    *[(t, "--hw-text-disabled", f"--hw-{g}", v)
      for t, row in (("light", [3.21, 3.42, 3.03]), ("dark", [3.51, 3.26, 3.64]))
      for g, v in zip(("ground", "surface", "surface-sunken"), row)],
]


def published_ratios(root):
    """Every numeric cell in the book's ratio tables, as (theme, fg, bg, value).

    Four table shapes across the two files that carry them: a per-theme grid whose header row
    names the grounds, a row inside such a grid keyed on a named pair, a two-column light/dark
    table keyed on one foreground, and a two-column table keyed on a named pair."""
    out = []
    for name in TABLES:
        theme, cols = None, None
        for line in (root / "design" / name).read_text(encoding="utf-8").splitlines():
            if line.startswith("### Light"):
                theme = "light"
            elif line.startswith("### Dark"):
                theme = "dark"
            elif line.startswith("## "):
                theme, cols = None, None
            m = TWO_THEME_TOKEN.match(line)
            if m:
                for t, v in (("light", m.group(2)), ("dark", m.group(3))):
                    out.append((t, "--hw-border-strong", "--" + m.group(1), float(v)))
                continue
            m = TWO_THEME_PAIR.match(line)
            if m:
                for t, v in (("light", m.group(3)), ("dark", m.group(4))):
                    out.append((t, "--" + m.group(1), "--" + m.group(2), float(v)))
                continue
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] in ("ink", "foreground"):
                cols = []
                for c in cells[1:]:
                    m = COLUMN.search(c)
                    cols.append((m.group(1) or m.group(2)) if m else None)
                continue
            if not (theme and cols):
                continue
            m = PAIR_CELL.match(cells[0])
            if m:
                values = [c for c in cells[1:] if CELL.fullmatch(c)]
                if values:
                    out.append((theme, "--" + m.group(1), "--" + m.group(2),
                                float(CELL.fullmatch(values[0]).group(1))))
            elif cells[0].startswith("`hw-"):
                fg = "--" + cells[0].strip("`")
                for g, v in zip(cols, cells[1:]):
                    if g and CELL.fullmatch(v):
                        out.append((theme, fg, "--hw-" + g, float(CELL.fullmatch(v).group(1))))
    return out


# --- pass 5: a product's own colour ---------------------------------------------------------
# What every product colour is held to, declared here rather than read from the product's seed,
# so a product cannot weaken it in the same edit as the value it guards: at least 3:1 on each of
# the six surfaces, and PRODUCT_SEPARATION in hue and chroma from the three states and the
# accent. The seed is read only for what it adds - a pair at a text bar, or a further colour to
# stay clear of.
PRODUCT_APART = [f"--hw-{s}" for s in SEMANTICS]
# In hue and chroma alone, with lightness left out, because a product colour's anchors are its
# own and a maroon clears any reading that counts lightness while still reading as red
# (95-extending.md#why-the-separation-leaves-lightness-out).
PRODUCT_SEPARATION = 8.0


def raised(bar):
    return max(bar, MORE_BAR[AA]) if bar >= AA else MORE_BAR[NON_TEXT]


def finite_bar(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def extension_shape(ext):
    """Every way a product seed's raw JSON cannot be trusted, checked once at the boundary so
    the measuring code after it can index the seed freely."""
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
        name = "--" + e["name"]
        floors = e.get("floors", [])
        if not isinstance(floors, list):
            bad.append(f"{name} has floors {floors!r}, which is not a list")
        else:
            for floor in floors:
                if not isinstance(floor, dict):
                    bad.append(f"{name} carries a floor {floor!r} that is not an object")
                    continue
                if not finite_bar(floor.get("bar")):
                    bad.append(f"{name} carries a floor with bar {floor.get('bar')!r}, which "
                               f"is not a finite number")
                on = floor.get("on", [])
                if not (isinstance(on, list) and all(isinstance(g, str) for g in on)):
                    bad.append(f"{name} carries a floor on {on!r}, which is not a list of "
                               f"house colour names")
        apart = e.get("apart", [])
        if not (isinstance(apart, list) and all(isinstance(a, str) for a in apart)):
            bad.append(f"{name} has apart {apart!r}, which is not a list of house colour "
                       f"names")
    return bad


def load_extension(seed_path, css_arg):
    """The one entry point for a product seed: read it, parse it, validate its shape and
    every leaf, and resolve and check its built CSS exists - all before any other --extend
    code touches the seed or the path. (failures, ext, css path)."""
    try:
        text = seed_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{seed_path} could not be read: {exc.strerror or exc}"], None, None
    try:
        ext = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"{seed_path} is not valid JSON: {exc}"], None, None
    shape = extension_shape(ext)
    if shape:
        return shape, None, None
    css = Path(css_arg) if css_arg else seed_path.parent / (ext["namespace"] + ".tokens.css")
    if not css.exists():
        return [f"{css} does not exist; run tools/build.py --extend {seed_path} first"], None, None
    return [], ext, css


def extension(themes, ext, seed_path, css_path):
    """(failures, report lines) for one product's seed and the CSS already resolved and
    confirmed to exist by load_extension."""
    prod = parse_tokens(css_path)
    bad, report = [], []
    ns = ext["namespace"]
    for block, tokens in prod.items():
        for token in tokens:
            if token.startswith("--hw-"):
                bad.append(f"{block} {token} is redefined by {Path(css_path).name}, and a product "
                           f"can never redefine an hw- token")
            elif not token.startswith(f"--{ns}-"):
                bad.append(f"{block} {token} is outside the --{ns}- namespace")
    for e in ext["color"]["tokens"]:
        name = "--" + e["name"]
        pairs = {s: NON_TEXT for s in SURFACES}
        for floor in e.get("floors", []):
            bar = floor["bar"]
            if bar != NON_TEXT and bar < AA:
                bad.append(f"{name} claims {bar}:1, which certifies nothing this file holds")
                continue
            for g in floor["on"]:
                pairs[f"--hw-{g}"] = max(pairs.get(f"--hw-{g}", 0), bar)
        apart = sorted(set(PRODUCT_APART) | {"--" + a for a in e.get("apart", [])})
        for theme in BLOCKS_CERTIFIED:
            fg = prod[theme].get(name)
            if fg is None:
                bad.append(f"{theme} {name} is declared in {Path(seed_path).name} and not in "
                           f"{Path(css_path).name}")
                continue
            if not in_gamut(*fg):
                bad.append(f"{theme} {name} oklch{fg} falls outside sRGB")
            worst = None
            for bg, base in pairs.items():
                bar = raised(base) if theme.endswith("-more") else base
                if bg not in themes[theme]:
                    bad.append(f"{theme} {name} is claimed on {bg}, which the house does not "
                               f"declare")
                    continue
                got, got8 = ratio(fg, themes[theme][bg])
                if got < bar or got8 < bar:
                    bad.append(f"{theme} {name} on {bg}: {got:.3f} ({got8:.3f} at 8-bit), below "
                               f"{bar}, {hexof(*fg)} on {hexof(*themes[theme][bg])}")
                if worst is None or got < worst[0]:
                    worst = (got, got8, bg)
            bad += [f"{theme} {name} is held apart from {a}, which the house does not declare"
                    for a in apart if a not in themes[theme]]
            valid_apart = [a for a in apart if a in themes[theme]]
            seps = sorted((separation(fg, themes[theme][a], lightness=False), a)
                          for a in valid_apart)
            bad += [f"{theme} {name} sits {d:.1f} from {a} in hue and chroma, below "
                    f"{PRODUCT_SEPARATION}: a product colour that reads as a house state"
                    for d, a in seps if d < PRODUCT_SEPARATION]
            if seps:
                report.append(f"  {name} {theme:10} {hexof(*fg)}  worst {worst[0]:.3f} (8-bit "
                              f"{worst[1]:.3f}) on {worst[2]}; closest {seps[0][0]:.1f} to "
                              f"{seps[0][1]}")
            else:
                report.append(f"  {name} {theme:10} {hexof(*fg)}  worst {worst[0]:.3f} (8-bit "
                              f"{worst[1]:.3f}) on {worst[2]}; no house colour to measure "
                              f"separation against")
    for copy, block in (("media-dark", "dark"), ("media-dark-more", "dark-more")):
        if prod[copy] != prod[block]:
            bad.append(f"the {copy} block of {Path(css_path).name} differs from {block}")
    return bad, report


def main(argv):
    ap = argparse.ArgumentParser(prog="contrast.py", description=__doc__.split("\n")[0])
    ap.add_argument("css", nargs="?", default=str(ROOT / "tokens" / "tokens.css"))
    ap.add_argument("--extend", metavar="SEED", help="also verify this product seed's tokens")
    ap.add_argument("--extend-css", metavar="FILE",
                    help="the product's built CSS, if not <namespace>.tokens.css beside the seed")
    opts = ap.parse_args(argv[1:])
    path = opts.css
    themes = parse_tokens(path)
    failures = []

    m = BRAND_LINE.search(Path(path).read_text(encoding="utf-8"))
    brand = m.group(1) if m else "not named in the header"
    if brand == "house":
        claims = published_ratios(ROOT) + PROSE
        for theme, fg, bg, want in claims:
            got, _ = ratio(themes[theme][fg], themes[theme][bg])
            # The book prints two or three decimals, so a cell is reproduced when it rounds back
            # to what is written. 0.011 is half a unit in the last place of a two-decimal cell.
            if abs(got - want) > 0.011:
                failures.append(f"published {theme} {fg} on {bg}: book says {want}, "
                                f"this file computes {got:.3f}")
        print(f"pass 1: {len(claims)} published ratios re-derived from "
              f"{', '.join('design/' + t for t in TABLES)} and the prose list, "
              f"{len(failures)} mismatched")
    else:
        print(f"pass 1: skipped. This set's brand is {brand}; the published ratios were "
              f"measured on the house set and do not describe it.")

    checked, worst = 0, {}
    for base, fg, bg, why in required():
        for theme in BLOCKS_CERTIFIED:
            bar = MORE_BAR[base] if theme.endswith("-more") else base
            for token in (fg, bg):
                if token not in themes[theme]:
                    failures.append(f"{theme} {token} is certified and is not in {path}")
            if fg not in themes[theme] or bg not in themes[theme]:
                continue
            got, got8 = ratio(themes[theme][fg], themes[theme][bg])
            checked += 1
            # No tolerance on either reading. WCAG states its thresholds without rounding, and a
            # tolerance is how 2.9953 came to be published as 3.00.
            if got < bar:
                failures.append(f"{theme} {fg} on {bg}: {got:.3f} below {bar} ({why})")
            elif got8 < bar:
                failures.append(f"{theme} {fg} on {bg}: {got:.3f} clears {bar} but reads "
                                f"{got8:.3f} at 8-bit, {hexof(*themes[theme][fg])} on "
                                f"{hexof(*themes[theme][bg])} ({why})")
            key = ("text" if base >= AA else "nontext", theme)
            if key not in worst or got < worst[key][0]:
                worst[key] = (got, got8, fg, bg)
    for bar, fg, bg, why in refused():
        for theme in ("light", "dark"):
            got, got8 = ratio(themes[theme][fg], themes[theme][bg])
            checked += 1
            if got >= bar or got8 >= bar:
                failures.append(f"{theme} {fg} on {bg}: {got:.3f} now clears {bar}, and the book "
                                f"still refuses it ({why})")
    print(f"pass 2: {checked} certified pairs checked against AA {AA}:1 and non-text "
          f"{NON_TEXT}:1, and under prefers-contrast: more against {MORE_BAR[AA]}:1 and "
          f"{MORE_BAR[NON_TEXT]}:1, on the float value and at 8-bit, "
          f"{2 * len(list(refused()))} of them asserted below their bar")
    for (kind, theme), (got, got8, fg, bg) in sorted(worst.items()):
        print(f"  worst {kind:8} {theme:10} {got:6.3f} (8-bit {got8:6.3f})  {fg} on {bg}")

    for theme in BLOCKS_CERTIFIED:
        bad, (d, a, b), w = separations(themes[theme])
        bad += roles(themes[theme])
        failures += [f"{theme} {f}" for f in bad]
        print(f"pass 3: {theme:10} {len(bad)} below bar; accent ink {w['ink']:.1f}, fill "
              f"{w['fill']:.1f}, ring {w['ring']:.1f}; ring from border {w['ring-border']:.1f}; "
              f"state fill from ground {w['fill-ground']:.1f}; closest chart pair {d:.1f}, "
              f"{a[5:]} / {b[5:]}")
    bad, shape = geometry(path)
    failures += bad
    print(f"pass 3: shape register {shape}, {len(bad)} outside the house's own")

    for theme in BLOCKS_CERTIFIED:
        for token, (L, C, H) in sorted(themes[theme].items()):
            if not in_gamut(L, C, H):
                failures.append(f"{theme} {token} oklch({L} {C} {H}) falls outside sRGB")
    for copy, block in (("media-dark", "dark"), ("media-dark-more", "dark-more")):
        if themes[copy] != themes[block]:
            diff = sorted(set(themes[block].items()) ^ set(themes[copy].items()))
            failures.append(f"the {copy} block differs from {block} in {len(diff)} "
                            f"declaration(s): " + ", ".join(t for t, _ in diff[:6]))
    print(f"pass 4: {sum(len(themes[t]) for t in BLOCKS_CERTIFIED)} tokens inside sRGB; "
          f"media-dark agrees with dark on {len(themes['media-dark'])} declarations and "
          f"media-dark-more with dark-more on {len(themes['media-dark-more'])}")

    if opts.extend:
        seed = Path(opts.extend)
        extend_failures, ext, css = load_extension(seed, opts.extend_css)
        if extend_failures:
            failures += extend_failures
            print(f"pass 5: {seed} could not be verified; {len(extend_failures)} failed")
        else:
            bad, report = extension(themes, ext, seed, css)
            failures += bad
            print(f"pass 5: {Path(css).name} against this set, every token 3:1 or its "
                  f"claimed bar on all six surfaces and {PRODUCT_SEPARATION} in hue and chroma "
                  f"from the "
                  f"states and the accent; {len(bad)} failed")
            print("\n".join(report))

    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
