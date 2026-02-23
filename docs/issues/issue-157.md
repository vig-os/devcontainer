---
type: issue
state: open
created: 2026-02-22T09:52:12Z
updated: 2026-02-22T09:52:12Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/157
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-23T04:30:07.108Z
---

# [Issue 157]: [[FEATURE] Show pipeline phase (progress) per issue in gh-issues dashboard](https://github.com/vig-os/devcontainer/issues/157)

### Description

Add a "Phase" column to the `just gh-issues` issue table that shows where each issue stands in the skill pipeline (as defined in `docs/SKILL_PIPELINE.md`). The phase is inferred from issue comments and linked PR/branch state, giving an at-a-glance view of progress without clicking into each issue.

### Problem Statement

The `just gh-issues` dashboard shows issues with their metadata (priority, effort, assignee, branch, PR) but gives no signal about *how far along* the work is. An issue might have a branch but no design, or a full design but no implementation plan, or code already in review. Currently, you have to open each issue and scan the comments to understand its progress. For project triage and daily standups, a compact phase indicator would save significant context-switching.

### Proposed Solution

#### Phase column (issues table)

Detect the pipeline phase per issue by scanning issue comments for well-known headings (mirroring the state detection in `worktree_solve-and-pr`), plus branch/PR state:

| Detected signal | Phase label |
|---|---|
| No branch, no comments | `Backlog` |
| Branch exists, no design comment | `Claimed` |
| `## Design` comment found | `Design` |
| `## Implementation Plan` comment found | `Planned` |
| Commits on branch (or plan + branch with commits) | `In Progress` |
| Linked PR exists (open) | `In Review` |
| Linked PR merged | `Done` |

Display as a color-coded "Phase" column (e.g., dim for Backlog, cyan for Claimed, yellow for Design/Planned, green for In Progress/In Review).

#### Column consolidation (PRs table) — open question

The current PR table has 10 columns (`#`, `Title`, `Author`, `Assignee`, `Issues`, `Branch`, `CI`, `Review`, `Reviewer`, `Delta`) which causes heavy truncation on normal terminal widths. Consider merging columns that carry related information into compact representations:

**Review + Reviewer → single "Review" column** using icons/shorthand per reviewer:

| State | Display |
|---|---|
| Review requested | `?alice` (dim) |
| Pending / commented | `◎bob` (yellow) |
| Approved | `✓carol` (green) |
| Changes requested | `✗dave` (red) |

This preserves all information (who + state) in one column instead of two, freeing horizontal space for the new Phase column and reducing truncation overall.

Other candidates for consolidation:
- **Author + Assignee** — often the same person on solo projects; could merge into `Owner` showing author, with assignee only when different.
- **Branch** — already partially redundant with `Issues` column (branch name encodes issue number); could shorten or drop in favour of issue link.

> **Question:** Which column merges feel right? The Review+Reviewer merge seems like the clearest win. Author+Assignee and Branch trimming are more opinionated — worth doing in the same pass or separate issue?

### Alternatives Considered

- **GitHub Projects board** — provides a Kanban view but isn't integrated into the terminal dashboard and doesn't auto-detect phase from comments.
- **Manual labels** (e.g., `phase:design`, `phase:in-progress`) — requires discipline to update. Auto-detection from existing artifacts is more reliable and zero-overhead.

### Additional Context

- This should be a sub-issue of #145 (Rewrite gh-issues dashboard).
- The phase detection logic mirrors `worktree_solve-and-pr`'s state detection (see `docs/SKILL_PIPELINE.md` § State Detection).
- The implementation needs a GraphQL or REST call to fetch issue comments (at least headings) — consider batching to avoid N+1 queries.

### Impact

- **Beneficiaries:** Anyone using `just gh-issues` for triage or daily planning.
- **Breaking change:** No — additive column in the issue table, consolidation preserves information.

### Changelog Category

Added

### Acceptance Criteria

- [ ] Phase column renders in issue table with color-coded phase label
- [ ] Phase detection covers: Backlog, Claimed, Design, Planned, In Progress, In Review
- [ ] At least Review+Reviewer column merge implemented in PR table
- [ ] No information loss from column consolidation
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)
