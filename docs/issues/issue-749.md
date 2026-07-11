---
type: issue
state: closed
created: 2026-06-29T14:00:08Z
updated: 2026-06-30T07:42:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/749
comments: 1
labels: bug, priority:medium, area:image, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:54.932Z
---

# [Issue 749]: [[BUG] In-image nix.conf lacks build-users-group= — on-demand nix local builds fail (no nixbld group)](https://github.com/vig-os/devkit/issues/749)

## Description

The Nix-built image bakes `/etc/nix/nix.conf` with `experimental-features = nix-command flakes` + `accept-flake-config = true` (#739), but does **not** set `build-users-group =`. The in-image Nix runs as **root, single-user, daemonless**, with `/nix/store` owned `root:root` and no `nixbld` group. So any on-demand `nix shell` / `nix develop` that needs a **local build** (rather than a pure binary-cache substitution) aborts with:

```
error: the group 'nixbld' specified in 'build-users-group' does not exist
```

This breaks the "source extra toolchains on-demand" story for any flake that builds something locally. Cache-substitutable closures work (e.g. `nix shell nixpkgs#cargo` succeeds), which masks the gap until a real local build is needed.

## Steps to Reproduce

In `ghcr.io/vig-os/devcontainer:dev` (a fresh store), run a flake whose dev-shell assembles local derivations — e.g. a `rust-overlay` toolchain (the `scitadel` consumer):

```
nix develop   # in a rust-overlay project
→ error: the group 'nixbld' specified in 'build-users-group' does not exist
```

Confirmed cause/fix: the same command with `--option build-users-group ""` succeeds and builds the toolchain.

## Expected Behavior

In-image on-demand Nix can perform local builds; `nix develop`/`nix shell` work for flakes that aren't fully cache-substitutable.

## Actual Behavior

Local builds abort on the missing `nixbld` group; only cache-substitutable on-demand paths work.

## Environment

- **Image**: `ghcr.io/vig-os/devcontainer:dev` (built from `feature/625-nix-claude-migration`)
- **Runtime**: Podman 5.8.2 — **OS**: NixOS host — **Arch**: AMD64
- Surfaced by the `scitadel` (Rust/rust-overlay) consumer in the cross-stack sweep.

## Possible Solution

Add `build-users-group =` (empty) to the baked `/etc/nix/nix.conf` (the `buildLayeredImage` bootstrap heredoc that #739 added in `flake.nix`). The empty value is the standard setting for rootless/single-user in-container Nix and makes root build directly without dropping to a build-users group. Extends #739; complements the on-demand-toolchain model.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #750 (046ba4f) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

