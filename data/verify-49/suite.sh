set -u
for c in "tools/ramps.py --check" "tools/contrast.py" "tools/export.py" "tools/export.py examples/papertrace" "tools/export.py examples/quoth" "tools/export.py examples/pointback" "tools/distinct.py" "tools/faces.py --vendored" "tools/components.py --check" "tools/check-links.py" "tools/test-check-sources.py" "tests/invariants.py" "tests/mutation_tests.py" "tests/ramps.py" "tests/exports.py" "tests/components.py" "tests/browser.py" "tests/token_diff.py"; do
  out=$(timeout 900 python3 $c 2>&1); rc=$?
  printf '%-45s exit %s | %s\n' "python3 $c" "$rc" "$(echo "$out" | grep -v '^\s*$' | tail -1 | cut -c1-140)"
done
echo "porcelain after: $(git status --porcelain | wc -l) lines"
