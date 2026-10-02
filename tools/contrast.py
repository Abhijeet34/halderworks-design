#!/usr/bin/env python3
"""Re-derive and verify this system's contrast claims from the files tools/ramps.py writes.

This is the SECOND instrument, and two things make it one rather than a second reading of the
first. It shares no line of arithmetic with tools/ramps.py: the conversion here is the CSS
Color 4 reference path (w3c/csswg-drafts css-color-4/conversions.js, OKLab_to_LMS, LMS_to_XYZ
and XYZ_to_lin_sRGB as exact rationals), which is what a browser implements, while ramps.py uses
Ottosson's published Oklab constants. And the floors and pairs it requires are declared here,
not imported from ramps.py, so a floor cannot be weakened in the same edit as the value it
guards. Until 2026-09-21 neither held for the solver this replaced: it imported this file's
converter, and its seed carried the floors, so deleting a floor and moving its value was one edit
that no tool refused.

The principle both instruments are built to: MEASURE THE ARTIFACT, NEVER THE INTENT. A number
that was not re-measured in the exact form it will ship has not been certified.

Per brand and theme, against WCAG AA 4.5:1 for text and 1.4.11's 3:1 for a control boundary,
with no tolerance and each pair measured twice, on the unquantized value and on the 8-bit sRGB
value a display receives (a pair that clears 3:1 on floats and reads 2.999 in hex is not a pair
any third-party checker will agree about):

  1. Every step floor: 8 at 3:1 on steps 1-3 of every ramp, 11 at 4.5:1 and 12 at 13:1 on steps
     1-5, a hue's 12 at 7:1, and the label on solids 9 and 10 at 4.5:1.
  2. Every role in ramps/roles.css on the grounds it is read on, at its step's floor, and under
     prefers-contrast: more at the raised bar: 7:1 for text and 4.5:1 for a mark. A line it
     cannot read, or a role certified by nothing and exempted nowhere, is a failure.
  3. The CIEDE2000 bars, on the 8-bit value: the accent fill apart from the three state fills,
     the primary from the danger solid, the focus ring from the error and from a control's own
     edge, each state's fill from the ground, each status word from the text, and the six chart
     series apart from each other and from the three states, with what a dichromat sees of them
     reported. The text roles keep a visible lightness step. A brand's shape register, icon
     stroke and display width are one of the house's own.
  4. Every colour is inside sRGB, and each dark block a user with no explicit choice actually
     gets, through a prefers-color-scheme query, is identical to the explicit one.

    python3 tools/contrast.py [ramps/tokens/NAME.tokens.css ...]   # default: every brand
"""
import argparse
import math
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- the converter: the CSS Color 4 reference path -----------------------------------------
# Exact rationals for XYZ -> linear sRGB, as conversions.js carries them, so white comes back as
# exactly 1.000000 here; tools/ramps.py goes straight from LMS to linear sRGB on Ottosson's
# rounded constants instead, and tests/invariants.py bounds how far the two may disagree.

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
# white. The difference formula is Sharma, Wu and Dalal 2005, written here in their numbered
# steps, and tests/invariants.py holds it to the paper's own test pairs.

LIN_SRGB_TO_XYZ = tuple(tuple(float(x) for x in row) for row in (
    (F(506752, 1228815), F(87881, 245763), F(12673, 70218)),
    (F(87098, 409605), F(175762, 245763), F(12673, 175545)),
    (F(7918, 409605), F(87881, 737289), F(1001167, 1053270))))
D65 = (0.3127 / 0.3290, 1.0, (1.0 - 0.3127 - 0.3290) / 0.3290)


def lab(fg, seen=None):
    """CIELAB (D65) of an oklch triple as the display receives it, quantized to 8 bits, or of
    what a dichromat sees of it when `seen` is one of DICHROMACY's matrices."""
    return lab_rgb(quantize(oklch_to_rgb(*fg)), seen)


def lab_rgb(rgb, seen=None):
    """CIELAB (D65) of gamma-encoded sRGB in 0..1, such as a pixel tools/painted.py read."""
    lin = [_lin(c) for c in rgb]
    if seen:
        lin = [min(max(v, 0.0), 1.0) for v in _mul(seen, lin)]
    xyz = _mul(LIN_SRGB_TO_XYZ, lin)
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


# Machado, Oliveira and Fernandes 2009, severity 1.0, on linear sRGB: the paper's table. What a
# dichromat sees of the chart series is reported and never refused on (70-data-display.md).
DICHROMACY = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900))}


def dichromat_painted(a, b):
    """(CIEDE2000, kind) for the dichromacy under which two oklch colours come closest."""
    return min((de2000(lab(a, m), lab(b, m)), kind) for kind, m in DICHROMACY.items())



# --- what this system certifies ------------------------------------------------------------

AA, NON_TEXT = 4.5, 3.0
# prefers-contrast: more raises text to WCAG 2.2 SC 1.4.6's 7:1. SC 1.4.11 has no enhanced level,
# so a non-text pair is raised to 4.5:1, the next bar this file already holds.
MORE_BAR = {AA: 7.0, NON_TEXT: AA}


def raised(bar):
    return max(bar, MORE_BAR[AA]) if bar >= AA else MORE_BAR[NON_TEXT]


# The CIEDE2000 bars, each the maintainer's decision (10-color.md#the-three-bars-the-accent-is-held-to):
# the selected fill from a state's fill, the primary from the danger solid, the ring from the
# error, the ring from a control's own edge, and a state's fill from the ground.
FILL_FROM_STATE, PRIMARY_FROM_DANGER, RING_FROM_DANGER = 5, 14, 17
RING_FROM_BORDER, FILL_FROM_GROUND = 14, 6
CHARTS = [f"--hw-chart-{n}" for n in range(1, 7)]
# The smallest lightness step between primary and muted text, below which two roles read as one.
ROLE_STEP = 0.06
# A brand's shape and stroke, one of the house's own: three radii bound to three roles, child
# never larger than parent, is what a register guarantees; a free triple does not.
REGISTERS = {"crisp": ("2px", "3px", "6px"), "house": ("4px", "6px", "10px"),
             "moulded": ("4px", "7px", "12px"), "soft": ("6px", "8px", "14px")}
ICON_STROKES = ("1.5px", "1.75px", "2px")
FACES = ("--hw-font-sans", "--hw-font-display", "--hw-font-read", "--hw-font-mono")
DISPLAY_STRETCHES = ("100%", "125%")   # the normal width, and Archivo Expanded's
# The ramps every brand carries: the neutral, the five roles.css names and the six chart series.
# Any other is the brand's own, reported against the three state ramps below.
STATE_RAMPS = ("red", "amber", "green")
HOUSE_RAMPS = ("gray", "accent", "mark", *STATE_RAMPS, "teal", "blue", "violet", "pink", "olive",
               "sky")


# --- the ramps: tools/ramps.py's files and ramps/roles.css ----------------------------------
# What the ramps claim, declared again here rather than imported from tools/ramps.py: a floor
# cannot be weakened in the same edit as the step it guards. Floors are those of ramps.py's
# docstring; a role is held to the floor of the step it names, and under prefers-contrast: more
# to raised() of it.

RAMPS_DIR = ROOT / "ramps"
STEP_FLOORS = {8: (NON_TEXT, (1, 2, 3)), 11: (AA, (1, 2, 3, 4, 5)), 12: (13.0, (1, 2, 3, 4, 5))}
# A hue's step 12 is read only as text under more, so it holds that bar and not the gray's 13:1.
HUE_STEP_12 = MORE_BAR[AA]
SOLIDS = (9, 10)
RAMP_BLOCKS = {(None, ":root"): "brand",
               (None, ':root, [data-theme="light"]'): "light", (None, '[data-theme="dark"]'): "dark",
               ("@media (prefers-color-scheme: dark)", ':root:not([data-theme="light"])'):
               "media-dark"}
ROLE_BLOCKS = {(None, ":root"): "base", (None, '[data-theme="dark"]'): "dark",
               ("@media (prefers-color-scheme: dark)", ':root:not([data-theme="light"])'):
               "media-dark", ("@media (prefers-contrast: more)", ":root"): "more",
               ("@media (prefers-contrast: more)", '[data-theme="dark"]'): "dark-more",
               ("@media (prefers-contrast: more) and (prefers-color-scheme: dark)",
                ':root:not([data-theme="light"])'): "media-dark-more"}
# A step-8 role holds 3:1 on steps 1 to 3 only, so it is certified on the grounds at or beyond them.
ROLE_GROUNDS = ["--hw-bg", "--hw-bg-subtle", "--hw-surface", "--hw-surface-raised", "--hw-fill"]
ROLE_FILLS = ["--hw-fill-hover", "--hw-fill-active"]
ROLE_TINTS = ["--hw-accent-fill", "--hw-success-fill", "--hw-warning-fill", "--hw-danger-fill",
              "--hw-insert-fill", "--hw-delete-fill", "--hw-mark-quiet"]
ROLE_TEXT = {"--hw-text": 13.0, "--hw-text-muted": AA, "--hw-accent-text": AA,
             "--hw-success": AA, "--hw-warning": AA, "--hw-danger": AA, "--hw-insert": AA,
             "--hw-delete": AA}
ROLE_EDGES = ["--hw-line-strong", "--hw-focus", "--hw-ink"]
# Disabled text is exempt from 1.4.3 and held to 3:1 in both tiers rather than raised.
ROLE_DISABLED = "--hw-text-disabled"
ROLE_LABELS = {"--hw-on-ink": ("--hw-ink", "--hw-ink-hover"),
               "--hw-on-accent": ("--hw-accent", "--hw-accent-hover"),
               "--hw-on-danger": ("--hw-danger-solid", "--hw-danger-hover"),
               "--hw-on-mark": ("--hw-mark",)}
# Roles no pair reads as a foreground, each with why. A role in neither list is refused, so a new
# role cannot land certified by nothing.
ROLE_EXEMPT = {"--hw-line": "a divider, never a control boundary",
               "--hw-accent-line": "a tint's edge, beside a word", "--hw-success-line": "same",
               "--hw-warning-line": "same", "--hw-danger-line": "same",
               "--hw-scrim": "translucent, never read on"}

# The CIEDE2000 bars of pass 3, carried onto the roles: (what, ours, theirs, bar, what it reads
# as below the bar). The accent fill is the old selected-row bar, the one an accent at a state's
# hue fails first. The primary bar holds --hw-ink, the primary action, and not the accent solid,
# as pass 3 holds --hw-ink and not --hw-brand.
STATE_FILLS = ("--hw-success-fill", "--hw-warning-fill", "--hw-danger-fill")
# A status word keeps its hue against the text beside it in every tier, the bar a product colour
# keeps from a state: under more in dark every step 12 sat near white, 2.1 from --hw-text.
STATE_TEXT = ("--hw-danger", "--hw-warning", "--hw-success", "--hw-delete", "--hw-insert")
STATE_FROM_TEXT = 14
ROLE_BARS = [("fill", "--hw-accent-fill", s, FILL_FROM_STATE, "a brand fill that reads as a state")
             for s in STATE_FILLS] + [
    ("primary", "--hw-ink", "--hw-danger-solid", PRIMARY_FROM_DANGER, "a primary that reads as danger"),
    ("ring", "--hw-focus", "--hw-danger", RING_FROM_DANGER, "a focus ring that reads as an error"),
    ("ring-border", "--hw-focus", "--hw-line-strong", RING_FROM_BORDER,
     "a focused control that reads as a bordered one")] + [
    ("fill-ground", s, "--hw-bg", FILL_FROM_GROUND, "a status fill that sinks into the ground")
    for s in STATE_FILLS] + [
    ("state-text", s, "--hw-text", STATE_FROM_TEXT, "a status word in the text's own colour")
    for s in STATE_TEXT]
ROLE_INK_REPORTED = ("--hw-accent-text", ("--hw-success", "--hw-warning", "--hw-danger"))
# A chart series is a mark: 1.4.11's 3:1 on every ground a chart is drawn on, the raised bar under
# more, and held CHART_APART from every other series and every state ink, the bar a product colour
# keeps from a state. Six hues cannot all survive a dichromacy (Machado 2009 puts the closest pair
# near 3), so that is reported and the word beside a series carries it (70-data-display.md).
CHART_APART = 14
ROLE_BARS += [("chart", a, b, CHART_APART, "two series that read as one")
              for i, a in enumerate(CHARTS) for b in CHARTS[i + 1:]] + [
    ("chart-state", c, s, CHART_APART, "a series that reads as a state")
    for c in CHARTS for s in ROLE_INK_REPORTED[1]]

WHITE_OKLCH = (1.0, 0.0, 0.0)   # the reference path returns #FFFFFF from this exactly
RAMP_DECL = re.compile(r"^(--hw-[a-z][a-z0-9-]*):\s*(.+?);$")
RAMP_STEP = re.compile(r"^--hw-([a-z][a-z0-9]*)-(\d+|on-solid)$")
OKLCH = re.compile(r"^oklch\(([0-9.]+) ([0-9.]+) ([0-9.]+)(?: / [0-9.]+)?\)$")
RELATIVE = re.compile(r"^oklch\(from var\((--[a-z0-9-]+)\) calc\(l ([+-]) ([0-9.]+)\) c h\)$")
VAR = re.compile(r"^var\((--[a-z0-9-]+)\)$")


def declarations(path, known):
    """({block: {name: raw value}}, failures) for a CSS file whose every block is in `known`.
    Anything else inside a block, a repeated name or an unknown block is a failure: these files
    are generated or hand-held to one shape, and a line this cannot read is one it did not measure."""
    text = re.sub(r"/\*.*?\*/", "", Path(path).read_text(encoding="utf-8"), flags=re.S)
    blocks, bad, stack, name = {}, [], [], Path(path).name
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s:
            continue
        if s.endswith("{"):
            stack.append(s[:-1].strip())
            if not s.startswith("@media"):
                media = stack[-2] if len(stack) > 1 else None
                if (media, stack[-1]) not in known:
                    bad.append(f"{name}:{n}: a block this does not certify: {media or ''} {s}")
            continue
        if s == "}":
            if stack:
                stack.pop()
            continue
        key = known.get((stack[-2] if len(stack) > 1 else None, stack[-1])) if stack else None
        m = RAMP_DECL.match(s)
        if key is None or not m:
            bad.append(f"{name}:{n}: cannot read {s!r}")
            continue
        block = blocks.setdefault(key, {})
        if m[1] in block:
            bad.append(f"{name}:{n}: {m[1]} declared twice in one block")
        block[m[1]] = m[2]
    return blocks, bad


def resolve(name, env, seen=()):
    """An oklch triple for `name` in env, following var() and the one relative form roles.css
    uses, or ValueError saying why it cannot be measured."""
    if name in seen:
        raise ValueError(f"{name} refers to itself through {' -> '.join(seen)}")
    if name not in env:
        raise ValueError(f"{name} is not declared")
    v = env[name]
    if m := OKLCH.match(v):
        return tuple(float(x) for x in m.groups())
    if v.upper() in ("#FFFFFF", "#FFF"):
        return WHITE_OKLCH
    if m := VAR.match(v):
        return resolve(m[1], env, (*seen, name))
    if m := RELATIVE.match(v):
        L, C, h = resolve(m[1], env, (*seen, name))
        return (L - float(m[3]) if m[2] == "-" else L + float(m[3]), C, h)
    raise ValueError(f"{name} is {v!r}, a form this instrument does not convert")


def ramp_steps(block):
    """{ramp: {step: raw}} and the failures of shape: every ramp twelve steps and a label."""
    ramps, bad = {}, []
    for name, value in block.items():
        m = RAMP_STEP.match(name)
        if not m:
            bad.append(f"{name} is not a ramp step")
            continue
        ramps.setdefault(m[1], {})[m[2]] = value
    want = {str(i) for i in range(1, 13)} | {"on-solid"}
    bad += [f"--hw-{r} declares {sorted(s, key=lambda k: (len(k), k))}, not steps 1 to 12 and "
            f"on-solid" for r, s in ramps.items() if set(s) != want]
    if "gray" not in ramps:
        bad.append("no gray ramp")
    return ramps, bad


def brand_shape(block):
    """(failures, register) for a brand's own block: its four faces and the display width, and
    radii and an icon stroke that are one of the house's own."""
    owned = (*FACES, "--hw-font-display-stretch", "--hw-radius-sm", "--hw-radius-md",
             "--hw-radius-lg", "--hw-icon-stroke")
    bad = [f"the brand block names no {k}" for k in owned if k not in block]
    bad += [f"{k} is in the brand block, which carries faces, the display width, radii and the icon stroke only"
            for k in sorted(set(block) - set(owned))]
    if bad:
        return bad, None
    radii = tuple(block[f"--hw-radius-{s}"] for s in ("sm", "md", "lg"))
    register = next((n for n, r in REGISTERS.items() if r == radii), None)
    if register is None:
        bad.append(f"radii {' '.join(radii)} are none of the house's registers: "
                   + "; ".join(f"{n} {' '.join(r)}" for n, r in REGISTERS.items()))
    if block["--hw-font-display-stretch"] not in DISPLAY_STRETCHES:
        bad.append(f"--hw-font-display-stretch is {block['--hw-font-display-stretch']}, which is "
                   f"none of {', '.join(DISPLAY_STRETCHES)}")
    if block["--hw-icon-stroke"] not in ICON_STROKES:
        bad.append(f"--hw-icon-stroke is {block['--hw-icon-stroke']}, which is none of "
                   f"{', '.join(ICON_STROKES)}")
    return bad, register


def certify_ramps(tokens_path, roles_path=RAMPS_DIR / "roles.css", pairs=None):
    """(failures, report lines) for one tools/ramps.py file and ramps/roles.css over it. A list
    passed as `pairs` receives every pair certified, as (tier, fg, bg, bar, "ratio" | "de2000")
    with custom property names, so tools/painted.py renders exactly these and no copy of them."""
    rb, bad = declarations(tokens_path, RAMP_BLOCKS)
    lb, rbad = declarations(roles_path, ROLE_BLOCKS)
    bad += rbad
    for b in ("brand", "light", "dark", "media-dark"):
        if b not in rb:
            bad.append(f"{Path(tokens_path).name} has no {b} block")
    if bad or "base" not in lb:
        return bad + ([] if "base" in lb else ["roles.css has no :root block"]), []
    if rb["media-dark"] != rb["dark"]:
        bad.append("the prefers-color-scheme: dark block of the ramps differs from "
                   "[data-theme=\"dark\"]")
    if lb.get("media-dark") != lb.get("dark"):
        bad.append("roles.css's prefers-color-scheme: dark overrides differ from "
                   "[data-theme=\"dark\"]'s")
    if lb.get("media-dark-more") != lb.get("dark-more"):
        bad.append("roles.css's prefers-color-scheme: dark overrides under more differ from "
                   "[data-theme=\"dark\"]'s")
    sbad, register = brand_shape(rb["brand"])
    bad += sbad
    report, lowest = [], {}
    used = {*ROLE_GROUNDS, *ROLE_FILLS, *ROLE_TINTS, *ROLE_EDGES, *ROLE_TEXT, ROLE_DISABLED, *CHARTS,
            *ROLE_LABELS, *(f for fs in ROLE_LABELS.values() for f in fs),
            *(n for bar in ROLE_BARS for n in bar[1:3])}

    def low(key, got, where):
        if key not in lowest or got < lowest[key][0]:
            lowest[key] = (got, where)

    def certified(tier, fg, bg, bar, kind):
        if pairs is not None:
            pairs.append((tier, *(n if n.startswith("--") else f"--hw-{n}" for n in (fg, bg)),
                          bar, kind))

    def measure(fg, bg, bar, key, where, a, b, tier):
        certified(tier, fg, bg, bar, "ratio")
        got, got8 = ratio(a, b)
        low(key, min(got, got8), where)
        if got < bar or got8 < bar:
            bad.append(f"{where}: {fg} on {bg} is {got:.3f} ({got8:.3f} at 8-bit), below {bar}, "
                       f"{hexof(*a)} on {hexof(*b)}")

    for theme in ("light", "dark"):
        ramps, shape = ramp_steps(rb[theme])
        bad += [f"{theme} {x}" for x in shape]
        if shape:
            continue
        env = dict(rb[theme])
        steps = {}
        for r, s in ramps.items():
            for k in s:
                try:
                    steps[(r, k)] = resolve(f"--hw-{r}-{k}", env)
                except ValueError as e:
                    bad.append(f"{theme} {e}")
        if len(steps) != 13 * len(ramps):
            continue
        for (r, k), c in steps.items():
            if not in_gamut(*c):
                bad.append(f"{theme} --hw-{r}-{k} oklch{c} falls outside sRGB")
        for step, (floor, span) in STEP_FLOORS.items():
            for r in ramps:
                bar = HUE_STEP_12 if step == 12 and r != "gray" else floor
                for g in ramps:
                    for i in span:
                        measure(f"{r}-{step}", f"{g}-{i}", bar, step, f"{theme} step {step}",
                                steps[(r, str(step))], steps[(g, str(i))], theme)
        # A brand's own hue (quoth's live orange, the house pencil) is reported against the three
        # states, never refused: the solver's product-colour pass held one 14 apart, which the
        # live ramp misses against amber, and a product painting it keeps the word beside it.
        for r in set(ramps) - set(HOUSE_RAMPS):
            low("own hue from a state, reported", *min(
                (painted(steps[(r, k)], steps[(st, k)]), f"{theme} {r}-{k} and {st}-{k}")
                for k in ("8", "11") for st in STATE_RAMPS))
        for r in ramps:
            for i in SOLIDS:
                measure(f"{r}-on-solid", f"{r}-{i}", AA, "label", f"{theme} solid label",
                        steps[(r, "on-solid")], steps[(r, str(i))], theme)
        for more in (False, True):
            tier = theme + ("-more" if more else "")
            dark = theme == "dark"
            roles = {**lb["base"], **(lb.get("dark", {}) if dark else {}),
                     **(lb.get("more", {}) if more else {}),
                     **(lb.get("dark-more", {}) if dark and more else {})}
            env = {**rb[theme], **roles}
            bad += [f"{tier} {r} is in roles.css and certified by nothing; certify it or name it "
                    f"in ROLE_EXEMPT" for r in sorted(roles) if r not in used | set(ROLE_EXEMPT)]
            col = {}
            for r in sorted(used | set(roles)):
                try:
                    col[r] = resolve(r, env)
                except ValueError as e:
                    bad.append(f"{tier} {e}")
                    continue
                if not in_gamut(*col[r]):
                    bad.append(f"{tier} {r} oklch{col[r]} falls outside sRGB")
            if not used <= set(col):
                continue

            def bar_of(b):
                return raised(b) if more else b
            for fg, floor in ROLE_TEXT.items():
                for bg in ROLE_GROUNDS + ROLE_FILLS + ROLE_TINTS:
                    measure(fg, bg, bar_of(floor), "role text", tier, col[fg], col[bg], tier)
            for fg in ROLE_EDGES:
                for bg in ROLE_GROUNDS:
                    measure(fg, bg, bar_of(NON_TEXT), "role edge", tier, col[fg], col[bg], tier)
            for fg in CHARTS:
                for bg in ROLE_GROUNDS:
                    measure(fg, bg, bar_of(NON_TEXT), "chart mark", tier, col[fg], col[bg], tier)
            for bg in ROLE_GROUNDS:
                measure(ROLE_DISABLED, bg, NON_TEXT, "role edge", tier, col[ROLE_DISABLED], col[bg],
                        tier)
            for fg, fills in ROLE_LABELS.items():
                for bg in fills:
                    measure(fg, bg, bar_of(AA), "role label", tier, col[fg], col[bg], tier)
            for what, a, b, bar, reads in ROLE_BARS:
                certified(tier, a, b, bar, "de2000")
                d = painted(col[a], col[b])
                if d < bar:
                    bad.append(f"{tier}: {a} sits {d:.1f} CIEDE2000 from {b} at 8-bit, below "
                               f"{bar}: {reads}")
                else:
                    low(what, d, tier)
            ink, states = ROLE_INK_REPORTED
            low("ink, reported", min(painted(col[ink], col[s]) for s in states), tier)
            d, kind, a, b = min((*dichromat_painted(col[a], col[b]), a, b)
                                for i, a in enumerate(CHARTS) for b in CHARTS[i + 1:])
            low("chart to a dichromat, reported", d, f"{tier}, {kind}, {a} and {b}")
            # roles.css raises muted text to step 12 under more, so the ladder is reported there.
            step = abs(col["--hw-text"][0] - col["--hw-text-muted"][0])
            if not more and step < ROLE_STEP:
                bad.append(f"{tier} --hw-text and --hw-text-muted are {step:.4f} apart in "
                           f"lightness, below the {ROLE_STEP} that keeps them two roles")
            elif more:
                low("ladder under more, reported", step, tier)
    report.insert(0, "  lowest: " + "; ".join(f"{k} {v[0]:.2f} ({v[1]})" for k, v in lowest.items()))
    report.insert(1, f"  shape: the {register} register, icon stroke {rb['brand'].get('--hw-icon-stroke')}")
    return bad, report


def main_ramps(paths):
    paths = [Path(p) for p in paths] or sorted((RAMPS_DIR / "tokens").glob("*.tokens.css"))
    failures = []
    if not paths:
        failures.append(f"no *.tokens.css in {RAMPS_DIR / 'tokens'}")
    for path in paths:
        if not path.is_file():
            failures.append(f"{path} does not exist; build it with tools/ramps.py first")
            continue
        try:
            bad, report = certify_ramps(path)
        except (OSError, UnicodeDecodeError) as e:
            failures.append(f"{path} could not be read: {e}")
            continue
        failures += [f"{path.name.removesuffix('.tokens.css')}: {f}" for f in bad]
        print(f"ramps {path.name}: every step floor and solid label, every role in "
              f"roles.css in light, dark and both under prefers-contrast: more, float and "
              f"8-bit, and the brand's shape; {len(bad)} failed")
        print("\n".join(report))
    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(failures)} failures")
    return 1 if failures else 0




def main(argv):
    ap = argparse.ArgumentParser(prog="contrast.py", description=__doc__.split("\n")[0])
    ap.add_argument("tokens", nargs="*", help="tools/ramps.py files (default every "
                                             "ramps/tokens/*.tokens.css)")
    return main_ramps(ap.parse_args(argv[1:]).tokens)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
