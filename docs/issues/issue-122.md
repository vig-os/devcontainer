---
type: issue
state: closed
created: 2026-02-20T15:35:54Z
updated: 2026-02-20T16:26:59Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/122
comments: 0
labels: chore, area:ci, area:image, effort:small, semver:patch
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T16:48:52.259Z
---

# [Issue 122]: [[CHORE] Add hadolint linting for Containerfiles](https://github.com/vig-os/devcontainer/issues/122)

### Chore Type

CI / Build change

### Description

Add [hadolint](https://github.com/hadolint/hadolint) static analysis for all Containerfiles in the repository. Hadolint enforces Dockerfile best practices (pinned base image tags, consolidated `RUN` layers, pinned apk/apt versions, etc.) and integrates shellcheck for inline `RUN` scripts.

### Acceptance Criteria

- [ ] `hadolint` pre-commit hook added to `.pre-commit-config.yaml`, pinned by SHA
- [ ] `Containerfile` passes hadolint with no warnings
- [ ] `tests/fixtures/sidecar.Containerfile` passes hadolint with no warnings
- [ ] `uv run pre-commit run --all-files` exits clean

### Implementation Notes

- Use `hadolint-docker` hook from `https://github.com/hadolint/hadolint`, pinned to `346e4199e4baca7d6827f20ac078b6eee5b39327` (v2.9.3)
- `DL3018` (unpinned apk packages) should be suppressed inline with `# hadolint ignore=DL3018` in fixture files where pinning individual package versions would be brittle
- The main `Containerfile` may need fixes after the hook is wired in

### Related Issues

_None_

### Priority

Medium

### Changelog Category

Added

### Additional Context

_None_
