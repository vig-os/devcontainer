---
type: issue
state: closed
created: 2026-03-22T09:31:37Z
updated: 2026-03-22T12:39:04Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/407
comments: 1
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-23T04:34:22.639Z
---

# [Issue 407]: [Release 0.3.1-rc10 failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/407)


Release 0.3.1-rc10 encountered an error during the automated release workflow.

**Failed Jobs:** publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23400039119)

**Release PR:** #342

**Rollback Results:**
- Branch rollback: success
- Tag deletion: success

**Actions Taken:**
- Release branch rolled back to pre-finalization state
- Release tag deleted (if created)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.3.1-rc10-*` and remove any orphaned images manually.

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Re-run the workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on March 22, 2026 at 12:22 PM_

## Root Cause Analysis

**Failure:** `Publish Release` job, `Install uv` step (via `.github/actions/setup-env`)
**Error:** `Unexpected HTTP response: 404` downloading `uv 0.10.0` from GitHub Releases CDN
**Resolution:** Rerun (attempt 2) succeeded -- transient GitHub CDN issue, no code changes needed.

### Timeline

| Time (UTC) | Event |
|---|---|
| 09:30:30 | `astral-sh/setup-uv@v7` starts downloading `uv-x86_64-unknown-linux-gnu.tar.gz` |
| 09:30:31 | HTTP 404 received; step fails |
| 09:31:01 | `Publish Release` job fails; rollback job runs (branch reset + tag deletion) |
| ~09:21 (attempt 2) | Manual rerun succeeds; all jobs pass |

### Root Cause

The `astral-sh/setup-uv` action downloads the uv binary directly from GitHub Releases. GitHub's CDN occasionally returns transient 404s for valid release assets (caching propagation delays, edge node issues). The action has no built-in retry logic for download failures.

### Fix

Add a `continue-on-error` + conditional retry pattern to the `Install uv` step in `.github/actions/setup-env/action.yml`, matching the pattern already used for SBOM generation and attestation steps in `release.yml`.

Tracked separately -- see linked issue/PR.


