---
type: issue
state: closed
created: 2026-03-22T09:44:08Z
updated: 2026-03-22T12:15:33Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/408
comments: 2
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-23T04:34:22.243Z
---

# [Issue 408]: [Smoke-test dispatch failed for 0.3.1-rc10](https://github.com/vig-os/devcontainer/issues/408)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.3.1-rc10`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `23400039119`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/23400039119
- source_sha: `60ae67a84619b17dd61e0c229217a4ed2ddb164b`
- correlation_id: `vig-os/devcontainer:23400039119:0.3.1-rc10`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23400308501
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/57
- release PR: https://github.com/vig-os/devcontainer-smoke-test/pull/58

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `success`
- ready-release-pr: `failure`
- trigger-release: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Re-dispatch using a new RC tag/version once root cause is fixed.
---

# [Comment #1]() by [c-vigo]()

_Posted on March 22, 2026 at 12:12 PM_

## Root Cause Analysis

**Cause:** Self-approval by the same GitHub App that authored the PR.

The `repository-dispatch.yml` on `main` in `devcontainer-smoke-test` runs an
outdated version of the `ready-release-pr` job that calls
`gh pr review --approve` after creating the release PR. Since the same app
(`vig-os-release-app[bot]`) authored PR #58 and attempted to approve it,
GitHub rejected with:

> `failed to create review: GraphQL: Review Can not approve your own pull request`

This caused the `ready-release-pr` job to fail, which cascaded: auto-merge was
never enabled, release-kind labels were never applied, and `trigger-release` was
skipped entirely.

**Why the old workflow ran:** `repository_dispatch` events always use the
workflow from the default branch (`main`). The fix was already deployed to `dev`
via 0.3.1-rc10, but hasn't reached `main` yet -- a bootstrap problem since
the release PR merge is what promotes it.

**Evidence:**
- [Failing step log](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23400308501) -- step "Mark release PR ready and approve", error at `gh pr review --approve`
- [PR #58](https://github.com/vig-os/devcontainer-smoke-test/pull/58) -- open, `CLEAN` merge state, auto-merge not enabled, no labels

**Current state of PR #58:**
- Open, ready for review, mergeable (`CLEAN`)
- Auto-merge: not enabled
- Contains the corrected workflow (no self-approve)

**Resolution:** Manually merge PR #58. This promotes the fixed workflow to
`main`, preventing recurrence for future dispatches. No upstream code changes
needed -- the template already has the fix.

---

# [Comment #2]() by [c-vigo]()

_Posted on March 22, 2026 at 12:15 PM_

## Follow-up

[PR #58](https://github.com/vig-os/devcontainer-smoke-test/pull/58) has been merged to `main` in `devcontainer-smoke-test`.

The updated `repository-dispatch.yml` (no self-approve; label + auto-merge steps) is now the default-branch workflow, so future `repository_dispatch` runs should no longer hit the failure described in the RCA.

Closing as resolved.

