# Container CI Notes

Behavioral notes for the workspace CI workflow (`.github/workflows/ci.yml`)
when jobs run inside `ghcr.io/vig-os/devcontainer:*` via GitHub Actions
`container:`.

## Tool bootstrap model

The workflow runs with tools already provided by the devcontainer image, then
uses downstream `just` recipes to keep CI aligned with project commands:

```yaml
- run: just sync
```

## git safe.directory

`actions/checkout` runs on the host and bind-mounts the workspace into the
container. The resulting directory is owned by a different UID than the
container's root user, which triggers git's `safe.directory` rejection.
The container workflow adds:

```yaml
- run: git config --global --add safe.directory "$GITHUB_WORKSPACE"
```

## Root user

The container runs as `root` by default. No `sudo` is required and file
permission issues are unlikely, but any git operations need the
`safe.directory` fix above.

## No Docker-in-Docker

The container job does not have access to a Docker or Podman daemon.
Jobs that require building or running containers (e.g. integration tests
using `devcontainer up`) are not supported in this workflow.

## Security scope

`bandit` can still run as a `prek` lint hook (add it to
`.pre-commit-config.yaml`; the hook runner is `prek`, not the removed
`pre-commit` binary — see docs/MIGRATION.md), but there is no separate CI
security-report job with JSON artifact uploads.

## Dependency review scope

The CI workflow does not include a dedicated `actions/dependency-review-action`
job; it focuses on validating code quality and tests inside the image.

## No coverage artifact upload

The test job runs `just test` (plain `pytest`) and does not upload
coverage artifacts.

## prek cache miss

The image ships a prek hook cache at `/opt/prek-cache` (`PREK_HOME`), built
from the template workspace's `.pre-commit-config.yaml` (which uses version
tags as revs).  This repository pins hooks by commit hash, so the cached
environments do not match and prek downloads fresh environments at
runtime.

## Public-image assumption (private / rate-limited registries)

**Limitation (tracked, not yet fixed):** the shipped container workflows assume
`ghcr.io/vig-os/devcontainer` is **publicly pullable and unauthenticated**.

- The `resolve-image` action validates the tag with an unauthenticated
  `docker manifest inspect` and swallows its stderr, so an auth or rate-limit
  failure surfaces only as the generic "Cannot access image manifest" error.
- The in-container jobs (`ci.yml`, `prepare-release.yml`, …) declare
  `container: { image: … }` with **no `credentials:` block**, so a private
  image (or an anonymous pull throttled by GHCR) fails opaquely at the job's
  container-pull step.

If you pin a **private** devkit image, add a `credentials:` block to each
container job (`username`/`password` from a registry PAT secret) yourself for
now. A first-class fix (authenticated probe + templated `credentials:`) is
tracked in [#920](https://github.com/vig-os/devcontainer/issues/920) and rides
the devkit rename cycle
([#781](https://github.com/vig-os/devcontainer/issues/781)).
