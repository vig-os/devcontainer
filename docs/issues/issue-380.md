---
type: issue
state: closed
created: 2026-03-19T16:27:55Z
updated: 2026-03-19T22:35:09Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/380
comments: 0
labels: bug, area:ci, area:workspace, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:23.903Z
---

# [Issue 380]: [[BUG] Sparse checkout in resolve-image job excludes the local resolve-image action](https://github.com/vig-os/devcontainer/issues/380)

## Description

The `resolve-image` job in workspace workflow templates uses a sparse checkout that only fetches `.vig-os`, but the same job references the local composite action `./.github/actions/resolve-image`. Since the sparse checkout excludes `.github/actions/resolve-image/action.yml`, GitHub Actions cannot find the action definition, causing the job to fail.

This blocks all downstream smoke-test deployment PRs because the non-container `ci.yml` workflow cannot resolve the devcontainer image tag.

## Steps to Reproduce

1. Publish an RC via `just publish-candidate 0.3.1`
2. Observe the smoke-test dispatch creates PR [vig-os/devcontainer-smoke-test#40](https://github.com/vig-os/devcontainer-smoke-test/pull/40)
3. The `Resolve image tag` check fails with: `Can't find 'action.yml', 'action.yaml' or 'Dockerfile' under '.github/actions/resolve-image'`

## Expected Behavior

The `resolve-image` job should successfully resolve the container image tag and downstream CI checks should pass.

## Actual Behavior

The `Resolve image tag` job fails because the sparse checkout does not include `.github/actions/resolve-image/action.yml`. This cascades: `Lint & Format` and `Tests` are skipped, `CI Summary` fails, and the PR is blocked.

## Environment

- **Release workflow run:** [23303525517](https://github.com/vig-os/devcontainer/actions/runs/23303525517)
- **Failed downstream PR:** [vig-os/devcontainer-smoke-test#40](https://github.com/vig-os/devcontainer-smoke-test/pull/40)
- **Failed CI run:** [23304436517](https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23304436517)

## Additional Context

All 5 workspace workflow templates that have a `resolve-image` job are affected:
- `assets/workspace/.github/workflows/ci.yml`
- `assets/workspace/.github/workflows/release-core.yml`
- `assets/workspace/.github/workflows/release-publish.yml`
- `assets/workspace/.github/workflows/sync-issues.yml`
- `assets/workspace/.github/workflows/sync-main-to-dev.yml`

Related auto-created issue: #379 (rollback notification)

## Possible Solution

Add `.github/actions/resolve-image` to the `sparse-checkout` pattern in the `resolve-image` job of all 5 affected workflows:

```yaml
      - name: Checkout repository
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2
        with:
          sparse-checkout: |
            .vig-os
            .github/actions/resolve-image
          sparse-checkout-cone-mode: false
```

## Changelog Category

Fixed

---
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
