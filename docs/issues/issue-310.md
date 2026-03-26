---
type: issue
state: open
created: 2026-03-13T16:40:10Z
updated: 2026-03-13T21:59:08Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/310
comments: 0
labels: chore, area:ci
assignees: none
milestone: 0.3.1
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:54.044Z
---

# [Issue 310]: [[CHORE] Add final-release step to publish GitHub Release with notes](https://github.com/vig-os/devcontainer/issues/310)

### Chore Type
CI / Build change

### Description
Add an explicit step in the release cycle to publish a proper GitHub Release for final versions (non-RC), including release notes.

### Acceptance Criteria
- [ ] Final version releases (e.g. `vX.Y.Z`) create a GitHub Release automatically (or via a documented release command step).
- [ ] RC versions (e.g. `vX.Y.Z-rc.N`) do **not** create a final GitHub Release.
- [ ] The created GitHub Release includes release notes generated from the finalized release content.
- [ ] The release process fails clearly if release notes generation/publishing fails.

### Implementation Notes
- Reuse existing release metadata/changelog as the source of truth for release notes.
- Gate release publication by version type (final vs RC).
- Keep this step integrated with the current release automation flow to avoid manual drift.

### Related Issues
Related to #300

### Priority
Medium

### Changelog Category
No changelog needed

### Additional Context
Goal: ensure every final release has a proper GitHub Release entry with notes, while RCs remain pre-release artifacts only.
