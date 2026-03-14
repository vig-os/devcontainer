---
type: issue
state: closed
created: 2026-03-13T08:22:30Z
updated: 2026-03-13T10:47:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/286
comments: 0
labels: chore, priority:blocking, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:56.118Z
---

# [Issue 286]: [[CHORE] Track commit-action fix for malformed tree path and update smoke-test pin](https://github.com/vig-os/devcontainer/issues/286)

## Chore Type
CI / Build change

## Description
Track the upstream fix for `vig-os/commit-action` where `FILE_PATHS: .` includes `.git/*` paths and fails GitHub Trees API with `tree.path contains a malformed path component`.

This repository should update its pinned `vig-os/commit-action` SHA in smoke-test workflow templates after the upstream fix is released.

## Acceptance Criteria
- [x] Upstream bug issue is resolved in `vig-os/commit-action` ([#15](https://github.com/vig-os/commit-action/issues/15))
- [x] A fixed `commit-action` release/tag exists and is verified
- [ ] `assets/smoke-test/.github/workflows/repository-dispatch.yml` is updated to the fixed `commit-action` ref
- [ ] `build/assets/smoke-test/.github/workflows/repository-dispatch.yml` is regenerated/updated consistently
- [ ] Smoke-test dispatch run passes end-to-end after pin update
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

## Implementation Notes
- Current failing pin in smoke-test template:
  - `vig-os/commit-action@e7dc876fbb73df9099831fed9bfc402108fd04c3` (v0.1.4)
- Failure observed in step:
  - `Commit and push deploy changes via signed commit-action`
- Root cause tracked upstream:
  - Directory expansion with `FILE_PATHS: .` includes `.git/*`, which is invalid for `git.createTree`.

## Related Issues
- Related to #284
- Related to #169
- Blocks release smoke-test stabilization
- Upstream: `vig-os/commit-action#15`

## Priority
Critical

## Changelog Category
No changelog needed

## Additional Context
- Failing job: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23041842084/job/66921644763#step:8:15
- Upstream fix tracking issue: https://github.com/vig-os/commit-action/issues/15
