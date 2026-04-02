---
type: issue
state: open
created: 2026-03-18T07:51:30Z
updated: 2026-03-18T07:51:46Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/354
comments: 0
labels: bug, priority:medium, area:ci, area:workflow, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-19T04:27:47.079Z
---

# [Issue 354]: [[BUG] Intermittent repository_dispatch deploy failure in commit-action (Git refs 404)](https://github.com/vig-os/devcontainer/issues/354)

## Description
The smoke-test `repository_dispatch` deploy flow intermittently fails in the step `Commit and push deploy changes via signed commit-action` with a Git refs `Not Found` error, even when the target branch exists and a retry of the same dispatch later succeeds.

## Steps to Reproduce
1. Trigger smoke-test dispatch with tag `0.3.1-rc3`:
   - `gh api repos/vig-os/devcontainer-smoke-test/dispatches -f event_type=smoke-test-trigger -f 'client_payload[tag]=0.3.1-rc3' -f 'client_payload[release_kind]=candidate'`
2. Observe one run failing in deploy step:
   - https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23233047185/job/67530586917
3. Trigger the same dispatch again with the same payload.
4. Observe deploy step succeeding in a later run:
   - https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23234285563/job/67534417755

## Expected Behavior
The deploy commit step is deterministic and succeeds consistently for identical dispatch payloads, or performs bounded retry for transient API/token failures.

## Actual Behavior
Intermittent failure in `vig-os/commit-action`:
`Not Found - https://docs.github.com/rest/git/refs#get-a-reference`
This occurs after branch preparation and after logging `Using TARGET_BRANCH: chore/deploy-0.3.1-rc3`.

## Environment
- **OS**: GitHub-hosted runner `ubuntu-22.04`
- **Container Runtime**: N/A (workflow-side GitHub API operation)
- **Image Version/Tag**: smoke-test dispatch tag `0.3.1-rc3`
- **Architecture**: x86_64 (GitHub-hosted runner)

## Additional Context
- Relevant workflow template: `assets/smoke-test/.github/workflows/repository-dispatch.yml`
- `create-github-app-token` is pinned to v3 SHA in the current template.
- Proposed mitigation: add one bounded retry around commit-action with fresh commit-app token mint before retry.
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Possible Solution
Implement a targeted retry block only for `Commit and push deploy changes via signed commit-action`:
- attempt once with current token,
- on failure, re-mint commit app token,
- retry once after short backoff,
- fail hard if second attempt fails.

## Changelog Category
No changelog needed
