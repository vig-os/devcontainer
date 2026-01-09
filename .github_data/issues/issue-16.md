---
type: issue
state: closed
created: 2025-12-16T10:02:02Z
updated: 2026-01-06T15:43:29Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/16
comments: 2
labels: none
assignees: none
milestone: 0.2
projects: none
relationship: none
synced: 2026-01-09T16:17:34.074Z
---

# [Issue 16]: [feat: Use pre-commit cache directly from container image instead of copying](https://github.com/vig-os/devcontainer/issues/16)

## Problem

Currently, `init-workspace.sh` copies **all** template files from `/root/assets/workspace/` to the user's mounted workspace, including the `.pre-commit-cache` directory (518MB, 22K+ files).

Copying this cache through the macOS Podman bind mount is extremely slow (60+ seconds), causing test timeouts and poor user experience.

## Current Workaround

We've excluded `.pre-commit-cache` from the copy operation, which means:
- Workspace init is fast (~2-3 seconds)
- But users must wait 30-60s on first `pre-commit run` to rebuild the cache

## Proposed Solution

The pre-commit cache is already baked into the container image at `/root/assets/workspace/.pre-commit-cache`. Instead of copying it, we should use it directly:

### Option 1: Set PRE_COMMIT_HOME environment variable
```yaml
# In docker-compose.yml
environment:
  - PRE_COMMIT_HOME=/root/assets/workspace/.pre-commit-cache
```

### Option 2: Symlink in post-create.sh
```bash
ln -sf /root/assets/workspace/.pre-commit-cache "$HOME/.cache/pre-commit"
```

## Benefits

- **Fast init**: No 500MB copy through bind mount
- **Instant pre-commit**: Cache is immediately available
- **Best of both worlds**: Fast startup AND fast first pre-commit run

## Related

This is part of a larger architectural discussion about moving more work inside the container (post-create.sh) rather than doing it on the host (init-workspace.sh). See discussion in PR/commits for context.

## Tasks

- [ ] Test `PRE_COMMIT_HOME` approach
- [ ] Verify pre-commit hooks work correctly with shared cache
- [ ] Update docker-compose.yml or post-create.sh
- [ ] Remove cache exclusion workaround from init-workspace.sh (if no longer needed)
- [ ] Update documentation
---

# [Comment #1]() by [c-vigo]()

_Posted on December 18, 2025 at 08:26 AM_

Should this be included in Release 0.2?

---

# [Comment #2]() by [gerchowl]()

_Posted on December 18, 2025 at 09:14 AM_

is already done. cache lives only in devcontainer under /workspace/..cache..
never copied to host. host downloads it itself .. which is once for a repo ever .. so really not that often.
and potentially leaving open for someone to have a common folder for his pre-commit cache

