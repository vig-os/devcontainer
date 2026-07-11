---
type: issue
state: closed
created: 2026-07-04T20:34:13Z
updated: 2026-07-08T07:41:24Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/854
comments: 1
labels: feature, priority:medium, area:ci, area:workspace, effort:large
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:36.062Z
---

# [Issue 854]: [[FEATURE] Nix-direct (direnv-mode) CI lane + version-skew hardening for shipped workflows](https://github.com/vig-os/devkit/issues/854)

## Context

The 0.4.0-rc1 smoke-test failure (#852) prompted a full audit of the CI glue the workspace scaffold ships to consumers (`assets/workspace/.github/**`, justfile layering, hook runner wiring). The immediate defect is fixed (#852: `.vig-os` pin honors `install.sh --version`), but the audit surfaced structural gaps that need their own cycle — most likely alongside or after the devkit rename (#781).

## A. Nix-direct CI lane (the main feature)

"direnv mode" today is **local-only**: `init-workspace.sh` prunes `.devcontainer/` but ships all 13 workflows unchanged, so a direnv consumer's CI still runs every job inside `container: ghcr.io/vig-os/devcontainer:<pin>` and hard-depends on `.vig-os` — if the consumer (reasonably) deletes it, `resolve-image` hard-fails and bricks 9 of 13 workflows (ci, sync-issues, renovate-changelog-build, release*, promote-release, sync-main-to-dev; only codeql/scorecard/renovate-changelog-commit/release-extension survive).

A nix-direct lane should mirror the parent repo's own `project-checks` job (`.github/workflows/ci.yml:168-221`): host runner → install-nix + cachix composite → `nix develop -c just sync|precommit|test` (the dev-shell provides prek/ruff/uv from the flake SSoT), dropping the container-only `UV_PROJECT_ENVIRONMENT` / `PREK_HOME` env. Open design questions: mode-conditional workflow scaffolding vs one workflow with a mode matrix; what the smoke test covers (today it exercises only the devcontainer mode).

## B. Version-skew hardening (defects found by the audit)

1. **No CI-wired skew guard**: `version-check.sh` runs only in the interactive container lifecycle (`post-attach.sh:26`, `|| true`); no workflow compares scaffold generation vs `DEVCONTAINER_VERSION`. The `resolve-image` action validates manifest *existence* only — no minimum-version floor, no tool probe. A `command -v prek` first-step guard in the lint job (with an actionable error) would have turned today's opaque failure into a one-line diagnosis.
2. **`prepare-release.yml:62-73` forks the resolver**: inline awk parse with a silent `latest` fallback — diverges from the shared `resolve-image` action (which hard-fails). Unify.
3. **Old-scaffold + new-image breakage is undocumented**: old `just precommit` = `uv run pre-commit run --all-files`; `pre-commit` was dropped from image+venv in 0.4.0 (#778). Needs a release-notes/MIGRATION callout.
4. **`justfile.devc devc-upgrade` curls `install.sh` from `main`** — upgrades the scaffold to HEAD regardless of the pin the consumer keeps; itself a skew generator.
5. **Shell-settings drift in direnv mode**: `set shell := ["bash","-euo","pipefail","-c"]` lives in the devc-managed `justfile.devc:6`; absent in direnv mode, identical `justfile.project` recipes run under `sh -cu` without pipefail. Move to the root justfile.
6. **Stale Debian-era doc**: `docs/container-ci-quirks.md:41-43` still describes a `uv run bandit` pre-commit hook that no longer exists and names the wrong runner.
7. **`init-precommit.sh:5` hard-codes `/workspace/{{SHORT_NAME}}`** — derive from the script location.
8. **Private-image consumers**: `resolve-image` probes with unauthenticated `docker manifest inspect` (stderr swallowed) and no `container:` block declares `credentials:` — public-image-only today, opaque failure otherwise.

## Scope

- Not 0.4.0-blocking: the release-blocking chain (#842/#847/#849/#852) is fixed on `release/0.4.0`.
- Target: devkit-1.0.0 rename cycle (#781) or the cycle after — the rename already touches the entire `assets/workspace/` scaffold, so the two blast radii overlap.

Refs: #852, #781
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:41 AM_

Delivered by #923 (merged to `dev` on 2026-07-07). Closing as complete for milestone 0.5.

