---
type: issue
state: closed
created: 2026-06-24T09:24:47Z
updated: 2026-06-30T07:41:57Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/671
comments: 1
labels: feature, area:workspace, area:workflow, semver:minor
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:09.075Z
---

# [Issue 671]: [feat(scripts): make just init Nix-first; retire requirements.yaml](https://github.com/vig-os/devkit/issues/671)

Tracking: #625

## Context

Epic #625 made `flake.nix`'s `devTools` list the single source of truth for the
toolchain, provisioned via `nix develop` / `direnv allow` (#631, #632, #633). It
decommissioned the Debian image path (#642) and moved CI to flake provisioning
(#632). But the **contributor bootstrap was never touched**: `just init` →
`scripts/init.sh` is still a ~680-line OS-detecting installer driven by
`scripts/requirements.yaml` — a 14-tool list with per-OS apt/brew/dnf/apk/curl
install commands. That file is now a **second toolchain SSoT** that already drifts
from `flake.nix devTools` (22+ tools), violating the SSoT principle. No existing
sub-issue covers reworking `just init`.

## Scope

**In:**
- Rewrite `scripts/init.sh` into a **Nix-first prerequisite gate + one-time project
  bootstrap**: gate on `nix` + `direnv` (with install guidance) and on being inside
  the dev-shell; then bootstrap `uv sync --frozen --all-extras`, git hooks path,
  commit-message template, and `pre-commit install-hooks`; advisory `podman info` and
  `gh auth status` checks (probe + guide, never install).
- Delete `scripts/requirements.yaml`; make `flake.nix devTools` the sole toolchain SSoT.
- Repoint docs: trim `docs/generate.py` (drop requirements loader/table/install
  functions + context keys) and rewrite the `CONTRIBUTE.md.j2` "Requirements" section
  into "Prerequisites: Nix + direnv + a working host container runtime"; regenerate
  `CONTRIBUTE.md`.
- Update the `justfile` `init` recipe comment.

**Out:**
- Changing the flake `shellHook` (bootstrap stays in the recipe, not on every shell entry).
- Stale README base-image line and `verify-auth.sh` editor comment (separate cleanups).
- Auto-installing Nix or podman.

## Tasks

- [ ] RED: rewrite `tests/bats/init.bats` to the new gate/bootstrap contract; trim the
  requirements test classes in `tests/test_utils.py`
- [ ] GREEN: rewrite `scripts/init.sh`
- [ ] Delete `scripts/requirements.yaml`; trim `docs/generate.py`; rewrite
  `docs/templates/CONTRIBUTE.md.j2`; regenerate `CONTRIBUTE.md` via `just docs`
- [ ] Update `justfile` `init` recipe comment + `CHANGELOG.md` Unreleased (Changed, Removed)

## Acceptance criteria

- `scripts/requirements.yaml` no longer exists; `grep -r requirements.yaml` is clean.
- `just init` exits non-zero with install guidance when Nix/direnv are absent, and
  performs project bootstrap idempotently when inside the dev-shell.
- Docs state "Prerequisites: Nix + direnv + host podman"; the toolchain is sourced
  from `flake.nix devTools`.
- `bats tests/bats/init.bats`, `uv run pytest tests/test_utils.py`, `just docs`, and
  the full `just test` suite are green.

## Dependencies

- **Depends-on:** #631, #632, #633 (flake SSoT + direnv onboarding) — merged on the epic branch.
- **Blocks:** none.

## Files

- `scripts/init.sh`
- `scripts/requirements.yaml` (delete)
- `docs/generate.py`
- `docs/templates/CONTRIBUTE.md.j2`
- `CONTRIBUTE.md` (regenerated)
- `tests/bats/init.bats`
- `tests/test_utils.py`
- `justfile`

## Test notes

- Strict TDD: failing tests first (`test:` commit), then implementation.
- Confirm `just test` parity (testinfra + bats + renovate validation) before PR.
- PR targets the epic branch `feature/625-nix-claude-migration`.

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:41 AM_

Resolved by #672 (aef2fca) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

