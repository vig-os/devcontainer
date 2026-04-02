---
type: issue
state: closed
created: 2026-03-23T12:31:29Z
updated: 2026-03-23T17:10:26Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/417
comments: 1
labels: bug
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-24T04:25:02.786Z
---

# [Issue 417]: [Smoke-test dispatch failed for 0.3.1-rc12](https://github.com/vig-os/devcontainer/issues/417)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.3.1-rc12`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `23436693172`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/23436693172
- source_sha: `59962c01a49848e3d688dd8f1b1058f7a82840f8`
- correlation_id: `vig-os/devcontainer:23436693172:0.3.1-rc12`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23437228417
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/65
- release PR: not created

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `failure`
- ready-release-pr: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Re-dispatch using a new RC tag/version once root cause is fixed.
---

# [Comment #1]() by [c-vigo]()

_Posted on March 23, 2026 at 03:17 PM_

## RCA (smoke-test dispatch `0.3.1-rc12`)

### Symptom
Downstream run [23437228417](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23437228417) failed in **Trigger and wait for prepare-release workflow** because [prepare-release run 23437371680](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23437371680) exited in **Validate Release Preparation** with:

```
ERROR: CHANGELOG.md Unreleased section has no entries
```

### Root cause
1. **Smoke-test install** (`init-workspace.sh --smoke-test`) uses `rsync --delete`, which replaces workspace `CHANGELOG.md` with the empty scaffold (only `### Added` / `### Changed` headings, no bullets).
2. **Manual deploy** to smoke-test `main` (PR #63) replaced the previous workflow behavior that wrote a minimal changelog (or later only remapped headers) without restoring real entries. After that, merged `dev` ended up with an empty `## Unreleased`.
3. **prepare-release** correctly requires at least one bullet under `## Unreleased`; with none, validation fails.

### Fix (landed in devcontainer repo)
- **`prepare-changelog unprepare`** in `packages/vig-utils`: renames the first top-level `## [semver] - …` heading to `## Unreleased` (inverse of the header side of `prepare`).
- **`init-workspace.sh --smoke-test`**: after template + smoke-test overlay, copy `.devcontainer/CHANGELOG.md` → `CHANGELOG.md` and run `prepare-changelog unprepare` so workspace changelog carries devcontainer release notes and satisfies prepare-release.
- **Smoke-test `repository-dispatch.yml`**: removed the redundant inline `awk`/`sed` remap (handled in the installer).

### Next steps for operators
- Promote updated templates to `vig-os/devcontainer-smoke-test` (deploy PR / manual deployment as usual).
- Re-dispatch smoke-test after a new RC tag that includes this fix.

Refs: implementation targets issue #417.

