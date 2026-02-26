---
type: issue
state: open
created: 2026-02-24T15:42:40Z
updated: 2026-02-24T15:42:40Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/181
comments: 0
labels: feature, area:ci, area:workspace, effort:small, semver:minor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:52.964Z
---

# [Issue 181]: [[FEATURE] Add TOML linting as a pre-commit hook](https://github.com/vig-os/devcontainer/issues/181)

### Summary

Add TOML linting to the pre-commit pipeline so TOML files are validated consistently in local development and CI.

### Problem / Motivation

TOML files currently lack dedicated lint enforcement, which can allow format or style drift and late CI failures.

### Proposed Solution

Wire a TOML linter as a pre-commit hook, pinned to a stable version, and run it on TOML files in this repository.

### Acceptance Criteria

- [ ] TOML linting hook is added to `.pre-commit-config.yaml` with a pinned version
- [ ] Repository TOML files pass the new lint check
- [ ] `uv run pre-commit run --all-files` passes with the hook enabled
- [ ] CI runs the same TOML lint check without extra manual setup
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

### Out of Scope

- Non-TOML linting changes
- Broad pre-commit refactors unrelated to TOML

### Related Issues

Related to #122  
Related to #161

### Priority

Medium

### Changelog Category

Added

### Additional Context

Goal: TOML linting as a pre-commit hook.
