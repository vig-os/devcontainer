---
type: issue
state: closed
created: 2026-06-24T18:27:32Z
updated: 2026-06-30T07:42:19Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/701
comments: 1
labels: bug, priority:medium, area:ci, area:testing
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:03.219Z
---

# [Issue 701]: [[BUG] Integration tests run the published image (DEVCONTAINER_VERSION), not the freshly-built one](https://github.com/vig-os/devkit/issues/701)

## Description

The integration suite (`tests/test_integration.py`, e.g. `TestDevContainerCLI::test_git_commit_ssh_signature`) scaffolds a workspace **from the freshly-built image** (`TEST_CONTAINER_TAG`), but then runs the devcontainer itself from a **different, published image** — whichever tag `DEVCONTAINER_VERSION` resolves to. So the job validates *fresh scaffolding running inside an old published image*, not the image being built.

This is a latent quirk that surfaced while fixing #697/#698 on PR #670: it has no effect as long as the scaffolded config is self-contained, but any change that makes the scaffold depend on the image's toolchain breaks against the stale image.

## Root cause

- The scaffolded `assets/workspace/.devcontainer/docker-compose.yml` pins the runtime image as `image: ghcr.io/vig-os/devcontainer:${DEVCONTAINER_VERSION:-latest}`.
- `DEVCONTAINER_VERSION` comes from `.vig-os` (currently `0.3.9`), baked into the image and written to `.devcontainer/.env` by `initialize.sh`.
- Nothing in the test harness (`tests/conftest.py` `_run_devcontainer_up` / `devcontainer_up`) overrides `DEVCONTAINER_VERSION` to the freshly-built `TEST_CONTAINER_TAG`.
- Net effect: `init-workspace.sh` runs from the fresh image (so the scaffold is fresh), but `devcontainer up` (compose) pulls the published `:0.3.9` image for the actual container.

## Evidence (from PR #670)

#699 converted the scaffolded `ruff`/`typos` pre-commit hooks to `language: system` (resolved from the flake toolchain). The in-container `git commit` then failed with `Executable 'typos' not found`, because the running container was the published `:0.3.9` image, which has no `typos` binary. It was green before only because the hooks were self-contained (pre-commit-managed). Worked around in PR #670 by keeping the scaffolded hooks self-contained ([#697]), but the underlying test gap remains.

Separately, pointing the test at the **fresh Nix image** (`DEVCONTAINER_VERSION=<test tag>`) fails earlier: `post-create.sh` aborts on `cat /etc/os-release` because the Nix image is not an FHS distro — so the fresh image is not yet integration-ready.

## Proposed work

1. Make the integration harness run the devcontainer from the **image under test**: override `DEVCONTAINER_VERSION` (or the compose `image:`) to `TEST_CONTAINER_TAG` in `_run_devcontainer_up`/`devcontainer_up` (compose reads the shell env over `.env`).
2. Fix the Nix image's `post-create`/`os-release` incompatibility so it can actually be brought up by the devcontainer CLI (the `/etc/os-release` probe and any other FHS assumptions in `post-create.sh`).
3. Re-run the integration suite against the fresh image and remove any compensating workarounds that only exist because the published image was used.

## Acceptance criteria

- [ ] Integration tests run the devcontainer from the freshly-built image (`TEST_CONTAINER_TAG`), not the published `DEVCONTAINER_VERSION`
- [ ] The Nix image comes up cleanly under `devcontainer up` (no `os-release`/FHS failures in `post-create`)
- [ ] `TestDevContainerCLI::test_git_commit_ssh_signature` (and the rest of the suite) pass against the fresh image
- [ ] Document the image-selection behaviour for integration tests

## Notes

- Discovered fixing #697/#698 on PR #670; sub-issue of the Nix migration epic #625.
- Once (2) lands, the scaffolded config could even be reconsidered (the decoupling in #697 is the current compensating control).

Refs: #625

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #702 (baa4637) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

