---
type: issue
state: closed
created: 2026-03-12T06:56:02Z
updated: 2026-03-12T07:47:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/262
comments: 0
labels: bug
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-12T07:59:29.202Z
---

# [Issue 262]: [[BUG] Smoke-test install deletes docs/issues/ and docs/pull-requests/ via rsync --delete](https://github.com/vig-os/devcontainer/issues/262)

### Description

The smoke-test deployment in `init-workspace.sh` uses `rsync --delete` (line 219) which deletes `docs/issues/` and `docs/pull-requests/` in the target repo. These directories are populated by `sync-issues` and should be preserved across workspace re-deployments.

### Steps to Reproduce

1. Have `docs/issues/` and `docs/pull-requests/` present in the smoke-test repo (populated by `sync-issues`)
2. Run `init-workspace.sh --smoke-test`
3. Observe both directories are deleted because they don't exist in `assets/workspace/`

### Expected Behavior

`docs/issues/` and `docs/pull-requests/` are preserved (excluded from `--delete`).

### Actual Behavior

Both directories are deleted by `rsync --delete`.

### Environment

- Devcontainer image (any version with `--smoke-test` support)

### Additional Context

Parent issue: #173
Related issue: #169

### Possible Solution

Add `--exclude='docs/issues/' --exclude='docs/pull-requests/'` to the smoke-test rsync command in `assets/init-workspace.sh`.

### Changelog Category

Fixed

### Acceptance Criteria

- [ ] `docs/issues/` and `docs/pull-requests/` survive `init-workspace.sh --smoke-test` re-deployment
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
