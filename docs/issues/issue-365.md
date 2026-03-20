---
type: issue
state: closed
created: 2026-03-19T07:32:20Z
updated: 2026-03-19T09:04:20Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/365
comments: 1
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:26.696Z
---

# [Issue 365]: [Release  failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/365)


Release  encountered an error during the automated release workflow.

**Failed Jobs:** validate, finalize, build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23284512115)

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

_Posted on March 19, 2026 at 08:19 AM_

## Root Cause Analysis

- The release workflow failure is caused by `uv run retry` being used in jobs that do not install `uv`.
- In run 23284512115, `validate` failed at "Checkout release branch" with `uv: command not found` before any branch/tag validation actually ran.
- The fallback branch-not-found message was misleading because the command failed before `git fetch` executed.
- `rollback` then also hit `uv: command not found` for branch rollback/tag-check steps, so rollback branch reset was reported as failure.

Why this happened:
- Commit `2ff89ec` introduced `uv run retry` wrappers broadly in `.github/workflows/release.yml`.
- `validate`, `publish`, `smoke-test`, and `rollback` do not provision `uv` in their current form; `finalize` only sets up env for `final` releases.

Fix direction in this PR:
1) Ensure jobs with checkout set up `uv` before using `uv run retry`.
2) Replace `uv run retry` in no-checkout jobs (`rollback`, `smoke-test`) with inline shell retry logic.

Workflow run: https://github.com/vig-os/devcontainer/actions/runs/23284512115

