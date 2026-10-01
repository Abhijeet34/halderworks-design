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

Rule 3 is also held on every tokens/tokens.css. Four negative controls replay a defect this
suite exists to catch, among them the touch block as it shipped before the compact fix, and each
must be refused, so a green run cannot be a suite that checks nothing.

    python3 tests/exports.py
"""
import itertools
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZES = {"s": 13, "m": 15, "l": 17, "xl": 19, "xxl": 22}
DEFAULT_PX = 16
TOUCH_FLOOR = 44
TARGET_FLOOR = 24           # WCAG 2.2 2.5.8, and the ring geometry design/45-density.md sizes for
TYPE_FLOOR = 11
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


def check(name, text, fails, touch_only=False):
    rules, n = parse(text), 0
    seen = {}
    for sc in scenarios():
        theme, scheme_dark, more, coarse, reduce, size = sc
        root, child = scenario(rules, *sc)
        where = (f"{name} theme={theme or 'none'} scheme={'dark' if scheme_dark else 'light'} "
                 f"more={more} coarse={coarse} reduce={reduce} size={size}")
        n += 1
        try:
            root_px = DEFAULT_PX * float(root.get("font-size", "100%").rstrip("%")) / 100 \
                if not touch_only else DEFAULT_PX
            if not touch_only and abs(root_px - SIZES[size]) > 0.01:
                fails.append(f"{where}: root {root_px:g}px, not {SIZES[size]}px")
            for el, props in (("root", root), ("compact", child)):
                h = px(resolve(props["--hw-control-h"], props), root_px)
                if coarse and h < TOUCH_FLOOR:
                    fails.append(f"{where}: a {el} control is {h:g}px under a coarse pointer")
                if h < TARGET_FLOOR - 0.01:
                    fails.append(f"{where}: a {el} control is {h:g}px, under {TARGET_FLOOR}px")
            if touch_only:
                continue
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
        if cascade_digest(v) != cascade_digest(t):
            fails.append(f"{rel}/theme.css does not cascade as {rel}/variables.css does")
    print(f"  exports:      {n} scenarios over {len(exports)} brands, root and compact child, "
          f"theme.css cascading identically")
    tokens = sorted(ROOT.glob("**/tokens/tokens.css"))
    for p in tokens:
        check(str(p.relative_to(ROOT)), p.read_text(encoding="utf-8"), fails, touch_only=True)
    print(f"  touch floor:  held on {len(tokens)} tokens/tokens.css, compact or not")

    # Negative controls: each replays one defect and must be refused.
    house = (ROOT / "exports" / "variables.css").read_text(encoding="utf-8")
    coarse = re.search(r"@media \(pointer: coarse\) \{.*?\n\}\n", house, re.S).group(0)
    before_fix = house.replace(coarse, "").replace(
        '[data-density="compact"] {',
        "@media (pointer: coarse) {\n  :root { --hw-control-h: max(44px, 2.1333rem); }\n}\n"
        '[data-density="compact"] {', 1)
    shipped = subprocess.run(["git", "show", "1250209:tokens/tokens.css"], cwd=ROOT,
                             capture_output=True, text=True).stdout
    cases = [
        ("the touch block before the compact one, as tokens.css shipped it",
         before_fix, False),
        ("tokens/tokens.css at 1250209, before this fix", shipped, True),
        ("no prefers-color-scheme copy",
         re.sub(r"@media \(prefers-color-scheme: dark\) \{.*?\n\}\n", "", house, flags=re.S), False),
        ("text size S left at the M root",
         re.sub(r'html\[data-text-size="s"\] \{ font-size: [^;]+;', 'html[data-text-size="s"] '
                "{ font-size: 93.75%;", house), False),
    ]
    for label, text, touch_only in cases:
        got = []
        if not text:
            fails.append(f"negative control {label!r} has no input")
            continue
        check("control", text, got, touch_only=touch_only)
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
