---
type: issue
state: closed
created: 2026-02-11T15:21:42Z
updated: 2026-02-13T17:30:59Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/51
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:34.905Z
---

# [Issue 51]: [[FEATURE] Extract commit validation and action pin check into reusable org-level GitHub Actions](https://github.com/vig-os/devcontainer/issues/51)

### Description

Parent: #50 (Security Hardening)

Extract `validate_commit_msg.py` and `check_action_pins.py` (with their test suites) into standalone, reusable GitHub Actions hosted in separate `vig-os` org repositories. This enables consistent enforcement of commit message standards and SHA pinning policy across all org repositories.

### Problem Statement

Currently, `validate_commit_msg.py` and `check_action_pins.py` live inside the `devcontainer` repository. Any other `vig-os` repository that wants the same enforcement must copy these scripts manually, leading to drift and duplicated maintenance.

### Proposed Solution

1. **Create `vig-os/action-validate-commit-msg`**
   - Publish as a composite GitHub Action
   - Accept inputs for custom commit message patterns (optional override)
   - Include the test suite for CI on the action repo itself
   - Version with semantic tags (e.g. `v1`, `v1.0.0`)

2. **Create `vig-os/action-check-action-pins`**
   - Publish as a composite GitHub Action
   - Accept inputs for repo root path and verbosity
   - Include the test suite for CI on the action repo itself
   - Version with semantic tags

3. **Update `devcontainer` to consume the new actions**
   - Replace local script invocations in `.pre-commit-config.yaml` and `test-project/action.yml` with the published actions (SHA-pinned, naturally)
   - Keep local scripts as thin wrappers or remove them entirely

### Alternatives Considered

- **Monorepo for all org actions:** Simpler repo management but harder to version independently.
- **Keep scripts local, copy to other repos:** Current state; does not scale.

### Additional Context

- Both scripts are self-contained Python with no external dependencies beyond the standard library
- Pre-commit hooks can reference remote repos, so the actions could also serve as pre-commit hook sources

### Impact

- **Beneficiaries:** All `vig-os` repositories
- **Compatibility:** Non-breaking; existing repos adopt at their own pace
- **Risks:** Minimal; versioned releases ensure stability
