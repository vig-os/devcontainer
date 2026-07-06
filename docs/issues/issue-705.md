---
type: issue
state: open
created: 2026-06-25T12:12:28Z
updated: 2026-06-25T12:12:28Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/705
comments: 0
labels: bug, priority:high, area:image
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:53.779Z
---

# [Issue 705]: [[BUG] flake.nix bakes WIP image tag 'nix-wt634' — guard before cutover](https://github.com/vig-os/devcontainer/issues/705)

## Problem
`flake.nix:426` sets `tag = "nix-wt634";` — a discovery tag from epic #625 work. The downstream docker-compose template pulls `ghcr.io/vig-os/devcontainer:${DEVCONTAINER_VERSION:-latest}`, so shipping this WIP tag to `main` produces a mislabeled/unresolvable image.

## Recommendation
Replace with the versioned/`latest` scheme, or explicitly defer to the #639 cutover and add a CI or pre-commit guard that fails if a `nix-wt*` tag is present on `main`.

## Context
Found during the state-of-the-repo review of #670 (epic #625). Pre-merge cleanup; relates to #639 (publish-cutover gate).

Refs: #625
