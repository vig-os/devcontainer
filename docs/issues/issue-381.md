---
type: issue
state: open
created: 2026-03-19T16:30:25Z
updated: 2026-03-19T16:30:25Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/381
comments: 0
labels: feature, area:ci, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:23.588Z
---

# [Issue 381]: [[FEATURE] Fail fast in wait-deploy-merge when deploy PR checks fail](https://github.com/vig-os/devcontainer/issues/381)

### Description

The `wait-deploy-merge` job in the smoke-test `repository-dispatch.yml` workflow should detect failed CI checks on the deploy PR and exit early, rather than waiting for the full 30-minute timeout.

### Problem Statement

When the deploy PR's CI checks fail (e.g. [PR #40](https://github.com/vig-os/devcontainer-smoke-test/pull/40)), auto-merge never fires and the PR remains in `OPEN` state. The current polling loop only checks for `MERGED` or `CLOSED` states, so it keeps polling for up to 1800 seconds before timing out. This wastes ~30 minutes of CI runner time and delays failure feedback to the upstream release pipeline.

### Proposed Solution

Enhance the polling loop in the `wait-deploy-merge` job (`assets/smoke-test/.github/workflows/repository-dispatch.yml`) to also query the PR's check status on each iteration. Strategy:

1. After checking `state`, query the PR's status checks via `gh pr checks "${PR_URL}" --json bucket,state` (or `gh pr view --json statusCheckRollup`).
2. If all checks have completed and any have failed, exit immediately with an error -- auto-merge will never proceed.
3. If checks are still pending, continue polling as before.

Sketch of the additional check inside the loop:

```bash
CHECKS_JSON="$(gh pr checks "${PR_URL}" --json bucket 2>/dev/null || echo '[]')"
FAIL_COUNT="$(echo "${CHECKS_JSON}" | jq '[.[] | select(.bucket == "fail")] | length')"
PENDING_COUNT="$(echo "${CHECKS_JSON}" | jq '[.[] | select(.bucket == "pending")] | length')"
if [ "${FAIL_COUNT}" -gt 0 ] && [ "${PENDING_COUNT}" -eq 0 ]; then
  echo "ERROR: deploy PR checks failed -- auto-merge will not proceed: ${PR_URL}"
  exit 1
fi
```

### Alternatives Considered

- **Webhook-based approach**: Replace polling with a `workflow_run` trigger on the downstream repo. More complex, requires additional workflow wiring, and does not fit the current cross-repo dispatch pattern as directly.
- **Reduce timeout**: Lowering timeout still wastes runner time and can create false timeouts on slow CI runs.
- **Check only after N iterations**: Simpler, but still delays feedback.

### Additional Context

- Downstream deploy PR: [#40](https://github.com/vig-os/devcontainer-smoke-test/pull/40)
- Waiting job run: [actions job 67774383060](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23304352254/job/67774383060)

### Impact

- Faster failure feedback when deploy PR checks fail.
- Reduced wasted CI runtime on known-failed deploy PRs.
- No behavior change on successful merge path.

### Changelog Category

Changed

### Acceptance Criteria

- [ ] `wait-deploy-merge` exits within 2 polling cycles when deploy PR checks fail
- [ ] `wait-deploy-merge` still waits correctly when checks are pending
- [ ] `wait-deploy-merge` still succeeds when PR merges normally
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
