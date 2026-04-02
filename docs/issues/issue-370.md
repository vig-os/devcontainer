---
type: issue
state: closed
created: 2026-03-19T11:06:29Z
updated: 2026-03-19T12:43:45Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/370
comments: 0
labels: bug, priority:high, area:ci, effort:medium, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:25.648Z
---

# [Issue 370]: [[BUG] Release test-image setup intermittently segfaults on uv sync (exit 139)](https://github.com/vig-os/devcontainer/issues/370)

## Description
Release run `23290944122` (attempt 3) fails in `Build and Test (amd64)` job `#67728038442` during `Run image tests`.

Failure path:
`Run image tests` → internal `setup-env` → `uv sync --frozen --all-extras` → exit `139` (segfault)

Observed pattern:
- `uv sync --frozen --all-extras` succeeds earlier in `Build container image`
- The segfault occurs when `test-image` runs setup again in the same job
- This reproduces across retries and is no longer a one-off transient

## Steps to Reproduce
1. Trigger Release workflow for `release/0.3.1` (same conditions as run `23290944122`)
2. Let `Build and Test (amd64)` proceed to `Run image tests`
3. Observe failure in internal setup step at `uv sync --frozen --all-extras`
4. Repeat run/retry; observe same `exit 139` pattern

## Expected Behavior
`Run image tests` setup completes successfully and does not crash in `uv sync`.

## Actual Behavior
`uv sync --frozen --all-extras` exits with code `139` (segfault), failing the job.

## Environment
- **OS**: GitHub Actions Ubuntu runner (`ubuntu-22.04`)
- **Container Runtime**: Podman (installed via setup action)
- **Image Version/Tag**: `0.3.1-rc4-amd64`
- **Architecture**: AMD64

## Additional Context
- Related run: https://github.com/vig-os/devcontainer/actions/runs/23290944122
- Failing job: https://github.com/vig-os/devcontainer/actions/runs/23290944122/job/67728038442
- Related rollback issue: #369
- arm64 leg is cancelled due matrix `fail-fast` after amd64 failure

## Possible Solution
Harden setup around `uv sync` in `.github/actions/setup-env/action.yml` with retry/fallback handling (e.g., targeted cache cleanup and single retry on crash), or avoid redundant sync during test-image setup when already prepared.

## Changelog Category
Fixed
