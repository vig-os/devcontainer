---
type: issue
state: closed
created: 2026-02-20T10:23:44Z
updated: 2026-02-20T13:59:33Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/108
comments: 2
labels: feature, area:image, effort:small, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:35.576Z
---

# [Issue 108]: [[FEATURE] Install cursor-agent CLI in devcontainer image](https://github.com/vig-os/devcontainer/issues/108)

### Description

Install the `cursor-agent` CLI (`agent` command) in the devcontainer image so that worktree recipes (`just worktree-start`, etc.) can run autonomously inside the container without manual installation.

### Problem Statement

The worktree workflow (`justfile.worktree`) depends on the `agent` CLI for launching autonomous cursor-agent sessions in tmux. Currently, `agent` is not installed in the container image nor in any lifecycle script. Running `just worktree-start` fails immediately with:

```
[ERROR] cursor-agent CLI is not installed.
```

Users must manually install it each time a container is created, which breaks the autonomous workflow.

### Proposed Solution

Add a `cursor-agent` installation step to the `Containerfile`, similar to how `gh`, `just`, and `uv` are installed — fetching the latest release with checksum verification:

```bash
RUN curl https://cursor.com/install -fsSL | bash
```

Verify with `agent --version` after install.

### Alternatives Considered

- **Install in `post-create.sh`**: Works but adds network dependency at container creation time and is slower than baking it into the image.
- **Leave as manual step**: Current state — breaks the autonomous worktree workflow.

### Impact

- All users of the worktree workflow benefit — `just worktree-start` works out of the box.
- Backward compatible — no existing functionality is changed.

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 20, 2026 at 01:16 PM_

## Implementation Plan

Issue: #108
Branch: feature/108-install-cursor-agent-cli

### Context

The Containerfile change was contributed externally in PR #110 (by @nacholiya, commit preserved with original authorship). CHANGELOG entry and `Refs: #108` added by maintainer. TDD order is inverted because we adopted an external contribution — the test commit retroactively closes the gap.

### Tasks

- [x] Task 1: Add failing test for `agent` CLI presence — `tests/test_image.py` — verify: `just test-image` (expect fail, image not yet rebuilt with change)
- [x] Task 2: Rebuild image and confirm test passes — verify: `just build && just test-image`

### Notes

- Build revealed the cursor-agent installer puts the binary in `~/.local/bin` which wasn't in PATH during docker build. Fixed by adding `ENV PATH="/root/.local/bin:${PATH}"` before the install step, matching the cargo-binstall pattern. Also simplified the RUN step (removed redundant `command -v` check since `set -e` already catches failures).

---

# [Comment #2]() by [nacholiya]()

_Posted on February 20, 2026 at 01:32 PM_

Thanks for integrating the change and preserving authorship — appreciate it!

