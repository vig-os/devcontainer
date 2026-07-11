---
type: issue
state: closed
created: 2026-06-30T08:34:09Z
updated: 2026-06-30T11:19:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/760
comments: 1
labels: bug, priority:medium, area:ci, effort:medium, area:testing
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:51.410Z
---

# [Issue 760]: [[BUG] arm64 image testing stranded post-merge by nix-image.yml branch filter](https://github.com/vig-os/devkit/issues/760)

## Description

PR #670 review (larger nit). The `nix-image.yml` branch filter strands arm64
image testing post-merge: `ci.yml` build-image is amd64-only, so once the
migration branch merges, arm64 image coverage is lost.

## Steps to Reproduce

1. Inspect `nix-image.yml` branch filter and `ci.yml` build-image matrix.
2. Post-merge on `dev`, arm64 image is no longer exercised.

## Expected Behavior

arm64 image testing coverage is retained on `dev`.

## Actual Behavior

arm64 coverage is stranded by the branch filter once merged.

## Fix

Restore arm64 image-testing coverage on `dev` (extend the matrix / adjust the
`nix-image.yml` branch filter).

## Acceptance Criteria

- [ ] arm64 image is exercised on `dev` post-merge
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Files

- `.github/workflows/nix-image.yml`, `.github/workflows/ci.yml`

## Related Issues

Parent: #625. From PR #670 review (Comment 2, larger nits).

**Priority:** Medium · **Changelog Category:** Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:19 AM_

Landed on the migration branch via #767.

