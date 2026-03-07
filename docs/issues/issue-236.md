---
type: issue
state: open
created: 2026-03-06T21:57:36Z
updated: 2026-03-06T21:57:36Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/236
comments: 0
labels: feature, area:workflow, effort:large
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:36.631Z
---

# [Issue 236]: [devc-remote gh:org/repo:branch — clone project repo and start devcontainer](https://github.com/vig-os/devcontainer/issues/236)

## Context

After `--bootstrap` (#235) prepares a remote host with the devcontainer image, we still need a way to clone a project repo and start its devcontainer in one command.

Refs: #70, #231, #235

## Proposal

Support a `gh:org/repo[:branch]` target syntax in `devc-remote.sh`:

```bash
# Clone fd5, checkout main, init-workspace, compose up, connect
devc-remote.sh ksb-meatgrinder gh:vig-os/fd5

# Clone at specific branch
devc-remote.sh ksb-meatgrinder gh:vig-os/fd5:feature/my-branch

# Existing path still works (current behavior)
devc-remote.sh ksb-meatgrinder:~/Projects/fd5
```

### Flow

1. Read remote config (`~/.config/devc-remote/config.yaml` from #235) for `projects_dir`
2. Clone `gh:org/repo` to `<projects_dir>/<repo>` (or fetch + checkout if already cloned)
3. Checkout `:branch` if specified, default branch otherwise
4. Run `init-workspace.sh` on remote (resolves `{{IMAGE_TAG}}`, `{{SHORT_NAME}}` templates)
5. Proceed with existing `compose up` + connect flow

### Re-run behavior

- Repo already cloned → `git fetch && git checkout <branch>` (no re-clone)
- Container already running on the right branch → skip compose restart, just connect
- Different branch requested → checkout, re-init if needed, `compose up`

### Config interaction

Uses `projects_dir` from remote config (#235) to determine clone location. Falls back to `~/Projects` if no config exists.

## Acceptance criteria

- [ ] `gh:org/repo` clones to `<projects_dir>/<repo>` on remote
- [ ] `gh:org/repo:branch` checks out specified branch
- [ ] Already-cloned repos are fetched, not re-cloned
- [ ] `init-workspace.sh` runs after clone/checkout
- [ ] Existing `host:path` syntax continues working
- [ ] Tests for arg parsing of `gh:` syntax
