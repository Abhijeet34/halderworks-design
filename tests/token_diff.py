#!/usr/bin/env python3
"""tools/token-diff.py puts a moved token in the pull request comment, and nothing else there.

A role moved one ramp step is a few components in exports/design-tokens.json, so each case
edits a copy of the committed file the way a step change does and reads what the comment says:
the token and mode named with the old and new value, an untouched file reported as no change, a
base without the file read as every token added, and removed and added names listed.

    python3 tests/token_diff.py
"""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "token-diff.py"
COMMITTED = json.loads((ROOT / "exports" / "design-tokens.json").read_text(encoding="utf-8"))


def comment(old: dict | None, new: dict, tmp: Path, name: str) -> str:
    new_path = tmp / f"{name}-new.json"
    new_path.write_text(json.dumps(new), encoding="utf-8")
    old_path = tmp / f"{name}-old.json"
    if old is not None:
        old_path.write_text(json.dumps(old), encoding="utf-8")
    p = subprocess.run([sys.executable, str(TOOL), str(old_path), str(new_path)],
                       capture_output=True, text=True, timeout=60)
    if p.returncode:
        return f"exit {p.returncode}: {p.stderr}"
    return p.stdout


def main() -> int:
    fails = []

    def check(label: str, ok: bool, got: str) -> None:
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        if not ok:
            fails.append(f"{label}: {got[:400]}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        same = comment(COMMITTED, COMMITTED, tmp, "same")
        check("an untouched file is reported as no change", "no change" in same, same)
        check("the comment opens with the marker the workflow updates in place",
              same.startswith("<!-- token-diff -->"), same)

        # --hw-text-muted moved from one ramp step to another in the dark mode only.
        moved = copy.deepcopy(COMMITTED)
        token = moved["color"]["text-muted"]
        before = token["$extensions"]["halderworks"]["modes"]["dark"]["components"][0]
        token["$extensions"]["halderworks"]["modes"]["dark"]["components"][0] = round(before + 0.05, 3)
        out = comment(COMMITTED, moved, tmp, "moved")
        check("a role step change names the token, the mode and both values",
              "1 changed, 0 added, 0 removed" in out and "| `color.text-muted` | dark |" in out
              and f"oklch({before:g} " in out and f"oklch({round(before + 0.05, 3):g} " in out, out)
        check("a mode that did not move is not listed", "| light |" not in out, out)

        changed = copy.deepcopy(COMMITTED)
        del changed["color"]["scrim"]
        changed["color"]["brand-new"] = copy.deepcopy(COMMITTED["color"]["bg"])
        out = comment(COMMITTED, changed, tmp, "names")
        check("an added and a removed token are listed by name",
              "Added: `color.brand-new`" in out and "Removed: `color.scrim`" in out, out)

        out = comment(None, COMMITTED, tmp, "nobase")
        check("a base without the file reads as every token added",
              "0 changed," in out and " 0 removed" in out and "`color.bg`" in out, out)

    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
