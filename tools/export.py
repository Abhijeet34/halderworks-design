#!/usr/bin/env python3
"""Emit this system in the five interchange formats, from the files a product would load.

The requirement is that the book be usable irrespective of which model reads it.
A design system that exists only as prose is a system every agent re-interprets; these five
are the forms agents actually consume:

  exports/DESIGN.md            the extended brief: every role and scale with its job, plus the rules
  exports/DESIGN.compact.md    the short brief, for a context window that cannot take the long one
  exports/theme.css            the runtime variables plus a Tailwind v4 `@theme inline` map
  exports/variables.css        plain CSS custom properties, with every theme and media block
  exports/design-tokens.json   W3C DTCG format, $value / $type / $description per token

Three sources, composed and never re-solved:

  ramps/tokens/<brand>.tokens.css   the twelve-step ramps, generated and floored by tools/ramps.py
  ramps/roles.css                   the roles and scales every brand shares, with every media block
  <dir>/tokens/tokens.json          the brand's faces, shape and layout, which ramps/ does not carry

This is NOT tools/build.py or tools/ramps.py: it only re-expresses values that are already
solved, so it can never invent one. It proves that by parsing back what it wrote and refusing
if any block, condition or value differs from the three sources.

    python3 tools/export.py [design-system-dir]
    python3 tools/export.py examples/quoth      # quoth's set, into examples/quoth/exports/
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Families tokens.json still owns and the export carries unchanged. Everything in SUPERSEDED
# (and the per-style type tokens) now comes from ramps/roles.css, so tokens.css declaring a
# property in neither list is a token this export would silently drop.
CARRIED = ("radius", "shadow", "layout", "icon", "zIndex", "stroke")
SUPERSEDED = ("color", "spacing", "duration", "easing", "density")
TYPE_PARTS = ("text", "leading", "tracking", "weight")

# Every "color" name ramps/roles.css replaces, each under a name of its own (surface -> bg,
# border -> line, quiet -> fill, ring -> focus...): no literal match is expected for one of
# these, so membership here stands in for one. UNROLED is the opposite case: six categorical
# steps ramps/roles.css gives no role to at all, a stated gap (design/75-spec-sheet.md,
# follow-up house-chart-roles-r8). A colour tokens.json declares in neither set is new and
# unaccounted for, so check_sources refuses it by name instead of folding it in by family.
RENAMED_COLOR = frozenset({
    "hw-accent", "hw-accent-hover", "hw-accent-quiet", "hw-accent-ring",
    "hw-border", "hw-border-strong", "hw-danger", "hw-danger-quiet", "hw-ground",
    "hw-ink", "hw-ink-active", "hw-ink-hover", "hw-ink-text", "hw-scrim",
    "hw-success", "hw-success-quiet", "hw-surface", "hw-surface-active",
    "hw-surface-hover", "hw-surface-raised", "hw-surface-sunken", "hw-text",
    "hw-text-disabled", "hw-text-muted", "hw-text-secondary", "hw-warning",
    "hw-warning-quiet",
})
UNROLED = frozenset({
    "hw-chart-1", "hw-chart-2", "hw-chart-3", "hw-chart-4", "hw-chart-5", "hw-chart-6",
})

TEXT_SIZES = ("s", "m", "l", "xl", "xxl")
# Every condition a product needs answered. Without one, a product that loads the export loses
# dark mode, the high-contrast set, a density, the touch floor, reduced motion or a text size.
REQUIRED = [
    (None, '[data-theme="dark"]'),
    ("(prefers-color-scheme: dark)", ':root:not([data-theme="light"])'),
    ("(prefers-contrast: more)", ":root"),
    (None, '[data-density="compact"]'),
    ("(pointer: coarse)", ":root"),
    ("(pointer: coarse)", '[data-density="compact"]'),
    ("(prefers-reduced-motion: reduce)", ":root"),
] + [(None, f'html[data-text-size="{s}"]') for s in TEXT_SIZES]
BROWSER_DEFAULT_PX = 16
MODES = ("light", "dark", "light-more", "dark-more")

# Design Tokens Format Module 2025.10 types a value by its SHAPE, not by the family it sits
# in: a dimension is {value, unit} with unit px or rem, a duration is {value, unit} in ms or s,
# a cubicBezier is four numbers, a colour is a colour space plus components. A CSS string under
# any of those types is an invalid token, so the type is read off the value.
NUM = r"-?\d+(?:\.\d+)?"
DIMENSION = re.compile(rf"^({NUM})(px|rem)$")
DURATION = re.compile(rf"^({NUM})(ms|s)$")
BEZIER = re.compile(
    rf"^cubic-bezier\(\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*\)$")
OKLCH = re.compile(rf"^oklch\(\s*({NUM})\s+({NUM})\s+({NUM})\s*(?:/\s*({NUM})\s*)?\)$")
RGBA = re.compile(
    rf"^rgba?\(\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*(?:,\s*({NUM})\s*)?\)$")
HEX = re.compile(r"^#([0-9a-fA-F]{6})$")
CHARS = re.compile(rf"^({NUM})ch$")
BARE = re.compile(rf"^{NUM}$")
LENGTH_FN = re.compile(rf"^(?:max|min|clamp)\(.*?(?<![\d.])({NUM})rem\b")
PERCENT = re.compile(rf"^({NUM})%$")
VAR = re.compile(r"var\((--[a-z0-9-]+)\)")
RELATIVE = re.compile(rf"^oklch\(from (oklch\([^)]*\)) calc\(l - ({NUM})\) c h\)$")
COMMENT = re.compile(r"/\*.*?\*/", re.S)
DESCRIBED = re.compile(r"^\s*(--hw-[a-z0-9-]+):[^;]+;\s*/\*\s*(.*?)\s*\*/", re.M)


def num(text):
    """A JSON number, integral where the CSS was integral, so 0 does not ship as 0.0."""
    f = float(text)
    return int(f) if f == int(f) else f


# --- reading CSS --------------------------------------------------------------------------

def blocks(text):
    """[(media, selector, {property: value})] in source order, one @media level deep.

    Source order is kept because it is half the cascade: the touch block only wins over the
    compact block because it comes after it at the same specificity. Any at-rule other than
    @media holding declarations, such as `@theme inline`, is read as a block of its own.
    """
    out, media, sel, pos = [], None, None, 0
    text = COMMENT.sub("", text)
    for m in re.finditer(r"[{}]", text):
        chunk, pos = text[pos:m.start()].strip(), m.end()
        if m.group() == "{":
            chunk = " ".join(chunk.rsplit(";", 1)[-1].split())   # drop a leading @import;
            if chunk.startswith("@media"):
                media = chunk[len("@media"):].strip()
            else:
                sel = chunk
        elif sel is not None:
            decls = {}
            for d in chunk.split(";"):
                if ":" in d:
                    k, v = d.split(":", 1)
                    decls[k.strip()] = " ".join(v.split())
            out.append((media, sel, decls))
            sel = None
        else:
            media = None
    return out


def body(text):
    """A source file without its leading header comment, which describes that file, not this."""
    return re.sub(r"^\s*/\*.*?\*/\s*", "", text, count=1, flags=re.S).rstrip() + "\n"


def scope(bs, theme, more=False):
    """{property: value} on the root element, cascaded by source order.

    Theme is chosen by attribute, so the prefers-color-scheme copy is not applied; every
    selector that can match the root here has the same specificity, so order decides.
    """
    match = {":root", "html", f'[data-theme="{theme}"]'}
    env = {}
    for media, sel, decls in bs:
        if media not in (None, "(prefers-contrast: more)" if more else None):
            continue
        if any(part.strip() in match for part in sel.split(",")):
            env.update(decls)
    return env


def resolve(value, env):
    """A value with every var() replaced, so a role ships as the colour a display receives."""
    for _ in range(8):
        new = VAR.sub(lambda m: env[m.group(1)], value)
        if new == value:
            break
        value = new
    m = RELATIVE.match(value)
    if m:   # relative colour syntax: DTCG has no form for it, so it ships computed
        l, c, h, _ = OKLCH.match(m.group(1)).groups()
        value = f"oklch({float(l) - float(m.group(2)):.3f} {c} {h})"
    return value


def at_root(value, root_px):
    """A rem, px or max() length in px at a root size; None for anything viewport-relative."""
    m = re.fullmatch(r"max\((.*)\)", value)
    if m:
        parts = [at_root(p, root_px) for p in split_outside_parens(m.group(1), ",")]
        return None if None in parts else max(parts)
    m = DIMENSION.match(value)
    if m:
        return float(m.group(1)) * (root_px if m.group(2) == "rem" else 1)
    return None


# --- the three sources --------------------------------------------------------------------

def sources(root):
    brand = "house" if root.resolve() == ROOT else root.resolve().name
    ramp = ROOT / "ramps" / "tokens" / f"{brand}.tokens.css"
    if not ramp.exists():
        raise ValueError(f"no ramps for brand {brand!r}: {ramp.relative_to(ROOT)} does not exist; "
                         f"add ramps/brands/{brand}.json and run tools/ramps.py")
    tokens = json.loads((root / "tokens" / "tokens.json").read_text(encoding="utf-8"))
    roles = (ROOT / "ramps" / "roles.css").read_text(encoding="utf-8")
    return {"brand": brand, "tokens": tokens, "ramp": body(ramp.read_text(encoding="utf-8")),
            "carried": carried_css(tokens), "roles": body(roles),
            "describe": dict(DESCRIBED.findall(roles))}


def carried(tokens):
    for fam in CARRIED:
        yield from ((fam, e) for e in tokens[fam]["tokens"])


def carried_css(tokens):
    out = [":root {"]
    out += [f"  --hw-font-{k}: {v};" for k, v in tokens["type"]["families"].items()]
    out += [f"  --{e['name']}: {e['value']};" for _, e in carried(tokens)
            if isinstance(e["value"], str)]
    out.append("}")
    themed = [e for _, e in carried(tokens) if isinstance(e["value"], dict)]
    for sel, theme, indent in ((':root, [data-theme="light"]', "light", ""),
                               ('[data-theme="dark"]', "dark", ""),
                               (':root:not([data-theme="light"])', "dark", "  ")):
        if indent:
            out.append("@media (prefers-color-scheme: dark) {")
        out.append(f"{indent}{sel} {{")
        out += [f"{indent}  --{e['name']}: {e['value'][theme]};" for e in themed]
        out.append(f"{indent}}}")
        if indent:
            out.append("}")
    return "\n".join(out) + "\n"


def runtime_css(src):
    return "\n".join([
        f"/* ---- the ramps every role names, from ramps/tokens/{src['brand']}.tokens.css ---- */",
        src["ramp"],
        "/* ---- faces, shape and layout, from tokens/tokens.json ---- */",
        src["carried"],
        "/* ---- roles and scales, with every media block, from ramps/roles.css ---- */",
        src["roles"]])


def expected_blocks(src):
    return blocks(src["ramp"]) + blocks(src["carried"]) + blocks(src["roles"])


def roles(src):
    """[(name, raw value)] declared by ramps/roles.css on :root, in its order."""
    first = next(d for m, s, d in blocks(src["roles"]) if m is None and s == ":root")
    return list(first.items())


def modes(src):
    bs = expected_blocks(src)
    return {"light": scope(bs, "light"), "dark": scope(bs, "dark"),
            "light-more": scope(bs, "light", True), "dark-more": scope(bs, "dark", True)}


def is_colour(value):
    return bool(OKLCH.match(value) or RGBA.match(value) or HEX.match(value))


def text_sizes(src):
    """[(setting, css, root px at the browser default)] from the html blocks."""
    out = []
    for media, sel, decls in blocks(src["roles"]):
        m = re.fullmatch(r'html\[data-text-size="([a-z]+)"\]', sel)
        if media is None and m:
            pct = float(PERCENT.match(decls["font-size"]).group(1))
            out.append((m.group(1), decls["font-size"], BROWSER_DEFAULT_PX * pct / 100))
    return out


def conditions(src):
    """{property: {condition: value}} for every non-colour role a block other than :root moves."""
    out = {}
    for media, sel, decls in blocks(src["roles"]):
        if (media, sel) == (None, ":root") or sel.startswith("html"):
            continue
        for k, v in decls.items():
            if k.startswith("--"):
                out.setdefault(k, {})[f"{media + ' ' if media else ''}{sel}"] = v
    return out


# --- the checks, which are why this file is allowed to write anything ----------------------

CSS_VAR = re.compile(r"^\s*(--hw-[a-z0-9-]+):\s*([^;]+);")
BASE_SELECTORS = {':root, [data-theme="light"]': "light",
                  '[data-theme="dark"]': "dark", ":root": "root"}


def base_blocks(path):
    """The three UNCONDITIONAL blocks of tokens.css, keyed by theme."""
    out, cur, depth = {"light": {}, "dark": {}, "root": {}}, None, 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.endswith("{"):
            # Only a top-level selector declares. The light selector also opens a block inside
            # @media (prefers-contrast: more), and reading that one would overwrite the default.
            cur = BASE_SELECTORS.get(s[:-1].strip()) if depth == 0 else None
            depth += 1
            continue
        if s.startswith("}"):
            depth -= 1
            cur = None
            continue
        m = CSS_VAR.match(line)
        if m and cur:
            out[cur][m.group(1)] = m.group(2).strip()
    return out


def check_sources(src, root):
    """What must hold before anything is written."""
    bad = []
    tokens = src["tokens"]
    # 1. tokens.css is still the file a product on the old set loads: every property it declares
    # is either carried here with the same value, or one roles.css now owns.
    css = base_blocks(root / "tokens" / "tokens.css")
    mine = {}
    for media, sel, decls in blocks(src["carried"]):
        if media is None:
            theme = BASE_SELECTORS[sel]
            mine.setdefault(theme, {}).update(decls)
    owned = {"--" + e["name"] for fam in SUPERSEDED for e in tokens[fam]["tokens"]
             if fam != "color"}
    colors = {e["name"] for e in tokens["color"]["tokens"]}
    owned |= {"--" + n for n in colors & (RENAMED_COLOR | UNROLED)}
    bad += [f"--{n} is a colour token ramps/roles.css neither renames nor declares UNROLED"
            for n in sorted(colors - RENAMED_COLOR - UNROLED)]
    owned |= {f"--hw-{part}-{s['name']}" for g in tokens["type"]["groups"]
              for s in g["styles"] for part in TYPE_PARTS}
    for theme, props in css.items():
        for k, v in props.items():
            if k in owned:
                continue
            got = mine.get(theme, {}).get(k)
            if got is None:
                bad.append(f"{k} [{theme}] is in tokens.css and neither carried by the export nor "
                           f"owned by ramps/roles.css")
            elif got != v:
                bad.append(f"{k} [{theme}]: tokens.css {v!r} != export {got!r}")
    # 2. The three sources are disjoint: a name declared on :root by two of them would let load
    # order, not the system, decide its value.
    seen = {}
    for part in ("ramp", "carried", "roles"):
        names = {k for m, s, d in blocks(src[part]) for k in d if k.startswith("--")}
        for k in names:
            if k in seen:
                bad.append(f"{k} is declared by both {seen[k]} and {part}")
            seen.setdefault(k, part)
    # 3. Every role resolves to a value in every mode, so no var() names a step the brand lacks.
    for mode, env in modes(src).items():
        for k, _ in roles(src):
            try:
                resolve(env[k], env)
            except KeyError as exc:
                bad.append(f"{k} [{mode}] names {exc.args[0]}, which no source declares")
    return bad


def check_written(src, written):
    """Parse back what was written: every block, in order, and every required condition."""
    want, bad = expected_blocks(src), []
    for name in ("variables.css", "theme.css"):
        got = [b for b in blocks(written[name]) if not b[1].startswith("@theme")]
        if got != want:
            bad.append(f"exports/{name}: its {len(got)} blocks are not the {len(want)} of "
                       f"ramps, tokens.json and ramps/roles.css, in that order")
        present = {(m, s) for m, s, _ in got}
        bad += [f"exports/{name} has no {s} block{' under ' + m if m else ''}"
                for m, s in REQUIRED if (m, s) not in present]
    defined = {k for _, _, d in want for k in d}
    for _, sel, decls in blocks(written["theme.css"]):
        if sel.startswith("@theme"):
            bad += [f"exports/theme.css maps {k} onto {v}, which nothing declares"
                    for k, v in decls.items() if VAR.fullmatch(v).group(1) not in defined]
    return bad


# --- emitters -----------------------------------------------------------------------------

def emit_variables_css(src):
    return (f"/* {src['tokens']['name']}, brand {src['brand']} - plain CSS custom properties.\n"
            "   Generated by tools/export.py from ramps/ and tokens/tokens.json. Do not hand-edit.\n"
            "   Light by default; [data-theme] and prefers-color-scheme for dark, "
            "prefers-contrast: more,\n"
            "   [data-density=\"compact\"], (pointer: coarse), prefers-reduced-motion and "
            "html[data-text-size]\n   are all answered below. */\n\n" + runtime_css(src))


def tw_name(name, value):
    """The Tailwind v4 theme variable for one of ours, or None where no utility namespace fits."""
    short = name[len("--hw-"):]
    if is_colour(value):
        return f"--color-{short}"
    if name == "--hw-leading":
        return "--leading-normal"
    if short.startswith(("text-", "leading-", "radius-", "shadow-", "font-", "ease-")):
        return f"--{short}"
    # A bare --spacing-4 would rebind Tailwind's own p-4, so space keeps its prefix: p-space-4.
    if short.startswith(("space-", "icon", "control-h", "row-h", "cell-pad", "field-pad")):
        return f"--spacing-{short}"
    return None


def emit_theme_css(src):
    env = modes(src)["light"]
    names = [k for k, _ in roles(src)] + [k for _, _, d in blocks(src["carried"]) for k in d]
    out = [f"/* {src['tokens']['name']}, brand {src['brand']} - Tailwind v4.",
           "   Generated by tools/export.py from ramps/ and tokens/tokens.json. Do not hand-edit.",
           "   @theme cannot sit inside a media query, so the runtime variables come first with",
           "   every block, and `@theme inline` points each utility at one of them: bg-surface",
           "   then follows dark, contrast more, text size, density and touch like var() does. */",
           "", '@import "tailwindcss";', "", runtime_css(src), "@theme inline {"]
    done = set()
    for k in names:
        tw = tw_name(k, resolve(env[k], env))
        if tw and k not in done:
            out.append(f"  {tw}: var({k});")
            done.add(k)
    out.append("}")
    return "\n".join(out) + "\n"


def as_color(value):
    m = OKLCH.match(value)
    if m:
        out = {"colorSpace": "oklch", "components": [num(g) for g in m.groups()[:3]]}
        if m.group(4) is not None:
            out["alpha"] = num(m.group(4))
        return out
    m = HEX.match(value)
    if m:
        value = "rgb(" + ", ".join(str(int(m.group(1)[i:i + 2], 16)) for i in (0, 2, 4)) + ")"
    m = RGBA.match(value)
    if not m:
        raise ValueError(f"not a colour this emitter can express: {value!r}")
    r, g, b = (int(round(float(c))) for c in m.groups()[:3])
    out = {"colorSpace": "srgb", "components": [round(c / 255, 6) for c in (r, g, b)],
           "hex": f"#{r:02x}{g:02x}{b:02x}"}
    if m.group(4) is not None:
        out["alpha"] = num(m.group(4))
    return out


def split_outside_parens(value, sep):
    parts, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch == sep and depth == 0:
            parts.append(cur.strip()); cur = ""
        else:
            cur += ch
    parts.append(cur.strip())
    return [p for p in parts if p]


def as_shadow(value):
    """[{color, offsetX, offsetY, blur, spread}] - a CSS shadow list, layer by layer.

    Both separators inside a shadow list are ambiguous to a plain split: the layers are comma
    separated and so are the rgba() components, and the lengths are space separated inside a
    layer whose colour also contains spaces in other notations. Depth-aware splitting is the
    only reading that survives both.
    """
    layers = []
    for layer in split_outside_parens(value, ","):
        parts = split_outside_parens(layer, " ")
        lengths, colour = parts[:-1], parts[-1]
        if len(lengths) == 3:
            lengths.append("0")
        if len(lengths) != 4:
            raise ValueError(f"not a shadow layer this emitter can express: {layer!r}")
        keys = ("offsetX", "offsetY", "blur", "spread")
        out = {"color": as_color(colour)}
        out.update(zip(keys, (as_dimension(x) for x in lengths)))
        layers.append(out)
    return layers if len(layers) > 1 else layers[0]


def as_dimension(value):
    m = DIMENSION.match(value)
    if m:
        return {"value": num(m.group(1)), "unit": m.group(2)}
    if BARE.match(value):           # a bare 0 in a shadow offset is a length of zero pixels
        return {"value": num(value), "unit": "px"}
    raise ValueError(f"not a DTCG dimension: {value!r}")


def dtcg_node(fam, value):
    """The `$type` and `$value` of one CSS value, as the 2025.10 module defines them."""
    if fam == "shadow":
        return {"$type": "shadow", "$value": as_shadow(value)}
    m = BEZIER.match(value)
    if m:
        return {"$type": "cubicBezier", "$value": [num(g) for g in m.groups()]}
    m = DURATION.match(value)
    if m:
        return {"$type": "duration", "$value": {"value": num(m.group(1)), "unit": m.group(2)}}
    if is_colour(value):
        return {"$type": "color", "$value": as_color(value)}
    if DIMENSION.match(value):
        return {"$type": "dimension", "$value": as_dimension(value)}
    m = LENGTH_FN.match(value)
    if m:
        # The module has no expression type, so max() and clamp() ship their rem term as the
        # value and the CSS a product must use beside it, as a measure in ch does below.
        return {"$type": "dimension", "$value": {"value": num(m.group(1)), "unit": "rem"},
                "$extensions": {"halderworks": {"css": value}}}
    m = CHARS.match(value)
    if m:
        # ch is not a DTCG dimension unit - the module allows px and rem and nothing else - and
        # a measure in ch is a count of characters rather than a length, so it ships as the
        # number it is, with the CSS it came from beside it.
        return {"$type": "number", "$value": num(m.group(1)),
                "$extensions": {"halderworks": {"css": value}}}
    if BARE.match(value):
        return {"$type": "number", "$value": num(value)}
    raise ValueError(f"no DTCG type for {fam} value {value!r}")


def role_family(name, value):
    if is_colour(value):
        return "color"
    for prefix, fam in (("--hw-text-", "type"), ("--hw-leading", "type"),
                        ("--hw-space-", "spacing"), ("--hw-duration-", "duration"),
                        ("--hw-ease-", "easing")):
        if name.startswith(prefix):
            return fam
    return "density"


def emit_dtcg(src):
    every, cond = modes(src), conditions(src)
    env = every["light"]
    doc = {"$description": (
        f"{src['tokens']['name']}, brand {src['brand']}. Generated by tools/export.py to the "
        "Design Tokens Format Module 2025.10. A colour carries its value in every mode under "
        "$extensions.halderworks.modes, and $value is light; a size or duration that a density, "
        "the touch floor or reduced motion moves carries those values under "
        "$extensions.halderworks.conditions.")}
    for name, raw in roles(src):
        value = resolve(env[name], env)
        fam = role_family(name, value)
        node = dtcg_node(fam, value)
        node["$description"] = src["describe"].get(name, "")
        ext = node.setdefault("$extensions", {}).setdefault("halderworks", {})
        if fam == "color":
            ext["modes"] = {m: as_color(resolve(e[name], e)) for m, e in every.items()}
        elif name in cond:
            ext["conditions"] = cond[name]
        if not ext:
            del node["$extensions"]
        doc.setdefault(fam, {"$description": f"{fam} tokens"})[name[len("--hw-"):]] = node
    sizes = {"$description": "the text-size setting: the root size at the browser's default "
                             f"{BROWSER_DEFAULT_PX}px, set by html[data-text-size]"}
    for setting, css, px in text_sizes(src):
        sizes[setting] = {"$type": "dimension", "$value": {"value": num(round(px, 4)), "unit": "px"},
                          "$extensions": {"halderworks": {"css": css}}}
    doc["textSize"] = sizes
    for fam in CARRIED:
        group = {"$description": f"{fam} tokens"}
        for e in src["tokens"][fam]["tokens"]:
            v = e["value"]
            node = dtcg_node(fam, v if isinstance(v, str) else v["light"])
            node["$description"] = e.get("usage", "")
            if isinstance(v, dict):
                node.setdefault("$extensions", {}).setdefault("halderworks", {})["modes"] = {
                    t: dtcg_node(fam, x)["$value"] for t, x in v.items()}
            group[e["name"][len("hw-"):]] = node
        doc[fam] = group
    doc["font"] = {"$description": "font families", **{
        k: {"$type": "fontFamily", "$value": font_stack(src["tokens"], k)}
        for k in src["tokens"]["type"]["families"]}}
    bad = dtcg_violations(doc)
    if bad:
        raise ValueError("; ".join(bad))
    return json.dumps(doc, indent=2) + "\n"


def font_stack(tokens, family):
    """A DTCG fontFamily is an ordered list of names, not one CSS string."""
    return [n.strip().strip('"') for n in tokens["type"]["families"][family].split(",")]


# Every $type below is a type the module defines, and every check is its $value syntax. The
# emitter is the only thing that decides a type, so nothing else in this repository would
# notice it deciding wrongly: this is what makes "W3C DTCG" a checked claim rather than a label.
DTCG_SHAPE = {
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "dimension": lambda v: (isinstance(v, dict) and set(v) == {"value", "unit"}
                            and isinstance(v["value"], (int, float))
                            and v["unit"] in ("px", "rem")),
    "duration": lambda v: (isinstance(v, dict) and set(v) == {"value", "unit"}
                           and isinstance(v["value"], (int, float))
                           and v["unit"] in ("ms", "s")),
    "cubicBezier": lambda v: (isinstance(v, list) and len(v) == 4
                              and all(isinstance(n, (int, float)) for n in v)
                              and 0 <= v[0] <= 1 and 0 <= v[2] <= 1),
    "color": lambda v: (isinstance(v, dict) and isinstance(v.get("colorSpace"), str)
                        and isinstance(v.get("components"), list)
                        and all(isinstance(n, (int, float)) for n in v["components"])),
    "shadow": lambda v: all(
        isinstance(l, dict) and set(l) == {"color", "offsetX", "offsetY", "blur", "spread"}
        and DTCG_SHAPE["color"](l["color"])
        and all(DTCG_SHAPE["dimension"](l[k]) for k in
                ("offsetX", "offsetY", "blur", "spread"))
        for l in (v if isinstance(v, list) else [v])),
    "fontFamily": lambda v: (isinstance(v, str) or (
        isinstance(v, list) and v and all(isinstance(n, str) and n for n in v))),
}


def dtcg_violations(doc, path=""):
    """Every token in the emitted document, against the $value syntax its $type names."""
    bad = []
    for key, node in doc.items():
        if key.startswith("$") or not isinstance(node, dict):
            continue
        where = f"{path}{key}"
        if "$value" not in node:
            bad += dtcg_violations(node, where + ".")
            continue
        kind = node.get("$type") or doc.get("$type")
        if kind not in DTCG_SHAPE:
            bad.append(f"{where}: $type {kind!r} is not a type the module defines")
        elif not DTCG_SHAPE[kind](node["$value"]):
            bad.append(f"{where}: $value {node['$value']!r} is not a valid {kind}")
    return bad


RULES = [
    "Never write a literal colour, size, radius, duration, breakpoint or z-index. A value the "
    "system lacks is a gap to report, not a number to invent.",
    "Use a role, never a ramp step: a role carries its step's contrast floor, and a step chosen "
    "by eye carries none.",
    "The primary action is hw-ink and carries no hue. There is exactly one per screen.",
    "Every state carries a word, never a colour alone.",
    "No gradient behind text, no backdrop-filter, no shadow on anything that cannot be "
    "dismissed. A patterned ground carries only ink certified against its own worst pixel.",
    "Type, space and control sizes are rem, so the text-size setting moves them; never set one "
    "in px. Page gutters, breakpoints and the 44px touch floor are the px exceptions.",
    "Uppercase exists at one step, xs, for a column head or an eyebrow.",
    "Every column of figures takes tabular-nums.",
    "Left-aligned by default. Centre only a single-element empty state or a dialog action row.",
    "The focus ring is never removed.",
    "No invented quotes, logos, metrics or placeholder data presented as real.",
]

ANSWERS = [
    ('`[data-theme="dark"]`, or `prefers-color-scheme: dark` when the page names no theme',
     "the dark set"),
    ("`prefers-contrast: more`", "muted text, lines, the focus ring, solids and state text "
                                 "move to step 12, which clears 7:1"),
    ('`data-text-size="s|m|l|xl|xxl"` on `html`', "the root size, so every rem step moves"),
    ('`data-density="compact"` on any ancestor', "control height, row height and vertical "
                                                 "cell and field padding"),
    ("`pointer: coarse`", "a control never measures under 44px, compact or not, at any text size"),
    ("`prefers-reduced-motion: reduce`", "durations collapse to 100ms and only colour and "
                                         "opacity still transition"),
]


def fmt_px(v):
    return "-" if v is None else f"{round(v, 1):g}"


def emit_design_md(src, compact):
    tokens, every = src["tokens"], modes(src)
    env, sizes = every["light"], text_sizes(src)
    m_px = dict((s, px) for s, _, px in sizes)["m"]
    rs = [(k, resolve(env[k], env)) for k, _ in roles(src)]
    colours = [(k, v) for k, v in rs if is_colour(v)]
    out = [f"# {tokens['name']}, brand {src['brand']} - DESIGN.md",
           "",
           "Generated by `tools/export.py` from `ramps/` and `tokens/tokens.json`. Do not hand-edit.",
           "",
           f"A house design system: {len(colours)} colour roles, each naming a step of a "
           f"twelve-step ramp that carries its contrast floor, in two themes and a "
           f"`prefers-contrast: more` set; one type ramp, space and control sizes in rem under "
           f"{len(sizes)} text sizes; two densities. `variables.css` and `theme.css` carry every "
           f"block below.",
           "",
           "## Rules that are not negotiable", ""]
    out += [f"{i}. {r}" for i, r in enumerate(RULES, 1)]
    out += ["", "## What the CSS answers", "", "| when | what moves |", "|---|---|"]
    out += [f"| {w} | {what} |" for w, what in ANSWERS]
    out += ["", "## Colour roles", ""]
    desc = src["describe"]
    if compact:
        out += ["| role | light | dark | role |", "|---|---|---|---|"]
        out += [f"| `{k}` | `{v}` | `{resolve(every['dark'][k], every['dark'])}` | "
                f"{desc.get(k, '')} |" for k, v in colours]
    else:
        out += ["| role | " + " | ".join(MODES) + " | role |", "|---|" + "---|" * len(MODES) + "---|"]
        out += [f"| `{k}` | " + " | ".join(f"`{resolve(every[m][k], every[m])}`" for m in MODES)
                + f" | {desc.get(k, '')} |" for k, _ in colours]
    out += ["", "## Text size", "",
            f"The root size at the browser's default {BROWSER_DEFAULT_PX}px, and every type step "
            "at it, in px. A reader who raised the browser's own default keeps that raise.", ""]
    steps = [(k, raw) for k, raw in roles(src) if k.startswith("--hw-text-") and not is_colour(
        resolve(env[k], env))]
    out += ["| setting | root | " + " | ".join(k[len("--hw-text-"):] for k, _ in steps) + " |",
            "|---|---|" + "---|" * len(steps)]
    for s, css, px in sizes:
        out.append(f"| `{s}` | {px:g} ({css}) | " + " | ".join(
            fmt_px(at_root(raw, px) and round(at_root(raw, px), 1)) for _, raw in steps) + " |")
    out += ["", "A `-` is a stage size, set by `clamp()` against the viewport as well.", ""]
    for fam in ("type", "spacing", "density", "duration", "easing"):
        rows = [(k, v) for k, v in rs if not is_colour(v) and role_family(k, v) == fam]
        out += [f"## {fam}", ""]
        if compact:
            out += ["  ".join(f"`{k}` {v}" for k, v in rows), ""]
            continue
        out += [f"| token | value | px at M | role |", "|---|---|---|---|"]
        out += [f"| `{k}` | `{v}` | {fmt_px(at_root(v, m_px))} | {desc.get(k, '')} |"
                for k, v in rows]
        out.append("")
    for fam in CARRIED:
        entries = tokens[fam]["tokens"]
        out += [f"## {fam}", ""]
        val = lambda e: e["value"] if isinstance(e["value"], str) else e["value"]["light"]
        if compact:
            out += ["  ".join(f"`--{e['name']}` {val(e)}" for e in entries), ""]
            continue
        out += ["| token | value | role |", "|---|---|---|"]
        out += [f"| `--{e['name']}` | `{val(e)}` | {e.get('usage', '')} |" for e in entries]
        out.append("")
    if not compact:
        out += ["## Faces", ""]
        face = tokens["type"].get("faceDeclarations", {})
        for key, stack in tokens["type"]["families"].items():
            out.append(f"- **{key}**: `--hw-font-{key}`, `{stack}`"
                       + (f", with `{face[key]}`" if key in face else ""))
        if tokens["type"].get("quoteSizeAdjust"):
            out.append(f"- The quote face sets the words a person said or wrote, inside a step, "
                       f"with `font-size-adjust: {tokens['type']['quoteSizeAdjust']}`.")
        if tokens["type"].get("sansSizeAdjust"):
            out.append(f"- The text face is held to the house x-height: set `font-size-adjust: "
                       f"{tokens['type']['sansSizeAdjust']}` wherever `--hw-font-sans` is set.")
        out += ["", "## What this file does not carry", "",
                "The ramp steps themselves (`--hw-<hue>-1` to `-12`, in `variables.css`, named "
                "only through a role), the reasoning, the measurements every value was solved "
                "against, the component anatomies, the anti-pattern list and the spec sheet of "
                "named assets. Those are the numbered files beside this one; `README.md` says "
                "which answers what.", "",
                "Chart colours have no role yet and are a stated gap, followed up in "
                "house-chart-roles-r8: `--hw-chart-1` to `-6` stay in `tokens/tokens.json` and "
                "`tokens/tokens.css` but carry no name in `ramps/roles.css`, so this export "
                "does not carry them either.", ""]
    return "\n".join(out)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT)
    try:
        src = sources(root)
    except ValueError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    tokens = src["tokens"]

    bad = check_sources(src, root)
    if bad:
        for b in bad:
            print("FAIL  " + b, file=sys.stderr)
        print(f"\nrefusing to write: {len(bad)} disagreement(s) between the sources",
              file=sys.stderr)
        return 1
    try:
        dtcg = emit_dtcg(src)
    except ValueError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        print("\nrefusing to write: the DTCG export would not be valid DTCG", file=sys.stderr)
        return 1

    written = {
        "DESIGN.md": emit_design_md(src, compact=False),
        "DESIGN.compact.md": emit_design_md(src, compact=True),
        "theme.css": emit_theme_css(src),
        "variables.css": emit_variables_css(src),
        "design-tokens.json": dtcg,
    }
    out = root / "exports"
    out.mkdir(exist_ok=True)
    for name, text in written.items():
        (out / name).write_text(text, encoding="utf-8")

    # Measure the artifact: read the files back from disk, not the strings that were meant.
    gaps = check_written(src, {n: (out / n).read_text(encoding="utf-8") for n in written})
    if gaps:
        for g in gaps:
            print("FAIL  " + g, file=sys.stderr)
        print(f"\nexport wrote, but it is not equivalent to its sources: {len(gaps)} gap(s)",
              file=sys.stderr)
        return 1

    n_blocks = len(expected_blocks(src))
    print(f"brand {src['brand']}: {len(roles(src))} roles and scales from ramps/roles.css, "
          f"resolved in {len(MODES)} modes; {sum(1 for _ in carried(tokens))} carried from "
          f"tokens.json.")
    for name in written:
        print(f"  exports/{name:20s} {len(written[name]):7,d} bytes")
    print(f"\n{n_blocks} CSS blocks re-read from both CSS exports, 0 divergent, "
          f"{len(REQUIRED)} required conditions present. 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
