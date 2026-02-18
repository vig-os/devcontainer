---
type: issue
state: open
created: 2026-02-18T07:38:08Z
updated: 2026-02-18T07:38:08Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/72
comments: 0
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T07:38:24.221Z
---

# [Issue 72]: [[bug] Minor improvements to CI/CD](https://github.com/vig-os/devcontainer/issues/72)

## Review findings

### High – Release can proceed before all required CI checks are complete

In `release.yml`, the "Find and verify PR" step only rejects `FAILURE`/`ERROR` conclusions and requires at least one `SUCCESS`. Checks that are still `PENDING`, `IN_PROGRESS`, `QUEUED`, or `null` are silently ignored — so a release can proceed while checks are still running.

**Suggestion:** Also reject when any check has a non-terminal conclusion:

```bash
CI_PENDING=$(echo "$STATUS_ROLLUP" | jq '[.[] | select(.conclusion == null or .conclusion == "" or .conclusion == "PENDING")] | length')
if [ "$CI_PENDING" != "0" ]; then
  echo "ERROR: PR #$PR_NUMBER has $CI_PENDING checks still in progress"
  exit 1
fi
```

---

### Medium – Test actions can silently switch the workspace commit during release

Both `test-image/action.yml` and `test-integration/action.yml` run `actions/checkout` internally without a `ref` input. In `release.yml`, the `build-and-test` job first checks out `finalize_sha`, but these internal checkouts resolve to the event's `GITHUB_SHA` (HEAD of the dispatched branch), not the pinned SHA. If the release branch receives commits between dispatch and test execution (e.g., from the `sync-issues` workflow triggered during `finalize`), tests may run against different code than the build.

**Suggestion:** Add a `ref` input to both composite actions and pass `finalize_sha` from the calling workflow, or remove the internal checkout and rely on the job-level checkout.

---

### Low – `install-just` input is defined but not honored

In `setup-env/action.yml`, the `install-just` input defaults to `'true'` but the "Install just" step has no `if` condition — it always runs. Every other optional tool (`podman`, `node`, `devcontainer-cli`, `bats`) has an `if:` guard; this one is missing.

**Fix:** Add `if: inputs.install-just == 'true'` to the step.

---

### Low – macOS `stat` fallback is dead code

In `build-image/action.yml`, the tar verification step uses `stat -f%z ... || stat -c%s ...`. The `-f%z` form is macOS syntax. Since this action only runs on `ubuntu-22.04` runners, the macOS branch always silently fails. Not a bug, but misleading.

**Suggestion:** Remove the macOS fallback or add a comment explaining it's there for local testing.

_Originally posted by @gerchowl in https://github.com/vig-os/devcontainer/pull/56#pullrequestreview-3815764417_
            
