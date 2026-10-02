#!/usr/bin/env python3
"""The component layer, checked from outside, against the exports it loads after.

components/components.css is plain CSS that names house properties, so the checks are about
what it may name and what it may paint:

  1. tools/components.py --check: every sheet and render is current
  2. every var(--hw-*) in the layer is declared by every brand's exports/variables.css, every one
     in a sheet's demo by the house's, and the layer declares no --hw- property of its own
  3. no literal colour outside the forced-colours block, and no literal length or duration
     except the ones declared in LITERALS with the reason each is a literal
  4. every rule that sets a text colour and a background together sets a pair tools/contrast.py
     certifies (its own role lists, imported, not copied), or one in EXCEPTIONS, which is
     measured here on every brand in both themes, float and 8-bit
  5. no text smaller than 1em that is not held to the 11px floor with max()
  6. exactly one script, radiogroup.js, and every icon used is vendored with Lucide's licence

Each check has a negative control: a wrong input that must be refused, so a green run cannot be
a suite that checks nothing. What it cannot see is a rendered page; the browser pass that rendered
every sheet is the release step in AGENTS.md, and its renders are stamped by rule 1.

    python3 tests/components.py
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import contrast  # noqa: E402  the second instrument's own role lists and converter
import runpy  # noqa: E402

CSS = ROOT / "components" / "components.css"

# Every literal the layer may write, with why it is not a token.
LITERALS = {
    "0px": "a zero inside max()",
    "1px": "a hairline: the link underline and the meter bar's corner",
    "-1px": "the inset focus ring on a field sits over its 1px edge",
    "2px": "a 2px stroke or inset: keycap edge, slider ring, segmented inset, avatar and pin ring",
    "-2px": "the inset focus ring on a menu item",
    "4px": "twice the segmented control's 2px inset",
    "11px": "the type floor the scales hold (--hw-text-xs is max(0.8rem, 11px))",
    "24px": "the WCAG 2.2 2.5.8 target floor",
    "44px": "the coarse-pointer target floor the scales hold",
    "500ms": "the tooltip's delay in; no duration token is a delay",
    "0.8s": "the busy spinner's period; a loop has no duration token",
    "1.4s": "the indeterminate sweep's period; a loop has no duration token",
    "0s": "the tooltip's visibility flips at the end of its fade, with no duration of its own",
}
SYSTEM_COLOURS = {"Highlight", "HighlightText", "Canvas", "CanvasText"}

# Pairs the layer paints that contrast.py's role lists do not hold, measured here instead.
# (foreground, background, theme it is painted in, bar, why)
EXCEPTIONS = [
    ("--hw-text", "--hw-mark-7", "dark", 4.5,
     "the dark highlight: a block in mark step 7, since a swipe under light text measured 1.15:1"),
]

FG_PROPS = ("color", "--_fg", "--_on")
BG_PROPS = ("background", "background-color", "--_bg", "--_field", "--_f")


def rules_of(text):
    """[(media, selector, {prop: value})] for every style rule."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out, stack, buf = [], [], ""
    for ch in text:
        if ch == "{":
            stack.append(" ".join(buf.split()))
            buf = ""
        elif ch == "}":
            head = stack.pop() if stack else ""
            if not head.startswith("@"):
                media = next((s for s in reversed(stack) if s.startswith("@")), None)
                decls = dict(tuple(x.strip() for x in d.split(":", 1)) for d in buf.split(";") if ":" in d)
                out.append((media, head, decls))
            buf = ""
        else:
            buf += ch
    return out


def declared(path):
    return set(re.findall(r"(--hw-[a-z0-9-]+)\s*:", path.read_text(encoding="utf-8")))


def role(value):
    """The one --hw- property a colour value names, or None for anything else."""
    m = re.fullmatch(r"var\((--hw-[a-z0-9-]+)\)", value.strip())
    return m.group(1) if m else None


def certified():
    pairs = {(fg, bg) for fg in contrast.ROLE_TEXT
             for bg in contrast.ROLE_GROUNDS + contrast.ROLE_FILLS + contrast.ROLE_TINTS}
    pairs |= {(fg, bg) for fg, bgs in contrast.ROLE_LABELS.items() for bg in bgs}
    pairs |= {(contrast.ROLE_DISABLED, bg) for bg in contrast.ROLE_GROUNDS}
    return pairs


def pairs_in(rules):
    """(selector, fg, bg) for every rule that paints a text colour over a background, with a
    component's base background carried to a variant that sets only its foreground."""
    base = {}
    for media, sel, d in rules:
        if re.fullmatch(r"\.hw-[a-z-]+", sel):
            for p in BG_PROPS:
                if p in d:
                    base[sel] = d[p]
    out = []
    for media, sel, d in rules:
        if media and "forced-colors" in media:
            continue
        fg = next((d[p] for p in FG_PROPS if p in d), None)
        bg = next((d[p] for p in BG_PROPS if p in d), None)
        if fg and not bg:
            owner = re.match(r"(\.hw-[a-z]+)(?:--[a-z-]+)?$", sel)
            bg = base.get(owner.group(1)) if owner else None
        if fg and bg and role(fg) and role(bg):
            out.append((sel, role(fg), role(bg)))
    return out


def check_tokens(text, exports, demos):
    """A demo is drawn on the house exports; a demo token a brand lacks, such as quoth's live
    hue, falls back inside the layer (the meter reads var(--_live, var(--hw-accent)))."""
    bad = []
    used = set(re.findall(r"var\((--hw-[a-z0-9-]+)", text))
    for path, names in exports.items():
        bad += [f"{n} is not declared by {path}" for n in sorted(used - names)]
    shown = set(re.findall(r"var\((--hw-[a-z0-9-]+)", demos))
    bad += [f"{n}, in a demo, is not declared by exports/variables.css" for n in sorted(shown - exports["exports/variables.css"])]
    own = set(re.findall(r"(--hw-[a-z0-9-]+)\s*:", re.sub(r"/\*.*?\*/", "", text, flags=re.S)))
    bad += [f"the layer declares {n}; a component reads the house, never redefines it" for n in sorted(own)]
    return bad


def check_literals(text):
    bad, body = [], re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    forced = re.search(r"@media \(forced-colors: active\) \{.*?\n\}", body, re.S)
    rest = body.replace(forced.group(0), "") if forced else body
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\(", rest):
        bad.append(f"a literal colour {m.group(0)!r}")
    for word in SYSTEM_COLOURS:
        if re.search(rf"\b{word}\b", rest):
            bad.append(f"the system colour {word} outside the forced-colours block")
    for lit in sorted(set(re.findall(r"(?<![\w.-])-?\d*\.?\d+(?:px|ms|s)\b", rest))):
        if lit not in LITERALS:
            bad.append(f"the literal {lit} is not declared in LITERALS")
    return bad


def check_pairs(rules, envs):
    ok, bad, rows = certified(), [], []
    excepted = {(fg, bg) for fg, bg, *_ in EXCEPTIONS}
    for sel, fg, bg in pairs_in(rules):
        if (fg, bg) not in ok and (fg, bg) not in excepted:
            bad.append(f"{sel} paints {fg} on {bg}, a pair tools/contrast.py does not certify")
    for fg, bg, theme, bar, why in EXCEPTIONS:
        for brand, env in envs.items():
            for tier in ("", "-more"):
                e = env.get(theme + tier)
                if e is None:
                    continue
                f8 = contrast.ratio(contrast.resolve(fg, e), contrast.resolve(bg, e))
                low = min(f8)
                rows.append(f"{brand} {theme}{tier} {fg} on {bg}: {low:.2f}:1")
                if low < bar:
                    bad.append(f"{brand} {theme}{tier}: {fg} on {bg} is {low:.2f}:1, under {bar} ({why})")
    return bad, rows


def check_type_floor(text):
    bad = []
    body = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for m in re.finditer(r"(font-size|font)\s*:\s*([^;}]+)", body):
        value = m.group(2)
        if "max(" in value:
            continue
        for em in re.findall(r"(?<![\w.(])(\d*\.\d+)em\b", value):
            if float(em) < 1:
                bad.append(f"{m.group(0).strip()!r} sets text at {em}em with no 11px floor")
    return bad


def check_files():
    bad = []
    scripts = sorted(p.name for p in (ROOT / "components").glob("*.js"))
    if scripts != ["radiogroup.js"]:
        bad.append(f"the layer ships {scripts}; it is one script, radiogroup.js")
    if "ISC License" not in (ROOT / "components" / "icons" / "LICENSE").read_text(encoding="utf-8"):
        bad.append("components/icons/LICENSE is not Lucide's ISC licence")
    return bad


def ramp_envs():
    """{brand: {theme: env}} built the way contrast.py builds them."""
    out = {}
    lb, _ = contrast.declarations(contrast.RAMPS_DIR / "roles.css", contrast.ROLE_BLOCKS)
    for tokens in sorted((contrast.RAMPS_DIR / "tokens").glob("*.tokens.css")):
        rb, _ = contrast.declarations(tokens, contrast.RAMP_BLOCKS)
        brand = tokens.name.split(".")[0]
        out[brand] = {}
        for theme in ("light", "dark"):
            roles = {**lb["base"], **(lb.get("dark", {}) if theme == "dark" else {})}
            out[brand][theme] = {**rb[theme], **roles}
            out[brand][theme + "-more"] = {**rb[theme], **roles, **lb.get("more", {})}
    return out


def generator_check(tree):
    return subprocess.run([sys.executable, str(tree / "tools" / "components.py"), "--check"],
                          capture_output=True, text=True)


def main():
    fails = []
    text = CSS.read_text(encoding="utf-8")
    rules = rules_of(text)
    exports = {str(p.relative_to(ROOT)): declared(p) for p in sorted(ROOT.glob("**/exports/variables.css"))}
    demos = "\n".join(c["demo"] for c in runpy.run_path(str(ROOT / "components" / "catalogue.py"))["COMPONENTS"])
    envs = ramp_envs()

    r = generator_check(ROOT)
    if r.returncode:
        fails.append("tools/components.py --check:\n" + r.stderr.strip())
    print(f"  generated:    {r.stdout.strip()}")

    got = check_tokens(text, exports, demos)
    fails += got
    used = set(re.findall(r"var\((--hw-[a-z0-9-]+)", text + demos))
    print(f"  tokens:       {len(used)} house properties named by the layer and its demos, the layer's declared by all {len(exports)} exports")
    got = check_literals(text)
    fails += got
    print(f"  literals:     {len(LITERALS)} declared, {len(got)} undeclared")
    got, rows = check_pairs(rules, envs)
    fails += got
    print(f"  pairs:        {len(pairs_in(rules))} rules paint text on a background, all certified or excepted")
    for row in rows:
        print(f"                exception {row}")
    got = check_type_floor(text)
    fails += got
    print(f"  type floor:   {len(got)} sub-1em sizes without the 11px floor")
    fails += check_files()

    # Negative controls: each replays a mistake and must be caught.
    btn = ".hw-btn--primary { --_bg: var(--hw-ink); --_fg: var(--hw-on-ink);"
    cases = [
        ("an undeclared token", lambda: check_tokens(text.replace("var(--hw-line-strong)", "var(--hw-line-strongest)", 1), exports, demos)),
        ("the layer redefining a house token", lambda: check_tokens(text + "\n.hw-x { --hw-text: red; }", exports, demos)),
        ("a literal hex colour", lambda: check_literals(text.replace("var(--hw-ink)", "#111111", 1))),
        ("an undeclared literal length", lambda: check_literals(text.replace("var(--hw-space-12)", "13px", 1))),
        ("muted text on the ink solid", lambda: check_pairs(rules_of(text.replace(btn, ".hw-btn--primary { --_bg: var(--hw-ink); --_fg: var(--hw-text-muted);")), envs)[0]),
        ("a label on the wrong solid", lambda: check_pairs(rules_of(text.replace(btn, ".hw-btn--primary { --_bg: var(--hw-accent); --_fg: var(--hw-on-ink);")), envs)[0]),
        ("a 0.8em keycap with no floor", lambda: check_type_floor(text.replace("max(0.8em, 11px)", "0.8em", 1))),
    ]
    if btn not in text:
        fails.append("negative controls: the primary button rule they edit has moved")
    clean = {"tokens": set(check_tokens(text, exports, demos)), "literals": set(check_literals(text)),
             "pairs": set(check_pairs(rules, envs)[0]), "type": set(check_type_floor(text))}
    before = set().union(*clean.values())
    for label, run in cases:
        caught = [f for f in run() if f not in before]
        if not caught:
            fails.append(f"negative control not caught: {label}")
        print(f"  control:      {label}: {'caught' if caught else 'MISSED'}, first: {caught[0] if caught else '-'}")

    # The generator's own refusals, on a copy of the tree.
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        for part in ("components", "tools", "design", "exports"):
            shutil.copytree(ROOT / part, tree / part)
        cat = tree / "components" / "catalogue.py"
        original = cat.read_text(encoding="utf-8")
        for label, edit in (
            ("a stale sheet", lambda s: s.replace("Starts an action whose verb is its label.", "Starts an action.")),
            ("a demo using a class the layer does not define", lambda s: s.replace('class="hw-btn hw-btn--quiet"', 'class="hw-btn hw-btn--ghost"', 1)),
            ("an icon that is not vendored", lambda s: s.replace("{{icon:copy}}", "{{icon:clipboard}}", 1)),
            ("an em dash in a sheet", lambda s: s.replace("Starts an action whose verb", "Starts an action \u2014 whose verb", 1)),
        ):
            cat.write_text(edit(original), encoding="utf-8")
            r = generator_check(tree)
            first = (r.stderr.strip().splitlines() or ["-"])[0]
            if r.returncode == 0:
                fails.append(f"negative control not caught: {label}")
            print(f"  control:      {label}: {'caught' if r.returncode else 'MISSED'}, first: {first}")
        cat.write_text(original, encoding="utf-8")
        css = tree / "components" / "components.css"
        css.write_text(css.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        r = generator_check(tree)
        if r.returncode == 0:
            fails.append("negative control not caught: a render older than the CSS")
        print(f"  control:      a render older than the CSS: {'caught' if r.returncode else 'MISSED'}, "
              f"first: {(r.stderr.strip().splitlines() or ['-'])[0]}")

    for f in fails:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
