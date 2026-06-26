---
type: issue
state: open
created: 2026-06-24T12:27:01Z
updated: 2026-06-24T12:27:01Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/683
comments: 0
labels: bug, priority:high, area:workspace, effort:medium, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:57.511Z
---

# [Issue 683]: [[BUG] just init fails on NixOS hosts: uv downloads a generic CPython NixOS can't execute](https://github.com/vig-os/devcontainer/issues/683)

## Description

On a **NixOS host**, onboarding via `direnv allow` + `just init` fails during the `uv sync` bootstrap step. The Nix dev-shell deliberately ships no Python on `PATH` and points uv at upstream's download metadata (`UV_PYTHON_DOWNLOADS_JSON_URL`) so `uv sync` fetches a *managed* CPython matching `requires-python` (`>=3.14,<3.15`). That downloaded interpreter is a generic, dynamically-linked ELF — which NixOS cannot execute out of the box (no `/lib` `ld-linux`, see https://nix.dev/permalink/stub-ld). `uv sync` therefore aborts and `just init` exits non-zero.

The dev-shell itself loads fine; only the project-venv bootstrap (`uv sync`) is broken, and only on NixOS hosts. FHS hosts (Ubuntu, etc.) are unaffected because they can run the downloaded interpreter.

Sub-issue of #625 (Nix migration master). Surfaced while testing onboarding on a NixOS host.

## Steps to Reproduce

On a NixOS host:

1. `git checkout feature/625-nix-claude-migration`
2. `direnv allow`  (dev-shell loads: `devcontainer dev environment loaded (nix)`)
3. `just init`

## Expected Behavior

`just init` materializes the project venv from the lockfile and completes the bootstrap on a NixOS host, the same as on FHS hosts.

## Actual Behavior

```
ℹ  Syncing the project environment from the lockfile...
error: Querying Python at `/home/<user>/.local/share/uv/python/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14` failed with exit status exit status: 127

[stderr]
Could not start dynamically linked executable: /home/<user>/.local/share/uv/python/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
✗  Failed to sync project dependencies
error: recipe `init` failed on line 62 with exit code 1
```

## Environment

- **OS**: NixOS (host running the dev-shell directly via direnv, not the container)
- **Provisioning**: Nix flake dev-shell (`direnv allow` / `nix develop`)
- **Branch**: `feature/625-nix-claude-migration`
- **Architecture**: x86_64

## Additional Context

- The relevant dev-shell mechanism is `uvPythonDownloadsJsonUrl` / `UV_PYTHON_DOWNLOADS_JSON_URL` in `flake.nix` (`mkProjectShell`), added in #632 / #666 so the stripped nixpkgs uv can fetch a managed CPython. The accompanying comment notes the dev-shell carries no Python on PATH by design.
- The **image** path already avoids this: it bakes a Nix-built interpreter (`pythonEnv`) and sets `UV_PYTHON=${python}/bin/python3.14` + `UV_PYTHON_DOWNLOADS=never`, so it never downloads a generic CPython.
- Failure originates at `scripts/init.sh` `uv sync --frozen --all-extras`.
- Related onboarding/scripts work: #671, #641.

## Possible Solution

Have the dev-shell use a Nix-provided interpreter instead of (or in addition to) a downloaded managed CPython, mirroring the image path so it works on NixOS and FHS hosts alike. For example, in `mkProjectShell` provide a Nix CPython (matching `requires-python`) and set `UV_PYTHON` to it with `UV_PYTHON_DOWNLOADS=never`, so `uv sync` resolves the store interpreter rather than fetching a generic one. Must remain compatible with non-NixOS hosts. (One implementer to confirm the exact approach vs. relying on the host's nixpkgs python.)

## Acceptance Criteria

- [ ] `just init` completes successfully on a NixOS host (dev-shell path), with the project venv materialized from the lockfile.
- [ ] Onboarding remains working on FHS hosts (no regression).
- [ ] No generic dynamically-linked CPython is downloaded by `uv sync` in the dev-shell on NixOS.
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

**Changelog Category:** Fixed
