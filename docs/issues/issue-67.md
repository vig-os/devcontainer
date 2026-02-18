---
type: issue
state: open
created: 2026-02-18T00:45:33Z
updated: 2026-02-18T00:45:33Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/67
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:30.789Z
---

# [Issue 67]: [[FEATURE] Consolidate sync-manifest and sync-workspace into a declarative Python manifest](https://github.com/vig-os/devcontainer/issues/67)

### Description

Replace the current dual-system approach (`sync-manifest.txt` + `prepare-build.sh` for build-time copies, and `sync-workspace.sh` for pre-commit-time generation with transformations) with a single declarative Python manifest that handles both what gets copied into `assets/workspace/` and how files are transformed.

### Problem Statement

We currently have two competing systems for getting files into the workspace template:

1. **`sync-manifest.txt` + `prepare-build.sh`** — build-time overlay that copies repo-root files into `build/assets/workspace/`. Tested via `test_manifest_files` (SHA-256 checksum verification).
2. **`sync-workspace.sh`** — pre-commit hook that copies + transforms files into `assets/workspace/` (committed to the repo).

This causes:
- Duplicate logic for copying files
- Commented-out manifest entries to avoid conflicts
- Fragile awk/sed/grep transformations scattered across a shell script
- Two systems to maintain, with neither being the full picture

### Proposed Solution

Create a **single Python manifest** (`scripts/sync_manifest.py`) that declaratively describes both file mappings and transformations:

```python
MANIFEST = [
    # Copy as-is
    Entry(src=".yamllint"),
    Entry(src=".hadolint.yaml"),
    Entry(src=".github/workflows/scorecard.yml"),

    # Copy with transformations
    Entry(src=".cursor/rules/", transforms=[
        Sed(file="commit-messages.mdc", pattern=r"Full reference: \[docs/.*\]\n", replace=""),
    ]),
    Entry(src=".pre-commit-config.yaml", transforms=[
        RemoveHooks(["generate-docs", "sync-workspace"]),
        Sed(pattern="s|bandit -r packages/vig-utils/src/ scripts/ assets/workspace/|bandit -r src/|g"),
    ]),
]
```

- `prepare-build.sh` calls `uv run python scripts/sync_manifest.py sync build/assets/workspace/`
- The `just sync-workspace` recipe calls the same script targeting `assets/workspace/`
- `test_manifest_files` reads the same manifest, skipping checksum verification for transformed entries
- Remove `sync-workspace.sh`, `remove-precommit-hooks.py`, and the pre-commit `sync-workspace` hook

### Alternatives Considered

- **Keep both systems** — current state; causes confusion and manifest/test drift
- **Add transformations to `prepare-build.sh` as shell code** — keeps bash, but transformations stay fragile and non-declarative
- **YAML/TOML manifest** — possible, but Python gives us type safety and the transform functions live next to the data

### Additional Context

- Related to #63 (agent-driven development workflows — the workspace sync was introduced here)
- The existing `sync-manifest.txt` was introduced in PR #54 alongside `prepare-build.sh`
- BATS tests for `prepare-build.sh` exist (`tests/bats/prepare-build.bats`) and will need updating
- `test_manifest_files` in `test_image.py` verifies checksums and will need a "skip transforms" path

### Impact

- **Beneficiaries:** Maintainers adding new workspace template files or transformations
- **Compatibility:** No change to the built image content — only build pipeline internals
- **Risks:** Low; the manifest is tested and the output is identical

### Changelog Category

Changed
