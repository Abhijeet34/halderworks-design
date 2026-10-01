#!/usr/bin/env python3
"""The claims tools/ramps.py makes, checked from outside it.

  1. The committed ramps/tokens/*.tokens.css are what the brand files build (`--check`).
  2. Every floor and solid label in them holds when re-measured by tools/contrast.py's converter,
     which shares no arithmetic with tools/ramps.py, on the float value and on the 8-bit value,
     and every written triple is inside sRGB by that converter's tolerance.
  3. Every var() in ramps/roles.css resolves in every brand, so a role cannot name a step a brand
     does not emit.
  4. Every accent hue is open: all 360 at chroma 0.15, every fifth at the 0.4 chroma ceiling,
     and every tenth as a named light solid that carries ink, each building and verifying.
  5. Step 9 is the brightest solid that carries white: 0.001 brighter misses the solve's target.
  6. A malformed brand file is refused with a sentence, never a traceback.
  7. verify() refuses a written file that breaks a floor, a label, a fixed step or the two dark
     blocks' agreement, so the re-measure is a check rather than a formality.

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
HOUSE = json.loads((ROOT / "ramps" / "brands" / "house.json").read_text(encoding="utf-8"))


def committed_files_are_fresh(fails):
    r = subprocess.run([sys.executable, str(TOOL), "--check"], capture_output=True, text=True)
    if r.returncode:
        fails.append(f"tools/ramps.py --check exited {r.returncode}:\n{r.stderr}")
    print(f"  fresh:        tools/ramps.py --check exit {r.returncode}")


def second_instrument_agrees(fails):
    """The floors re-measured by contrast.py's CSS Color 4 path rather than ramps.py's own."""
    n, low = 0, {}
    files = sorted((ROOT / "ramps" / "tokens").glob("*.tokens.css"))
    for path in files:
        blocks = ramps.parse(path.read_text(encoding="utf-8"))
        for theme in ("light", "dark"):
            rs = blocks[theme]
            for name, r in rs.items():
                for i in range(1, 13):
                    if not contrast.in_gamut(*r[i]):
                        fails.append(f"{path.name} {theme} {name}-{i} is outside sRGB "
                                     "by contrast.py")
            for step, (floor, span) in ramps.FLOORS.items():
                for name, r in rs.items():
                    for g in rs:
                        for i in span:
                            got = min(contrast.ratio(r[step], rs[g][i]))
                            n += 1
                            low[step] = min(low.get(step, 99), got)
                            if got < floor:
                                fails.append(f"{path.name} {theme} {name}-{step} on {g}-{i}: "
                                             f"{got:.3f} by contrast.py, under {floor}")
            ink = rs["gray"][12 if theme == "light" else 1]
            for name, r in rs.items():
                label = (1.0, 0.0, 0.0) if r["on-solid"] == ramps.WHITE else ink
                for i in (9, 10):
                    got = min(contrast.ratio(label, r[i]))
                    n += 1
                    low["label"] = min(low.get("label", 99), got)
                    if got < ramps.LABEL:
                        fails.append(f"{path.name} {theme} {name}-{i} label {r['on-solid']}: "
                                     f"{got:.3f} by contrast.py, under {ramps.LABEL}")
    print(f"  second view:  {n} pairs over {len(files)} brands by contrast.py, float and 8-bit; "
          f"lowest " + ", ".join(f"{k} {v:.3f}" for k, v in low.items()))


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
    roles_resolve(fails)
    step_9_is_brightest(fails)
    malformed_brands_are_refused(fails)
    verify_refuses_a_broken_file(fails)
    every_hue_is_open(fails)
    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
