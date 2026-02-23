---
type: issue
state: open
created: 2026-02-22T09:34:10Z
updated: 2026-02-22T09:46:58Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/154
comments: 0
labels: bug, area:workflow
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-23T04:30:07.393Z
---

# [Issue 154]: [[BUG] worktree-start silently fails when agent --print hangs during branch name derivation](https://github.com/vig-os/devcontainer/issues/154)

### Description

`just worktree-start` (aliased as `wt-start`) silently fails with a generic `exit code 1` when `agent --print` hangs during the branch name derivation step. The user sees no diagnostic output explaining what went wrong.

The root cause is that `agent --print` (cursor-agent CLI `2026.02.13-41ac335`) currently hangs indefinitely in headless mode regardless of model. Because the script uses `set -euo pipefail`, the failed command substitution on line 130 of `justfile.worktree` kills the script before the explicit error handler on line 138 ever runs.

### Steps to Reproduce

1. Ensure issue has no linked branch (e.g. `gh issue develop --list <issue>` returns empty)
2. Run `just wt-start <issue> "/worktree_solve-and-pr"`
3. The recipe reaches the `agent --print` call to derive a branch name summary
4. `agent --print` hangs indefinitely, eventually the script fails

### Expected Behavior

- The `agent --print` call should have a timeout (e.g. 30s)
- On timeout or failure, the script should print a clear error message including:
  - What command failed (`agent --print`)
  - The exit code or signal
  - A suggested manual workaround (`gh issue develop <issue> --base dev --name <type>/<issue>-<summary>`)
- The existing `[ERROR] Agent failed to derive a branch summary` message (line 139) should actually be reachable

### Actual Behavior

```
[*] No linked branch for issue #121. Creating one...
error: Recipe `worktree-start` failed with exit code 1
```

No indication of what failed. The user must manually debug to discover the `agent --print` hang.

### Environment

- **OS**: macOS 24.5.0 (darwin, arm64)
- **cursor-agent CLI**: 2026.02.13-41ac335
- **just**: latest
- **Shell**: zsh

### Additional Context

- `agent --print` hangs across all models (composer-1.5, sonnet-4, gpt-5) — this is a Cursor CLI bug, not model-specific
- `agent status`, `agent about`, `agent --list-models` all work fine — only `--print` mode is broken
- Workaround: create the branch manually with `gh issue develop <issue> --base dev --name <type>/<issue>-<summary>`, then re-run `wt-start`

### Possible Solution

1. Wrap the `agent --print` call in `timeout 30` (or similar) so it can't hang indefinitely
2. Capture the exit code explicitly instead of relying on `set -e` to kill the script:
   ```bash
   SUMMARY=$(timeout 30 agent --print --yolo --trust --model "$MODEL" "..." | tail -1 | tr -d '[:space:]') || true
   ```
3. Keep the existing guard (`if [ -z "$SUMMARY" ]`) reachable so the diagnostic message and manual workaround instructions are printed

### Changelog Category

Fixed
