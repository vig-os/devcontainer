---
type: issue
state: closed
created: 2026-07-08T17:36:29Z
updated: 2026-07-09T05:40:39Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/946
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:19.115Z
---

# [Issue 946]: [Smoke-test dispatch failed for 0.5.0-rc1](https://github.com/vig-os/devkit/issues/946)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.5.0-rc1`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `manual-redispatch-after-fix`
- source_run_id: `28958113492`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/28958113492
- source_sha: `b843b2313f4476cbf9318247e073bbabc043a4e9`
- correlation_id: `manual-revalidation:0.5.0-rc1:after-206-945`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28962690842
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/207
- release PR: https://github.com/vig-os/devcontainer-smoke-test/pull/208

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `success`
- ready-release-pr: `success`
- trigger-release: `failure`
- wait-release-pr-ci: `skipped`
- trigger-promote-release: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Do not rewrite or delete **published** GitHub Releases (or their linked tags when **immutable releases** are enabled) to retry the same version; bare git tags without a published release are not locked by that feature unless a tag ruleset applies.
- After fixing the root cause upstream, publish a **new** RC tag (or a new final attempt only after branch/tag state matches your release policy), then rely on a fresh dispatch.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 9, 2026 at 05:40 AM_

Resolved. This dispatch got past the deploy/prepare stages (after the pytest fix, devcontainer-smoke-test#206) and failed at 'Trigger and wait for release workflow' with `startup_failure` — root cause was the #920 `packages: read` gap on the consumer release pipeline's reusable-calling jobs, fixed by #948. The **0.5.0-rc2 smoke-test now passes end-to-end** (https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28976856991). Closing.

