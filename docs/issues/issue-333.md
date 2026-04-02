---
type: issue
state: closed
created: 2026-03-17T07:01:39Z
updated: 2026-03-17T09:24:23Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/333
comments: 0
labels: chore
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:23.623Z
---

# [Issue 333]: [[CHORE] Ship CHANGELOG.md in devcontainer image and smoke-test deployment root](https://github.com/vig-os/devcontainer/issues/333)

## Chore Type
CI / Build change

## Description
Ensure `CHANGELOG.md` is distributed as part of the devcontainer image workspace payload so it is available inside `assets/workspace/.devcontainer/`.

Also update smoke-test deployment behavior to copy `CHANGELOG.md` into the repository root so it serves as the smoke-test repository changelog as well.

## Acceptance Criteria
- [ ] Devcontainer image packaging includes `CHANGELOG.md` in the workspace payload used by downstream consumers
- [ ] `CHANGELOG.md` is present under `assets/workspace/.devcontainer/` in the distributed image/workspace output
- [ ] Smoke-test deployment copies `CHANGELOG.md` to the smoke-test repository root
- [ ] Smoke-test repository root `CHANGELOG.md` matches source changelog content for the deployed version
- [ ] Existing release/smoke-test automation remains green after this change

## Implementation Notes
- Likely touch points:
  - workspace/bootstrap/init logic that defines shipped files
  - smoke-test deploy workflow/scripts that prepare repository contents
- Keep `CHANGELOG.md` as single source and copy from canonical source during deployment (no divergent maintenance).

## Related Issues
Related to #331

## Priority
Medium

## Changelog Category
Changed

## Additional Context
Requested objective: make changelog accessible inside the devcontainer workspace and reuse it as the smoke-test repository changelog in deployment output.
