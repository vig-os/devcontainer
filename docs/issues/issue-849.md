---
type: issue
state: closed
created: 2026-07-04T19:26:27Z
updated: 2026-07-04T20:17:08Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/849
comments: 2
labels: bug, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:36.891Z
---

# [Issue 849]: [Release 0.4.0-rc1 failed -- automatic rollback](https://github.com/vig-os/devkit/issues/849)


Release 0.4.0-rc1 encountered an error during the automated release workflow.

**Failed Jobs:** build-and-test, publish

**Workflow Run:** [View logs](https://github.com/vig-os/devcontainer/actions/runs/28716836525)

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

_Posted on July 4, 2026 at 07:28 PM_

**Diagnosis — the release lane's Trivy step is the last Debian-era blocking scanner; the ratified Nix posture makes Trivy awareness-only.**

Third candidate run: validate, finalize, **vulnix-gate**, and (new since #843/#848) the amd64 **image + integration tests all passed** — the run died at `Scan image for vulnerabilities` (`release.yml`, `exit-code: '1'` on HIGH/CRITICAL against the raw image tar with only `.trivyignore`).

Findings: ~14 HIGH / 0 CRITICAL, all in language-ecosystem packages embedded in shipped binaries (Rust crates `gix-fs`/`thin-vec`/`quinn-proto`, Go `golang.org/x/net`/`rekor` in Go binaries, npm `sigstore`) — the same 2026-07 batch already triaged into `.vulnixignore` (which is why the blocking vulnix-gate passes).

Everywhere else the org already runs Trivy on the Nix image as **defense-in-depth, awareness only** per the #637 decision:
- `security-scan.yml:145-154` — "Trivy SBOM-mode scan (defense in depth, awareness only)", `exit-code: '0'`, `continue-on-error: true`
- `ci.yml:323,334` — `exit-code: '0'` (non-blocking report), which is why the same image passed the release PR's Security Scan check today

The blocking CVE control for the release is the **vulnix-gate + `.vulnixignore`** (#639). Fix: align the release build-and-test Trivy step with the ratified posture (`exit-code: '0'`, `continue-on-error: true`), keeping the table output in the job log as awareness signal.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 08:17 PM_

Resolved by #850 (merged `80de2c52`): candidate run [28717901832](https://github.com/vig-os/devcontainer/actions/runs/28717901832) fully green — the Trivy step now runs awareness-only per the #637 posture; the blocking vulnix-gate passed on the triaged `.vulnixignore` register. 0.4.0-rc1 published.

