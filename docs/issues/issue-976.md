---
type: issue
state: closed
created: 2026-07-10T14:35:10Z
updated: 2026-07-10T14:38:13Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/976
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:15.131Z
---

# [Issue 976]: [Release 1.0.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/976)


Release 1.0.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** validate, finalize, build-and-test, vulnix-gate, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/29100258839)

**Release PR:** #975

**Rollback Results:**
- Branch rollback: success
- PR body restoration: skipped

**Tag status (forward-fix policy):**
- Release tags are **not** deleted by automation (workflow choice; not the same as GitHub immutable-release lock-in).
- If the tag was pushed before the failure, it remains on the remote; use a new release candidate to validate fixes, then re-run the final release when ready.

**Actions Taken:**
- Release branch reset to pre-finalization state (best-effort)
- Release PR body restored to TBD / prepare-release format when applicable (best-effort)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:1.0.0-rc1-*` and remove any orphaned images manually.
- If a **draft** GitHub Release exists for this tag, edit or manage it from the Releases UI (**publishing** locks the linked tag and assets when **immutable releases** are enabled).

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Publish a new release candidate to validate the fix; re-run the final workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 10, 2026 at 02:38 PM_

Not a real release failure — the candidate was dispatched immediately after `prepare-release` opened PR #975, so 4 of its CI checks were still in progress and the RC gate correctly rejected ("checks still in progress"). `release/1.0.0` and PR #975 are intact (no branch reset for a validate-stage candidate failure). Re-dispatching `publish-candidate 1.0.0` once #975's CI is fully green. Closing as a premature-dispatch false alarm.

