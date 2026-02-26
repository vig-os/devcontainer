---
type: issue
state: open
created: 2026-02-24T10:13:19Z
updated: 2026-02-24T10:13:19Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/171
comments: 0
labels: feature, area:ci, effort:medium, area:testing, semver:minor
assignees: none
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-25T04:25:55.384Z
---

# [Issue 171]: [[FEATURE] Add container-based CI workflow to smoke-test repo](https://github.com/vig-os/devcontainer/issues/171)

### Description

Add a `ci-container.yml` workflow to the smoke-test repo that runs the CI pipeline inside the devcontainer image using the GitHub Actions `container:` directive. This validates the image works as a CI environment alongside the existing bare-runner CI.

### Problem Statement

The devcontainer image ships all CI tools (Python, uv, pre-commit, ruff, pytest), but nothing validates that a full CI workflow runs successfully inside it in a real GitHub Actions environment. `test-image` checks tool presence; `test-integration` checks the devcontainer lifecycle. Neither tests the end-to-end CI use case with the `container:` directive.

### Proposed Solution

- Create `ci-container.yml` in the smoke-test repo
- Use `container: ghcr.io/vig-os/devcontainer:<tag>` directive on CI jobs
- Mirror the template CI steps (lint, test) but running inside the container
- Use `:latest` initially (RC tag support comes with sub-issue 4)
- Document any quirks or differences vs bare-runner CI (e.g., `actions/checkout` behavior, root user, no Docker-in-Docker)

### Alternatives Considered

See parent issue #169 for full alternatives analysis.

### Additional Context

This is sub-issue 2 of 4 for #169 (Phase 1). Depends on #170 (smoke-test repo bootstrap).

Dependency graph:
- Depends on #170 (smoke-test repo must exist)
- Sub-issue 4 (cross-repo dispatch) depends on this issue

### Impact

- Backward compatible. Adds a new workflow to the smoke-test repo only.
- No changes to shipped templates.

### Changelog Category

Added

### Acceptance Criteria

- [ ] `ci-container.yml` exists in the smoke-test repo
- [ ] CI jobs run inside the devcontainer image via `container:` directive
- [ ] Lint and test jobs pass inside the container
- [ ] Both bare-runner (`ci.yml`) and container (`ci-container.yml`) CI run on PRs
- [ ] Quirks and differences vs bare-runner CI are documented
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
