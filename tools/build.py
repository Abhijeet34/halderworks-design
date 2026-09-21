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

What the build does, in order:

  1. Resolve every token's hue. Neutrals and the accent family follow the accent hue seed,
     because 10-color.md's stated reason for the neutrals carrying a trace of it is that the
     accent should look native to the palette. The six chart hues are the accent plus a fixed
     rotation. The three semantics do not move: a green that means "passed" cannot follow a
     brand decision.
  2. Refuse a hue that sits closer than the recorded separation to any semantic. 10-color.md
     records 8.2 and 8.9 in oklab distance times 100 as the separation hue 198 keeps from
     success, and rejects a teal candidate at 3.8 on that measurement. This is that test made
     executable, which is what 95-extending.md's "a product cannot take hue 150" needs to be
     true rather than merely written.
  3. Clamp chroma to the in-gamut maximum at each token's lightness and hue. An out-of-gamut
     oklch triple is simply not the colour the token file claims, and 90-evidence.md records a
     warning at chroma 0.12 shipping exactly that way.
  4. Re-solve lightness for any token whose contrast floor no longer holds, by binary search,
     staying as close to the seed anchor as the floor permits. Rotating a hue at fixed
     lightness moves WCAG luminance, so this is not a formality.
  5. Refuse an off-unit space or size value that is not a declared grid exception, and
     refuse a declared exception whose value has since moved back onto the unit. 32-rhythm.md
     is what that check makes checkable.
  6. Refuse to write anything if a floor or the grid still fails.

Why the output is byte-identical to the committed files at the shipped hue: at hue 198 steps
3 and 4 are no-ops, because the committed set already satisfies its own spec. That is not a
replay - it runs the same code path - and it is the regression that proves the seed and the
shipped files agree.

The seed's contrast floors and this script are one instrument. tools/contrast.py is a second,
independent one: it re-derives published ratios from the emitted CSS and knows nothing about
the seed. A build that passes and a contrast run that fails would mean the seed is wrong, and
that is exactly the disagreement two instruments exist to surface.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contrast import in_gamut, luminance, oklch_to_rgb, ratio_lum  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-9


# --- colour helpers not already in contrast.py ---------------------------------------------

def max_chroma(L, h, hi=0.45):
    """The largest in-gamut chroma at this lightness and hue, to 1e-4.

    Bisection rather than a formula: the sRGB gamut boundary in OKLCH has no closed form, and
    an analytic approximation that is wrong by a thousandth ships a colour the file does not
    claim - which is the defect this whole step exists to stop.
    """
    if not in_gamut(L, 0.0, h):
        return 0.0
    lo = 0.0
    while hi - lo > 1e-4:
        mid = (lo + hi) / 2
        if in_gamut(L, mid, h):
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


# --- the seed ------------------------------------------------------------------------------

def load_seed(path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_hue(expr, accent):
    if expr == "accent":
        return accent % 360
    if isinstance(expr, str) and expr.startswith("accent+"):
        return (accent + int(expr[len("accent+"):])) % 360
    return int(expr) % 360


def theme_ids(seed):
    return [t["id"] for t in seed["themes"]]


# --- the solve -----------------------------------------------------------------------------

class Solver:
    """Resolves one theme's colour tokens: hue, then chroma clamp, then lightness."""

    def __init__(self, seed, accent, theme):
        self.seed, self.accent, self.theme = seed, accent, theme
        self.solved = {}      # short name -> (L, C, h)
        self.notes = []
        self.failures = []

    def short(self, name):
        return name[len("hw-"):]

    def entries(self):
        return [e for e in self.seed["color"]["tokens"] if e["kind"] == "oklch"]

    def meets(self, L, C, h, floors):
        """(ok, worst_ratio, worst_ground). A ground not yet solved is skipped, which is why
        grounds are resolved in the first pass."""
        worst, where, ok = None, None, True
        lum = luminance(L, C, h)
        for floor in floors:
            for g in floor["on"]:
                if g not in self.solved:
                    continue
                r = ratio_lum(lum, luminance(*self.solved[g]))
                if worst is None or r < worst:
                    worst, where = r, g
                if r + 0.005 < floor["bar"]:
                    ok = False
        return ok, worst, where

    def ground_pull(self, floors):
        """Mean luminance of the grounds this token is checked against, which decides whether
        solving means darkening or lightening."""
        lums = [luminance(*self.solved[g])
                for floor in floors for g in floor["on"] if g in self.solved]
        return sum(lums) / len(lums) if lums else 0.5

    def solve_one(self, entry):
        h = resolve_hue(entry["hue"], self.accent)
        anchor = entry[self.theme]
        L0, C0 = float(anchor["L"]), float(anchor["C"])
        C = min(C0, max_chroma(L0, h))
        floors = entry.get("floors")

        if not floors:
            return L0, C, h, (abs(C - C0) > EPS)

        ok, _, _ = self.meets(L0, C, h, floors)
        if ok:
            return L0, C, h, (abs(C - C0) > EPS)

        # Move away from the grounds. Contrast is monotonic in that direction, so the nearest
        # acceptable lightness is a bisection over the side the token is already on.
        darken = luminance(L0, C, h) < self.ground_pull(floors)
        lo, hi = (0.0, L0) if darken else (L0, 1.0)
        best = None
        for _ in range(60):
            mid = (lo + hi) / 2
            c = min(C0, max_chroma(mid, h))
            if self.meets(mid, c, h, floors)[0]:
                best = (mid, c)
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
                f"{entry['name']} ({self.theme}): no lightness at hue {h} clears its floor; "
                f"worst {worst:.2f} on --hw-{where}")
            return L0, C, h, True
        L, C = best
        self.notes.append(
            f"{entry['name']} ({self.theme}): re-solved L {L0:.4f} -> {L:.4f}, "
            f"C {C0:.4f} -> {C:.4f} at hue {h}")
        return L, C, h, True

    def run(self):
        entries = self.entries()
        # Two passes: everything without a floor is a ground or a fill and must exist before
        # anything is measured against it.
        order = [e for e in entries if not e.get("floors")] + \
                [e for e in entries if e.get("floors")]
        out = {}
        for e in order:
            L, C, h, moved = self.solve_one(e)
            self.solved[self.short(e["name"])] = (L, C, h)
            out[e["name"]] = (L, C, h, moved, e)
        for name, (L, C, h, _, _) in out.items():
            if not in_gamut(L, C, h):
                self.failures.append(f"{name} ({self.theme}): oklch({L} {C} {h}) is outside sRGB")
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


def check_semantic_separation(seed, accent):
    """A new accent must stay clear of every semantic, which is 10-color.md's own test."""
    bar = seed["seed"]["minSemanticSeparation"]
    by_name = {e["name"]: e for e in seed["color"]["tokens"]}
    bad = []
    for theme in theme_ids(seed):
        a = by_name["hw-accent"]
        acc = (float(a[theme]["L"]), float(a[theme]["C"]), resolve_hue(a["hue"], accent))
        for sem in ("success", "warning", "danger"):
            e = by_name[f"hw-{sem}"]
            s = (float(e[theme]["L"]), float(e[theme]["C"]), resolve_hue(e["hue"], accent))
            d = separation(acc, s)
            if d < bar:
                bad.append(f"accent hue {acc[2]} sits {d:.1f} from hw-{sem} in {theme} theme, "
                           f"below the {bar} this system requires (10-color.md#why-hue-198)")
    return bad


# --- emitters ------------------------------------------------------------------------------

def value_string(L, C, h, entry, theme):
    anchor = entry[theme]
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


def build_tokens_css(seed, resolved, accent, stats):
    ids = theme_ids(seed)
    n_text = stats["text_pairs"]
    n_nontext = stats["nontext_pairs"]
    o = []
    o.append(f"""/* {seed['name']} - token definitions.
   Generated from tokens/tokens.seed.json by tools/build.py, which solves every colour against
   its contrast floor in the same run and refuses to emit if one does not hold.
   Do not hand-edit this file or tokens/tokens.json; edit the seed and rebuild.

   {n_text} text-on-ground pairs, both themes, 0 below WCAG AA 4.5:1.
   {n_nontext} non-text pairs (control boundary, focus ring, chart fills, disabled) held to
   3:1, 0 below it.
   {len(resolved[ids[0]])} colour tokens, 0 outside sRGB. Accent hue {accent % 360}. */
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
    o.append(CSS_TAIL.rstrip("\n"))
    for g in seed["type"]["groups"]:
        for s in g["styles"]:
            n = s["name"]
            o.append(f".hw-{n} {{ font-family: var(--hw-font-{g['family']}); "
                     f"font-size: var(--hw-text-{n});")
            o.append(f"  line-height: var(--hw-leading-{n}); "
                     f"letter-spacing: var(--hw-tracking-{n});")
            o.append(f"  font-weight: var(--hw-weight-{n}); }}")
    o.append(CSS_MOTION.rstrip("\n"))
    return "\n".join(o) + "\n"


# --- the matrix report ---------------------------------------------------------------------

def count_pairs(seed, resolved):
    """Every pair the seed asserts, counted by bar, so the header states what was verified
    rather than a number somebody typed."""
    text = nontext = 0
    for theme in theme_ids(seed):
        solved = {n[len("hw-"):]: v[:3] for n, v in resolved[theme].items()}
        for e in seed["color"]["tokens"]:
            for floor in e.get("floors", []):
                n = sum(1 for g in floor["on"] if g in solved)
                if floor["bar"] >= 4.5:
                    text += n
                else:
                    nontext += n
    return {"text_pairs": text, "nontext_pairs": nontext}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--accent-hue", type=int, default=None,
                    help="override the seed's accent hue and re-solve the whole set")
    ap.add_argument("--check", action="store_true",
                    help="emit nothing; exit non-zero if the committed files are stale")
    ap.add_argument("--out", default=None, help="write into this directory instead of tokens/")
    a = ap.parse_args(argv)

    seed = load_seed(ROOT / "tokens" / "tokens.seed.json")
    accent = a.accent_hue if a.accent_hue is not None else seed["seed"]["accentHue"]

    failures = check_semantic_separation(seed, accent) + check_grid(seed)

    resolved, notes = {}, []
    for theme in theme_ids(seed):
        s = Solver(seed, accent, theme)
        resolved[theme] = s.run()
        notes += s.notes
        failures += s.failures

    stats = count_pairs(seed, resolved)
    js = build_tokens_json(seed, resolved)
    css = build_tokens_css(seed, resolved, accent, stats)

    for n in notes:
        print("solved  " + n)
    if failures:
        for f in failures:
            print("FAIL  " + f, file=sys.stderr)
        print(f"\nrefusing to write: {len(failures)} check(s) failed", file=sys.stderr)
        return 1

    out = Path(a.out) if a.out else ROOT / "tokens"
    out.mkdir(parents=True, exist_ok=True)
    targets = {"tokens.json": js, "tokens.css": css}

    if a.check:
        stale = [n for n, text in targets.items()
                 if not (out / n).exists() or (out / n).read_text(encoding="utf-8") != text]
        for n in stale:
            print(f"FAIL  tokens/{n} is not what the seed builds", file=sys.stderr)
        print(f"\n{len(targets) - len(stale)} of {len(targets)} token files match the seed.")
        return 1 if stale else 0

    for n, text in targets.items():
        (out / n).write_text(text, encoding="utf-8")

    n_col = len(seed["color"]["tokens"])
    print(f"accent hue {accent % 360}; {n_col} colour tokens solved across "
          f"{len(theme_ids(seed))} themes, {len(notes)} re-solved.")
    print(f"{stats['text_pairs']} pairs held to WCAG AA 4.5:1 and "
          f"{stats['nontext_pairs']} to 3:1, 0 below bar. 0 outside sRGB.")
    on, off = grid_stats(seed)
    print(f"{on} space and size values on the {seed['grid']['unit']}px unit, "
          f"{off} off it and all {off} declared with a reason.")
    for n in targets:
        print(f"  tokens/{n:12s} {len(targets[n]):7,d} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
