---
type: issue
state: closed
created: 2026-07-04T18:45:45Z
updated: 2026-07-04T20:17:06Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/847
comments: 2
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:37.258Z
---

# [Issue 847]: [Release 0.4.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/847)


Release 0.4.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28715886300)

**Release PR:** #813

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
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.4.0-rc1-*` and remove any orphaned images manually.
- If a **draft** GitHub Release exists for this tag, edit or manage it from the Releases UI (**publishing** locks the linked tag and assets when **immutable releases** are enabled).

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Publish a new release candidate to validate the fix; re-run the final workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 06:48 PM_

**Diagnosis — flaky SIGPIPE race in `setup-env`, unrelated to the release content and to #842** (whose vulnix-gate fix is proven by this run: `Vulnix CVE Gate` passed; `Build and Test (amd64)` was only cancelled by fail-fast).

`Build and Test (arm64)` died at exit 2 during the test-image action's `setup-env` sub-step, at `.github/actions/setup-env/action.yml:167`:

```
printf '%s' "$SHELL_PATH" | tr ':' '\n' | grep '^/nix/store' | head -50
```

The step shell is `bash -e -o pipefail`. When `head` exits after 50 lines before `grep` finishes writing, `grep` takes `SIGPIPE` (`grep: write error: Broken pipe` is in the log at the exact failure timestamp, 18:42:21) and exits 2 → `pipefail` fails the step. It's a scheduling race — the same line has run green across all workflows for weeks — but with the dev-shell PATH now exceeding 50 nix-store entries it can fire on any leg at any time.

Fix: replace `head -50` with `sed -n '1,50p'`, which consumes the whole stream (no early pipe close, no SIGPIPE) and prints the same first 50 lines.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:17 PM_

Resolved by #848 (merged `f20162db`): candidate run [28717901832](https://github.com/vig-os/devcontainer/actions/runs/28717901832) fully green — both build-and-test legs completed setup-env without the SIGPIPE race (`sed -n '1,50p'` drains the stream). 0.4.0-rc1 published.

