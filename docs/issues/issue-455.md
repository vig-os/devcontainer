---
type: issue
state: open
created: 2026-03-26T18:38:47Z
updated: 2026-03-26T18:38:47Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/455
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-27T04:38:58.294Z
---

# [Issue 455]: [[BUG] Release 0.3.1 CHANGELOG date not set -- TBD persisted through publish and merge](https://github.com/vig-os/devcontainer/issues/455)

### Description

The `release.yml` finalize-release workflow for 0.3.1 (`release-kind=final`) completed successfully, but the `## [0.3.1] - TBD` heading was never replaced with the actual release date. This TBD then propagated to every downstream artifact: the GHCR image, the release PR body, and the smoke-test deployment.

### Steps to Reproduce

1. `just finalize-release 0.3.1` (workflow run [#23609745942](https://github.com/vig-os/devcontainer/actions/runs/23609745942))
2. All jobs reported success (validate, finalize, build-and-test, publish, smoke-test)
3. Release PR [#342](https://github.com/vig-os/devcontainer/pull/342) was merged to main

### Expected Behavior

- `CHANGELOG.md` should contain `## [0.3.1] - 2026-03-26` on the release branch after the finalize job
- The GHCR image `ghcr.io/vig-os/devcontainer:0.3.1` should ship the finalized CHANGELOG in `/root/assets/workspace/.devcontainer/CHANGELOG.md`
- Release PR #342 body should show the finalized date
- `origin/main` should contain the finalized CHANGELOG after merge
- GitHub Release notes should include the `## [0.3.1] - 2026-03-26` header
- Downstream smoke-test PR [#112](https://github.com/vig-os/devcontainer-smoke-test/pull/112) should receive the finalized CHANGELOG

### Actual Behavior

- `podman run --rm ghcr.io/vig-os/devcontainer:0.3.1 head -8 /root/assets/workspace/.devcontainer/CHANGELOG.md` shows `## [0.3.1] - TBD`
- `origin/main` CHANGELOG.md starts with `## [0.3.1] - TBD`
- Release PR #342 body shows `## [0.3.1] - TBD` in the changelog section (header correctly reads `Release 0.3.1 - 2026-03-26`)
- GitHub Release body starts at `### Added` -- no version header at all
- Downstream smoke-test PR #112 body shows `## [0.3.1] - TBD`

### Environment

- Release workflow run: [#23609745942](https://github.com/vig-os/devcontainer/actions/runs/23609745942)
- Image: `ghcr.io/vig-os/devcontainer:0.3.1`
- Release PR: [#342](https://github.com/vig-os/devcontainer/pull/342) (merged)
- Downstream PR: [vig-os/devcontainer-smoke-test#112](https://github.com/vig-os/devcontainer-smoke-test/pull/112) (merged)
- GitHub Release: [0.3.1](https://github.com/vig-os/devcontainer/releases/tag/0.3.1) (published, non-draft)

### Additional Context

Root cause investigation areas in `.github/workflows/release.yml`:

1. **Finalize commit race**: `commit-action` (line 632) commits via API to `refs/heads/release/$VERSION`. The subsequent `git fetch + git reset --hard` (line 709) may have fetched before the API commit was visible, causing `build-and-test` to use a pre-finalize SHA.
2. **Workspace CHANGELOG sync**: `scripts/sync_manifest.py sync` (line 600) must propagate the finalized root `CHANGELOG.md` to `assets/workspace/.devcontainer/CHANGELOG.md`. If the manifest doesn't include CHANGELOG or the sync ran before `prepare-changelog finalize`, the workspace copy would retain TBD.
3. **PR body refresh**: The sed extraction (line 722) runs after `git reset --hard`, but if the reset didn't pick up the finalize commit, the CHANGELOG on disk would still have TBD.

The fact that `origin/main` still has TBD after merge strongly suggests the finalize commit either didn't land or was superseded by a concurrent commit (e.g. from `sync-issues.yml`).

### Possible Solution

- Add a post-commit verification step that fetches the finalized SHA from the API, confirms `CHANGELOG.md` contains the date, and fails the job if TBD is still present
- Ensure `build-and-test` checks out the exact SHA from the API commit response rather than relying on `git rev-parse HEAD` after a `git reset`
- Add an integration test: `grep -q "## \[$VERSION\] - [0-9]" CHANGELOG.md` after the finalize commit lands

### Changelog Category

Fixed

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
