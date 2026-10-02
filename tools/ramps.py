#!/usr/bin/env python3
"""Twelve-step OKLCH ramps with a contrast floor per step, one ramp per hue per theme.

Every colour the house ships starts here: tools/export.py composes exports/ and examples/*/exports/
from these files, ramps/roles.css and ramps/scales.css. A brand (ramps/brands/<name>.json) is a
neutral and five to eight named hues, and may name a shape register, an icon stroke and a face per
family from ramps/roster.json, which supplies the house's own for any it leaves out. Every role in
ramps/roles.css names a step of one of these ramps, so a role inherits that step's floor and a new
role is a choice of step, never a new solve.

    python3 tools/ramps.py              # ramps/brands/*.json -> ramps/tokens/<name>.tokens.css
    python3 tools/ramps.py --check      # emit nothing; fail if a file is stale or a floor fails
    python3 tools/ramps.py BRAND.json --out DIR

The steps, per theme:

  1-7   fixed lightness, the grounds, fills and borders (light 0.985 to 0.820, dark 0.165 to 0.400).
  8     solved to 3:1 against steps 1-3 of every ramp: a control boundary.
  11    solved to 4.5:1 against steps 1-5 of every ramp: secondary text.
  12    solved to 13:1 against steps 1-5 of every ramp on the gray: primary text. A hue's step 12
        is solved to 7:1 instead, the raised text bar of prefers-contrast: more, the one tier that
        reads it; at 13:1 every dark step 12 sat near white, a status word in the text's colour.
  9     the brightest solid that carries a white label at 4.5:1, the same in both themes, unless
        the brand names the solid's lightness per theme (a yellow or a pencil that carries ink).
  10    step 9 moved 0.04 darker: the hovered solid.

"Of every ramp" rather than the prototype's own ramp, so accent text holds on a gray fill and
muted gray text on an accent fill by construction, not by luck of lightness.

Every value is quantized to the form it is written in before it is measured, every ratio is
the lower of the float value and the 8-bit value a display receives (the 8-bit alone let the
float miss by 0.016, which tools/contrast.py reads), and the written CSS is parsed back and measured
again before anything reaches disk: MEASURE THE ARTIFACT, NEVER THE INTENT.
The converter is Ottosson's published Oklab constants, a separate path from contrast.py's CSS
Color 4 one, so the second instrument never checks this one with its own arithmetic.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDS = ROOT / "ramps" / "brands"
OUT = ROOT / "ramps" / "tokens"
ROSTER = ROOT / "ramps" / "roster.json"
FAMILIES = ("sans", "display", "read", "mono")

FIXED = {
    "light": (0.985, 0.968, 0.948, 0.928, 0.905, 0.875, 0.820),
    "dark": (0.165, 0.195, 0.230, 0.262, 0.295, 0.335, 0.400),
}
# step -> (floor, the steps of every ramp it is measured against)
FLOORS = {8: (3.0, (1, 2, 3)), 11: (4.5, (1, 2, 3, 4, 5)), 12: (13.0, (1, 2, 3, 4, 5))}
HUE_12 = 7.0         # step 12 of every ramp but the gray, measured against the same span


def floor_of(step, name):
    return HUE_12 if step == 12 and name != "gray" else FLOORS[step][0]
LABEL = 4.5          # WCAG 2.2 SC 1.4.3, for the label on a solid
# A solve aims this far above its floor. 8-bit rounding is measured directly rather than budgeted,
# so this covers only a second converter landing a channel one code value the other side.
MARGIN = 0.02
HOVER = 0.04
REQUIRED = ("accent", "mark", "red", "amber", "green")   # the hues ramps/roles.css names
MAX_HUES = 8
# The six chart series, one ramp each, the same hues in every brand: ramps/roles.css names step 8 or
# 11 of each, so a series holds that step's floor like any role. The hues keep clear of the three
# states (27, 70, 150); tools/contrast.py holds the CIEDE2000 bars between them.
SERIES = {"teal": 180, "blue": 260, "violet": 310, "pink": 355, "olive": 110, "sky": 220}
SERIES_CHROMA = 0.15
CHROMA_MAX = 0.4     # CSS Color 4 maps 100% oklch chroma to 0.4
WHITE = "#FFFFFF"


def oklch_to_lin(L, C, h):
    """oklch -> linear sRGB, by Ottosson's published Oklab-to-LMS and LMS-to-sRGB constants."""
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def in_gamut(L, C, h, eps=0.0):
    return all(-eps <= c <= 1 + eps for c in oklch_to_lin(L, C, h))


def encode(c):
    c = min(max(c, 0.0), 1.0)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def decode(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rgb8(L, C, h):
    return [round(encode(c) * 255) for c in oklch_to_lin(L, C, h)]


def luminance(L, C, h):
    """WCAG relative luminance on the float value and on the 8-bit value a display receives. A
    pair can clear its floor on one and miss on the other, and the house certifies both."""
    def y(r, g, b):
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    return (y(*(min(max(c, 0.0), 1.0) for c in oklch_to_lin(L, C, h))),
            y(*(decode(v / 255) for v in rgb8(L, C, h))))


WHITE_Y = (1.0, 1.0)


def ratio(y1, y2):
    """The lower of the float and the 8-bit contrast ratio between two luminance pairs."""
    return min((max(a, b) + 0.05) / (min(a, b) + 0.05) for a, b in zip(y1, y2))


def colour(L, C, h):
    """The triple exactly as it is written: L to 3 places, C clamped into sRGB and then floored to
    3 places (rounding up could leave the gamut), h to 1 place. Every measurement takes this."""
    L, h = round(L, 3), round(h, 1)
    if not in_gamut(L, C, h):
        lo, hi = 0.0, C
        for _ in range(32):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if in_gamut(L, mid, h) else (lo, mid)
        C = lo
    return (L, math.floor(C * 1000 + 1e-9) / 1000, h)


def num(x):
    return f"{x:.3f}".rstrip("0").rstrip(".") if x else "0"


def fmt(t):
    return f"oklch({t[0]:.3f} {t[1]:.3f} {num(t[2])})"


# ---- the brand file ------------------------------------------------------------------------

class BrandError(Exception):
    pass


def number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def load_brand(path):
    """The brand file, or BrandError naming every problem in it. NaN, Infinity and a repeated key
    are refused at parse time, because json would otherwise accept them silently."""
    def no_constant(c):
        raise BrandError(f"{c} is not a number a brand can name")

    def no_duplicates(pairs):
        keys = [k for k, _ in pairs]
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            raise BrandError(f"key {dup[0]!r} appears twice")
        return dict(pairs)
    try:
        brand = json.loads(Path(path).read_text(encoding="utf-8"),
                           parse_constant=no_constant, object_pairs_hook=no_duplicates)
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise BrandError(str(e)) from None
    errors = brand_errors(brand)
    if errors:
        raise BrandError("; ".join(errors))
    return brand


def keys_errors(obj, where, required, optional=()):
    if not isinstance(obj, dict):
        return [f"{where} must be an object"]
    errors = [f"{where} is missing {k!r}" for k in required if k not in obj]
    errors += [f"{where} has unknown key {k!r}" for k in obj if k not in required + optional]
    return errors


def hue_chroma_errors(spec, where, neutral):
    """A neutral may be pure gray; a hue with no chroma is a second gray under another name."""
    errors = []
    if "hue" in spec and not (number(spec["hue"]) and 0 <= spec["hue"] < 360):
        errors.append(f"{where}.hue must be a number in [0, 360), not {spec['hue']!r}")
    c = spec.get("chroma", 0)
    if not (number(c) and (c >= 0 if neutral else c > 0) and c <= CHROMA_MAX):
        errors.append(f"{where}.chroma must be a number in {'[' if neutral else '('}0, "
                      f"{CHROMA_MAX}], not {c!r}")
    return errors


def brand_errors(brand):
    errors = keys_errors(brand, "the brand", ("neutral", "hues"),
                         ("note", "shape", "iconStroke", "faces"))
    if errors:
        return errors
    errors = identity_errors(brand, roster())
    e = keys_errors(brand["neutral"], "neutral", ("hue", "chroma"))
    errors += e or hue_chroma_errors(brand["neutral"], "neutral", True)
    hues = brand["hues"]
    if not isinstance(hues, dict):
        return errors + ["hues must be an object"]
    errors += [f"hues is missing {k!r}, which ramps/roles.css names" for k in REQUIRED
               if k not in hues]
    if len(hues) > MAX_HUES:
        errors.append(f"hues names {len(hues)} ramps; a brand has at most {MAX_HUES}")
    for name, spec in hues.items():
        where = f"hues.{name}"
        if not re.fullmatch(r"[a-z][a-z0-9]*", name) or name == "gray":
            errors.append(f"{where}: a ramp name is lowercase letters and digits, and not 'gray'")
        if name in SERIES:
            errors.append(f"{where}: {name!r} is a chart series every brand carries; name the "
                          f"brand's own hue something else")
        e = keys_errors(spec, where, ("hue", "chroma"), ("solid",))
        errors += e
        if not isinstance(spec, dict):
            continue
        errors += hue_chroma_errors(spec, where, False)
        if "solid" in spec:
            solid = spec["solid"]
            errors += keys_errors(solid, f"{where}.solid", ("light", "dark"))
            if isinstance(solid, dict):
                errors += [f"{where}.solid.{t} must be a lightness in ({HOVER}, 1), "
                           f"not {solid[t]!r}" for t in ("light", "dark")
                           if t in solid and not (number(solid[t]) and HOVER < solid[t] < 1)]
    return errors


# ---- the roster: shape, stroke and faces ---------------------------------------------------

FACE_LICENCE = "OFL-1.1"   # design/20-type.md#the-licence-rule
FACE_FILE_FIELDS = ("source", "licence", "sha256", "xHeight", "licenceText", "licenceSha256",
                    "upstream", "formats")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def roster_errors(r):
    """A self-hosted face is an OFL file pinned by the sha256 of its upstream file and of its
    licence text; a system face is a stack that loads nothing and pins nothing."""
    errors = keys_errors(r, "ramps/roster.json", ("note", "default", "registers", "iconStrokes",
                                                  "faces"))
    if errors:
        return errors
    for name, f in r["faces"].items():
        where = f"roster face {name!r}"
        if f.get("delivery") == "system":
            errors += [f"{where} is a system stack and names {k!r}; it loads no file"
                       for k in FACE_FILE_FIELDS + ("vendored",) if k in f]
        elif f.get("delivery") != "self-hosted":
            errors.append(f"{where} has delivery {f.get('delivery')!r}, not self-hosted or system")
        elif missing := [k for k in FACE_FILE_FIELDS if k not in f]:
            errors.append(f"{where} is self-hosted and names no {missing}")
        elif f["licence"] != FACE_LICENCE:
            errors.append(f"{where} is licensed {f['licence']!r}; a roster face is "
                          f"{FACE_LICENCE} and nothing else")
        elif not all(SHA256.match(str(f[k])) for k in ("sha256", "licenceSha256")):
            errors.append(f"{where} pins a sha256 that is not 64 hex digits")
    errors += identity_errors(r["default"], r, "the roster's default")
    return errors


def roster():
    try:
        r = json.loads(ROSTER.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BrandError(f"ramps/roster.json: {e}") from None
    errors = roster_errors(r)
    if errors:
        raise BrandError("; ".join(errors))
    return r


def identity_errors(brand, r, where="the brand"):
    """The shape, stroke and faces a brand names, each one the roster carries."""
    errors = []
    for key, allowed in (("shape", tuple(r["registers"])), ("iconStroke", tuple(r["iconStrokes"]))):
        if key in brand and brand[key] not in allowed:
            errors.append(f"{where}: {key} {brand[key]!r} is not one of {', '.join(allowed)}")
    faces = brand.get("faces", {})
    if not isinstance(faces, dict):
        return errors + [f"{where}: faces must be an object"]
    for family, face in faces.items():
        if family not in FAMILIES:
            errors.append(f"{where}: faces.{family} is not a family; the families are "
                          f"{', '.join(FAMILIES)}")
        elif face not in r["faces"]:
            errors.append(f"{where}: faces.{family} {face!r} is not a roster face")
        elif family == "mono" and not r["faces"][face].get("monospaced"):
            mono = [n for n, f in r["faces"].items() if f.get("monospaced")]
            errors.append(f"{where}: faces.mono {face!r} is not one of {', '.join(mono)}")
    return errors


ROLE_NOTES = {"sans": "interface and body text", "display": "the stage voice",
              "read": "running prose and quoted words", "mono": "code, keys and figures"}
SHAPE_NOTES = {"sm": "things inside other things: badges, checkboxes, swatches, the status dot",
               "md": "interactive controls: buttons, inputs, selects, menu items, tabs",
               "lg": "containers: cards, panels, dialogs, popovers, toasts"}


def identity(brand):
    """[(property, value, description)]: the faces, shape and stroke a brand paints with."""
    r = roster()
    d = r["default"]
    faces = {**d["faces"], **brand.get("faces", {})}
    house_x = r["faces"][d["faces"]["sans"]]["xHeight"]
    out = []
    for family in FAMILIES:
        face = r["faces"][faces[family]]
        note = f"{ROLE_NOTES[family]}: {faces[family]}"
        if family == "sans" and faces["sans"] != d["faces"]["sans"]:
            note += f", held to the house x-height with font-size-adjust: {house_x}"
        out.append((f"--hw-font-{family}", face["stack"], note))
        if family == "display":
            # A width is part of a face's identity (Archivo Expanded is Archivo at 125%), and a
            # comment cannot set one, so the display face's width ships as its own value.
            out.append(("--hw-font-display-stretch", face.get("stretch", "100%"),
                        f"the display face's width, as font-stretch: {faces[family]}"))
    shape = brand.get("shape", d["shape"])
    out += [(f"--{k}", v, f"the {shape} register; {SHAPE_NOTES[k.rsplit('-', 1)[1]]}")
            for k, v in r["registers"][shape].items()]
    out.append(("--hw-icon-stroke", brand.get("iconStroke", d["iconStroke"]),
                "stroke weight at 16px and 20px"))
    return out


# ---- the solve -----------------------------------------------------------------------------

def nearest(theme, passes):
    """The lightness nearest the grounds at which passes(L) holds, walking away from them (down in
    light, up in dark) by 0.01 and then back over the last stride by 0.001. A pass window
    narrower than 0.01 can be stepped over; it only moves the answer further out, and verify()
    measures whatever is written either way."""
    sign = -1 if theme == "light" else 1
    start, end = (999, 1) if theme == "light" else (1, 999)
    for coarse in [*range(start, end, 10 * sign), end]:
        if passes(coarse / 1000):
            for fine in range(coarse - 10 * sign, coarse + sign, sign):
                if 0 < fine < 1000 and passes(fine / 1000):
                    return fine / 1000
    raise BrandError("no lightness passes")


def solve(floor, grounds, h, C, theme):
    """The step nearest the grounds that clears floor + MARGIN against every one of them."""
    def passes(L):
        y = luminance(*colour(L, C, h))
        return min(ratio(y, g) for g in grounds) >= floor + MARGIN
    try:
        return colour(nearest(theme, passes), C, h)
    except BrandError:
        raise BrandError(f"no lightness at hue {h} clears {floor}:1 against its grounds") from None


def brightest_white_solid(h, C):
    try:
        return nearest("light", lambda L: ratio(luminance(*colour(L, C, h)), WHITE_Y)
                       >= LABEL + MARGIN)
    except BrandError:
        raise BrandError(f"no solid at hue {h} carries a white label") from None


def ramp_specs(brand):
    n = brand["neutral"]
    gray = {"hue": n["hue"], "chroma": n["chroma"], "neutral": True}
    series = {name: {"hue": h, "chroma": SERIES_CHROMA} for name, h in SERIES.items()}
    return {"gray": gray, **brand["hues"], **series}


def step_chroma(spec, step):
    """The chroma each step aims at before the gamut clamp. A hue's grounds rise from 17% to 59%
    of its chroma; the neutral holds its tint on the grounds and doubles it on 8 and 11."""
    C = spec["chroma"]
    if spec.get("neutral"):
        return 2 * C if step in (8, 11) else C
    if step <= 7:
        return C * (0.10 + 0.07 * step)
    return 0.9 * C if step == 8 else C


def label_for(theme, steps, ink):
    """White if it reads better on step 9 than the theme's dark ink, else that ink."""
    y9 = luminance(*steps[9])
    return WHITE if ratio(y9, WHITE_Y) >= ratio(y9, luminance(*ink)) else "ink"


def build(brand):
    """{theme: {ramp: {step: (L, C, h), 'label': WHITE | 'ink'}}, 'identity': identity(brand)},
    or BrandError."""
    specs = ramp_specs(brand)
    solids = {name: brightest_white_solid(s["hue"], s["chroma"])
              for name, s in specs.items() if "solid" not in s}
    out = {}
    for theme in ("light", "dark"):
        ramps = {name: {i: colour(L, step_chroma(s, i), s["hue"])
                        for i, L in enumerate(FIXED[theme], start=1)}
                 for name, s in specs.items()}
        for step, (_, span) in FLOORS.items():
            grounds = {luminance(*r[i]) for r in ramps.values() for i in span}
            for name, s in specs.items():
                ramps[name][step] = solve(floor_of(step, name), grounds, s["hue"],
                                          step_chroma(s, step), theme)
        ink = ramps["gray"][12 if theme == "light" else 1]
        for name, s in specs.items():
            L9 = s["solid"][theme] if "solid" in s else solids[name]
            ramps[name][9] = colour(L9, step_chroma(s, 9), s["hue"])
            ramps[name][10] = colour(L9 - HOVER, step_chroma(s, 10), s["hue"])
            ramps[name]["label"] = label_for(theme, ramps[name], ink)
        out[theme] = ramps
    out["identity"] = identity(brand)
    return out


# ---- the artifact --------------------------------------------------------------------------

SELECTORS = {"light": ':root, [data-theme="light"]', "dark": '[data-theme="dark"]'}
MEDIA_DARK = "@media (prefers-color-scheme: dark)"


def label_value(theme, label):
    return WHITE if label == WHITE else f"var(--hw-gray-{12 if theme == 'light' else 1})"


def emit(built, source):
    def block(theme, indent):
        lines = []
        for name, steps in built[theme].items():
            lines += [f"{indent}--hw-{name}-{i}: {fmt(steps[i])};" for i in range(1, 13)]
            lines.append(f"{indent}--hw-{name}-on-solid: {label_value(theme, steps['label'])};")
        return "\n".join(lines)
    faces = "\n".join(f"  {k}: {v};  /* {note} */" for k, v, note in built["identity"])
    return (f"/* Halderworks ramps, generated from {source} by tools/ramps.py.\n"
            "   The brand's faces, shape and stroke, then twelve steps per hue per theme;\n"
            "   tools/ramps.py measures every floor on the 8-bit value written here and refuses\n"
            "   to emit if one does not hold. Do not hand-edit: edit the brand file and rebuild.\n"
            "   Load before ramps/roles.css. */\n"
            f":root {{\n{faces}\n}}\n\n"
            f"{SELECTORS['light']} {{\n{block('light', '  ')}\n}}\n\n"
            f"{SELECTORS['dark']} {{\n{block('dark', '  ')}\n}}\n\n"
            f"{MEDIA_DARK} {{\n  :root:not([data-theme=\"light\"]) {{\n"
            f"{block('dark', '    ')}\n  }}\n}}\n")


STEP = re.compile(r"^\s*--hw-([a-z][a-z0-9]*)-(\d+): oklch\(([0-9.]+) ([0-9.]+) ([0-9.]+)\);$")
ON_SOLID = re.compile(r"^\s*--hw-([a-z][a-z0-9]*)-on-solid: (#FFFFFF|var\(--hw-gray-(?:1|12)\));$")


def parse(css):
    """The three colour blocks of an emitted file, read back from the text alone."""
    blocks, current = {}, None
    heads = {SELECTORS["light"] + " {": "light", SELECTORS["dark"] + " {": "dark",
             ':root:not([data-theme="light"]) {': "dark-media"}
    for line in css.splitlines():
        if line.strip() in heads:
            current = blocks.setdefault(heads[line.strip()], {})
        elif (m := STEP.match(line)) and current is not None:
            current.setdefault(m[1], {})[int(m[2])] = (float(m[3]), float(m[4]), float(m[5]))
        elif (m := ON_SOLID.match(line)) and current is not None:
            current.setdefault(m[1], {})["on-solid"] = m[2]
    return blocks


def verify(css):
    """Every floor, label and fixed lightness, measured on the text that would be written.
    Returns (failures, lowest ratio seen per check)."""
    blocks = parse(css)
    fails, lowest = [], {}
    if set(blocks) != {"light", "dark", "dark-media"}:
        return [f"expected light, dark and dark-media blocks, found {sorted(blocks)}"], lowest
    if blocks["dark"] != blocks["dark-media"]:
        fails.append(f"the {MEDIA_DARK} block differs from [data-theme=\"dark\"]")
    for theme in ("light", "dark"):
        ramps = blocks[theme]
        bad = [n for n, r in ramps.items() if set(r) != set(range(1, 13)) | {"on-solid"}]
        if bad or "gray" not in ramps:
            fails.append(f"{theme}: ramps without twelve steps and a label: {bad or ['gray']}")
            continue
        for name, r in ramps.items():
            for i in range(1, 13):
                if not in_gamut(*r[i], eps=1e-6):
                    fails.append(f"{theme} {name}-{i} {fmt(r[i])} is outside sRGB")
            for i, L in enumerate(FIXED[theme], start=1):
                if r[i][0] != L:
                    fails.append(f"{theme} {name}-{i} has lightness {r[i][0]}, not the fixed {L}")
        for step, (_, span) in FLOORS.items():
            grounds = [(f"{g}-{i}", luminance(*ramps[g][i])) for g in ramps for i in span]
            for name, r in ramps.items():
                floor = floor_of(step, name)
                y = luminance(*r[step])
                worst, on = min((ratio(y, gy), g) for g, gy in grounds)
                lowest[step] = min(lowest.get(step, (99, "")), (worst, f"{theme} {name}"))
                if worst < floor:
                    fails.append(f"{theme} {name}-{step} is {worst:.2f}:1 on {on}, "
                                 f"under its {floor}:1 floor")
        ink = ramps["gray"][12 if theme == "light" else 1]
        for name, r in ramps.items():
            y = WHITE_Y if r["on-solid"] == WHITE else luminance(*ink)
            for i in (9, 10):
                got = ratio(y, luminance(*r[i]))
                lowest["label"] = min(lowest.get("label", (99, "")), (got, f"{theme} {name}-{i}"))
                if got < LABEL:
                    fails.append(f"{theme} {name}-{i} carries its label {r['on-solid']} at "
                                 f"{got:.2f}:1, under {LABEL}:1")
    return fails, lowest


def render(path):
    """(css, failures, lowest) for one brand file; BrandError if the brand cannot be built."""
    path = Path(path).resolve()
    try:
        source = path.relative_to(ROOT).as_posix()
    except ValueError:
        source = path.name
    css = emit(build(load_brand(path)), source)
    return (css, *verify(css))


def summary(name, lowest):
    return (f"{name}: lowest step 8 {lowest[8][0]:.2f} ({lowest[8][1]}), "
            f"11 {lowest[11][0]:.2f} ({lowest[11][1]}), 12 {lowest[12][0]:.2f} ({lowest[12][1]}), "
            f"label {lowest['label'][0]:.2f} ({lowest['label'][1]})")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("brands", nargs="*", type=Path,
                    help="brand files (default ramps/brands/*.json)")
    ap.add_argument("--out", type=Path, default=OUT, help="directory for <name>.tokens.css")
    ap.add_argument("--check", action="store_true", help="emit nothing; fail if stale or refused")
    a = ap.parse_args(argv)
    brands = a.brands or sorted(BRANDS.glob("*.json"))
    if not brands:
        print(f"FAIL  no brand files in {BRANDS}", file=sys.stderr)
        return 1
    fails, written = [], {}
    for path in brands:
        try:
            css, f, lowest = render(path)
        except BrandError as e:
            fails.append(f"{path}: {e}")
            continue
        fails += [f"{path.stem}: {x}" for x in f]
        if not f:
            print(summary(path.stem, lowest))
            written[a.out / f"{path.stem}.tokens.css"] = css
    if a.check:
        for out, css in written.items():
            if not out.is_file() or out.read_text(encoding="utf-8") != css:
                fails.append(f"{out} is stale; run python3 tools/ramps.py")
        if not a.brands:
            fails += [f"{p} has no brand file in {BRANDS}"
                      for p in sorted(a.out.glob("*.tokens.css"))
                      if p not in written and not (BRANDS / f"{p.name[:-11]}.json").is_file()]
    if fails:
        for x in fails:
            print(f"FAIL  {x}", file=sys.stderr)
        return 1
    if not a.check:
        a.out.mkdir(parents=True, exist_ok=True)
        for out, css in written.items():
            out.write_text(css, encoding="utf-8")
            print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
