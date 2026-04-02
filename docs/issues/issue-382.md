---
type: issue
state: open
created: 2026-03-19T16:38:19Z
updated: 2026-03-19T16:38:19Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/382
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:23.281Z
---

# [Issue 382]: [Smoke-test dispatch failed for 0.3.1-rc5](https://github.com/vig-os/devcontainer/issues/382)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.3.1-rc5`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `unknown`
- source_run_id: `unknown`
- source_run_url: n/a
- source_sha: `unknown`
- correlation_id: `unknown`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23304352254
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/40
- release PR: not created

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `failure`
- cleanup-release: `skipped`
- trigger-prepare-release: `skipped`
- ready-release-pr: `skipped`
- trigger-release: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Re-dispatch using a new RC tag/version once root cause is fixed.
