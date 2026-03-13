---
type: issue
state: closed
created: 2026-02-20T13:48:23Z
updated: 2026-02-20T14:06:20Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/116
comments: 0
labels: chore
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:34.394Z
---

# [Issue 116]: [[CHORE] Define more granular CODEOWNERS rules](https://github.com/vig-os/devcontainer/issues/116)

### Chore Type

Configuration change

### Description

The current `.github/CODEOWNERS` file uses a catch-all `*` rule and only distinguishes a handful of paths (`.github/workflows/`, `.github/actions/`, `scripts/`, and a few security-sensitive files). As the repository grows, more granular ownership rules would improve review routing and ensure the right people are notified for changes in specific areas.

**Approach:** Start by analyzing the git history — commits, branches, and authors — to identify which contributors have been active in which areas of the codebase. Use this data (e.g. files/folders touched per author, commit frequency by path, branch authorship) to define ownership scopes grounded in actual contribution patterns rather than guesswork.

### Acceptance Criteria

- [ ] Analyze git history (commits, branches, authors) to map contributors to files, folders, and config areas
- [ ] Use the analysis as the basis for defining ownership scopes in `.github/CODEOWNERS`
- [ ] Add granular per-area ownership rules beyond the current catch-all
- [ ] Later (more specific) rules take precedence over earlier (general) rules, following CODEOWNERS semantics
- [ ] Existing rules for security-sensitive files are preserved

### Implementation Notes

- Start with `git log --format='%aN' -- <path>`, `git shortlog -sn -- <path>`, or similar to build a contributor-by-area matrix.
- CODEOWNERS uses last-match-wins precedence — keep the `*` catch-all first, add specific overrides after.
- Currently there is only one maintainer (`@c-vigo`). The granularity is useful for self-documenting ownership areas and preparing for future contributors.
- Consider whether `assets/workspace/.github/CODEOWNERS` (the template shipped to downstream workspaces) should also be updated.

### Priority

Low

### Changelog Category

No changelog needed
