---
type: issue
state: closed
created: 2026-03-23T17:43:04Z
updated: 2026-03-23T20:17:36Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/419
comments: 1
labels: bug
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-24T04:25:02.490Z
---

# [Issue 419]: [Smoke-test release phase 2 failed for 0.3.1](https://github.com/vig-os/devcontainer/issues/419)

Smoke-test release phase 2 failed while triggering downstream release workflow.

## Release metadata
- version: `0.3.1`
- release_kind: `candidate`
- release_pr: https://github.com/vig-os/devcontainer-smoke-test/pull/70

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23451495795

## Job results
- validate: `success`
- trigger-release: `failure`
- summary: `failure`
---

# [Comment #1]() by [c-vigo]()

_Posted on March 23, 2026 at 06:09 PM_

## Root cause analysis (0.3.1 smoke-test phase 2)

### Summary

Phase 2 failed because the downstream `release.yml` run in **devcontainer-smoke-test** tries to check out `release/0.3.1`, but that branch no longer exists when the workflow runs. The branch was removed automatically when the release PR merged, **before** phase 2’s `release.yml` could use it.

### Reconstructed timeline (UTC, 2026-03-23)

- **17:20:13** — `just publish-candidate 0.3.1` triggered devcontainer `release.yml` on `release/0.3.1` ([run 23450601238](https://github.com/vig-os/devcontainer/actions/runs/23450601238)). Validate, build, and publish succeeded.
- **17:35:01** — Upstream `smoke-test` job dispatched to the smoke-test repo. Phase 1 (`repository-dispatch.yml`) started ([run 23451261786](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23451261786)).
- Phase 1 succeeded in sequence: `validate` → `deploy` → `wait-deploy-merge` → `cleanup-release` (deleted stale `release/0.3.1`) → `trigger-prepare-release` (recreated `release/0.3.1` from `dev`, opened [PR #70](https://github.com/vig-os/devcontainer-smoke-test/pull/70) as draft) → `ready-release-pr`.
- **17:39:39** — PR #70 marked ready for review.
- **17:39:42** — PR #70 labeled `release-kind:candidate`.
- **17:39:45** — Auto-merge enabled on PR #70.
- **17:39:54** — Phase 1 run completed successfully.
- **17:40:22** — PR #70 auto-merged (`release/0.3.1` → `main`).
- **17:40:23** — GitHub auto-deleted branch `release/0.3.1` (repo has **Automatically delete head branches** enabled).
- **17:40:25** — Phase 2 (`on-release-pr-merge.yml`) started on PR close ([run 23451495795](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23451495795)).
- **17:40:41** — Phase 2 `trigger-release` dispatched `release.yml` with `--ref dev`, inputs `version=0.3.1`, `release-kind=candidate` ([inner run 23451507841](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23451507841)).
- **17:41:28** — Inner workflow failed at **Checkout release branch**: `A branch or tag with the name 'release/0.3.1' could not be found`.
- **17:42:46** — Phase 2 reported the inner `release.yml` conclusion as `failure`.
- **17:43:07** — `notify-failure` opened this issue.

So: deployment and prepare-release (phase 1) behaved as designed; the failure is confined to **phase 2** waiting on a `release.yml` that assumes `release/<version>` still exists after the release PR has merged.

### Technical root cause

Downstream `release-core.yml` checks out `release/${{ version }}` unconditionally in the validate job (see `assets/workspace/.github/workflows/release-core.yml`, step **Checkout release branch**).

After phase 1 enables auto-merge, the release PR merges quickly; with **delete branch on merge**, `release/0.3.1` is removed immediately. Phase 2 then dispatches `release.yml`, which still expects that ref — hence the checkout error.

This is a **design gap**: phase 2 orchestration assumes the release branch survives the merge, but auto-merge plus auto-delete-head-branch removes it first.

### Possible directions for a fix (separate scope)

1. **Recreate the branch in phase 2** — e.g. in `on-release-pr-merge.yml`, recreate `release/<version>` from the merge commit before dispatching `release.yml`.
2. **Make `release-core.yml` resilient** — if `release/<version>` is missing, fall back to `main` (content already merged).
3. **Turn off auto-delete head branches** on the smoke-test repo (keeps the branch; needs cleanup discipline).
4. **Change orchestration** — e.g. defer merge until after downstream `release.yml` succeeds (larger behavioral change).

Happy to help turn one of these into a concrete issue/PR once we pick an approach.


