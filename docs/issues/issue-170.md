---
type: issue
state: open
created: 2026-02-24T10:13:03Z
updated: 2026-02-24T12:42:49Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/170
comments: 0
labels: feature, area:ci, effort:medium, area:testing, semver:minor
assignees: c-vigo
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-25T04:25:55.708Z
---

# [Issue 170]: [[FEATURE] Bootstrap smoke-test repo with bare-runner CI](https://github.com/vig-os/devcontainer/issues/170)

### Description

Create the public repository `vig-os/devcontainer-smoke-test`, deploy a workspace from the current devcontainer template, and verify that the shipped `ci.yml` workflow runs successfully in a real GitHub Actions environment.

### Problem Statement

The CI workflow shipped under `assets/workspace/.github/workflows/ci.yml` is never executed in a real GitHub Actions environment as part of any testing process. If an action pin breaks, a `uv` version incompatibility appears, or a runner environment changes, no test catches it until a downstream user hits the failure.

### Proposed Solution

- Create public repo `vig-os/devcontainer-smoke-test`
- Deploy a fresh workspace via `init-workspace.sh` (with placeholder values resolved)
- Set up branch model (dev/main) with branch protection
- Verify the shipped `ci.yml` runs successfully (lint, test, security, dependency-review jobs pass)
- Add a `repository_dispatch` listener workflow (stub for later cross-repo wiring in a follow-up sub-issue)
- Add a README documenting the repo's purpose and relationship to the devcontainer project

### Alternatives Considered

See parent issue #169 for full alternatives analysis.

### Additional Context

This is sub-issue 1 of 4 for #169 (Phase 1). Can be worked in parallel with sub-issue 3 (RC publishing).

Dependency graph:
- **This issue** and sub-issue 3 (RC publishing) have no dependencies
- Sub-issue 2 (container CI variant) depends on this issue
- Sub-issue 4 (cross-repo dispatch) depends on all three

### Impact

- Backward compatible. Creates new infrastructure only.
- Public repo = free GitHub Actions minutes.

### Changelog Category

Added

### Acceptance Criteria

- [x] Public repo `vig-os/devcontainer-smoke-test` exists
- [x] Workspace is deployed from the current template with placeholders resolved
- [x] Branch model (dev/main) is set up
- [ ] `ci.yml` passes on a PR to dev (lint, test, security jobs)
- [ ] `repository_dispatch` listener workflow exists (stub)
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
