#!/usr/bin/env python3
"""Markdown for what changed between two exports/design-tokens.json files.

    python3 tools/token-diff.py OLD NEW

A change to a role's ramp step is a few lines in this output and a 3,800-line diff in the file,
repeated in four directories, so the pull request comment carries this instead. A path that does
not exist reads as an empty token set, which is how a base branch without the file is diffed.
Starts with MARKER so the workflow can find its own comment and update it in place.
"""
import json
import sys
from pathlib import Path

MARKER = "<!-- token-diff -->"


def tokens(path: Path) -> dict[str, dict]:
    """Every leaf token by dotted path, keeping what a consumer sees: value, modes, conditions."""
    if not path.exists():
        return {}
    out: dict[str, dict] = {}

    def walk(node: dict, trail: tuple[str, ...]) -> None:
        if "$value" in node:
            ext = node.get("$extensions", {}).get("halderworks", {})
            out[".".join(trail)] = {"value": node["$value"], **{
                k: ext[k] for k in ("modes", "conditions", "css") if k in ext}}
            return
        for key, child in node.items():
            if isinstance(child, dict) and not key.startswith("$"):
                walk(child, trail + (key,))

    walk(json.loads(path.read_text(encoding="utf-8")), ())
    return out


def show(value) -> str:
    """One short string for a token value; a colour reads as its oklch components."""
    if isinstance(value, dict) and "components" in value:
        return f"oklch({' '.join(f'{c:g}' for c in value['components'])})"
    if isinstance(value, dict) and "value" in value and "unit" in value:
        return f"{value['value']:g}{value['unit']}"
    return json.dumps(value, sort_keys=True)


def facets(token: dict) -> dict[str, str]:
    """The token flattened to labelled strings: `value`, then one per mode or condition."""
    out = {"value": show(token["value"])}
    for group in ("modes", "conditions"):
        for name, value in token.get(group, {}).items():
            out[name] = show(value)
    if "css" in token:
        out["css"] = token["css"]
    return out


def diff(old: dict[str, dict], new: dict[str, dict]) -> str:
    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    changed = [k for k in sorted(old.keys() & new.keys()) if old[k] != new[k]]
    if not (added or removed or changed):
        return f"{MARKER}\n**Tokens:** no change to `exports/design-tokens.json`.\n"
    lines = [MARKER, f"**Tokens:** {len(changed)} changed, {len(added)} added, "
             f"{len(removed)} removed in `exports/design-tokens.json`.", ""]
    if changed:
        lines += ["| token | where | before | after |", "|---|---|---|---|"]
        for key in changed:
            before, after = facets(old[key]), facets(new[key])
            for where in before.keys() | after.keys():
                if before.get(where) != after.get(where):
                    lines.append(f"| `{key}` | {where} | `{before.get(where, '-')}` "
                                 f"| `{after.get(where, '-')}` |")
        lines.append("")
    for title, keys in (("Added", added), ("Removed", removed)):
        if keys:
            lines += [f"{title}: " + ", ".join(f"`{k}`" for k in keys), ""]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    sys.stdout.write(diff(tokens(Path(sys.argv[1])), tokens(Path(sys.argv[2]))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
