---
type: issue
state: closed
created: 2026-02-20T13:43:29Z
updated: 2026-02-20T14:19:43Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/115
comments: 0
labels: chore
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:34.749Z
---

# [Issue 115]: [[CHORE] Update PR template to align with commit types and release cycle](https://github.com/vig-os/devcontainer/issues/115)

### Chore Type

General task

### Description

The PR template (`.github/pull_request_template.md`) is out of sync with the current commit type conventions defined in `CLAUDE.md` and the branching strategy in `docs/RELEASE_CYCLE.md`.

Gaps identified:
- "Type of Change" lists 7 ad-hoc options instead of matching the canonical commit types (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`, `revert`, `style`)
- "Breaking change" is listed as a standalone type, but it's a modifier (`!`) on any type
- The template doesn't account for PRs targeting `release/X.Y.Z` branches (only dev workflow assumed)
- Checklist references `just docs` which may need verification against current justfile recipes
- The `pr:create` skill consumes this template — misalignment causes friction for the agent

### Acceptance Criteria

- [ ] "Type of Change" checkboxes align with canonical commit types from `CLAUDE.md`
- [ ] Breaking change is a separate modifier checkbox, not a type
- [ ] Template works for development PRs (to `dev`) and bugfix PRs (to `release/X.Y.Z`)
- [ ] Checklist items match current tooling (`just` recipes, conventions)
- [ ] `pr:create` skill still references the template correctly after changes

### Implementation Notes

Target file: `.github/pull_request_template.md`

Reference docs:
- `CLAUDE.md` (commit types)
- `docs/RELEASE_CYCLE.md` (branching strategy, PR workflows)
- `.cursor/skills/pr:create/SKILL.md` (skill that consumes the template)

The `assets/workspace/` copy may also need updating if it mirrors this template.

### Related Issues

Related to #79 (both address PR workflow conventions)

### Priority

Low

### Changelog Category

No changelog needed
