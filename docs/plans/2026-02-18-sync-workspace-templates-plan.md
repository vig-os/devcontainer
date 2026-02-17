# Plan: Sync workspace templates from repo root

**Issue**: #63
**Date**: 2026-02-18
**Design decision**: Ground truth lives in repo root; `just sync-workspace` copies
to `assets/workspace/` with generalizations. Distributed via devcontainer release
cycle. No `init-workspace.sh` changes needed.

---

## Context

The devcontainer repo has `.cursor/` rules/commands, `.github/` templates, and
`.pre-commit-config.yaml` that should ship to downstream projects via the
workspace template (`assets/workspace/`). Rather than maintaining two copies, a
sync script copies from root to `assets/workspace/` applying mechanical
transformations.

## Copy strategy

### Directory copies (rsync --delete)

New files auto-ship. Deleted files auto-remove. No script update needed.

| Source directory | Destination |
|---|---|
| `.cursor/rules/` | `assets/workspace/.cursor/rules/` |
| `.cursor/commands/` | `assets/workspace/.cursor/commands/` |
| `.github/ISSUE_TEMPLATE/` | `assets/workspace/.github/ISSUE_TEMPLATE/` |

### Explicit file copies

Selective — surrounding files in these directories should NOT ship.

| Source file | Destination |
|---|---|
| `.github/pull_request_template.md` | `assets/workspace/.github/pull_request_template.md` |
| `.github/dependabot.yml` | `assets/workspace/.github/dependabot.yml` |
| `.pre-commit-config.yaml` | `assets/workspace/.pre-commit-config.yaml` |
| `.gitmessage` | `assets/workspace/.gitmessage` |

## Post-copy transformations

Applied to the **destination** files after copying.

| File | Transform |
|---|---|
| `assets/workspace/.cursor/rules/commit-messages.mdc` | Remove link to `docs/COMMIT_MESSAGE_STANDARD.md` (does not exist in downstream repos) |
| `assets/workspace/.cursor/commands/tdd.md` | Replace devcontainer-specific test recipes (`just test-image`, `just test-integration`, `just test-utils`) with generic recipes (`just test`, `just test-cov`, `just test-pytest`) |
| `assets/workspace/.cursor/commands/verify.md` | Replace `just test-image` with `just test` in the example recipes |
| `assets/workspace/.github/dependabot.yml` | Remove Docker ecosystem section (devcontainer-specific) |
| `assets/workspace/.pre-commit-config.yaml` | 1. Remove `generate-docs` hook block. 2. Replace Bandit paths (`packages/vig-utils/src/ scripts/ assets/workspace/`) with generic `src/`. 3. Replace active `validate-commit-msg` args with commented examples. |

## Files NOT synced (devcontainer-repo-specific)

| File | Reason |
|---|---|
| `.github/workflows/*.yml` (root versions) | Workspace has its own simplified CI and release workflows |
| `.github/actions/*` | Devcontainer-specific composite actions |
| `.github/dependency-review-allow.txt` | Devcontainer-specific advisory list |
| `.github/CODEOWNERS` | Already in workspace template (not overwritten) |
| `docs/COMMIT_MESSAGE_STANDARD.md` | Devcontainer-specific doc |

## Untracked file handling

The sync script copies from the **filesystem**, not the git index. If a developer
has untracked files in a synced directory (e.g. a half-finished command), rsync
will copy them to `assets/workspace/`.

**Behavior**: The script checks for untracked files in source directories and
prints a warning. It does NOT fail — the developer sees the warning and decides
whether to `git add` or `.gitignore` the file. A CI staleness check (follow-up)
is the safety net.

```
⚠ Untracked source files detected (not yet in git):
    .cursor/commands/new-workflow.md
  Run 'git add' on these files, then re-run sync.
```

## Pre-commit integration

The hook follows the same pattern as `generate-docs`:

```yaml
- id: sync-workspace
  name: sync-workspace (sync templates to assets/workspace)
  entry: bash -c 'scripts/sync-workspace.sh && git add assets/workspace/ 2>/dev/null || true'
  language: system
  files: ^(\.cursor/|\.github/ISSUE_TEMPLATE/|\.github/pull_request_template\.md|\.github/dependabot\.yml|\.pre-commit-config\.yaml|\.gitmessage)
  pass_filenames: false
```

Trigger: any staged file matching the source patterns.
Effect: runs full sync, stages all workspace output (additions, modifications, deletions).

---

## Tasks

### Task 1: Create `scripts/sync-workspace.sh`

- **What**: Shell script that:
  1. rsync `--delete` copies `.cursor/rules/`, `.cursor/commands/`,
     `.github/ISSUE_TEMPLATE/` to `assets/workspace/`
  2. Explicit-copies `.github/pull_request_template.md`, `.github/dependabot.yml`,
     `.pre-commit-config.yaml`, `.gitmessage` to `assets/workspace/`
  3. Applies post-copy sed transformations to destination files
  4. Warns (does not fail) about untracked files in source directories
- **Files**: `scripts/sync-workspace.sh` (new)
- **Verification**: `bash scripts/sync-workspace.sh` completes without error;
  diff output files against expected content to verify transforms.

### Task 2: Add `just sync-workspace` recipe

- **What**: Add recipe to `justfile` in the `[info]` group, calling
  `scripts/sync-workspace.sh`.
- **Files**: `justfile`
- **Verification**: `just sync-workspace` runs successfully.

### Task 3: Add `sync-workspace` pre-commit hook

- **What**: Add a `local` pre-commit hook that triggers
  `scripts/sync-workspace.sh` when source files change, then stages the output
  via `git add assets/workspace/`.
- **Files**: `.pre-commit-config.yaml`
- **Verification**: `just precommit` picks up the hook; modifying a source file
  and running pre-commit produces updated workspace files.

### Task 4: Run initial sync and verify output

- **What**: Run `just sync-workspace` to populate `assets/workspace/` with all
  new files. Verify key transformations are correct.
- **Files**: All destination files listed above.
- **Verification**:
  - `assets/workspace/.cursor/rules/` contains 4 `.mdc` files
  - `assets/workspace/.cursor/commands/` contains 15 `.md` files
  - `assets/workspace/.github/ISSUE_TEMPLATE/` contains 3 `.yml` files
  - `assets/workspace/.github/pull_request_template.md` exists
  - `assets/workspace/.github/dependabot.yml` exists without Docker section
  - `assets/workspace/.gitmessage` exists
  - `assets/workspace/.pre-commit-config.yaml` has no `generate-docs` hook,
    generic Bandit paths, commented `validate-commit-msg` args
  - `assets/workspace/.cursor/commands/tdd.md` has generic test recipes
  - `assets/workspace/.cursor/commands/verify.md` has generic test recipes
  - `assets/workspace/.cursor/rules/commit-messages.mdc` has no doc link

### Task 5: Update CHANGELOG.md

- **What**: Add entries under `## Unreleased / ### Added` for the new workspace
  template files and sync mechanism.
- **Files**: `CHANGELOG.md`
- **Verification**: Entry present under Unreleased.

---

## Follow-up issues (out of scope)

- Ship docs-as-code tooling (`docs/generate.py` skeleton, `docs/templates/`
  example, `generate-docs` pre-commit hook) to workspace template
- BATS tests for `sync-workspace.sh`
- CI staleness check: run `just sync-workspace` and verify
  `git diff --exit-code assets/workspace/`
