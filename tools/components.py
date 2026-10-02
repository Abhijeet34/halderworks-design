#!/usr/bin/env python3
"""Generate the component sheets from components/catalogue.py and components/components.css.

    python3 tools/components.py            # write components/sheets/*.html and design/64-component-sheets.md
    python3 tools/components.py --check    # write nothing; fail if either is stale or a render is
    python3 tools/components.py --stamp    # record the renders in components/renders/ as current

One source, two outputs: each catalogue entry becomes a card on its group's rendered page and a
section of the Markdown sheet, so the words and the render cannot drift apart. A component's token
list is read from the CSS rules that name its classes rather than written by hand, so a sheet
cannot name a token the component does not use or miss one it does.

It refuses to emit, naming the entry, when an entry leaves a field empty, names a class the CSS
does not define, uses an hw- class in its demo that the CSS does not define, names an icon not
vendored in components/icons/, or carries an em dash. The renders are screenshots taken in a
browser, which nothing here can take; --stamp records the sha256 of the inputs they were taken
from, and --check refuses once those inputs change, so a stale render cannot sit beside a sheet.
"""
import hashlib
import html
import json
import re
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = ROOT / "components"
CSS = COMP / "components.css"
ICONS = COMP / "icons"
SHEETS = COMP / "sheets"
RENDERS = COMP / "renders"
MANIFEST = RENDERS / "manifest.json"
BOOK = ROOT / "design" / "64-component-sheets.md"
FIELDS = ("name", "verdict", "used", "purpose", "notfor", "anatomy", "states", "keyboard", "do",
          "dont", "demo")
THEMES = ("light", "dark")
SIZES = ("s", "m", "l", "xl", "xxl")


def slug(text):
    """GitHub's heading anchor, the one tools/check-coverage.py resolves."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def css_rules(text):
    """[(selector, body)] for every style rule, inside at-rules or not."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    rules, stack, buf = [], [], ""
    for ch in text:
        if ch == "{":
            stack.append(" ".join(buf.split()))
            buf = ""
        elif ch == "}":
            head = stack.pop() if stack else ""
            if not head.startswith("@"):
                rules.append((head, buf))
            buf = ""
        else:
            buf += ch
    return rules


def classes_in(selector):
    return set(re.findall(r"\.(hw-[a-z0-9-]+)", selector))


def split_top(text, seps):
    """Split on any character in seps that sits outside parentheses."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        depth += (ch == "(") - (ch == ")")
        if ch in seps and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    return [p for p in parts + [cur] if p.strip()]


def owners(selector):
    """The classes a rule belongs to: those in the first compound that names an hw- class, so
    `.hw-tooltip .hw-kbd` is the tooltip's rule about a keycap and not the keycap's own."""
    found = set()
    for part in split_top(selector, ","):
        for compound in split_top(part, " >+~"):
            if classes_in(compound):
                found |= classes_in(compound)
                break
    return found


def tokens_for(classes, rules):
    """The --hw- properties read by every rule a component's classes own."""
    names = {c.lstrip(".") for c in classes}
    found = set()
    for sel, body in rules:
        if owners(sel) & names:
            found |= set(re.findall(r"var\((--hw-[a-z0-9-]+)", body))
    return sorted(found)


def icon(name):
    svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
    svg = re.sub(r'\s(width|height)="24"', "", svg)
    svg = re.sub(r'\sclass="[^"]*"', "", svg)
    svg = svg.replace('stroke-width="2"', 'stroke-width="1.75"')
    svg = svg.replace("<svg", '<svg aria-hidden="true" focusable="false"', 1)
    return " ".join(svg.split())


def expand(demo):
    return re.sub(r"\{\{icon:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), demo)


def validate(groups, comps, rules):
    defined = set().union(*(classes_in(s) for s, _ in rules))
    keys = {k for k, _ in groups}
    bad, seen = [], set()
    for c in comps:
        who = f"{c['name']!r}"
        bad += [f"{who}: {f} is empty" for f in FIELDS if not str(c.get(f, "")).strip()]
        bad += [f"{who}: {f} carries an em dash" for f in FIELDS if "\u2014" in str(c.get(f, ""))]
        if c["group"] not in keys:
            bad.append(f"{who}: group {c['group']!r} is not in GROUPS")
        if slug(c["name"]) in seen:
            bad.append(f"{who}: a second component with the same anchor")
        seen.add(slug(c["name"]))
        for cls in c["classes"]:
            if cls.lstrip(".") not in defined:
                bad.append(f"{who}: names {cls}, which components.css does not define")
        for cls in set(re.findall(r'class="([^"]*)"', c["demo"])):
            for name in cls.split():
                if name.startswith("hw-") and name not in defined:
                    bad.append(f"{who}: its demo uses .{name}, which components.css does not define")
        for name in re.findall(r"\{\{icon:([a-z0-9-]+)\}\}", c["demo"]):
            if not (ICONS / f"{name}.svg").exists():
                bad.append(f"{who}: icon {name!r} is not vendored in components/icons/")
        if not tokens_for(c["classes"], rules):
            bad.append(f"{who}: no rule for its classes reads a house token")
    owned = set().union(*({x.lstrip(".") for x in c["classes"]} for c in comps))
    for name in sorted(defined - owned):
        if not any(name.startswith(o + "--") for o in owned) and name not in SHARED:
            bad.append(f".{name} is defined in components.css and owned by no catalogue entry")
    return bad


# Classes the CSS defines that belong to no one component: type styles and helpers.
SHARED = {"hw-num", "hw-visually-hidden", "hw-headline", "hw-title", "hw-heading",
          "hw-subheading", "hw-lead", "hw-body", "hw-small", "hw-label", "hw-dialog-actions",
          "hw-callout-actions", "hw-confirm-actions"}

PAGE_STYLE = """
body { margin: 0; padding: var(--hw-space-32) var(--hw-gutter-md) var(--hw-space-64); background: var(--hw-bg); color: var(--hw-text); font: 400 var(--hw-text-md)/var(--hw-leading) var(--hw-font-sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1320px; margin: 0 auto; display: grid; gap: var(--hw-space-24); }
.top { display: grid; gap: var(--hw-space-8); }
.bench { display: flex; flex-wrap: wrap; gap: var(--hw-space-4) var(--hw-space-16); font-size: var(--hw-text-sm); }
.bench a { color: var(--hw-text-muted); }
.bench a[aria-current] { color: var(--hw-text); font-weight: 600; }
.bench a:focus-visible { outline: var(--hw-focus-w) solid var(--hw-focus); outline-offset: var(--hw-focus-offset); }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 36rem), 1fr)); gap: var(--hw-space-24); }
.cc { background: var(--hw-surface); border: var(--hw-border-w) solid var(--hw-line); border-radius: var(--hw-radius-lg); padding: var(--hw-space-24); display: grid; gap: var(--hw-space-16); align-content: start; min-width: 0; container-type: inline-size; }
.cc header { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: var(--hw-space-8); }
.demo { background: var(--hw-bg); border-radius: var(--hw-radius-md); padding: var(--hw-space-24); display: grid; gap: var(--hw-space-12); min-width: 0; container-type: inline-size; }
.demo > * { justify-self: start; max-width: 100%; }
.demo > :is(.hw-callout, .hw-list, .hw-diff, .grid2, .hw-confirm, .hw-tabs, .hw-field, .hw-stage, .backdrop, .hw-disclosure, .stack, .scroll, .hw-search, .hw-kv) { justify-self: stretch; }
.demo > :is(.narrow) { width: min(100%, 22rem); }
.row { display: flex; flex-wrap: wrap; gap: var(--hw-space-12); align-items: center; }
.row.top { align-items: flex-start; }
.row.tall { padding-top: var(--hw-space-32); }
.row.gap-lg { gap: var(--hw-space-32); }
.stack { display: grid; gap: var(--hw-space-8); justify-items: start; }
.stack.wide { width: min(100%, 26rem); justify-items: stretch; }
.spread { display: flex; flex-wrap: wrap; justify-content: space-between; gap: var(--hw-space-8); }
.grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr)); gap: var(--hw-space-16); }
.scroll { overflow-x: auto; }
.strong { color: var(--hw-text); }
.muted { color: var(--hw-text-muted); font-weight: 400; }
.large { font-size: var(--hw-text-lg); }
.framed { width: min(100%, 16rem); border: var(--hw-border-w) solid var(--hw-line); border-radius: var(--hw-radius-lg); }
.backdrop { padding: var(--hw-space-24); border-radius: var(--hw-radius-lg); display: grid; place-items: center; }
.sheetframe { place-items: stretch end; padding: 0; min-height: 20rem; overflow: hidden; }
.sheetframe > .hw-sheet { width: min(22rem, 100%); }
.hw-stage .hw-headline { margin: var(--hw-space-8) 0 var(--hw-space-12); }
.spec { grid-template-columns: 6.5rem 1fr; }
.spec code.tok { font: 400 0.88em/1.5 var(--hw-font-mono); white-space: nowrap; }
"""

BENCH = """(() => { const q = new URLSearchParams(location.search), h = document.documentElement;
  for (const [p, k] of [["theme", "theme"], ["text-size", "textSize"], ["density", "density"]]) { const v = q.get(p); if (v) h.dataset[k] = v; }
  const b = q.get("brand"); if (b && /^[a-z]+$/.test(b)) document.getElementById("hw-vars").href = `../../examples/${b}/exports/variables.css`; })();"""


def tok(text):
    """Keep a token name on one line: a break after its leading -- reads as two words."""
    return re.sub(r"(--hw-[a-z0-9-]+)", r'<code class="tok">\1</code>', text)


def card(c, rules):
    toks = ", ".join(tokens_for(c["classes"], rules))
    rows = [("For", c["purpose"]), ("Not for", c["notfor"]), ("Anatomy", c["anatomy"]),
            ("States", c["states"]), ("Keyboard", c["keyboard"]), ("Do", c["do"]),
            ("Do not", c["dont"])]
    dl = "".join(f"<dt>{k}</dt><dd>{tok(html.escape(v))}</dd>" for k, v in rows)
    return (f'<article class="cc" id="{slug(c["name"])}"><header><h2 class="hw-heading">{html.escape(c["name"])}</h2>'
            f'<span class="hw-badge hw-badge--plain">{html.escape(c["verdict"].split(":")[0])}</span></header>\n'
            f'<div class="demo">{expand(c["demo"])}</div>\n'
            f'<dl class="hw-kv spec">{dl}<dt>Tokens</dt><dd>{tok(toks)}</dd></dl></article>')


def page(key, title, groups, comps, rules):
    nav = " ".join(f'<a class="hw-link" href="{k}.html"{" aria-current=\"page\"" if k == key else ""}>{t}</a>'
                   for k, t in groups)
    bench = " ".join([f'<a href="?theme={t}">{t}</a>' for t in THEMES] +
                     [f'<a href="?text-size={s}">{s.upper()}</a>' for s in SIZES] +
                     ['<a href="?density=compact">compact</a>'])
    cards = "\n".join(card(c, rules) for c in comps if c["group"] == key)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Components: {title}</title>
<link id="hw-vars" rel="stylesheet" href="../../exports/variables.css">
<link rel="stylesheet" href="../components.css">
<script>{BENCH}</script>
<script src="../radiogroup.js" defer></script>
<style>{PAGE_STYLE}</style>
</head>
<body>
<!-- Generated by tools/components.py from components/catalogue.py. Do not hand-edit. -->
<main class="wrap">
<header class="top"><p class="hw-label">Halderworks components</p><h1 class="hw-title">{title}</h1>
<nav class="bench" aria-label="Groups">{nav}</nav>
<nav class="bench" aria-label="Render conditions">{bench}</nav></header>
<div class="cards">
{cards}
</div>
</main>
</body>
</html>
"""


INTRO = """# Component sheets

<!-- Generated by tools/components.py from components/catalogue.py and components/components.css. Do not hand-edit: edit those and run python3 tools/components.py. -->

{n} components in {g} groups, as plain CSS in [components/components.css](../components/components.css) over the house roles and scales, with one script, [components/radiogroup.js](../components/radiogroup.js), for the segmented control's arrow keys.
Each sheet below is generated from the same entry as its rendered card, and its token list is read from the CSS rules that name the component's classes, so it cannot name a token the component does not use.
Where a sheet and an older card in [65-components.md](65-components.md) differ, the sheet is the later decision.

## The component layer

Load it after the variables a brand exports, and load the script once:

```html
<link rel="stylesheet" href="exports/variables.css">
<link rel="stylesheet" href="components/components.css">
<script src="components/radiogroup.js" defer></script>
```

A product brand loads `examples/<brand>/exports/variables.css` in place of the house file and gets the same components in its own colour.
The layer names `hw-` properties and declares none of its own, except the `--_` locals a component sets on itself; a product extends in its own namespace.
Every size is in rem or em, so `html[data-text-size]` grows every box with its text, and `[data-density="compact"]`, `(pointer: coarse)`, `prefers-contrast: more` and `prefers-reduced-motion` reach every component through the variables it reads.
`forced-colors: active` redraws the checked and current states in system colours.

What the layer does not do: it positions nothing a product has to place (a toast's corner, a menu's anchor in an engine without anchor positioning), it captures no hotkey, and it moves focus only where a native element does.
Those are the product's, and each sheet's Keyboard line says which.

Open a group's page in a browser to see every state live, at any theme, text size, density or brand, with `?theme=dark`, `?text-size=xl`, `?density=compact` or `?brand=papertrace`.

## Print

Printing is a house surface, answered by one block at the end of the layer rather than by a component.
Under `@media print` the floating surfaces (tooltip, toast, menu, popover, sheet, scrim), the skeleton, the level meter and an indeterminate progress bar are removed; a dialog or a margin note keeps a 1px `--hw-line-strong` edge in place of its shadow; a stage prints as ink on paper inside that edge; marks, proof marks, diff rows, badges, pins and status dots keep their colour with `print-color-adjust: exact`; rows, table rows, callouts, notes and key-value pairs do not break across pages; and an external link prints its address after its text.
"""


def markdown(groups, comps, rules):
    out = [INTRO.format(n=len(comps), g=len(groups))]
    for key, title in groups:
        out += [f"## {title}", "",
                f"Rendered: [the live page](../components/sheets/{key}.html), "
                f"and at M, [light](../components/renders/{key}-light.webp) and "
                f"[dark](../components/renders/{key}-dark.webp).", ""]
        for c in [c for c in comps if c["group"] == key]:
            toks = ", ".join(f"`{t}`" for t in tokens_for(c["classes"], rules))
            out += [f"### {c['name']}", "",
                    f"- **For:** {c['purpose']}", f"- **Not for:** {c['notfor']}",
                    f"- **Anatomy:** {c['anatomy']}", f"- **States:** {c['states']}.",
                    f"- **Keyboard:** {c['keyboard']}", f"- **Tokens:** {toks}.",
                    f"- **Do:** {c['do']}", f"- **Do not:** {c['dont']}",
                    f"- **Classes:** {', '.join(f'`{x}`' for x in c['classes'])}.",
                    f"- **Against the house before this layer:** {c['verdict']}.",
                    f"- **Used by:** {c['used']}.", ""]
    return "\n".join(out).rstrip() + "\n"


def stamp_inputs():
    """The files a render is a picture of: the layer, its script and every generated page."""
    files = [CSS, COMP / "radiogroup.js", *sorted(SHEETS.glob("*.html"))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main(argv):
    check, stamp = "--check" in argv, "--stamp" in argv
    ns = runpy.run_path(str(COMP / "catalogue.py"))
    groups, comps = ns["GROUPS"], ns["COMPONENTS"]
    rules = css_rules(CSS.read_text(encoding="utf-8"))
    bad = validate(groups, comps, rules)
    if bad:
        for b in bad:
            print("FAIL  " + b, file=sys.stderr)
        print(f"\n{len(bad)} problems; nothing written", file=sys.stderr)
        return 1

    want = {SHEETS / f"{k}.html": page(k, t, groups, comps, rules) for k, t in groups}
    want[BOOK] = markdown(groups, comps, rules)
    stale = [p for p, text in want.items()
             if not p.exists() or p.read_text(encoding="utf-8") != text]
    extra = sorted(set(SHEETS.glob("*.html")) - set(want))
    if check:
        for p in stale:
            print(f"FAIL  {p.relative_to(ROOT)} is stale; run python3 tools/components.py",
                  file=sys.stderr)
        for p in extra:
            print(f"FAIL  {p.relative_to(ROOT)} belongs to no group", file=sys.stderr)
    else:
        SHEETS.mkdir(exist_ok=True)
        for p in stale:
            p.write_text(want[p], encoding="utf-8")
            print(f"wrote {p.relative_to(ROOT)}")
        for p in extra:
            p.unlink()
            print(f"removed {p.relative_to(ROOT)}")
        stale, extra = [], []

    missing = [f"{k}-{t}.webp" for k, _ in groups for t in THEMES
               if not (RENDERS / f"{k}-{t}.webp").exists()]
    if stamp:
        if missing:
            print(f"FAIL  cannot stamp: {', '.join(missing)} not rendered", file=sys.stderr)
            return 1
        MANIFEST.write_text(json.dumps({"inputs": stamp_inputs()}, indent=2) + "\n",
                            encoding="utf-8")
        print(f"stamped {len(groups) * len(THEMES)} renders against {len(stamp_inputs())} inputs")
    render_bad = [f"{m} is missing" for m in missing]
    if MANIFEST.exists():
        then = json.loads(MANIFEST.read_text(encoding="utf-8"))["inputs"]
        now = stamp_inputs()
        render_bad += [f"{p} changed since the renders were taken" for p in sorted(set(then) | set(now))
                       if then.get(p) != now.get(p)]
    else:
        render_bad.append("components/renders/manifest.json is missing")
    for b in render_bad:
        print(f"FAIL  render: {b}; re-render every group in both themes, then run "
              f"python3 tools/components.py --stamp", file=sys.stderr)

    print(f"{len(comps)} components in {len(groups)} groups; "
          f"{len(want)} generated files {'checked' if check else 'current'}; "
          f"{len(groups) * len(THEMES) - len(missing)} renders, "
          f"{'stale' if render_bad else 'current'}")
    return 1 if (check and (stale or extra)) or render_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
