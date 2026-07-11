---
type: issue
state: closed
created: 2026-07-08T15:34:10Z
updated: 2026-07-08T16:12:36Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/940
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:20.652Z
---

# [Issue 940]: [Release 0.5.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/940)


Release 0.5.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** vulnix-gate, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28954286382)

**Release PR:** #938

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
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.5.0-rc1-*` and remove any orphaned images manually.
- If a **draft** GitHub Release exists for this tag, edit or manage it from the Releases UI (**publishing** locks the linked tag and assets when **immutable releases** are enabled).

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Publish a new release candidate to validate the fix; re-run the final workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 04:12 PM_

Resolved. This rollback was the `0.5.0-rc1` run failing at the **Vulnix CVE Gate** on 17 fresh HIGH/CRITICAL curl 8.20.0 CVEs (real findings, not a workflow-mechanics issue). No patched curl exists upstream or in nixpkgs to bump to, so the findings were accepted as time-boxed `.vulnixignore` exceptions (expiry 2026-07-22) via #941 / #942, now merged to `release/0.5.0`.

Rollback left no residue (release branch + CHANGELOG intact; tags forward-fix). Re-dispatch of the RC is proceeding once release-branch CI is green. Closing as completed.

