---
type: issue
state: open
created: 2026-03-19T15:50:20Z
updated: 2026-03-19T15:50:20Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/379
comments: 0
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:24.213Z
---

# [Issue 379]: [Release 0.3.1-rc5 failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/379)


Release 0.3.1-rc5 encountered an error during the automated release workflow.

**Failed Jobs:** build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23303525517)

**Release PR:** #342

**Rollback Results:**
- Branch rollback: success
- Tag deletion: success

**Actions Taken:**
- Release branch rolled back to pre-finalization state
- Release tag deleted (if created)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.3.1-rc5-*` and remove any orphaned images manually.

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Re-run the workflow when ready

For details, check the workflow run linked above.

