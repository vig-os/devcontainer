---
type: issue
state: closed
created: 2026-07-08T16:38:13Z
updated: 2026-07-09T05:40:37Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/943
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:19.832Z
---

# [Issue 943]: [Smoke-test dispatch failed for 0.5.0-rc1](https://github.com/vig-os/devkit/issues/943)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.5.0-rc1`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `28958113492`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/28958113492
- source_sha: `72dae066fa313f8dbcac8df2a4dca19883d25380`
- correlation_id: `vig-os/devcontainer:28958113492:0.5.0-rc1`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28959225333
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/204
- release PR: not created

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `failure`
- cleanup-release: `skipped`
- trigger-prepare-release: `skipped`
- ready-release-pr: `skipped`
- trigger-release: `skipped`
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

Resolved. This dispatch failed at 'Wait for deploy PR merge' because the deploy PR's `just test` couldn't find pytest (pytest-as-extra vs groups-only sync) — fixed downstream in devcontainer-smoke-test#206. A later re-dispatch then surfaced a second issue (consumer release pipeline `startup_failure`, fixed by #948). The **0.5.0-rc2 smoke-test now passes end-to-end** (https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28976856991). Closing.

