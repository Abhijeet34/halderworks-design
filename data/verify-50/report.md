# Verification of PR #50, "feat(ramps): the working accent", at afa89a8a

Base: `origin/main` 2fd14a0, the merge base. Head: afa89a8a, two commits: dd3bee4 adds the tests only, and afa89a8 is the feature.
Each was checked out in its own worktree. Every suite ran in the foreground, one suite per command, without `tests/run.py`.

## 1. Red, then green

| run | command | result |
|---|---|---|
| red: dd3bee4's `tests/` on top of base's tools | `python3 tests/ramps.py` | rc=1, 4 failures. meadow, spotify and ember each "printed no shift for an accent beside a state". contrast.py refuses `--hw-accent-fill` against a state fill: meadow 1.2, spotify 3.0/3.3, ember 3.2/3.4 CIEDE2000, bar 5. This is the reason the PR states. |
| red: head's `tests/` on top of base's tools | `python3 tests/invariants.py`, `python3 tests/ramps.py` | rc=1 for both, with an AttributeError: base `ramps` has no `de2000` or `FILL_FROM_STATE`. This is expected, because these tests check new API. |
| green: head | `python3 tests/ramps.py` | rc=0, 0 failures. The three test brands are certified, and the 7 hostile cases pass. |
| green: head | `python3 tests/invariants.py` | rc=0. "contrast.de2000 and ramps.de2000 each reproduce 6 Sharma pairs both ways". |

The PR body names the red commit as `a93de3a`. The commit on the branch is `dd3bee4`. The content matches, so the branch was probably rewritten after the body was written.

## 2. Full check entry points on head (AGENTS.md), with base for comparison

All of these ran on both base and head, and both gave the same results:

- `python3 tools/ramps.py --check`: rc=0. No `shift` lines for house, papertrace, pointback or quoth.
- `python3 tools/contrast.py`: rc=0
- `python3 tools/export.py`, plus `python3 tools/export.py examples/{papertrace,pointback,quoth}`: rc=0 each, and `git status --porcelain` is empty afterwards. Nothing generated drifted.
- `python3 tools/distinct.py`: rc=0
- `python3 tools/faces.py --vendored`: rc=0
- `python3 tools/components.py --check`: rc=0
- `python3 tools/check-links.py`: rc=0, "152 internal links and anchors checked, 0 unresolved"
- `python3 tools/test-check-sources.py`: rc=0
- `python3 tools/painted.py --browser <chromium wrapper adding --no-sandbox>`: rc=0, 0 failures
- `python3 tests/invariants.py`: rc=0
- `python3 tests/mutation_tests.py`: rc=0, "23 cases: 23 as expected, 0 improved, 0 failed"
- `python3 tests/ramps.py`: rc=0
- `python3 tests/ramps.py --sweeps`:
  - base: rc=0, "27 of 72 accent hues refused".
  - head: rc=0, "72 of 72 accent hues build and are certified, 28 with a working accent". The 28 are 0–85, 130–175. Both runs show "468 accent builds over 360 hues".
- `python3 tests/exports.py`, `tests/components.py`, `tests/token_diff.py`: rc=0
- `HW_BROWSER=<chromium wrapper> python3 tests/browser.py`: rc=0, 0 failures. Running as root needs a wrapper that adds `--no-sandbox`. Without it, both base and head fail at launch, which is a problem with this environment, not with the PR.
- Not run: `tools/check-sources.py`, the weekly network check. The PR cites no new source.

## 3. Attacks

The house brand was used each time with only its accent replaced. Scripts and logs are in this directory: `attack12.py`, `attack3.py`, `attacks-1-2.log`.

**A1. Brand hue exactly on `--hw-danger`'s hue (27).** Run at chroma 0.05, 0.10, 0.15, 0.19 and 0.25.
- What the PR claims should happen: selection and focus move to the nearest hue that clears every bar, the brand's hue stays on 9, 10, light 11 and 12, the shift is printed, and contrast.py certifies the result.
- What happened: `ramps.py` exits 0 and prints two shift lines. At chroma ≥ 0.10 the move is 27 → 355; at 0.05 it is 27 → 342. Focus is forced by the ring under dark-more, 11.3–14.9 against a bar of 17. The emitted hues are 3, 7 and 8 at 355; dark 11 at 355; and 9, 10, light 11 and 12 at 27. `contrast.py` gives rc=0 with 0 failures. **Holds.**
- As disclosed, dark `--hw-accent-text` (dark step 11) also moves to 355, so dark links in a red brand become pink.
- Side note: a red accent with a named solid at L 0.6 is refused for its label contrast (4.32:1). That is the pre-existing label floor and has nothing to do with this PR.

**A2. Brand hue where both search sides fail for all 180°.** This is a near-grey accent at hue 262.
- What the PR claims should happen: no file is written, and the build refuses with a sentence that names the bar.
- What happened:
  - chroma 0.001, 0.005, 0.02 and 0.03: rc=1, no file. The message reads "the accent at chroma C reads as a state or a border at every hue: no hue clears the ring from --hw-line-strong; the ring from --hw-line-strong under more for its focus". The full walk takes about 2.8 s before refusing.
  - chroma 0.04: focus moves 262 → 284, and contrast.py certifies it.
  - chroma 0.0: refused earlier, by the schema check, "(0, 0.4]".
  - **Holds.**
- One nit: the message also says "or a state" when only border bars failed.

**A3. A moved focus role colliding with the success colour in dark `prefers-contrast: more`.**
- Input: every fifth hue at chroma 0.10, 0.15 and 0.19. That gives 26 builds whose focus moved. For each, I measured dark `accent-11` (the ring under more) against dark `green-12` (`--hw-success` under more), and dark `accent-8` against `green-11`.
- What the PR claims should happen: the PR claims nothing about this. Neither `SEPARATION` in ramps.py nor `ROLE_BARS` in contrast.py holds the ring apart from success, on base or on head. The only bars are against danger and line-strong.
- What happened: a moved focus never comes near success. The closest case is brand 45 or 50 at chroma 0.10, where focus goes to 88 and sits 29.6 CIEDE2000 from green-12 (32.4 at step 8). Moves go either to 355 or to 87–88, because the search walks away from red and stops well before 150. **No collision can be produced through the shift.**
- What does exist is a gap that predates this PR: an *unshifted* green brand leaves its ring about 11 from success under dark-more. Brand 150 gives 11.08, 145 gives 11.41 and 148.9 (spotify) gives 11.12, and neither instrument refuses this on base or head. Base refused these brands for their fill, not their ring. Head now ships them with the ring at the brand's green, because only the selection moved. So the PR does turn previously refused green brands into certified ones whose ring is about 11 CIEDE2000 from `--hw-success` under dark-more. This is no regression on any bar the house declares. Whether a ring should be held apart from success is a question for the captain.

## 4. Neighbours

Every check that reads the files this PR touches was run on both base and head. Those files are `tools/ramps.py`, `tests/ramps.py`, `tests/invariants.py`, `tests/brands/`, and the docs that `check-links.py` reads. The tools that call into ramps.py are contrast.py, export.py, distinct.py, mutation_tests, painted and browser.

All are green on both. Nothing fails on head that passes on base. The only other in-tree caller of `ramps.render`/`ramps.build` is `tools/ramps.py:731`, which the PR updated for the 4-tuple.

## 5. Things in the diff the body does not mention, or mentions differently

1. The body's red commit hash (`a93de3a`) is not on the branch; the real one is `dd3bee4`.
2. `verify()` now refuses any CSS whose separation bars miss. This applies only when the file has no other failures and both themes carry an accent. So `ramps.py --check` now enforces the separation bars on committed files too, and it uses ramps.py's own CIEDE2000. That is a new refusal path in the first instrument, which the body only partly states ("re-measures the bars on the written file").
3. `build(brand, shift=True)` gained a parameter, and `render()` now returns 4 values instead of 3. This is internal API. The only caller is updated.
4. `lab8()` uses IEC 61966-2-1's four-place matrix and white, rather than contrast.py's rationals. The bars are aimed 0.3 above to absorb the difference. This is in the docstring, not the body.
5. Step 10 (hover) is always built at the brand's hue, while step 9 keeps the brand's hue too. That is consistent with the claim.
6. `--hw-accent-edge` (step 8) moves with focus, so an accent solid's edge takes the working hue while the solid keeps the brand hue. This is in the design doc's table but not called out as visible.
7. The refusal sentence can be empty of bar names if every candidate raised `BrandError`, because `everywhere` stays `None`. I could not trigger this; it is a robustness nit.

Verdict: PASS - red on base for the stated reason and green on head. Every entry point is green on head and nothing is new versus base. A1 and A2 behave as claimed. A3 cannot be produced through the shift, and the nearest real issue predates the PR: no bar holds the ring from success, and unshifted green brands now certify at about 11 CIEDE2000. Only documentary nits otherwise, mainly the wrong red-commit hash in the body.
