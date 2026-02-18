---
type: issue
state: open
created: 2026-02-17T23:08:54Z
updated: 2026-02-18T20:39:00Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/64
comments: 2
labels: feature, priority:low, area:workflow, effort:medium, semver:minor
assignees: none
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-18T20:39:41.984Z
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

---

# [Comment #2]() by [gerchowl]()

_Posted on February 18, 2026 at 08:39 PM_

## Design: Cursor Worktree & Parallel Agent Support

### Overview

Two parallel paths for running agents in isolated worktrees:

1. **Native Cursor worktrees** (`.cursor/worktrees.json`) — for macOS/Linux local development (Cursor UI handles everything).
2. **CLI-based worktrees** (justfile recipes + tmux + `cursor-agent` CLI) — for devcontainer environments where native worktrees have known bugs.

Both paths are complemented by a set of **autonomous worktree skills** that mirror the interactive workflow skills but never block for user feedback.

---

### Component 1: `.cursor/worktrees.json`

Native Cursor worktree initialization config. When Cursor creates a worktree on macOS/Linux, this script sets up the environment:

```json
{
  "setup-worktree-unix": [
    "uv sync",
    "pre-commit install --install-hooks",
    "git config commit.template .gitmessage",
    "test -f \"$ROOT_WORKTREE_PATH/.env\" && cp \"$ROOT_WORKTREE_PATH/.env\" .env || true"
  ]
}
```

- `setup-worktree-unix` only (no Windows support needed — devcontainer is Linux, native is macOS/Linux).
- `$ROOT_WORKTREE_PATH` is set by Cursor automatically, pointing to the primary working tree.
- Conditional `.env` copy — doesn't fail if no `.env` exists.

**Known limitation:** Cursor's native worktree UI does **not** work inside devcontainers (Feb 2026). Path resolution and Apply button failures. See [forum thread](https://forum.cursor.com/t/cursor-parallel-agents-in-wsl-devcontainers-misresolve-worktree-paths-and-context/145711/6). This file only takes effect when Cursor runs natively.

---

### Component 2: `justfile.worktree` — CLI-based worktree recipes

New justfile module imported from the main `justfile`. Provides tmux + `cursor-agent` CLI orchestration for devcontainer environments.

**Worktree location:** `../<repo>-worktrees/<issue>/` relative to the project root. Example:

```
Projects/eXoma/
├── devcontainer/                  # main checkout
├── devcontainer-worktrees/        # auto-created by recipes
│   ├── 42/                        # worktree for issue #42
│   └── 67/                        # worktree for issue #67
```

**Recipes:**

| Recipe | Description |
|--------|-------------|
| `worktree-start <issue> [prompt]` | Create git worktree, open tmux session, launch `cursor-agent` |
| `worktree-list` | List active worktrees and their tmux sessions |
| `worktree-attach <issue>` | Attach to an existing tmux session |
| `worktree-stop <issue>` | Kill tmux session and remove worktree |
| `worktree-clean` | Remove all cursor-managed worktrees and sessions |

**`worktree-start` flow:**

1. Validate prerequisites (tmux installed, `CURSOR_API_KEY` set).
2. Derive `<repo>` from `basename $(git rev-parse --show-toplevel)`.
3. Create branch and worktree: `git worktree add ../<repo>-worktrees/<issue>`.
4. Run setup in worktree (uv sync, pre-commit install, git config, .env copy).
5. Start tmux session `wt-<issue>`.
6. Inside session: `agent chat "<prompt>"` (or drop to shell if no prompt).

**Devcontainer limitation documented** as comments at the top of `justfile.worktree`:

```
# NOTE: Cursor's native worktree UI does NOT work inside devcontainers (Feb 2026).
# These recipes provide a CLI-based alternative using tmux + cursor-agent.
# Native worktree support (.cursor/worktrees.json) works on macOS/Linux local only.
# Tracked: https://forum.cursor.com/t/.../145711
```

---

### Component 3: Autonomous worktree skills

Worktree-specific skill variants that mirror the interactive workflow but **never block for user feedback**. They make reasonable decisions autonomously.

#### State-aware pipeline (`worktree:solve-and-pr`)

The compound skill reads the **full issue** (body + comments) to determine what phase to start from:

**Read full context:**
- `gh issue view <number> --json title,body,labels,comments`
- Parse body for: description, proposed solution, acceptance criteria, constraints
- Parse comments for phase markers (H2 headings)

**State detection:**

| What exists | Meaning | Agent starts from |
|---|---|---|
| Body only (no design comment) | Fresh issue | `worktree:brainstorm` |
| Body + `## Design` comment | Design done | `worktree:plan` |
| Body + `## Design` + `## Implementation Plan` | Plan done | `worktree:execute` |

The body is **always read** as the foundation — it contains the problem, proposed solution, and acceptance criteria. Comments layer completed phases on top.

**Full pipeline:**

| Phase | Skill | Output |
|---|---|---|
| 1. Design | `worktree:brainstorm` | Posts `## Design` comment on issue |
| 2. Plan | `worktree:plan` | Posts `## Implementation Plan` comment on issue |
| 3. Implement | `worktree:execute` | Commits (TDD: test → impl → refactor) |
| 4. Verify | `worktree:verify` | Full test suite + lint + precommit. Evidence-based pass/fail. Loops back to execute on failure. |
| 5. PR | `worktree:pr` | Creates PR with summary |

#### Individual skills

| Skill | Purpose | Blocks? |
|---|---|---|
| `worktree:brainstorm` | Autonomous design — reads issue body, posts `## Design` comment | No |
| `worktree:plan` | Autonomous planning — posts `## Implementation Plan` comment | No |
| `worktree:execute` | TDD implementation — commits as it goes | No |
| `worktree:verify` | Runs full verification, evidence only. Loops back to fix on failure. | No |
| `worktree:pr` | Creates PR from worktree branch | No |
| `worktree:ask` | Posts question to issue comment (placeholder for Telegram bot — separate issue) | Polls |
| `worktree:solve-and-pr` | Compounds all above: detect state → run remaining phases → PR | No |

#### Feedback channel: `worktree:ask`

When an autonomous agent is genuinely stuck, it uses `worktree:ask` to post a question as a GitHub issue comment. **Placeholder implementation** — a future issue will add Telegram/Element bot integration for push notifications and faster reply loops.

---

### Component 4: Sync manifest update

Add to `scripts/sync_manifest.py`:

1. **`.cursor/worktrees.json`** — synced as-is (setup commands are generic for uv-based projects).
2. **`justfile.worktree`** — synced to downstream projects (may need transforms for project-specific paths).

---

### Component 5: Changelog

Under `## Unreleased` → `### Added`:
- **Cursor worktree support for parallel agent development** ([#64](https://github.com/vig-os/devcontainer/issues/64))

---

### Out of scope

- **No changes to `issue:claim`** — the `agent:parallel` / `worktree:solve-and-pr` skill handles parallel workflow separately.
- **No separate docs/ file** — justfile comments are the in-repo documentation (SSoT). Research context lives in this issue.
- **No Windows support** — devcontainer is Linux, native is macOS/Linux.
- **No Telegram bot implementation** — separate issue. `worktree:ask` uses GitHub comments as placeholder.

