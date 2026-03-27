---
type: issue
state: open
created: 2026-03-12T07:47:15Z
updated: 2026-03-12T07:48:15Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/264
comments: 0
labels: chore, priority:low, area:ci, area:workspace, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-12T07:59:28.837Z
---

# [Issue 264]: [[CHORE] Remove unused workflow_call triggers from workspace CI templates](https://github.com/vig-os/devcontainer/issues/264)

## Chore Type
CI / Build change

## Description
`assets/smoke-test/.github/workflows/repository-dispatch.yml` no longer invokes reusable workflows via
`uses: ./.github/workflows/ci.yml` and `uses: ./.github/workflows/ci-container.yml`.

The workspace template workflows still declare `on.workflow_call`:
- `assets/workspace/.github/workflows/ci.yml`
- `assets/workspace/.github/workflows/ci-container.yml`

This issue tracks removing obsolete reusable-workflow entry points and any now-stale rationale comments tied to that mode.

## Acceptance Criteria
- [ ] Confirm there are no active callers that rely on `workflow_call` for workspace CI templates
- [ ] Remove `workflow_call` from `assets/workspace/.github/workflows/ci.yml`
- [ ] Remove `workflow_call` from `assets/workspace/.github/workflows/ci-container.yml`
- [ ] Remove/update related permission comments that only apply to reusable-workflow mode
- [ ] Validate workflow syntax and trigger behavior for PR + workflow_dispatch paths
- [ ] Update docs/changelog only if user-visible behavior or documented trigger model changes

## Implementation Notes
Target files:
- `assets/workspace/.github/workflows/ci.yml`
- `assets/workspace/.github/workflows/ci-container.yml`
- (optional, if needed) docs that mention reusable invocation assumptions

Keep diff minimal and scoped to trigger/permission-comment cleanup.

## Related Issues
- Related to #169

## Priority
Low

## Changelog Category
Changed

## Additional Context
This came from review of current local state where `repository-dispatch.yml` orchestrates deploy/PR flow and relies on PR-triggered CI rather than reusable `uses:` calls.
