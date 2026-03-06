---
type: issue
state: open
created: 2026-03-04T13:02:10Z
updated: 2026-03-04T13:23:53Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/219
comments: 0
labels: refactor, priority:medium, area:workspace, effort:medium, semver:patch
assignees: none
milestone: 0.3
projects: none
relationship: none
synced: 2026-03-05T04:18:18.378Z
---

# [Issue 219]: [[REFACTOR] Refurbish workspace justfile structure for devc/project split](https://github.com/vig-os/devcontainer/issues/219)

### Description

Refurbish workspace justfile structure to separate devcontainer lifecycle recipes from project-level recipes and improve maintainability ahead of smoke-test work in #169.
This includes fixing a typo in `.vscode/settings.json`, renaming `assets/workspace/.devcontainer/justfile.base` to `justfile.devc`, and moving non-devcontainer recipes (starting with testing/syncing) into `assets/workspace/justfile.project`.

### Files / Modules in Scope

- `.vscode/settings.json`
- `assets/workspace/.devcontainer/justfile.base` -> `assets/workspace/.devcontainer/justfile.devc`
- `assets/workspace/justfile` (imports updated)
- `assets/workspace/justfile.project`
- Any template sync/manifests that reference `justfile.base` under `assets/workspace/.devcontainer/`

### Out of Scope

- Behavioral changes to devcontainer startup/teardown commands
- Changes to CI workflows or release pipelines
- Large script migration already tracked by #217
- New features unrelated to justfile structure

### Invariants / Constraints

- Existing `just` command behavior remains backward-compatible for current recipe names (or clearly documented aliases if needed)
- Workspace bootstrap/sync still includes all required justfiles
- No regression in developer workflows for container lifecycle commands
- Minimal diff focused only on justfile structure and typo correction

### Acceptance Criteria

- [ ] Typo in `.vscode/settings.json` is corrected
- [ ] `assets/workspace/.devcontainer/justfile.base` is renamed to `assets/workspace/.devcontainer/justfile.devc`
- [ ] `assets/workspace/justfile` imports updated to the new filename
- [ ] `justfile.devc` contains only devcontainer-focused recipes
- [ ] Testing/syncing recipes are moved to `assets/workspace/justfile.project`
- [ ] Additional candidate moves are inventoried (for follow-up) to prepare #169
- [ ] Existing justfile commands continue to work as expected
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Changelog Category

Changed

### Additional Context

- Part of #169
- Related: #71 (broader justfile expansion), #217 (scripts reorganization)
