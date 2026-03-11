---
type: issue
state: closed
created: 2026-03-10T14:53:34Z
updated: 2026-03-10T15:34:55Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/252
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-11T04:15:14.754Z
---

# [Issue 252]: [Fix bats test warnings and tmux session crash](https://github.com/vig-os/devcontainer/issues/252)

## Problem

- **githooks.bats**: BW01 warnings for `run` exit code 127 on IN_CONTAINER=true guard tests (hooks call downstream tooling not available on host)
- **worktree.bats**: `send-keys` trust-prompt test crashes with `server exited unexpectedly` when `agent` command exits immediately inside tmux

## Solution

- Use `run -127` with `bats_require_minimum_version 1.5.0` to acknowledge expected exit code in githooks tests
- Start tmux session with persistent shell and `remain-on-exit on` before sending agent command

Refs: #238
