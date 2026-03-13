---
type: issue
state: open
created: 2026-02-18T00:45:33Z
updated: 2026-02-18T16:39:57Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/67
comments: 1
labels: feature, priority:high, area:workspace, effort:large, semver:minor
assignees: none
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-19T00:08:10.155Z
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
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 04:39 PM_

## Design: Skill Namespace Renaming (Colon-Separated Prefixes)

### Problem

15 flat skill folders in `.cursor/skills/` make it hard to filter and invoke the right skill quickly. No grouping or namespace hints in the names.

### Approach

Add **colon-separated namespace prefixes** to skill folder names. Cursor doesn't support nested skill directories, so the namespace is encoded in the flat folder name itself (e.g., `git:commit`). Typing `code:` in the skill picker filters to implementation skills only.

### Mapping

| New name | Old name | Namespace |
|---|---|---|
| `issue:create` | `create-issue` | issue |
| `issue:claim` | `claim-issue` | issue |
| `issue:triage` | `issue-triage` | issue |
| `design:brainstorm` | `brainstorm` | design |
| `design:plan` | `plan` | design |
| `code:execute` | `execute-plan` | code |
| `code:tdd` | `tdd` | code |
| `code:debug` | `debug` | code |
| `code:verify` | `verify` | code |
| `code:review` | `review` | code |
| `git:commit` | `commit-msg` | git |
| `ci:check` | `check-ci` | ci |
| `ci:fix` | `fix-ci` | ci |
| `pr:create` | `submit-pr` | pr |
| `pr:post-merge` | `after-pr-merge` | pr |

### Workflow flow (left to right)

```
issue:* → design:* → code:* → git:* → ci:* → pr:*
```

### What changes

For each skill rename:
1. Rename `.cursor/skills/<old>/` → `.cursor/skills/<new>/`
2. Update `name:` frontmatter in `SKILL.md`
3. Update all cross-references (`../old/SKILL.md` → `../new/SKILL.md`)
4. Update `scripts/sync_manifest.py` transform targets
5. Rename `assets/workspace/.cursor/skills/<old>/` → `assets/workspace/<new>/` (or re-run sync)
6. Update any references in `.github/label-taxonomy.toml`, `CHANGELOG.md`

### Constraints

- Cursor does not support nested skill directories — folder name is the skill identifier
- Colon (`:`) chosen as separator — unambiguous, no collision with kebab-case words
- `assets/workspace/.cursor/skills/` is a sync mirror; rename source first, then sync

