# Verification of PR #47 at head 0bb96356

PR: https://github.com/Abhijeet34/halderworks-design/pull/47, "chore(gates): lock gates at 7c07f96851a2 (v8)"
Head: `0bb9635607eb8ff060619369fdd256e76024c3fe` (0bb96356). Author `hw-bodhi[bot]`.
Merge base: `2fd14a03581a4bae80b75c1d28c8a427b64dae5d`, which is also the tip of `main` when this was checked (2026-11-18).

**Verdict 47: PARTIAL.** Everything that can run in this repository passes on base and on head, and
the allowlist's intended behaviour goes red to green. Two things could not be run here: gates'
own `run/lock.sh` drift check, and a byte comparison of `.gitleaks.toml` with gates at `7c07f96`.
This session can read only this repository, not `Abhijeet34/gates`, so both rest on the PR's CI log.
Step 3 also found a hole in the new allowlist (finding F1). It does nothing in this repository,
which has no `log/` directory, and it cannot be fixed here because the file is the fleet's
canonical copy. It should go to gates.

## What the diff is

```
$ git diff --stat 2fd14a0 0bb9635
 .github/gates.lock |  1 +
 .gitleaks.toml     | 16 ++++++++++++++++
```

- `.github/gates.lock` (new): `7c07f96851a21041ad9f1cd0915f2c3220686ce4\n`.
- `.gitleaks.toml`: adds one `[[allowlists]]` entry at the end and removes nothing (0 `-` lines). The entry uses `targetRules = ["generic-api-key"]`, `condition = "AND"`, path `^log/[0-9]{20}\.jsonl$`, `regexTarget = "match"` and the regex `^key":"(?:[a-z]+(?:-[a-z]+)*-[0-9]+|[A-Za-z0-9-]+/[A-Za-z0-9._-]+/runs/[0-9]+)"$`.

What it claims: CI's gates calls move to the v8 commit through the lock, and the files gates syncs
come along with it.

## 1. Red then green

### My own check, written from the claim alone (title: "lock gates at 7c07f96851a2")

```
$ od -c .github/gates.lock          # at head
0000000   7   c   0   7   f   9   6   8   5   1   a   2   1   0   4   1
0000020   a   d   9   f   1   c   d   0   9   1   5   f   2   c   3   2
0000040   2   0   6   8   6   c   e   4  \n
$ python3 -c "...re.fullmatch(r'[0-9a-f]{40}\n', t) ... t.startswith('7c07f96851a2')"
40-hex+LF: True | prefix matches title 7c07f96851a2: True
$ git show 2fd14a0:.github/gates.lock
fatal: path '.github/gates.lock' does not exist in '2fd14a03581a4bae80b75c1d28c8a427b64dae5d'
```

Red on base: there is no lock, so gates runs at the bootstrap pin. Green on head: the lock names the full v8 commit from the title.

### The behaviour change, as CI meets it (the end-user symptom: step 2)

What a user of this repository sees is which gates commit its required `secrets` job runs at.

- **Base**: CI run 41564807304 (push of 2fd14a0 to main). `referenced_workflows` shows
  `shared-secret-scan.yml@2d686fa31bf6...` with no lock. The secret scan log ends
  `no local rule fixture; the rules are gates' canonical copy, verified above` / `scanned 46 commits, no leaks found`.
- **Head**: CI run 42029691080, job 127252665110 (`secrets / secret scan`). It checks out the
  bootstrap `2d686fa`, then `run/lock.sh` prints **`gates locked at 7c07f96851a21041ad9f1cd0915f2c3220686ce4`**,
  then `the rules are gates' canonical copy, verified above` / `scanned 47 commits, no leaks found`.
  All six check runs on head are `success`: `checks`, `secrets / secret scan`,
  `watermark / watermark scan`, `consistency / the system agrees with itself`, `token-diff` and
  `shadow / gate runner (shadow)`.

These are read from GitHub's logs, not re-run here. I could not run `lock.sh` locally because the
gates repository is outside this session's access. That is why step 2 is PARTIAL.

### The synced allowlist, red then green, on a fixture

The fixture is a scratch git repository. CI scans git history, so the scan here runs in `git` mode.
The first two files are the shapes the allowlist says it excuses:

| file | content (`key` field) | purpose |
|---|---|---|
| `log/00000000000000000001.jsonl` | `"key":"stopped-returns-2968"` | excused shape 1 |
| `log/00000000000000000002.jsonl` | `"key":"Abhijeet34/halderworks-design/runs/40330983490"` | excused shape 2 |

```
$ gitleaks git fx --config base.toml -f json -r t.json --exit-code 0     # gitleaks 8.30.0 and 8.29.0
   log/00000000000000000001.jsonl key":"stopped-returns-2968"           <- RED on base
   ... findings: 7
$ gitleaks git fx --config head.toml -f json -r t.json --exit-code 0
   (log/...0001.jsonl absent)                                             <- GREEN on head
   ... findings: 5
```

Shape 2 (`owner/repo/runs/<id>`) is not flagged even on base with this value, so the fixture does
not show that this branch of the regex is needed.

**Version caveat, measured.** gitleaks 8.24.3, 8.26.0, 8.27.2 and 8.28.0 ignore `targetRules`
allowlists entirely. They do not even apply the entries that already exist in this file: a fixture
at `internal/intent/redact_test.go` and `test/attachment-store.test.js` gives 2 findings on those
versions and 0 on 8.29.0 and 8.30.0. Every result above uses 8.29.0 or 8.30.0. Which version gates
installs (`run/install-gitleaks.sh`) could not be read from here.

## 3. Attack it (head config, gitleaks 8.29.0 and 8.30.0, same results)

| # | hostile input | outcome on head | right? |
|---|---|---|---|
| 03 | random 32-char value in `key`, right path | **reported** | yes |
| 04 | excused value, 19-digit file name `log/0000000000000000004.jsonl` | **reported** | yes |
| 05 | excused value, other directory `other/<20 digits>.jsonl` | **reported** | yes |
| 06 | secret disguised as word-number: `aK9fQ2xZ7bLm4PqR8sTvW1yC-6` | **reported** (mixed case is outside `[a-z]+`) | yes |
| 08 | excused value under another field name, `"api_key":"stopped-returns-2968"` | **reported** | yes |
| **07** | **secret disguised as a run path: `aK9fQ2xZ7bLm4PqR8sTvW1yC6dE3gH5j/x/runs/1`** | **excused (not reported)** | **no** |

**F1 (hole in the new allowlist).** The run-path branch, `[A-Za-z0-9-]+/[A-Za-z0-9._-]+/runs/[0-9]+`,
puts no limit on the owner and repo segments. Any high-entropy string written as
`<secret>/<anything>/runs/<digits>` in the `key` field of a `log/<20 digits>.jsonl` file is excused.
The entry's own comment says "a random-looking value in the same field of the same file is still
reported", and that is false for this shape. The blast radius is small: it needs that exact path,
the `key` field and a deliberately run-path-shaped value, and this repository has no `log/`
directory. The file is gates' canonical copy and the drift check forbids editing it here, so the fix
belongs upstream. One option is to limit the owner segment to GitHub's owner charset and length,
`[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})`, and to add a negative fixture for this case to
`.ci/gitleaks/test-allowlists.py`. This does not block the lock bump in this repository.

## 4. Neighbours: the repository's per-change checks and every suite in `tests/run.py` SUITES, base and head

Run in two worktrees (`git worktree add <dir> 2fd14a0` and `... pr47`), each command in the foreground:

| command | base | head |
|---|---|---|
| `python3 tools/ramps.py --check` | rc=0 | rc=0 |
| `python3 tools/contrast.py` | rc=0, 0 failures | rc=0, 0 failures |
| `python3 tools/export.py` (+ every `examples/*`), then `git status --porcelain` | rc=0, porcelain empty | rc=0, porcelain empty |
| `python3 tools/distinct.py` | rc=0, 6 pairs, 0 indistinguishable | same |
| `python3 tools/faces.py --vendored` | rc=0, 0 failed | same |
| `python3 tools/components.py --check` | rc=0, 18 renders current | same |
| `python3 tools/check-links.py` | rc=0, 149 checked, 0 unresolved | same |
| `python3 tools/test-check-sources.py` | rc=0 | rc=0 |
| `python3 tests/invariants.py` | rc=0, 0 failures | same |
| `python3 tests/mutation_tests.py` | rc=0, 23 cases: 23 as expected, 0 improved, 0 failed (80s) | same (81s) |
| `python3 tests/ramps.py` | rc=0, 0 failures | same |
| `python3 tests/exports.py` | rc=0, 0 failures | same |
| `python3 tests/components.py` | rc=0, 0 failures | same |
| `python3 tests/browser.py` | rc=1 the first time on both: "Running as root without --no-sandbox" (this container runs as root, so not the PR). Re-run with `HW_BROWSER=<wrapper that adds --no-sandbox to /opt/pw-browsers/chromium>`: rc=0, 0 failures | same |
| `python3 tests/token_diff.py` | rc=0 | rc=0 |
| `gitleaks git . --config .gitleaks.toml --exit-code 1` (8.30.0) | rc=0, no leaks found | rc=0, no leaks found |

The diff touches no Python, CSS or Markdown, so no check above can tell base from head. They are
run as the neighbour gate and all agree. The direct users of the two changed files are gates'
`shared-secret-scan.yml`, `shared-watermark-scan.yml` and `shared-gate-shadow.yml`. All three
reported `success` on head in CI (see step 2).

## 5. Scope

The diff changes only the lock and one synced file, which matches the title. I found nothing extra.
The rule in AGENTS.md ("A lock change is refused unless the pull request changes only the lock and
the synced copies and comes from the bump identity") holds: there are 2 files and the author is
`hw-bodhi[bot]`. Three notes:

- The PR body says it "Moves `.github/gates.lock` from 2d686fa...". The base has no lock file. The
  effective commit before this change was the bootstrap pin `2d686fa` in `ci.yml`, so the substance
  is right but the wording is not.
- `.githooks/pre-push` and `.githooks/commit-msg` are unchanged. The CI drift check at `7c07f96`
  passed, which suggests they still match v8. I did not check that directly (gates is out of scope).
- After merge, AGENTS.md ("currently v4, `2d686fa`" and "the caller has no `.github/gates.lock`,
  which is this repository's state") and the `# v4` comments in `ci.yml` and `gate-shadow.yml` will
  be stale. A lock PR may not touch them, so a follow-up docs PR is needed. The `uses: ...@2d686fa`
  lines are correct to stay, because they are the bootstrap.

## What could not be run, and why

- gates' `run/lock.sh` drift check, and a byte diff of `.gitleaks.toml` against gates@`7c07f96`.
  This session's GitHub access covers only `Abhijeet34/halderworks-design`, so both are taken from
  the head CI log ("gates locked at 7c07f96...", "the rules are gates' canonical copy, verified above").
- The exact gitleaks version gates installs. The results are given for 8.29.0 and 8.30.0, the first
  releases that honour `targetRules`.

## Spend

- About 10 minutes wall clock. Two runs of every suite (base and head, in parallel, about 2 minutes),
  plus the browser re-run.
- 7 read-only GitHub API calls (PR, check runs, two job logs, run list, job list) and nothing written
  to GitHub. Six gitleaks release tarballs downloaded from github.com/gitleaks (about 50 MB) into a
  scratch directory, not into the repository.
- No token counter is available inside this session, so model token spend is not reported.
