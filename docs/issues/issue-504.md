---
type: issue
state: closed
created: 2026-04-08T07:25:10Z
updated: 2026-04-08T09:39:05Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/504
comments: 1
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-08T09:40:38.175Z
---

# [Issue 504]: [Release 0.3.2 failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/504)


Release 0.3.2 encountered an error during the automated release workflow.

**Failed Jobs:** publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/24122830083)

**Release PR:** #486

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
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.3.2-*` and remove any orphaned images manually.
- If a **draft** GitHub Release exists for this tag, edit or manage it from the Releases UI (**publishing** locks the linked tag and assets when **immutable releases** are enabled).

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Publish a new release candidate to validate the fix; re-run the final workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on April 8, 2026 at 07:45 AM_

## RCA: Release 0.3.2 failure — publish job CHANGELOG parse mismatch

### Trigger
`just finalize-release 0.3.2` dispatched [Release workflow run](https://github.com/vig-os/devcontainer/actions/runs/24122830083). The **Publish Release** job failed at **Generate final release notes from CHANGELOG** ([job](https://github.com/vig-os/devcontainer/actions/runs/24122830083/job/70381830965)).

### Root cause
The publish step used an `awk` guard that only matched headings of the form `## [X.Y.Z] - …` (closing `]` immediately before ` - `). After **Finalize Release**, `prepare-changelog finalize` rewrites the heading to include a GitHub release link, e.g.

`## [0.3.2](https://github.com/vig-os/devcontainer/releases/tag/0.3.2) - 2026-04-08`

That format comes from `finalize_release_date()` in `packages/vig-utils/src/vig_utils/prepare_changelog.py` (linked headings were added in commit `23c6694`). The old `index($0, "## [" version "] - ") == 1` pattern never matched, so `/tmp/github-release-notes.md` was empty and the step exited 1.

**Finalize** / **rollback** PR-body steps already used prefix matching on `## [${VERSION}]` only, so they kept working.

### Side effects
- Tag **`0.3.2`** was pushed before this step failed; it remains on the remote (forward-fix policy), pointing at the finalize commit.
- Rollback reset the release branch and restored the PR body; no GHCR push and no draft GitHub Release occurred after this failure.

### Fix (tracked in repo)
Align the publish job `awk` with finalize/rollback: match `## [VERSION]` at line start, then collect until the next `## [` section. Implemented in `.github/workflows/release.yml` (publish → Generate final release notes from CHANGELOG).

