# devcontainer Smoke Test

This repository is a smoke-test workspace for the
[vig-os/devcontainer](https://github.com/vig-os/devcontainer) project.

Its purpose is to verify that the devcontainer template and the shipped CI
workflow run successfully on real GitHub-hosted runners, not only in local or
synthetic test environments.

## Why this repo exists

The main `vig-os/devcontainer` repository publishes template files under
`assets/workspace/`, including a CI workflow
(`assets/workspace/.github/workflows/ci.yml`).

This repository provides a real target where that template can be bootstrapped
and executed end-to-end so regressions are caught early, for example:

- broken GitHub Action pins
- runner environment changes
- dependency/tooling incompatibilities (for example `uv` changes)

## Scope

This repository is intentionally minimal. It is used to:

1. bootstrap a fresh workspace from the current devcontainer template
2. run the shipped CI workflow on pull requests
3. validate that expected jobs pass in GitHub Actions
4. host CI wiring experiments such as `repository_dispatch` listeners

## Relationship to `vig-os/devcontainer`

- **Source of truth for template**: `vig-os/devcontainer`
- **Execution/verification target**: this repository

Template or workflow changes should be made in
[`vig-os/devcontainer`](https://github.com/vig-os/devcontainer), then validated
here through a normal PR run.

## Automated deploy-and-test flow

For release validation, this repository receives `repository_dispatch` events
from `vig-os/devcontainer` and runs an automated deploy-and-test cycle:

1. validate the dispatch payload and extract the tag
2. deploy that tag with the online installer
3. create branch `chore/deploy-<tag>`, commit (always), and open a PR to `dev`
4. CI workflows (`ci.yml`, `ci-container.yml`) trigger on the PR
5. enable auto-merge once checks pass

This flow applies to both RC tags and final tags.

## Audit trail and status

There is no CHANGELOG in this repository.

Deployment history is tracked through:

- deploy PRs labeled `deploy`
- merge history on `dev`
- GitHub Actions runs attached to each deploy PR

## Recreate this smoke-test repo

If this repository is lost or needs to be rebuilt, recreate it from the
`vig-os/devcontainer` image/template:

1. Create a new empty repository (for example `vig-os/devcontainer-smoke-test`).
2. Clone it locally and run the installer with smoke-test assets enabled:

   ```bash
   curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --smoke-test .
   ```

3. Commit the generated files and push to `main`.
4. Open a PR and confirm both shipped workflows pass:
   - `.github/workflows/ci.yml`
   - `.github/workflows/ci-container.yml`
5. Verify `.github/workflows/repository-dispatch.yml` exists and listens for
   `repository_dispatch` events.
