---
type: issue
state: open
created: 2026-02-19T17:26:31Z
updated: 2026-02-20T08:39:45Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/96
comments: 0
labels: refactor, priority:low, area:workspace, effort:small, semver:patch
assignees: none
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-20T09:26:11.007Z
---

# [Issue 96]: [Refactor: extract shared utilities from sync_manifest.py](https://github.com/vig-os/devcontainer/issues/96)

## Context

During PR #68 review, it was noted that `scripts/sync_manifest.py` contains utility code (transform classes, file operations) that could be extracted into a shared `scripts/utils.py` module. This would improve reusability and testability.

## Scope

- Extract generic transform classes (`Sed`, `RemoveLines`, `StripTrailingBlankLines`, `RemoveBlock`, `ReplaceBlock`) into `scripts/utils.py`
- Keep manifest-specific logic (`MANIFEST`, `sync()`, `list_entries()`) in `sync_manifest.py`
- Update imports accordingly
- Ensure existing tests still pass

## Out of scope

- Changing the manifest format or sync behavior
- Adding new transforms

## Acceptance criteria

- [ ] Transform classes live in `scripts/utils.py`
- [ ] `sync_manifest.py` imports from `scripts/utils.py`
- [ ] `just sync-workspace` produces identical output before and after
- [ ] All existing tests pass
