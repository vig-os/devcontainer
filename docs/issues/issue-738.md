---
type: issue
state: closed
created: 2026-06-29T10:21:23Z
updated: 2026-06-30T07:42:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/738
comments: 1
labels: bug, priority:medium, area:workspace, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:55.974Z
---

# [Issue 738]: [[BUG] install.sh --mode direnv --force overwrites populated consumer files (pyproject.toml, .devcontainer/)](https://github.com/vig-os/devkit/issues/738)

## Description

Running `install.sh --mode direnv --version <v> --skip-pull --podman --force <repo>` on an **already-populated** consumer repo is destructive: in `direnv` mode it deploys the full workspace template over the project. Observed:
- **exoma-ch/brother-printer**: overwrote the real `pyproject.toml` (replaced the uv-workspace with a generic scaffold), deleted tracked `.devcontainer/{devcontainer.json,README.md,CHANGELOG.md,docker-compose.project.yaml}`, injected `tests/test_example.py`.
- **vig-os/scitadel**: preserved its own `flake.nix`/`.envrc` (scaffold-once guarantee held — good) but pruned `.devcontainer/` and then errored at `just sync` (the pruned justfile has no `sync` recipe).

`PRESERVE_FILES` protects `flake.nix`/`.envrc`/README/LICENSE/`justfile.project` but **not** `pyproject.toml` or `.devcontainer/*`, so a re-init/upgrade to add the direnv stub clobbers real project files.

Minor related: `install.sh` also prints `warn: User configuration script not found at .../copy-host-user-conf.sh` even when that script exists (seen on sync-issues-action) — a misleading non-fatal warning.

## Steps to Reproduce

`bash install.sh --mode direnv --version dev --skip-pull --podman --force <existing-python-repo>` → inspect `git status` (pyproject.toml overwritten, `.devcontainer/*` deleted).

## Expected Behavior

`--mode direnv` on an existing repo should only add the Nix/direnv stub (`flake.nix`, `.envrc`, `.vig-os`) and never overwrite `pyproject.toml` or delete a populated `.devcontainer/`, or it should refuse/warn loudly before clobbering.

## Actual Behavior

Real project files overwritten/deleted as above.

## Environment

- `install.sh` from `feature/625-nix-claude-migration` @ 8f778f5; Podman 5.8.2; NixOS host.

## Possible Solution

In `--mode direnv`, scope the scaffold to the Nix stub only (don't rsync `pyproject.toml`/`.devcontainer/`), expand `PRESERVE_FILES` to cover `pyproject.toml`, and detect/skip an existing populated `.devcontainer/`. Fix the spurious `copy-host-user-conf.sh` warning.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #741 (2c4e2cd) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

