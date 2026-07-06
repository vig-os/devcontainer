---
type: issue
state: open
created: 2026-06-24T10:59:40Z
updated: 2026-06-24T10:59:40Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/674
comments: 0
labels: chore, priority:medium, area:ci, area:image
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:58.817Z
---

# [Issue 674]: [[CHORE] Nix flake quality gates: nixfmt formatter + nix flake check in CI](https://github.com/vig-os/devcontainer/issues/674)

### Chore Type

CI / Build change

### Description

`flake.nix` (≈396 lines) is now the toolchain SSoT, but the flake itself is
ungated:

- **No formatter**: there is no `formatter` flake output and no nix formatter in
  the pre-commit hooks, so `flake.nix` can drift in style with nothing to catch
  it.
- **No checks / no `nix flake check` in CI**: there is no `checks` output and CI
  never runs `nix flake check`; the flake is only validated implicitly by
  `nix build .#devcontainerImage`. Eval errors or dev-shell/image drift are only
  caught late (or not at all).

Add lightweight quality gates so the SSoT stays formatted and evaluable.

### Acceptance Criteria

- [ ] `flake.formatter.<system>` is set (e.g. `nixfmt-rfc-style`) and `nix fmt`
      is idempotent on `flake.nix`
- [ ] A nixfmt pre-commit hook fails on unformatted `*.nix`
- [ ] `flake.checks.<system>` exposes at least flake evaluation + the existing
      dev-shell parity test (`tests/test_flake_devshell.py`)
- [ ] `nix flake check` runs in CI (`.github/workflows/ci.yml`, project-checks)
      and fails on format/parity drift
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

### Implementation Notes

Target files: `flake.nix`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
Keep CI edits confined to `ci.yml` — the sibling in-container smoke-test issue
edits `nix-image.yml` — so the two follow-up PRs do not conflict on a shared
workflow file.

### Related Issues

Part of #625.

### Priority

Medium

### Changelog Category

Added

