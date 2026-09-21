#!/bin/sh
# Applies the repository settings that are not files, from the files that describe them.
# Idempotent: a ruleset whose name already exists is updated in place rather than duplicated,
# which is what makes this safe to re-run after editing one of the JSON files.
#
# Usage: scripts/apply-repo-settings.sh OWNER/REPO
#
# It sends whatever is in the working tree and has no idea which files are the right ones, so
# run it only from a tree whose .github/rulesets/ and .github/settings/ are the ones you intend.
# `set -eu` makes it fail-fast for the same reason: a paste of independent lines would run the
# dangerous one after the safe one had already failed.
#
# `gh` rather than `gh-axi`, which is the fleet's usual tool: `gh-axi api` takes only
# `--field key=value` and has no flag that sends a JSON file as the request body, so it cannot
# express a ruleset. pointback and treadling both carry `gh-axi api -X PUT --input` in their copy
# of this script; that invocation is refused by the installed gh-axi with "unknown flag -X".
#
# AGENTS.md, "The settings that are not files", carries the reasoning; this file carries the
# commands so nobody retypes them.
set -eu

REPO="${1:?usage: apply-repo-settings.sh OWNER/REPO}"
cd "$(dirname "$0")/.."

# The ruleset requires the `checks` context. A required context that never reports blocks every
# pull request forever, so this is applied LAST, after .github/workflows/ci.yml has been merged
# and seen to publish that context on a real pull request.
apply_ruleset() {
  file="$1"
  name=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["name"])' "$file")
  # A name that matches nothing leaves the tool printing an empty-body notice rather than
  # nothing at all, so the id is taken only if it is all digits.
  id=$(gh api "repos/$REPO/rulesets" --jq \
    ".[] | select(.name == \"$name\") | .id" | tr -d ' ' | grep -E '^[0-9]+$' || true)
  if [ -n "$id" ]; then
    echo "updating ruleset $name ($id) from $file"
    gh api --method PUT "repos/$REPO/rulesets/$id" --input "$file"
  else
    echo "creating ruleset $name from $file"
    gh api --method POST "repos/$REPO/rulesets" --input "$file"
  fi
}

# Squash only, and keep the commit messages, so a conventional-commit subject survives the merge.
# Deleting the branch on merge is the same decision in the other direction: nothing on this
# repository reads a merged branch afterwards.
gh api --method PATCH "repos/$REPO" --input .github/settings/repository.json

# Topics are their own endpoint; they are not a field on the repository body.
gh api --method PUT "repos/$REPO/topics" --input .github/settings/topics.json

# Read-only default token, it cannot approve a pull request, and no unpinned action can come
# back. `enabled` is required in the second body: sending sha_pinning_required on its own is a
# validation error, not a partial update.
#
# can_approve_pull_request_reviews is false here where pointback and treadling both send true.
# This repository already had it off and turning it on would let a workflow satisfy a review
# requirement; there is no automation here that needs to.
#
# SHA pinning does not refuse `Abhijeet34/gates/...@main` below: a reusable workflow in a
# repository the same account owns is outside the policy. Measured on pointback, which has this
# setting live and calls the same shared secret scan at @main.
gh api --method PUT "repos/$REPO/actions/permissions/workflow" \
  --input .github/settings/actions-workflow-permissions.json
gh api --method PUT "repos/$REPO/actions/permissions" \
  --input .github/settings/actions-permissions.json

# Unchanged from GitHub's default, and applied anyway so it is diffable: this is what decides
# whether a fork's pull request runs CI without a maintainer clicking approve.
gh api --method PUT "repos/$REPO/actions/permissions/fork-pr-contributor-approval" \
  --input .github/settings/actions-fork-pr-approval.json

apply_ruleset .github/rulesets/main.json

echo "applied. verify:"
echo "  gh api \"repos/$REPO/rulesets\""
# NOT branches/main/protection: that endpoint does not read rulesets and answers 404 with
# every rule live, which reads exactly like an unprotected branch.
echo "  gh api \"repos/$REPO/rules/branches/main\""
echo "  gh api \"repos/$REPO/branches/main\" --jq .protected"
echo "  gh api \"repos/$REPO/actions/permissions\""
echo "  gh api \"repos/$REPO/actions/permissions/workflow\""
