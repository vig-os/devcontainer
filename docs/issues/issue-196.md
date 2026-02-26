---
type: issue
state: closed
created: 2026-02-25T09:41:25Z
updated: 2026-02-25T10:06:06Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/196
comments: 0
labels: chore, priority:medium, area:workflow, effort:small
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-26T04:22:24.588Z
---

# [Issue 196]: [[CHORE] Add missing worktree workflow dependencies to setup requirements](https://github.com/vig-os/devcontainer/issues/196)

## Chore Type
Dependency update

## Description
The autonomous worktree pipeline currently fails if host-level tools required by `worktree-start` are missing.  
At minimum, `tmux` is missing from `scripts/requirements.yaml` even though `just worktree-start` hard-requires it.

A quick dependency scan of the worktree workflow suggests additional required tools are not declared in setup requirements:
- `tmux` (explicit prerequisite check)
- `agent` / cursor-agent CLI (explicit prerequisite check)
- `jq` (used in worktree trust/config and issue metadata parsing)

## Acceptance Criteria
- [ ] `scripts/requirements.yaml` includes `tmux` as a required dependency with install/check instructions
- [ ] `scripts/requirements.yaml` includes any other host-level tools required by worktree commands (`agent`, `jq`) with clear install guidance
- [ ] `scripts/init.sh --check` reports missing worktree prerequisites before users run worktree commands
- [ ] Worktree launch path (`just worktree-start <issue> \"/worktree-solve-and-pr\"`) no longer fails due to undeclared missing dependencies on a fresh host setup

## Implementation Notes
- Target file: `scripts/requirements.yaml`
- Verify commands used by `worktree-start` and `worktree-attach` in `justfile.worktree` and align the declared dependency list with runtime requirements
- Consider whether `pre-commit` should remain venv-only (`uv run`) or also be explicitly checked as a host command in worktree flows

## Related Issues
Related to #195

## Priority
Medium

## Changelog Category
No changelog needed

## Additional Context
Observed failure while launching `/solve-and-pr 195`:
`[ERROR] tmux is not installed. Install it first.`
