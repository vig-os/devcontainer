---
type: issue
state: open
created: 2026-02-24T16:39:39Z
updated: 2026-02-24T16:54:28Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/187
comments: 3
labels: bug, area:workspace, effort:small, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:51.533Z
---

# [Issue 187]: [[BUG] just check uses wrong path — justfile_directory() resolves incorrectly in imported justfile.base](https://github.com/vig-os/devcontainer/issues/187)

### Description

The `check` recipe in `justfile.base` uses `dirname "{{justfile_directory()}}"` to locate `.devcontainer/scripts/version-check.sh`. This path computation is wrong in both contexts where `justfile.base` is used:

- **Deployed workspace:** `justfile_directory()` returns the project root (where the root `justfile` lives). `dirname` of that goes one level above the project, producing a path like `/workspace/.devcontainer/scripts` instead of `/workspace/<project>/.devcontainer/scripts`.
- **Devcontainer repo:** Same logic produces `<parent-of-repo>/.devcontainer/scripts`, which also doesn't exist.

### Steps to Reproduce

1. Open a deployed workspace container
2. Run `just check`

### Expected Behavior

`just check` locates `.devcontainer/scripts/version-check.sh` and runs the version check.

### Actual Behavior

```
Error: Could not locate .devcontainer/scripts directory
```

### Environment

- All deployed workspaces using `justfile.base`
- Also fails in the devcontainer repo itself

### Additional Context

`justfile.gh` already uses the correct pattern:

```
_gh_scripts := source_directory() / "scripts"
```

`source_directory()` (available since just 1.27.0) returns the directory of the current source file, not the root justfile. The container installs the latest `just` release, which is well past 1.27.0.

### Possible Solution

Replace line 76 in `justfile.base`:

```bash
# Before (broken):
SCRIPT_DIR="$(cd "$(dirname "{{justfile_directory()}}")/.devcontainer/scripts" && pwd)"

# After (fixed):
SCRIPT_DIR="$(cd "{{source_directory()}}/scripts" && pwd)"
```

This works correctly in both contexts:
- **Deployed workspace:** `source_directory()` = `.devcontainer/` → `scripts/` is right there
- **Devcontainer repo:** `source_directory()` = repo root → fails cleanly with "version-check.sh not found" (expected, since the script only exists in deployed workspaces)

### Changelog Category

Fixed

---

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 24, 2026 at 04:42 PM_

## Design

**Problem:** The `check` recipe uses `dirname(justfile_directory())` to locate `.devcontainer/scripts/`. In both contexts (deployed workspace and devcontainer repo), this resolves one level above the project root, producing invalid paths.

**Solution:** Use `source_directory()` (available since just 1.27.0) — returns the directory of the current source file, not the root justfile. This matches the pattern already used in `justfile.gh` (`_gh_scripts := source_directory() / "scripts"`).

**Change:** Replace line 76 in `justfile.base`:
- Before: `SCRIPT_DIR="$(cd \"$(dirname \"{{justfile_directory()}}\")/.devcontainer/scripts\" && pwd)"`
- After: `SCRIPT_DIR="$(cd \"{{source_directory()}}/scripts\" && pwd)"`

**Context behavior:**
- **Deployed workspace:** `source_directory()` = `.devcontainer/` → `scripts/` resolves correctly.
- **Devcontainer repo:** `source_directory()` = repo root → `scripts/` = `repo/scripts`; version-check.sh not present (expected) → fails cleanly with "version-check.sh not found".

**Files:** `justfile.base` (canonical); `assets/workspace/.devcontainer/justfile.base` is synced via manifest from root.

**Testing:** Existing integration tests that run `just check` in initialized workspaces will verify the fix.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 24, 2026 at 04:42 PM_

## Implementation Plan

Issue: #187
Branch: bugfix/187-fix-just-check-path

### Tasks

- [x] Replace `dirname(justfile_directory())` with `source_directory()` in check recipe — `justfile.base` — verify: `just sync-workspace` runs; integration test for `just check` passes

---

# [Comment #3]() by [gerchowl]()

_Posted on February 24, 2026 at 04:54 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (1 task)
- Execute: all tasks done
- Verify: integration tests pass (110), lint pass
- PR: https://github.com/vig-os/devcontainer/pull/189
- CI: status checks not yet reported on PR — may be pending workflow trigger

