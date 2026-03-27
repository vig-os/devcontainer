---
type: issue
state: closed
created: 2026-03-03T07:30:26Z
updated: 2026-03-03T09:55:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/213
comments: 0
labels: chore, priority:low, area:image, effort:small, semver:patch
assignees: c-vigo
milestone: 0.3
projects: none
parent: none
children: 88
synced: 2026-03-14T04:16:04.780Z
---

# [Issue 213]: [[CHORE] Refresh pinned python:3.12-slim-bookworm image digest in Containerfile](https://github.com/vig-os/devcontainer/issues/213)

### Chore Type
Dependency update

### Description
The base image line in `Containerfile` pins `python:3.12-slim-bookworm` to a specific digest. Security/update checks now report that the pinned digest is out of date.
Update the digest to the current upstream value for the same tag so builds stay reproducible while receiving latest base-image patches.

### Acceptance Criteria
- [ ] Resolve the current digest for `python:3.12-slim-bookworm`
- [ ] Update the pinned digest in `Containerfile`
- [ ] Build/validate succeeds with the new digest
- [ ] No tag change (remain on `python:3.12-slim-bookworm`), only digest refresh

### Implementation Notes
- Target file: `Containerfile`
- Keep pinning-by-digest policy intact (tag + digest)
- Prefer minimal diff (single-line base image update + any required note updates)

### Related Issues
- Related to #88 (dependency/security maintenance in image context)

### Priority
Low

### Changelog Category
No changelog needed

### Additional Context
Observed warning: `The image digest is out of date`.
