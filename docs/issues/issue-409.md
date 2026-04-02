---
type: issue
state: closed
created: 2026-03-22T12:13:02Z
updated: 2026-03-22T12:24:14Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/409
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-23T04:34:21.808Z
---

# [Issue 409]: [Smoke-test release phase 2 failed for unknown](https://github.com/vig-os/devcontainer/issues/409)

Smoke-test release phase 2 failed while triggering downstream release workflow.

## Release metadata
- version: `unknown`
- release_kind: `unknown`
- release_pr: n/a

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23402800282

## Job results
- validate: `failure`
- trigger-release: `skipped`
- summary: `failure`
---

# [Comment #1]() by [c-vigo]()

_Posted on March 22, 2026 at 12:24 PM_

## Root cause

**One-time bootstrap / chicken-and-egg.** The fix for [#402](https://github.com/vig-os/devcontainer/issues/402) (remove self-approval on the release PR, split smoke-test orchestration into two phases) shipped in the **0.3.1-rc10** payload. The **repository_dispatch** that deploys that payload still runs [`repository-dispatch.yml`](https://github.com/vig-os/devcontainer-smoke-test/blob/main/.github/workflows/repository-dispatch.yml) from **smoke-test `main`**, which at dispatch time was still the **older** workflow that ran `gh pr review --approve` as the same identity that opened the PR.

## What happened

1. **Phase 1 – dispatch** ([smoke-test run 23400308501](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23400308501), also tracked in [#408](https://github.com/vig-os/devcontainer/issues/408)): job *Sync changelog and prepare release PR* failed at *Mark release PR ready and approve* with:
   ```
   failed to create review: GraphQL: Review Can not approve your own pull request (addPullRequestReview)
   ```
   After that failure, steps that apply the required **`release-kind:candidate`** / **`release-kind:final`** label never ran, so [PR #58](https://github.com/vig-os/devcontainer-smoke-test/pull/58) stayed **without** those labels.

2. **Manual step:** The release PR was merged manually (approval/merge outside the failed automation). That is **consistent with** the phase-1 failure above; it is not a separate root cause.

3. **Phase 2 – merged release PR** ([smoke-test run 23402800282](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23402800282)): `on-release-pr-merge.yml` validates that the merged PR has a `release-kind:*` label. PR #58 had **none**, so *Extract version and release kind* failed with:
   ```
   ERROR: missing required release-kind label (expected 'release-kind:final' or 'release-kind:candidate')
   ```
   *trigger-release* was skipped; this issue was opened by the phase-2 notify job. Upstream metadata in the issue body shows `unknown` because validation failed before outputs were set.

## Relationship to other issues

- **[#402](https://github.com/vig-os/devcontainer/issues/402)** / **[#398](https://github.com/vig-os/devcontainer/issues/398)** – prior work that removed self-approval and introduced the two-phase flow (e.g. `373e56c`).

- **[#408](https://github.com/vig-os/devcontainer/issues/408)** – same dispatch run; phase-1 failure. [#409](https://github.com/vig-os/devcontainer/issues/409) is the **follow-on** failure after the release PR was merged without labels.

## Resolution

- **No additional code change is required for this specific incident:** smoke-test `main` now carries the updated workflows (no self-approval; labeling in phase 1; phase 2 on merge). The next successful dispatch path should apply `release-kind:*` before merge.

- **Operational note:** Template changes under `assets/smoke-test/` still need promotion to smoke-test `main` per repo notes; this incident is the expected edge case when the fix ships **via** the pipeline that was still running the pre-fix workflow.

Closing as **resolved** (one-time bootstrap).

