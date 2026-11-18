# Verification of PR #48 at cf8d55ae

PR: "fix(contrast): certify component fills against the grounds they sit on".
Base: origin/main 2fd14a0 (the merge base). Head: cf8d55a.
Commits on the head: 344742e (test, red on purpose), 2023911 (fix), cf8d55a (test hardening).
Logs and the attack harness are in this directory.

## 1. Red then green

The changed test is `tests/components.py`. It gains rule 8, `check_fills`, and seven negative controls.

| tree | command | exit | result |
|---|---|---|---|
| base 2fd14a0 + head's `tests/components.py` | `python3 tests/components.py` | 1 | 34 failures (`red-base.txt`) |
| first PR commit 344742e (test only) | `python3 tests/components.py` | 1 | 30 failures (`red-first-commit.txt`) |
| head cf8d55a | `python3 tests/components.py` | 0 | 0 failures, 22 solids and tracks, 0 under 1.4.11, 7 excepted, every control caught (`green-head.txt`) |

The failures on base are for the reason the PR gives.
- 30 are rule 8: `.hw-btn--accent` (fill and hover) and `.hw-meter > i.on` on pointback light and quoth light, each on all five page grounds.
- Pointback measures 1.68 to 1.95:1 and quoth 1.15 to 1.34:1, against a bar of 3.0.
- The other 4 are bookkeeping. Two say "the rule they edit has moved", and two controls are reported as not caught. All four exist because those controls edit strings the fix introduces.
- The audit control fails on base at exactly the numbers the PR quotes: the pin without its inner edge, refused at pointback 1.95:1 and quoth 1.34:1.

## 2. Full check entry points on head

All were run in the foreground with `timeout 900`. The script is reproduced in `full-*.txt`.

| command | head |
|---|---|
| `python3 tools/ramps.py --check` | exit 0 |
| `python3 tools/contrast.py` | exit 0, 0 failures |
| `python3 tools/export.py`, plus `examples/papertrace`, `examples/pointback` and `examples/quoth` | exit 0 each, 0 divergent; `git status --porcelain` empty |
| `python3 tools/distinct.py` | exit 0, 6 pairs, 0 indistinguishable |
| `python3 tools/faces.py --vendored` | exit 0, 0 failed |
| `python3 tools/components.py --check` | exit 0, 18 renders current |
| `python3 tools/check-links.py` | exit 0, 149 checked, 0 unresolved |
| `python3 tools/test-check-sources.py` | exit 0 |
| `python3 tests/invariants.py` | exit 0, 0 failures |
| `python3 tests/mutation_tests.py` | exit 0, 23/23 as expected |
| `python3 tests/ramps.py` (no `--sweeps`) | exit 0, 0 failures |
| `python3 tests/exports.py` | exit 0, 0 failures |
| `python3 tests/components.py` | exit 0, 0 failures |
| `python3 tests/browser.py` | exit 0, 0 failures (a local Chromium was found) |
| `python3 tests/token_diff.py` | exit 0 |

- `git diff --quiet origin/main pr48 -- exports examples ramps fonts tools` exits 0. No token, export, font or tool changed, so the body's consumer claim holds.
- CI on cf8d55a: `checks`, `consistency`, `token-diff`, `secrets`, `watermark` and `shadow` all completed success.
- Not run: `tests/ramps.py --sweeps`, `tools/painted.py` (a local/release check) and `tools/check-sources.py` (it uses the network).

## 3. Attacks

Each attack edits `components.css` in memory and calls the head's own `check_fills` with its own `ramp_envs`. A result counts only failures that are not already present on the unmodified head. The harness is `attack*.py` and its output is `attacks-head.txt`.

**A. A fill on a tinted ground inside a dark prefers-contrast block.**

1. Input: `@media (prefers-contrast: more) { [data-theme="dark"] .hw-row[aria-selected="true"] .hw-btn--accent { --_bg: var(--hw-accent); --_bd: var(--hw-accent-edge); } }`. The real tinted ground is `--hw-accent-fill`.
   - Expected from the PR's claim ("on the ground it sits on"): measured against `--hw-accent-fill` in dark-more.
   - What happened: passed, but it was measured against the five neutral page grounds, never against `--hw-accent-fill`, and in all four tiers rather than dark-more.
   - The outcome is right today only by construction. Every tinted `*-fill` is step 3, and step 8 is held to 3:1 on steps 1 to 3. I measured `--hw-accent-edge` on accent, danger and success fills at 3.03 to 3.14 (light and dark) and 5.23 to 5.76 (more).
2. Input: the same, but `.hw-callout--danger .hw-btn--danger-solid` with the danger solid.
   - Expected: measured on `--hw-danger-fill`.
   - What happened: refused, but on page grounds (house dark-more 1.73 to 2.05:1). The descendant selector also no longer matches the selector-keyed `FILL_EXCEPTIONS` entry for `.hw-btn--danger-solid` in dark-more, so the exception does not follow the component.
3. Input: the same rule, declaring its tinted ground as a halo (`box-shadow: 0 0 0 2px var(--hw-danger-fill)`).
   - Expected: measured on the halo.
   - What happened: refused on `--hw-danger-fill` at 1.76 to 1.77:1 in dark-more only. That is correct.
4. Input: a dark-more override that swaps the accent button's edge for `--hw-accent-fill`.
   - Expected: refused.
   - What happened: refused (pointback light 1.87:1, edge 1.11:1).
   - Media and theme scope are ignored, so the same rule scoped to `[data-theme="light"]` is measured in every tier. This errs strict, not lax.

Conclusion: the check does not model a nested ground. Only a halo or the one hand-entered `GROUND_OF` entry (`.hw-toast .hw-btn` on ink) changes the ground. No current house rule is wrong because of this.

**B. A component whose fill token is an alias of another alias.**

1. Input: `.hw-btn--brand { --_solid: var(--hw-accent); --_brand: var(--_solid); --_bg: var(--_brand); --_bd: var(--_brand); }`.
   - Expected: refused, as the direct form is (pointback light 1.87:1).
   - What happened: **missed entirely, measured as nothing**. `roles_in` only reads `var(--hw-…)` literally present in the declaration, and it does not follow a private `--_x` alias chain.
   - This is a real gap, and the PR's own unmeasured `--_live` is one instance of it. No current rule uses such a chain for a solid.
2. Input: the meter's fallback switched to the role-to-step alias `--hw-accent-hover`.
   - Expected: refused.
   - What happened: refused (pointback light 2.15:1). Role aliases of aliases resolve through `contrast.resolve`.
3. Input: a fallback chain, `var(--_x, var(--_y, var(--hw-accent)))`.
   - Expected: refused.
   - What happened: refused. Fallbacks are read.

**C. A fill that passes on one ground and fails on another.**

1. Input: `.hw-btn--brand { --_bg: var(--hw-gray-9); --_bd: var(--hw-gray-9); }`. In house light-more this measures 4.54 on surface and 3.90 on fill.
   - Expected: refused on exactly the failing grounds.
   - What happened: refused in house light-more on `--hw-bg` (4.35), `--hw-bg-subtle` (4.13) and `--hw-fill` (3.90). It was not refused on `--hw-surface` or `--hw-surface-raised`. Each ground is judged on its own.
2. Input: the same, with a halo in `--hw-surface`.
   - Expected: light-more passes, because the solid now sits on its halo.
   - What happened: light-more passed, and dark-more was refused at 4.01 to 4.03:1, which is correct.
3. Input: the accent button edged in `--hw-line`.
   - Expected: refused.
   - What happened: refused (pointback light edge 1.40:1).

## 4. Neighbours, base against head

I ran the same 18 entry points from section 2 on base 2fd14a0, and all exited 0 (`full-base.txt`). Nothing fails on head that passes on base, and nothing fails on either.

## 5. What the diff does that the body does not say

- **The commit hashes in the body are stale.** It cites 7258d5f, 680d87e and cd74e75; the branch holds 344742e, 2023911 and cf8d55a. The first commit's red count (30) does match.
- **Media queries and theme selectors are ignored by `fills_in`.** Only forced-colors and print are skipped. Every rule is measured in all four tiers, and `FILL_EXCEPTIONS` keys on the exact selector string. A scoped or nested restatement of an excepted component therefore loses its exception (see A2).
- **An edge is inherited only by a selector of the exact form `.hw-x--y`.** A nested or stated variant is measured with no edge unless it restates one. This errs strict.
- **`EDGE_PROPS` is `--_bd`, `border-color` and `border`, plus inset box-shadow.** `outline` and the per-side `border-*` properties are not read as an edge, so a component edged that way would be refused.
- **`is_solid` treats any directly named step 9 or 10 as a solid**, in any fill property. That is stated in the code comment, not in the body.
- The body does mention the README sentence, catalogue anatomy, the regenerated sheets, `design/64-component-sheets.md`, the 18 re-stamped renders, and the `ramp_envs` dark-more fix.
- The renders were checked only by stamp: `tools/components.py --check` hashes the inputs, not the pixels. I did not look at the images.

## Summary

- The fix does what it says. It is red on base for the stated reason, green on head, all checks pass on head, and nothing changed outside `components/`, `tests/`, the README and the generated book.
- Rule 8 holds against direct, fallback and role-alias fills, per-ground differences, halos and later state or theme overrides.
- It does not follow private `--_x` alias chains (B1 missed outright).
- It does not model a ground set by nesting rather than by a halo. A tinted ground is never consulted unless declared, and media scope is ignored.
- Neither gap hides a failure in today's CSS.
- The README sentence says the check refuses a solid "on the ground it sits on", which is broader than what it measures.

Verdict: PARTIAL - the fix is correct and red/green and every check pass, but rule 8 misses a fill reached through a private alias chain and never measures a tinted ground set by nesting, so the README claim is wider than the check.

## Re-run (head 3f0e9798)

The head moved from cf8d55a to 3f0e979. Three commits were added, and they touch only `tests/components.py` and `README.md`:

- a602585 adds a control (test)
- 078ecb4 follows `--_x` aliases (fix)
- 3f0e979 narrows the README (docs)

`components/`, `exports`, `examples`, `ramps`, `fonts`, `tools` and `design` are byte-identical to cf8d55a. The merge base is still 2fd14a0. Logs are in `rerun-*.txt`.

### Each gap I named

| gap | status at 3f0e979 | a check that fails without it? |
|---|---|---|
| B1: a fill through a private alias chain is not measured | **Closed in code.** `roles_in` follows `--_x` through the box's own declarations and its component's base rule, and takes a fallback only when the alias is undeclared | **Yes.** At a602585 (control added, fix absent), `python3 tests/components.py` exits 1 with "negative control not caught: a solid reached through a private alias chain". At head it exits 0 and the control is caught at pointback light 1.87:1. On head with the alias branch replaced by `elif False:`, it exits 1 with the same failure |
| A: a ground set by nesting (a tinted callout or selected row) is never measured | **Not closed in code.** The README and the rule-8 docstring now say plainly that it is not modelled, and that such rules are measured on the five page grounds unless `GROUND_OF` names the ground | **No.** No check. The over-broad claim is gone, but the gap is now a documented limit, not a refusal. Attacks 1a and 1h behave exactly as before |
| Media and theme scope ignored; selector-keyed exceptions do not follow a nested selector | Unchanged | No. This errs strict: it can only over-refuse, never miss |
| PR body cites stale hashes (7258d5f, 680d87e, cd74e75) | Unchanged. The body still cites them and does not mention a602585, 078ecb4 or 3f0e979 | n/a |

### New attacks on the alias fix

All were run through head's own `check_fills` (`attack6.py`).

| input | expected | result |
|---|---|---|
| B4 an alias cycle, `--_a: var(--_b); --_b: var(--_a); --_bg: var(--_a)` | no hang or crash; nothing painted, as in a browser | no crash, nothing measured |
| B5 an alias declared on the base `.hw-chip`, read by `.hw-chip--brand` | refused | refused, pointback light 1.87:1 |
| B6 an alias declared as `--hw-surface`, with the solid as its fallback | not refused (a browser uses the alias) | not refused |
| B7 an undeclared alias with the solid as its fallback | measured | measured as `--hw-accent`. It passes on the `--hw-line-strong` edge it inherits from `.hw-btn` (at least 3.06), which is correct |
| B8 an alias set on the ancestor `.hw-callout`, read by `.hw-callout .hw-btn--x` | refused | refused. Scope comes from the first `.hw-` class in the selector |
| B9 a state rule dropping the pin's edge through an alias in its halo | refused | refused, pointback 1.95:1 and quoth 1.34:1 |
| B10 a three-deep alias chain in the accent button's edge, resolving to `--hw-line` | refused | refused, edge 1.40:1 |

All the earlier attacks were re-run on head (`rerun-attacks-head.txt`). Every result is as in the first run except 2a, which is now refused at pointback light 1.87:1.

### Nothing regressed

- The same 18 entry points as in section 2 were run on 3f0e979, and all exited 0 (`rerun-full-head.txt`): ramps --check, contrast, export ×4 with an empty porcelain, distinct, faces --vendored, components --check (18 renders current), check-links (149, 0 unresolved), test-check-sources, and tests invariants, mutation_tests (23/23), ramps, exports, components, browser and token_diff.
- The `fills:` section of `tests/components.py` is identical to cf8d55a's: 22 solids and tracks, 0 under 1.4.11, 7 excepted, the same lowest figures. The alias fix changes no measured value in today's CSS.
- CI on 3f0e979: `checks`, `consistency`, `token-diff`, `secrets`, `watermark` and `shadow` all completed success.

Verdict 48 (re-run): PARTIAL - the alias-chain gap is closed with a control that fails without the fix (red at a602585 and under mutation, green at head), and nothing regressed; but the nested-ground gap is closed only by narrowing the README and docstring, with no check, and the PR body still cites stale commit hashes.
