---
type: issue
state: closed
created: 2026-06-30T08:33:50Z
updated: 2026-06-30T11:22:07Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/753
comments: 1
labels: bug, priority:high, area:ci, effort:medium, security
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:54.164Z
---

# [Issue 753]: [[BUG] B2 — vulnix-gate not wired to the release publish path](https://github.com/vig-os/devkit/issues/753)

## Description

PR #670 review (B2). The `vulnix-gate` is not wired to the publish path, so the
release can ship an image that nightly vulnix would have blocked.

`vulnix-gate` exists only as a step id in the nightly `security-scan.yml:86`.
`release.yml` publish (`needs: [validate, finalize, build-and-test]`, line 807)
has no link to it. The only CVE gate on the publish path is the per-arch Trivy
step (`release.yml:784-793`), which the repo documents as "largely dark" on a
Nix image.

## Steps to Reproduce

1. Inspect `release.yml` publish `needs:` — no vulnix dependency.
2. A HIGH/CRITICAL CVE caught by nightly vulnix would not block a release publish.

## Expected Behavior

A hard vulnix gate blocks the publish path.

## Actual Behavior

No vulnix gate on publish; only the largely-dark Trivy step.

## Fix

Add a hard vulnix gate on the publish path — either a `vulnix-gate` job in
`release.yml` that `publish` `needs:`, or make the nightly a required
pre-publish check. **Reuse** the gate step (`security-scan.yml:85-90`) and
`vig_utils.vulnix_gate`.

## Acceptance Criteria

- [ ] `publish` cannot run unless a vulnix gate has passed
- [ ] Gate reuses `security-scan.yml:85-90` / `vig_utils.vulnix_gate` (no logic duplication)
- [ ] Gated/dry run shows the gate blocking publish on a seeded HIGH/CRITICAL finding
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Files

- `.github/workflows/release.yml`

## Related Issues

Parent: #625. References #639 (gated publish-cutover). From PR #670 review (Comment 2, B2).

**Changelog Category:** Security

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:22 AM_

Landed on the migration branch via #769.

