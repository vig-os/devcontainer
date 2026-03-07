---
type: issue
state: open
created: 2026-03-06T19:11:47Z
updated: 2026-03-06T19:11:47Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/227
comments: 0
labels: chore, area:workflow, effort:small
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:38.092Z
---

# [Issue 227]: [[CHORE] Add Nix flake devShell for reproducible host tooling](https://github.com/vig-os/devcontainer/issues/227)

### Chore Type

Configuration change

### Description

Host development setup relies on `just init` / `requirements.yaml` which installs tools imperatively and has no way to guarantee PATH availability for all consumers (pre-commit hooks, Claude Code, CI-like local runs).

Add a `flake.nix` with a `devShell` that declares all host-side tools from `requirements.yaml`. Combined with `direnv` (`.envrc` with `use flake`), every maintainer gets identical tooling with zero manual steps.

### Acceptance Criteria

- [ ] `flake.nix` with devShell containing: just, uv, gh, git, jq, tmux, hadolint, taplo, shellcheck, nodejs (for bats/devcontainer CLI)
- [ ] `.envrc` with `use flake` for automatic activation via direnv
- [ ] `nix develop` provides all tools on PATH
- [ ] Pre-commit hooks pass without manual installs
- [ ] Document in CONTRIBUTE.md as the recommended setup method

### Implementation Notes

- User already has Nix + Home Manager in `~/dotfiles/`
- `requirements.yaml` stays as SSoT for tool list and container installs
- `flake.nix` is the host-side complement
- Keep `just init` as fallback for non-Nix users

### Related Issues

Unblocks #226 (taplo binary not found locally)

### Priority

Medium

### Changelog Category

No changelog needed
