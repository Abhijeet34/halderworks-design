#!/usr/bin/env python3
"""Re-derive and verify this system's contrast claims from tokens/tokens.css.

This is the SECOND instrument, and its independence is the point. tools/build.py solves each
colour against the floors recorded in tokens/tokens.seed.json; this file knows nothing about
the seed and re-derives the ratios from the CSS a browser actually loads. A build that passes
and a contrast run that fails means the seed is wrong, which is the disagreement two
instruments exist to surface and which one instrument checking itself can never report.

It runs two passes and exits non-zero if either fails:

  1. A self-test against ratios published in 10-color.md and 15-color-combinations.md. A
     converter that cannot reproduce the existing table cannot certify a new pair either,
     and this caught a real bug: omitting the XYZ step returns a plausible-looking colour
     with the wrong hue, and it put the light ground at #F2F8FF instead of #F6F8F8.
  2. The form-layer matrix: every pair 66-forms.md, 67-validation.md and 36-form-factors.md
     rely on, text held to WCAG AA 4.5:1 and non-text to 1.4.11's 3:1.

  Pass 1 is measured at the shipped accent hue. Run against a set rebuilt at a different hue -
  `tools/build.py --accent-hue N` - the published ratios no longer describe that palette, so
  pass 1 reports itself skipped and names the hue rather than failing rows that were never
  claimed about it. Pass 2 is hue-independent and always runs; it is the matrix.

    python3 tools/contrast.py [tokens.css]
"""
import math
import re
import sys
from pathlib import Path

M1 = ((0.8189330101, 0.3618667424, -0.1288597137),
      (0.0329845436, 0.9293118715, 0.0361456387),
      (0.0482003018, 0.2643662691, 0.6338517070))
M2 = ((0.2104542553, 0.7936177850, -0.0040720468),
      (1.9779984951, -2.4285922050, 0.4505937099),
      (0.0259040371, 0.7827717662, -0.8086757660))

XYZ_TO_LRGB = ((3.2409699419045226, -1.5373831775700939, -0.4986107602930034),
               (-0.9692436362808796, 1.8759675015077202, 0.0415550574071756),
               (0.0556300796969936, -0.2039769588889765, 1.0569715142428784))

def oklch_to_linear_srgb(L, C, h_deg):
    """oklch -> oklab -> LMS' -> LMS -> XYZ(D65) -> linear sRGB. The XYZ step is not optional:
    omitting it silently returns a plausible-looking colour with the wrong hue."""
    h = math.radians(h_deg)
    lab = (L, C * math.cos(h), C * math.sin(h))
    lms = [sum(M2inv[i][j] * lab[j] for j in range(3)) ** 3 for i in range(3)]
    xyz = [sum(M1inv[i][j] * lms[j] for j in range(3)) for i in range(3)]
    return [sum(XYZ_TO_LRGB[i][j] * xyz[j] for j in range(3)) for i in range(3)]

def inv3(m):
    (a,b,c),(d,e,f),(g,h,i) = m
    det = a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)
    return [[(e*i-f*h)/det, (c*h-b*i)/det, (b*f-c*e)/det],
            [(f*g-d*i)/det, (a*i-c*g)/det, (c*d-a*f)/det],
            [(d*h-e*g)/det, (b*g-a*h)/det, (a*e-b*d)/det]]

M1inv, M2inv = inv3(M1), inv3(M2)

def linear_to_srgb(u):
    return 12.92*u if u <= 0.0031308 else 1.055*(abs(u)**(1/2.4))*(1 if u>=0 else -1) - 0.055

def oklch_to_rgb(L, C, h):
    return [linear_to_srgb(v) for v in oklch_to_linear_srgb(L, C, h)]

def in_gamut(L, C, h, eps=1e-3):
    """eps absorbs matrix round-off. Measured: pure white, oklch(1 0 198), comes back as
    1.000186 through the three matrices, while the real out-of-gamut defect 90-evidence.md
    records, a warning at chroma 0.12, sits at -0.1185 on blue. 1e-3 is a quarter of a 1/255
    channel step and two orders below that defect, so it absorbs the former and still fails
    the latter."""
    return all(-eps <= v <= 1 + eps for v in oklch_to_rgb(L, C, h))

def luminance_rgb(rgb):
    def lin(c):
        c = min(max(c, 0.0), 1.0)
        return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    return 0.2126*r + 0.7152*g + 0.0722*b

def luminance(L, C, h):
    return luminance_rgb(oklch_to_rgb(L, C, h))

def ratio_lum(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def ratio(fg, bg):
    return ratio_lum(luminance(*fg), luminance(*bg))

def hexof(L, C, h):
    return "#" + "".join("%02X" % round(min(max(v,0),1)*255) for v in oklch_to_rgb(L, C, h))

TOKEN_RE = re.compile(r"^\s*(--hw-[a-z0-9-]+):\s*oklch\(([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\)\s*;")

def parse_tokens(path):
    """Return {'light': {...}, 'dark': {...}}. Light is the :root/[data-theme=light] block,
    dark the [data-theme=dark] block; the prefers-color-scheme copy is ignored as a duplicate."""
    themes, cur = {"light": {}, "dark": {}}, None
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if s.startswith(":root, [data-theme=\"light\"]"): cur = "light"; continue
        if s.startswith("[data-theme=\"dark\"]"): cur = "dark"; continue
        if s.startswith("@media (prefers-color-scheme"): cur = None; continue
        if s.startswith("}"): cur = None if cur else cur
        m = TOKEN_RE.match(line)
        if m and cur:
            themes[cur][m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    return themes


# --- pass 1: ratios this system already published, which the converter must reproduce -------

PUBLISHED = {
    ("light", "--hw-text", "--hw-ground"): 14.83,
    ("light", "--hw-text", "--hw-surface"): 15.78,
    ("light", "--hw-text", "--hw-surface-sunken"): 13.98,
    ("light", "--hw-text-secondary", "--hw-ground"): 6.37,
    ("light", "--hw-text-muted", "--hw-ground"): 4.88,
    ("light", "--hw-accent", "--hw-ground"): 5.09,
    ("light", "--hw-warning", "--hw-ground"): 5.10,
    ("light", "--hw-ink-text", "--hw-ink"): 17.63,
    ("light", "--hw-ink-text", "--hw-ink-active"): 10.68,
    ("light", "--hw-accent", "--hw-accent-quiet"): 4.60,
    ("light", "--hw-accent-ring", "--hw-surface-sunken"): 3.05,
    ("light", "--hw-text-disabled", "--hw-surface"): 3.38,
    ("dark", "--hw-text", "--hw-ground"): 16.38,
    ("dark", "--hw-text", "--hw-surface-raised"): 14.02,
    ("dark", "--hw-text-muted", "--hw-surface-raised"): 4.60,
    ("dark", "--hw-accent", "--hw-ground"): 5.60,
    ("dark", "--hw-ink-text", "--hw-ink"): 17.36,
    ("dark", "--hw-success", "--hw-success-quiet"): 4.61,
    ("dark", "--hw-accent-ring", "--hw-surface-raised"): 3.05,
    ("dark", "--hw-text-disabled", "--hw-surface"): 3.26,
}

# --- pass 2: the pairs the form layer introduces -------------------------------------------

SURFACES = ["--hw-ground", "--hw-surface", "--hw-surface-raised", "--hw-surface-sunken",
            "--hw-surface-hover", "--hw-surface-active"]

AA, NON_TEXT = 4.5, 3.0

# The accent hue pass 1's table was measured at. 10-color.md#why-hue-198 owns the choice.
PUBLISHED_HUE = 198


def form_pairs():
    """(kind, foreground, background, what relies on it). Kind picks the bar."""
    for s in SURFACES:
        yield "nontext", "--hw-border-strong", s, "input, select, textarea, switch, slider rail, panel edge"
        yield "nontext", "--hw-ink", s, "checked box, radio dot, switch on, slider fill"
        yield "nontext", "--hw-accent-ring", s, "focus ring on a form control"
        yield "nontext", "--hw-danger", s, "error field border"
        yield "text", "--hw-danger", s, "inline error message"
        yield "text", "--hw-success", s, "field success"
        yield "text", "--hw-warning", s, "pending or degraded"
    for s in ["--hw-surface", "--hw-surface-sunken", "--hw-surface-raised"]:
        yield "text", "--hw-text", s, "label, legend, read-only value"
        yield "text", "--hw-text-secondary", s, "helper text"
        yield "text", "--hw-text-muted", s, "placeholder, character count"
    yield "nontext", "--hw-text-disabled", "--hw-surface-sunken", "disabled field text"
    yield "text", "--hw-ink-text", "--hw-ink", "check glyph, switch thumb"
    for sem in ("danger", "success", "warning"):
        yield "text", f"--hw-{sem}", f"--hw-{sem}-quiet", f"{sem} summary block"


def main(argv):
    path = argv[1] if len(argv) > 1 else str(Path(__file__).resolve().parent.parent / "tokens" / "tokens.css")
    themes = parse_tokens(path)
    failures = []

    hue = themes["light"]["--hw-accent"][2]
    if abs(hue - PUBLISHED_HUE) < 0.5:
        for (theme, fg, bg), want in sorted(PUBLISHED.items()):
            got = ratio(themes[theme][fg], themes[theme][bg])
            if abs(got - want) > 0.011:
                failures.append(f"self-test {theme} {fg} on {bg}: published {want:.2f}, "
                                f"computed {got:.2f}")
        print(f"pass 1: {len(PUBLISHED)} published ratios re-derived, "
              f"{len(failures)} mismatched")
    else:
        print(f"pass 1: skipped. This set is built at accent hue {hue:.0f}; the published "
              f"ratios were measured at {PUBLISHED_HUE} and do not describe it.")

    checked = 0
    worst = {}
    for kind, fg, bg, why in form_pairs():
        bar = AA if kind == "text" else NON_TEXT
        for theme in ("light", "dark"):
            got = ratio(themes[theme][fg], themes[theme][bg])
            checked += 1
            if got + 0.005 < bar:
                failures.append(f"{theme} {fg} on {bg}: {got:.2f} below {bar} ({why})")
            key = (kind, theme)
            if key not in worst or got < worst[key][0]:
                worst[key] = (got, fg, bg)
    print(f"pass 2: {checked} form-layer pairs checked against "
          f"AA {AA}:1 and non-text {NON_TEXT}:1")
    for (kind, theme), (got, fg, bg) in sorted(worst.items()):
        print(f"  worst {kind:8} {theme:5} {got:5.2f}  {fg} on {bg}")

    for token, (L, C, H) in sorted(themes["light"].items()) + sorted(themes["dark"].items()):
        if not in_gamut(L, C, H):
            failures.append(f"{token} oklch({L} {C} {H}) falls outside sRGB")

    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
