---
type: issue
state: closed
created: 2026-03-13T12:57:31Z
updated: 2026-03-13T13:15:06Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/293
comments: 1
labels: chore, priority:high, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: 0.3
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:55.374Z
---

# [Issue 293]: [[CHORE] Fix repository-dispatch branch reset boolean payload](https://github.com/vig-os/devcontainer/issues/293)

### Chore Type
CI / Build change

### Description
Fix the smoke-test `repository-dispatch` workflow branch-reset step that fails when reusing an existing deploy branch (`chore/deploy-<tag>`).

Current failure in `Prepare deploy branch and metadata`:
- `gh api -X PATCH ... -f force=true`
- GitHub API returns `HTTP 422` because `force` is sent as a string instead of a boolean.

This blocks deploy PR creation for repeat dispatches/re-runs.

### Acceptance Criteria
- [ ] `repository-dispatch` updates an existing `chore/deploy-<tag>` branch without API validation errors
- [ ] `Deploy tag and open PR to dev` completes successfully for both:
  - [ ] first run (branch create path)
  - [ ] rerun/redeploy (branch patch path)
- [ ] `Dispatch summary` passes after deploy succeeds
- [ ] Add or update tests/verification evidence for this workflow behavior

### Implementation Notes
- Update `gh api` argument typing for the PATCH call in:
  - `assets/smoke-test/.github/workflows/repository-dispatch.yml`
  - `build/assets/smoke-test/.github/workflows/repository-dispatch.yml`
- Prefer typed boolean input (e.g. `-F force=true`) or equivalent JSON payload with boolean `true`.
- Validate with a manual dispatch against an existing deploy branch.

### Related Issues
- Sub-issue of #169

### Priority
High

### Changelog Category
No changelog needed

### Additional Context
Failing job:
https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23051686417/job/66954252175

Observed error:
`For 'properties/force', "true" is not a boolean. (HTTP 422)`
---

# [Comment #1]() by [c-vigo]()

_Posted on March 13, 2026 at 01:15 PM_

> Failing job:
> https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23051686417/job/66954252175

Subsequent run of the same job fails at a later stage, but this issue is solved: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23052409303/job/66956710509

