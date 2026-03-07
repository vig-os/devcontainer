---
type: issue
state: open
created: 2026-03-06T21:57:19Z
updated: 2026-03-06T22:01:02Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/235
comments: 0
labels: feature, area:workflow, effort:large
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:36.943Z
---

# [Issue 235]: [devc-remote --bootstrap: one-time remote host setup with config file](https://github.com/vig-os/devcontainer/issues/235)

## Context

`devc-remote.sh` assumes the remote host is fully set up: devcontainer image available, repos cloned, `init-workspace.sh` run. This makes first-time use on a new remote (e.g. ksb-meatgrinder) a manual multi-step process.

Refs: #70, #231

## Proposal

Add `devc-remote.sh --bootstrap <ssh-host>` that performs one-time remote setup:

### 1. Interactive first-run setup

On first bootstrap (no config file exists yet), prompt the user:

```
No devc-remote config found on ksb-meatgrinder.
Where should projects be cloned? [~/Projects]: 
Creating ~/.config/devc-remote/config.yaml on ksb-meatgrinder...
```

- Prompt for `projects_dir` with sensible default (`~/Projects`)
- Write config, print its path so user knows where to edit later:
  `Config written to ~/.config/devc-remote/config.yaml — edit to customize.`
- `--yes` flag skips prompt, uses defaults

### 2. Remote config file

`~/.config/devc-remote/config.yaml` on the remote:

```yaml
projects_dir: ~/Projects          # where repos get cloned
devcontainer_repo: vig-os/devcontainer  # which repo to build the base image from
devcontainer_path: ~/Projects/devcontainer  # resolved path
image_tag: dev                    # tag used by build.sh
registry: ghcr.io/vig-os/devcontainer
```

- Created with user input (or defaults with `--yes`) on first `--bootstrap`
- User can edit afterwards to change paths, registry, etc.
- Subsequent `devc-remote` commands read this config

### 3. GHCR auth forwarding

Forward local container registry credentials to the remote:
- Copy `~/.config/containers/auth.json` (podman) or `~/.docker/config.json` to remote
- Or use a scoped GHCR token via env var (`GHCR_TOKEN`)
- Needed so the remote can pull base images or fallback layers

### 4. Build devcontainer image locally on remote

- Clone `vig-os/devcontainer` to `config.devcontainer_path`
- Run `scripts/build.sh` → produces local `ghcr.io/vig-os/devcontainer:dev`
- All downstream project repos use this cached image (no registry pull needed)

### 5. Re-run behavior

`--bootstrap` on an already-bootstrapped host:
- Reads existing config (doesn't overwrite, doesn't re-prompt)
- `git pull` in devcontainer repo
- Rebuilds image (picks up changes)
- Prints: `Config: ~/.config/devc-remote/config.yaml (existing, not modified)`

## Acceptance criteria

- [ ] First run prompts for `projects_dir` with default, mentions config file path
- [ ] `--yes` skips prompt, uses defaults
- [ ] Config file is human-editable, controls `projects_dir` and image settings
- [ ] GHCR auth forwarded from local to remote
- [ ] Devcontainer image built locally on remote
- [ ] Re-running bootstrap reads existing config without re-prompting
- [ ] Tests for config creation and re-run idempotency
