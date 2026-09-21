#!/usr/bin/env python3
"""Read a face's x-height and cap height from its font file, and hold the roster to the file.

A brand names its display and text faces from the roster in tokens/tokens.seed.json, and the one
number the build takes from a face is the house text face's x-height, which every brand's text
face is held to with `font-size-adjust`. 20-type.md measured that number in a browser at 100px;
this reads it from the file, with the standard library, so a roster entry is a measurement a
reader can repeat rather than a number somebody typed.

    python3 tools/faces.py FONT...            # print x-height, cap height and sha256 per file
    python3 tools/faces.py --check FONT...    # and refuse any file whose roster entry disagrees

The repository vendors no font, so this runs on demand against a copy of the upstream file each
roster entry cites, not in CI. A file is matched to its entry by sha256, which is the check that
the metrics were read from the file the roster says they were.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sfnt_offsets(data):
    """The start of every font in the file: one for a .ttf or .otf, several for a .ttc."""
    if data[:4] == b"ttcf":
        n = struct.unpack(">I", data[8:12])[0]
        return list(struct.unpack(f">{n}I", data[12:12 + 4 * n]))
    return [0]


def table(data, base, tag):
    n = struct.unpack(">H", data[base + 4:base + 6])[0]
    for i in range(n):
        rec = base + 12 + 16 * i
        if data[rec:rec + 4] == tag:
            return struct.unpack(">I", data[rec + 8:rec + 12])[0]
    raise ValueError(f"no {tag.decode()} table")


def metrics(data, base=0):
    """(x-height, cap height), each over units per em. OS/2 carries both from version 2 on, and
    a file too old to carry them is refused rather than guessed at."""
    head, os2 = table(data, base, b"head"), table(data, base, b"OS/2")
    upm = struct.unpack(">H", data[head + 18:head + 20])[0]
    if struct.unpack(">H", data[os2:os2 + 2])[0] < 2:
        raise ValueError("OS/2 table older than version 2 carries no x-height")
    x, cap = struct.unpack(">hh", data[os2 + 86:os2 + 90])
    return x / upm, cap / upm


def roster():
    seed = json.loads((ROOT / "tokens" / "tokens.seed.json").read_text(encoding="utf-8"))
    return seed["brand"]["faces"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("fonts", nargs="+", type=Path)
    ap.add_argument("--check", action="store_true",
                    help="refuse a file whose roster entry carries different metrics")
    a = ap.parse_args(argv)
    by_hash = {f["sha256"]: name for name, f in roster().items() if "sha256" in f}
    failures = []
    for path in a.fonts:
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        for base in sfnt_offsets(data):
            x, cap = metrics(data, base)
            name = by_hash.get(digest)
            print(f"{path.name:44} x-height {x:.3f}  cap {cap:.3f}  x/cap {x / cap:.3f}  "
                  f"{digest[:12]}  {name or 'not in the roster'}")
        if not a.check:
            continue
        if name is None:
            failures.append(f"{path.name}: sha256 {digest} matches no roster entry")
        elif abs(roster()[name]["xHeight"] - round(x, 3)) > 0.0005:
            failures.append(f"{name}: the roster says x-height {roster()[name]['xHeight']} and "
                            f"{path.name} measures {x:.3f}")
    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    if a.check:
        print(f"\n{len(a.fonts)} file(s) against the roster, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
