# Working on Halderworks Instrument

This file is for anyone changing the system: a person or an agent editing tokens, rules or tools.
An agent *using* the system to build a product screen reads [SKILL.md](SKILL.md) instead.

## Layout

| path | what it is |
|---|---|
| `design/` | the book: one Markdown file per subject, numbered in reading order. [design/05-coverage.md](design/05-coverage.md) is the inventory every other file answers to |
| `tokens/tokens.seed.json` | the source of every token value |
| `tokens/tokens.css`, `tokens/tokens.json` | generated from the seed by `tools/build.py`; never edited by hand |
| `exports/` | generated from `tokens/tokens.json` by `tools/export.py`; never edited by hand |
| `tools/` | six standard-library Python 3 scripts, no dependencies. Only `check-sources.py` uses the network |
| `.github/rulesets/`, `.github/settings/` | what this repository enforces on the forge, as files. Nothing applies them on its own; see "The settings that are not files" below |
| `scripts/apply-repo-settings.sh` | the one command that sends those files to GitHub |
| `docs/publication-record.md` | the one-off record of the first publication; not maintained |

## The tools, which are the checks

Python 3, no dependencies. Only `check-sources.py` uses the network.

```bash
python3 tools/build.py            # tokens/tokens.seed.json -> tokens.json + tokens.css
python3 tools/build.py --check    # emit nothing; fail if the committed files are stale
python3 tools/contrast.py         # re-derive every published ratio from the CSS, independently
python3 tools/export.py           # regenerate exports/ and refuse if it diverges from the CSS
python3 tools/check-coverage.py   # the inventory, its refusals, its manifest, and every link
python3 tools/test-check-sources.py  # the source classifier, against a local server
python3 tools/check-sources.py    # every cited source still resolves. THE ONE THAT LEAVES THE MACHINE
```

`check-sources.py` is the weekly job's and is not run per change; everything above it is. It
answers in three classes rather than two, and the middle one is the point: `ok` for 2xx/3xx,
`refusing` for 401/403/429 - a server answered, so the source exists and only access from a
data-centre address is gated - and `dead` for 404, 410, any other error status, or no response
at all. Only `dead` fails. What it treats as a citation in the first place is narrower than
every URL in the tree: a URL inside a fenced code block is an example the book prints, not a
source it stands behind, so a `preconnect` hint, a CDN base or an XML namespace is never
probed. `test-check-sources.py` holds both lines against a local `http.server` and a closed
port, so a merge cannot quietly widen or narrow either.

`build.py` and `contrast.py` are deliberately two instruments rather than one. The build solves
against the floors recorded in the seed; `contrast.py` knows nothing about the seed and re-derives
the ratios from the CSS a browser actually loads. A build that passes while a contrast run fails
means the seed is wrong, and that is a disagreement one instrument checking itself can never report.

Taking a different accent hue is a rebuild, never a hand-pick:

```bash
python3 tools/build.py --accent-hue 318 --out ./my-tokens
python3 tools/contrast.py ./my-tokens/tokens.css
```

At hue 318 three tokens re-solve and all 112 form-layer pairs still clear their bar. At hue 150 the
build refuses, because that hue sits 4.4 from `hw-success` against the 8.0 separation
[design/10-color.md](design/10-color.md) requires - which is what makes "a product cannot take hue
150" an executable rule rather than a sentence.

## Rules a change is held to

Read [design/95-extending.md](design/95-extending.md) first. In short:

- **Never redefine an `hw-` token.** A product extends in its own namespace, `--quoth-`, `--gates-`.
- **A new token needs four things**: a name in the scale it belongs to, a usage note saying where it
  may and may not be used, a number with a derivation, and its row in the verification.
- **Never hand-edit `tokens/tokens.css` or `tokens/tokens.json`.** Both are generated. Edit
  `tokens/tokens.seed.json` and rebuild.
- **A gap is a finding, not a blocker.** Ship the screen with the nearest house value and say in
  the same breath what you needed.

Run the per-change tools before opening a pull request; CI runs the same ones and a merge
depends on them. [`.github/workflows/consistency.yml`](.github/workflows/consistency.yml) is their single
definition, and both [`ci.yml`](.github/workflows/ci.yml) and
[`maintenance.yml`](.github/workflows/maintenance.yml) call that one file rather than carrying a
copy each.

A change to a rule file also keeps `tools/check-coverage.py` at 0 unbacked: a refusal written
anywhere in `design/` must resolve to a row in [design/05-coverage.md](design/05-coverage.md), and
the header counts must match the table.

A source the book cites is named, with what was taken from it and what was left.
[design/85-considered-and-declined.md](design/85-considered-and-declined.md) is where a screened and
refused source goes, with the reason and what would change the answer; a source the system's owner
supplies also gets its row in the ledger in [design/90-evidence.md](design/90-evidence.md#sources-the-owner-supplied-one-by-one).

## What a merge depends on

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every pull request, on Linux, with
no path filter. It has four jobs: the fleet's two shared scans from `Abhijeet34/gates`, the
`consistency` call described above, and a `checks` aggregate that `needs:` the other three and
refuses any result that is not `success`.

**`checks` is the only required status context**, named in
[`.github/rulesets/main.json`](.github/rulesets/main.json). Jobs can be added or renamed in
`ci.yml` without touching branch protection, which is the whole reason the aggregate exists. The
converse is the trap: a context required by the ruleset that no workflow publishes blocks every
pull request forever, so **`ci.yml` ships first and the ruleset follows only once the context has
been seen reporting on a real pull request**.

## The settings that are not files

`main` is protected by a ruleset, not by the older branch-protection API, and the ruleset lives in
the tree:

```bash
scripts/apply-repo-settings.sh Abhijeet34/halderworks-design
```

It sends `.github/rulesets/main.json` and the four files under `.github/settings/`, and it is
idempotent - a ruleset whose name already exists is updated in place, and the name is the join, so
renaming one in the file creates a second on the forge. It sends whatever is in the working tree,
so run it only from a tree whose settings files are the ones you intend.

Editing one of those files changes what this repository *says* it enforces. It changes what GitHub
*does* enforce only when somebody runs that command. Read the live state back afterwards:

```bash
gh api repos/Abhijeet34/halderworks-design/rulesets
gh api repos/Abhijeet34/halderworks-design/rules/branches/main
gh api repos/Abhijeet34/halderworks-design/branches/main --jq .protected
```

**Not `branches/main/protection`.** That is the older branch-protection API and it does not read
rulesets: with the ruleset live and all five rules enforcing, it still answers
`Branch not protected (HTTP 404)`, which reads exactly like an unprotected branch. `rules/branches/main`
lists the rules that actually apply, each with the ruleset id it came from.

Two more things measured rather than assumed, because both look like a broken setup otherwise:

- `gh-axi api` sends only `--field key=value` and has no flag for a JSON request body, so it cannot
  apply a ruleset. `scripts/apply-repo-settings.sh` uses `gh api --input` for that reason.
- GitHub fills `require_extra_approval_for_unattributed_changes: true` into the `pull_request` rule,
  a key `.github/rulesets/main.json` does not carry. A file that mirrored the response back could be
  refused by the endpoint that applies it, so the file stays as written and the live read carries
  one extra key.

## The weekly maintenance job

[`.github/workflows/maintenance.yml`](.github/workflows/maintenance.yml) runs every Monday and on
demand, on Linux, with no secrets beyond the repository's own token. **It opens an issue only when
something has actually moved**, so a quiet week is silent rather than noisy.

**What it checks.** The first six rows are the `consistency` call, which `ci.yml` makes on every
pull request as well; only the last row is the weekly job's own, because only a schedule can catch
a source that went away without anyone touching this repository. That is also why this workflow
has no `push` trigger: `ci.yml` already runs the consistency call on every push to `main`, and a
per-push network sweep is 26 outbound requests against a field that moves in months.

| check | how it fails |
|---|---|
| the token files still build from the seed | `build.py --check` finds a committed file the seed does not produce |
| every space and size value is on the 4px unit or declared | `build.py` finds an undeclared off-unit value, or a declared exception that has moved back onto the unit |
| every published contrast ratio still holds | `contrast.py` re-derives the matrix and finds a pair below bar or a token outside sRGB |
| every export still matches its source | `export.py` exits non-zero, or regenerates `exports/` and `git status --porcelain -- exports/` is no longer empty |
| the coverage inventory's claims | `check-coverage.py`: a row naming a missing file or section, a partial with no statement of what is missing, an exclusion with no reason, a refusal resolving to no row, a manifest with no lists or no date |
| every internal link and anchor | the same script, across every Markdown file in the repository |
| every cited external source still resolves | an HTTP request per distinct URL in the book, failing on 404, 410, any other error status, or no response. A 401, 403 or 429 is reported as alive-but-refusing and does not fail |

**What it does not check, stated plainly so nobody reads its green as more than it is:**

- **It does not re-screen the field.** It cannot tell you that a design system published something
  new, that a licence changed, that a source you cited now says something different, or that a
  taxonomy gained a row this inventory should carry. A link that still returns 200 is a live URL and
  nothing more.
- **It does not judge whether a value is still right.** It verifies that the numbers are internally
  consistent and that the claims about them are backed. Whether hue 198 is still the right accent,
  or 44px still the right row, is a measurement somebody has to take again.
- **It does not look at a rendered screen.** Nothing here rasterises anything, so a rule that is
  correct on paper and wrong in a browser passes.
- **The coverage cross-check is not re-run.** The manifest in
  [design/05-coverage.md](design/05-coverage.md) names the six external lists and the date they were
  enumerated. Re-running that audit is a deliberate act, and
  [design/85-considered-and-declined.md](design/85-considered-and-declined.md) names six further
  taxonomies that have never been checked at all.

**A field re-screen is a monthly job for a person**, and the green tick on this workflow is not
evidence one happened.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
