---
type: issue
state: closed
created: 2026-03-03T07:25:04Z
updated: 2026-03-03T09:34:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/212
comments: 0
labels: bug, priority:high, area:workspace, effort:small, semver:patch
assignees: c-vigo
milestone: 0.3
projects: none
parent: none
children: none
synced: 2026-03-14T04:16:05.046Z
---

# [Issue 212]: [[BUG] --force overwrites preserved files when rsync is unavailable](https://github.com/vig-os/devcontainer/issues/212)

## Description
Running `install.sh` with `--force` should preserve user files listed in `PRESERVE_FILES` (including `README.md` and `CHANGELOG.md`).
When `rsync` is not available in the container, the fallback copy path overwrites those files anyway.

## Steps to Reproduce
1. Use an image/environment where `rsync` is not installed.
2. In an existing workspace, customize `README.md` and `CHANGELOG.md`.
3. Run:
   `install.sh <workspace> --version dev --skip-pull --force --org vigOS`
4. Observe init output:
   `Warning: rsync not available, preserved files may be overwritten`
5. Check `README.md` and `CHANGELOG.md`.

## Expected Behavior
Files in the preserve list are never overwritten during `--force`, regardless of copy backend.

## Actual Behavior
Preserved files are overwritten when fallback copy is used (no `rsync`).

## Environment
- **OS**: Linux
- **Container Runtime**: Podman
- **Image Version/Tag**: `ghcr.io/vig-os/devcontainer:dev`
- **Architecture**: amd64

## Additional Context
The init output lists preserved files correctly before copy, but fallback logic does not enforce preservation.
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

## Possible Solution
- Add `rsync` to the image to use the primary safe copy path.
- Keep fallback logic preserving files explicitly for robustness.
- Add regression coverage for fallback behavior.

## Changelog Category
Fixed
