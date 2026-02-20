---
type: issue
state: open
created: 2026-02-20T10:00:14Z
updated: 2026-02-20T15:25:13Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/103
comments: 2
labels: feature, area:workflow, effort:large, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:35.960Z
---

# [Issue 103]: [[FEATURE] Enhance worktree workflow and autonomous agent integration](https://github.com/vig-os/devcontainer/issues/103)

### Description

Improve the worktree-based autonomous development workflow by addressing configuration management, bug fixes, and PR automation enhancements. This is a parent issue tracking multiple related improvements to the `just worktree-*` recipes and autonomous agent integration.

### Problem Statement

The worktree workflow has evolved organically and now has several areas that need systematic improvement:

1. **Configuration scattered across recipes** - Agent model selections were hardcoded in justfile recipes rather than being centrally configured
2. **Branch resolution bugs** - `gh issue develop --list` now returns tab-separated output (`branch\tURL`), breaking the `grep -oE '[^ ]+$'` pattern that expects space-separated output
3. **Limited PR automation** - The autonomous PR creation cannot specify reviewers, requiring manual follow-up

These issues affect the reliability and maintainability of the autonomous agent workflow that powers parallel development via worktrees.

### Proposed Solution

Address these issues through focused sub-issues:

1. **Config as SSoT** - Extract agent model assignments to `.cursor/agent-models.toml` with task tiers (lightweight, autonomous)
2. **Fix branch resolution** - Update the parsing logic to handle tab-separated `gh` output correctly
3. **Optional PR reviewer param** - Thread an optional `reviewer` parameter through `worktree-start` so autonomous PRs can assign reviewers

Each improvement maintains backward compatibility and follows the repo's Single Source of Truth principle.

### Alternatives Considered

- **Monolithic refactor** - Rejected in favor of incremental, traceable improvements via sub-issues
- **Wait for native Cursor worktree support in devcontainers** - Still broken as of Feb 2026, CLI workflow remains necessary

### Additional Context

The worktree workflow enables true parallel autonomous development where multiple agents can work on different issues simultaneously in isolated environments. Reliability and configuration management are critical for this workflow.

Related:
- Cursor forum issue: https://forum.cursor.com/t/cursor-parallel-agents-in-wsl-devcontainers-misresolve-worktree-paths-and-context/145711

### Impact

- Improves reliability and maintainability of autonomous agent workflows
- Makes configuration explicit and centralized (SSoT)
- Backward compatible - all changes are additive or fix existing bugs
- Benefits anyone using `just worktree-start` for parallel development

### Changelog Category

Changed
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 10:00 AM_

## Sub-issues

- #102 - Add optional reviewer parameter to worktree-start

---

# [Comment #2]() by [gerchowl]()

_Posted on February 20, 2026 at 03:25 PM_

## Implementation Plan

Issue: #103
Branch: `feature/103-worktree-workflow-enhancements`

**Scope:** Goal 2 — Fix branch resolution for tab-separated `gh issue develop --list` output. (Goals 1 and 3 are already done.)

**Bug:** `gh issue develop --list` returns `branch<TAB>URL`. The current parsing `grep -oE '[^ ]+$'` treats tab as non-space, capturing the entire line instead of just the branch name. Fix: replace with `head -1 | cut -f1`.

### Tasks (TDD)

- [ ] Task 1 (RED): Write BATS test asserting tab-separated `gh issue develop` output is parsed to extract only the branch name — `tests/bats/worktree.bats` — verify: `bats tests/bats/worktree.bats` fails
- [ ] Task 2 (GREEN): Fix line 117 of `justfile.worktree` — replace `grep -oE '[^ ]+$' | head -1` with `head -1 | cut -f1` for issue branch resolution — `justfile.worktree` — verify: `bats tests/bats/worktree.bats` passes
- [ ] Task 3 (GREEN): Fix line 154 of `justfile.worktree` — same replacement for parent branch resolution — `justfile.worktree` — verify: `bats tests/bats/worktree.bats` passes
- [ ] Task 4: Update CHANGELOG — add entry under `## Unreleased` > `Fixed` — `CHANGELOG.md` — verify: visual check

### Commit sequence

1. `test: add BATS test for tab-separated branch resolution parsing` (RED)
2. `fix: parse tab-separated gh issue develop output in worktree recipes` (GREEN, tasks 2+3)
3. `docs: update CHANGELOG for branch resolution fix` (task 4)

