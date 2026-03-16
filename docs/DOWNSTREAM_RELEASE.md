# Downstream Release Workflows

This document describes the downstream release workflow contract shipped in `assets/workspace/.github/workflows/`.

## Overview

The downstream template uses a split release architecture:

- `prepare-release.yml` (`workflow_dispatch`) prepares `release/X.Y.Z`
- `release.yml` (`workflow_dispatch`) orchestrates:
  - `release-core.yml` (`workflow_call`)
  - `release-extension.yml` (`workflow_call`, project-owned)
  - `release-publish.yml` (`workflow_call`)

All files are deployed from `assets/workspace/` by `init-workspace.sh`.

On failure, the orchestrator runs a single consolidated rollback that resets the release branch, removes any created tag, and opens a failure issue.

## Release Modes

`release.yml` supports two release modes via `release_kind`:

- `candidate` (default): computes and publishes the next `X.Y.Z-rcN` tag as a GitHub pre-release
- `final`: publishes `X.Y.Z`, finalizes `CHANGELOG.md` release date, and runs `sync-issues`

Candidate mode keeps release branch content unchanged (no CHANGELOG date finalization). Final mode performs changelog finalization before publish.

## Workflow Contract

Current contract version: `"1"`.

The following workflows require `contract_version: "1"`:

- `.github/workflows/release-core.yml`
- `.github/workflows/release-extension.yml`
- `.github/workflows/release-publish.yml`

Contract validation is performed by the shared composite action `.github/actions/validate-contract`. The expected version is defined once in that action's default input. When bumping the contract version, update the action default and the `contract_version` values in `release.yml`.

If `contract_version` does not match, the workflow fails with an actionable error.

## Input Naming Convention

All `workflow_call` inputs use underscores (e.g. `release_kind`, `dry_run`, `git_user_name`). The orchestrator `release.yml` translates its own `workflow_dispatch` hyphenated inputs at each call site.

## Extension Hook

Project-specific release behavior belongs in `.github/workflows/release-extension.yml`.

Default template behavior is no-op. Projects can customize this workflow for tasks such as:

- package publishing
- container publishing
- signing and attestations
- release artifact upload

Extension contract inputs include both `release_kind` and `publish_version`, so custom logic can branch on candidate vs final behavior.

`release.yml` requires extension success before publish, so extension failures block release publication.

## Repository Dispatch Smoke-Test Release

The workspace template now includes `.github/workflows/repository-dispatch.yml` for downstream smoke-test release handling.

### Trigger

- `repository_dispatch`
- `event_type: smoke-test-trigger`

### Payload Contract

- Required:
  - `client_payload[tag]`
- Release kind:
  - `client_payload[release_kind]` (`candidate` or `final`)
- Optional source context:
  - `client_payload[event_type]`
  - `client_payload[source_repo]`
  - `client_payload[source_workflow]`
  - `client_payload[source_run_id]`
  - `client_payload[source_run_url]`
  - `client_payload[source_sha]`
  - `client_payload[correlation_id]`

If `release_kind` is missing, the workflow infers it from `tag` (`-rcN` => `candidate`, otherwise `final`) for backward compatibility.

### Behavior

On dispatch, the downstream workflow:

1. Validates payload and resolves release kind
2. Runs smoke tests (`just test`)
3. Creates a GitHub release for the dispatched tag:
   - `candidate`: pre-release (`--prerelease`)
   - `final`: full release

This release object is consumed by upstream release gating in two ways:

- release run completion waits for downstream release creation for the dispatched tag
- upstream final publish additionally requires the latest RC pre-release to exist downstream during validation

### Example: GHCR Publishing

The following shows how a downstream project could customize `release-extension.yml` to build and push a container image to GHCR:

```yaml
name: Release Extension

on:
  workflow_call:
    inputs:
      version:
        required: true
        type: string
      finalize_sha:
        required: true
        type: string
      release_date:
        required: true
        type: string
      release_kind:
        required: true
        type: string
      publish_version:
        required: true
        type: string
      contract_version:
        required: true
        type: string

jobs:
  ghcr-publish:
    name: Publish Container Image
    runs-on: ubuntu-22.04
    permissions:
      contents: read
      packages: write
    steps:
      - name: Validate contract version
        uses: ./.github/actions/validate-contract
        with:
          contract_version: ${{ inputs.contract_version }}

      - name: Checkout finalized commit
        uses: actions/checkout@v4
        with:
          ref: ${{ inputs.finalize_sha }}

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ inputs.publish_version }}
            ${{ inputs.release_kind == 'final' && format('ghcr.io/{0}:latest', github.repository) || '' }}
```

## Upgrade Path

1. Upgrade downstream devcontainer version (which redeploys `assets/workspace` templates).
2. Keep project-owned `release-extension.yml` (preserved on force upgrades).
3. Ensure orchestrator and called workflows use the expected `contract_version`.
4. Run `prepare-release` / `release` in `--dry-run` mode to validate integration.

## Pinning and Drift

Release workflow logic is centralized in shipped local reusable workflows (`release-core.yml`, `release-publish.yml`) while extension logic remains project-owned (`release-extension.yml`).

This reduces drift in release safety checks while preserving downstream customization boundaries.
