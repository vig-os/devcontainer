---
type: issue
state: closed
created: 2026-06-29T10:21:25Z
updated: 2026-06-30T07:42:32Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/740
comments: 1
labels: bug, priority:low, area:image, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:55.288Z
---

# [Issue 740]: [[BUG] Image has no docker binary (podman only) though compose/env reference docker](https://github.com/vig-os/devkit/issues/740)

## Description

The image ships a **`podman`** client but **no `docker`** binary, while the consumer `.devcontainer/docker-compose.yml` mounts the socket at `/var/run/docker.sock` and sets `DOCKER_HOST`/`CONTAINER_HOST`. Docker-out-of-Docker works because `podman` honors `DOCKER_HOST` (verified: sibling `hello-world` container spawned from inside `:dev`), but any recipe/script that invokes `docker` literally will fail with `command not found`.

## Steps to Reproduce

In `ghcr.io/vig-os/devcontainer:dev`: `command -v docker` → empty; `docker ps` → not found. `podman ps` (with socket + `DOCKER_HOST`) → works.

## Expected Behavior

Either a `docker` shim/alias pointing at `podman`, or documented guidance that consumers must use `podman` (and recipes must probe `command -v podman`).

## Actual Behavior

DooD works via `podman` only; `docker`-literal calls fail. Consumer recipes that probe `podman` first are unaffected.

## Environment

- **Image**: `ghcr.io/vig-os/devcontainer:dev` (from `feature/625-nix-claude-migration` @ 8f778f5); Podman 5.8.2; NixOS host.

## Possible Solution

Add a `docker → podman` shim in the image (nixpkgs `podman` provides a `docker` compat wrapper option), or document the podman-only contract for DooD consumers.

## Changelog Category

Changed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #743 (fcbe02f) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

