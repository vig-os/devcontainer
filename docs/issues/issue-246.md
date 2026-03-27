---
type: issue
state: open
created: 2026-03-09T12:48:10Z
updated: 2026-03-09T12:48:10Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/246
comments: 0
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-10T04:14:45.261Z
---

# [Issue 246]: [feat: seamless local-to-remote handoff with just remote-devc](https://github.com/vig-os/devcontainer/issues/246)

## Context

After #70 merges and the devcontainer image is published to GHCR, the main use case for `devc-remote.sh` becomes: "I'm developing locally, now I want to continue on a remote machine."

Currently this requires knowing the full `gh:org/repo:branch` syntax. It should be a single command from within any project.

Parent: #70

## Proposed UX

From any project with a devcontainer:

```bash
just remote-devc ksb-meatgrinder
just remote-devc --force ksb-meatgrinder    # auto-push before deploy
just remote-devc ksb-meatgrinder:~/custom   # override remote path
```

### Auto-detection

The recipe derives everything from the current repo state:
- **Repo**: `git remote get-url origin` → `gh:org/repo`
- **Branch**: `git branch --show-current` → `:branch`
- **IDE**: auto-detect from `$TERM_PROGRAM` (existing)
- **GHCR auth**: forward local credentials on every deploy (idempotent)

### Unpushed commits guard

- Default: check for unpushed commits on current branch. If any, warn and abort.
- `--force` / `-f`: auto-push to origin before deploying.
- Rationale: deploying to remote without pushing means the remote clone won't have your latest work. No valid reason to skip the push.

```
$ just remote-devc ksb-meatgrinder
✗ 3 unpushed commits on feature/my-branch. Push first or use --force.

$ just remote-devc --force ksb-meatgrinder
ℹ Pushing feature/my-branch to origin...
✓ Pushed 3 commits
ℹ Deploying gh:vig-os/fd5:feature/my-branch to ksb-meatgrinder...
```

## Implementation

1. **Move GHCR auth forwarding into normal flow** — `bootstrap_forward_ghcr_auth` runs after `check_ssh`, before `compose up`. Idempotent, no config file needed.
2. **Add `--force` flag to `devc-remote.sh`** — pushes current branch to origin before cloning on remote.
3. **Add unpushed commits check** — in `main()`, after `parse_args`, before `remote_clone_project`. Abort if unpushed and no `--force`.
4. **Add `remote-devc` recipe to `justfile.base`** — wraps `devc-remote.sh` with auto-detected `gh:org/repo:branch`.
5. **Simplify/remove `--bootstrap`** — with GHCR auth in normal flow and image from registry, bootstrap's only job was auth forwarding + local build. Post-release, the image comes from GHCR. Bootstrap can be removed or reduced to a no-op that prints "no longer needed."

## Out of scope

- Interactive project selection (pick from multiple repos)
- Multi-server deployment
- Automatic `--open cursor` from WezTerm (handled by existing auto-detect)

Refs: #70
