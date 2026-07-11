---
type: issue
state: closed
created: 2026-06-29T10:21:18Z
updated: 2026-06-30T07:42:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/735
comments: 1
labels: bug, priority:high, area:image, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:57.059Z
---

# [Issue 735]: [[BUG] Nix image missing /root/assets/workspace/.venv — consumer post-create.sh aborts on first line](https://github.com/vig-os/devkit/issues/735)

## Description

The Nix-built image (`ghcr.io/vig-os/devcontainer`) sets `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` to `/root/assets/workspace/.venv` but **does not create that venv** (the old Debian image did). The 0.3.x consumer `post-create.sh` template starts with `sed -i … /root/assets/workspace/.venv/bin/activate`, which fails, and with `set -euo pipefail` the whole post-create aborts (exit 2) — so git setup, gh auth, pre-commit install, and `just sync` never run.

Reproduced on **4/4 non-TypeScript consumers** tested (devcontainer-smoke-test, exoma-ch/brother-printer, vig-os/scitadel, exo-pet/playground-carlos). TypeScript consumers have a different post-create (no `.venv` sed) and are unaffected.

## Steps to Reproduce

1. `just build` → `ghcr.io/vig-os/devcontainer:dev`.
2. Run any Python/shell consumer in it and execute `.devcontainer/scripts/post-create.sh`.

## Expected Behavior

The baked `/root/assets/workspace/.venv` exists (as in the published 0.3.x image), so post-create's `sed`/`.bashrc` PATH/`just sync` steps work; or the image stops advertising `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` to a path it doesn't ship.

## Actual Behavior

```
sed: can't read /root/assets/workspace/.venv/bin/activate: No such file or directory
=== post-create.sh exit: 2 ===
```
`/root/assets/workspace` is a store-symlinked template with no `.venv`. The flake bootstrap layer creates `/opt/pre-commit-cache`, `/workspace`, `/usr/local/bin`, `/tmp` — but not the `.venv`.

## Environment

- **Image**: `ghcr.io/vig-os/devcontainer:dev` (built from `feature/625-nix-claude-migration` @ 8f778f5)
- **Runtime**: Podman 5.8.2 — **OS**: NixOS host — **Arch**: AMD64

## Possible Solution

Either bake the pre-built venv into the image (restore parity with the Debian image), or pre-create it in the flake bootstrap layer, or make the consumer `post-create.sh` template tolerate a missing venv (create-then-activate) and not point `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` at a non-existent path.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #745 (c2c8329) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

