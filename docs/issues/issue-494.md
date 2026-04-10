---
type: issue
state: closed
created: 2026-04-07T09:47:03Z
updated: 2026-04-07T11:12:03Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/494
comments: 0
labels: bug, area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-08T04:42:43.367Z
---

# [Issue 494]: [[BUG] Release finalize corrupts README.md and CONTRIBUTE.md (just not installed)](https://github.com/vig-os/devcontainer/issues/494)

### Description

The `finalize` job in `release.yml` explicitly sets `install-just: 'false'` (line 505), but then runs `docs/generate.py` (line 521) which calls `just --list`. Without `just` installed, `get_just_help()` silently falls back to a placeholder comment, replacing ~130 lines of just recipe documentation in `README.md` and `CONTRIBUTE.md` with `<!-- Run 'just --list' to see available recipes -->`.

The corrupted docs are committed by `commit-action`, and the subsequent CI project-checks job fails because its `generate-docs` pre-commit hook (which has `just` installed) regenerates the correct content, detecting a diff.

### Steps to Reproduce

1. Run `just finalize-release 0.3.2` (or any version)
2. The `release.yml` finalize job runs `setup-env` with `install-just: 'false'`
3. `docs/generate.py` runs, `just --list` fails silently
4. `README.md` and `CONTRIBUTE.md` committed with placeholder content
5. CI project-checks runs pre-commit, `generate-docs` detects stale docs, fails

### Expected Behavior

The finalize commit should contain the correct `just --list` output in `README.md` and `CONTRIBUTE.md`, and CI project checks should pass.

### Actual Behavior

The finalize commit replaces the just recipes section with `<!-- Run 'just --list' to see available recipes -->`. CI project-checks fails because `generate-docs` pre-commit regenerates the correct content.

- Failed finalize commit: https://github.com/vig-os/devcontainer/commit/059bde7
- Failed CI run: https://github.com/vig-os/devcontainer/actions/runs/24074373544/job/70218986061

### Environment

- **Workflow:** `.github/workflows/release.yml`, finalize job
- **Runner:** ubuntu-22.04
- **Affected release:** 0.3.2

### Possible Solution

Remove `install-just: 'false'` from the finalize job's `setup-env` step (line 505 of `release.yml`), allowing `just` to be installed (the default). The `docs/generate.py` script requires `just` to correctly generate documentation.

Additionally, consider hardening `get_just_help()` in `docs/generate.py` to fail hard (exit non-zero) rather than silently falling back, so this class of error is caught immediately instead of producing corrupted output.

### Changelog Category

Fixed

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
