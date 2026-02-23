---
type: issue
state: open
created: 2026-02-20T15:09:51Z
updated: 2026-02-21T23:37:45Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/121
comments: 3
labels: bug
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-22T04:23:22.579Z
---

# [Issue 121]: [[BUG] gh_issues.py cross-ref misses PRs linked via Refs: instead of Closes/Fixes](https://github.com/vig-os/devcontainer/issues/121)

### Description

The `_build_cross_refs` function in `scripts/gh_issues.py` only detects issue↔PR links via branch name matching and `Closes/Fixes/Resolves` keywords in PR bodies. It does not detect `Refs: #<number>` — which is the project's standard commit/PR reference format (see `CLAUDE.md`).

### Problem

PR #106 merged with `Refs: #102` in its body. GitHub did not auto-close issue #102 and did not create a formal PR↔issue link because `Refs:` is not a GitHub closing keyword. The `gh-issues` table also fails to show the PR↔issue cross-reference since `_build_cross_refs` doesn't parse `Refs:`.

### Expected Behavior

`_build_cross_refs` should also match `Refs: #<number>` (and comma-separated variants like `Refs: #102, #103`) in PR bodies to build the issue↔PR mapping.

### Reproduction

1. Create a PR whose body contains `Refs: #102` (no `Closes`/`Fixes`)
2. Run `just gh-issues`
3. Observe that the PR column for issue #102 is empty

### Proposed Fix

Add a regex for `Refs:\s*#(\d+)` (with comma-separated support) to `_build_cross_refs` alongside the existing `_CLOSING_RE`.
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 11:29 PM_

## Design

**Problem:** `_build_cross_refs` only detects issue↔PR links via branch names and `Closes/Fixes/Resolves` keywords. The project uses `Refs: #<n>` as the standard format (CLAUDE.md), which GitHub does not auto-link.

**Solution:** Add a regex `Refs:\s*#(\d+)` (with comma-separated support) alongside `_CLOSING_RE` in `_build_cross_refs`. Both regexes feed into the same `linked` set — no structural change.

**Files:** `scripts/gh_issues.py` only.

**Testing:** Add unit tests in `tests/test_gh_issues.py` for `Refs: #102` and `Refs: #102, #103` (TDD: test first, then implementation).

---

# [Comment #2]() by [gerchowl]()

_Posted on February 21, 2026 at 11:29 PM_

## Implementation Plan

Issue: #121
Branch: bugfix/121-cross-ref-misses-refs-linked-prs

### Tasks

- [ ] Task 1: Add failing unit tests for Refs: #N and Refs: #N, #M in `tests/test_gh_issues.py` — verify: `pytest tests/test_gh_issues.py::TestBuildCrossRefs -v`
- [ ] Task 2: Add _REFS_RE regex and use it in _build_cross_refs in `scripts/gh_issues.py` — verify: `pytest tests/test_gh_issues.py::TestBuildCrossRefs -v`

---

# [Comment #3]() by [gerchowl]()

_Posted on February 21, 2026 at 11:37 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (2 tasks)
- Execute: all tasks done
- Verify: all checks pass
- PR: https://github.com/vig-os/devcontainer/pull/150
- CI: all checks pass

