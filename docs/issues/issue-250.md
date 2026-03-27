---
type: issue
state: closed
created: 2026-03-10T09:01:26Z
updated: 2026-03-10T15:35:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/250
comments: 0
labels: feature, area:image, area:workspace, effort:small, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-11T04:15:15.087Z
---

# [Issue 250]: [[FEATURE] Add --smoke-test flag to init-workspace.sh to deploy smoke-test-specific files](https://github.com/vig-os/devcontainer/issues/250)

### Description

Add a `--smoke-test` flag to `init-workspace.sh` that deploys additional files specific to the smoke-test repo (`vig-os/devcontainer-smoke-test`). Currently the only file not provided by the standard workspace template is `.github/workflows/repository-dispatch.yml` -- the dispatch listener that wires RC smoke testing. Bundle this file (and any future smoke-test-specific assets) in the image and deploy them when the flag is passed.

### Problem Statement

After a fresh `init-workspace.sh` deployment, the smoke-test repo is fully functional except for the `repository-dispatch.yml` workflow. This file must be manually committed to the smoke-test repo, creating a maintenance gap: updates to the dispatch listener must be synced by hand rather than shipped with the image. As the smoke-test repo evolves (Phase 2/3 of #169), more smoke-test-specific files may be needed, and without a dedicated deployment path they will all require manual sync.

### Proposed Solution

1. **Bundle smoke-test assets in the image:** Place smoke-test-specific files under a well-known path in the image (e.g. `assets/smoke-test/`), alongside the existing workspace template assets.
2. **Add `--smoke-test` flag to `init-workspace.sh`:** When passed, the script copies the smoke-test assets into the workspace after the standard template deployment. Currently this means:
   - `.github/workflows/repository-dispatch.yml`
3. **No-flag behavior is unchanged:** Standard workspace deployment is unaffected.

### Alternatives Considered

- **Keep `repository-dispatch.yml` committed in the smoke-test repo:** Current approach. Works but requires manual sync when the dispatch listener changes. Becomes worse as more smoke-test-specific files are added in later phases.
- **Separate script (`init-smoke-test.sh`):** Adds another entrypoint to maintain. A flag on the existing script is simpler and more discoverable.

### Additional Context

Sub-issue of #169 (Phase 1). Related to #173 (cross-repo dispatch).

After a fresh `init-workspace.sh` deploy, the only missing file is:
- `.github/workflows/repository-dispatch.yml` (dispatch listener for RC smoke testing)

Everything else (.cursor/rules, .cursor/skills, .github/workflows/ci.yml, .github/workflows/ci-container.yml, issue templates, label taxonomy, etc.) is already provided by the standard template.

### Impact

- **Who benefits:** Maintainers of the smoke-test repo. The dispatch listener stays in sync with the image automatically.
- **Compatibility:** Backward compatible. `--smoke-test` is opt-in; default behavior is unchanged.

### Changelog Category

Added

### Acceptance Criteria

- [ ] Smoke-test-specific files are bundled in the image under a documented path
- [ ] `init-workspace.sh` accepts `--smoke-test` and deploys those files
- [ ] Standard (no-flag) behavior is unchanged
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
