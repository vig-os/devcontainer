## Description

Fully automate and standardize the repository setup for the devcontainer template. This PR delivers the complete infrastructure for commit message validation, branch naming enforcement, automated release cycles, CI/CD pipelines, security hardening, and code coverage — establishing a reproducible, audit-ready starting point for all projects.

## Related Issue(s)

Closes #37

Related to #36, #38, #48, #50, #52

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [x] Documentation update
- [x] Refactoring (no functional changes)
- [x] Test updates

## Changes Made

### Commit Message Standardization (#36)

- Conventional Commits format (`type(scope)!: subject`) with mandatory `Refs: #<issue>` line
- `docs/COMMIT_MESSAGE_STANDARD.md` defining format, approved types, and traceability requirements
- `scripts/validate_commit_msg.py` validation script with `.githooks/commit-msg` hook
- Pre-commit integration, `.gitmessage` template, and Cursor rules/commands
- `chore` commits may omit `Refs:` when no issue is directly related
- Full workspace template included in `assets/workspace/`

### Branch Naming Enforcement (#38)

- Pre-commit hook enforcing `<type>/<issue>-<summary>` naming convention
- Cursor rules (`.cursor/rules/branch-naming.mdc`) for branch naming workflow and `gh issue develop` integration
- Integration tests for valid and invalid branch names

### Automated Release Cycle (#48)

- `prepare-release` and `finalize-release` justfile commands triggering GitHub Actions workflows
- `prepare-changelog.py` with prepare, validate, reset, and finalize commands
- `prepare-release.yml` workflow: validates semantic version, creates release branch, prepares CHANGELOG
- Unified `release.yml` pipeline: validate → finalize → build/test → publish → rollback
- `post-release.yml` workflow for post-merge cleanup
- Comprehensive `docs/RELEASE_CYCLE.md` documentation

### CI/CD Infrastructure (#48)

- `ci.yml` workflow replacing `test.yml` with streamlined project checks
- Reusable composite actions: `setup-env`, `build-image`, `test-image`, `test-integration`, `test-project`
- Artifact transfer between jobs for consistent image testing
- Retry logic across all CI operations for transient failure handling
- Consolidated test files by domain (6 → 4 files)
- Replaced `setup-python-uv` with flexible `setup-env` composite action

### Security Hardening (#50)

- Containerfile hardened with digest-pinned base image and SHA256 checksum verification for all binaries
- Minisign signature verification for cargo-binstall
- GitHub Actions and Docker actions pinned to commit SHAs across all workflows
- Pre-commit hook repos pinned to commit SHAs
- `scripts/check_action_pins.py` enforcement script with pre-commit hook and CI check
- Workflow permissions hardened with least-privilege principle
- Input sanitization: inline expression interpolation replaced with env variables
- `SECURITY.md` with vulnerability reporting procedures
- `CODEOWNERS` for automated review assignment
- `dependabot.yml` for automated dependency update PRs
- OpenSSF Scorecard (`scorecard.yml`) and CodeQL analysis (`codeql.yml`) workflows
- Vulnerability scanning and dependency review in CI pipeline
- SBOM generation, container signing (cosign), and provenance attestation in release workflow

### Code Coverage (#52)

- Coverage measurement integrated into test-project action
- Coverage threshold raised to 50%
- Expanded unit tests for `utils.py`, `validate_commit_msg.py`, and `prepare_changelog.py`

### Additional Improvements

- Virtual environment prompt renamed from "template-project" to project short name (#34)
- `--org` flag for install script (#33)
- `nano`, `just-lsp`, `pip-licenses` added to devcontainer image
- Merged `prepare-build.sh` into `build.sh`
- Removed deprecated `sync-prs-issues.sh` script
- Bumped `actions/create-github-app-token` to v2, pinned `@devcontainers/cli` to 0.81.1
- Improved sync-issues workflow robustness (pinned runner, target branch validation)
- Fixed action outputs to set conditionally based on step outcome

## Testing

- [x] Tests pass locally (`just test`)

## Checklist

- [x] My code follows the project's style guidelines
- [x] I have performed a self-review of my code
- [x] I have commented my code, particularly in hard-to-understand areas
- [x] I have updated the documentation accordingly (README.md, CONTRIBUTE.md, etc.)
- [x] I have updated the CHANGELOG.md in the `[Unreleased]` section
- [x] My changes generate no new warnings or errors
- [x] I have added tests that prove my fix is effective or that my feature works
- [x] New and existing unit tests pass locally with my changes
- [x] Any dependent changes have been merged and published

## Additional Notes

This is a large feature branch (70 files changed, ~10,300 insertions, ~1,800 deletions) that consolidates work from multiple sub-issues (#36, #38, #48, #50, #52) into the umbrella issue #37. The branch includes all infrastructure needed to make the devcontainer template self-enforcing and audit-ready from day one, targeting medical-device compliance (IEC 62304 / ISO 13485).

### Key files added/changed

| Area | Key files |
|------|-----------|
| Commit standard | `docs/COMMIT_MESSAGE_STANDARD.md`, `scripts/validate_commit_msg.py`, `.githooks/commit-msg` |
| Branch enforcement | `.cursor/rules/branch-naming.mdc`, `.pre-commit-config.yaml` |
| Release cycle | `docs/RELEASE_CYCLE.md`, `scripts/prepare-changelog.py`, `.github/workflows/release.yml`, `prepare-release.yml`, `post-release.yml` |
| CI/CD | `.github/workflows/ci.yml`, `.github/actions/{setup-env,build-image,test-image,test-integration,test-project}/action.yml` |
| Security | `SECURITY.md`, `.github/CODEOWNERS`, `.github/dependabot.yml`, `scripts/check_action_pins.py`, `.github/workflows/{codeql,scorecard}.yml` |
| Tests | `tests/test_validate_commit_msg.py`, `tests/test_check_action_pins.py`, `tests/test_prepare_changelog.py`, `tests/test_utils.py`, `tests/test_integration.py` |
