---
type: issue
state: closed
created: 2026-03-13T13:16:31Z
updated: 2026-03-13T13:47:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/295
comments: 0
labels: chore, priority:medium, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:55.103Z
---

# [Issue 295]: [[CHORE] Align sync-main-to-dev checkout action pin with repository standard](https://github.com/vig-os/devcontainer/issues/295)

## Chore Type
CI / Build change

## Description
The `sync-main-to-dev` workflow currently pins `actions/checkout` to `34e114876b0b11c390a56381ad16ebd13914f8d5  # v4` in two steps, while the repository standard in other workflows is `de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2`.

Align both checkout steps to the repository-standard pinned SHA to keep workflow behavior and supply-chain posture consistent.

## Acceptance Criteria
- [ ] Update both `actions/checkout` entries in `.github/workflows/sync-main-to-dev.yml` to the repository-standard pin (`de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2`)
- [ ] Ensure mirrored/generated workflow assets remain consistent where applicable
- [ ] CI/workflow lint checks pass after the update

## Implementation Notes
- Target file: `.github/workflows/sync-main-to-dev.yml`
- Context: Copilot review on `vig-os/devcontainer-smoke-test#27` identified the mismatch.
- Keep scope limited to pin alignment only (no behavioral refactors).

## Related Issues
Related to #169

## Priority
Medium

## Changelog Category
Changed

## Additional Context
Follow-up from review feedback on:
https://github.com/vig-os/devcontainer-smoke-test/pull/27
