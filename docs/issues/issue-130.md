---
type: issue
state: open
created: 2026-02-20T17:36:01Z
updated: 2026-02-20T17:41:15Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/130
comments: 0
labels: chore
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-21T04:11:17.757Z
---

# [Issue 130]: [[CHORE] Install tmux in Containerfile for worktree session persistence](https://github.com/vig-os/devcontainer/issues/130)

### Chore Type

Configuration change

### Description

The `justfile.worktree` recipes rely on tmux to run autonomous `cursor-agent` sessions in detached tmux sessions (`tmux new-session -d -s "wt-<issue>"`). However, tmux is not included in the Containerfile's `apt-get install` list (line 53-62), so `just worktree-start` fails at the prerequisite check.

This is especially important for the remote devcontainer use case: worktree agents must survive Cursor session disconnects, and tmux is the persistence mechanism that makes this possible. Without tmux, the autonomous TDD workflow (RED-GREEN-REFACTOR with per-phase commits as defined in `.cursor/rules/tdd.mdc`) cannot run to completion — a disconnected session kills the agent mid-cycle, leaving partial test/implementation commits and breaking TDD compliance in the git history.

### Acceptance Criteria

- [ ] `tmux` is installed via `apt-get` in the Containerfile alongside existing system dependencies
- [ ] Container image builds successfully with tmux included
- [ ] `just worktree-start` no longer fails the tmux prerequisite check inside the container
- [ ] Autonomous worktree agents can complete full TDD cycles (test commit → implementation commit → refactor commit) after Cursor session disconnect
- [ ] Unit test: `test_tmux_installed` added to `TestSystemTools` in `tests/test_image.py` — verifies `tmux` apt package is installed (follows existing pattern: `host.package("tmux").is_installed`)
- [ ] Unit test: `test_tmux_version` added to `TestSystemTools` — verifies `tmux --version` returns successfully and matches expected major version
- [ ] `tmux` version added to `EXPECTED_VERSIONS` dict in `tests/test_image.py`
- [ ] Integration/smoke test: `test_tmux_detached_session_survives` added to `tests/test_image.py` — creates a detached tmux session, verifies it appears in `tmux list-sessions`, and confirms the session's background process is running (validates the core persistence mechanism worktree agents rely on)

### Implementation Notes

- Add `tmux \` to the existing `apt-get install` block in the Containerfile (line 53-62). No other changes should be needed — the justfile already has the tmux check and usage in place.
- Unit tests follow the exact pattern of `test_nano_installed` / `test_git_version` etc. in `TestSystemTools`.
- The smoke test should create a detached session (`tmux new-session -d -s test-session "sleep 60"`), verify it with `tmux list-sessions`, then clean up (`tmux kill-session -s test-session`). This validates the same mechanism `justfile.worktree` uses without needing the full worktree infrastructure.

### Related Issues

_None_

### Priority

Medium

### Changelog Category

Added

### Additional Context

The `justfile.worktree` already validates tmux is present and errors with a helpful message if missing. This issue just closes the gap so the container is ready out of the box for autonomous TDD workflows.
