---
type: issue
state: closed
created: 2026-07-07T13:31:01Z
updated: 2026-07-07T14:02:37Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/904
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:27.429Z
---

# [Issue 904]: [Release 0.4.1-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/904)


Release 0.4.1-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** vulnix-gate, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28869306823)

**Release PR:** #898

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
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.4.1-rc1-*` and remove any orphaned images manually.
- If a **draft** GitHub Release exists for this tag, edit or manage it from the Releases UI (**publishing** locks the linked tag and assets when **immutable releases** are enabled).

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Publish a new release candidate to validate the fix; re-run the final workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 02:02 PM_

Resolved. Root cause: the release CVE gate blocked on `CVE-2026-57231` (CVSS 7.5) in podman 5.8.2 — a host-env-var leak with no covering `.vulnixignore` exception.

Fixed in #906 (merged into `release/0.4.1`, merge commit c3770915c) via #905: added a short-dated register exception (expires 2026-08-06, flips to a nixpkgs rev-advance once the release-26.05 podman 5.8.4 backport NixOS/nixpkgs#536367 lands). Verified — the vulnix gate now passes on the release branch.

Next step: re-dispatch the 0.4.1 RC release workflow; it should clear the gate.

