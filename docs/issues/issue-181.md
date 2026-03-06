---
type: issue
state: open
created: 2026-02-24T15:42:40Z
updated: 2026-03-04T12:33:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/181
comments: 1
labels: feature, area:ci, area:workspace, effort:small, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-05T04:18:20.284Z
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
---

# [Comment #1]() by [c-vigo]()

_Posted on March 4, 2026 at 08:54 AM_

Implementation plan for #181 (no claim, no code changes yet)

Chosen TOML tool: Taplo (`ComPWA/taplo-pre-commit`), pinned to a stable revision.
Reason: mature + widely adopted TOML toolkit with reliable pre-commit integration; complements existing `check-toml` syntax validation.

Plan:
1. Update root `.pre-commit-config.yaml`
   - Keep existing `check-toml` hook
   - Add pinned Taplo hook (`taplo-lint`)
2. Mirror the same hook update in `assets/workspace/.pre-commit-config.yaml` to keep workspace template parity.
3. Verify locally:
   - `uv run pre-commit run --all-files`
4. Confirm CI parity:
   - No workflow changes expected, since CI already runs `uv run pre-commit run --all-files` via `.github/actions/test-project/action.yml`.
5. Validate acceptance criteria and include evidence in the PR notes.

Scope guardrails:
- In scope: TOML linting hook addition only
- Out of scope: unrelated pre-commit refactors and non-TOML linting changes

