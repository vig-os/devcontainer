---
type: issue
state: open
created: 2026-02-17T16:12:48Z
updated: 2026-02-17T16:12:48Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/55
comments: 0
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-17T16:13:04.490Z
---

# [Issue 55]: [Register release workflows on default branch (main)](https://github.com/vig-os/devcontainer/issues/55)

## Register release workflows on default branch (main)

### Problem

GitHub only indexes `workflow_dispatch` workflows that exist on the **default branch** (`main`).
The release workflows developed on `dev` are invisible to the Actions tab because `main` has never
seen them. Neither `gh workflow run`, the GitHub REST API, nor the Actions UI can discover or
trigger these workflows.

**Current state on `main`:** only `publish-container-image.yml` and `sync-issues.yml` exist.

**On `dev` (not registered by GitHub):**

- `prepare-release.yml` (workflow_dispatch) -- creates release branch and draft PR
- `release.yml` (workflow_dispatch) -- builds, tests, tags, and publishes a release
- `post-release.yml` (pull_request closed) -- post-release housekeeping (changelog reset, back-merge)

These workflows depend on composite actions that also only exist on `dev`:

- `.github/actions/setup-env/`
- `.github/actions/build-image/`
- `.github/actions/test-image/`
- `.github/actions/test-integration/`

### Proposed Solution

Create a focused branch from `main` that copies **only** the release-related workflows and their
required composite actions from `dev`. Open a PR to `main` so the changes can be reviewed.

Once merged, GitHub will register the `workflow_dispatch` workflows and they will appear in the
Actions tab. The workflows can then be triggered with `--ref dev` (or any branch that has the
full runtime dependencies) until `dev` is fully merged into `main`.

#### Scope

**Files to add (from `dev`):**

- `.github/workflows/prepare-release.yml`
- `.github/workflows/release.yml`
- `.github/workflows/post-release.yml`
- `.github/actions/setup-env/action.yml`
- `.github/actions/build-image/action.yml`
- `.github/actions/test-image/action.yml`
- `.github/actions/test-integration/action.yml`

**Excluded** (will arrive with the full `dev` merge later):

- `ci.yml`, `codeql.yml`, `scorecard.yml`, `security-scan.yml`
- `.github/actions/test-project/`

**No files removed** -- `publish-container-image.yml` remains until the full `dev` merge.

#### Limitations

Workflows that depend on runtime files not yet on `main` (e.g., `uv run prepare-changelog`,
`pyproject.toml`) will be registered but will only fully execute when triggered against a ref
that contains those files (e.g., `--ref dev`).

### Acceptance Criteria

- [ ] `prepare-release.yml` and `release.yml` appear in the GitHub Actions tab
- [ ] `gh workflow run prepare-release.yml --ref dev -f version=X.Y.Z -f dry-run=true` succeeds
- [ ] No existing workflows on `main` are broken

