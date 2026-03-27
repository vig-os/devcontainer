---
type: issue
state: closed
created: 2026-03-12T13:09:08Z
updated: 2026-03-12T14:03:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/276
comments: 0
labels: chore, priority:high, area:ci, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: 0.3
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:57.536Z
---

# [Issue 276]: [[CHORE] Enforce release PR title format as release: X.Y.Z](https://github.com/vig-os/devcontainer/issues/276)

## Chore Type
CI / Build change

## Description
The release PR failed the \"Validate PR Title\" check because the current title format (`Release 0.3.0`) does not satisfy repository commit-title rules.

Standardize release PR titles to:
- `release: X.Y.Z`

This should be applied by release automation and documented in release process guidance.

## Acceptance Criteria
- [ ] Release PRs are created with title format `release: X.Y.Z`
- [ ] `Validate PR Title` passes for release PRs
- [ ] Release workflow/tests/docs are updated so this format is preserved
- [ ] Existing release PR creation path is validated with a real or dry-run check

## Implementation Notes
- Investigate where release PR titles are generated in workflows/scripts.
- Update release PR title generation from `Release X.Y.Z` to `release: X.Y.Z`.
- Verify compatibility with `validate-commit-msg --subject-only` / PR title checks.
- Check whether PR template hints should be updated for release branches.

## Related Issues
- Related to PR #270
- Failed run: https://github.com/vig-os/devcontainer/actions/runs/23002702709/job/66791079620?pr=270

## Priority
High

## Changelog Category
No changelog needed

## Additional Context
This blocks merging the release PR until title validation succeeds.
