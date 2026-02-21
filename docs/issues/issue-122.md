---
type: issue
state: open
created: 2026-02-20T15:35:54Z
updated: 2026-02-21T00:22:45Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/122
comments: 1
labels: chore, area:ci, area:image, effort:small, semver:patch
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-21T04:11:18.657Z
---

# [Issue 122]: [[CHORE] Add hadolint linting for Containerfiles](https://github.com/vig-os/devcontainer/issues/122)

### Chore Type

CI / Build change

### Description

Add [hadolint](https://github.com/hadolint/hadolint) static analysis for all Containerfiles in the repository. Hadolint enforces Dockerfile best practices (pinned base image tags, consolidated `RUN` layers, pinned apk/apt versions, etc.) and integrates shellcheck for inline `RUN` scripts.

### Acceptance Criteria

- [ ] `hadolint` pre-commit hook added to `.pre-commit-config.yaml`, pinned by SHA
- [ ] `Containerfile` passes hadolint with no warnings
- [ ] `tests/fixtures/sidecar.Containerfile` passes hadolint with no warnings
- [ ] `uv run pre-commit run --all-files` exits clean

### Implementation Notes

- Use `hadolint-docker` hook from `https://github.com/hadolint/hadolint`, pinned to `346e4199e4baca7d6827f20ac078b6eee5b39327` (v2.9.3)
- `DL3018` (unpinned apk packages) should be suppressed inline with `# hadolint ignore=DL3018` in fixture files where pinning individual package versions would be brittle
- The main `Containerfile` may need fixes after the hook is wired in

### Related Issues

_None_

### Priority

Medium

### Changelog Category

Added

### Additional Context

_None_
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 12:22 AM_

## Bug: `hadolint-docker` hook requires Docker daemon

@c-vigo The `hadolint-docker` pre-commit hook added in PR #124 requires a running Docker daemon to pull and execute the hadolint container. This breaks local commits on Podman-only setups — which is the project's standard runtime (Docker is not listed in `scripts/requirements.yaml`).

**Reproduction:** Any commit touching `Containerfile` fails with:

```
hadolint.................................................................An unexpected error has occurred: CalledProcessError: command: ('/opt/homebrew/bin/docker', 'system', 'info', '--format', '{{ json . }}')
stderr: Cannot connect to the Docker daemon at unix:///...docker.sock. Is the docker daemon running?
```

**Options to fix:**
1. Switch hook from `hadolint-docker` to native `hadolint` (requires adding `hadolint` to `requirements.yaml` as an optional dep, e.g. `brew install hadolint`)
2. Make the hook work with Podman by setting `DOCKER_HOST` to the Podman socket
3. Mark the hook as non-blocking locally and rely on CI for Containerfile linting

This is currently blocking commits for #130 (tmux installation) on any machine without Docker Desktop running.

