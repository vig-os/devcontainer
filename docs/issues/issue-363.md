---
type: issue
state: closed
created: 2026-03-19T07:15:08Z
updated: 2026-03-19T07:20:14Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/363
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:27.371Z
---

# [Issue 363]: [Release  failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/363)


Release  encountered an error during the automated release workflow.

**Failed Jobs:** validate, finalize, build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23284029649)

**Release PR:** #null

**Rollback Results:**
- Branch rollback: failure
- Tag deletion: success

**Actions Taken:**
- Release branch rolled back to pre-finalization state
- Release tag deleted (if created)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:-*` and remove any orphaned images manually.

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Re-run the workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on March 19, 2026 at 07:20 AM_

Launched too early before CI on release branch was done

