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
  7. every class components.css defines appears in a class attribute of the markup in
     design/64-component-sheets.md, so no class is left for a reader to find in the CSS
  8. every rule that paints a solid (a ground tools/contrast.py certifies a label on: the ink,
     accent, danger and mark solids) or a control's track holds WCAG 1.4.11's 3:1 against each
     ground it sits on, 4.5:1 under prefers-contrast: more, either with its fill or with an edge
     it paints itself, measured here on every brand in every tier, float and 8-bit. A fill
     contrast.py certifies a label on is not thereby certified against the page: pointback's
     accent is 1.95:1 on white and quoth's 1.34:1. A rule with a halo (an outer ring in a role)
     sits on its halo; any exception is in FILL_EXCEPTIONS with its reason

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

# Rule 8. The solids are the grounds contrast.py certifies a label on, read from its own lists.
# A track or an indicator is a rule whose fill is the state it reports, measured whatever role it
# names: the switch's track, and the meter's lit bar, which paints a 3:1 step rather than a solid.
SOLID_FILLS = tuple(dict.fromkeys(f for fs in contrast.ROLE_LABELS.values() for f in fs))
TRACKS = (".hw-switch input", ".hw-meter > i.on")
FILL_PROPS = ("background", "background-color", "--_bg", "--_bgh", "--_field")
EDGE_PROPS = ("--_bd", "border-color", "border")
# A rule drawn inside another component sits on that component's fill, not on the page.
GROUND_OF = {".hw-toast .hw-btn": "--hw-ink"}
# (selector, fill, tier or None for every tier): why the rule is not held to 1.4.11 against the
# page there. Each is a decision recorded where it was taken, not a measurement skipped.
REGION = "a region a product is loud in, not a control; its text is a certified label"
DANGER_MORE = ("ramps/roles.css, dark under more: no colour carries the gray-12 label at 7:1 and "
               "clears 3:1 on a dark ground (2.65:1 at best), so the word carries it")
FILL_EXCEPTIONS = {
    (".hw-mark", "--hw-mark", None): "a highlighter behind words: the word is the content, ink on the swipe",
    (".hw-mark.hw-mark--solid", "--hw-mark", None): "a highlighted word, certified as --hw-on-mark on --hw-mark",
    (".hw-stage", "--hw-mark", None): REGION,
    (".hw-stage--ink", "--hw-ink", None): REGION,
    (".hw-stage--accent", "--hw-accent", None): REGION,
    (".hw-btn--danger-solid", "--hw-danger-solid", "dark-more"): DANGER_MORE,
    (".hw-btn--danger-solid", "--hw-danger-hover", "dark-more"): DANGER_MORE,
}

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


def var_calls(value):
    """(name, fallback or None) for every var() in a value, outermost first, gradients included."""
    out, i, text = [], 0, value or ""
    while (i := text.find("var(", i)) != -1:
        depth, j = 0, i + 3
        for j in range(i + 3, len(text)):
            depth += {"(": 1, ")": -1}.get(text[j], 0)
            if depth == 0:
                break
        name, _, fallback = text[i + 4:j].partition(",")
        out.append((name.strip(), fallback.strip() or None))
        i = j + 1
    return out


def roles_in(value, scope=None, seen=()):
    """Every --hw- role a value paints, fallbacks and gradient stops included. A private --_x
    alias is followed through `scope`, the declarations on the box (finding B1 of the PR 48
    verification: a chain of them was measured as nothing); its fallback is read only when the
    alias is declared nowhere in scope, as a browser would."""
    out = []
    for name, fallback in var_calls(value):
        if name.startswith("--hw-"):
            out.append(name)
        elif name.startswith("--_") and scope and name in scope and name not in seen:
            out += roles_in(scope[name], scope, (*seen, name))
        elif fallback:
            out += roles_in(fallback, scope, seen)
    return out


def shadows(value, scope=None):
    """(inset edges, halos) a box-shadow paints in a role: an inset ring is the object's own edge,
    an outer spread ring is the ground the object then sits on."""
    edges, halos = [], []
    for part in re.split(r",(?![^(]*\))", value or ""):
        names = roles_in(part, scope)
        if not names:
            continue
        if re.search(r"\binset\b", part):
            edges.extend(names)
        elif re.match(r"\s*0 0 0 ", part):
            halos.extend(names)   # a ring, not an elevation token such as --hw-shadow-overlay
    return edges, halos


def is_solid(name):
    """A solid by role, or a ramp's solid step named directly: a fill on --hw-accent-9 is the
    accent solid whatever it is called."""
    return name in SOLID_FILLS or re.fullmatch(r"--hw-[a-z][a-z0-9]*-(?:9|10)", name) is not None


# An inactive control is exempt from 1.4.11 (its own understanding note), and the house paints it
# in --hw-text-disabled, which contrast.py holds to 3:1 in both tiers rather than raising.
DISABLED = re.compile(r":disabled|\[aria-disabled|\[disabled")


def fills_in(rules):
    """(selector, fill, edges, grounds) for every rule that paints a solid or a track, with a
    variant inheriting its component's edge, and its grounds the halo it paints or GROUND_OF.
    A later rule on the same box that restates an edge or a ring (a state, a theme override)
    without restating the solid is measured as that solid under its own edge, so an edge cannot
    be dropped in a rule this check would otherwise never read."""
    base, decls, owners, later = {}, {}, [], []
    for media, sel, d in rules:
        if re.fullmatch(r"\.hw-[a-z-]+", sel):
            decls.setdefault(sel, {}).update(d)
            for p in EDGE_PROPS:
                if p in d:
                    base[sel] = d[p]

    def scope_of(sel, d):
        """The declarations a box reads its --_x aliases from: its component's base rule, then its own."""
        comp = re.match(r"(\.hw-[a-z]+)", sel)
        return {**(decls.get(comp.group(1), {}) if comp else {}), **d}

    for media, sel, d in rules:
        if media and ("forced-colors" in media or "print" in media):
            continue
        track = sel in TRACKS
        scope = scope_of(sel, d)
        fills = [r for p in FILL_PROPS for r in roles_in(d.get(p), scope)
                 if is_solid(r) or (track and p in ("background", "background-color"))]
        if not fills:
            if any(p in d for p in (*EDGE_PROPS, "box-shadow")):
                later.append((sel, d))
            continue
        edge_values = [d[p] for p in EDGE_PROPS if p in d]
        if not edge_values:
            owner = re.match(r"(\.hw-[a-z]+)--[a-z-]+$", sel)
            if owner and owner.group(1) in base:
                edge_values = [base[owner.group(1)]]
        edges = [r for v in edge_values for r in roles_in(v, scope)]
        owners.append((sel, scope, list(dict.fromkeys(fills)), edges, *shadows(d.get("box-shadow"), scope)))
    for sel, d in later:
        if DISABLED.search(sel):
            continue
        for osel, oscope, fills, edges, inset, halos in list(owners):
            # the same box: the owner's selector last, then only states (:hover, [aria-*]), never a
            # descendant, and never a pseudo-element the owner is not (a thumb sits on its track)
            on_box = re.search(re.escape(osel) + r"(?:[:\[][^\s>+~]*)?$", sel) and ("::" in osel or "::" not in sel)
            if sel == osel or not on_box:
                continue
            scope = {**oscope, **d}
            own = [r for p in FILL_PROPS for r in roles_in(d.get(p), scope)]
            stated = [d[p] for p in EDGE_PROPS if p in d]
            new_edges = [r for v in stated for r in roles_in(v, scope)] if stated else edges
            ring = shadows(d["box-shadow"], scope) if "box-shadow" in d else (inset, halos)
            owners.append((sel, scope, own or fills, new_edges, *ring))
    out = []
    for sel, _, fills, edges, inset, halos in owners:
        edges = edges + inset
        grounds = [GROUND_OF[sel]] if sel in GROUND_OF else halos or list(contrast.ROLE_GROUNDS)
        for fill in fills:
            out.append((sel, fill, edges, grounds))
    return out


def check_fills(rules, envs):
    """Rule 8: a solid or a track holds 3:1 on every ground it sits on, raised under more, with
    its fill or an edge it paints, on every brand in every tier, float and 8-bit."""
    bad, rows, lowest = [], [], {}
    for sel, fill, edges, grounds in fills_in(rules):
        if (sel, fill, None) in FILL_EXCEPTIONS:
            continue
        for brand, env in envs.items():
            for tier, e in env.items():
                if (sel, fill, tier) in FILL_EXCEPTIONS:
                    continue
                bar = contrast.raised(contrast.NON_TEXT) if tier.endswith("-more") else contrast.NON_TEXT
                for g in grounds:
                    ground = contrast.resolve(g, e)
                    # a width such as --hw-border-w is a role name in the value and no colour
                    got = {x: min(contrast.ratio(contrast.resolve(x, e), ground))
                           for x in [fill, *edges] if x in e}
                    best = max(got, key=got.get)
                    key = (sel, fill)
                    if key not in lowest or got[best] < lowest[key][0]:
                        lowest[key] = (got[best], f"{brand} {tier} on {g}, by {best}")
                    if got[best] < bar:
                        edge = ", ".join(f"edge {x} {got[x]:.2f}:1" for x in edges if x in got) or "no edge"
                        bad.append(f"{brand} {tier}: {sel} paints {fill} on {g} at {got[fill]:.2f}:1, "
                                   f"under {bar} ({edge})")
    for (sel, fill), (r, where) in lowest.items():
        rows.append(f"{sel} {fill}: lowest {r:.2f}:1 ({where})")
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


def check_documented(text, book):
    """The audit's count, kept: a class defined in the layer and absent from every class
    attribute in the book's markup is one a reader can learn only from the CSS."""
    defined = set().union(*(re.findall(r"\.([A-Za-z_][\w-]*)", sel) for _, sel, _ in rules_of(text)))
    shown = {n for v in re.findall(r'class="([^"]*)"', book) for n in v.split()}
    return [f".{n} is defined in components.css and appears in no markup in the sheets"
            for n in sorted(defined - shown)]


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
            dark = theme == "dark"
            roles = {**lb["base"], **(lb.get("dark", {}) if dark else {})}
            out[brand][theme] = {**rb[theme], **roles}
            out[brand][theme + "-more"] = {**rb[theme], **roles, **lb.get("more", {}),
                                           **(lb.get("dark-more", {}) if dark else {})}
    return out


def generator_check(tree):
    return subprocess.run([sys.executable, str(tree / "tools" / "components.py"), "--check"],
                          capture_output=True, text=True)


def main():
    fails = []
    text = CSS.read_text(encoding="utf-8")
    rules = rules_of(text)
    exports = {str(p.relative_to(ROOT)): declared(p) for p in sorted(ROOT.glob("**/exports/variables.css"))}
    comps = runpy.run_path(str(ROOT / "components" / "catalogue.py"))["COMPONENTS"]
    demos = "\n".join([c["demo"] for c in comps] + [s for c in comps for _, s in c["markup"]])
    book = (ROOT / "design" / "64-component-sheets.md").read_text(encoding="utf-8")
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
    got, rows = check_fills(rules, envs)
    fails += got
    print(f"  fills:        {len(fills_in(rules))} solids and tracks against the grounds they sit on, "
          f"{len(got)} under 1.4.11, {len(FILL_EXCEPTIONS)} excepted")
    for row in rows:
        print(f"                {row}")
    got = check_type_floor(text)
    fails += got
    print(f"  type floor:   {len(got)} sub-1em sizes without the 11px floor")
    fails += check_files()
    got = check_documented(text, book)
    fails += got
    print(f"  documented:   {len(got)} classes components.css defines that no markup in the sheets shows")

    # Negative controls: each replays a mistake and must be caught.
    btn = ".hw-btn--primary { --_bg: var(--hw-ink); --_fg: var(--hw-on-ink);"
    pin_edge = "box-shadow: inset 0 0 0 var(--hw-border-w) var(--hw-accent-edge), 0 0 0 2px var(--hw-surface)"
    cases = [
        ("an undeclared token", lambda: check_tokens(text.replace("var(--hw-line-strong)", "var(--hw-line-strongest)", 1), exports, demos)),
        ("the layer redefining a house token", lambda: check_tokens(text + "\n.hw-x { --hw-text: red; }", exports, demos)),
        ("a literal hex colour", lambda: check_literals(text.replace("var(--hw-ink)", "#111111", 1))),
        ("an undeclared literal length", lambda: check_literals(text.replace("var(--hw-space-12)", "13px", 1))),
        ("muted text on the ink solid", lambda: check_pairs(rules_of(text.replace(btn, ".hw-btn--primary { --_bg: var(--hw-ink); --_fg: var(--hw-text-muted);")), envs)[0]),
        ("a label on the wrong solid", lambda: check_pairs(rules_of(text.replace(btn, ".hw-btn--primary { --_bg: var(--hw-accent); --_fg: var(--hw-on-ink);")), envs)[0]),
        ("the pin without its inner edge, as before audit row H1", lambda: check_fills(rules_of(text.replace(
            pin_edge, "box-shadow: 0 0 0 2px var(--hw-surface)")), envs)[0]),
        ("the accent button edged in its own solid, as before audit row H2", lambda: check_fills(rules_of(text.replace(
            "--_bd: var(--hw-accent-edge); --_bgh: var(--hw-accent-hover);",
            "--_bd: var(--hw-accent); --_bgh: var(--hw-accent-hover);")), envs)[0]),
        ("the lit meter bar in the accent solid, as before audit row H2", lambda: check_fills(rules_of(text.replace(
            "var(--_live, var(--hw-accent-edge))", "var(--_live, var(--hw-accent))")), envs)[0]),
        ("a new solid named by its raw ramp step", lambda: check_fills(rules_of(
            text + "\n.hw-btn--brand { --_bg: var(--hw-accent-9); --_bd: var(--hw-accent-9); }"), envs)[0]),
        ("a state rule that drops the pin's edge", lambda: check_fills(rules_of(
            text + "\n.hw-pin:hover { box-shadow: 0 0 0 2px var(--hw-surface); }"), envs)[0]),
        ("a theme override that drops the accent button's edge", lambda: check_fills(rules_of(
            text + '\n:where([data-theme="light"]) .hw-btn--accent { --_bd: transparent; }'), envs)[0]),
        ("a pin haloed in its own solid", lambda: check_fills(rules_of(text.replace(
            pin_edge, pin_edge.replace("2px var(--hw-surface)", "2px var(--hw-accent)"))), envs)[0]),
        ("a solid reached through a private alias chain (verification of PR 48, B1)", lambda: check_fills(rules_of(
            text + "\n.hw-btn--brand { --_solid: var(--hw-accent); --_brand: var(--_solid); --_bg: var(--_brand); --_bd: var(--_brand); }"),
            envs)[0]),
        ("a 0.8em keycap with no floor", lambda: check_type_floor(text.replace("max(0.8em, 11px)", "0.8em", 1))),
        ("a class the sheets never show", lambda: check_documented(text + "\n.hw-btn--ghost { color: var(--hw-text); }", book)),
    ]
    if btn not in text:
        fails.append("negative controls: the primary button rule they edit has moved")
    for rule in (pin_edge, "--_bd: var(--hw-accent-edge); --_bgh: var(--hw-accent-hover);",
                 "var(--_live, var(--hw-accent-edge))"):
        if rule not in text:
            fails.append(f"negative controls: the rule they edit has moved: {rule}")
    # The audit's numbers, held: the pin without its edge is refused on its halo at exactly these.
    bare = check_fills(rules_of(text.replace(pin_edge, "box-shadow: 0 0 0 2px var(--hw-surface)")), envs)[0]
    for brand, at in (("pointback", "1.95"), ("quoth", "1.34")):
        want = f"{brand} light: .hw-pin paints --hw-accent on --hw-surface at {at}:1"
        if not any(f.startswith(want) for f in bare):
            fails.append(f"negative control: the bare pin is not refused as {want!r}")
    clean = {"tokens": set(check_tokens(text, exports, demos)), "literals": set(check_literals(text)),
             "pairs": set(check_pairs(rules, envs)[0]), "fills": set(check_fills(rules, envs)[0]),
             "type": set(check_type_floor(text)),
             "documented": set(check_documented(text, book))}
    before = set().union(*clean.values())
    for label, run in cases:
        caught = [f for f in run() if f not in before]
        if not caught:
            fails.append(f"negative control not caught: {label}")
        print(f"  control:      {label}: {'caught' if caught else 'MISSED'}, first: {caught[0] if caught else '-'}")

    # The generator's own refusals, on a copy of the tree. fonts/ is a render input, so a copy
    # without it fails on the stamp and every control would be caught for the wrong reason: the
    # copy must pass unedited, and each control must fail with its own message.
    quiet = '("Quiet", """<button type="button" class="hw-btn hw-btn--quiet">Cancel</button>"""),'
    plain = '("Badge without its dot", """<span class="hw-badge hw-badge--plain">Draft</span>"""),'
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        for part in ("components", "tools", "design", "exports", "fonts"):
            shutil.copytree(ROOT / part, tree / part)
        r = generator_check(tree)
        if r.returncode:
            fails.append("the unedited copy fails tools/components.py --check, so the controls on it "
                         "prove nothing:\n" + r.stderr.strip())
        cat = tree / "components" / "catalogue.py"
        original = cat.read_text(encoding="utf-8")
        if quiet not in original or plain not in original:
            fails.append("negative controls: the markup they edit has moved")
        for label, edit, want in (
            ("a stale sheet", lambda s: s.replace("Starts an action whose verb is its label.", "Starts an action."), "is stale"),
            ("a demo using a class the layer does not define", lambda s: s.replace('class="hw-btn hw-btn--quiet"', 'class="hw-btn hw-btn--ghost"', 1), "its demo uses .hw-btn--ghost"),
            ("markup using a class the layer does not define", lambda s: s.replace(quiet, quiet.replace("--quiet", "--ghost"), 1), "its markup 'Quiet' uses .hw-btn--ghost"),
            ("an icon that is not vendored", lambda s: s.replace("{{icon:copy}}", "{{icon:clipboard}}", 1), "icon 'clipboard' is not vendored"),
            ("an em dash in a sheet", lambda s: s.replace("Starts an action whose verb", "Starts an action \u2014 whose verb", 1), "carries an em dash"),
            ("a variant no markup shows", lambda s: s.replace(plain, "", 1), ".hw-badge--plain is defined in components.css and no entry's markup shows it"),
        ):
            cat.write_text(edit(original), encoding="utf-8")
            r = generator_check(tree)
            caught = r.returncode != 0 and want in r.stderr
            first = (r.stderr.strip().splitlines() or ["-"])[0]
            if not caught:
                fails.append(f"negative control not caught: {label}")
            print(f"  control:      {label}: {'caught' if caught else 'MISSED'}, first: {first}")
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
