---
type: issue
state: open
created: 2026-02-20T22:14:35Z
updated: 2026-02-21T00:47:36Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/132
comments: 1
labels: bug, area:workflow
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-21T04:11:17.295Z
---

# [Issue 132]: [[BUG] worktree-attach fails when tmux session stopped but worktree exists](https://github.com/vig-os/devcontainer/issues/132)

### Current Behavior

When a worktree exists but its tmux session has been terminated (shown as `[STOPPED]` in `just wt-list`), running `just wt-attach <issue>` fails with:

```
[ERROR] No tmux session 'wt-<issue>' found.
Start one with: just worktree-start <issue>
```

However, `just worktree-start <issue>` is not the correct remedy — it detects the existing worktree directory and re-creates a session, but the error message from `worktree-attach` is misleading and the UX requires the user to know internals.

### Expected Behavior

`just worktree-attach <issue>` should detect when the worktree directory exists but the tmux session is not running, and automatically restart a tmux session in the existing worktree directory before attaching.

### Steps to Reproduce

1. `just worktree-start 130` (creates worktree + tmux session)
2. Stop the tmux session (e.g., exit the shell inside tmux, or the agent completes)
3. `just wt-list` — shows `[STOPPED]` for #130
4. `just wt-attach 130` — fails with misleading error

### Acceptance Criteria

- [ ] `worktree-attach` restarts the tmux session when the worktree directory exists but no tmux session is running
- [ ] After restart, the user is attached to the new session
- [ ] Behavior is unchanged when the tmux session is already running (attach as before)
- [ ] Behavior is unchanged when neither worktree nor session exists (error as before)
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Test Strategy

Tests go in `tests/bats/worktree.bats`, extending the existing BATS test file.

**Approach: end-to-end lifecycle smoke test using `--help` as prompt**

The `just worktree-start` recipe accepts a `prompt` parameter that becomes the command run inside the tmux session. By passing `--help` (i.e., `cursor-agent --help`) as the prompt, the tmux session starts and exercises the full worktree infrastructure, but the inner command exits immediately — no interactive agent, no blocking. This enables a real end-to-end lifecycle test without mocking:

```
wt-start (prompt="--help")  →  wt-list  →  wt-attach  →  wt-stop  →  wt-clean
```

**BATS test cases (lifecycle):**
1. `wt-start` with `--help` prompt creates worktree dir + tmux session
2. `wt-list` shows the worktree as `[RUNNING]` (or `[STOPPED]` once `--help` exits)
3. `wt-attach` on a stopped session (session exited after `--help`) restarts and attaches — **this is the new behavior under test**
4. `wt-attach` errors when no worktree dir exists at all
5. `wt-stop` kills the session and removes the worktree
6. `wt-clean` removes any leftover worktree directories

This tests all `just wt-*` commands in a single sequential flow, covering the happy path, the bug scenario (attach after session exit), and the error path — with zero mocking.

**Prerequisites:** tmux installed, a git repo with at least one issue branch resolvable (or a test fixture issue number). CI must have tmux available (covered by #130).

### Implementation Notes

- Affected file: `justfile.worktree` (recipe `worktree-attach`, line ~253)
- The `worktree-start` recipe already has logic to restart a tmux session for an existing worktree (lines 95-104) — reuse that pattern in `worktree-attach`
- The `_wt_base` variable defines the worktree directory path
- The `--help` trick works because `worktree-start` passes the prompt as the tmux session command: `tmux new-session -d -s "$SESSION" -c "$WT_DIR" "agent chat ... \"$PROMPT\""` — when `$PROMPT` is `--help`, the agent prints help and exits, leaving a stopped session

### Related Issues

Related to #130 (tmux installation), as this bug surfaces when using worktree tmux sessions.

### Priority

Medium

### Changelog Category

Fixed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 12:39 AM_

## Implementation Plan

Issue: #132
Branch: `bugfix/132-worktree-attach-stopped-session`

### Root Cause

`agent chat --trust` fails immediately with exit code 1:
```
Error: --trust can only be used with --print/headless mode
```
The `--trust` flag is incompatible with interactive `agent chat` mode. All 4 `agent chat` invocations in `justfile.worktree` include `--trust`, causing every tmux session to die on launch. The `_wt_ensure_trust` function already writes the worktree directory to `~/.cursor/cli-config.json` `trustedDirectories` before the session starts, so `--trust` was redundant — and actively breaking things.

### Tasks

- [ ] **Task 1 (RED): Write BATS integration tests for worktree-attach restart logic** — `tests/bats/worktree.bats` — verify: `just test-bats` (new tests fail)
  - Skip if tmux not available (`command -v tmux || skip`)
  - Setup: create a temp directory simulating a worktree, start a tmux session with a fast-exit command (`true`), wait for session to die
  - Test cases:
    1. Attach on stopped session with existing worktree dir → restarts tmux session (assert `tmux has-session` succeeds after restart)
    2. Attach errors when neither worktree dir nor session exists → assert non-zero exit
    3. Attach on already-running session → attaches directly, no restart
    4. Worktree directory is added to `trustedDirectories` in `~/.cursor/cli-config.json` after restart
  - Teardown: kill sessions, remove temp dirs, restore trust config
  - **No `agent` CLI or `gh` needed** — tests use `tmux`, `jq`, and filesystem ops only → fully CI-compatible once #130 merges

- [ ] **Task 2 (GREEN): Remove `--trust` from `agent chat` invocations** — `justfile.worktree` — verify: `just test-bats`
  - Remove `--trust` from all 4 `agent chat` command lines (lines 100, 102, 192, 194)
  - `_wt_ensure_trust` already handles workspace trust via `cli-config.json` before session launch — `--trust` flag was redundant and incompatible with chat mode

- [ ] **Task 3 (GREEN): Fix `worktree-attach` to restart stopped sessions** — `justfile.worktree` (recipe `worktree-attach`) — verify: `just test-bats` (all tests pass)
  - When `tmux has-session` fails, check if `_wt_base/<issue>` directory exists
  - If worktree dir exists: restart a tmux session in that directory (reuse pattern from `worktree-start` lines 95–104), then attach
  - If worktree dir does not exist: keep current error message
  - Add comment above the recipe referencing `tests/bats/worktree.bats` for future maintainers

- [ ] **Task 4: Update CHANGELOG.md** — `CHANGELOG.md` — verify: visual inspection
  - Add "Fixed" entry under `## Unreleased` for the worktree-attach bug

### Design Decisions

- **Root cause fix included**: `--trust` removal is required for sessions to survive at all — without it, the restart logic in Task 3 would just restart a session that immediately dies again.
- **Option B (focused integration tests)** chosen over full end-to-end smoke tests. Tests replicate the shell patterns from the recipes (tmux session creation, directory check, trust logic) without calling the full `just` recipes — avoids dependencies on `agent` auth, `gh` API, `uv sync`, `pre-commit`.
- Tests skip gracefully when tmux is unavailable (`command -v tmux || skip`), so CI works before #130 merges.
- `tmux new-session -d` always returns exit 0 regardless of inner command success — error detection for failed agent sessions is out of scope (potential follow-up issue).
- A comment in `justfile.worktree` on the `worktree-attach` recipe points to the test file, so recipe changes trigger test awareness.

