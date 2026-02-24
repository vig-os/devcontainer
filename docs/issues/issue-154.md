---
type: issue
state: open
created: 2026-02-22T09:34:10Z
updated: 2026-02-23T23:19:17Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/154
comments: 3
labels: bug, area:workflow
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-24T04:24:09.870Z
---

# [Issue 154]: [[BUG] worktree-start preflight gaps — agent --print hang and gh repo set-default ambiguity](https://github.com/vig-os/devcontainer/issues/154)

### Description

`just worktree-start` (aliased as `wt-start`) has two preflight gaps that cause silent or confusing failures. Both should be caught early with clear diagnostics.

---

### Problem 1: `agent --print` hangs during branch name derivation

`agent --print` (cursor-agent CLI `2026.02.13-41ac335`) hangs indefinitely in headless mode regardless of model. Because the script uses `set -euo pipefail`, the failed command substitution on line 130 of `justfile.worktree` kills the script before the explicit error handler on line 138 ever runs.

**Steps to Reproduce**

1. Ensure issue has no linked branch (e.g. `gh issue develop --list <issue>` returns empty)
2. Run `just wt-start <issue> "/worktree_solve-and-pr"`
3. The recipe reaches the `agent --print` call to derive a branch name summary
4. `agent --print` hangs indefinitely, eventually the script fails

**Actual Behavior**

```
[*] No linked branch for issue #121. Creating one...
error: Recipe `worktree-start` failed with exit code 1
```

No indication of what failed.

**Possible Solution**

1. Wrap the `agent --print` call in `timeout 30` (or similar) so it can't hang indefinitely
2. Capture the exit code explicitly instead of relying on `set -e` to kill the script:
   ```bash
   SUMMARY=$(timeout 30 agent --print --yolo --trust --model "$MODEL" "..." | tail -1 | tr -d '[:space:]') || true
   ```
3. Keep the existing guard (`if [ -z "$SUMMARY" ]`) reachable so the diagnostic message and manual workaround instructions are printed

---

### Problem 2: `gh` commands fail when multiple remotes exist (no default repo)

When a collaborator adds a fork as a second remote (e.g. `origin` + `nacholiya`), `gh` can no longer auto-detect which repository to target. All `gh` API calls (`gh issue develop`, `gh issue view`, `gh repo view`, etc.) fail with:

```
No default remote repository has been set. To learn more about the default repository, run: gh repo set-default --help
```

The recipe exits with `exit code 1` and no further context.

**Steps to Reproduce**

1. Add a second remote pointing to a fork: `git remote add myfork git@github.com:user/devcontainer`
2. Run `just wt-start <issue> "/worktree_solve-and-pr"`
3. The first `gh` command fails with the "no default remote" error

**Possible Solution**

Add a preflight check near the existing prerequisites block:

1. Run `gh repo set-default --view` to test if a default is set
2. If not, auto-resolve from `origin` remote (`git remote get-url origin` → extract `owner/repo`) and run `gh repo set-default owner/repo`
3. Or fail with a clear message: `"Multiple remotes detected. Run: gh repo set-default <owner/repo>"`

---

### Expected Behavior (both problems)

- Clear, actionable error messages when something fails
- Manual workaround instructions included in the error output
- Preflight checks catch known failure modes before the main logic runs

### Environment

- **OS**: macOS 24.5.0 (darwin, arm64)
- **cursor-agent CLI**: 2026.02.13-41ac335
- **just**: latest
- **Shell**: zsh

### Acceptance Criteria

- [ ] `agent --print` call has a timeout; failure produces a clear error with manual workaround
- [ ] `gh repo set-default` is checked before any `gh` API calls; auto-resolved or error with instructions
- [ ] Both failures tested manually by reproducing the conditions

### Changelog Category

Fixed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 23, 2026 at 07:53 AM_

## Design

Brainstorm: agents for branch naming — testing, local models, devcontainer.

### Current State

- **Branch naming flow** (`justfile.worktree`): When no linked branch exists, `worktree-start` uses `agent --print --yolo --trust --model $(_read_model lightweight)` to derive a kebab-case summary from the issue title.
- **Lightweight model**: `composer-1.5` (Cursor API).
- **Tests**: `worktree.bats` covers `resolve-branch.sh`, tmux, and worktree-attach — but **not** the agent-based branch naming.

---

### 1. How to Test Agent-Based Branch Naming

**Option A: Unit-style tests with mock agent**
- Introduce a wrapper script (e.g. `scripts/derive-branch-summary.sh`) that accepts issue title + rules path, calls `agent --print`, returns summary.
- In tests, inject a mock: `BRANCH_SUMMARY_CMD="echo fix-login-bug"` or similar.
- BATS tests assert the wrapper produces valid kebab-case output when given known inputs.

**Option B: Snapshot / golden tests**
- Record expected summaries for a fixed set of issue titles.
- Run the real agent in CI (or locally) and diff against snapshots.
- Pros: catches quality regressions. Cons: flaky if model behavior drifts.

**Option C: Deterministic fallback + agent optional**
- Implement a simple heuristic (e.g. `tr '[:upper:]' '[:lower:]' | tr -s ' ' '-' | sed 's/^...//'`) as fallback.
- Use agent only when heuristic is ambiguous or when explicitly requested.
- Tests focus on the heuristic; agent behavior is optional/exploratory.

**Option D: Contract tests**
- Define a contract: "Given title X, output must match regex `^[a-z0-9]+(-[a-z0-9]+)*$`".
- Test that the agent output satisfies the contract.
- Doesn't validate quality, only format.

---

### 2. Small Local Models in the Devcontainer

**Candidates:**
- **Ollama + llama3.2:1b** (~1.3GB) — fast, good for simple text tasks
- **Ollama + phi3:mini** (~2.3GB) — better instruction-following
- **Ollama + gemma2:2b** (~1.6GB) — good quality/size tradeoff
- **llama.cpp** — no server, direct CLI inference

**Integration options:**
1. **Ollama as sidecar** — Add `ollama` service in `docker-compose.project.yaml`, mount model cache volume. Agent would need to call Ollama instead of Cursor API (or a custom script would).
2. **Ollama in postCreate** — Install Ollama in devcontainer image or via postCreateCommand, pull small model on first run. Increases image size and startup time.
3. **Dedicated script using Ollama** — Replace `agent --print` with a script that calls `ollama run <model> "<prompt>"` (or curl to Ollama API), parses last line as summary. No Cursor API for this step; fully local.
4. **cursor-agent + local model** — If cursor-agent supports a local backend, configure it. Otherwise, use a separate script that talks to Ollama.

**Tradeoffs:** Pros: no API key, no network, predictable latency, works offline. Cons: image size, startup time, memory; quality may be lower than cloud models for edge cases.

---

### 3. Putting Local Models into the Devcontainer

**Minimal approach:**
- Add `ollama` service in `docker-compose.project.yaml` with model cache volume.
- Add `scripts/derive-branch-summary-ollama.sh` that uses `ollama run` or HTTP API.
- In `justfile.worktree`, branch: use `agent --print` when CURSOR_API_KEY set, else use Ollama script when OLLAMA_HOST set or when running in devcontainer.

**Hybrid strategy:** Default to Cursor API for best quality; fallback to Ollama when API unavailable (no key, offline); override via `BRANCH_NAMING_BACKEND=ollama`.

**Testing with local models:** In CI, either skip agent-based tests, use mock (`BRANCH_SUMMARY_CMD`), or run a tiny Ollama model in a CI service container (slower, more complex).

---

### 4. Suggested Path (YAGNI)

1. **Extract the agent call** into `scripts/derive-branch-summary.sh` that accepts `TITLE` and `NAMING_RULE` path, calls `agent --print`, returns summary.
2. **Add mock for tests** — `BRANCH_SUMMARY_CMD` env var to override the agent.
3. **Add BATS tests** for the wrapper (format checks, mock-based behavior).
4. **Defer local models** until there's a concrete need (offline, no API key, cost).

---

# [Comment #2]() by [gerchowl]()

_Posted on February 23, 2026 at 11:12 PM_

## Implementation Plan

Issue: #154
Branch: bugfix/154-worktree-start-silent-fail-agent-print-hang

### Tasks

- [ ] Task 1: Add gh repo set-default preflight before any gh API calls — `justfile.worktree` — verify: `just --list | grep worktree-start`
- [ ] Task 2: Extract agent branch-summary call to scripts/derive-branch-summary.sh with timeout and BRANCH_SUMMARY_CMD mock — `scripts/derive-branch-summary.sh`, `justfile.worktree` — verify: `BRANCH_SUMMARY_CMD="echo test-summary" just worktree-start 154 "" 2>&1 | head -5` (or existing worktree path)
- [ ] Task 3 (RED): Add BATS test for derive-branch-summary timeout when mock hangs — `tests/bats/worktree.bats` — verify: `just test-bats` (new test fails)
- [ ] Task 4 (GREEN): Implement timeout in derive-branch-summary.sh — `scripts/derive-branch-summary.sh` — verify: `just test-bats` (all pass)
- [ ] Task 5 (RED): Add BATS test for derive-branch-summary error message when mock fails — `tests/bats/worktree.bats` — verify: `just test-bats` (new test fails)
- [ ] Task 6 (GREEN): Ensure derive-branch-summary prints clear error with manual workaround — `scripts/derive-branch-summary.sh` — verify: `just test-bats` (all pass)
- [ ] Task 7 (RED): Add BATS test for gh preflight when no default repo — `tests/bats/worktree.bats` — verify: `just test-bats` (new test fails)
- [ ] Task 8 (GREEN): Implement gh preflight with auto-resolve or clear error — `justfile.worktree` — verify: `just test-bats` (all pass)


---

# [Comment #3]() by [gerchowl]()

_Posted on February 23, 2026 at 11:19 PM_

## Autonomous Run Complete

- Design: posted (existing)
- Plan: posted (8 tasks)
- Execute: all tasks done
- Verify: BATS tests pass (12/12), lint pass, precommit pass (hadolint skipped — Docker daemon not running locally)
- PR: https://github.com/vig-os/devcontainer/pull/165
- CI: pending (workflows may take a few minutes to start)

