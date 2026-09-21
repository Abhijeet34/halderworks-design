#!/usr/bin/env python3
"""Emit this system in the five interchange formats, from tokens.json alone.

The requirement is that the book be usable irrespective of which model reads it.
A design system that exists only as prose is a system every agent re-interprets; these five
are the forms agents actually consume:

  exports/DESIGN.md            the extended brief: every token with its role, plus the rules
  exports/DESIGN.compact.md    the short brief, for a context window that cannot take the long one
  exports/theme.css            a Tailwind v4 @theme block
  exports/variables.css        plain CSS custom properties, both themes
  exports/design-tokens.json   W3C DTCG format, $value / $type / $description per token

This is NOT tools/build.py. build.py solves colour to a contrast target; this only re-expresses
values that are already solved, so it can never invent one - and it proves that by re-deriving
every colour it emits against the shipped tokens.css and refusing to write if any one differs.
The DTCG file is held to its own module's value syntax as well, by dtcg_violations().

    python3 tools/export.py [design-system-dir]
"""
import json
import re
import sys
from pathlib import Path

# Tailwind v4 reads these namespaces to generate utilities. A family mapped to the wrong one
# emits a variable that works in var() and generates no class, which looks fine until someone
# writes `rounded-lg` and gets nothing.
TW_NAMESPACE = {
    "color": "color", "spacing": "spacing", "radius": "radius",
    "shadow": "shadow", "icon": "spacing",
}
# Design Tokens Format Module 2025.10 types a value by its SHAPE, not by the family it sits
# in: a dimension is {value, unit} with unit px or rem, a duration is {value, unit} in ms or s,
# a cubicBezier is four numbers, a colour is a colour space plus components. A CSS string under
# any of those types is an invalid token, and a family map cannot type `layout`, which holds
# lengths, a count and two measures in ch. So the type is read off the value.
NUM = r"-?\d+(?:\.\d+)?"
DIMENSION = re.compile(rf"^({NUM})(px|rem)$")
DURATION = re.compile(rf"^({NUM})(ms|s)$")
BEZIER = re.compile(
    rf"^cubic-bezier\(\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*\)$")
OKLCH = re.compile(rf"^oklch\(\s*({NUM})\s+({NUM})\s+({NUM})\s*\)$")
RGBA = re.compile(
    rf"^rgba?\(\s*({NUM})\s*,\s*({NUM})\s*,\s*({NUM})\s*(?:,\s*({NUM})\s*)?\)$")
CHARS = re.compile(rf"^({NUM})ch$")
BARE = re.compile(rf"^{NUM}$")


def load(root):
    return json.loads((root / "tokens" / "tokens.json").read_text(encoding="utf-8"))


def families(tokens):
    """(family, [entries]) for every token family, type excluded - it has its own shape."""
    for fam, v in tokens.items():
        if fam in ("name", "version") or not isinstance(v, dict) or "tokens" not in v:
            continue
        yield fam, v["tokens"]


def theme_ids(tokens):
    return [t["id"] for t in tokens["color"]["themes"]]


def value_for(entry, theme, first):
    v = entry["value"]
    if isinstance(v, str):
        return v
    return v.get(theme, v.get(first))


def num(text):
    """A JSON number, integral where the CSS was integral, so 0 does not ship as 0.0."""
    f = float(text)
    return int(f) if f == int(f) else f


def as_color(value):
    m = OKLCH.match(value)
    if m:
        return {"colorSpace": "oklch", "components": [num(g) for g in m.groups()]}
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
    if OKLCH.match(value) or RGBA.match(value):
        return {"$type": "color", "$value": as_color(value)}
    if DIMENSION.match(value):
        return {"$type": "dimension", "$value": as_dimension(value)}
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


# --- the self-check, which is why this file is allowed to write anything ------------------

CSS_VAR = re.compile(r"^\s*(--hw-[a-z0-9-]+):\s*([^;]+);")


def shipped_css(root):
    """{theme: {name: value}} from tokens.css, the file products actually load."""
    out, cur = {"light": {}, "dark": {}}, None
    for line in (root / "tokens" / "tokens.css").read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith(':root, [data-theme="light"]'):
            cur = "light"; continue
        if s.startswith('[data-theme="dark"]'):
            cur = "dark"; continue
        if s.startswith("@media (prefers-color-scheme"):
            cur = None; continue
        m = CSS_VAR.match(line)
        if m and cur:
            out[cur][m.group(1)] = m.group(2).strip()
    return out


def verify(tokens, root):
    """Every colour this emitter would write must equal what tokens.css already ships.

    An exporter that can disagree with the file products load is worse than no exporter: it
    hands an agent a palette nobody rendered. Checked per theme, not just on the light block,
    because the two are solved separately and only one of them was ever wrong before.
    """
    css, ids = shipped_css(root), theme_ids(tokens)
    bad = []
    for entry in tokens["color"]["tokens"]:
        for theme in ids:
            want = value_for(entry, theme, ids[0])
            got = css.get(theme, {}).get("--" + entry["name"])
            if got is None:
                bad.append(f"{entry['name']} ({theme}) is in tokens.json and not in tokens.css")
            elif got != want:
                bad.append(f"{entry['name']} ({theme}): tokens.json {want!r} != tokens.css {got!r}")
    return bad


BASE_SELECTORS = {':root, [data-theme="light"]': "light",
                  '[data-theme="dark"]': "dark", ":root": "root"}


def base_blocks(path):
    """The three UNCONDITIONAL blocks of a token stylesheet, keyed by theme.

    Everything else - @media, [data-density], the prefers-color-scheme copy, the .hw-*
    classes - is an override rather than a declaration, and reading one as a declaration is
    how a comparison reports four phantom differences.
    """
    out, cur = {"light": {}, "dark": {}, "root": {}}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.endswith("{"):
            cur = BASE_SELECTORS.get(s[:-1].strip())
            continue
        if s.startswith("}"):
            cur = None
            continue
        m = CSS_VAR.match(line)
        if m and cur:
            out[cur][m.group(1)] = m.group(2).strip()
    return out


# --- emitters -----------------------------------------------------------------------------

def emit_variables_css(tokens):
    ids = theme_ids(tokens)
    out = ["/* Halderworks Instrument - plain CSS custom properties.",
           "   Generated by tools/export.py from tokens.json. Do not hand-edit.",
           f"   {len(tokens['color']['tokens'])} colour tokens, {len(ids)} themes. */", ""]
    themed = [f for f, _ in families(tokens) if any(
        isinstance(e["value"], dict) for e in dict(families(tokens))[f])]
    for i, theme in enumerate(ids):
        sel = ':root, [data-theme="light"]' if i == 0 else f'[data-theme="{theme}"]'
        out.append(sel + " {")
        for fam, entries in families(tokens):
            if fam not in themed:
                continue
            for e in entries:
                out.append(f"  --{e['name']}: {value_for(e, theme, ids[0])};")
        out.append("}")
        out.append("")
    out.append(":root {")
    for fam, entries in families(tokens):
        if fam in themed:
            continue
        for e in entries:
            out.append(f"  --{e['name']}: {value_for(e, ids[0], ids[0])};")
    for key, stack in tokens["type"]["families"].items():
        out.append(f"  --hw-font-{key}: {stack};")
    for g in tokens["type"]["groups"]:
        for s in g["styles"]:
            out.append(f"  --hw-text-{s['name']}: {s['fontSize']};")
            out.append(f"  --hw-leading-{s['name']}: {s['lineHeight']};")
            out.append(f"  --hw-tracking-{s['name']}: {s.get('letterSpacing', '0')};")
            out.append(f"  --hw-weight-{s['name']}: {s['fontWeight']};")
    out.append("}")
    # Without this the export silently drops an accessibility accommodation that tokens.css
    # has always carried. Reduced motion removes the movement and keeps the feedback, so the
    # durations collapse and nothing is set to none. 40-motion.md owns the rule.
    # Compact density is one attribute rebinding four tokens. Emitting the values without it
    # ships a system that has one density, which is not this system.
    if "density" in tokens:
        out += ["", '[data-density="compact"] {',
                "  --hw-control-h: var(--hw-control-h-sm);",
                "  --hw-row-h: var(--hw-row-h-compact);",
                "  --hw-cell-pad-y: var(--hw-cell-pad-y-compact);",
                "  --hw-field-pad-y: var(--hw-field-pad-y-compact);", "}"]
    if "duration" in tokens:
        out += ["", "@media (prefers-reduced-motion: reduce) {", "  :root {",
                "    --hw-duration-instant: 1ms;", "    --hw-duration-fast: 100ms;",
                "    --hw-duration-base: 100ms;", "    --hw-duration-slow: 100ms;",
                "  }", "}"]
    return "\n".join(out) + "\n"


def emit_theme_css(tokens):
    """Tailwind v4. @theme cannot be conditional, so the first theme goes in the block and
    every other theme is an override after it - stated rather than silently dropped."""
    ids = theme_ids(tokens)
    out = ["/* Halderworks Instrument - Tailwind v4.",
           "   Generated by tools/export.py from tokens.json. Do not hand-edit.",
           "   @theme carries the first theme; later themes override under their attribute,",
           "   because an @theme block cannot itself be conditional. */", "",
           '@import "tailwindcss";', "", "@theme {"]
    for fam, entries in families(tokens):
        ns = TW_NAMESPACE.get(fam)
        out.append(f"  /* {fam} */")
        for e in entries:
            short = e["name"][len("hw-"):]
            name = f"--{ns}-{short}" if ns else f"--{e['name']}"
            out.append(f"  {name}: {value_for(e, ids[0], ids[0])};")
    out.append("  /* type */")
    for key, stack in tokens["type"]["families"].items():
        out.append(f"  --font-{key}: {stack};")
    for g in tokens["type"]["groups"]:
        for s in g["styles"]:
            out.append(f"  --text-{s['name']}: {s['fontSize']};")
            out.append(f"  --text-{s['name']}--line-height: {s['lineHeight']};")
            if s.get("letterSpacing"):
                out.append(f"  --text-{s['name']}--letter-spacing: {s['letterSpacing']};")
            if s.get("fontWeight"):
                out.append(f"  --text-{s['name']}--font-weight: {s['fontWeight']};")
    out.append("}")
    for theme in ids[1:]:
        out += ["", f'[data-theme="{theme}"] {{']
        for e in tokens["color"]["tokens"]:
            out.append(f"  --color-{e['name'][len('hw-'):]}: {value_for(e, theme, ids[0])};")
        out.append("}")
    return "\n".join(out) + "\n"


def emit_dtcg(tokens):
    ids = theme_ids(tokens)
    doc = {"$description": (
        "Halderworks Instrument. Generated by tools/export.py from tokens.json, to the Design "
        "Tokens Format Module 2025.10. Colour tokens carry one $value per theme under "
        "$extensions.halderworks.themes; $value is the first theme.")}
    for fam, entries in families(tokens):
        group = {"$description": f"{fam} tokens"}
        for e in entries:
            node = dtcg_node(fam, value_for(e, ids[0], ids[0]))
            node["$description"] = e.get("usage", "")
            if isinstance(e["value"], dict):
                themes = {t: dtcg_node(fam, value_for(e, t, ids[0]))["$value"] for t in ids}
                node.setdefault("$extensions", {}).setdefault(
                    "halderworks", {})["themes"] = themes
            group[e["name"][len("hw-"):]] = node
        doc[fam] = group
    typ = {"$description": "type styles", "$type": "typography"}
    for g in tokens["type"]["groups"]:
        for s in g["styles"]:
            node = {"$type": "typography", "$description": s.get("usage", ""),
                    "$value": {"fontFamily": font_stack(tokens, g["family"]),
                               "fontSize": as_dimension(s["fontSize"]),
                               "lineHeight": s["lineHeight"],
                               "fontWeight": s["fontWeight"]}}
            # letterSpacing is a dimension in DTCG and this system tracks in em, which the
            # module's dimension does not admit. Emitting "-0.022em" under it would be an
            # invalid token, and converting to px would bind the tracking to one font size.
            if s.get("letterSpacing"):
                node["$extensions"] = {"halderworks": {"letterSpacing": s["letterSpacing"]}}
            typ[s["name"]] = node
    doc["type"] = typ
    bad = dtcg_violations(doc)
    if bad:
        raise ValueError("; ".join(bad))
    return json.dumps(doc, indent=2) + "\n"


def font_stack(tokens, family):
    """A DTCG fontFamily is an ordered list of names, not one CSS string."""
    return [n.strip().strip('"') for n in tokens["type"]["families"][family].split(",")]


# Every $type below is a type the module defines, and every check is its $value syntax. The
# emitter is the only thing that decides a type, so nothing else in this repository would
# notice it deciding wrongly: this is what makes "W3C DTCG" a checked claim rather than a
# label. Section 9.8's own example is the authority for the typography shape.
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
    "typography": lambda v: (isinstance(v, dict) and isinstance(v.get("fontFamily"), list)
                             and DTCG_SHAPE["dimension"](v.get("fontSize"))
                             and isinstance(v.get("lineHeight"), (int, float))
                             and isinstance(v.get("fontWeight"), (int, float))),
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
    "Put ink only on a ground the permission table allows. Never re-derive a ratio by eye.",
    "The primary action is hw-ink and carries no hue. There is exactly one per screen.",
    "The accent has four jobs: a link, a selected row, a live state, the focus ring. A screen "
    "with no state on it has no hue on it.",
    "Every state carries a word, never a colour alone.",
    "No gradient behind text, no backdrop-filter, no shadow on anything that cannot be "
    "dismissed. A patterned ground carries only ink certified against its own worst pixel.",
    "Uppercase exists at one step, micro, for a column head or an eyebrow.",
    "Every column of figures takes tabular-nums.",
    "Left-aligned by default. Centre only a single-element empty state or a dialog action row.",
    "The focus ring is never removed.",
    "No invented quotes, logos, metrics or placeholder data presented as real.",
]


def emit_design_md(tokens, compact):
    ids = theme_ids(tokens)
    n_col = len(tokens["color"]["tokens"])
    out = [f"# {tokens['name']} - DESIGN.md",
           "",
           "Generated by `tools/export.py` from `tokens.json`. Do not hand-edit.",
           "",
           f"A house design system: one token set, {len(ids)} themes, two densities. "
           f"{n_col} colour tokens per theme, all pairs certified at WCAG AA for text and "
           f"3:1 for non-text indicators. Neutral ground, one accent hue, colour spent only "
           f"where a state is reported.",
           "",
           "## Rules that are not negotiable", ""]
    out += [f"{i}. {r}" for i, r in enumerate(RULES, 1)]
    out += ["", "## Tokens", ""]
    for fam, entries in families(tokens):
        out += [f"### {fam}", ""]
        if fam == "color":
            out += ["| token | " + " | ".join(ids) + " | role |",
                    "|---|" + "---|" * len(ids) + "---|"]
            for e in entries:
                vals = " | ".join(f"`{value_for(e, t, ids[0])}`" for t in ids)
                role = e.get("usage", "") if not compact else e.get("usage", "").split(".")[0]
                out.append(f"| `--{e['name']}` | {vals} | {role} |")
        elif compact:
            # One line per family. The compact brief exists for a context window that cannot
            # take the long one, so a family whose values are a scale is a scale, not a table.
            out += ["  ".join(f"`--{e['name']}` {value_for(e, ids[0], ids[0])}"
                              for e in entries), ""]
        else:
            out += ["| token | value | role |", "|---|---|---|"]
            for e in entries:
                out.append(f"| `--{e['name']}` | `{value_for(e, ids[0], ids[0])}` | "
                           f"{e.get('usage', '')} |")
        out.append("")
    out += ["### type", "", "| step | face | size | line-height | tracking | weight | role |",
            "|---|---|---|---|---|---|---|"]
    for g in tokens["type"]["groups"]:
        for s in g["styles"]:
            role = s.get("usage", "") if not compact else s.get("usage", "").split(".")[0]
            out.append(f"| `{s['name']}` | {g['family']} | {s.get('fontSize','')} | "
                       f"{s.get('lineHeight','')} | {s.get('letterSpacing','0')} | "
                       f"{s.get('fontWeight','')} | {role} |")
    out.append("")
    if not compact:
        out += ["## Faces", ""]
        for key, stack in tokens["type"]["families"].items():
            out.append(f"- **{key}**: `{stack}`")
        out += ["", "## What this file does not carry", "",
                "The reasoning, the measurements every value was solved against, the component "
                "anatomies, the anti-pattern list and the spec sheet of named assets. Those are "
                "the numbered files beside this one; `README.md` says which answers what.", ""]
    return "\n".join(out)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
    tokens = load(root)

    bad = verify(tokens, root)
    if bad:
        for b in bad:
            print("FAIL  " + b, file=sys.stderr)
        print(f"\nrefusing to write: {len(bad)} token(s) disagree with tokens.css",
              file=sys.stderr)
        return 1

    out = root / "exports"
    out.mkdir(exist_ok=True)
    try:
        dtcg = emit_dtcg(tokens)
    except ValueError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        print("\nrefusing to write: the DTCG export would not be valid DTCG", file=sys.stderr)
        return 1

    written = {
        "DESIGN.md": emit_design_md(tokens, compact=False),
        "DESIGN.compact.md": emit_design_md(tokens, compact=True),
        "theme.css": emit_theme_css(tokens),
        "variables.css": emit_variables_css(tokens),
        "design-tokens.json": dtcg,
    }
    for name, text in written.items():
        (out / name).write_text(text, encoding="utf-8")

    # The export is only worth anything if it IS the system. Found three real omissions when
    # it was first run by hand - the per-step leading/tracking/weight, reduced motion, and
    # compact density - each of which would have shipped a quietly different system to
    # whichever agent read the export instead of tokens.css.
    drift = base_blocks(root / "tokens" / "tokens.css")
    mine = base_blocks(out / "variables.css")
    gaps = []
    for block in ("light", "dark", "root"):
        for k in sorted(set(drift[block]) ^ set(mine[block])):
            gaps.append(f"{k} is in only one of tokens.css and exports/variables.css [{block}]")
        for k in sorted(set(drift[block]) & set(mine[block])):
            if drift[block][k] != mine[block][k]:
                gaps.append(f"{k} [{block}]: tokens.css {drift[block][k]!r} != export "
                            f"{mine[block][k]!r}")
    if gaps:
        for g in gaps:
            print("FAIL  " + g, file=sys.stderr)
        print(f"\nexport wrote, but it is not equivalent to tokens.css: {len(gaps)} gap(s)",
              file=sys.stderr)
        return 1
    n_props = sum(len(drift[b]) for b in drift)

    n = sum(len(e) for _, e in families(tokens)) + sum(
        len(g["styles"]) for g in tokens["type"]["groups"])
    print(f"{len(tokens['color']['tokens'])} colour tokens re-derived against tokens.css, "
          f"0 mismatched.")
    for name in written:
        print(f"  exports/{name:20s} {len(written[name]):7,d} bytes")
    print(f"\n{n} tokens exported in {len(written)} formats. {n_props} CSS custom properties "
          f"re-derived against tokens.css, 0 divergent. 0 failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
