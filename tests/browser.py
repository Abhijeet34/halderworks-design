#!/usr/bin/env python3
"""The component layer in a browser: the probes the 2026-10-15 adoption trial ran by hand.

tests/components.py reads components.css as text. These are the defects only a rendered page
shows, each probed on a page that loads exactly what a product loads (exports/variables.css,
fonts/fonts.css, components/components.css, components/radiogroup.js) and nothing of a sheet's:

  hidden       a component given the hidden attribute is display: none
  switch       a disabled, checked switch's track differs from an enabled one's
  pin          "128" fits its pin with the pin's own side padding to spare
  kv           a key-value list in its 300px .hw-kv-wrap stacks, and in a tall box keeps its pitch
  segmented    a segmented control in a 660px grid cell is as wide as its segments
  avatars      no covered avatar in a group loses an initial under the next one, at every size
  busy         a busy button under reduced motion draws no ring
  disabled     a button disabled mid-hover paints its settled fill at once, not a fade
  tooltip      Escape hides a showing tooltip without moving focus or pointer, and it returns
  kbd          a keycap asks for weight 400, the one every product vendors

Each probe runs in light and dark. It needs a Chromium, found as tools/painted.py finds one
(Brave first; HW_BROWSER names another), and fails rather than skips when there is none.

    python3 tests/browser.py
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import painted  # noqa: E402  its CDP pipe driver and browser search, not a copy of them

LOADS = [ROOT / "exports" / "variables.css", ROOT / "fonts" / "fonts.css",
         ROOT / "components" / "components.css"]
SCRIPT = ROOT / "components" / "radiogroup.js"

BODY = """
<button id="hidden-btn" class="hw-btn" hidden>I should be hidden</button>
<div id="hidden-seg" class="hw-segmented" hidden></div>

<label class="hw-switch">On <input id="sw-on" type="checkbox" role="switch" checked></label>
<label class="hw-switch">On, disabled <input id="sw-off" type="checkbox" role="switch" checked disabled></label>

<span id="pin" class="hw-pin">128</span>

<div style="display:grid;width:660px;height:400px"><div id="kv-wrap" class="hw-kv-wrap" style="width:300px"><dl id="kv" class="hw-kv"><dt>Model</dt><dd>Base (English), 148 MB</dd><dt>Runs on</dt><dd>This Mac</dd></dl></div></div>
<div style="display:grid;width:660px;height:400px"><dl id="kv-tall" class="hw-kv"><dt>Model</dt><dd>Base</dd><dt>Runs on</dt><dd>This Mac</dd></dl></div>

<div style="display:grid;width:660px"><div id="seg" class="hw-segmented" role="radiogroup" aria-label="Size"><button type="button" role="radio" aria-checked="true">S</button><button type="button" role="radio" aria-checked="false">M</button><button type="button" role="radio" aria-checked="false">L</button></div></div>

<span class="hw-avatar-group av"><span class="hw-avatar hw-avatar--sm">MS</span><span class="hw-avatar hw-avatar--sm">MW</span><span class="hw-avatar hw-avatar--sm">WM</span></span>
<span class="hw-avatar-group av"><span class="hw-avatar">MS</span><span class="hw-avatar">MW</span><span class="hw-avatar">WM</span></span>
<span class="hw-avatar-group av"><span class="hw-avatar hw-avatar--lg">MS</span><span class="hw-avatar hw-avatar--lg">MW</span><span class="hw-avatar hw-avatar--lg">WM</span></span>

<button id="busy" class="hw-btn" aria-busy="true">Checking DOIs</button>
<button id="fade" class="hw-btn hw-btn--primary">Send</button>
<button id="settled" class="hw-btn hw-btn--primary" disabled>Send</button>

<p style="margin-top:80px"><span class="hw-tip"><button id="tip-btn" class="hw-btn hw-btn--icon" aria-label="Copy">C</button><span id="tip" class="hw-tooltip" aria-hidden="true">Copy</span></span>
<button id="after-tip" class="hw-btn">Next</button></p>

<kbd id="kbd" class="hw-kbd">K</kbd>
"""

PROBES = """({
  hidden: [getComputedStyle(document.getElementById("hidden-btn")).display,
           getComputedStyle(document.getElementById("hidden-seg")).display],
  switch: [getComputedStyle(document.getElementById("sw-on")).backgroundColor,
           getComputedStyle(document.getElementById("sw-off")).backgroundColor],
  pin: (() => { const p = document.getElementById("pin"), r = document.createRange();
    r.selectNodeContents(p);
    return {scroll: p.scrollWidth, client: p.clientWidth, text: r.getBoundingClientRect().width,
            pad: parseFloat(getComputedStyle(p).paddingLeft), width: p.getBoundingClientRect().width}; })(),
  kv: getComputedStyle(document.getElementById("kv")).gridTemplateColumns,
  kvTall: (() => { const dts = document.querySelectorAll("#kv-tall dt");
    return {pitch: dts[1].getBoundingClientRect().top - dts[0].getBoundingClientRect().top,
            line: (r => (r.selectNodeContents(dts[0]), r.getBoundingClientRect().height))(document.createRange()),
            gap: parseFloat(getComputedStyle(document.getElementById("kv-tall")).rowGap)}; })(),
  seg: (() => { const s = document.getElementById("seg"), b = s.querySelectorAll("button"),
    cs = getComputedStyle(s);
    return {width: s.getBoundingClientRect().width,
            content: b[b.length - 1].getBoundingClientRect().right - b[0].getBoundingClientRect().left
                     + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight)}; })(),
  avatars: [...document.querySelectorAll(".av")].flatMap(g => {
    const a = [...g.children];
    return a.slice(0, -1).map((el, i) => { const r = document.createRange(); r.selectNodeContents(el);
      return {text: el.textContent, size: el.getBoundingClientRect().width,
              right: r.getBoundingClientRect().right,
              cover: a[i + 1].getBoundingClientRect().left - 2}; }); }),
  kbd: getComputedStyle(document.getElementById("kbd")).fontWeight,
})"""

FADE = """(() => { const b = document.getElementById("fade"); getComputedStyle(b).backgroundColor;
  b.disabled = true;
  return [getComputedStyle(b).backgroundColor,
          getComputedStyle(document.getElementById("settled")).backgroundColor]; })()"""

BUSY = """(() => { const s = getComputedStyle(document.getElementById("busy"), "::before");
  return {border: s.borderTopWidth, image: s.backgroundImage}; })()"""

TIP = 'getComputedStyle(document.getElementById("tip")).visibility'
FOCUSED = "document.activeElement && document.activeElement.id"


def page(theme):
    links = "".join(f'<link rel="stylesheet" href="{p.as_uri()}">' for p in LOADS)
    return (f'<!doctype html><html lang="en" data-theme="{theme}"><head><meta charset="utf-8">'
            f'{links}<script src="{SCRIPT.as_uri()}" defer></script></head>'
            f'<body style="background:var(--hw-surface);color:var(--hw-text);font-family:var(--hw-font-sans);'
            f'display:grid;gap:16px;justify-items:start;padding:24px">{BODY}</body></html>')


class Page:
    def __init__(self, browser):
        self.b = browser

    def js(self, expr):
        r = self.b.call("Runtime.evaluate", {"expression": expr, "returnByValue": True,
                                             "awaitPromise": True}, page=True)
        if "exceptionDetails" in r:
            raise painted.BrowserError(r["exceptionDetails"].get("text", "script error"))
        return r["result"].get("value")

    def key(self, key, code):
        for kind in ("keyDown", "keyUp"):
            self.b.call("Input.dispatchKeyEvent", {"type": kind, "key": key, "code": key,
                                                   "windowsVirtualKeyCode": code}, page=True)

    def mouse(self, x, y):
        self.b.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y}, page=True)

    def media(self, motion):
        self.b.call("Emulation.setEmulatedMedia", {"features": [
            {"name": "prefers-reduced-motion", "value": motion}]}, page=True)

    def open(self, path):
        self.b.events.clear()
        self.b.call("Page.navigate", {"url": path.as_uri()}, page=True)
        self.b.wait("Page.loadEventFired")
        self.js("document.fonts.ready.then(() => true)")


def settle(seconds=0.9):
    """Past the tooltip's 500ms delay and its 120ms fade, with room for a slow runner."""
    time.sleep(seconds)


def probe(pg, theme):
    fails, report = [], []
    got = pg.js(PROBES)

    def check(name, ok, detail):
        report.append(f"  {theme:5} {name:10} {'ok  ' if ok else 'FAIL'} {detail}")
        if not ok:
            fails.append(f"{theme}: {name}: {detail}")

    check("hidden", got["hidden"] == ["none", "none"],
          f"display of a hidden .hw-btn and .hw-segmented: {got['hidden']}")
    on, off = got["switch"]
    check("switch", on != off, f"enabled-on track {on}, disabled-on track {off}")
    p = got["pin"]
    check("pin", p["scroll"] <= p["client"] and p["text"] + 2 * p["pad"] <= p["width"] + 0.5 and p["pad"] > 0,
          f'"128" {p["text"]:.1f}px wide with {p["pad"]:.0f}px padding each side in a {p["width"]:.1f}px pin, '
          f'scrollWidth {p["scroll"]} clientWidth {p["client"]}')
    check("kv", len(got["kv"].split()) == 1, f"grid-template-columns in a 300px wrap: {got['kv']}")
    k = got["kvTall"]
    natural = 2 * k["line"] + 2 * k["gap"]
    check("kv-tall", k["pitch"] <= natural + 0.5,
          f"row pitch {k['pitch']:.1f}px in a 400px box, natural at most {natural:.1f}px")
    s = got["seg"]
    check("segmented", abs(s["width"] - s["content"]) <= 0.5,
          f"{s['width']:.1f}px wide in a 660px cell for {s['content']:.1f}px of segments")
    clipped = [f"{a['text']} at {a['size']:.0f}px ({a['right']:.1f} > {a['cover']:.1f})"
               for a in got["avatars"] if a["right"] > a["cover"] + 0.5]
    check("avatars", not clipped and len(got["avatars"]) == 6,
          f"{len(got['avatars'])} covered avatars at three sizes, clipped: {clipped or 'none'}")
    check("kbd", got["kbd"] == "400", f"font-weight {got['kbd']}")

    now, settled = pg.js(FADE)
    check("disabled", now == settled, f"background the frame it is disabled {now}, settled {settled}")

    pg.media("reduce")
    busy = pg.js(BUSY)
    pg.media("no-preference")
    check("busy", busy["border"] == "0px" and "gradient" in busy["image"],
          f"reduced motion: ::before border {busy['border']}, image {busy['image'][:40]}")

    # Keyboard: Tab onto the control, wait for the tip, Escape, and the focus has not moved.
    pg.js('document.getElementById("busy").focus(); true')
    while pg.js(FOCUSED) != "tip-btn":
        pg.key("Tab", 9)
        if pg.js(FOCUSED) in (None, "", "after-tip"):
            break
    settle()
    before = pg.js(TIP)
    pg.key("Escape", 27)
    settle(0.4)
    after, focus = pg.js(TIP), pg.js(FOCUSED)
    pg.key("Tab", 9)
    pg.js('document.getElementById("tip-btn").focus(); true')
    settle()
    back = pg.js(TIP)
    check("tip-keys", (before, after, focus, back) == ("visible", "hidden", "tip-btn", "visible"),
          f"focused {before}, after Escape {after} with focus on {focus}, after leaving and returning {back}")

    # Pointer: hover, Escape, the pointer stays put and the tip stays hidden until it leaves.
    pg.js("document.activeElement.blur(); true")
    box = pg.js('(r => [r.x + r.width / 2, r.y + r.height / 2])(document.getElementById("tip-btn").getBoundingClientRect())')
    pg.mouse(*box)
    settle()
    before = pg.js(TIP)
    pg.key("Escape", 27)
    settle(0.4)
    after = pg.js(TIP)
    pg.mouse(1, 1)
    pg.mouse(*box)
    settle()
    back = pg.js(TIP)
    pg.mouse(1, 1)
    check("tip-hover", (before, after, back) == ("visible", "hidden", "visible"),
          f"hovered {before}, after Escape {after}, after leaving and returning {back}")
    return fails, report


def main():
    path = painted.find_browser(os.environ.get("HW_BROWSER"))
    if not path:
        print(f"FAIL  no browser: tried {', '.join(painted.BROWSERS)}; set HW_BROWSER", file=sys.stderr)
        return 1
    fails = []
    with tempfile.TemporaryDirectory(prefix="hw-browser-") as tmp:
        work = Path(tmp)
        try:
            browser = painted.Browser(path, work / "profile")
        except painted.BrowserError as e:
            print(f"FAIL  {e}", file=sys.stderr)
            return 1
        try:
            print(f"  browser:    {browser.call('Browser.getVersion')['product']}")
            pg = Page(browser)
            browser.call("Emulation.setFocusEmulationEnabled", {"enabled": True}, page=True)
            browser.call("Emulation.setDeviceMetricsOverride", {
                "width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False}, page=True)
            for theme in ("light", "dark"):
                html = work / f"{theme}.html"
                html.write_text(page(theme), encoding="utf-8")
                pg.open(html)
                got, report = probe(pg, theme)
                fails += got
                print("\n".join(report))
        except painted.BrowserError as e:
            fails.append(str(e))
        finally:
            browser.close()
    for f in fails:
        print("FAIL  " + f, file=sys.stderr)
    print(f"\n{len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
