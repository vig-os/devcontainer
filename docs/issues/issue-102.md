---
type: issue
state: closed
created: 2026-02-20T09:40:30Z
updated: 2026-02-20T15:10:55Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/102
comments: 2
labels: feature, area:workflow, effort:small, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:36.404Z
---

# [Issue 102]: [[FEATURE] Add optional reviewer parameter to worktree-start for autonomous PR creation](https://github.com/vig-os/devcontainer/issues/102)

### Description

Add an optional `reviewer` parameter to the `worktree-start` just recipe so the autonomous pipeline (`worktree:solve-and-pr`) can optionally assign a PR reviewer at creation time.

### Problem Statement

The autonomous `worktree:pr` skill creates PRs with `--assignee @me` but has no way to request a reviewer. The interactive `pr:create` skill asks the user, but the autonomous variant runs unattended. Currently there is no mechanism to control whether a reviewer gets tagged on the resulting PR.

### Proposed Solution

Thread an optional `reviewer` parameter through the justfile and tmux environment:

1. **`justfile.worktree`** — add `reviewer=""` parameter to `worktree-start`. Assign to `REVIEWER` variable and pass into the tmux session via `-e "PR_REVIEWER=$REVIEWER"`.
2. **`worktree:pr/SKILL.md`** — in step 6 (Create PR), if `$PR_REVIEWER` is set and non-empty, append `--reviewer "$PR_REVIEWER"` to the `gh pr create` command.
3. **`assets/workspace/` copies** — mirror the same changes.

Usage:
```bash
just worktree-start 99 "/worktree-solve-and-pr" "@c-vigo"   # with reviewer
just worktree-start 99 "/worktree-solve-and-pr"              # no reviewer
```

### Alternatives Considered

- **Agent-assessed reviewer at PR time**: Agent decides based on diff size/labels. Rejected — too subjective, and late in context window.
- **Capture PR context upfront to a JSON file**: `worktree:solve-and-pr` writes `.github/pr-context-<issue>.json` at start when context is fresh. More elegant but heavier — overkill for a single setting right now. Could revisit if more PR preferences emerge.
- **Prompt-based convention**: User includes "reviewer: @handle" in the prompt text. Less explicit, depends on agent parsing natural language reliably.

### Impact

- Backward compatible — `reviewer` defaults to empty string, existing invocations unchanged.
- Benefits anyone using the autonomous worktree pipeline who wants PR review assignment.

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 10:00 AM_

Parent issue: #103

---

# [Comment #2]() by [gerchowl]()

_Posted on February 20, 2026 at 03:10 PM_

Completed via PR #106 (merged 2026-02-20).

