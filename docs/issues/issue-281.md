---
type: issue
state: closed
created: 2026-03-12T15:41:50Z
updated: 2026-03-12T17:38:41Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/281
comments: 0
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:57.108Z
---

# [Issue 281]: [Release 0.3.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/281)


Release 0.3.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23009972089)

**Release PR:** #270

**Rollback Results:**
- Branch rollback: success
- Tag deletion: success

**Actions Taken:**
- Release branch rolled back to pre-finalization state
- Release tag deleted (if created)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.3.0-rc1-*` and remove any orphaned images manually.

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Re-run the workflow when ready

For details, check the workflow run linked above.

