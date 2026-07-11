---
type: issue
state: closed
created: 2026-07-04T20:17:53Z
updated: 2026-07-04T20:47:11Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/852
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:36.488Z
---

# [Issue 852]: [Smoke-test dispatch failed for 0.4.0-rc1](https://github.com/vig-os/devkit/issues/852)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.4.0-rc1`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `28717901832`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/28717901832
- source_sha: `80de2c521e20dd640d67408bee09ccb2c904469a`
- correlation_id: `vig-os/devcontainer:28717901832:0.4.0-rc1`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28718363996
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/187
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

_Posted on July 4, 2026 at 08:47 PM_

Fixed by #853 (merged): `install.sh --version` now pins the scaffolded `.vig-os` via the `VIG_OS_VERSION` override in `init-workspace.sh`. The receiver curls `install.sh` from the dispatched tag and already passes `--version`, so the next candidate (rc2) exercises the fixed path end-to-end. Root-cause analysis and the broader shipped-workflows audit: #854.

