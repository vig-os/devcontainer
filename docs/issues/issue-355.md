---
type: issue
state: closed
created: 2026-03-18T07:52:19Z
updated: 2026-03-18T09:50:54Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/355
comments: 0
labels: bug, priority:high, area:ci, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-19T04:27:46.769Z
---

# [Issue 355]: [[BUG] repository_dispatch smoke-test release job treats missing tag release as existing](https://github.com/vig-os/devcontainer/issues/355)

## Description
The `Publish smoke-test release artifact` job fails in `Create or validate GitHub release` for tag `0.3.1-rc3`, even when the release does not exist.

The workflow captures `gh api .../releases/tags/${TAG}` output with `|| true` and checks only for non-empty stdout. On 404, GitHub CLI still returns a JSON error payload, so the script incorrectly enters the \"release exists\" branch and compares `prerelease=null` against expected `true`, then exits 1.

## Steps to Reproduce
1. Trigger `repository_dispatch` with:
   - `event_type=smoke-test-trigger`
   - `tag=0.3.1-rc3`
   - `release_kind=candidate`
2. Run workflow `Repository Dispatch Listener` in `vig-os/devcontainer-smoke-test`.
3. Observe job `Publish smoke-test release artifact` fail at step `Create or validate GitHub release`.

## Expected Behavior
If no release exists for the tag, the workflow should create it (`gh release create ... --prerelease` for candidate tags).

## Actual Behavior
Workflow fails with:
`ERROR: Existing release '0.3.1-rc3' prerelease=null (expected true)`

## Environment
- **OS**: GitHub-hosted runner Ubuntu 22.04
- **Container Runtime**: N/A
- **Image Version/Tag**: `ubuntu-22.04` runner image
- **Architecture**: AMD64

## Additional Context
- Failing run/job: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23234285563/job/67534587912
- Related workflow path: `assets/smoke-test/.github/workflows/repository-dispatch.yml`

## Possible Solution
Use status-aware release lookup instead of stdout non-empty check, for example:
- capture HTTP status and branch only on 200
- or validate `.id`/`.tag_name` in successful JSON before treating as existing

## Acceptance Criteria
- [ ] Workflow treats 404 release lookup as \"release does not exist\"
- [ ] Candidate tags create prerelease artifacts successfully
- [ ] Existing release path still validates prerelease flag
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Changelog Category
Fixed
