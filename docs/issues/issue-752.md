---
type: issue
state: closed
created: 2026-06-30T08:33:47Z
updated: 2026-06-30T09:40:03Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/752
comments: 1
labels: bug, priority:high, area:ci, area:image, effort:small
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:54.554Z
---

# [Issue 752]: [[BUG] B1 — release.yml publish retags a tag the Nix image never carries](https://github.com/vig-os/devkit/issues/752)

## Description

PR #670 review (B1). The release publish path retags from a tag that the Nix
image never carries, so the publish step fails with **"No such image"**.

`flake.nix:603` bakes `tag = "nix-dev"`; `build-image/action.yml` saves the tar
verbatim and never retags; `release.yml:952-956` then runs
`docker tag "$REPO:$BUILD_VERSION-$arch" …` against an image tag that does not
exist.

## Steps to Reproduce

1. Run a (gated) release dry-run that loads the Nix image and reaches the
   `publish` job.
2. Observe `docker tag "$REPO:$BUILD_VERSION-$arch" …` fail with "No such image".

## Expected Behavior

The loaded image tag is captured dynamically and used as the retag source, so
publish succeeds.

## Actual Behavior

`publish` retags from the hardcoded `$BUILD_VERSION-$arch` tag, which the baked
`nix-dev` image never carries → "No such image".

## Fix

In the `publish` job, capture the loaded tag dynamically and retag from it.
**Reuse the pattern already in `nix-image.yml:152-156`**
(`docker load … | sed -n 's/^Loaded image: //p' | head -n1`). Either retag in
`release.yml` publish, or have `build-image/action.yml` emit the loaded tag as a
step output consumed downstream.

## Acceptance Criteria

- [ ] `publish` retags from the dynamically-captured loaded tag (no hardcoded `nix-dev`/`$BUILD_VERSION-$arch` assumption)
- [ ] Gated release dry-run: `docker load` → tag capture → `docker tag` succeeds (no "No such image")
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Files

- `.github/workflows/release.yml` (publish ~952-956)
- optionally `.github/actions/build-image/action.yml`

## Related Issues

Parent: #625. References #639 (gated publish-cutover). From PR #670 review (Comment 2, B1).

**Changelog Category:** Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 09:40 AM_

Landed on the migration branch via #763 (merge `f3f22e3`).

