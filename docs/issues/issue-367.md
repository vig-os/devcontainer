---
type: issue
state: closed
created: 2026-03-19T08:46:58Z
updated: 2026-03-19T10:18:47Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/367
comments: 0
labels: bug
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:26.309Z
---

# [Issue 367]: [[BUG] Upstream workflows incorrectly depend on resolve-image and .vig-os](https://github.com/vig-os/devcontainer/issues/367)

## Description

The upstream `vig-os/devcontainer` repo uses `resolve-image` + `container:` in two workflows (`sync-issues.yml`, `sync-main-to-dev.yml`), creating a circular dependency on its own published GHCR image. The repo also ships `.vig-os` at the root and in `assets/smoke-test/`, neither of which belongs in this upstream repo.

## Steps to Reproduce

1. Observe `.vig-os` at repo root with `DEVCONTAINER_VERSION=latest`
2. Observe `.github/workflows/sync-issues.yml` and `.github/workflows/sync-main-to-dev.yml` both use `./.github/actions/resolve-image` and run inside `container: ghcr.io/vig-os/devcontainer:${{ needs.resolve-image.outputs.image-tag }}`
3. If the `latest` image is unavailable on GHCR, both workflows fail

## Expected Behavior

Upstream workflows should use `./.github/actions/setup-env` to install tools natively on the runner. No `.vig-os` file should exist in the upstream repo (it is a downstream-only concept). The `resolve-image` action remains for downstream use via `assets/workspace/`.

## Actual Behavior

Upstream CI has a latent failure mode — it depends on a pre-published GHCR image (`resolve-image` reads `.vig-os`, validates the image exists, then jobs run inside that container). There is no guarantee the image has been published.

## Environment

- GitHub Actions (ubuntu-22.04 runners)
- GHCR (`ghcr.io/vig-os/devcontainer`)

## Additional Context

Affected files:
- `.vig-os` (repo root) — should not exist
- `assets/smoke-test/.vig-os` — should not exist (installer creates it)
- `.github/workflows/sync-issues.yml` — uses `resolve-image` + `container:`
- `.github/workflows/sync-main-to-dev.yml` — uses `resolve-image` + `container:`

The `resolve-image` action itself and `assets/workspace/.github/actions/resolve-image/` are correct — they serve downstream consumers.

## Possible Solution

1. Remove `.vig-os` from repo root
2. Remove `assets/smoke-test/.vig-os`
3. In `sync-issues.yml` and `sync-main-to-dev.yml`: drop the `resolve-image` job and `container:` directive; add `setup-env` steps to install tools natively
4. Keep `resolve-image` and `assets/workspace/.github/actions/resolve-image/` intact for downstream repos

## Changelog Category

Fixed

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
