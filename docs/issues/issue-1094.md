---
type: issue
state: closed
created: 2026-07-15T07:14:59Z
updated: 2026-07-15T07:37:16Z
author: github-actions[bot]
author_url: https://github.com/github-actions[bot]
url: https://github.com/vig-os/devkit/issues/1094
comments: 1
labels: security, security-scan
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-15T11:04:53.681Z
---

# [Issue 1094]: [Nightly security scan: unexcepted HIGH/CRITICAL vulnix findings](https://github.com/vig-os/devkit/issues/1094)

The nightly vulnix gate found **unexcepted HIGH/CRITICAL** CVEs in the Nix image closure (after `.vulnixignore`).

- **Scan target:** flake `devkitImageEnv` (image package closure)
- **Scan date (UTC):** 2026-07-15T07:14:58Z
- **Workflow run:** https://github.com/vig-os/devkit/actions/runs/29396607272
- **Findings artifact:** `nix-image-cve-scan` on the run above (`vulnix-findings.json`, `vulnix-report.txt`)
- **Security tab:** https://github.com/vig-os/devkit/security

**To remediate:** advance the pinned nixpkgs rev if a fix has landed, or add a time-boxed `.vulnixignore` exception with a rationale (see `docs/CONTAINER_SECURITY.md`). Close this issue once a later scheduled run passes the gate.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 07:37 AM_

Remediated in #1098 (merged to `dev`). Added a time-boxed `.vulnixignore` block for the two new perl 5.42.0 findings — CVE-2026-13221 (9.1) and CVE-2026-57432 (8.4) — with `Expiration: 2026-08-14` and verified rationale (fixes exist only in the perl 5.43.x dev series; no stable rev to advance to yet). `vulnix-gate` against this run's artifact with the merged register reports **0 blocking findings**. Closing manually since the fix merged to `dev`, not the default branch; a later scheduled scan will confirm the gate green.

