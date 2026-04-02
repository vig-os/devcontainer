---
type: issue
state: closed
created: 2026-03-26T15:45:21Z
updated: 2026-03-27T11:39:44Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/453
comments: 1
labels: bug
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:15.008Z
---

# [Issue 453]: [Smoke-test dispatch failed for 0.3.1-rc25](https://github.com/vig-os/devcontainer/issues/453)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.3.1-rc25`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `23602722662`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/23602722662
- source_sha: `11bc8e9db642a8f1801118b537db062a3b15609b`
- correlation_id: `vig-os/devcontainer:23602722662:0.3.1-rc25`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23603456323
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/107
- release PR: not created

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `failure`
- ready-release-pr: `skipped`
- trigger-release: `skipped`
- merge-release-pr: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Do not rewrite or delete **published** GitHub Releases (or their linked tags when **immutable releases** are enabled) to retry the same version; bare git tags without a published release are not locked by that feature unless a tag ruleset applies.
- After fixing the root cause upstream, publish a **new** RC tag (or a new final attempt only after branch/tag state matches your release policy), then rely on a fresh dispatch.
---

# [Comment #1]() by [c-vigo]()

_Posted on March 27, 2026 at 09:30 AM_

## Root Cause Analysis

### Summary

The smoke-test dispatch failed on attempts 1 and 2 due to a **GitHub API eventual consistency race condition** in the `prepare-release.yml` workflow (in `vig-os/devcontainer-smoke-test`), compounded by an **incomplete rollback** that left the `dev` branch in a dirty state.

### Timeline

| Time (UTC) | Event |
|---|---|
| 15:41 | Attempt 1 starts: deploy PR created, merged to dev |
| 15:44:48 | `prepare-release.yml` run [23603591924](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23603591924) freezes CHANGELOG on `dev` (commit `c4340e06`) |
| 15:44:51.665 | Release branch `release/0.3.1` created via `POST /git/refs` API |
| 15:44:52.205 | `commit-action` attempt 1/3: **HTTP 404** resolving `refs/heads/release/0.3.1` (~540ms after creation) |
| 15:44:53.434 | `commit-action` attempt 2/3: **HTTP 404** (~1.8s after creation) |
| 15:44:55.667 | `commit-action` attempt 3/3: **HTTP 404** (~4.0s after creation) -- step fails |
| 15:44:55 | Rollback step runs: deletes `release/0.3.1` branch, detects CHANGELOG rollback needed |
| 15:44:55 | **"Commit CHANGELOG rollback to dev via API" step is SKIPPED** |
| 15:45:03 | Orchestrator detects prepare-release failure, attempt 1 fails |
| 17:38 | Attempt 2 re-runs only the failed orchestrator job |
| 17:38:22 | `prepare-release.yml` run [23609090467](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23609090467) checks out `dev` at `c4340e06` (frozen CHANGELOG) |
| 17:38:22 | Validation fails: `ERROR: CHANGELOG.md Unreleased section has no entries` |
| 17:40 | Attempt 3 triggered (full re-run of all jobs) |
| 17:41:41 | Deploy step re-runs `install.sh`, syncs workspace CHANGELOG from `.devcontainer/CHANGELOG.md`, restoring entries under `## Unreleased` |
| 17:43 | Prepare-release passes validation, all jobs succeed |

### Attempt 1: GitHub API eventual consistency

**Failed step:** "Commit stripped CHANGELOG to release branch via API" in `prepare-release.yml` run [23603591924](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23603591924)

The `release/0.3.1` branch was created via `POST /repos/.../git/refs`, and the API response confirmed creation. However, when `vig-os/commit-action` immediately tried to resolve the same ref via `GET /repos/.../git/ref/heads/release/0.3.1`, it received **HTTP 404** on all 3 retry attempts spanning ~4 seconds.

This matches GitHub API eventual consistency behavior: newly created Git references may not be immediately resolvable. The `commit-action` retry window (3 attempts, exponential backoff starting at ~1s) was insufficient for the reference to propagate.

**Evidence:** The same 404 race condition was observed in attempt 3's deploy step (`GitHub API attempt 1/3 failed (HTTP 404 (transient)), retrying in 1180ms`), but there the second attempt succeeded because the longer backoff was sufficient.

### Incomplete rollback leaves `dev` in dirty state

The "Roll back prepare-release side effects on failure" step (`if: failure()`) ran successfully and:

1. Deleted the `release/0.3.1` branch
2. Detected that `dev` needed a CHANGELOG rollback (set output `changelog_rollback_needed`)

However, the subsequent **"Commit CHANGELOG rollback to dev via API"** step was **SKIPPED**. Its condition in [`prepare-release.yml`](https://github.com/vig-os/devcontainer/blob/dev/assets/workspace/.github/workflows/prepare-release.yml) is:

```yaml
if: ${{ failure() && steps.rollback_prepare.outputs.changelog_rollback_needed == 'true' }}
```

Despite `failure()` being true and the rollback step succeeding, the commit step did not execute. The most likely cause is that the `changelog_rollback_needed` output was not set to `'true'` -- possibly because the GitHub Contents API returned stale (pre-freeze) content for `?ref=dev`, making the CHANGELOG comparison find no difference, which would leave the output as `false`.

This left `dev` with a frozen CHANGELOG where all entries had been moved from `## Unreleased` to `## [0.3.1] - TBD`, with an empty `## Unreleased` section.

### Attempt 2: Cascading failure from dirty `dev` state

**Failed step:** "Verify CHANGELOG has Unreleased section entries" in `prepare-release.yml` run [23609090467](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23609090467)

Attempt 2 re-ran only the failed orchestrator job (other jobs were reused from attempt 1). The newly triggered `prepare-release.yml` checked out `dev` at the frozen commit `c4340e06`, found the empty `## Unreleased` section, and correctly rejected it.

### How attempt 3 self-healed

Attempt 3 was a full re-run. The deploy step re-ran `install.sh` which synced the workspace CHANGELOG from `.devcontainer/CHANGELOG.md` (the upstream devcontainer CHANGELOG), renaming the top version section to `## Unreleased`. This overwrote the frozen CHANGELOG, restoring entries under Unreleased. The deploy PR ([#108](https://github.com/vig-os/devcontainer-smoke-test/pull/108)) was merged to `dev`, and `prepare-release.yml` passed validation.

### Identified issues

1. **`commit-action` retry window too short for freshly-created branches.** The 3-attempt retry with ~1-2s exponential backoff (total ~4s) is sometimes insufficient for GitHub API eventual consistency. Consider adding an explicit delay after branch creation, or increasing the retry count/backoff in `commit-action`.

2. **Rollback mechanism unreliable.** The "Roll back prepare-release side effects on failure" step detected the need for rollback, but the subsequent commit step was skipped. The CHANGELOG comparison logic (using GitHub Contents API with `?ref=dev`) may be subject to the same eventual consistency issues, returning stale content and reporting no difference. Consider adding explicit `echo` logging in the rollback script to trace the comparison outcome, and/or implementing the rollback commit within the same step rather than depending on output passing between steps.

### Additional note

The `vig-os/commit-action` action is running on Node.js 20, which will be deprecated. Node.js 24 will become the default on June 2, 2026, and Node.js 20 will be removed September 16, 2026. See [GitHub changelog](https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/).

### References

- Orchestrator run: [smoke-test-trigger #38](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23603456323)


