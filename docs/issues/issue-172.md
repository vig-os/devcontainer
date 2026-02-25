---
type: issue
state: open
created: 2026-02-24T10:13:37Z
updated: 2026-02-24T10:13:37Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/172
comments: 0
labels: feature, area:ci, effort:medium, semver:minor
assignees: none
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-25T04:25:55.092Z
---

# [Issue 172]: [[FEATURE] Add RC publishing and cleanup to devcontainer release workflow](https://github.com/vig-os/devcontainer/issues/172)

### Description

Add release-candidate (RC) publishing capability to the devcontainer release workflow, allowing pre-release images to be smoke-tested before the final release. Include cleanup of RC tags after the final release is published.

### Problem Statement

The current release workflow publishes the final image directly. There is no pre-release validation step where the built image can be tested in a real downstream CI environment before it reaches users. If the image has a regression that existing tests don't catch (e.g., tool misconfiguration in a CI context), it ships to users.

### Proposed Solution

- Add RC publishing capability (new workflow `release-rc.yml` or new job in existing `release.yml`):
  - Triggered manually or automatically when CI passes on a release branch PR
  - Publishes `X.Y.Z-rc1` to GHCR (`ghcr.io/vig-os/devcontainer:X.Y.Z-rc1`)
  - Supports incrementing RC number (`rc1`, `rc2`, etc.)
- Add RC cleanup step to the final release publish job:
  - After `X.Y.Z` is published, delete all `X.Y.Z-rc*` tags from GHCR via `gh api`
- RC tags follow SemVer pre-release format

### Alternatives Considered

See parent issue #169 for full alternatives analysis.

### Additional Context

This is sub-issue 3 of 4 for #169 (Phase 1). Can be worked in parallel with #170 (smoke-test repo bootstrap).

Dependency graph:
- No dependencies (parallel with #170, #171)
- Sub-issue 4 (cross-repo dispatch) depends on this issue

The devcontainer repo's existing release workflow is at `.github/workflows/release.yml`. The template release workflow at `assets/workspace/.github/workflows/release.yml` is not modified by this issue.

### Impact

- Backward compatible. Adds new capability to the release workflow without changing the existing release flow.
- Minor GHCR storage cost for RC images (cleaned up after final release).

### Changelog Category

Added

### Acceptance Criteria

- [ ] Can publish `X.Y.Z-rc1` to GHCR from a release branch
- [ ] Can publish incremented RCs (`rc2`, `rc3`, etc.)
- [ ] RC tags are cleaned up from GHCR after the final `X.Y.Z` is published
- [ ] Existing release workflow is not broken
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
