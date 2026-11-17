# Verification of PR #50 at afa89a8 (working in progress)

## 1. Red then green
- Base: origin/main 2fd14a0 (merge base). Head: afa89a8a.
- Red: tests from dd3bee4 (the PR's test-only commit) over base tools: `python3 tests/ramps.py` -> rc=1, 4 failures:
  meadow/spotify/ember "printed no shift", and contrast.py refusing `--hw-accent-fill` vs a state fill
  (meadow 1.2, spotify 3.0/3.3, ember 3.2/3.4 CIEDE2000, bar 5). This is the stated reason.
- Green: `python3 tests/ramps.py` on head -> 0 failures.
