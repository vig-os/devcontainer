---
type: issue
state: open
created: 2026-03-26T18:39:18Z
updated: 2026-03-26T18:39:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/456
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-27T04:38:57.946Z
---

# [Issue 456]: [[FEATURE] Split final release into publish and promote phases](https://github.com/vig-os/devcontainer/issues/456)

### Description

Split the current single `release.yml` final-release flow into two separate workflows: a **publish** phase that builds and pushes versioned artifacts, and a **promote** phase that makes them the official "latest" after manual verification.

### Problem Statement

The current `release.yml` performs all final-release actions in a single workflow run: finalize CHANGELOG, build images, push `X.Y.Z` and `latest` tags to GHCR, create a draft GitHub Release, and dispatch smoke tests. This means:

1. If a defect is discovered after publish (e.g. the TBD bug in 0.3.1, see #455), the `latest` tag already points to the broken image -- there is no inspection window.
2. The draft GitHub Release is created before anyone can verify the published artifacts actually work.
3. Merging the release branch to `main` is fully manual (PR merge) with no automation gate linking it to a successful release.

A two-phase approach provides a human checkpoint between "artifacts exist in the registry" and "artifacts are promoted to production."

### Proposed Solution

**Phase 1 -- Publish (`release.yml` with `release-kind=final`, triggered by `just finalize-release`):**

1. Validate (existing RC gate, CHANGELOG, PR, CI checks)
2. Finalize CHANGELOG (set date, regenerate docs, commit)
3. Sync issues
4. Build and test images from finalize SHA
5. Push images to GHCR as `X.Y.Z` (per-arch + multi-arch manifest, **no `latest` tag**)
6. Sign and attest (cosign, SBOM, provenance)
7. Create **draft** GitHub Release with finalized notes
8. Dispatch smoke test to downstream

**Phase 2 -- Promote (new workflow, e.g. `promote-release.yml`, triggered by `just promote-release` or manual dispatch after inspection):**

1. Validate that GHCR `X.Y.Z` images exist and are signed
2. Validate that the draft GitHub Release for `X.Y.Z` exists
3. Validate that downstream smoke-test passed (pre-release exists for the release tag)
4. Update GHCR `latest` tag to point at the `X.Y.Z` multi-arch manifest
5. Publish the draft GitHub Release (set non-draft)
6. Merge the release PR into `main` (via API merge or auto-merge enablement)

### Alternatives Considered

- **Keep single workflow with a manual approval gate (environment protection rule):** Would work but is less flexible -- you can't re-run just the promote step, and the workflow run stays "in progress" during the wait, consuming CI minutes.
- **Use a GitHub Actions `workflow_dispatch` input to toggle publish vs promote mode:** Possible but overloads the single workflow with too many conditional paths; two separate workflows are easier to reason about and independently retry.

### Impact

- Operators get a verification window between image publication and promotion to `latest`
- The `latest` GHCR tag only moves when a human has confirmed the release is good
- GitHub Release publication is decoupled from artifact creation
- Release branch merge to `main` is automated as part of the promote phase, reducing manual steps
- Backward compatible: the publish phase is a strict subset of the current flow; promote is additive

### Additional Context

Related to #455 (TBD bug in release 0.3.1), where the `latest` tag and GitHub Release were published before anyone could detect that the CHANGELOG date was never set. A two-phase release would have caught this during the inspection window.

Current architecture in `.github/workflows/release.yml` (lines 1031-1040) unconditionally updates `latest` during publish for dual-arch final releases. The promote workflow would move this logic into its own job with prerequisite checks.

### Changelog Category

Changed

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
