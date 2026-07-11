---
type: issue
state: closed
created: 2026-06-29T07:55:56Z
updated: 2026-06-30T07:42:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/729
comments: 3
labels: bug, priority:medium, area:image, area:workspace, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:57.471Z
---

# [Issue 729]: [[BUG] Downstream mkProjectShell dev-shell omits bare python/python3 and pre-commit (image has them)](https://github.com/vig-os/devkit/issues/729)

## Description

When a downstream project consumes the toolchain via the flake-input / direnv path (`vigos.lib.mkProjectShell`, `nix develop`), the resulting dev-shell does **not** expose bare `python` / `python3` or `pre-commit` on `PATH`, even though the OCI image provides all three. `python` is reachable only via `uv run python`.

This is a dev-shell ↔ image parity gap for the *downstream* shell (mkProjectShell), distinct from the testinfra parity work in #666.

## Steps to Reproduce

1. Scaffold a direnv stub into a consumer (`install.sh --mode direnv ...`).
2. `nix develop --override-input vigos path:<local devcontainer> --command bash -c '...'`.
3. In the shell:
   - `command -v python` / `python3` → MISSING
   - `command -v pre-commit` → MISSING
   - `uv run python --version` → works (CPython 3.14.4 from the store)

## Expected Behavior

The downstream dev-shell exposes the same core tools as the image (at minimum `python3` and `pre-commit`), or this asymmetry is documented as intentional (uv-first Python, per-project pre-commit).

## Actual Behavior

Image: `python`, `python3`, `pre-commit` all present.
Downstream `mkProjectShell` dev-shell: none of the three on `PATH`; Python only via `uv run`.

## Environment

- **OS**: NixOS (host)
- **Container Runtime**: Podman 5.8.2 (image), `nix develop` (shell)
- **Image Version/Tag**: `dev` (built from `feature/625-nix-claude-migration`)
- **Architecture**: AMD64

## Additional Context

Found live-testing the direnv/flake-input mode vs `commit-action`. Related: #640 (downstream flake stub), #666 (image toolchain parity), #625 (master).

## Possible Solution

Either add `python3` + `pre-commit` to `mkProjectShell`'s base packages, or document the intended way to invoke them (`uv run`, project-local pre-commit) in `docs/NIX.md`.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 29, 2026 at 09:11 AM_

Reopening: PR #733's implementation (exposing the Nix store `python3` on the dev-shell PATH) regressed #698/#700 on FHS hosts — pre-commit then builds the `pymarkdown` hook env with the Nix interpreter, whose manylinux `pyjson5` wheel can't resolve `libstdc++` (the #700 `LD_LIBRARY_PATH` rescue is NixOS-gated per #703). Reverted on `feature/625-nix-claude-migration` (commit 8f778f5) to restore CI; a host-safe re-implementation is in progress.

---

# [Comment #2]() by [c-vigo]()

_Posted on June 29, 2026 at 09:26 AM_

## Deferring: scoped fix is unsound; needs a dedicated rework

The first implementation (PR #733, exposing the Nix store `python3` + `pre-commit` on the dev-shell PATH) regressed #698/#700 on FHS hosts and has been **reverted** on `feature/625-nix-claude-migration` (commit 8f778f5). CI is green again. Findings so a future fix doesn't repeat the dead ends:

### Root cause
On the FHS CI runner, pre-commit's manylinux-wheel hooks (`pymarkdown` → `pyjson5`, a C-extension needing `libstdc++.so.6`) are **meant to run under a uv-downloaded, FHS-compatible CPython** (see the `UV_PYTHON_DOWNLOADS_JSON_URL` / #632/#683 comment in `flake.nix`). Adding the Nix store `python3` to the dev-shell PATH made pre-commit pick **that** interpreter instead. The Nix python uses the Nix `ld-linux` (no `/etc/ld.so.cache`), so the manylinux wheel can't find `libstdc++` — and #700's `LD_LIBRARY_PATH` rescue is NixOS-gated (#703 forbids a global FHS export, which leaks the Nix `libstdc++`/`libm` into host `just`/bash → `GLIBC_ABI_DT_X86_64_PLT` crashes).

### Why a "scoped wrapper" cannot work (verified)
- **Wrapping the interpreter** (`makeWrapper python --prefix LD_LIBRARY_PATH`): a venv built from the wrapper symlinks `venv/bin/python3 → python3.14 → the real binary`, bypassing the wrapper. Confirmed locally: `LD_LIBRARY_PATH` is unset inside the venv. pre-commit's hook venv runs the real interpreter, not the wrapper.
- **RPATH-patching the interpreter**: `pyjson5.so` is `dlopen`'d and `DT_RUNPATH` is **non-transitive**, so the interpreter's RPATH is not consulted when resolving the extension's `libstdc++`.
- **Conclusion**: the only thing that delivers `libstdc++` to the hook process is `LD_LIBRARY_PATH` in its environment — i.e. a global/ancestor export, which is exactly the #703 leak. There is no clean per-process scoping.

### Viable directions for a dedicated fix
1. **Decouple pre-commit's hook interpreter from the dev-shell PATH python** — keep exposing `python3` for users, but ensure pre-commit's manylinux hooks still use the uv-downloaded/FHS CPython (e.g. pin the hook interpreter, or keep the store python off the name pre-commit resolves). Preferred; FHS-only-verifiable.
2. **Partial**: expose only `pre-commit` (does not add a store `python3` to PATH, so it won't hijack pre-commit's interpreter on CI) and document Python access via `uv run`. Caveat: a downstream FHS user invoking the **Nix** `pre-commit` directly (not `uv run pre-commit`) would still hit the libstdc++ issue.
3. **Make `pymarkdown` a non-manylinux hook** (the #697 `language: system` pattern) so no `pyjson5` wheel is built — blocked today because pymarkdown isn't in nixpkgs (per the #700 comment).

Any fix must be verified on the FHS CI runner (the failure does not reproduce on a NixOS host, where the #700 NixOS-gated injection masks it).

---

# [Comment #3]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #747 (a2f0e54) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

