---
type: issue
state: closed
created: 2026-06-29T10:21:21Z
updated: 2026-07-02T11:41:40Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/737
comments: 1
labels: bug, priority:medium, area:image, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:56.334Z
---

# [Issue 737]: [[BUG] Image Python 3.14.4 vs consumers pinning ==3.14.6 — uv sync fails](https://github.com/vig-os/devkit/issues/737)

## Description

The image ships **CPython 3.14.4**, but consumers can pin an exact patch (e.g. `devcontainer-smoke-test` has `requires-python == 3.14.6`). `uv sync` then refuses the image interpreter and fails. The image's Python patch version should track what consumers/templates expect (or templates should pin a range, not `==`).

## Steps to Reproduce

In `ghcr.io/vig-os/devcontainer:dev`, in `devcontainer-smoke-test`: `uv sync` (or `just sync`).

## Expected Behavior

`uv sync` resolves against the baked interpreter.

## Actual Behavior

```
error: The requested interpreter resolved to Python 3.14.4, which is incompatible
with the project's Python requirement: `==3.14.6`
```
(The published 0.3.9 image shipped 3.14.6.)

## Environment

- **Image**: `ghcr.io/vig-os/devcontainer:dev` (from `feature/625-nix-claude-migration` @ 8f778f5)
- **Runtime**: Podman 5.8.2 — **OS**: NixOS — **Arch**: AMD64

## Possible Solution

Bump the flake's pinned CPython to the patch consumers expect (3.14.6) and keep it in sync, and/or change the workspace template `requires-python` to a compatible range (`>=3.14,<3.15`) rather than an exact `==` pin.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on July 2, 2026 at 11:41 AM_

Resolved in #666 (commit c7839602): image/template pyprojects relaxed from `==3.14.6` to `>=3.14,<3.15`, so `uv sync` resolves against the baked CPython 3.14.4. (If the standalone `devcontainer-smoke-test` repo still hard-pins `==3.14.6`, that fix belongs in that repo.) Closing.

