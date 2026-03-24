---
type: issue
state: closed
created: 2026-03-23T20:43:57Z
updated: 2026-03-23T22:04:28Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devcontainer/issues/421
comments: 1
labels: bug
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-24T04:25:02.158Z
---

# [Issue 421]: [Smoke-test dispatch failed for 0.3.1-rc14](https://github.com/vig-os/devcontainer/issues/421)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.3.1-rc14`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `23458250740`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/23458250740
- source_sha: `8f8b60fe235c211534b9e121219a398672199989`
- correlation_id: `vig-os/devcontainer:23458250740:0.3.1-rc14`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23458873798
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/74
- release PR: https://github.com/vig-os/devcontainer-smoke-test/pull/75

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `success`
- ready-release-pr: `success`
- trigger-release: `failure`
- merge-release-pr: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Re-dispatch using a new RC tag/version once root cause is fixed.
---

# [Comment #1]() by [c-vigo]()

_Posted on March 23, 2026 at 09:46 PM_

## Root Cause Analysis

### Failure chain

```
repository-dispatch.yml (trigger-release job)
  → release.yml (run 23459089461)
    → release-core.yml (Validate Release Core job)
      → step 8: "Validate image accessibility" ← FAILED
    → Rollback on Failure job
      → step 10: "Create failure issue" ← ALSO FAILED
```

### Primary cause: redundant image check runs `docker` CLI inside a container that doesn't have it

The `Validate Release Core` job in `release-core.yml` runs inside a container:

```yaml
container:
  image: ghcr.io/vig-os/devcontainer:${{ needs.resolve-image.outputs.image-tag }}
```

Step 8, "Validate image accessibility", then attempts:

```bash
retry --retries 3 --backoff 5 --max-backoff 30 -- docker manifest inspect "$IMAGE" > /dev/null 2>&1
```

This fails because:

1. **The `docker` CLI is not installed in the devcontainer image.** Confirmed locally: `docker run --rm ghcr.io/vig-os/devcontainer:0.3.1-rc14 bash -c 'which docker'` → not found.
2. `retry` detects the command-not-found (`ENOENT`) and exits immediately (exit 127) without retrying — total elapsed time ~70ms, consistent with the CI logs showing the step completing in ~80ms.
3. The `> /dev/null 2>&1` suppresses both `retry`'s diagnostic output and the underlying error, so the logs only show the generic "Cannot access image manifest" message.

**The step is redundant by design.** The validate job is already running inside the image it's trying to validate. If the image were inaccessible, the job container would never have started. The `resolve-image` composite action already performs this same check on the bare runner (where the docker CLI exists), and that check passed.

### Secondary cause: Rollback job cannot create failure issue

The `Rollback on Failure` job also runs in a container. Its "Create failure issue" step runs `gh issue create`, but `gh` requires a git repository context to resolve `--repo`. The checkout step is gated on `needs.core.outputs.pre_finalize_sha != ''`, which is empty because validation failed before that output was set. Without a checkout, `gh` fails:

```
fatal: not a git repository (or any parent up to mount point /)
```

This fails 3 times with backoff (5s, 10s) before giving up.

### Evidence

| Signal | Value |
|---|---|
| Failed step | `Validate image accessibility` (step 8 of Validate Release Core) |
| Elapsed time | ~80ms (no retries occurred — `retry` exits immediately on ENOENT) |
| Docker CLI in image | Not installed (`which docker` → not found) |
| `resolve-image` same check | Passed on bare runner (docker CLI available there) |
| Container image pull | Succeeded (image is accessible) |
| Rollback failure | `gh issue create` → "not a git repository" (no checkout) |

### Downstream state

- Deploy PR [#74](https://github.com/vig-os/devcontainer-smoke-test/pull/74): merged ✓
- Release PR [#75](https://github.com/vig-os/devcontainer-smoke-test/pull/75): open, not merged (labeled `release-kind:candidate`)
- No tags were created, no finalization commits were pushed — no cleanup needed beyond the stale release PR/branch if desired.

### Fix direction

Remove the redundant "Validate image accessibility" step from `release-core.yml` — the container job already proves image accessibility. The `resolve-image` composite action's check on the bare runner is sufficient.

The rollback `gh issue create` failure is a separate issue (missing `GH_REPO` env or unconditional checkout).

