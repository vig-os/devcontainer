---
type: issue
state: closed
created: 2026-03-19T13:21:52Z
updated: 2026-03-19T13:53:11Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/374
comments: 2
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:25.002Z
---

# [Issue 374]: [Release 0.3.1-rc4 failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/374)


Release 0.3.1-rc4 encountered an error during the automated release workflow.

**Failed Jobs:** build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23296757616)

**Release PR:** #342

**Rollback Results:**
- Branch rollback: success
- Tag deletion: success

**Actions Taken:**
- Release branch rolled back to pre-finalization state
- Release tag deleted (if created)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.3.1-rc4-*` and remove any orphaned images manually.

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Re-run the workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on March 19, 2026 at 01:35 PM_

## Root Cause Analysis

This failure is a regression related to, but distinct from, [#370](https://github.com/vig-os/devcontainer/issues/370) and the fix merged in [PR #371](https://github.com/vig-os/devcontainer/pull/371).

- The original problem in #370 was `uv sync --frozen --all-extras` crashing intermittently (exit 139) during repeated environment setup.
- PR #371 hardened `uv sync` with cache cleanup/retry logic, but also introduced a new retry-helper export path in `setup-env` (`3aa4f4c`), which writes and reuses `BASH_ENV`.
- In release run `23296757616`, `setup-env` runs twice in the same `build-and-test` job (`build-image` then `test-image`).
- On the second invocation, `PREV_BASH_ENV` already equals `RETRY_HELPER` (`$RUNNER_TEMP/setup-env-retry.sh`). The merge logic prepends `source "$PREV_BASH_ENV"` into that same file, creating a self-reference.
- The next bash step sources `BASH_ENV`, recursively sources itself, and crashes with SIGSEGV (exit 139).

Why CI can still pass: in CI workflow, build and image tests run in separate jobs/runners, so `setup-env` is not re-invoked in the same runner context.

Reference successful baseline run before this regression: [run 23232712985](https://github.com/vig-os/devcontainer/actions/runs/23232712985).

---

# [Comment #2]() by [c-vigo]()

_Posted on March 19, 2026 at 01:35 PM_

## Implementation Plan

1. **Patch `setup-env` self-reference guard**
   - File: `.github/actions/setup-env/action.yml`
   - Change the merge condition in the retry-helper step to skip merging when `PREV_BASH_ENV` equals `RETRY_HELPER`.
   - Target condition:
     - `if [ -n "$PREV_BASH_ENV" ] && [ -f "$PREV_BASH_ENV" ] && [ "$PREV_BASH_ENV" != "$RETRY_HELPER" ]; then`

2. **Update changelog (`Unreleased` / Fixed)**
   - File: `CHANGELOG.md`
   - Add a `Fixed` entry for #374 describing the BASH_ENV self-reference recursion fix in setup-env.

3. **Verify call patterns and risk surface**
   - Confirm release workflow re-invokes `setup-env` in one job (the failing path).
   - Confirm CI workflow uses separate jobs/runners for build/test so behavior remains unchanged.
   - Confirm no behavior change on first `setup-env` invocation.

4. **Validation**
   - Check modified workflow/action files for syntax/lint diagnostics.
   - Re-run release workflow after merge to confirm `Run image tests` no longer crashes with exit 139.

