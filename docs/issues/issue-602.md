---
type: issue
state: closed
created: 2026-06-19T09:29:49Z
updated: 2026-07-07T09:39:14Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/602
comments: 1
labels: security, security-scan
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:17.670Z
---

# [Issue 602]: [Nightly security scan: HIGH/CRITICAL vulnerabilities in :latest](https://github.com/vig-os/devkit/issues/602)

Nightly scan found **fixable HIGH/CRITICAL** vulnerabilities in the resolved image below (after `.trivyignore`).

- **Image (resolved):** `ghcr.io/vig-os/devcontainer@sha256:9002a0e8ab76f08dc3d065ad92e859bdfc8379b49cd1f3fcd28b6da2576319e6`
- **Tag pulled:** `ghcr.io/vig-os/devcontainer:latest`
- **Scan date (UTC):** 2026-06-19T09:29:48Z
- **Workflow run:** https://github.com/vig-os/devcontainer/actions/runs/27817416422
- **Security tab:** https://github.com/vig-os/devcontainer/security

Close this issue after the image is remediated and the next scheduled run passes the gate.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 09:39 AM_

For the record (housekeeping via #677): this was the nightly Debian `:latest` Trivy gate issue, closed 2026-06-22 without a note. The scan that produced it is gone — 0.4.0 (promoted, main @ f20bf6b) replaced it with vulnix + SBOM against the Nix image (#637); the Debian path was removed in #642's landed work. Same rationale as the #521 closure. Last `container-image-latest` Trivy upload was 2026-07-06 from the pre-promote main (0.3.9); the 2026-07-07 scheduled run on 0.4.0 produced none.

