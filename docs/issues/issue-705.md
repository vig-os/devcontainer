---
type: issue
state: closed
created: 2026-06-25T12:12:28Z
updated: 2026-07-01T11:17:46Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/705
comments: 1
labels: bug, priority:high, area:image
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:02.442Z
---

# [Issue 705]: [[BUG] flake.nix bakes WIP image tag 'nix-wt634' — guard before cutover](https://github.com/vig-os/devkit/issues/705)

## Problem
`flake.nix:426` sets `tag = "nix-wt634";` — a discovery tag from epic #625 work. The downstream docker-compose template pulls `ghcr.io/vig-os/devcontainer:${DEVCONTAINER_VERSION:-latest}`, so shipping this WIP tag to `main` produces a mislabeled/unresolvable image.

## Recommendation
Replace with the versioned/`latest` scheme, or explicitly defer to the #639 cutover and add a CI or pre-commit guard that fails if a `nix-wt*` tag is present on `main`.

## Context
Found during the state-of-the-repo review of #670 (epic #625). Pre-merge cleanup; relates to #639 (publish-cutover gate).

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:17 AM_

Resolved on `dev`. The discovery image tag is no longer a WIP `nix-wt*` value — `flake.nix` now bakes `tag = "nix-dev"` via PR #713 (`build(image): tag the discovery image nix-dev to match CI`). The versioned/`:latest` scheme is owned by the gated publish-cutover #639. Closing the baked-tag defect; if a hard CI guard that fails on a stray `nix-wt*`/discovery tag reaching a release is still wanted, that belongs with #639.

