---
type: issue
state: open
created: 2026-02-18T16:59:19Z
updated: 2026-02-18T16:59:19Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/84
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T16:59:39.310Z
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
