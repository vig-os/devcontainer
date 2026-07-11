---
type: issue
state: closed
created: 2026-07-03T08:09:02Z
updated: 2026-07-06T14:02:42Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/805
comments: 1
labels: security, security-scan
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:44.232Z
---

# [Issue 805]: [Nightly security scan: HIGH/CRITICAL vulnerabilities in :latest](https://github.com/vig-os/devkit/issues/805)

Nightly scan found **fixable HIGH/CRITICAL** vulnerabilities in the resolved image below (after `.trivyignore`).

- **Image (resolved):** `ghcr.io/vig-os/devcontainer@sha256:acec45749e68a4d252cee3b5417ae32096c4b857ed7be8d1066dbe33f64c5222`
- **Tag pulled:** `ghcr.io/vig-os/devcontainer:latest`
- **Scan date (UTC):** 2026-07-03T08:09:01Z
- **Workflow run:** https://github.com/vig-os/devcontainer/actions/runs/28647359378
- **Security tab:** https://github.com/vig-os/devcontainer/security

Close this issue after the image is remediated and the next scheduled run passes the gate.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 12:09 PM_

This will be resolved by the 0.4.0 Nix publish-cutover (#639), not by patching the Debian image: the flagged image is the final Debian-built `:latest` (0.3.9), whose build path was decommissioned (#642). At promote, `:latest` is re-pointed at the Nix-built 0.4.0 and the merge to `main` replaces this Trivy-on-Debian nightly with the vulnix scan. Keep open until the first green scheduled vulnix nightly on `main` post-promote.

