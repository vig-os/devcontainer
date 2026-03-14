---
type: issue
state: closed
created: 2026-03-13T14:02:55Z
updated: 2026-03-13T15:54:20Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devcontainer/issues/299
comments: 3
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-14T04:15:54.553Z
---

# [Issue 299]: [Release 0.3.0-rc3 failed -- automatic rollback](https://github.com/vig-os/devcontainer/issues/299)


Release 0.3.0-rc3 encountered an error during the automated release workflow.

**Failed Jobs:** build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/23054106926)

**Release PR:** #270

**Rollback Results:**
- Branch rollback: success
- Tag deletion: success

**Actions Taken:**
- Release branch rolled back to pre-finalization state
- Release tag deleted (if created)
- This issue created for investigation

**Manual Cleanup May Be Needed:**
- If images were pushed to GHCR before the failure, they are **not** automatically deleted. Check `ghcr.io/vig-os/devcontainer:0.3.0-rc3-*` and remove any orphaned images manually.

**Next Steps:**
1. Review the workflow logs to identify the root cause
2. Check rollback results above; fix any partial rollback manually
3. Fix the issue on the release branch
4. Re-run the workflow when ready

For details, check the workflow run linked above.

---

# [Comment #1]() by [c-vigo]()

_Posted on March 13, 2026 at 02:11 PM_

Diagnostic findings from release run https://github.com/vig-os/devcontainer/actions/runs/23054106926 (job https://github.com/vig-os/devcontainer/actions/runs/23054106926/job/66962755426):

- Failure is isolated to  -> .
- Failing test: .
- Error is a hard timeout, not an assertion mismatch:
  - 
- In same release stream, this specific test has passed on arm64 (example: run 23049118093, arm64 job 66945611261), and it also does not reproduce consistently in CI/local.

Assessment:
- Most likely intermittent runner/resource jitter on amd64 causing  to exceed the strict 10s budget.
- Lower likelihood of deterministic logic bug in  because behavior is inconsistent across runs/architectures.

Suggested next action (minimal-risk):
1) Increase this test timeout from 10s to 20-30s to reduce false negatives.
2) Add timeout diagnostics (or lightweight timing logs) around  so any future slow path is attributable.

Note:
- Node.js 20 deprecation warnings are present in this run, but they are warnings and not the direct cause of this failure.

---

# [Comment #2]() by [c-vigo]()

_Posted on March 13, 2026 at 02:11 PM_

Diagnostic findings from release run https://github.com/vig-os/devcontainer/actions/runs/23054106926 (job https://github.com/vig-os/devcontainer/actions/runs/23054106926/job/66962755426):

- Failure is isolated to Build and Test (amd64) -> Run integration tests.
- Failing test: tests/test_integration.py::TestVigOsConfig::test_initialize_writes_devcontainer_version_to_env.
- Error is a hard timeout, not an assertion mismatch:
  - subprocess.TimeoutExpired: initialize.sh timed out after 10 seconds.
- In the same release stream, this specific test has passed on arm64 (example: run 23049118093, arm64 job 66945611261), and it also does not reproduce consistently in CI/local.

Assessment:
- Most likely intermittent runner/resource jitter on amd64 causing initialize.sh to exceed the strict 10s budget.
- Lower likelihood of deterministic logic bug in initialize.sh because behavior is inconsistent across runs/architectures.

Suggested next action (minimal risk):
1) Increase this test timeout from 10s to 20-30s to reduce false negatives.
2) Add timeout diagnostics (or lightweight timing logs) around initialize.sh so any future slow path is attributable.

Note:
- Node.js 20 deprecation warnings are present in this run, but they are warnings and not the direct cause of this failure.

---

# [Comment #3]() by [c-vigo]()

_Posted on March 13, 2026 at 03:54 PM_

The problem was with workflow permissions for the Commit App

