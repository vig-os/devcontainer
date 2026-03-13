---
type: issue
state: open
created: 2026-02-17T18:35:19Z
updated: 2026-02-18T16:31:06Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/57
comments: 1
labels: bug, priority:medium, area:ci, effort:small, semver:patch
assignees: c-vigo
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-19T00:08:12.687Z
---

# [Issue 57]: [Inconsistent version tag convention: git tags use 'v' prefix, GHCR image tags do not](https://github.com/vig-os/devcontainer/issues/57)

## Problem

Git tags use a `v` prefix (`v0.2.1`) while GHCR container image tags use bare semver (`0.2.1`, `latest`). This mismatch is confusing and leads to errors when users naturally try the git tag format with container commands:

```bash
# Fails — tag v0.2.1 does not exist in the registry
just pull v0.2.1
podman pull ghcr.io/vig-os/devcontainer:v0.2.1

# Works — bare semver
just pull 0.2.1
podman pull ghcr.io/vig-os/devcontainer:0.2.1
```

The `--version` flag in `install.sh` also expects the bare semver format, which contradicts what users see in GitHub releases (e.g. `v0.2.1`).

## Suggestion

Pick one convention and apply it consistently, or publish image tags under **both** formats (`0.2.1` and `v0.2.1`) so either works. Options:

1. **Publish both tags** in the release workflow — lowest friction, no breaking change
2. **Strip the `v` prefix in tooling** — e.g. `install.sh` and `just pull` could auto-strip a leading `v` before passing the tag to the registry
3. **Align on one format everywhere** — more disruptive but cleaner long-term

## Context

- Git tags: `v0.1`, `v0.2.0`, `v0.2.1`
- Image tags: `latest`, `0.2.1`, etc. (no `v` prefix)
- README documented `--version 1.0.0` (non-existent version) — already fixed in a pending change along with a note about the tag convention

/cc @c-vigo
---

# [Comment #1]() by [c-vigo]()

_Posted on February 18, 2026 at 01:35 PM_

- Consolidate into version tags `X.Y.Z`without `v`
- Try to update existing tags and released images (or re-tag them)


