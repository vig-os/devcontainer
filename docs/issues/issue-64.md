---
type: issue
state: open
created: 2026-02-17T23:08:54Z
updated: 2026-02-18T08:04:10Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/64
comments: 1
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:23:25.235Z
---

# [Issue 64]: [Add Cursor worktree support for parallel agent development](https://github.com/vig-os/devcontainer/issues/64)

## Description

Add `.cursor/worktrees.json` and update development commands to support Cursor's native Parallel Agents feature, which uses git worktrees for isolated agent execution.

## Problem Statement

When working on an issue and needing to start a second task (e.g. found a bug while working on a feature), the current workflow requires stashing and switching branches. Cursor's Parallel Agents feature can run agents in isolated worktrees, but this repo has no worktree setup configuration.

## Proposed Solution

### 1. Create `.cursor/worktrees.json`
Setup script to initialize worktrees for this repo:
- `uv sync` (install Python deps)
- `pre-commit install` (hooks)
- `git config commit.template .gitmessage`
- Copy `.env` if present

### 2. Update `start-issue.md`
When the user is already on a feature branch with changes, offer the parallel agent option as an alternative to stash-and-switch.

### 3. Document the workflow
Add guidance for when to use parallel agents vs. local mode.

## Known Limitations (as of Feb 2026)

Cursor's worktree/parallel agents have **known bugs inside devcontainers**:

- **Path resolution failure** — agents produce ENOENT errors with malformed worktree paths in WSL + devcontainer environments. `.cursor/worktrees.json` detection also fails despite files existing. ([Forum: misresolved paths](https://forum.cursor.com/t/cursor-parallel-agents-in-wsl-devcontainers-misresolve-worktree-paths-and-context/145711/6))
- **Apply button failure** — in devcontainers, the "Apply" button tries to read files via `vscode-remote://` URIs instead of local paths, failing completely. ([Forum: apply failure](https://forum.cursor.com/t/failed-to-apply-worktree-to-current-branch-in-dev-container/151303))

**Worktrees work correctly when Cursor runs natively** (macOS local, Linux local). Since this project is a devcontainer, the primary user workflow (developing *inside* the container) is affected. Implementation should proceed once Cursor fixes the devcontainer integration, or can be scoped to local-only development initially.

## Research References

- [Cursor Parallel Agents docs](https://cursor.com/docs/configuration/worktrees)
- [Cursor blog: agent best practices](https://cursor.com/blog/agent-best-practices)
- [Git worktrees done right (bare repo pattern)](https://gabri.me/blog/git-worktrees-done-right)
- [Reddit: organizing worktree folders](https://reddit.com/r/git/comments/wwapum/how_to_organize_git_worktree_folders)
- [obra/superpowers: using-git-worktrees](https://github.com/obra/superpowers/tree/main/skills/using-git-worktrees)

## Acceptance Criteria

- [ ] `.cursor/worktrees.json` created with repo-specific setup script
- [ ] `start-issue.md` updated to mention parallel agent option
- [ ] Devcontainer limitation documented
- [ ] Tested with Cursor Parallel Agents in local (non-container) mode
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 08:04 AM_

**Idea: tmux + cursor-agent CLI for multi-worktree terminals**

We might want to include `tmux` in the container and also have the `cursor-agent` CLI installed. This would allow running multiple worktrees in parallel terminals via tmux sessions — useful for orchestrating several agent-driven development streams simultaneously from within the devcontainer.

