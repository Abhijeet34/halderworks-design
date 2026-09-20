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
| `tools/` | four standard-library Python 3 scripts, no dependencies and no network |
| `docs/publication-record.md` | the one-off record of the first publication; not maintained |

## The tools, which are the checks

Python 3, no dependencies, no network.

```bash
python3 tools/build.py            # tokens/tokens.seed.json -> tokens.json + tokens.css
python3 tools/build.py --check    # emit nothing; fail if the committed files are stale
python3 tools/contrast.py         # re-derive every published ratio from the CSS, independently
python3 tools/export.py           # regenerate exports/ and refuse if it diverges from the CSS
python3 tools/check-coverage.py   # the inventory, its refusals, its manifest, and every link
```

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

Run all four tools before opening a pull request; the workflow runs the same ones.

A change to a rule file also keeps `tools/check-coverage.py` at 0 unbacked: a refusal written
anywhere in `design/` must resolve to a row in [design/05-coverage.md](design/05-coverage.md), and
the header counts must match the table.

A source the book cites is named, with what was taken from it and what was left.
[design/85-considered-and-declined.md](design/85-considered-and-declined.md) is where a screened and
refused source goes, with the reason and what would change the answer; a source the system's owner
supplies also gets its row in the ledger in [design/90-evidence.md](design/90-evidence.md#sources-the-owner-supplied-one-by-one).

## The weekly maintenance job

[`.github/workflows/maintenance.yml`](.github/workflows/maintenance.yml) runs every Monday and on
demand, on Linux, with no secrets beyond the repository's own token. **It opens an issue only when
something has actually moved**, so a quiet week is silent rather than noisy.

**What it checks:**

| check | how it fails |
|---|---|
| the token files still build from the seed | `build.py --check` finds a committed file the seed does not produce |
| every space and size value is on the 4px unit or declared | `build.py` finds an undeclared off-unit value, or a declared exception that has moved back onto the unit |
| every published contrast ratio still holds | `contrast.py` re-derives the matrix and finds a pair below bar or a token outside sRGB |
| every export still matches its source | `export.py` regenerates `exports/` and the working tree is no longer clean |
| the coverage inventory's claims | `check-coverage.py`: a row naming a missing file or section, a partial with no statement of what is missing, an exclusion with no reason, a refusal resolving to no row, a manifest with no lists or no date |
| every internal link and anchor | the same script, across every Markdown file in the repository |
| every cited external source still resolves | an HTTP request per distinct URL in the book, failing on a status that is neither a success nor a redirect |

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
