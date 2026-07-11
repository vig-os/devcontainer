---
type: issue
state: closed
created: 2026-07-06T09:11:13Z
updated: 2026-07-06T13:01:52Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/869
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:33.713Z
---

# [Issue 869]: [Release 0.4.0 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/869)


Release 0.4.0 encountered an error during the automated release workflow.

**Failed Jobs:** vulnix-gate, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28778654505)

**Release PR:** #813

**Rollback Results:**
- Branch rollback: success
- PR body restoration: success

**Tag status (forward-fix policy):**
- Release tags are **not** deleted by automation (workflow choice; not the same as GitHub immutable-release lock-in).
- If the tag was pushed before the failure, it remains on the remote; use a new release candidate to validate fixes, then re-run the final release when ready.

**Actions Taken:**
- Release branch reset to pre-finalization state (best-effort)
- Release PR body restored to TBD / prepare-release format when applicable (best-effort)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.4.0-*` and remove any orphaned images manually.
- If a **draft** GitHub Release exists for this tag, edit or manage it from the Releases UI (**publishing** locks the linked tag and assets when **immutable releases** are enabled).

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Publish a new release candidate to validate the fix; re-run the final workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 6, 2026 at 01:01 PM_

Root cause resolved. The rollback's failed `vulnix-gate` (and consequently `publish`) was caused by `nvd.nist.gov` throttling/404-ing the NVD feed downloads (`ReadTimeoutError`/`IncompleteRead`). That's now fixed by the self-hosted NVD mirror (#870, PRs #871 + #872, merged into `release/0.4.0`): vulnix fetches from https://vig-os.github.io/nvd-mirror/ instead of `nvd.nist.gov`, verified passing in ~97 s.

Closing — a fresh `0.4.0` release can be attempted when ready. The manual-cleanup checklist above still applies: check for orphaned `ghcr.io/vig-os/devcontainer:0.4.0-*` images and any draft release from the failed attempt.

