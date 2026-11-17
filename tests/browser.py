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
  busy         a busy button under reduced motion draws no ring, and an ellipsis after its label
  disabled     a button disabled mid-hover paints its settled fill at once, not a fade
  tooltip      Escape hides a showing tooltip without moving focus or pointer, and it returns
  kbd          a keycap asks for weight 400, the one every product vendors
  rows         no child of a list row paints over another, and none leaves the row, at 300 and
               1440 wide: text first, meta first, an unbreakable address, and .hw-row--lead, whose
               leading column stays 5.5em; the grid the layer shipped before must be refused

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

<ul id="rows" class="hw-list" style="justify-self:stretch">
<li class="hw-row"><p>staging.atlas.dev</p><span class="hw-row-meta">2 days ago</span></li>
<li class="hw-row" aria-selected="true"><p>api-gateway-eu-west-1.staging.internal.example.com</p><span class="hw-row-meta">Failed</span><span class="hw-row-meta">14 Nov 2026</span><div class="hw-row-actions"><button class="hw-btn hw-btn--sm">Redeploy</button><button class="hw-btn hw-btn--sm">View log</button></div></li>
<li class="hw-row"><p>Quarterly report</p></li>
<li class="hw-row"><span class="hw-row-meta">INV-2041</span><p>Northwind Traders</p><span class="hw-row-meta">$1,240.00</span></li>
<li class="hw-row hw-row--lead" id="lead"><span class="hw-row-meta">12:30 pm</span><p>Moved the launch review to Thursday</p><span class="hw-row-meta">Mira Shah</span></li>
<li class="hw-row hw-row--lead" aria-selected="true"><span class="hw-row-meta">10:41 am</span><p>Renamed the project</p><span class="hw-row-meta">Sam Lee</span><div class="hw-row-actions"><button class="hw-btn hw-btn--sm">Undo</button></div></li>
</ul>
"""

# Each child's painted extent is its content's, not its grid area's: text that overflows its
# column paints past its box, which is the defect. A row's actions are measured as their box.
ROWS = """(() => {
  const ext = el => { if (el.classList.contains("hw-row-actions")) return el.getBoundingClientRect();
    const r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect(); };
  const hits = [];
  for (const row of document.querySelectorAll("#rows .hw-row")) {
    const kids = [...row.children], boxes = kids.map(ext), rb = row.getBoundingClientRect();
    const name = i => `${row.textContent.slice(0, 24)}: ${kids[i].textContent.slice(0, 18)}`;
    boxes.forEach((a, i) => {
      if (a.left < rb.left - 0.5 || a.right > rb.right + 0.5) hits.push(`${name(i)} leaves the row`);
      boxes.slice(i + 1).forEach((b, k) => {
        if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 0.5
            && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 0.5)
          hits.push(`${name(i)} over ${name(i + 1 + k).split(": ")[1]}`); }); });
  }
  const lead = document.getElementById("lead");
  return {rows: document.querySelectorAll("#rows .hw-row").length, hits,
          lead: parseFloat(getComputedStyle(lead).gridTemplateColumns) / parseFloat(getComputedStyle(lead).fontSize)};
})()"""

# The grid the layer shipped before this probe: 5.5em, 1fr, auto for every row.
BEFORE = """(() => { const s = document.createElement("style"); s.id = "before";
  s.textContent = "#rows .hw-row {grid-template-columns: 5.5em 1fr auto; grid-auto-flow: row}"
    + " #rows .hw-row > * {grid-row: auto; overflow-wrap: normal}"
    + " #rows .hw-row > .hw-row-actions {grid-column: 2 / -1}";
  document.head.append(s); return true; })()"""

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

BUSY = """(() => { const b = document.getElementById("busy");
  return {before: getComputedStyle(b, "::before").display, after: getComputedStyle(b, "::after").content}; })()"""

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

    def width(self, px):
        self.b.call("Emulation.setDeviceMetricsOverride", {
            "width": px, "height": 900, "deviceScaleFactor": 1, "mobile": False}, page=True)
        self.js("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))")

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
    check("busy", busy["before"] == "none" and busy["after"] == '"\u2026"',
          f"reduced motion: the ring's display {busy['before']}, after the label {busy['after']}")

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

    for width in (300, 1440):
        pg.width(width)
        r = pg.js(ROWS)
        check(f"rows {width}", r["rows"] == 6 and not r["hits"] and abs(r["lead"] - 5.5) < 0.01,
              f"{r['rows']} rows, overlaps: {r['hits'] or 'none'}, --lead first column {r['lead']:.2f}em")
    # Negative control: the grid before this probe, on the same rows, must be refused.
    pg.width(1440)
    pg.js(BEFORE)
    r = pg.js(ROWS)
    pg.js('document.getElementById("before").remove(); true')
    check("rows old", any("staging.atlas.dev" in h for h in r["hits"]),
          f"the 5.5em grid on a text-first row is refused: {r['hits'][:2] or 'NOT REFUSED'}")
    return fails, report


def silent_browser_is_reaped():
    """A browser that never answers raises, and is killed rather than left writing its profile."""
    with tempfile.TemporaryDirectory(prefix="hw-silent-") as tmp:
        fake = Path(tmp) / "browser"
        fake.write_text("#!/bin/sh\nexec sleep 60\n", encoding="utf-8")
        fake.chmod(0o755)
        spawned, real = [], painted.subprocess.Popen
        painted.subprocess.Popen = lambda *a, **k: spawned.append(real(*a, **k)) or spawned[-1]
        was, painted.TIMEOUT = painted.TIMEOUT, 1
        try:
            painted.Browser(str(fake), Path(tmp) / "profile")
            return "a browser that never answered was accepted"
        except painted.BrowserError:
            return None if spawned and spawned[0].poll() is not None else "the silent browser is still running"
        finally:
            painted.subprocess.Popen, painted.TIMEOUT = real, was
            for p in spawned:
                p.kill()


def main():
    problem = silent_browser_is_reaped()
    print(f"  silent:     {'ok   a browser that never answers is refused and reaped' if not problem else 'FAIL ' + problem}")
    if problem:
        print("FAIL  " + problem, file=sys.stderr)
        return 1
    path = painted.find_browser(os.environ.get("HW_BROWSER"))
    if not path:
        print(f"FAIL  no browser: tried {', '.join(painted.BROWSERS)}; set HW_BROWSER", file=sys.stderr)
        return 1
    fails = []
    with tempfile.TemporaryDirectory(prefix="hw-browser-", ignore_cleanup_errors=True) as tmp:
        work = Path(tmp)
        # One retry: a cold runner has left the first launch unanswered for 30s (run
        # 38796005141); a browser that is really broken fails the second launch the same way.
        for attempt in (1, 2):
            try:
                browser = painted.Browser(path, work / f"profile{attempt}")
                break
            except painted.BrowserError as e:
                if attempt == 2:
                    print(f"FAIL  {e}", file=sys.stderr)
                    return 1
                print(f"  browser:    launch {attempt} failed ({e}); retrying once")
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
