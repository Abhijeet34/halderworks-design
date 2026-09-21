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
  3. The six chart colours are told apart from the three semantics and from each other, and
     neighbours alternate in lightness. A chart hue is the accent plus a fixed rotation while
     the semantics stay put, so a collision moves around the wheel with every accent rebuild;
     until 2026-09-21 nothing measured it and three series sat within 1.6 to 4.4 of a semantic.
     The text roles keep a visible lightness step, which raising the floors once erased.
  4. Every colour token is inside sRGB, and each dark block a user with no explicit choice
     actually gets, through a prefers-color-scheme query, is identical to the explicit one. That
     copy used to be discarded as a duplicate, which is a guess about a file this tool is here
     to stop guessing about.

  Pass 1 is measured at the shipped accent hue. Run against a set rebuilt at a different hue -
  `tools/build.py --accent-hue N` - the published ratios no longer describe that palette, so
  pass 1 reports itself skipped and names the hue rather than failing rows that were never
  claimed about it. Passes 2 to 4 are hue-independent and always run; they are the certificate.

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

# The accent hue pass 1's tables were measured at. 10-color.md#why-hue-198 owns the choice.
PUBLISHED_HUE = 198


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


# 10-color.md#why-hue-198's bar, in oklab distance times 100, and the lightness step adjacent
# chart series alternate by. Declared here rather than read from the seed, for the same reason
# the pairs are: 0.12 of lightness is a separation of 12 on its own, so neighbours stay apart
# where hue is lost, in greyscale print or to a reader who cannot see it.
SEPARATION, NEIGHBOUR_DL = 8.0, 0.12
CHARTS = [f"--hw-chart-{n}" for n in range(1, 7)]


def separation(a, b, lightness=True):
    """Oklab distance times 100 between two oklch triples. Without lightness it is the distance
    in hue and chroma alone, which pass 5 holds a product colour to."""
    (L1, C1, h1), (L2, C2, h2) = a, b
    da = C1 * math.cos(math.radians(h1)) - C2 * math.cos(math.radians(h2))
    db = C1 * math.sin(math.radians(h1)) - C2 * math.sin(math.radians(h2))
    return 100 * math.hypot(L1 - L2 if lightness else 0.0, da, db)


def separations(tokens):
    """(failures, closest chart pair), for one theme's block.

    hw-chart-1 shares the accent's hue by design, so it is not held apart from the accent; every
    chart colour, and the accent, is held apart from each semantic."""
    bad, closest = [], None
    for fg in ["--hw-accent"] + CHARTS:
        for sem in SEMANTICS[1:]:
            d = separation(tokens[fg], tokens[f"--hw-{sem}"])
            if d < SEPARATION:
                bad.append(f"{fg} sits {d:.1f} from --hw-{sem}, below {SEPARATION}: a series "
                           f"colour that reads as a state")
    for i, a in enumerate(CHARTS):
        for b in CHARTS[i + 1:]:
            d = separation(tokens[a], tokens[b])
            if closest is None or d < closest[0]:
                closest = (d, a, b)
            if d < SEPARATION:
                bad.append(f"{a} sits {d:.1f} from {b}, below {SEPARATION}")
        if i + 1 < len(CHARTS):
            dl = abs(tokens[a][0] - tokens[CHARTS[i + 1]][0])
            if dl < NEIGHBOUR_DL:
                bad.append(f"{a} and {CHARTS[i + 1]} are adjacent series {dl:.3f} apart in "
                           f"lightness, below {NEIGHBOUR_DL}")
    return bad, closest


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
# the six surfaces, and SEPARATION in hue and chroma from the three states and the accent. The
# seed is read only for what it adds - a pair at a text bar, or a further colour to stay clear of.
PRODUCT_APART = [f"--hw-{s}" for s in SEMANTICS]


def raised(bar):
    return max(bar, MORE_BAR[AA]) if bar >= AA else MORE_BAR[NON_TEXT]


def extension(themes, seed_path, css_path):
    """(failures, report lines) for one product's seed and the CSS built from it."""
    ext = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    ns, prod = ext["namespace"], parse_tokens(css_path)
    bad, report = [], []
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
            bar = floor.get("bar")
            if not isinstance(bar, (int, float)) or bar != NON_TEXT and bar < AA:
                bad.append(f"{name} claims {bar}:1, which certifies nothing this file holds")
                continue
            for g in floor["on"]:
                pairs[f"--hw-{g}"] = max(pairs.get(f"--hw-{g}", 0), floor["bar"])
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
            seps = sorted((separation(fg, themes[theme][a], lightness=False), a) for a in apart)
            bad += [f"{theme} {name} sits {d:.1f} from {a} in hue and chroma, below "
                    f"{SEPARATION}: a product colour that reads as a house state"
                    for d, a in seps if d < SEPARATION]
            report.append(f"  {name} {theme:10} {hexof(*fg)}  worst {worst[0]:.3f} (8-bit "
                          f"{worst[1]:.3f}) on {worst[2]}; closest {seps[0][0]:.1f} to "
                          f"{seps[0][1]}")
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

    hue = themes["light"]["--hw-accent"][2]
    if abs(hue - PUBLISHED_HUE) < 0.5:
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
        print(f"pass 1: skipped. This set is built at accent hue {hue:.0f}; the published "
              f"ratios were measured at {PUBLISHED_HUE} and do not describe it.")

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
        bad, (d, a, b) = separations(themes[theme])
        bad += roles(themes[theme])
        failures += [f"{theme} {f}" for f in bad]
        print(f"pass 3: {theme:10} separation and role steps, {len(bad)} below bar; "
              f"closest chart pair {d:.1f}, {a} / {b}")

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
        css = opts.extend_css or seed.parent / (json.loads(seed.read_text(encoding="utf-8"))
                                              ["namespace"] + ".tokens.css")
        bad, report = extension(themes, seed, css)
        failures += bad
        print(f"pass 5: {Path(css).name} against the house set, every token 3:1 or its claimed "
              f"bar on all six surfaces and {SEPARATION} in hue and chroma from the states and "
              f"the accent; {len(bad)} failed")
        print("\n".join(report))

    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
