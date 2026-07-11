---
type: issue
state: closed
created: 2026-07-09T12:19:43Z
updated: 2026-07-09T13:28:13Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/957
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:16.345Z
---

# [Issue 957]: [Smoke-test dispatch failed for 0.5.0](https://github.com/vig-os/devkit/issues/957)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.5.0`
- release_kind: `final`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `29011944679`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/29011944679
- source_sha: `22c99413f89486648e15e7109f90f54a9b5a9e89`
- correlation_id: `vig-os/devcontainer:29011944679:0.5.0`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/29013565109
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/215
- release PR: https://github.com/vig-os/devcontainer-smoke-test/pull/216

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

_Posted on July 9, 2026 at 01:28 PM_

Due to intermittent GitHub Actions problems

