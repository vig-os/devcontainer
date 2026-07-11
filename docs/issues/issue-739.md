---
type: issue
state: closed
created: 2026-06-29T10:21:24Z
updated: 2026-06-30T07:42:31Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/739
comments: 1
labels: chore, priority:low, area:image
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:55.630Z
---

# [Issue 739]: [[CHORE] Bake /etc/nix/nix.conf enabling nix-command/flakes for on-demand 'nix shell'](https://github.com/vig-os/devkit/issues/739)

## Description

The image bundles Nix (2.34.7) but ships **no `/etc/nix/nix.conf`**, so `nix-command`/`flakes` are disabled by default. Ad-hoc on-demand tooling (`nix shell nixpkgs#cargo`, `nix run …`) — the recommended way to pull a toolchain the minimal image doesn't bake — fails unless the user passes `--extra-experimental-features "nix-command flakes"`. The default registry also resolves `nixpkgs` to **unstable**, drifting from the image's pinned `nixos-26.05`.

## Steps to Reproduce

In `ghcr.io/vig-os/devcontainer:dev`: `nix shell nixpkgs#cargo -c cargo --version`.

## Expected Behavior

`nix shell`/`nix run` work out of the box for ad-hoc on-demand tools.

## Actual Behavior

```
error: experimental Nix feature 'nix-command' is disabled; add '--extra-experimental-features nix-command' to enable it
```

## Environment

- **Image**: `ghcr.io/vig-os/devcontainer:dev` (from `feature/625-nix-claude-migration` @ 8f778f5); Podman 5.8.2; NixOS host.

## Possible Solution

Bake `/etc/nix/nix.conf` with `experimental-features = nix-command flakes` (and consider pinning the flake registry `nixpkgs` to the image's `nixos-26.05` to avoid unstable drift for on-demand tools). Enables the "source extra toolchains on-demand" model for the minimal image.

## Changelog Category

Added

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #742 (0aa5125) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

