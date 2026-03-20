---
type: issue
state: closed
created: 2026-03-19T11:04:10Z
updated: 2026-03-19T13:02:12Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/369
comments: 0
labels: bug, priority:high, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:25.989Z
---

# [Issue 369]: [[BUG] Rollback workflow fails when local setup-env action is used without checkout](https://github.com/vig-os/devcontainer/issues/369)

## Chore Type
CI / Build change

## Description
The `Rollback on Failure` job in `release.yml` fails because it invokes the local action `./.github/actions/setup-env` without checking out the repository first.

This causes the rollback pipeline to fail with:
`Can't find 'action.yml', 'action.yaml' or 'Dockerfile' under '/home/runner/work/devcontainer/devcontainer/.github/actions/setup-env'. Did you forget to run actions/checkout before running your local action?`

## Acceptance Criteria
- [ ] `Rollback on Failure` performs a repository checkout before calling any local action path (e.g. `./.github/actions/setup-env`)
- [ ] Rollback job no longer fails with local action resolution errors
- [ ] A failed release run executes rollback steps successfully (or at minimum reaches rollback logic instead of failing in setup)

## Implementation Notes
- Target workflow: `.github/workflows/release.yml`
- In job `rollback`, add `actions/checkout` before the `Set up environment` step
- Keep behavior minimal and scoped to rollback path

## Related Issues
- Related release failure run: https://github.com/vig-os/devcontainer/actions/runs/23290944122
- Failing rollback job: https://github.com/vig-os/devcontainer/actions/runs/23290944122/job/67728158551

## Priority
High

## Changelog Category
No changelog needed

## Additional Context
This failure appears after `build-and-test` fails and currently prevents rollback logic from executing as intended.
