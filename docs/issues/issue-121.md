---
type: issue
state: open
created: 2026-02-20T15:09:51Z
updated: 2026-02-20T15:09:51Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/121
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:34.044Z
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
