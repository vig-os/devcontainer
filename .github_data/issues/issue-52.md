---
type: issue
state: open
created: 2026-02-11T18:16:29Z
updated: 2026-02-11T18:16:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/52
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-11T18:16:47.797Z
---

# [Issue 52]: [[FEATURE] Add code coverage reporting to CI](https://github.com/vig-os/devcontainer/issues/52)

### Description

Add code coverage instrumentation and reporting to the CI pipeline for project-level Python tests.

### Parent Issue

Sub-issue of #37 (point 4: Default GitHub Actions / CI — code coverage).

### Problem Statement

The `test-cov` recipe in `justfile.base` references `--cov` but `pytest-cov` is not in dependencies, there is no coverage configuration, and CI does not generate or report coverage. There is no visibility into how much of the codebase is exercised by tests.

### Proposed Solution

1. Add `pytest-cov` to test dependencies
2. Configure coverage settings in `pyproject.toml` (`[tool.coverage.*]` sections)
3. Add a coverage step to the `project-checks` CI job that runs project-level tests with `--cov`
4. Generate XML + terminal reports, upload XML as artifact, and write a summary to `$GITHUB_STEP_SUMMARY`
5. Set a `fail_under` threshold to prevent coverage regressions

### Scope

- **In scope:** Project-level tests (`test_utils`, `test_release_cycle`, `test_validate_commit_msg`, `test_check_action_pins`) covering `scripts/` and `docs/`
- **Out of scope (future):** Image/integration tests (run inside containers), Codecov/Coveralls integration

### Acceptance Criteria

- [ ] `pytest-cov` in test dependencies
- [ ] Coverage configuration in `pyproject.toml`
- [ ] `just test-cov` works locally
- [ ] CI `project-checks` job generates and uploads coverage report
- [ ] Coverage summary appears in GitHub Actions job summary
- [ ] `fail_under` threshold enforced

Refs: #37
