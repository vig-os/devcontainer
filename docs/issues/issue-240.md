---
type: issue
state: closed
created: 2026-03-09T08:26:09Z
updated: 2026-03-09T09:03:50Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/240
comments: 3
labels: chore, area:ci, area:image
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-10T04:14:46.188Z
---

# [Issue 240]: [[CHORE] Update base Python image and GitHub Actions dependencies](https://github.com/vig-os/devcontainer/issues/240)

### Chore Type

Dependency update

### Description

Update the base Python 3.12 image digest and all pinned GitHub Actions to their latest versions. The base image in `Containerfile` is pinned to `sha256:593bd0...` while the latest `python:3.12-slim-bookworm` is `sha256:4c5037...`. GitHub Actions across workflows and composite actions are also likely behind their latest releases.

### Acceptance Criteria

- [ ] Update `Containerfile` base image digest to latest `python:3.12-slim-bookworm`
- [ ] Update all GitHub Actions to latest digest-pinned versions across:
  - `.github/workflows/` (ci, release, prepare-release, scorecard, codeql, pr-title-check, sync-issues, sync-main-to-dev, security-scan)
  - `.github/actions/` (build-image, setup-env, test-image, test-integration, test-project)
- [ ] Update pinned tool versions where applicable (e.g. `trivy version: 'v0.69.2'`, `safety==3.7.0`)
- [ ] All CI checks pass after updates
- [ ] No regressions in `just build && just test`

### Implementation Notes

**Base image (`Containerfile`):**
- `python:3.12-slim-bookworm` — update SHA256 digest pin (line 4)

**GitHub Actions (unique actions to update):**
| Action | Current tag | Files |
|---|---|---|
| `actions/checkout` | v4 | 15+ locations |
| `actions/upload-artifact` | v4 | 6 locations |
| `actions/download-artifact` | v4 | 4 locations |
| `actions/cache` | v4 | setup-env, test-project |
| `actions/create-github-app-token` | v2 | sync-issues, prepare-release, release, sync-main-to-dev |
| `actions/setup-python` | v6 | setup-env |
| `actions/setup-node` | v4 | setup-env |
| `actions/dependency-review-action` | v4 | ci |
| `actions/attest-build-provenance` | v3 | release |
| `actions/attest-sbom` | v3 | release |
| `actions/github-script` | v7 | release |
| `aquasecurity/trivy-action` | v0.33.1 | ci, security-scan, release |
| `github/codeql-action` | v4 | ci, scorecard, security-scan, codeql |
| `ossf/scorecard-action` | v2.4.3 | scorecard |
| `astral-sh/setup-uv` | v7 | setup-env |
| `taiki-e/install-action` | (just) | setup-env |
| `bats-core/bats-action` | v4.0.0 | setup-env |
| `docker/setup-buildx-action` | v3.12.0 | build-image |
| `docker/metadata-action` | v5.10.0 | build-image |
| `docker/build-push-action` | v6.18.0 | build-image |
| `docker/login-action` | v3 | release |
| `sigstore/cosign-installer` | v4 | release |
| `anchore/sbom-action` | v0.22.2 | release |

**Other pinned versions:**
- `safety==3.7.0` (ci.yml line 196)
- `trivy version: 'v0.69.2'` (ci.yml, security-scan.yml)

Note: `vig-os/sync-issues-action` and `vig-os/commit-action` are internal — update if new releases exist.

### Related Issues

_None_

### Priority

Medium

### Changelog Category

Changed

### Additional Context

Dependabot handles Docker digest updates but not GitHub Actions. Consider enabling Dependabot for the `github-actions` ecosystem if not already configured.
---

# [Comment #1]() by [c-vigo]()

_Posted on March 9, 2026 at 08:34 AM_

## Design

**Scope:** Dependency bump chore. No architectural changes.

### 1. Base image (Containerfile line 4)

- **Current:** `python:3.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c`
- **Action:** Resolve latest `python:3.12-slim-bookworm` digest from Docker Hub (or `docker manifest inspect`) and replace the FROM line.
- **Rationale:** Issue reports latest digest is `sha256:4c5037...` — verify and pin.

### 2. GitHub Actions

- **Scope:** All `uses:` references in `.github/workflows/` and `.github/actions/`
- **Strategy:** For each action, resolve the latest release tag, fetch its digest from the action's `action.yml` or GitHub API, and pin `@<sha256>` (with `# vX.Y.Z` comment for traceability).
- **Key actions:** checkout, setup-python, setup-uv, setup-node, docker/*, aquasecurity/trivy-action, ossf/scorecard-action, github/codeql-action, vig-os/*, etc.
- **Composite actions:** `./.github/actions/*` remain path references; update only the external actions they use.

### 3. Pinned tool versions in workflows

- **safety:** `ci.yml` line 196 — bump from `3.7.0` to latest (check PyPI).
- **trivy version:** `security-scan.yml`, `ci.yml` — `version: 'v0.69.2'` passed to trivy-action; bump to latest trivy CLI release.
- **hadolint:** Optional — `Containerfile` uses fixed `v2.14.0`; only update if desired for consistency (lower priority).

### 4. Verification

- Run `just build && just test` locally.
- Push and ensure all CI jobs pass.
- No changes to application logic — only digests and versions.


---

# [Comment #2]() by [c-vigo]()

_Posted on March 9, 2026 at 08:35 AM_

## Implementation Plan

Issue: #240
Branch: feature/240-update-python-image-actions-deps

### Tasks

- [x] Task 1: Update Containerfile base image digest to latest python:3.12-slim-bookworm (`sha256:4c50375fc4b8ea5ca06ac9485186ccb50171c99390b0e9300c2bac871cc2dc3e`) — `Containerfile` — verify: `just build`
- [x] Task 2: Update trivy version from v0.69.2 to v0.69.3 in ci.yml and security-scan.yml — `.github/workflows/ci.yml`, `.github/workflows/security-scan.yml` — verify: `grep "v0.69.3" .github/workflows/*.yml`
- [x] Task 3: Update all GitHub Actions in .github/actions/setup-env to latest digest-pinned versions — `.github/actions/setup-env/action.yml` — verify: `yamllint .github/actions/setup-env/action.yml 2>/dev/null || true`
- [x] Task 4: Update all GitHub Actions in .github/actions/build-image to latest digest-pinned versions — `.github/actions/build-image/action.yml` — verify: `yamllint .github/actions/build-image/action.yml 2>/dev/null || true`
- [x] Task 5: Update all GitHub Actions in .github/actions/test-image, test-integration, test-project — `.github/actions/test-image/action.yml`, `.github/actions/test-integration/action.yml`, `.github/actions/test-project/action.yml` — verify: `yamllint .github/actions/*/action.yml 2>/dev/null || true`
- [x] Task 6: Update all GitHub Actions in .github/workflows/ci.yml, release.yml, prepare-release.yml — `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/workflows/prepare-release.yml` — verify: `just ci_check` or workflow syntax valid
- [x] Task 7: Update all GitHub Actions in .github/workflows/scorecard.yml, codeql.yml, pr-title-check.yml, sync-issues.yml, sync-main-to-dev.yml, security-scan.yml — `.github/workflows/*.yml` — verify: `actionlint .github/workflows/ 2>/dev/null || true`
- [x] Task 8: Run full verification — `just build && just test` and `pre-commit run --all-files` — verify: all pass


---

# [Comment #3]() by [c-vigo]()

_Posted on March 9, 2026 at 08:53 AM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (8 tasks)
- Execute: all tasks done
- Verify: all checks pass
- PR: https://github.com/vig-os/devcontainer/pull/241
- CI: all checks pass

