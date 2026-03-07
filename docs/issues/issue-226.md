---
type: issue
state: open
created: 2026-03-06T19:06:01Z
updated: 2026-03-06T19:06:01Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/226
comments: 0
labels: bug, area:image, effort:small, semver:patch
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:38.397Z
---

# [Issue 226]: [[BUG] Taplo pre-commit hook compiles from source instead of using system binary](https://github.com/vig-os/devcontainer/issues/226)

### Describe the bug

The `taplo-pre-commit` hook (added in #223) uses `ComPWA/taplo-pre-commit` which compiles taplo from Rust source via `maturin`. This fails during image build because of a missing crate file (`taplo-lsp/Cargo.toml`) in the upstream package.

### Expected behavior

Taplo should follow the same pattern as hadolint and shellcheck: install the binary via `requirements.yaml` / `init.sh`, then use `language: system` in the pre-commit hook.

### Steps to reproduce

1. `just build` on `feature/217-reorganize-scripts-vig-utils` branch
2. Build fails at `pre-commit install-hooks` step with `taplo` metadata-generation-failed

### Root cause

- `taplo` is not in `requirements.yaml` — no binary install path exists
- Pre-commit hook uses `ComPWA/taplo-pre-commit` which tries to compile from source
- Upstream package has a broken workspace (missing `taplo-lsp/Cargo.toml`)

### Acceptance Criteria

- [ ] Add `taplo` to `scripts/requirements.yaml` with binary install (macOS + Linux)
- [ ] Change `.pre-commit-config.yaml` taplo hooks to `language: system` (like hadolint)
- [ ] `just build` succeeds with taplo hooks working
- [ ] `just init` installs taplo locally

### Implementation Notes

Follow the hadolint pattern:
- `requirements.yaml`: add taplo with `brew install taplo` (macOS) and GitHub release binary (Linux)
- `.pre-commit-config.yaml`: switch from `ComPWA/taplo-pre-commit` to local hooks with `language: system`
- Containerfile already runs `init.sh` so taplo will be available in the image

### Related Issues

Part of #223 (taplo was added but install was missed).
Blocks #218 (image build fails).

### Priority

High

### Changelog Category

Fixed
