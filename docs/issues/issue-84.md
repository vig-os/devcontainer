---
type: issue
state: open
created: 2026-02-18T16:59:19Z
updated: 2026-02-18T19:10:07Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/84
comments: 1
labels: feature
assignees: gerchowl
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-19T00:08:06.072Z
---

# [Issue 84]: [[FEATURE] Add just recipe for GitHub issue and PR dashboard](https://github.com/vig-os/devcontainer/issues/84)

### Description

Add a `just gh-issues` recipe that displays open GitHub issues grouped by milestone in a rich, color-coded table, along with open pull requests. Provides a quick terminal-based project dashboard without leaving the CLI. Ships to all downstream workspaces via the sync manifest.

### Problem Statement

There's no quick way to get an at-a-glance overview of open issues grouped by milestone, with structured columns for type, priority, scope, effort, semver impact, assignee, and linked branch — all from the terminal.

### Proposed Solution

- New `justfile.gh` with a `gh-issues` recipe under a `[github]` group
- Python script `scripts/gh_issues.py` using `rich` tables for formatted output
- Issues grouped by milestone, each as a table with columns: #, Type, Title, Assignee, Branch, Prio, Scope, Effort, SemVer
- Linked development branches fetched in a single GraphQL call
- Open PRs in a separate section with: #, Title, Author, Branch, Review status, Delta
- Sync manifest entries to ship both files to downstream workspaces (`.devcontainer/justfile.gh` + `.devcontainer/scripts/gh_issues.py`)
- Downstream `justfile` template updated to import `.devcontainer/justfile.gh`

### Alternatives Considered

- Pure bash with `printf` — alignment breaks on long titles
- `gh issue list --json` + `jq` — flat output, no grouping or color

### Impact

- All downstream projects benefit from the dashboard out of the box
- No breaking changes, purely additive

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 05:01 PM_

## Implementation Plan (retroactive)

Issue: #84
Branch: feature/67-declarative-sync-manifest (bundled with #67 work)

### Tasks

- [x] Task 1: Create `justfile.gh` with `gh-issues` recipe under `[github]` group — `justfile.gh` — verify: `just gh-issues`
- [x] Task 2: Create `scripts/gh_issues.py` with rich table rendering for issues grouped by milestone — `scripts/gh_issues.py` — verify: `uv run python scripts/gh_issues.py`
- [x] Task 3: Import `justfile.gh` from root `justfile` — `justfile` — verify: `just --list` shows `[github]` group
- [x] Task 4: Add PR section to `scripts/gh_issues.py` with author, branch, review status, delta — `scripts/gh_issues.py` — verify: `just gh-issues` shows PR table
- [x] Task 5: Add linked branch column via GraphQL batch query — `scripts/gh_issues.py` — verify: issues with linked branches show branch name
- [x] Task 6: Use `source_directory()` in `justfile.gh` for portable script path resolution — `justfile.gh` — verify: `just --evaluate _gh_scripts`
- [x] Task 7: Add sync manifest entries for `justfile.gh` → `.devcontainer/justfile.gh` and `scripts/gh_issues.py` → `.devcontainer/scripts/gh_issues.py` — `scripts/sync_manifest.py` — verify: `just sync-workspace`
- [x] Task 8: Update downstream workspace `justfile` to import `.devcontainer/justfile.gh` — `assets/workspace/justfile` — verify: synced file includes import
- [x] Task 9: Update CHANGELOG.md with #84 entry under Added — `CHANGELOG.md`

### Notes

- TDD skipped: non-testable change (CLI tooling, templates, config). Script has no unit-testable logic beyond subprocess calls and rich rendering.
- `scripts/gh_issues.py` depends on `rich` (transitive via `bandit`), `gh` CLI, and GitHub API access.

