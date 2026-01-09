---
type: issue
state: closed
created: 2025-11-26T13:22:49Z
updated: 2025-12-09T05:58:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/3
comments: 0
labels: enhancement
assignees: c-vigo
milestone: Initial release
projects: none
relationship: none
synced: 2026-01-09T16:17:37.746Z
---

# [Issue 3]: [[FEATURE] Mount project in a sub-folder /workspace/project_name](https://github.com/vig-os/devcontainer/issues/3)

### Description

By default, mount the project root folder in a sub-directory of workspace

### Problem Statement

Allow multiple repositories in the same devcontainer for simultaneous development or testing.

### Proposed Solution

Modify initialization script and configuration files

### Alternatives Considered

_No response_

### Additional Context

_No response_

### Impact

- Projects that may be developed in parallel
- It might make the VS Code "Reopen project" context menu more helpful
- Breaking change! Incompatible with previous setup (but no release yet)
