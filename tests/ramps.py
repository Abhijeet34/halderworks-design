#!/usr/bin/env python3
"""The claims tools/ramps.py makes, checked from outside it.

  1. The committed ramps/tokens/*.tokens.css are what the brand files build (`--check`).
  2. tools/contrast.py --ramps certifies them: every floor, solid label and role re-measured by a
     converter that shares no arithmetic with tools/ramps.py, on the float and the 8-bit value.
  3. Every var() in ramps/roles.css resolves in every brand, so a role cannot name a step a brand
     does not emit.
  4. Every accent hue is open: all 360 at chroma 0.15, every fifth at the 0.4 chroma ceiling,
     and every tenth as a named light solid that carries ink, each building and verifying.
  5. Step 9 is the brightest solid that carries white: 0.001 brighter misses the solve's target.
  6. A malformed brand file is refused with a sentence, never a traceback.
  7. verify() refuses a written file that breaks a floor, a label, a fixed step or the two dark
     blocks' agreement, so the re-measure is a check rather than a formality.
  8. tools/contrast.py --ramps refuses a floor missed by under 0.01, a role on the wrong step, an
     accent equal to the success green, and malformed files, each by name and without a traceback.
  9. ramps.py's floors and contrast.py's are the same set, declared in each file.
  10. Every fifth accent hue through contrast.py's separation bars: hue 150 refused, 262 not.
      Every hue builds (4); this is how many of them read as a state once built.

    python3 tests/ramps.py [repo-root]
"""
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import contrast  # noqa: E402
import ramps     # noqa: E402

TOOL = ROOT / "tools" / "ramps.py"
CONTRAST = ROOT / "tools" / "contrast.py"
HOUSE = json.loads((ROOT / "ramps" / "brands" / "house.json").read_text(encoding="utf-8"))


def committed_files_are_fresh(fails):
    r = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True)
    if r.returncode:
        fails.append(f"tools/ramps.py --check exited {r.returncode}:\n{r.stderr}")
    print(f"  fresh:        tools/ramps.py --check exit {r.returncode}")


def second_instrument_agrees(fails):
    """The committed files certified by tools/contrast.py --ramps, which re-measures every floor,
    label and role by the CSS Color 4 path rather than ramps.py's own."""
    r = subprocess.run([sys.executable, str(CONTRAST), "--ramps"], capture_output=True, text=True)
    if r.returncode or "Traceback" in r.stderr:
        fails.append(f"tools/contrast.py --ramps exited {r.returncode}:\n{r.stderr}")
    print(f"  second view:  tools/contrast.py --ramps exit {r.returncode}, "
          f"{r.stdout.count('0 failed')} brands certified")


def floors_declared_twice(fails):
    """The floors ramps.py solves to and the floors contrast.py certifies are two declarations of
    one set, so weakening a floor takes an edit in both files and this check names it."""
    theirs = {k: (v[0], tuple(v[1])) for k, v in contrast.STEP_FLOORS.items()}
    if theirs != ramps.FLOORS or contrast.SOLIDS != (9, 10) or contrast.AA != ramps.LABEL:
        fails.append(f"tools/ramps.py solves to {ramps.FLOORS}, label {ramps.LABEL}, and "
                     f"tools/contrast.py certifies {theirs}, label {contrast.AA}")
    print(f"  floors:       ramps.py and contrast.py declare the same {len(theirs)} step floors "
          f"and the {ramps.LABEL}:1 label")


def brand_css(tmp, name, brand):
    path = Path(tmp) / f"{name}.tokens.css"
    path.write_text(ramps.emit(ramps.build(brand), name), encoding="utf-8")
    return path


def just_under(css, token, theme_head, under, bar):
    """css with `token` in the block after theme_head rewritten to the triple, at the precision
    the file is written in, whose worst reading by contrast.py (float or 8-bit) falls closest
    under bar: lightness walks toward the grounds by 0.001, then chroma picks the finest miss
    near that edge. Returns (css, how far under bar it lands)."""
    m = re.compile(rf"  {token}: oklch\(([0-9.]+) ([0-9.]+) ([0-9.]+)\);").search(
        css, css.index(theme_head))
    L, C, h = (float(x) for x in m.groups())
    sign = 1 if "light" in theme_head else -1

    def worst(t):
        return min(min(contrast.ratio(t, g)) for g in under)
    while worst((L, C, h)) >= bar:
        L = round(L + sign * 0.001, 3)
    near = [(L2, round(C2 / 1000, 3), h) for L2 in (L, round(L - sign * 0.001, 3))
            for C2 in range(0, int(C * 1000) + 61)]
    t = max((t for t in near if contrast.in_gamut(*t) and worst(t) < bar), key=worst)
    line = f"  {token}: oklch({t[0]:.3f} {t[1]:.3f} {ramps.num(h)});"
    return css[:m.start()] + line + css[m.end():], bar - worst(t)


def contrast_refuses(fails):
    """tools/contrast.py --ramps against inputs that must fail, each by the sentence it names."""
    house = (ROOT / "ramps" / "tokens" / "house.tokens.css").read_text(encoding="utf-8")
    roles = (ROOT / "ramps" / "roles.css").read_text(encoding="utf-8")
    light = ':root, [data-theme="light"] {'
    blocks = ramps.parse(house)
    grays = [blocks["light"][g][i] for g in blocks["light"] for i in range(1, 4)]
    texts = [blocks["light"][g][i] for g in blocks["light"] for i in range(1, 6)]
    near = [just_under(house, tok, light, under, bar) for tok, under, bar in (
        ("--hw-accent-8", grays, 3.0), ("--hw-red-11", texts, 4.5), ("--hw-gray-12", texts, 13.0))]
    fails += [f"the near miss on {bar} is {miss:.4f} under, not under 0.01"
              for (_, miss), bar in zip(near, (3.0, 4.5, 13.0)) if not 0 < miss < 0.01]
    green = copy.deepcopy(HOUSE)
    green["hues"]["accent"] = dict(green["hues"]["green"])
    at150 = copy.deepcopy(HOUSE)
    at150["hues"]["accent"] = {"hue": 150, "chroma": 0.15}
    dark_head = '[data-theme="dark"] {\n'
    token_cases = [
        (f"step 8 missing 3:1 by {near[0][1]:.4f}", near[0][0], "accent-8 on"),
        (f"step 11 missing 4.5:1 by {near[1][1]:.4f}", near[1][0], "red-11 on"),
        (f"step 12 missing 13:1 by {near[2][1]:.4f}", near[2][0], "gray-12 on"),
        ("a white label on the mark", tampered(house, "--hw-mark-on-solid: var(--hw-gray-12);",
                                               "--hw-mark-on-solid: #FFFFFF;"), "mark-on-solid on"),
        ("a dark block the media copy disagrees with",
         tampered(house, dark_head + "  --hw-gray-1: oklch(0.165", dark_head +
                  "  --hw-gray-1: oklch(0.166"), "differs from [data-theme"),
        ("a step dropped", tampered(house, "  --hw-red-12:", "  /* gone */ --hw-red-x:"),
         "not steps 1 to 12"),
        ("an unreadable line", tampered(house, "  --hw-red-12:", "  red twelve\n  --hw-red-12:"),
         "cannot read 'red twelve'"),
        ("a step written twice", tampered(house, "  --hw-red-12:", "  --hw-red-11: oklch(0.5 0.1 "
                                          "27);\n  --hw-red-12:"), "declared twice"),
        ("a hex the instrument does not convert",
         tampered(house, "--hw-red-on-solid: #FFFFFF;", "--hw-red-on-solid: #FEFEFE;"),
         "does not convert"),
        ("a block it does not certify", house + "\n.x {\n  --hw-gray-1: oklch(0.5 0 0);\n}\n",
         "a block this does not certify"),
        ("no dark block", house[:house.index(dark_head)], "has no dark block"),
        ("a truncated file", house[:len(house) // 2], "has no media-dark block"),
    ]
    role_cases = [
        ("muted text one step light", "--hw-text-muted: var(--hw-gray-11);",
         "--hw-text-muted: var(--hw-gray-10);", "--hw-text-muted on"),
        ("primary text on step 11", "--hw-text: var(--hw-gray-12);",
         "--hw-text: var(--hw-gray-11);", "--hw-text on"),
        ("the ring on step 7", "--hw-focus: var(--hw-accent-8);", "--hw-focus: var(--hw-accent-7);",
         "--hw-focus on"),
        ("a role certified by nothing", "--hw-bg: var(--hw-gray-1);",
         "--hw-bg: var(--hw-gray-1);\n  --hw-new: var(--hw-gray-5);", "--hw-new is in roles.css"),
        ("a role naming a step no brand emits", "--hw-fill: var(--hw-gray-3);",
         "--hw-fill: var(--hw-gray-13);", "--hw-gray-13 is not declared"),
        ("a role that names itself", "--hw-fill: var(--hw-gray-3);", "--hw-fill: var(--hw-fill);",
         "refers to itself"),
        ("the hover label under more", "    --hw-ink-hover: var(--hw-gray-12);\n", "",
         "--hw-on-ink on --hw-ink-hover"),
        ("a dark override left out of the media copy",
         "    --hw-mark-quiet: var(--hw-mark-5);\n    --hw-scrim: oklch(0 0 0 / 0.6);\n  }\n}",
         "    --hw-scrim: oklch(0 0 0 / 0.6);\n  }\n}", "dark overrides differ"),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        cases = []
        for what, text, expect in token_cases:
            path = Path(tmp) / "case.tokens.css"
            path.write_text(text, encoding="utf-8")
            r = subprocess.run([sys.executable, str(CONTRAST), "--ramps", str(path)],
                               capture_output=True, text=True)
            cases.append((what, r.returncode, r.stderr, expect))
        for what, old, new, expect in role_cases:
            path = Path(tmp) / "roles.css"
            path.write_text(tampered(roles, old, new), encoding="utf-8")
            bad, _ = contrast.certify_ramps(ROOT / "ramps" / "tokens" / "house.tokens.css", path)
            cases.append((what, 1 if bad else 0, "\n".join(bad), expect))
        for what, brand, expect in (("an accent equal to the success green", green,
                                     "--hw-accent-fill sits 0.0 CIEDE2000 from --hw-success-fill"),
                                    ("an accent at hue 150", at150,
                                     "--hw-accent-fill sits")):
            bad, _ = contrast.certify_ramps(brand_css(tmp, "case", brand))
            cases.append((what, 1 if bad else 0, "\n".join(bad), expect))
    for what, rc, err, expect in cases:
        if rc != 1 or expect not in err or "Traceback" in err:
            fails.append(f"contrast.py --ramps on {what}: exit {rc}, expected 1 naming "
                         f"{expect!r}; got: {err.strip()[:300]}")
    print(f"  refuses:      {len(cases)} wrong ramp files, roles and brands, each refused by "
          f"tools/contrast.py --ramps naming what broke; floors missed by "
          + ", ".join(f"{miss:.4f}" for _, miss in near))


def separation_sweep(fails):
    """Every fifth accent hue at chroma 0.15, through contrast.py's separation bars: the arc that
    builds but reads as a state is refused, and hue 150, the success green's, is inside it."""
    refused = []
    with tempfile.TemporaryDirectory() as tmp:
        for hue in range(0, 360, 5):
            b = copy.deepcopy(HOUSE)
            b["hues"]["accent"] = {"hue": hue, "chroma": 0.15}
            bad, _ = contrast.certify_ramps(brand_css(tmp, "sweep", b))
            if bad:
                refused.append(hue)
                if not all("CIEDE2000" in x for x in bad):
                    fails.append(f"accent hue {hue}: refused for more than separation: {bad[:3]}")
    if 150 not in refused or 262 in refused:
        fails.append(f"the separation sweep refused {refused}: hue 150 must be in it and 262 not")
    print(f"  separation:   {len(refused)} of 72 accent hues refused as reading as a state: "
          f"{refused}")


def roles_resolve(fails):
    roles = (ROOT / "ramps" / "roles.css").read_text(encoding="utf-8")
    defined = set(re.findall(r"(--hw-[a-z0-9-]+):", roles))
    used = set(re.findall(r"var\((--hw-[a-z0-9-]+)\)", roles))
    files = sorted((ROOT / "ramps" / "tokens").glob("*.tokens.css"))
    for path in files:
        emitted = set(re.findall(r"(--hw-[a-z0-9-]+):", path.read_text(encoding="utf-8")))
        missing = sorted(used - defined - emitted)
        if missing:
            fails.append(f"ramps/roles.css names {missing} that {path.name} does not emit")
    print(f"  roles:        {len(defined)} roles, {len(used)} var() references, resolved in "
          f"{len(files)} brands")


def build_and_verify(brand, what, fails):
    try:
        css = ramps.emit(ramps.build(brand), "sweep")
    except ramps.BrandError as e:
        fails.append(f"{what}: refused: {e}")
        return
    bad, _ = ramps.verify(css)
    fails += [f"{what}: {x}" for x in bad]


def every_hue_is_open(fails):
    n = 0
    for hue in range(360):
        cases = [("0.15", {"hue": hue, "chroma": 0.15})]
        if hue % 5 == 0:
            cases.append(("0.4", {"hue": hue, "chroma": 0.4}))
        if hue % 10 == 0:
            cases.append(("light solid", {"hue": hue, "chroma": 0.15,
                                          "solid": {"light": 0.92, "dark": 0.90}}))
        for what, accent in cases:
            b = copy.deepcopy(HOUSE)
            b["hues"]["accent"] = accent
            build_and_verify(b, f"accent hue {hue} at {what}", fails)
            n += 1
    print(f"  hues:         {n} accent builds over 360 hues, chroma 0.15 and 0.4, white and ink "
          f"solids")


def step_9_is_brightest(fails):
    built = ramps.build(HOUSE)
    named = {k for k, s in HOUSE["hues"].items() if "solid" in s}
    for name, r in built["light"].items():
        if name in named:
            continue
        L, C, h = r[9]
        s = ramps.ramp_specs(HOUSE)[name]
        brighter = ramps.colour(L + 0.001, ramps.step_chroma(s, 9), h)
        if ramps.ratio(ramps.luminance(*brighter), ramps.WHITE_Y) >= ramps.LABEL + ramps.MARGIN:
            fails.append(f"{name}-9 at L {L} is not the brightest white-label solid: "
                         f"{brighter} still carries white")
        if built["dark"][name][9] != r[9]:
            fails.append(f"{name}-9 differs between themes")
    print(f"  step 9:       {len(built['light']) - len(named)} unnamed solids are the brightest "
          f"carrying white, the same in both themes")


def with_hues(**hues):
    """The house brand file with some hues replaced (or removed, given None), as text."""
    b = copy.deepcopy(HOUSE)
    b["hues"].update(hues)
    b["hues"] = {k: v for k, v in b["hues"].items() if v is not None}
    return json.dumps(b)


REFUSALS = [
    ("not JSON", '{"neutral":', "Expecting value"),
    ("a list", "[]", "the brand must be an object"),
    ("NaN", json.dumps(HOUSE).replace("0.15", "NaN"), "NaN is not a number"),
    ("a repeated key", '{"neutral":{"hue":1,"chroma":0},"neutral":{"hue":2,"chroma":0},"hues":{}}',
     "key 'neutral' appears twice"),
    ("a missing role hue", with_hues(red=None), "hues is missing 'red'"),
    ("nine hues", with_hues(x={"hue": 1, "chroma": .1}, y={"hue": 2, "chroma": .1}), "at most 8"),
    ("a string hue and a bool chroma", with_hues(accent={"hue": "262", "chroma": True}),
     "hues.accent.hue must be a number"),
    ("a misspelt key", with_hues(accent={"hue": 262, "chroma": .15, "soild": {}}),
     "unknown key 'soild'"),
    ("hue 360", with_hues(accent={"hue": 360, "chroma": .1}), "[0, 360)"),
    ("chroma past 0.4", with_hues(accent={"hue": 1, "chroma": .5}), "(0, 0.4]"),
    ("a ramp named gray", with_hues(gray={"hue": 1, "chroma": .1}), "not 'gray'"),
    ("a null solid", with_hues(mark={"hue": 100, "chroma": .19, "solid": None}),
     "hues.mark.solid must be an object"),
    ("a solid that carries neither label",
     with_hues(accent={"hue": 262, "chroma": .15, "solid": {"light": .62, "dark": .62}}),
     "under 4.5:1"),
]


def malformed_brands_are_refused(fails):
    with tempfile.TemporaryDirectory() as tmp:
        for what, text, expect in REFUSALS:
            path = Path(tmp) / "bad.json"
            path.write_text(text, encoding="utf-8")
            r = subprocess.run([sys.executable, str(TOOL), str(path), "--out", tmp],
                               capture_output=True, text=True)
            if r.returncode != 1 or expect not in r.stderr or "Traceback" in r.stderr:
                fails.append(f"{what}: exit {r.returncode}, expected 1 naming {expect!r}; "
                             f"stderr: {r.stderr.strip()[:300]}")
            if (Path(tmp) / "bad.tokens.css").exists():
                fails.append(f"{what}: refused, but a file was written anyway")
    print(f"  refusals:     {len(REFUSALS)} malformed brand files, each refused by name")


def tampered(css, old, new):
    assert old in css, old
    return css.replace(old, new, 1)


def verify_refuses_a_broken_file(fails):
    css = (ROOT / "ramps" / "tokens" / "house.tokens.css").read_text(encoding="utf-8")
    light11 = re.search(r"--hw-accent-11: oklch\([0-9.]+ ", css)
    dark_head = '[data-theme="dark"] {\n'
    cases = [
        ("accent-11 lifted into its grounds",
         tampered(css, light11[0], "--hw-accent-11: oklch(0.700 ")),
        ("a white label on the mark", tampered(css, "--hw-mark-on-solid: var(--hw-gray-12);",
                                               "--hw-mark-on-solid: #FFFFFF;")),
        ("a fixed step moved",
         tampered(css, "--hw-gray-3: oklch(0.948", "--hw-gray-3: oklch(0.940")),
        ("the two dark blocks disagree", tampered(css, dark_head + "  --hw-gray-1: oklch(0.165",
                                                  dark_head + "  --hw-gray-1: oklch(0.166")),
        ("a step dropped", tampered(css, "  --hw-red-12:", "  --hw-red-x:")),
    ]
    for what, broken in cases:
        if not ramps.verify(broken)[0]:
            fails.append(f"verify() passed a file with {what}")
    print(f"  verify:       {len(cases)} broken files, each refused")


def main():
    fails = []
    print("tools/ramps.py, checked from outside")
    committed_files_are_fresh(fails)
    second_instrument_agrees(fails)
    floors_declared_twice(fails)
    roles_resolve(fails)
    step_9_is_brightest(fails)
    malformed_brands_are_refused(fails)
    verify_refuses_a_broken_file(fails)
    contrast_refuses(fails)
    separation_sweep(fails)
    every_hue_is_open(fails)
    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
