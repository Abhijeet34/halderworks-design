#!/usr/bin/env python3
"""The CSS a product loads, cascaded the way a browser does, in every condition it answers.

tools/export.py proves its files equal their sources block for block, which cannot see a source
that is itself wrong, such as a touch rule a compact ancestor overrides. This reads every
exports/variables.css and exports/theme.css from outside, with its own parser and cascade, and
for each theme (light, [data-theme="dark"], prefers-color-scheme: dark), contrast setting,
pointer, motion preference and text size cascades the root and a compact descendant, then holds
them to what the book promises:

  1. the root is 13, 15, 17, 19 and 22px at S to XXL, at the browser's default 16px
  2. no type step renders under 11px at any text size
  3. under a coarse pointer a control is at least 44px, compact or not, and 24px always
  4. reduced motion collapses every duration to 100ms, and only then
  5. the prefers-color-scheme copy equals [data-theme="dark"], property for property
  6. under prefers-contrast: more, muted text is step 12
  7. every var() resolves, and theme.css cascades exactly as variables.css does
  8. every space and size value is on the 4px unit at M, or is a declared exception below, and
     no declared exception has moved back onto the unit (design/30-space.md)

Four negative controls replay a defect this suite exists to catch, among them the touch block
as it shipped before the compact fix, and each must be refused, so a green run cannot be a suite
that checks nothing.

    python3 tests/exports.py
"""
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZES = {"s": 13, "m": 15, "l": 17, "xl": 19, "xxl": 22}
DEFAULT_PX = 16
TOUCH_FLOOR = 44
TARGET_FLOOR = 24           # WCAG 2.2 2.5.8 (design/60-accessibility.md)
TYPE_FLOOR = 11
UNIT = 4
# The space and size families the unit governs, pinned here rather than read from a file a
# change could narrow. Radius and stroke are not distances, and the line box is a type size times
# a line-height, so the unit governs none of them (design/30-space.md).
GRID = re.compile(r"--hw-(space|control-h|row-h|cell-pad|field-pad|icon(-sm|-lg|-gap)?$|bp|"
                  r"gutter|column-gap|container|rail|panel)")
OFF_UNIT = {
    "--hw-icon-gap": "6px: 4px reads as an icon and its label as one object, 8px as two",
    "--hw-icon-sm": "14px beside 12px label text; on the unit it is too small at 12 or overshoots at 16",
    "--hw-field-pad-y": "7px, what is left of the 32px control after the line box and the border",
    "--hw-field-pad-y-compact": "3px, the same consequence at the compact control height",
    "--hw-cell-pad-y-compact": "6px: 19.5px of line box plus 6px above and below is the 32px compact row",
}
MEDIA = {"(prefers-color-scheme: dark)": "scheme_dark", "(prefers-contrast: more)": "more",
         "(pointer: coarse)": "coarse", "(prefers-reduced-motion: reduce)": "reduce"}


def parse(text):
    """[(media or None, selector, [(property, value)])], source order kept."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out, stack, buf = [], [], ""
    for ch in text:
        if ch == "{":
            head = " ".join(buf.split(";")[-1].split())
            stack.append(head)
            buf = ""
        elif ch == "}":
            head = stack.pop()
            if not head.startswith("@media"):
                media = stack[-1][len("@media"):].strip() if stack else None
                decls = [tuple(x.strip() for x in d.split(":", 1))
                         for d in buf.split(";") if ":" in d]
                out.append((media, head, decls))
            buf = ""
        else:
            buf += ch
    return out


def media_holds(media, env):
    if media is None:
        return True
    return all(env[MEDIA[part.strip()]] for part in media.split(" and "))


def specificity(part, el):
    """(attributes and pseudo-classes, types) if the compound matches el, else None."""
    is_root = el["root"]
    m = re.fullmatch(r'\[data-(theme|density)="([a-z]+)"\]', part)
    if m:
        return (1, 0) if el.get(m.group(1)) == m.group(2) else None
    m = re.fullmatch(r'html\[data-text-size="([a-z]+)"\]', part)
    if m:
        return (1, 1) if is_root and el.get("size") == m.group(1) else None
    if part == ":root":
        return (1, 0) if is_root else None
    if part == "html":
        return (0, 1) if is_root else None
    if part == ':root:not([data-theme="light"])':
        return (2, 0) if is_root and el.get("theme") != "light" else None
    if part in ("*", "*::before", "*::after") or part.startswith("@theme") or \
            part.startswith(".hw-"):
        return None             # sets no custom property and no root size
    raise ValueError(f"tests/exports.py cannot match selector {part!r}; teach it before trusting it")


def cascade(rules, el, env, inherited):
    won = dict(inherited)
    hits = []
    for order, (media, sel, decls) in enumerate(rules):
        if not media_holds(media, env):
            continue
        spec = max((s for s in (specificity(p.strip(), el) for p in sel.split(",")) if s),
                   default=None)
        if spec:
            hits += [(spec, order, k, v) for k, v in decls if k.startswith("--") or k == "font-size"]
    for _, _, k, v in sorted(hits, key=lambda h: (h[0], h[1])):
        won[k] = v
    return won


def resolve(value, props, depth=0):
    if depth > 10:
        raise ValueError(f"var() cycle at {value}")
    def sub(m):
        if m.group(1) not in props:
            raise KeyError(m.group(1))
        return resolve(props[m.group(1)], props, depth + 1)
    return re.sub(r"var\((--[a-z0-9-]+)\)", sub, value)


def px(value, root_px):
    value = value.strip()
    m = re.fullmatch(r"max\((.*)\)", value)
    if m:
        return max(px(p, root_px) for p in re.split(r",(?![^(]*\))", m.group(1)))
    m = re.fullmatch(r"(-?[\d.]+)(px|rem)", value)
    if not m:
        raise ValueError(f"not a length: {value!r}")
    return float(m.group(1)) * (root_px if m.group(2) == "rem" else 1)


def scenario(rules, theme, scheme_dark, more, coarse, reduce, size):
    env = {"scheme_dark": scheme_dark, "more": more, "coarse": coarse, "reduce": reduce}
    root = cascade(rules, {"root": True, "theme": theme, "size": size}, env, {})
    child = cascade(rules, {"root": False, "density": "compact"}, env,
                    {k: v for k, v in root.items() if k.startswith("--")})
    return root, child


def scenarios():
    for theme, scheme_dark in ((None, False), ("dark", False), (None, True)):
        for more, coarse, reduce in itertools.product((False, True), repeat=3):
            for size in SIZES:
                yield (theme, scheme_dark, more, coarse, reduce, size)


def check(name, text, fails):
    rules, n = parse(text), 0
    seen = {}
    for sc in scenarios():
        theme, scheme_dark, more, coarse, reduce, size = sc
        root, child = scenario(rules, *sc)
        where = (f"{name} theme={theme or 'none'} scheme={'dark' if scheme_dark else 'light'} "
                 f"more={more} coarse={coarse} reduce={reduce} size={size}")
        n += 1
        try:
            root_px = DEFAULT_PX * float(root.get("font-size", "100%").rstrip("%")) / 100
            if abs(root_px - SIZES[size]) > 0.01:
                fails.append(f"{where}: root {root_px:g}px, not {SIZES[size]}px")
            for el, props in (("root", root), ("compact", child)):
                h = px(resolve(props["--hw-control-h"], props), root_px)
                if coarse and h < TOUCH_FLOOR:
                    fails.append(f"{where}: a {el} control is {h:g}px under a coarse pointer")
                if h < TARGET_FLOOR - 0.01:
                    fails.append(f"{where}: a {el} control is {h:g}px, under {TARGET_FLOOR}px")
            for k in [k for k in root if re.fullmatch(r"--hw-text-(xs|sm|md|lg|x+l|2xl)", k)]:
                got = px(resolve(root[k], root), root_px)
                if got < TYPE_FLOOR - 0.01:
                    fails.append(f"{where}: {k} renders at {got:.2f}px")
            want = "100ms" if reduce else None
            for k, base in (("fast", "120ms"), ("base", "200ms"), ("slow", "320ms")):
                got = root[f"--hw-duration-{k}"]
                if got != (want or base):
                    fails.append(f"{where}: --hw-duration-{k} is {got}, not {want or base}")
            if more and resolve(root["--hw-text-muted"], root) != resolve("var(--hw-gray-12)", root):
                fails.append(f"{where}: muted text is not step 12 under contrast more")
            resolved = {k: resolve(v, root) for k, v in root.items() if k.startswith("--")}
        except KeyError as exc:
            fails.append(f"{where}: var({exc.args[0]}) names nothing")
            continue
        if theme == "dark" or scheme_dark:
            key = (more, coarse, reduce, size)
            other = seen.setdefault(key, resolved)
            if other is not resolved:
                diff = sorted(k for k in set(other) | set(resolved) if other.get(k) != resolved.get(k))
                if diff:
                    fails.append(f"{where}: the scheme copy and [data-theme=dark] differ on "
                                 f"{', '.join(diff[:4])}")
    return n


def grid(name, text, fails):
    """Every space and size length at the default size M, on the unit or declared, both ways."""
    root, _ = scenario(parse(text), None, False, False, False, False, "m")
    n = 0
    for k in sorted(k for k in root if GRID.match(k)):
        n += 1
        try:
            v = round(px(resolve(root[k], root), SIZES["m"]), 1)
        except ValueError:
            fails.append(f"{name}: {k} is {root[k]!r}, a length the {UNIT}px unit governs and "
                         f"this check cannot read")
            continue
        if v % UNIT == 0 and k in OFF_UNIT:
            fails.append(f"{name}: {k} is a declared exception at {v:g}px, which is on the "
                         f"{UNIT}px unit; remove the exception")
        elif v % UNIT and k not in OFF_UNIT:
            fails.append(f"{name}: {k} is {v:g}px at M, off the {UNIT}px unit, and not a "
                         f"declared exception")
    for k in OFF_UNIT:
        if k not in root:
            fails.append(f"{name}: {k} is a declared exception and names nothing")
    return n


def cascade_digest(text):
    rules = parse(text)
    return [scenario(rules, *sc) for sc in scenarios()]


def main():
    fails = []
    exports = sorted({p.parent for p in ROOT.glob("**/exports/variables.css")})
    n = 0
    for d in exports:
        rel = d.relative_to(ROOT)
        v = (d / "variables.css").read_text(encoding="utf-8")
        t = (d / "theme.css").read_text(encoding="utf-8")
        n += check(f"{rel}/variables.css", v, fails)
        g = grid(f"{rel}/variables.css", v, fails)
        if cascade_digest(v) != cascade_digest(t):
            fails.append(f"{rel}/theme.css does not cascade as {rel}/variables.css does")
    print(f"  exports:      {n} scenarios over {len(exports)} brands, root and compact child, "
          f"theme.css cascading identically")
    print(f"  unit:         {g} space and size values per brand at M, each on the {UNIT}px unit "
          f"but the {len(OFF_UNIT)} declared off it")

    # Negative controls: each replays one defect and must be refused.
    house = (ROOT / "exports" / "variables.css").read_text(encoding="utf-8")
    coarse = re.search(r"@media \(pointer: coarse\) \{.*?\n\}\n", house, re.S).group(0)
    before_fix = house.replace(coarse, "").replace(
        '[data-density="compact"] {',
        "@media (pointer: coarse) {\n  :root { --hw-control-h: max(44px, 2.1333rem); }\n}\n"
        '[data-density="compact"] {', 1)
    cases = [
        ("the touch block before the compact one, as tokens.css shipped it", before_fix),
        ("no prefers-color-scheme copy",
         re.sub(r"@media \(prefers-color-scheme: dark\) \{.*?\n\}\n", "", house, flags=re.S)),
        ("text size S left at the M root",
         re.sub(r'html\[data-text-size="s"\] \{ font-size: [^;]+;', 'html[data-text-size="s"] '
                "{ font-size: 93.75%;", house)),
        ("a space step moved off the unit, 12px to 13px",
         house.replace("--hw-space-12: 0.8rem;", "--hw-space-12: 0.8667rem;", 1)
         if "--hw-space-12: 0.8rem;" in house else ""),
    ]
    for label, text in cases:
        got = []
        if not text:
            fails.append(f"negative control {label!r} has no input")
            continue
        check("control", text, got)
        grid("control", text, got)
        if not got:
            fails.append(f"negative control not caught: {label}")
        print(f"  control:      {label}: {'caught' if got else 'MISSED'}, {len(got)} finding(s), "
              f"first: {got[0] if got else '-'}")

    for f in fails:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
