---
type: issue
state: closed
created: 2026-02-06T09:50:35Z
updated: 2026-02-06T10:37:23Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/46
comments: 0
labels: bug
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:36.343Z
---

# [Issue 46]: [fix: run pre-commit through uv in justfile precommit recipe](https://github.com/vig-os/devcontainer/issues/46)

### Description

The `just precommit` recipe currently runs `pre-commit run --all-files` directly, which may fail if `pre-commit` is not installed globally or not in PATH outside the virtual environment.

### Problem Statement

When running `just precommit` in a workspace where `pre-commit` is only available inside the uv-managed virtual environment, the command fails because it doesn't find the `pre-commit` executable.

### Proposed Solution

Change the `precommit` recipe in `justfile.base` to run pre-commit through uv:

```diff
-    pre-commit run --all-files
+    uv run pre-commit run --all-files
```

This ensures the command runs within the project's virtual environment where pre-commit is installed.

### Files Affected

- `justfile.base`
- `assets/workspace/.devcontainer/justfile.base`
