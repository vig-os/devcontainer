---
type: issue
state: closed
created: 2026-07-08T15:20:33Z
updated: 2026-07-08T15:26:32Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/939
comments: 1
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:21.044Z
---

# [Issue 939]: [Release 0.5.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/939)


Release 0.5.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** validate, finalize, build-and-test, vulnix-gate, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28954004072)

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

_Posted on July 8, 2026 at 03:26 PM_

Resolved. Root cause: the first `0.5.0-rc1` dispatch ran against the default branch (`main`), whose `release.yml` still enforces the pre-#902 gate (PR must be non-draft **and** approved for every release kind), so validate failed with `PR #938 is still in draft status`. The #902 change that gates candidates on **CI only** lives on `dev`/`release/0.5.0` but has not yet reached `main` — 0.5.0 is the release that carries it there.

Re-dispatched from the release branch (`gh workflow run release.yml --ref release/0.5.0`), so GitHub executes the release branch's copy of the workflow (with the #902 deferral). Validate now passes with the draft PR #938 and the build is proceeding: https://github.com/vig-os/devcontainer/actions/runs/28954286382

Note for the rest of this cycle: until 0.5.0 merges to `main`, the **final** release and **promote** dispatches must also target `--ref release/0.5.0`.

Closing as resolved — the rollback left no residue (release branch and CHANGELOG intact).

