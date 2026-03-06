---
type: issue
state: open
created: 2026-02-24T16:59:20Z
updated: 2026-02-24T17:06:23Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/190
comments: 1
labels: bug, area:workspace, effort:medium, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:51.160Z
---

# [Issue 190]: [[BUG] Synced justfiles reference scripts not included in workspace manifest](https://github.com/vig-os/devcontainer/issues/190)

### Description

Several scripts in the devcontainer repo's `scripts/` directory are referenced by synced justfiles and `.pre-commit-config.yaml`, but are never deployed to downstream workspaces via the manifest (`scripts/manifest.toml`). Any `just` recipe or pre-commit hook that calls them fails with "No such file or directory".

### Affected Scripts

| Script | Referenced by | Error trigger |
|--------|-------------|---------------|
| `scripts/devc-remote.sh` | `justfile.base` line 382 | `just devc-remote` in any deployed workspace |
| `scripts/resolve-branch.sh` | `justfile.worktree` lines 129, 165 | `just worktree-start` (latent — worktree not imported by default) |
| `scripts/derive-branch-summary.sh` | `justfile.worktree` lines 149, 153 | `just worktree-start` (latent — same) |
| `scripts/check-skill-names.sh` | `.pre-commit-config.yaml` line 137 | Commit touching `.cursor/skills/` (also tracked in #186) |

### Steps to Reproduce

1. Deploy a workspace with `install.sh` or `just -g init-workspace`
2. Open the devcontainer
3. Run `just devc-remote myserver` → fails: `bash: scripts/devc-remote.sh: No such file or directory`

### Expected Behavior

All scripts referenced by synced justfiles are available in the deployed workspace and recipes work correctly.

### Actual Behavior

Scripts are missing. The manifest (`scripts/manifest.toml`) syncs `justfile.base`, `justfile.worktree`, and `.pre-commit-config.yaml` but not the scripts they depend on.

### Environment

- All deployed workspaces using synced `justfile.base` and `.pre-commit-config.yaml`

### Root Cause

Two problems:

1. **Missing manifest entries** — The four `.sh` scripts have no entries in `scripts/manifest.toml`, so they are never copied into `assets/workspace/`.

2. **Path mismatch** — Even if synced, the paths would be wrong. In the devcontainer repo, `justfile.base` sits at the root and `scripts/` is a sibling directory. In a deployed workspace, `justfile.base` is imported from `.devcontainer/justfile.base` but `just` runs recipes from the project root — so `scripts/devc-remote.sh` resolves to `<project>/scripts/devc-remote.sh`, which doesn't exist. The scripts should be deployed to `.devcontainer/scripts/` and referenced via `source_directory()` (as identified in #187).

### Possible Solution

1. Add manifest entries to sync the four scripts into `.devcontainer/scripts/` in the workspace.
2. In synced justfiles, reference scripts relative to `source_directory()`:
   ```just
   _scripts := source_directory() / "scripts"
   ```
   This resolves correctly in both contexts:
   - **Devcontainer repo**: `source_directory()` = repo root → `scripts/` ✓
   - **Deployed workspace**: `source_directory()` = `.devcontainer/` → `.devcontainer/scripts/` ✓
3. For `check-skill-names.sh` in `.pre-commit-config.yaml`, apply a manifest `Sed` transform to update the path in the synced version.

### Additional Context

- #185 — related: making container scripts callable via PATH
- #186 — narrowly covers `bandit` + `check-skill-names.sh` for pre-commit
- #187 — covers `just check` path resolution (same `source_directory()` fix pattern)
- #161 — covers vig-utils CLI hooks not available in deployed workspaces
- `justfile.worktree` is synced to `.devcontainer/justfile.worktree` but not imported by `assets/workspace/justfile` — the worktree script failures are latent until a user adds the import

### Changelog Category

Fixed

---

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
---

# [Comment #1]() by [c-vigo]()

_Posted on February 24, 2026 at 05:06 PM_

Related to #185

