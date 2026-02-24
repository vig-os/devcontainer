---
type: issue
state: open
created: 2026-02-23T07:58:16Z
updated: 2026-02-23T08:12:14Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/158
comments: 5
labels: feature, area:workflow, effort:small, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-24T04:24:09.053Z
---

# [Issue 158]: [[FEATURE] worktree-clean: add filter option for stopped-only vs all worktrees](https://github.com/vig-os/devcontainer/issues/158)

### Description

`just worktree-clean` (alias `wt-clean`) currently removes **all** worktrees unconditionally — including those with running tmux sessions where an agent may still be actively working. This is destructive and error-prone when you only want to clean up finished or broken worktrees.

### Problem Statement

When running multiple parallel worktrees, some may have completed (tmux session stopped) while others are still running. Currently there is no way to selectively clean up only the finished ones — `wt-clean` kills everything, forcing you to manually `wt-stop` individual issues or risk losing in-progress agent work.

### Proposed Solution

Add a `mode` parameter to `worktree-clean` with these options:

- **`just worktree-clean`** (default, no argument) — clean only **stopped** worktrees (no running tmux session). Safe default.
- **`just worktree-clean all`** — clean **all** worktrees (current behavior), with a confirmation prompt or clear warning.

Implementation in `justfile.worktree`:
- The recipe already iterates over worktree dirs and checks `tmux has-session`. Add a filter: when `mode` is empty/`stopped`, skip dirs where the tmux session is still running.
- When `mode` is `all`, retain current behavior (kill everything).
- Print a summary of what was skipped vs cleaned.

### Alternatives Considered

- **Separate recipes** (`worktree-clean-stopped`, `worktree-clean-all`) — more discoverable but clutters the recipe list.
- **Interactive confirmation per worktree** — too slow for many worktrees, breaks autonomous usage.
- **Dry-run flag** — useful addition but doesn't solve the core need of selective cleaning.

### Impact

- All users of `just wt-clean` benefit from a safer default.
- Backward-incompatible change: the default behavior changes from "clean all" to "clean stopped only". Users who relied on the old default must pass `all` explicitly.
- This is the safer direction — preventing accidental destruction of active work.

### Changelog Category

Changed

### Acceptance Criteria

- [ ] `just worktree-clean` (no args) removes only stopped worktrees, skips running ones with a message
- [ ] `just worktree-clean all` removes all worktrees (current behavior)
- [ ] Summary output shows what was cleaned and what was skipped
- [ ] `just wt-clean` alias continues to work
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 23, 2026 at 08:00 AM_

## Design

**Issue:** #158 — worktree-clean filter mode for stopped-only vs all

### Summary

Add a `mode` parameter to `worktree-clean` so the default cleans only stopped worktrees (no running tmux session), while `just worktree-clean all` retains current behavior (clean everything). Print a summary of cleaned vs skipped worktrees.

### Architecture

**Recipe signature:** `worktree-clean mode="":`

- `just worktree-clean` (no args) → `mode=""` → stopped-only (safe default)
- `just worktree-clean all` → `mode="all"` → clean all (current behavior)

**Logic in `justfile.worktree`:**

1. **Stopped-only mode** (`mode` empty or `stopped`):
   - For each worktree dir in `$WT_BASE/*/`:
     - If `tmux has-session -t wt-${issue}` → skip, add to skipped list, continue
     - Else → kill session if exists, remove worktree, delete branch, add to cleaned list
   - Print summary: cleaned N, skipped M (with dir names)

2. **All mode** (`mode="all"`):
   - Retain current behavior (iterate, kill all sessions, remove all worktrees)
   - Add a clear warning before proceeding
   - Print summary: cleaned N

**Summary output format:**
```
[OK] Cleaned: dir1, dir2
[SKIP] Skipped (running): dir3, dir4
Summary: 2 cleaned, 2 skipped
```

### Error Handling

- Invalid mode: print error, exit 1
- Empty $WT_BASE: unchanged — [*] No worktrees to clean

### Testing Strategy

- BATS tests in `tests/bats/worktree.bats`:
  - Stopped-only: mock worktree dirs, some with running tmux sessions, some without; assert only stopped ones are cleaned
  - All mode: assert all are cleaned
  - Summary output: assert Cleaned and Skipped lines appear correctly
  - Alias: `just wt-clean` and `just wt-clean all` work
- Use temp dirs for isolation (pattern from existing worktree-attach test)

### Files to Modify

- `justfile.worktree` — worktree-clean recipe
- `tests/bats/worktree.bats` — new tests for worktree-clean modes

---

# [Comment #2]() by [gerchowl]()

_Posted on February 23, 2026 at 08:00 AM_

## Implementation Plan

Issue: #158
Branch: feature/158-worktree-clean-filter-mode

### Tasks

- [x] Task 1: Add BATS test for worktree-clean stopped-only mode (skips running sessions) — `tests/bats/worktree.bats` — verify: `bats tests/bats/worktree.bats -f "worktree-clean"`

- [x] Task 2: Implement worktree-clean mode parameter (stopped-only default, all option) — `justfile.worktree` — verify: `just worktree-clean --help` shows usage

- [x] Task 3: Add BATS test for worktree-clean all mode — `tests/bats/worktree.bats` — verify: `bats tests/bats/worktree.bats -f "worktree-clean"`

- [x] Task 4: Add summary output (cleaned vs skipped) and wt-clean alias verification — `justfile.worktree` — verify: `just test`

---

# [Comment #3]() by [gerchowl]()

_Posted on February 23, 2026 at 08:08 AM_

## CI Diagnosis

**Failing workflow:** CI / Build Container Image / Build container image
**Error:** buildx failed — gh CLI install step exited with code 22 (curl HTTP error)
**Root cause:** The Containerfile step that downloads/installs gh from GitHub releases is failing. This is unrelated to PR #160 changes (justfile.worktree, tests, CHANGELOG only). Likely upstream: gh release checksum mismatch, rate limit, or transient network.
**Planned fix:** None — our changes do not touch the Containerfile or gh install. Recommend retrying the workflow or investigating gh release availability.

---

# [Comment #4]() by [gerchowl]()

_Posted on February 23, 2026 at 08:08 AM_

## Question

**Context:** Autonomous solve-and-pr pipeline completed. PR #160 created. CI Build Container Image failed.

**Blocker:** Build fails when installing gh CLI in Containerfile (exit 22). Our PR only changed justfile.worktree, tests/bats/worktree.bats, CHANGELOG — no Containerfile changes.

**Options:**
1. Retry the workflow — may be transient (gh release checksum, rate limit)
2. Investigate gh install step — pin version or fix checksum logic
3. Merge as-is — BATS tests and lint pass locally; build failure is pre-existing/upstream

Please reply if you want a specific action.

---

# [Comment #5]() by [gerchowl]()

_Posted on February 23, 2026 at 08:12 AM_

## Autonomous Run Complete

- **Design:** posted
- **Plan:** posted (4 tasks)
- **Execute:** all tasks done (TDD: test first, then implementation)
- **Verify:** BATS 238/238 pass, lint pass
- **PR:** https://github.com/vig-os/devcontainer/pull/160
- **CI:** Build Container Image failed (gh CLI install, unrelated to our changes). Diagnosis and retry posted. Question for user on next steps.

