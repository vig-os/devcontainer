---
type: issue
state: closed
created: 2026-07-10T09:13:13Z
updated: 2026-07-10T10:19:03Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/965
comments: 1
labels: security, security-scan
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:15.519Z
---

# [Issue 965]: [Nightly vulnix security scan fails silently — auto-issue creation lost in Nix cutover](https://github.com/vig-os/devkit/issues/965)

## Summary

The **Scheduled Security Scan** no longer opens a GitHub issue when the nightly gate fails — so a red scan is now **silent** (only a red run in the Actions tab). This regressed during the Nix cutover.

## History / root cause

The Debian `:latest` Trivy job carried a deduplicated *"Create GitHub issue on gate failure"* step (`issues: write` + `gh issue create`, dedup by the `security-scan` label). It filed [#805](https://github.com/vig-os/devcontainer/issues/805), [#602](https://github.com/vig-os/devcontainer/issues/602), [#567](https://github.com/vig-os/devcontainer/issues/567), [#549](https://github.com/vig-os/devcontainer/issues/549), [#521](https://github.com/vig-os/devcontainer/issues/521), [#512](https://github.com/vig-os/devcontainer/issues/512).

- `c6368fa0` rewrote the scan; `1d4e9db1` *"build(nix): decommission the Debian build path"* (2026-06-24) removed the Debian job **and its issue-creation step**. The replacement `scan-nix-image` (vulnix) job never got one — an explicit TODO in the code: *"SARIF upload + a deduplicated issue (like scan-latest) land with the actual publish-cutover."*
- The current `scan-nix-image` job has `permissions: contents: read` only — it **cannot** open an issue.

Because the schedule runs from the default branch, the removal only bit once it reached `main` with the **0.5.0** merge (2026-07-09). The **2026-07-10** run ([29079456127](https://github.com/vig-os/devcontainer/actions/runs/29079456127), CVE-2026-60002, handled in #963) was the first to fail **silently** — it had to be spotted by hand.

Secondary: the `security-scan` label description is stale — *"...findings for :latest image"* — the scan is now the Nix image.

## Fix

Restore a deduplicated issue-creation step on the `scan-nix-image` vulnix gate-failure path (grant `issues: write`), adapting the old Debian step to vulnix (link the run + the `nix-image-cve-scan` artifact holding `vulnix-findings.json`/`vulnix-report.txt`). Refresh the stale label description.

Targets `release/0.5.1` (fixing it there means 0.5.1 ships with working alerting rather than waiting for the next cycle).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 10, 2026 at 10:19 AM_

Fixed in #966

