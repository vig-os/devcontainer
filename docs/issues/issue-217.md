---
type: issue
state: open
created: 2026-03-04T07:00:18Z
updated: 2026-03-04T08:57:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/217
comments: 1
labels: refactor, area:workspace, area:workflow, effort:large, semver:minor
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-05T04:18:18.745Z
---

# [Issue 217]: [[REFACTOR] Reorganize scripts/ — project-specific vs shared vig-utils](https://github.com/vig-os/devcontainer/issues/217)

### Description

Split `scripts/` into two clearly separated blocks:

1. **Project-specific** — container build tooling that only applies to this repo. Stays in `scripts/`.
2. **Shared with downstream** — utilities shipped to every deployed workspace. Moves into `packages/vig-utils/` as modules (Python) or package data with wrapper entry points (shell).

Currently shared scripts are loose files in `scripts/` copied to `assets/workspace/.devcontainer/scripts/` via manifest. This creates:

- Unclear ownership (which scripts are build-only vs shared?)
- Duplicated copies in `assets/workspace/`
- No standard entry point mechanism for downstream consumers
- Pre-commit hooks that break in deployed workspaces (#161)

### Proposed split

**Stays in `scripts/` (project-specific):**

- `build.sh`, `prepare-build.sh`, `clean.sh`, `init.sh` — image build pipeline
- `sync_manifest.py`, `transforms.py` — workspace sync engine
- `manifest.toml`, `requirements.yaml` — build config
- `utils.py` — build helpers (sed-inplace, version patching)

**Moves into `packages/vig-utils/` (shared):**

Python modules (as vig-utils submodules with entry points):

- `gh_issues.py` — project dashboard
- `prepare-commit-msg-strip-trailers.py` — commit message hook
- `check-agent-identity.py` — agent identity check
- `check-pr-agent-fingerprints.py` — PR fingerprint check

Shell scripts (as package data with wrapper entry points):

- `resolve-branch.sh` — branch resolution helper
- `derive-branch-summary.sh` — branch summary derivation
- `check-skill-names.sh` — skill name validation
- `setup-labels.sh` — label provisioning

**Already in vig-utils (no move needed):**

- `validate_commit_msg.py`, `check_action_pins.py`, `prepare_changelog.py`, `agent_blocklist.py`

### Files / Modules in Scope

- `scripts/` (source of shared scripts to migrate)
- `packages/vig-utils/` (target for shared utilities)
- `packages/vig-utils/pyproject.toml` (new entry points)
- `scripts/manifest.toml` (update sync entries to point to vig-utils)
- `.pre-commit-config.yaml` (update hook entries to use vig-utils entry points)
- `justfile.base`, `justfile.gh`, `justfile.worktree` (update script references)
- `assets/workspace/.devcontainer/scripts/` (remove redundant copies)

### Out of Scope

- Functional changes to any script (pure reorganization)
- gh-issues rewrite (#145) — comes after the move
- CI workflow changes beyond updating script paths
- Publishing vig-utils to PyPI (#161 option 2)

### Invariants / Constraints

- `just gh-issues` continues to work end-to-end
- All pre-commit hooks pass in both this repo and deployed workspaces
- All `just` recipes that invoke shared scripts continue to work
- Existing tests pass without modification
- vig-utils remains installable as a local editable package

### Acceptance Criteria

- [ ] `scripts/` contains only project-specific build tooling
- [ ] All shared Python scripts are vig-utils submodules with CLI entry points
- [ ] All shared shell scripts are vig-utils package data with wrapper entry points
- [ ] `manifest.toml` entries updated (no more `scripts/*.py` -> `.devcontainer/scripts/` copies)
- [ ] Downstream workspaces can invoke shared tools via vig-utils entry points
- [ ] All `just` recipes and pre-commit hooks updated to new paths/entry points
- [ ] Redundant copies in `assets/workspace/.devcontainer/scripts/` removed
- [ ] All existing tests pass
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Changed

### Related Issues

- Subsumes #179 (move gh_issues.py into vig-utils)
- Subsumes #185 (make container scripts callable via PATH)
- Addresses part of #161 (vig-utils hooks in deployed workspace CI)
- Partially addresses #190 (synced justfiles referencing missing scripts)
- Tangentially related to #187 (path resolution in justfiles)
---

# [Comment #1]() by [c-vigo]()

_Posted on March 4, 2026 at 07:47 AM_

## Implementation Plan for Issue #217

### Scope and migration strategy

- Keep **project-specific tooling** in `scripts/`.
- Move **shared downstream utilities** into `packages/vig-utils`.
- Use a **compatibility-first** sequence: add vig-utils commands first, keep wrappers/shims for compatibility, switch callers, then remove redundant copies.
- Prefer **wrapper-first** for shared shell scripts in this issue; treat pure-Python rewrites as follow-up work unless trivial and behavior-identical.

### 1) Freeze script classification and caller map

- Confirm the project-specific set remains in `scripts/`: `build.sh`, `prepare-build.sh`, `clean.sh`, `init.sh`, `sync_manifest.py`, `transforms.py`, `manifest.toml`, `requirements.yaml`.
- Confirm the shared set to package in vig-utils:
  - Python: `gh_issues.py`, `prepare-commit-msg-strip-trailers.py`, `check-agent-identity.py`, `check-pr-agent-fingerprints.py`
  - Shell: `resolve-branch.sh`, `derive-branch-summary.sh`, `check-skill-names.sh`, `setup-labels.sh`
  - Utility module: `utils.py` (move reusable logic into vig-utils)
- Map all current references before editing:
  - `justfile.gh`
  - `justfile.worktree`
  - `.pre-commit-config.yaml`
  - `scripts/manifest.toml`

### 2) Add shared commands to vig-utils

- Extend `packages/vig-utils/pyproject.toml` with entry points for migrated shared commands.
- Add Python command modules under `packages/vig-utils/src/vig_utils`.
- Package shell scripts in vig-utils and expose Python wrapper entry points that execute packaged shell assets via `bash`, preserving argv/stdin/stdout/stderr and exit codes.
- Keep behavior equivalent (no feature changes), especially for repo-root assumptions currently based on `__file__` in migrated scripts.

### 3) Migrate `scripts/utils.py` into vig-utils (with shim)

- Create a reusable vig-utils module (for `substitute_in_file`, `sed_inplace`, `update_version_line`, and CLI dispatch) under `packages/vig-utils/src/vig_utils`.
- Update `scripts/transforms.py` imports to use the new vig-utils module.
- Keep `scripts/utils.py` as a compatibility shim delegating to vig-utils so existing build commands remain stable during migration.
- Optionally add a dedicated vig-utils entry point for these utilities while preserving existing `scripts/utils.py` CLI behavior.

### 4) Switch all root callers to vig-utils entry points/wrappers

- Update `justfile.gh` `gh-issues` command to invoke the new vig-utils command instead of `python3 scripts/gh_issues.py`.
- Update `justfile.worktree` recipes that call `resolve-branch.sh` and `derive-branch-summary.sh` to use vig-utils wrapper entry points.
- Update `.pre-commit-config.yaml` hook entries currently calling `scripts/*.sh` / `scripts/*.py` to call corresponding vig-utils entry points.

### 5) Update workspace sync manifest and transforms

- Update `scripts/manifest.toml` so shared utilities are sourced from vig-utils (or no longer mirrored as loose `.devcontainer/scripts/*` files when entry points are sufficient).
- Update transform rules in the same manifest that currently rewrite old `scripts/...` paths in synced pre-commit config.
- Re-run sync flow and verify generated outputs in `assets/workspace` remain valid.

### 6) Remove redundant copied shared scripts

- Remove obsolete files under `assets/workspace/.devcontainer/scripts` that are replaced by vig-utils entry points/wrappers.
- Ensure no remaining references in synced configs/justfiles still point to removed paths.

### 7) Verification and test plan

- Run targeted package tests in `packages/vig-utils/tests` for new modules/wrappers.
- Run `tests/test_utils.py` and any updated tests validating the `scripts/utils.py` compatibility shim.
- Run sync validation (`scripts/sync_manifest.py`) and confirm generated workspace files match expected command paths.
- Run relevant just/pre-commit checks impacted by path changes:
  - `just gh-issues`
  - worktree recipes invoking branch helpers
  - pre-commit hooks updated in `.pre-commit-config.yaml`
- Run lint on touched files and resolve any introduced diagnostics.

### Delivery notes

- Keep diffs minimal and traceable to #217 only.
- Preserve user-facing behavior; this issue is structural reorganization, not feature expansion.
- If any command cannot be safely migrated without behavior change, keep a temporary shim and schedule cleanup as a follow-up issue.

