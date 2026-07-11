---
type: issue
state: closed
created: 2026-07-04T18:00:26Z
updated: 2026-07-04T20:17:04Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/842
comments: 2
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:37.632Z
---

# [Issue 842]: [Release 0.4.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/842)


Release 0.4.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** build-and-test, vulnix-gate, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28714705601)

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

_Posted on July 4, 2026 at 06:07 PM_

**Diagnosis — both failures are `release.yml` defects, not regressions in the release content.** This was the first Nix image through the release lane; two spots of the workflow were never exercised against the Nix stack:

1. **`Build and Test (amd64)` / integration tests** — `release.yml:760` pins the build-and-test matrix to `ubuntu-22.04`/`ubuntu-22.04-arm` (podman **3.4.4**). The identical `test-integration` action runs green in `ci.yml` and `nix-image.yml` on `ubuntu-24.04`/`ubuntu-24.04-arm` (podman **4.9.3**) — including on the same commit earlier today. Under podman 3.4.4's rootless UID mapping, `init-workspace.sh`'s rsync inside the container fails to chmod files in the `/workspace` volume mount (`Operation not permitted`, rsync exit 23), killing the scaffold and failing the fixture with pexpect EOF.

2. **`Vulnix CVE Gate`** — the scanner step intends to tolerate vulnix exit codes ≤ 2 (`0` none / `1` whitelisted / `2` findings), but unlike `security-scan.yml:111` it misses the `|| rc=$?` capture. GitHub's default shell is `bash -e {0}`, and the step's `set -uo pipefail` does not unset `-e`, so vulnix's normal exit 2 (findings present — the very findings triaged into `.vulnixignore` via #808/#811) aborts the step before `vulnix-gate` ever evaluates the register. The nightly and the manual dispatch pass because `security-scan.yml` captures the exit code correctly.

Forward-fix (per policy, no tag deleted — rc1 was never tagged since publish was skipped): one bugfix PR into `release/0.4.0` switching the matrix to `ubuntu-24.04`/`ubuntu-24.04-arm` (same expression as `nix-image.yml:64`) and porting `security-scan.yml`'s capture/retry pattern to the release vulnix step, preserving the "crash (exit > 2) must fail, not read as clean" intent.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:17 PM_

Resolved by #843 (merged `ebe1b106`): candidate run [28717901832](https://github.com/vig-os/devcontainer/actions/runs/28717901832) is fully green — vulnix-gate passes with the exit-code capture, and both build-and-test legs (incl. the integration tests that failed here) pass on the ubuntu-24.04 runners. 0.4.0-rc1 published.

