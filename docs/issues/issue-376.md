---
type: issue
state: closed
created: 2026-03-19T14:17:31Z
updated: 2026-03-19T15:26:45Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/376
comments: 2
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:24.592Z
---

# [Issue 376]: [Release 0.3.1-rc4 smoke dispatch failed](https://github.com/vig-os/devcontainer/issues/376)


Release 0.3.1-rc4 (candidate) failed while triggering downstream smoke-test dispatch.

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23298730621)
**Failed Job:** smoke-test

**Important:**
- Upstream publish already completed before this dispatch step.
- Published artifacts (GHCR images, tag, signatures, attestations, and final GitHub Release if applicable) are intentionally left intact.
- No branch reset or tag deletion is performed for dispatch-only failures.

**Next Steps:**
1. Review smoke-test dispatch logs in this workflow run.
2. Validate token/repository_dispatch permissions for `vig-os/devcontainer-smoke-test`.
3. Re-trigger dispatch after fixing the root cause.

---

# [Comment #1]() by [c-vigo]()

_Posted on March 19, 2026 at 02:33 PM_

## Root Cause Analysis (no fix proposed)

### What failed
The `Smoke-Test Dispatch` job in release run [`23298730621`](https://github.com/vig-os/devcontainer/actions/runs/23298730621) failed **before** dispatching to `vig-os/devcontainer-smoke-test`.

### Primary root cause
The job invokes a **local action** (`./.github/actions/setup-env`) without first checking out the repository in that job workspace.

From the failing job log:
- `Generate smoke-test dispatch token` succeeded
- Then `Set up environment` failed with:
  - `Can't find 'action.yml' ... '/home/runner/work/devcontainer/devcontainer/.github/actions/setup-env'. Did you forget to run actions/checkout before running your local action?`

Because each GitHub Actions job has an isolated workspace, local actions are unavailable unless `actions/checkout` runs in that same job.

### Why this was introduced
In commit `3aa4f4c` (`fix(ci): centralize release retry helper via setup-env`, refs `#365`), the smoke-test job was refactored to add:
- `- name: Set up environment`
- `uses: ./.github/actions/setup-env`

but no corresponding checkout step was added in that job.

### Contributing factor
The issue template text suggested checking token/dispatch permissions, but this incident occurred earlier in execution flow; token generation already succeeded, so permissions were not the blocking cause for this failure.

### Scope and impact
- Scope: release workflow `smoke-test` job.
- Impact: downstream smoke dispatch was never triggered.
- Non-impact: upstream publish artifacts were already produced and intentionally left intact (tag/images/signatures/attestations/release state unchanged), consistent with workflow behavior.

---

# [Comment #2]() by [c-vigo]()

_Posted on March 19, 2026 at 02:37 PM_

## Implementation Plan to Fix #376

Based on RCA, the failure is caused by using local action `./.github/actions/setup-env` in the `smoke-test` job without a checkout step in that same job workspace.

### Goal
Make `smoke-test` job reliably dispatch to `vig-os/devcontainer-smoke-test` by ensuring local action availability and validating the dispatch path end-to-end.

### Plan

1. **Update workflow job setup**
   - Edit `.github/workflows/release.yml` in the `smoke-test` job.
   - Add a checkout step before `Set up environment`:
     - `actions/checkout` (pinned SHA, consistent with repo standard).
   - Keep existing `permissions` and token generation flow unchanged unless required by tests.

2. **Add guardrails in job comments/logging**
   - Add a brief inline comment in `smoke-test` explaining that checkout is required for local actions (`./.github/actions/*`).
   - Keep log output focused so future failures clearly distinguish:
     - token creation failures vs
     - local action/bootstrap failures vs
     - downstream dispatch API failures.

3. **Validate workflow statically**
   - Run local workflow lint/validation (if available in project commands).
   - Confirm no syntax or action reference regressions in `release.yml`.

4. **Validate behavior in CI**
   - Trigger a controlled release workflow run (non-production-safe context as per maintainer process).
   - Verify in run logs:
     - `Set up environment` executes successfully in `smoke-test`.
     - `Trigger smoke-test repository dispatch` runs and returns success.
   - Verify downstream repo receives `repository_dispatch` event with expected payload fields.

5. **Post-change verification evidence**
   - Attach links in this issue to:
     - fixing commit/PR
     - successful workflow run
     - downstream smoke-test run/event evidence.
   - Close issue after evidence confirms dispatch path is restored.

### Acceptance Criteria
- `smoke-test` job no longer fails at local action resolution.
- Dispatch step executes successfully and triggers downstream smoke-test workflow/event.
- No regression in earlier release jobs (`validate`, `finalize`, `build-and-test`, `publish`).
- Issue contains run links proving successful end-to-end dispatch.

