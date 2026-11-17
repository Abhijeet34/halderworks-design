# Verification of PR 49 at ae279b20

PR: https://github.com/Abhijeet34/halderworks-design/pull/49, `fix(components): .hw-row columns follow its children, with an --lead opt-in; neutral demo content`.
Head `ae279b205dc9019abc5e78fa4b3b2d09abbd550e`. Base and merge base `2fd14a03581a4bae80b75c1d28c8a427b64dae5d` (origin/main). That is the same commit, so the PR is not behind main.
Browser: `/usr/bin/google-chrome` (Chrome/153.0.8010.12) for `tests/browser.py`, and Playwright's bundled Chromium for the attack harness.
Base and head were each checked out as a separate git worktree. Every raw log is in this directory.

## 1. Red then green

The PR adds one test: the `rows` probe in `tests/browser.py`. It runs `rows 300`, `rows 1440`, `rows 180` and `rows old`, each in light and dark.

| tree | command | result |
|---|---|---|
| base + head's `tests/browser.py` | `python3 tests/browser.py` | **exit 1, 6 failures**. All six are `rows` checks: `rows 300`, `rows 1440` and `rows 180`, in both themes. Every other probe is ok. |
| head | `python3 tests/browser.py` | **exit 0, 0 failures** |

On base, the failures are for the reason the PR gives:
- `staging.atlas.dev over 2 days ago`: text in a text-first row runs into its meta.
- `api-gateway-eu-west-1… over Failed`.
- At 180px, `narrowest text 0px of a 156px line`.

`rows old` passes on both trees. That is correct: it is the negative control, and it requires main's grid to be refused.

Logs: `red-base.txt`, `green-head.txt`.

## 2. Full entry points on head

Every per-change command in AGENTS.md was run one at a time in the foreground with `bash data/verify-49/suite.sh`. `check-sources.py` was skipped because it is the weekly network job, and `painted.py` because it is a local release check that needs Brave. The PR changes no token or source, so neither of those two is affected.

| command | head |
|---|---|
| `python3 tools/ramps.py --check` | exit 0 |
| `python3 tools/contrast.py` | exit 0, 0 failures |
| `python3 tools/export.py` | exit 0, 0 divergent, 0 failures |
| `python3 tools/export.py examples/papertrace` / `quoth` / `pointback` | exit 0 each, 0 failures |
| `python3 tools/distinct.py` | exit 0, 6 pairs, 0 indistinguishable |
| `python3 tools/faces.py --vendored` | exit 0, 0 failed |
| `python3 tools/components.py --check` | exit 0, 42 components in 9 groups; 10 generated files; 18 renders, current |
| `python3 tools/check-links.py` | exit 0, 149 checked, 0 unresolved |
| `python3 tools/test-check-sources.py` | exit 0, every class classified correctly |
| `python3 tests/invariants.py` | exit 0, 0 failures |
| `python3 tests/mutation_tests.py` | exit 0, 23 cases: 23 as expected, 0 improved, 0 failed |
| `python3 tests/ramps.py` | exit 0, 0 failures |
| `python3 tests/exports.py` | exit 0, 0 failures |
| `python3 tests/components.py` | exit 0, 0 failures |
| `python3 tests/browser.py` | exit 0, 0 failures |
| `python3 tests/token_diff.py` | exit 0, PASS |
| `git status --porcelain` after all of the above | empty |

`git diff --stat origin/main pr49 -- exports examples ramps fonts` is empty, so the token files are byte-identical. `grep -ciE 'quoth|papertrace|pointback' components/catalogue.py` on head returns 0. Both match the PR body. Log: `suite-head.txt`.

I also viewed `components/renders/data-light.webp` from head. It shows the new neutral list rows ("staging.atlas.dev", "Mira Shah invited Sam Lee") and the new invoice table, so the re-taken renders do picture the new sheets.

## 3. Attack

The harness is `attack.js`, run as `node attack.js <tree>`. It loads that tree's `exports/variables.css`, `fonts/fonts.css` and `components/components.css` from a `file://` page. Each case runs in a 180px list (inside a 300px viewport), at 300 wide and at 1440 wide. For every child it measures the painted extent: the text range, or the box for actions, nested rows and children with an explicit width. It reports any overlap between two children and any child that leaves its row.

Logs: `attack-head.txt`, `attack-base.txt`.

| input | expected from the PR's claim | head | base, for comparison |
|---|---|---|---|
| **zero children**, `<li class="hw-row"></li>` | still a row: min-height 44px, nothing breaks | flex, h=44 at every width, no hits | grid, h=44 |
| **one child**, text only | text takes the whole free line | text 156 / 228 / 1368px, which is the full content width; no hits | text forced into the 5.5em (83px) column |
| **one child**, meta only | meta as wide as its content | 55px, no hits | 83px |
| **twelve children**, text + 11 metas | metas wrap below the text and never overlap it | 5 / 5 / 2 lines, **0 overlaps** at 180, 300 and 1440 | overlaps at every width (`0 over 1` and others) |
| **twelve children**, 12 metas | wrap with no overlap | 4 / 3 / 1 lines, **0 overlaps** | 4 overlaps at 180 |
| **twelve children**, `--lead` | "main's grid, unchanged" | same widths and the same 4 overlaps at 180 as base; none at 300 or 1440 | same as head |
| **nested** `.hw-row` inside `.hw-row` | the inner row is a text-like child: it takes the line and lays out its own children | inner row takes the full line, **no hits** at any width | inner children leave the inner row at 180 and 300 |
| **nested** `.hw-row` inside `.hw-row--lead` | the outer grid is unchanged, the inner row is the new flex | no hits at any width. At 180 the row is 382px tall, because the inner row is squeezed into the 1fr track of about 24px and wraps hard. | inner child leaves the inner row at 180 and 300 |
| **child sets its own width**: text `<p style="width:120px">`, or the same width from a class | not stated by the PR. Ordinary CSS would honour the width. | **the width is ignored**: the text measures 156, 160 and 1300px, not 120. No hits. | 120px is honoured, but the text overlaps its meta at every width |
| **child sets its own width**: meta at 200px | not stated | honoured at 300 and 1440. At 180 it shrinks to 156 and stays inside the row. | honoured, but leaves the row at 180 and 300 |
| **child sets its own width**: meta at 400px | not stated | shrinks to fit (156 / 228), honoured at 1440, never leaves the row | leaves the row at 180 and 300 |

The PR's claim holds for zero, one and twelve children, and for nested rows. The `--lead` overlap in a narrow card is pre-existing, and the PR discloses it as a finding left for a later row.

## 4. Neighbours, base vs head

The PR touches `components/components.css`, `components/catalogue.py`, the generated sheets and `design/64-component-sheets.md`, the renders and their manifest, and `tests/browser.py`. The checks that cover those are `components.py --check`, `tests/components.py`, `tests/browser.py` and `check-links.py`. The full suite was run on base too (`suite-base.txt`).

**Every command passes on base and on head**, with the same summary lines. Head's only extra checks are the new `rows` checks, and they pass. No failure is new on head, and none was pre-existing either.

## 5. What the diff does that the body does not say

1. **A text child's own `width` is now ignored.** The rule `.hw-row:not(.hw-row--lead) > :not(.hw-row-meta, .hw-row-actions) { flex: 1 1 10em }` sets a non-auto `flex-basis`, and a non-auto `flex-basis` takes precedence over `width`. A consumer that sized a text child with `width` now gets 10em grown to fill the line. Only a `flex` or `flex-basis` override restores it. The body says "the text takes the free space at a 10em basis", but it does not warn consumers about this. It also does not affect `--lead` rows. Not a defect in the stated goal, but a migration note is missing.
2. **`overflow-wrap: anywhere` applies to every child of a default row**, not only to the text. That includes the metas and the actions container, and it is inherited by the buttons. The body describes breaking only for "text that can't wrap (a long hostname)". Nothing broke mid-word in any attack case, but a long meta or button label in a narrow card could now break inside a word.
3. **Two vendored icons are orphaned.** The new demo content drops every use of `mic-off` (4 uses on base, 0 on head) and `quote` (2 on base, 0 on head). `components/icons/mic-off.svg` and `quote.svg` are still in the tree, and AGENTS.md describes that directory as "the Lucide icons the sheets use". No check refuses an unused icon, so this passes CI silently.
4. **Changes the body does mention, confirmed:**
   - `.hw-row-actions` gains `flex-basis: 100%` ("actions sit on a line of their own").
   - The "Used by" field moves from product names to counts ("one product", "two products").
   - The Anatomy text of the list row in the catalogue is rewritten.
   - Every sheet and all 18 renders are regenerated.

   `--lead` is pixel-equivalent to main's grid by construction: under `display: grid`, the added `flex` and `flex-basis` properties do not apply, and the `:not(.hw-row--lead)` rules do not match. My `twelve_lead` case measured identical widths and hits on base and head.
5. **This is a breaking change for consumers.** Any existing `.hw-row` that opens with a time loses its fixed 5.5em column until it adds `hw-row--lead`. Any row setting `--_cols` also stops working without `--lead`. The body states both, and names quoth and pointback. Neither consumer repo is edited, so the release notes have to carry it.

Verdict: PASS - the new rows probe fails on base for the stated overlap and passes on head, every per-change check passes on head with no regression against base, and zero, one, twelve and nested children behave as claimed; the --lead narrow-card overlap is pre-existing and disclosed, and the unmentioned items (a text child's own width ignored, overflow-wrap on every child, orphaned mic-off/quote icons) are non-blocking notes.
