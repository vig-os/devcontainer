---
type: issue
state: closed
created: 2026-02-20T10:34:52Z
updated: 2026-07-07T14:39:17Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devkit/issues/109
comments: 3
labels: discussion, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:28.643Z
---

# [Issue 109]: [[DISCUSSION] Optimize CI pipeline for PRs to dev — full security scan on every PR?](https://github.com/vig-os/devkit/issues/109)

### Description

Should the full CI pipeline (including security scans and other long-running jobs) run on every PR to `dev`, or can we slim it down to "it builds & tests pass" for faster feedback?

Currently, PRs to `dev` run the complete CI suite including security scanning, which adds significant time. With the goal of faster PR turnaround, we should discuss whether that's necessary or if a smarter approach exists.

### Context / Motivation

CI runs on PRs to `dev` take a long time, partly due to security scans and other heavyweight checks. For a branch that primarily serves as an integration target (not production), this slows down the development loop without a clear proportional benefit. The question is whether the full suite is justified for every PR to `dev` or only for PRs into `main`.

### Options / Alternatives

1. **Minimal CI on PRs to `dev`** — Only run build + test. Reserve security scans and other heavyweight checks for PRs into `main`.
2. **Smart/conditional CI** — Detect what changed and skip security scans when no new packages or version updates are present. E.g., only trigger security scanning when `requirements.txt`, `Dockerfile`, lock files, or similar dependency files change.
3. **Keep full CI everywhere** — Accept the longer times for maximum safety at every stage.

### Open Questions

- Is "it builds & tests pass" sufficient confidence for merging into `dev`?
- Should security scanning only gate PRs into `main`?
- Can we use path-based triggers (e.g., changes to dependency files) to conditionally run security scans on `dev` PRs?
- Are there other long-running CI jobs besides security that could be deferred to the `main` gate?

### Related Issues

_None yet_

### Changelog Category

No changelog needed
---

# [Comment #1]() by [c-vigo]()

_Posted on June 23, 2026 at 06:56 AM_

The Trivy scan-category consolidation discussed here overlaps the CVE rework in #637 (vulnix + SBOM, part of #625); worth resolving together.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 7, 2026 at 09:32 AM_

@gerchowl proposing to close: this discussion pre-dates the Nix migration — the pipeline it debates no longer exists. Security scanning is now vulnix-first (blocking gate on the Nix closure, #637/#639) with Trivy SBOM as defence-in-depth, and the scan-on-PR question was settled by the scheduled-nightly + release-gate design. No branch to prune.

---

# [Comment #3]() by [c-vigo]()

_Posted on July 7, 2026 at 02:39 PM_

Resolved via #910 (merged to \`dev\`).

**Decision:** kept the security scan on **every** PR — rejected path-gating (option 2) because an unchanged image can still be hit by a newly-disclosed CVE, so conditional scanning would create a coverage blind spot. Instead we made the scan itself cheaper.

**Change:** the `Security Scan` job ran Trivy three times over the same image tar (HIGH/CRITICAL, MEDIUM, SBOM). Collapsed the two vuln tiers into one `severity: HIGH,CRITICAL,MEDIUM` run and let the SBOM step reuse the warm Trivy state.

**Result (measured on #910):** job **11m32s → 6m44s (~42%)**, no change to coverage or to the authoritative blocking gate (nightly `vulnix` in `security-scan.yml`). All findings still surfaced.

**Diagnostic / follow-up:** the win came entirely from dropping the redundant vuln run — the DB-cache flags didn't move the needle, which showed the real per-invocation cost is **parsing the image tar** (~2.7 min), not the DB pull. The two remaining Trivy runs each re-parse the same tar. A one-parse approach (`--format cyclonedx` → `trivy sbom` scan) could shave another ~2.7 min, but risks losing the bundled-binary CVE detection (Go stdlib in `gh`/`podman`/`runc`) that is Trivy's whole value on a Nix image per \`docs/security/nix-cutover-scan-overlap.md\` — so it was deliberately not pursued. If sub-5min CI is wanted later, the bigger lever is the job sitting on the critical path behind \`build-image\`; worth a separate issue.

Closing as resolved — current state is acceptable.

