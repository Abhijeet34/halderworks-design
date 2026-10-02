#!/usr/bin/env python3
"""Certify the ramps on the pixels a browser paints, not on a converter's prediction of them.

tools/contrast.py --ramps measures every pair on its own oklch-to-sRGB conversion. This renders
exactly the pairs it certifies, collected from contrast.certify_ramps rather than declared again,
in a headless Chromium (Brave first), screenshots them and measures the 8-bit pixels: a ratio
pair against its floor, a CIEDE2000 pair against its bar. Per brand it renders both themes, each
from the attribute and from the operating system's preference, and each under prefers-contrast:
more, so a pair is read in every cascade a page can reach.

    python3 tools/painted.py                     # every ramps/tokens/*.tokens.css
    python3 tools/painted.py ramps/tokens/house.tokens.css --browser PATH

Every page also paints a control, #777777 on white at 4.48:1, which must come back as exactly
those pixels and be refused; a run whose control holds has measured nothing, and exits 1.

Pixels come from Page.captureScreenshot and never from a canvas: Brave randomises
getImageData on http origins by a code value per channel (measured 2026-10-02: #FFFFFF read back
as 254,254,254, accent-9 68,116,207 as 69,117,207), which put labels that paint at 4.52:1
at 4.43:1. The browser is driven over --remote-debugging-pipe, so this needs no package and no
port, and it needs a sandbox that lets Chromium bind its profile's singleton socket.
"""
import argparse
import base64
import json
import os
import select
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contrast  # noqa: E402

ROOT = contrast.ROOT
ROLES = ROOT / "ramps" / "roles.css"
BROWSERS = ("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser", "brave-browser",
            "brave", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
# (name, data-theme, prefers-color-scheme): each theme from the attribute against the opposite
# preference, and from the preference with no attribute.
ROUTES = (("light", "light", "dark"), ("light from the OS", None, "light"),
          ("dark", "dark", "light"), ("dark from the OS", None, "dark"))
CELL, INNER, COLUMNS = 8, 4, 120   # a pair is an 8px ground with its 4px foreground centred
CONTROL = ("rgb(119, 119, 119)", "#FFFFFF", (119, 119, 119), (255, 255, 255))
TIMEOUT = 30


class BrowserError(Exception):
    pass


class Browser:
    """One headless Chromium, spoken to over the CDP pipe on fds 3 and 4."""

    def __init__(self, path, profile):
        to_child, self._w = os.pipe()
        self._r, from_child = os.pipe()

        def fds():
            a, b = os.dup(to_child), os.dup(from_child)
            os.dup2(a, 3)
            os.dup2(b, 4)
        self._log = tempfile.TemporaryFile()
        self.proc = subprocess.Popen(
            [path, "--headless=new", "--remote-debugging-pipe", f"--user-data-dir={profile}",
             "--force-color-profile=srgb", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--no-default-browser-check", "about:blank"],
            close_fds=False, preexec_fn=fds, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=self._log)
        os.close(to_child)
        os.close(from_child)
        self._n, self._buf, self.events = 0, b"", []
        target = self.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        self.session = self.call("Target.attachToTarget",
                                 {"targetId": target, "flatten": True})["sessionId"]
        self.call("Page.enable", page=True)

    def _message(self):
        while b"\0" not in self._buf:
            if not select.select([self._r], [], [], TIMEOUT)[0]:
                raise BrowserError(f"no answer in {TIMEOUT}s")
            chunk = os.read(self._r, 1 << 20)
            if not chunk:
                self._log.seek(0)
                tail = self._log.read().decode(errors="replace").strip().splitlines()[-3:]
                raise BrowserError("the browser exited: " + " | ".join(tail))
            self._buf += chunk
        raw, self._buf = self._buf.split(b"\0", 1)
        return json.loads(raw)

    def call(self, method, params=None, page=False):
        self._n += 1
        msg = {"id": self._n, "method": method, "params": params or {}}
        if page:
            msg["sessionId"] = self.session
        try:
            os.write(self._w, json.dumps(msg).encode() + b"\0")
        except BrokenPipeError:
            raise BrowserError("the browser closed its pipe") from None
        while True:
            m = self._message()
            if m.get("id") == self._n:
                if "error" in m:
                    raise BrowserError(f"{method}: {m['error'].get('message')}")
                return m["result"]
            self.events.append(m.get("method"))

    def wait(self, event):
        while event not in self.events:
            m = self._message()
            self.events.append(m.get("method"))
        self.events.clear()

    def close(self):
        try:
            self.call("Browser.close")
        except BrowserError:
            pass
        try:
            self.proc.wait(10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        os.close(self._w)
        os.close(self._r)


def pixels(png):
    """(width, rows of RGB tuples) from an 8-bit RGB or RGBA PNG, unfiltered by hand."""
    pos, idat = 8, b""
    while pos < len(png):
        size, kind = struct.unpack(">I4s", png[pos:pos + 8])
        data = png[pos + 8:pos + 8 + size]
        pos += 12 + size
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", data)
            if depth != 8 or ctype not in (2, 6) or interlace:
                raise BrowserError(f"a PNG this does not read: depth {depth}, type {ctype}")
        elif kind == b"IDAT":
            idat += data
    raw, bpp = zlib.decompress(idat), 4 if ctype == 6 else 3
    stride, prev, rows = w * bpp, bytearray(w * bpp), []
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b, c = prev[x], prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append([tuple(line[i:i + 3]) for i in range(0, stride, bpp)])
        prev = line
    return w, rows


def page(tokens, pairs):
    cells = [f'<b style="background:{CONTROL[1]}"><i style="color:{CONTROL[0]}"></i></b>']
    cells += [f'<b style="background:var({bg})"><i style="color:var({fg})"></i></b>'
              for fg, bg in pairs]
    return ("<!doctype html><html><head><meta charset=utf-8>"
            f'<link rel=stylesheet href="{tokens.as_uri()}"><link rel=stylesheet href="{ROLES.as_uri()}">'
            f"<style>html,body{{margin:0;background:#000}}body{{display:grid;grid-template-columns:"
            f"repeat({COLUMNS},{CELL}px);grid-auto-rows:{CELL}px}}b{{display:block}}"
            f"i{{display:block;margin:{(CELL - INNER) // 2}px;width:{INNER}px;height:{INNER}px;"
            "background:currentColor}</style></head><body>" + "".join(cells) + "</body></html>")


PROBE = """(names => ({theme: document.documentElement.dataset.theme || null,
  dark: matchMedia("(prefers-color-scheme: dark)").matches,
  more: matchMedia("(prefers-contrast: more)").matches,
  undeclared: names.filter(n => !getComputedStyle(document.documentElement).getPropertyValue(n).trim())}))"""


def paint(browser, html, path, theme, scheme, more, names, count):
    """The (fg, bg) pixels of `count` cells, after proving the page is in the condition asked."""
    path.write_text(html.replace("<html>", f'<html data-theme="{theme}">' if theme else "<html>"),
                    encoding="utf-8")
    browser.call("Emulation.setEmulatedMedia", {"features": [
        {"name": "prefers-color-scheme", "value": scheme},
        {"name": "prefers-contrast", "value": "more" if more else "no-preference"}]}, page=True)
    height = -(-count // COLUMNS) * CELL
    browser.call("Emulation.setDeviceMetricsOverride", {
        "width": COLUMNS * CELL, "height": height, "deviceScaleFactor": 1, "mobile": False},
        page=True)
    browser.events.clear()
    browser.call("Page.navigate", {"url": path.as_uri()}, page=True)
    browser.wait("Page.loadEventFired")
    got = browser.call("Runtime.evaluate", {"expression": f"{PROBE}({json.dumps(names)})",
                                            "returnByValue": True}, page=True)["result"]["value"]
    if (got["theme"], got["dark"], got["more"]) != (theme, scheme == "dark", more):
        raise BrowserError(f"asked for data-theme {theme}, {scheme}, more {more}; the page "
                           f"reports {got['theme']}, dark {got['dark']}, more {got['more']}")
    if got["undeclared"]:
        raise BrowserError(f"not declared in the page: {', '.join(got['undeclared'])}")
    shot = browser.call("Page.captureScreenshot", {"format": "png", "clip": {
        "x": 0, "y": 0, "width": COLUMNS * CELL, "height": height, "scale": 1}}, page=True)
    _, rows = pixels(base64.b64decode(shot["data"]))
    out, lo, hi = [], (CELL - INNER) // 2, (CELL + INNER) // 2
    for k in range(count):
        x, y = k % COLUMNS * CELL, k // COLUMNS * CELL
        ground = {rows[y + j][x + i] for j in range(CELL) for i in range(CELL)
                  if not (lo <= i < hi and lo <= j < hi)}
        ink = {rows[y + j][x + i] for j in range(lo, hi) for i in range(lo, hi)}
        if len(ground) != 1 or len(ink) != 1:
            raise BrowserError(f"cell {k} is not two flat colours: {sorted(ink)} on {sorted(ground)}")
        out.append((ink.pop(), ground.pop()))
    return out


def luminance(px):
    return contrast.luminance_rgb([v / 255 for v in px])


def certify(browser, tokens, work):
    """(failures, report lines) for one ramps file, in every route and tier."""
    pairs = []
    bad, _ = contrast.certify_ramps(tokens, pairs=pairs)
    fails = [f"contrast.py --ramps refuses it: {b}" for b in bad[:3]] if bad else []
    report = []
    for name, theme, scheme in ROUTES:
        tone = "dark" if "dark" in name else "light"
        for more in (False, True):
            tier = tone + ("-more" if more else "")
            todo = sorted({(fg, bg, bar, kind) for t, fg, bg, bar, kind in pairs if t == tier})
            if not todo:
                fails.append(f"{name}{' under more' if more else ''}: no pair certified for {tier}")
                continue
            names = sorted({n for fg, bg, _, _ in todo for n in (fg, bg)})
            got = paint(browser, page(tokens, [(fg, bg) for fg, bg, _, _ in todo]),
                        work / "page.html", theme, scheme, more, names, len(todo) + 1)
            where = f"{name}{', more' if more else ''}"
            control = contrast.ratio_lum(*map(luminance, got[0]))
            if got[0] != CONTROL[2:] or control >= contrast.AA:
                fails.append(f"{where}: the control painted {got[0][0]} on {got[0][1]} at "
                             f"{control:.3f}, not {CONTROL[2]} on {CONTROL[3]} under 4.5")
            low = {}
            for (fg, bg, bar, kind), (ink, ground) in zip(todo, got[1:]):
                if kind == "ratio":
                    v = contrast.ratio_lum(luminance(ink), luminance(ground))
                else:
                    v = contrast.de2000(*(contrast.lab_rgb([c / 255 for c in p]) for p in (ink, ground)))
                if v < bar:
                    fails.append(f"{where}: {fg} on {bg} paints {ink} on {ground}, "
                                 f"{v:.3f} {'CIEDE2000' if kind == 'de2000' else ':1'} below {bar}")
                if kind not in low or v - bar < low[kind][0] - low[kind][1]:
                    low[kind] = (v, bar, fg, bg)
            report.append(f"  {where}: {len(todo)} pairs; " + "; ".join(
                f"closest {k} {v:.3f} on a {b} bar ({f} on {g})" for k, (v, b, f, g) in low.items()))
    return fails, report


def find_browser(given):
    for c in ([given] if given else BROWSERS):
        found = c if os.path.isfile(c) else shutil.which(c)
        if found:
            return found
    return None


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tokens", nargs="*", type=Path,
                    help="tools/ramps.py files (default every ramps/tokens/*.tokens.css)")
    ap.add_argument("--browser", help="a Chromium executable (default Brave, then Chrome)")
    a = ap.parse_args(argv)
    paths = [p.resolve() for p in a.tokens] or sorted((ROOT / "ramps" / "tokens").glob("*.tokens.css"))
    path = find_browser(a.browser)
    if not path:
        print(f"FAIL  no browser: tried {', '.join([a.browser] if a.browser else BROWSERS)}",
              file=sys.stderr)
        return 1
    print(f"browser: {path}")
    failures = []
    with tempfile.TemporaryDirectory(prefix="hw-painted-") as tmp:
        work = Path(tmp)
        try:
            browser = Browser(path, work / "profile")
        except BrowserError as e:
            print(f"FAIL  {e}", file=sys.stderr)
            return 1
        try:
            print(browser.call("Browser.getVersion")["product"])
            for tokens in paths:
                if not tokens.is_file():
                    failures.append(f"{tokens} does not exist")
                    continue
                fails, report = certify(browser, tokens, work)
                failures += [f"{tokens.name.removesuffix('.tokens.css')}: {f}" for f in fails]
                print(f"painted {tokens.name}: {len(fails)} failed")
                print("\n".join(report))
        except BrowserError as e:
            failures.append(str(e))
        finally:
            browser.close()
    for f in failures:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
