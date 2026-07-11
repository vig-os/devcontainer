---
type: issue
state: closed
created: 2026-06-29T10:21:19Z
updated: 2026-06-30T07:42:36Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/736
comments: 1
labels: bug, priority:high, area:image, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:56.695Z
---

# [Issue 736]: [[BUG] Nix image can't run manylinux PyPI wheels (no /lib64 FHS loader, libstdc++ off-path) — breaks pre-commit + scientific stack](https://github.com/vig-os/devkit/issues/736)

## Description

The pure-Nix image cannot run **pre-compiled PyPI (manylinux) wheels / C-extensions** installed at runtime. Two missing pieces:
1. the FHS dynamic loader `/lib64/ld-linux-x86-64.so.2` does not exist in the image;
2. `libstdc++.so.6` exists in the store (`gcc-…-lib`) but is **not on the loader path** (`LD_LIBRARY_PATH` unset).

So any consumer that `uv`/`pip`-installs native code at runtime breaks. The image's *own* nix-built tools (ruff 0.15.14, etc.) are fine — only runtime-installed PyPI binaries fail.

This is the **image-side recurrence of #698** (which fixed the dev-shell case on NixOS via a NixOS-gated `LD_LIBRARY_PATH`), and it also defeats consumer pre-commit configs that pin PyPI versions (the #697 `language: system` conversion only applies to *this* repo's config, not consumers').

## Steps to Reproduce

In `ghcr.io/vig-os/devcontainer:dev`, in a Python consumer after `uv sync`:
- `uv run pre-commit run --all-files`, and `uv run pytest` on a project using numpy.

## Expected Behavior

Runtime-installed manylinux wheels (numpy/scipy/pandas/h5py; pre-commit hooks pinned to PyPI `pymarkdown`/`ruff`/`typos`) load and run.

## Actual Behavior

```
# pymarkdown hook
ImportError: libstdc++.so.6: cannot open shared object file: No such file or directory   # pyjson5 C-extension
# ruff / ruff-format / typos hooks (PyPI-pinned)
cannot execute: required file not found        # interp /lib64/ld-linux-x86-64.so.2 absent
# project tests
import numpy → ImportError (libstdc++.so.6 / loader)
```
Direct check: `ruff` (PyPI) requests interpreter `/lib64/ld-linux-x86-64.so.2` (absent); `/bin/ruff` (nix-built) works.

## Environment

- **Image**: `ghcr.io/vig-os/devcontainer:dev` (from `feature/625-nix-claude-migration` @ 8f778f5)
- **Runtime**: Podman 5.8.2 — **OS**: NixOS host — **Arch**: AMD64
- Confirmed on exoma-ch/brother-printer and exo-pet/playground-carlos (Python).

## Possible Solution

Give the image an FHS-compatible runtime for manylinux wheels: bundle **nix-ld** (or an FHS loader at `/lib64/ld-linux-x86-64.so.2`) and expose the common runtime libs (`libstdc++`, `libz`, `libgcc_s`, …) on the loader path. Mirror whatever final mechanism #698 uses, but at image scope (the image is Nix-but-not-NixOS, so the `/etc/NIXOS` gate never fires). Without this, every Python consumer's pre-commit and scientific stack break in-container.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #744 + #746 (586b50e, 3c3c93d) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

