---
type: issue
state: open
created: 2026-02-20T10:11:58Z
updated: 2026-02-20T10:11:58Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/105
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T13:17:16.451Z
---

# [Issue 105]: [[BUG] PR table Reviewer column shows requested reviewers instead of actual reviewers](https://github.com/vig-os/devcontainer/issues/105)

### Description

The "Reviewer" column in the `just gh-issues` PR table displays users from `reviewRequests` (people who have been **asked** to review) rather than users from `reviews` (people who have **actually submitted** a review). This makes it appear as though a review has been submitted when none has.

### Steps to Reproduce

1. Create a PR and add a reviewer via `gh pr edit --add-reviewer <user>`
2. Do **not** submit any review
3. Run `just gh-issues`
4. Observe the "Reviewer" column shows the requested reviewer's login with no distinction

### Expected Behavior

The Reviewer column should distinguish between requested and completed reviewers:

- **Requested** (pending): `?gerchowl` — prefixed with `?` to indicate awaiting review
- **Reviewed** (submitted): `gerchowl` — plain name, no prefix

This way a single column conveys both states at a glance.

### Actual Behavior

The "Reviewer" column shows `gerchowl` for PR #100 with no distinction, even though `reviews` is empty (`[]`) — only `reviewRequests` contains that user.

```json
{
  "reviewDecision": "REVIEW_REQUIRED",
  "reviewRequests": [{"__typename": "User", "login": "gerchowl"}],
  "reviews": []
}
```

### Environment

- **OS**: macOS (darwin 24.5.0)
- **gh CLI**: current
- **Script**: `scripts/gh_issues.py` (version with Reviewer/Assignee columns from #99 scope)

### Additional Context

- The Reviewer column is part of the uncommitted `gh_issues.py` enhancements tracked by #99
- The `_fetch_prs` call currently doesn't include `reviewRequests` in its `--json` fields; the column implementation likely conflates the two data sources
- Related: #99 (parent), #104 (clickable issue links)

### Possible Solution

Merge both data sources into the Reviewer column:
1. Collect actual reviewers from `reviews` — display as plain login (e.g. `gerchowl`)
2. Collect pending reviewers from `reviewRequests` that haven't submitted a review — display with `?` prefix (e.g. `?gerchowl`)
3. Style `?`-prefixed names dimmed/italic to further distinguish visually

### Changelog Category

Fixed
