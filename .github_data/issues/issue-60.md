---
type: issue
state: open
created: 2026-02-17T19:33:45Z
updated: 2026-02-17T19:33:45Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/60
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-17T19:34:02.544Z
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
