---
type: issue
state: open
created: 2026-02-24T15:22:45Z
updated: 2026-02-24T15:22:45Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/179
comments: 0
labels: refactor, area:workflow, effort:small
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-25T04:25:53.311Z
---

# [Issue 179]: [[REFACTOR] Move gh_issues.py into vig-utils and add entry point](https://github.com/vig-os/devcontainer/issues/179)

### Description

Move `scripts/gh_issues.py` into `packages/vig-utils`, create an entry point for running it, remove the shipped asset copy that is no longer needed, and adapt all references to the new location.

### Files / Modules in Scope

- `scripts/gh_issues.py` (source to migrate)
- `packages/vig-utils/**` (target module + entry point wiring)
- `assets/workspace/.devcontainer/scripts/gh_issues.py` (remove shipped asset copy)
- References/invocations that currently point to old paths

### Out of Scope

- New gh-issues features or UI changes
- Functional behavior changes beyond path/entrypoint migration
- Broader rewrite work tracked in `#145`

### Invariants / Constraints

- `just gh-issues` continues to work end-to-end
- Behavior/output remains equivalent after migration
- Existing tests and CI checks pass

### Acceptance Criteria

- [ ] `scripts/gh_issues.py` is moved under `packages/vig-utils`
- [ ] A supported entry point is created for invoking gh-issues
- [ ] `assets/workspace/.devcontainer/scripts/gh_issues.py` is removed
- [ ] All references are updated to the new entry point/location
- [ ] `just gh-issues` works after the migration
- [ ] All relevant tests pass
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Changed

### Additional Context

Related to parent issue `#145`.
