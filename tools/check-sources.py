#!/usr/bin/env python3
"""Check that every source the book cites still exists.

The other five tools in this directory are offline and internally consistent; this one is the
only one that leaves the machine, which is why it runs on the weekly schedule rather than on
every change. A source rots in months, so 22 outbound requests per push buy no information.

What "exists" means is the whole substance of this check, and it is a three-way answer rather
than a two-way one:

  ok        2xx or 3xx after redirects. The source is there.
  refusing  401, 403 or 429. A SERVER ANSWERED, and answered with a refusal aimed at an
            unauthenticated request from a data-centre address. The source exists; what is
            gated is access from here. Reported, never failed.
  dead      404 or 410, any other error status, or no response at all. This is the finding the
            job exists to produce.

The middle row is the one that was missing and it cost the job its credibility: `pageflows.com`
answers 403 to an unauthenticated request, the check called it DEAD, and a maintenance job that
sits red is one people stop reading. A blanket 4xx skip would have bought the same green by
giving up the check, so the split is by what the code actually proves: a status line is
evidence the host is alive, 404 and 410 are that same host stating the source is gone.

What counts as a citation at all is settled before any of that, and it is the narrower
question: a URL inside a fenced code block is part of an example the book prints, not a source
the book stands behind. `<link rel="preconnect" href="https://fonts.gstatic.com">` is a
connection hint to a host that serves font files at paths and answers 404 on its root by
design, and `http://www.w3.org/2000/svg` is an XML namespace identifier that was never meant to
be fetched. Both were reported dead every week. The fence is the line because it is the line
the book already draws between what it says and what it shows, and because it holds for the
next CDN base, example endpoint or namespace without anyone adding a name to a list.

    python3 tools/check-sources.py [repo-root] [--report PATH] [--summary PATH]

Exits 1 when any source is dead, 0 otherwise.
"""
import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Three kinds of citation, because the book cites more by name than by link: a full URL, a bare
# host or path in backticks, and an npm package at a pinned version.
SOURCES = ["design/*.md", "README.md", "SKILL.md"]
# A backticked dotted token is a host only if its last label is not a file extension.
NOT_TLD = {"md", "py", "css", "json", "js", "yml", "yaml", "txt", "html", "svg",
           "png", "jpg", "sh", "toml", "lock", "xml"}
URL = re.compile(r"https?://[A-Za-z0-9._~:/?#@!$&*+,;=%()-]+")
DOM = re.compile(r"`([a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)+"
                 r"(?:/[A-Za-z0-9._~/?#@!$&*+,;=%()-]*)?)`")
NPM = re.compile(r"`(@?[a-z0-9][a-z0-9._/-]*)@(\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)`")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")

# Sources the book itself records as unreachable, each with the entry that says so, and account
# handles that only look like hosts. Checking them would report the finding the book already
# carries, or a host that was never cited, every week.
SKIP = {
    "https://eightshapes.com",
    "https://figma.expert",
    # design/00-brand-book.md, "The mark": the domain is registered and its mail resolves,
    # and no web host answers the apex yet. The book says so where it names it.
    "https://halderworks.com",
    "https://height.app",
    "https://refero.design/web",
    "https://ui.ux.jam",
}

REFUSING = {401, 403, 429}
GONE = {404, 410}
AGENT = "halderworks-design maintenance (+github actions)"
TIMEOUT = 25
ATTEMPTS = 3


def prose(text: str) -> str:
    """The file with its fenced code blocks removed, so an example is not read as a citation."""
    out: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        m = FENCE.match(line)
        run = m.group(1) if m else None
        if fence is None:
            if run:
                fence = (run[0], len(run))
            else:
                out.append(line)
        elif run and run[0] == fence[0] and len(run) >= fence[1] and not line.strip(f" \t{run[0]}"):
            # CommonMark: a closing fence is the same character, at least as long, and alone
            # on its line. Anything else inside the block is content, including ```js.
            fence = None
    return "\n".join(out)


def extract(root: Path) -> list[str]:
    """Every distinct source cited anywhere in the book, as a URL.

    Fenced code is dropped first: what the book shows is not what the book cites.
    """
    files: list[Path] = []
    for pattern in SOURCES:
        files.extend(sorted(root.glob(pattern)))
    out: set[str] = set()
    for f in files:
        text = prose(f.read_text(encoding="utf-8"))
        for m in URL.findall(text):
            out.add(m.rstrip(".,;:)]"))
        for m in DOM.findall(text):
            tld = m.split("/")[0].rsplit(".", 1)[-1]
            if tld not in NOT_TLD and len(tld) >= 2 and not tld.isdigit():
                out.add("https://" + m)
        for name, version in NPM.findall(text):
            out.add(f"https://registry.npmjs.org/{name}/{version}")
    return sorted(out)


def probe(url: str) -> int | None:
    """The final status code, or None when nothing answered at all."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    last = None
    for attempt in range(ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status
        except urllib.error.HTTPError as e:
            # A status line is an answer, so it is the result and not something to retry:
            # a host that refuses an unauthenticated request refuses it three times.
            return e.code
        except Exception as e:  # URLError, socket timeout, a malformed redirect target
            last = e
    print(f"     {type(last).__name__}: {last}", file=sys.stderr)
    return None


def classify(code: int | None) -> str:
    if code is None:
        return "dead"
    if 200 <= code < 400:
        return "ok"
    if code in REFUSING:
        return "refusing"
    return "dead"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=".", type=Path)
    ap.add_argument("--report", type=Path,
                    help="write the dead sources as Markdown here; empty file when none")
    ap.add_argument("--summary", type=Path,
                    help="append a Markdown summary of every class here")
    args = ap.parse_args()

    dead: list[tuple[str, str]] = []
    refusing: list[tuple[str, int]] = []
    checked = 0
    for url in extract(args.root):
        if url in SKIP:
            print(f"skip      {url}  (recorded unreachable, or an account handle)")
            continue
        checked += 1
        code = probe(url)
        shown = "---" if code is None else str(code)
        verdict = classify(code)
        if verdict == "ok":
            print(f"ok   {shown}  {url}")
        elif verdict == "refusing":
            print(f"alive {shown}  {url}  (refusing an unauthenticated request)")
            refusing.append((url, code))
        else:
            reason = "no response" if code is None else f"returned {shown}"
            print(f"DEAD {shown}  {url}  ({reason})")
            dead.append((url, reason))
    print(f"{checked} sources checked, {len(dead)} dead, {len(refusing)} alive but refusing")

    report = ""
    if dead:
        report = "### A cited source no longer resolves\n\n"
        report += "".join(f"- `{url}` {reason}\n" for url, reason in dead)
        report += (
            "\nA dead link is not automatically a wrong claim: the source may have\n"
            "moved, and a package version may simply have been unpublished. Find where\n"
            "it went and update the citation, or record in\n"
            "`design/85-considered-and-declined.md` that it is now unreachable.\n\n")
    if args.report:
        args.report.write_text(report, encoding="utf-8")

    if args.summary:
        summary = report
        if refusing:
            # Said out loud rather than passed silently: a reader of a green run should see
            # which sources were only proved to exist, not proved to be readable from here.
            summary += "### Alive, but refusing an unauthenticated request\n\n"
            summary += "".join(f"- `{url}` answered `{code}`\n" for url, code in refusing)
            summary += ("\nThe server answered, so the source exists. Access from a\n"
                        "data-centre address is what is gated. This is not a dead link.\n\n")
        summary += f"{checked} sources checked, {len(dead)} dead, {len(refusing)} refusing.\n"
        with args.summary.open("a", encoding="utf-8") as fh:
            fh.write(summary)

    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
