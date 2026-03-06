---
type: issue
state: closed
created: 2026-02-24T12:49:22Z
updated: 2026-02-24T18:45:26Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/174
comments: 3
labels: bug
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:54.414Z
---

# [Issue 174]: [[BUG] Issue numbers in PR table 'Issues' column are not clickable links](https://github.com/vig-os/devcontainer/issues/174)

### Description

In the `just gh-issues` dashboard, the "Issues" column in the PR table renders issue numbers with color styling only (`_styled`), not as clickable terminal hyperlinks (`_gh_link`). This is inconsistent with how issue numbers and PR numbers are rendered elsewhere in the dashboard.

### Steps to Reproduce

1. Run `just gh-issues`
2. Look at the PR table, "Issues" column
3. Try to click on an issue number (e.g. `#143`)

### Expected Behavior

Issue numbers in the PR table's "Issues" column should be clickable hyperlinks (using Rich's `[link=...]` markup), just like PR numbers in the `#` column and issue numbers in the issues table.

### Actual Behavior

Issue numbers in the "Issues" column are styled with cyan color but are plain text — not clickable. The code at line 483 uses `_styled(f"#{n}", "cyan")` instead of `_gh_link(owner_repo, n, "issues")`.

### Environment

- **OS**: macOS (darwin 24.5.0)
- **Script**: `scripts/gh_issues.py`

### Possible Solution

Replace the `_styled` call with `_gh_link` in `_build_pr_table` (line ~483):

```python
# Current:
" ".join(_styled(f"#{n}", "cyan") for n in sorted(linked))

# Fix:
" ".join(_gh_link(owner_repo, n, "issues") for n in sorted(linked))
```

Note: `_gh_link` doesn't include the `#` prefix, so the display format will change slightly (from `#143` to `143` as a link). If the `#` prefix is desired, `_gh_link` could be updated to include it.

### Changelog Category

Fixed

### TDD Acceptance Criteria

- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
---

# [Comment #1]() by [gerchowl]()

_Posted on February 24, 2026 at 12:50 PM_

## Design

**Problem**: Issue numbers in the PR table "Issues" column are styled with cyan but not clickable. The code at line 636 uses `_styled(f"#{n}", "cyan")` instead of `_gh_link`.

**Solution**: Replace `_styled` with `_gh_link(owner_repo, n, "issues")` in `_build_pr_table` for the issues cell. This matches how PR numbers (line 642) and issue numbers in the issues table (line 399) are rendered.

**Display change**: Numbers will show as `143` (link) instead of `#143` (plain text). This is consistent with `_gh_link` usage elsewhere and acceptable per the issue.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 24, 2026 at 12:50 PM_

## Implementation Plan

Issue: #174
Branch: bugfix/174-pr-table-issues-clickable-links

### Tasks

- [x] Task 1: Replace `_styled` with `_gh_link` for issue numbers in PR table Issues column — `scripts/gh_issues.py` — verify: `just test`

---

# [Comment #3]() by [gerchowl]()

_Posted on February 24, 2026 at 12:54 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (1 task)
- Execute: all tasks done
- Verify: all checks pass
- PR: https://github.com/vig-os/devcontainer/pull/175
- CI: all checks pass (PR title fix applied: scope `gh_issues` → `gh-issues` for validator)

