---
type: issue
state: open
created: 2026-02-18T01:45:43Z
updated: 2026-02-18T01:45:43Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/70
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T01:45:59.811Z
---

# [Issue 70]: [[FEATURE] Remote devcontainer orchestration via just recipe](https://github.com/vig-os/devcontainer/issues/70)

### Description

Add a `just` recipe (e.g. `just devc --remote host [cmd]`) that orchestrates starting a devcontainer on a remote host and connecting Cursor/VS Code to it. This enables a workflow where developers can spin up their devcontainer on a powerful remote machine from their local terminal.

### Problem Statement

Currently, starting a devcontainer on a remote host requires multiple manual steps:
1. SSH into the remote host
2. Clone/update the repository
3. Check if podman/docker is available and start the container via compose
4. Open Cursor with `--remote ssh-remote+host /path/to/project`
5. Reopen in Container from within Cursor

This is tedious and error-prone. A single `just` command should handle the full orchestration.

### Proposed Solution

A `just` recipe (or small shell script invoked by `just`) in `justfile.base` that:

1. **SSHs into the specified remote host** and runs pre-flight checks:
   - Detects container runtime (podman → docker fallback)
   - Verifies git is available
2. **Clones the repo** if a target path is specified (defaults to `~/`), or skips if already present
3. **Starts the devcontainer** via `compose up -d` (reusing the same compose file stack as the local `just up` recipe)
4. **Opens Cursor/VS Code** attached to the remote host using `cursor --remote ssh-remote+host /path/to/project`

Example usage:
```bash
just devc --remote dev-server.example.com
just devc --remote user@host --clone-to /opt/projects
```

### Alternatives Considered

- **Manual SSH + compose**: Current approach — works but requires many steps.
- **VS Code Remote SSH + "Reopen in Container"**: GUI-only workflow, not scriptable.
- **`devcontainer` CLI over SSH**: Requires `@devcontainers/cli` installed on the remote host (extra dependency).
- **Cursor tunnels (`cursor tunnel`)**: Requires the Cursor CLI on the remote host and a different auth flow.

### Additional Context

- This was identified during the brainstorm for expanding `justfile.base` recipes (see `docs/plans/2026-02-18-justfile-base-recipes-design.md` once saved).
- The local devcontainer recipes (`up`, `down`, `open`, `shell`, etc.) are being added as a prerequisite — the remote recipe builds on the same compose patterns.
- Cursor CLI supports `cursor --remote ssh-remote+user@host /path` for opening remote SSH folders.
- Combining SSH remote + devcontainer attachment in a single CLI call is **not yet supported** by Cursor/VS Code — the recipe will need to handle the two-step flow (SSH connect, then reopen in container) or print instructions for the manual step.

### Impact

- Benefits developers working with remote build/dev machines (e.g. GPU servers, cloud VMs, CI runners)
- Backward compatible — new recipe, no changes to existing behavior
- Requires SSH access configured on the host (uses `~/.ssh/config`)

### Changelog Category

Added
