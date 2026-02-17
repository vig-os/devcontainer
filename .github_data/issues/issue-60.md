---
type: issue
state: closed
created: 2026-02-17T19:33:45Z
updated: 2026-02-17T19:34:27Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/60
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-17T19:34:46.721Z
---

# [Issue 60]: [[BUG] Host-specific paths in .gitconfig and unreliable postAttachCommand lifecycle](https://github.com/vig-os/devcontainer/issues/60)

## Description

The devcontainer setup scripts have two related issues with git/SSH/gh configuration inside the container:

1. **Host-absolute paths in `.gitconfig`**: `copy-host-user-conf.sh` exports the host's global git config verbatim, embedding host-specific absolute paths (e.g. `/Users/<user>/.ssh/id_ed25519_github.pub`, `/Users/<user>/.config/git/allowed-signers`) and host-only entries (Homebrew credential helpers, `core.excludesfile`). These paths don't exist inside the container.

2. **Unreliable `postAttachCommand`**: All one-time setup (git config placement, SSH key copy, gh auth, pre-commit install) runs via `postAttachCommand`, which is a known issue with Cursor (and sometimes VS Code) — it frequently doesn't fire, leaving the container without git config, SSH signing keys, or gh authentication.

## Steps to Reproduce

1. Run the install script: `curl -sSf .../install.sh | bash -s -- ~/my-project`
2. Inspect `.devcontainer/.conf/.gitconfig` — contains host-absolute paths
3. Open project in Cursor and reopen in container
4. Check `ls /root/.ssh/` — may only contain `known_hosts` (postAttachCommand didn't fire)
5. Check `git config user.signingkey` — points to host path like `/Users/.../id_ed25519_github.pub`

## Expected Behavior

- `.conf/.gitconfig` should contain container-appropriate paths (`/root/.ssh/...`, `/root/.config/git/...`)
- Host-only entries (credential helpers, excludesfile, includeIf) should be stripped at export time
- One-time setup (git config, SSH keys, gh auth, pre-commit) should run reliably on container creation
- Only lightweight verification (SSH agent check, gh auth status) should depend on `postAttachCommand`

## Actual Behavior

- `.gitconfig` has host paths that don't exist in the container
- All setup depends on `postAttachCommand` which frequently doesn't trigger in Cursor
- Container may start without any git configuration, SSH keys, or gh authentication

## Environment

- **OS**: macOS (Darwin 24.5.0)
- **Container Runtime**: Podman
- **Editor**: Cursor
- **Image Version**: latest

## Possible Solution

1. Fix `copy-host-user-conf.sh` awk block to rewrite paths and strip host-only entries at export time (fix at the source)
2. Refactor lifecycle: move one-time setup into `postCreateCommand`, keep only auth verification in `postAttachCommand`
3. Extract SSH agent + gh auth verification into a separate `verify-auth.sh` script
---

# [Comment #1]() by [gerchowl]()

_Posted on February 17, 2026 at 07:34 PM_

Fixed in commit 07aaab3 on `dev` branch.

**Changes:**
- `copy-host-user-conf.sh`: awk block now rewrites `signingkey` and `allowedsignersfile` to container paths (`/root/...`) and strips host-only entries (`credential`, `excludesfile`, `includeIf`) at export time
- `post-create.sh`: now runs all one-time setup (`init-git.sh`, `setup-git-conf.sh`, `init-precommit.sh`, `uv sync`)
- `setup-git-conf.sh`: stripped down to one-time file placement and gh auth (removed SSH agent scanning)
- `verify-auth.sh`: new script for lightweight SSH agent + gh auth verification
- `post-attach.sh`: now only calls `verify-auth.sh` (no longer critical if it doesn't fire)
- Tests updated to expect `verify-auth.sh` in file lists

