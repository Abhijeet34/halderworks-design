#!/usr/bin/env python3
"""Prove check-sources.py puts each class of response on the right side of the line.

Four classes, one local server and one closed port: a 200 is ok, a 403 is alive-but-refusing
and does not fail the run, a 404 is dead and does, and a host that never answers is dead too.
No third-party host is contacted, so this is a check rather than a weather report.

It also holds the line before the classes: a URL inside a fenced code block is an example and
is never probed, while the same URL in prose is a citation and is. That is what stops a
`<link rel="preconnect">` hint to a host that 404s its own root from being reported as a dead
source, and the prose half is what stops the rule from being a way to check nothing.

    python3 tools/test-check-sources.py
"""
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

TOOL = Path(__file__).resolve().parent / "check-sources.py"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        code = {"/ok": 200, "/refused": 403, "/gone": 404}.get(self.path, 404)
        self.send_response(code)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def book(root: Path, urls: list[str], body: str = "") -> None:
    """The smallest tree check-sources.py reads: design/*.md, README.md, SKILL.md."""
    (root / "design").mkdir()
    (root / "design" / "10-fixture.md").write_text(
        "\n".join(f"- [a source]({u})" for u in urls) + "\n" + body, encoding="utf-8")
    (root / "README.md").write_text("# fixture\n", encoding="utf-8")
    (root / "SKILL.md").write_text("# fixture\n", encoding="utf-8")


def run(root: Path, summary: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(TOOL), str(root), "--summary", str(summary)],
                       capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout


def main() -> int:
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    live = f"http://127.0.0.1:{server.server_port}"
    dark = f"http://127.0.0.1:{free_port()}/never"

    failures = []

    def check(label: str, condition: bool, detail: str) -> None:
        print(f"{'PASS' if condition else 'FAIL'}  {label}")
        if not condition:
            failures.append(f"{label}: {detail}")

    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # A 200 and a 403 together: the run passes, and the 403 is named as alive, not dead.
        alive_root = tmp / "alive"
        alive_root.mkdir()
        book(alive_root, [f"{live}/ok", f"{live}/refused"])
        summary = tmp / "alive-summary.md"
        rc, out = run(alive_root, summary)
        text = summary.read_text(encoding="utf-8")
        check("200 is ok", f"ok   200  {live}/ok" in out, out)
        check("403 is alive, not dead",
              f"alive 403  {live}/refused  (refusing an unauthenticated request)" in out, out)
        check("403 does not fail the run", rc == 0, f"exit {rc}")
        check("403 is reported in the job summary",
              "Alive, but refusing an unauthenticated request" in text
              and f"`{live}/refused` answered `403`" in text, text)

        # A 404 is the host saying the source is gone, and it still fails loudly.
        gone_root = tmp / "gone"
        gone_root.mkdir()
        book(gone_root, [f"{live}/ok", f"{live}/gone"])
        rc, out = run(gone_root, tmp / "gone-summary.md")
        check("404 is dead", f"DEAD 404  {live}/gone  (returned 404)" in out, out)
        check("404 fails the run", rc == 1, f"exit {rc}")

        # A 404 inside a fenced block is an example, not a citation: not probed, and the run
        # passes. The same URL in prose in the same file is still probed, so the rule draws a
        # line rather than switching the check off.
        fenced_root = tmp / "fenced"
        fenced_root.mkdir()
        book(fenced_root, [f"{live}/ok"],
             f"""
```html
<link rel="preconnect" href="{live}/gone" crossorigin>
```

~~~
{live}/gone
~~~

Prose after the block still counts: [a source]({live}/refused).
""")
        rc, out = run(fenced_root, tmp / "fenced-summary.md")
        check("a URL inside a fenced block is not a citation",
              f"{live}/gone" not in out, out)
        check("fenced examples do not fail the run", rc == 0, f"exit {rc}")
        check("a prose citation in the same file is still checked",
              f"alive 403  {live}/refused" in out, out)

        # The closing fence has to be the one that closes: a ```js inside a block is content,
        # and dropping the rest of the file on it would silence every citation after it.
        nested_root = tmp / "nested"
        nested_root.mkdir()
        book(nested_root, [f"{live}/ok"],
             f"""
````markdown
```js
fetch("{live}/gone")
```
````

A citation after the block: [still read]({live}/refused)
""")
        rc, out = run(nested_root, tmp / "nested-summary.md")
        check("a fence inside a longer fence does not end the block",
              f"{live}/gone" not in out, out)
        check("citations after a nested fence are still read",
              f"alive 403  {live}/refused" in out, out)

        # Nothing listening: no status line at all, which is the unreachable case.
        dark_root = tmp / "dark"
        dark_root.mkdir()
        book(dark_root, [f"{live}/ok", dark])
        rc, out = run(dark_root, tmp / "dark-summary.md")
        check("an unreachable host is dead", f"DEAD ---  {dark}  (no response)" in out, out)
        check("an unreachable host fails the run", rc == 1, f"exit {rc}")

    server.shutdown()
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("every class classified correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
