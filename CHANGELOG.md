# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- **`--org` flag for install script** ([#33](https://github.com/vig-os/devcontainer/issues/33))
  - Allows overriding the default organization name (default: `vigOS`)
  - Passes `ORG_NAME` as environment variable to the container
  - Usage: `curl -sSf ... | bash -s --org MyOrg -- ~/my-project`
  - Unit tests for `--org` flag in help, default value, and custom override
- **nano text editor** in devcontainer image ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **just-lsp** language server and VS Code extension for Just files ([#44](https://github.com/vig-os/devcontainer/issues/37))
- **pip-licenses** installed system-wide with version verification test ([#43](https://github.com/vig-os/devcontainer/issues/37))
- **Commit message standardization** ([#36](https://github.com/vig-os/devcontainer/issues/36))
  - Commit message format: `type(scope)!: subject` with mandatory `Refs: #<issue>` line
  - Documentation: `docs/COMMIT_MESSAGE_STANDARD.md` defining format, approved types (feat, fix, docs, chore, refactor, test, ci, build, revert, style), and traceability requirements
  - Validation script: `scripts/validate_commit_msg.py` enforcing the standard
  - Commit-msg hook: `.githooks/commit-msg` runs validation on every commit
  - Pre-commit integration: commit-msg stage hook in `.pre-commit-config.yaml`
  - Git commit template: `.gitmessage` with format placeholder
  - Cursor integration: `.cursor/rules/commit-messages.mdc` and `.cursor/commands/commit-msg.md` for AI-assisted commit messages
  - Workspace template: all commit message tooling included in `assets/workspace/` for new projects
  - Tests: `tests/test_validate_commit_msg.py` with comprehensive validation test cases
- **Chore Refs exemption** in commit message standard ([#37](https://github.com/vig-os/devcontainer/issues/37))
  - `chore` commits may omit the `Refs:` line when no issue or PR is directly related
  - Validator updated with `REFS_OPTIONAL_TYPES` to accept chore commits without Refs
  - Comprehensive test suite (`TestChoreRefsExemption`) covering all exemption scenarios
- **Branch name enforcement as a pre-commit hook** ([#38](https://github.com/vig-os/devcontainer/issues/38))
  - New `branch-name` hook enforcing `<type>/<issue>-<summary>` convention (e.g. `feature/38-standardize-branching-strategy-enforcement`)
  - Pre-commit configuration updated in repo and in workspace assets (`.pre-commit-config.yaml`, `assets/workspace/.pre-commit-config.yaml`)
  - Integration tests added for valid and invalid branch names
- **Cursor rules for branch naming and issue workflow** ([#38](https://github.com/vig-os/devcontainer/issues/38))
  - `.cursor/rules/branch-naming.mdc`: topic branch naming format, branch types, workflow for creating/linking branches via `gh issue develop`
  - Guidelines for inferring branch type from issue labels and deriving short summary from issue title
- **Virtual environment prompt renaming** ([#34](https://github.com/vig-os/devcontainer/issues/34))
  - Post-create script updates venv prompt from "template-project" to project short name
  - Integration test verifies venv activate script does not contain "template-project"
- **Automated release cycle** ([#48](https://github.com/vig-os/devcontainer/issues/48))
  - `prepare-release` and `finalize-release` justfile commands triggering GitHub Actions workflows
  - `prepare-changelog.py` script with prepare, validate, reset, and finalize commands for CHANGELOG automation
  - `reset-changelog` justfile command for post-merge CHANGELOG cleanup
  - `prepare-release.yml` GitHub Actions workflow: validates semantic version, creates release branch, prepares CHANGELOG
  - Unified `release.yml` pipeline: validate → finalize → build/test → publish → rollback
  - Comprehensive test suite in `tests/test_release_cycle.py`
- **CI testing infrastructure** ([#48](https://github.com/vig-os/devcontainer/issues/48))
  - `ci.yml` workflow replacing `test.yml` with streamlined project checks (lint, changelog validation, utility and release-cycle tests)
  - Reusable composite actions: `setup-env`, `build-image`, `test-image`, `test-integration`, `test-project`
  - Artifact transfer between jobs for consistent image testing
  - Retry logic across all CI operations for transient failure handling
- **Release cycle documentation** ([#38](https://github.com/vig-os/devcontainer/issues/38), [#48](https://github.com/vig-os/devcontainer/issues/48))
  - `docs/RELEASE_CYCLE.md` with complete release workflow, branching strategy, and CI/CD integration
  - Cursor commands: `after-pr-merge.md`, `submit-pr.md`
- **GitHub Actions SHA pinning enforcement** ([#50](https://github.com/vig-os/devcontainer/issues/50))
  - `scripts/check_action_pins.py` pre-commit hook and CI check ensuring all GitHub Actions and Docker actions reference commit SHAs
  - Comprehensive test suite in `tests/test_check_action_pins.py`
- **CODEOWNERS** for automated review assignment ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **SECURITY.md** with vulnerability reporting procedures and supported version policy ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **OpenSSF Scorecard workflow** (`scorecard.yml`) for supply chain security scoring ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **CodeQL analysis workflow** (`codeql.yml`) for automated static security analysis ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Dependabot configuration** for automated dependency update PRs ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Vulnerability scanning and dependency review** in CI pipeline ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **SBOM generation, container signing, and provenance attestation** in release workflow ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Edge case tests** for changelog validation, action SHA pinning, and install script ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Code coverage reporting in CI** ([#52](https://github.com/vig-os/devcontainer/issues/52))
  - Code coverage measurement integrated into test action workflow
  - Coverage threshold raised to 50% for unit tests
  - Expanded unit tests to improve overall test coverage

### Changed

- **Commit message guidelines** - updated documentation ([#36](https://github.com/vig-os/devcontainer/issues/37))
- **Expected version checks** - updated ruff and pre-commit versions in test suite ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Updated pre-commit hook configuration in the devcontainer** ([#38](https://github.com/vig-os/devcontainer/issues/38))
  - Exclude issue and template docs from .github_data
  - Autofix shellcheck
  - Autofix pymarkdown
  - Add license compliance check
- **Renamed `publish-container-image.yml` to `release.yml`** and expanded into unified release pipeline ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Merged `prepare-build.sh` into `build.sh`** — consolidated directory preparation, asset copying, placeholder replacement, and README updates into a single entry point ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Consolidated test files by domain** — reorganized from 6 files to 4 (`test_image.py`, `test_integration.py`, `test_utils.py`, `test_release_cycle.py`) ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Replaced `setup-python-uv` with flexible `setup-env` composite action** supporting optional inputs for podman, Node.js, and devcontainer CLI ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Reduced `sync-issues` workflow triggers** — removed `edited` event type from issues and pull_request triggers ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Release workflow pushes tested images** instead of rebuilding after tests pass ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Updated CONTRIBUTE.md** release workflow documentation to match automated process ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Bumped `actions/create-github-app-token`** from v1 to v2 across workflows with updated SHA pins ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Pinned `@devcontainers/cli`** to version 0.81.1 in CI for consistent behavior ([#37](https://github.com/vig-os/devcontainer/issues/37))

### Deprecated

### Removed

- **`scripts/prepare-build.sh`** — merged into `build.sh` ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **`scripts/sync-prs-issues.sh`** — deprecated sync script ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **`test.yml` workflow** — replaced by `ci.yml` ([#48](https://github.com/vig-os/devcontainer/issues/48))

### Fixed

- **Non-ASCII characters in justfiles** - Replaced Unicode box-drawing characters (═, ───) and emojis with ASCII equivalents for just-lsp compatibility ([#49](https://github.com/vig-os/devcontainer/issues/49))
- **`just precommit` recipe** - Run pre-commit through `uv run` to ensure it uses the virtual environment ([#46](https://github.com/vig-os/devcontainer/issues/46))
- **Pytest test collection** - Exclude `tests/tmp/` directory (integration test workspaces) from test discovery to prevent import errors
- **Hardened release workflows** — CI status check validation, eliminated double-push with PR creation as last step ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **PR and CI checks enforced as hard gates** (exit 1) in finalize-release workflow instead of soft warnings ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Sidecar tests in CI** — run via host podman to avoid API version mismatch between host (3.4.4) and container client (4.0.0) ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **CI environment setup** — podman socket handling, base image tagging, docker-compose wrapper for devcontainer CLI compatibility ([#48](https://github.com/vig-os/devcontainer/issues/48))
- **Pre-commit exclusion pattern** for pymarkdown updated to correct regex ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Action outputs set conditionally** based on step outcome in composite actions — tar-file output only set when `output-type=tar`, test-result reflects actual test pass/fail ([#37](https://github.com/vig-os/devcontainer/issues/37))
- **Sync-issues workflow robustness** — pinned runner to ubuntu-22.04, added target branch validation for `workflow_dispatch`, removed overly broad cache restore-key pattern ([#37](https://github.com/vig-os/devcontainer/issues/37))

### Security

- **Digest-pinned base image** and SHA256 checksum verification for all downloaded binaries in Containerfile ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Minisign signature verification** for cargo-binstall downloads ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **GitHub Actions and Docker actions pinned to commit SHAs** across all workflows ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Pre-commit hook repos pinned to commit SHAs** ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Workflow permissions hardened** with least-privilege principle and explicit token scoping ([#50](https://github.com/vig-os/devcontainer/issues/50))
- **Input sanitization** — inline expression interpolation replaced with environment variables in workflow run blocks to prevent injection ([#50](https://github.com/vig-os/devcontainer/issues/50))

## [0.2.1](https://github.com/vig-os/devcontainer/releases/tag/v0.2.1) - 2026-01-28

### Added

- **Manual target branch specification** for sync-issues workflow
  - Added `target-branch` input to `workflow_dispatch` trigger for manually specifying commit target branch
  - Allows explicit branch selection when triggering workflow manually (e.g., `main`, `dev`)
- **cargo-binstall** in Containerfile
  - Install via official install script; binaries in `/root/.cargo/bin` with `ENV PATH` set
  - Version check in `tests/test_image.py`
- **typstyle** linting
  - Install via `cargo-binstall` in Containerfile
  - Version check in test suite
  - Pre-commit hook configuration for typstyle
- **Just command runner** installation and version verification
  - Added installation of the latest version of `just` (1.46.0) in the Containerfile
  - Added tests to verify `just` installation and version in `test_image.py`
  - Added integration tests for `just` recipes (`test_just_default`, `test_just_help`, `test_just_info`, `test_just_pytest`)
- **GitHub Actions workflow for multi-architecture container image publishing** (`.github/workflows/release.yml`)
  - Automated build and publish workflow triggered on semantic version tags (vX.Y.Z)
  - Multi-architecture support (amd64, arm64) with parallel builds on native runners
  - Image testing before push: runs `pytest tests/test_image.py` against built images
  - Manual dispatch support for testing workflow changes without pushing images (default version: 99.0.1)
  - Optional manual publishing: `workflow_dispatch` can publish images/manifests when `publish=true` (default false)
  - Architecture validation and dynamic selection: users can specify single or multiple architectures (amd64, arm64) with validation
  - Comprehensive error handling and verification steps
  - OCI-standard labels via `docker/metadata-action`
  - Build log artifacts for debugging (always uploaded for manual dispatch and on failure)
  - Multi-architecture manifest creation for automatic platform selection
  - Centralized version extraction job for reuse across build and manifest jobs
  - Concurrency control to prevent duplicate builds
  - Timeout protection (60 minutes for builds, 10 minutes for manifest)
- **GitHub Actions workflow for syncing issues and PRs** (`.github/workflows/sync-issues.yml`)
  - Automated sync of GitHub issues and PRs to markdown files in `.github_data/`
  - Runs on schedule (daily), manual trigger, issue events, and PR events
  - Smart branch selection: commits to `main` when PRs are merged into `main`, otherwise commits to `dev`
  - Cache-based state management to track last sync timestamp
  - Force update option for manual workflow dispatch
- **Enhanced test suite**
  - Added utility function tests (`tests/test_utils.py`) for `sed_inplace` and `update_version_line`
  - Improved test organization in justfile with grouped test commands (`just test-all`, `just test-image`, `just test-utils`)
- **Documentation improvements**
  - Added workflow status badge to README template showing publish workflow status
  - Simplified contribution guidelines by removing QEMU build instructions

### Changed

- **Sync-issues workflow branch protection bypass**
  - Added GitHub App token generation step using `actions/create-github-app-token@v2`
  - Updated commit-action to use GitHub App token for bypassing branch protection rules
  - Updated `vig-os/commit-action` from `v0.1.1` to `v0.1.3`
  - Changed commit-action environment variable from `GITHUB_TOKEN`/`GITHUB_REF` to `GH_TOKEN`/`TARGET_BRANCH` to match action's expected interface
- **Devcontainer test fixtures** (`tests/conftest.py`)
  - Shared helpers for `devcontainer_up` and `devcontainer_with_sidecar`: path resolution, env/SSH, project yaml mount, run up, teardown
  - `devcontainer_with_sidecar` scope set to session (one bring-up per session for sidecar tests)
  - Cleanup uses same approach as `just clean-test-containers` (list containers by name, `podman rm -f`) so stacks are torn down reliably
  - Redundant imports removed; fixture logic simplified for maintainability
- **Build process refactoring**
  - Separated build preparation into dedicated `prepare-build.sh` script
  - Handles template replacement, asset copying, and README version updates
  - Improved build script with `--no-cache` flag support and better error handling
- **Development workflow streamlining**
  - Simplified contribution guidelines: removed QEMU build instructions and registry testing complexity
  - Consolidated test commands in justfile for better clarity
  - Updated development setup instructions to reflect simplified workflow
- **Package versions**
  - Updated `ruff` from 0.14.10 to 0.14.11 in test expectations

### Removed

- **Deprecated justfile test recipe and test**
  - Removed deprecated test command from justfile
  - Removed deprecated test for default recipe in justfile (`TestJustIntegration.test_default_recipe_includes_check`)
- **Registry testing infrastructure** (moved to GitHub Actions workflow)
  - Removed `scripts/push.sh` (455 lines) - functionality now in GitHub Actions workflow
  - Removed `tests/test_registry.py` (788 lines) - registry tests now in CI/CD pipeline
  - Removed `scripts/update_readme.py` (80 lines) - README updates handled by workflow
  - Removed `scripts/utils.sh` (75 lines) - utilities consolidated into other scripts
  - Removed `just test-registry` command - no longer needed with automated workflow

### Fixed

- **Multi-platform container builds** in Containerfile
  - Removed default value from `TARGETARCH` ARG to allow Docker BuildKit's automatic platform detection
  - Fixes "Exec format error" when building for different architectures (amd64, arm64)
  - Ensures correct architecture-specific binaries are downloaded during build
- **Image tagging after podman load** in publish workflow
  - Explicitly tag loaded images with expected name format (`ghcr.io/vig-os/devcontainer:VERSION-ARCH`)
  - Fixes test failures where tests couldn't find the image after loading from tar file
  - Ensures proper image availability for testing before publishing
- **GHCR publish workflow push permissions**
  - Authenticate to `ghcr.io` with the repository owner and token context, and set explicit job-level `packages: write` permissions to prevent `403 Forbidden` errors when pushing layers.
- **Sync-issues workflow branch determination logic**
  - Fixed branch selection to prioritize manual `target-branch` input when provided via `workflow_dispatch`
  - Improved branch detection: manual input → PR merge detection → default to `dev`
- **Justfile default recipe conflict**
  - Fixed multiple default recipes issue by moving `help` command to the main justfile
  - Removed default command from `justfile.project` and `justfile.base` to prevent conflicts
  - Updated just recipe tests to handle variable whitespace in command output formatting
- **Invalid docker-compose.project.yaml**
  - Added empty services section to docker-compose.project.yaml to fix YAML validation
- **Python import resolution in tests**
  - Fixed import errors in `tests/test_utils.py` by using `importlib.util` for explicit module loading
  - Improved compatibility with static analysis tools and linters
- **Build script improvements**
  - Fixed shellcheck warnings by properly quoting script paths
  - Improved debug output and error messages

## [0.2.0](https://github.com/vig-os/devcontainer/releases/tag/v0.2.0) - 2026-01-06

### Added

- **Automatic version check** for devcontainer updates with DRY & SOLID design
  - Checks GitHub API for new releases and notifies users when updates are available
  - Silent mode with graceful failure (no disruption to workflow)
  - Configurable check interval (default: 24 hours) with spam prevention
  - Mute notifications for specified duration (`just check 7d`, `1w`, `12h`, etc.)
  - Enable/disable toggle (`just check on|off`)
  - One-command update: `just update` downloads install script and updates template files
  - Configuration stored in `.devcontainer/.local/` (gitignored, machine-specific)
  - Auto-runs on `just` default command (can be disabled)
  - Comprehensive test suite (`tests/test_version_check.py`) with 24 tests covering all functionality
- **One-line install script** (`install.sh`) for curl-based devcontainer deployment
  - Auto-detection of podman/docker runtime (prefers podman)
  - Auto-detection and sanitization of project name from folder name (lowercase, underscores)
  - OS-specific installation instructions when runtime is missing (macOS, Ubuntu, Fedora, Arch, Windows)
  - Runtime health check with troubleshooting advice (e.g., "podman machine start" on macOS)
  - Flags: `--force`, `--version`, `--name`, `--dry-run`, `--docker`, `--podman`, `--skip-pull`
- `--no-prompts` flag for `init-workspace.sh` enabling non-interactive/CI usage
- `SHORT_NAME` environment variable support in `init-workspace.sh`
- Test suite for install script (`tests/test_install_script.py`) with unit and integration tests
- `just` as build automation tool (replaces `make`)
- Layered justfile architecture: `justfile.base` (managed), `justfile.project` (team-shared), `justfile.local` (personal)
- Generic sidecar passthrough: `just sidecar <name> <recipe>` for executing commands in sidecar containers
- Documentation generation system (`docs/generate.py`) with Jinja2 templates
- Python project template with `pyproject.toml` and standard structure (`src/`, `tests/`, `docs/`)
- Pre-built Python virtual environment with common dev/science dependencies (numpy, scipy, pandas, matplotlib, pytest, jupyter)
- Auto-sync Python dependencies on container attach via `uv sync`
- `UV_PROJECT_ENVIRONMENT` environment variable for instant venv access without rebuild
- `pip-licenses` pre-commit hook for dependency license compliance checking (blocks GPL-3.0/AGPL-3.0)
- Pre-flight container cleanup check in test suite with helpful error messages
- `just clean-test-containers` recipe for removing lingering test containers
- `PYTEST_AUTO_CLEANUP` environment variable for automatic test container cleanup
- `docker-compose.project.yaml` for team-shared configuration (git-tracked, preserved during upgrades)
- `docker-compose.local.yaml` for personal configuration (git-ignored, preserved during upgrades)
- Build-time manifest generation for optimized placeholder replacement
- `tests/CLEANUP.md` documentation for test container management

### Changed

- `ORG_NAME` now defaults to `"vigOS/devc"` instead of requiring user input
- `init-workspace.sh` now escapes special characters in placeholder values (fixes sed errors with `/` in ORG_NAME)
- Documentation updated with curl-based install as primary quick start method
- **BREAKING**: Replaced `make` with `just` - all build commands now use `just` (e.g., `just test`, `just build`, `just push`)
- **Versioning scheme**: Switched from X.Y format to Semantic Versioning (X.Y.Z format).
All new releases use MAJOR.MINOR.PATCH format (e.g., 0.2.0).
The previous v0.1 release is kept as-is for backwards compatibility.
- **Package versions**: Bumped tool and project versions from previous release:
  - `uv` (0.9.17 → 0.9.21)
  - `gh` (2.83.1 → 2.83.2)
  - `pre-commit` (4.5.0 → 4.5.1)
  - `ruff` (0.14.8 → 0.14.10)
- VS Code Python interpreter now points to pre-built venv (`/root/assets/workspace/.venv`)
- Test container cleanup check runs once at start of `just test` instead of each test phase
- **BREAKING**: Docker Compose file hierarchy now uses `project.yaml` and `local.yaml` instead of `override.yml`
- Socket detection prioritizes Podman over Docker Desktop on macOS and Linux
- `{{TAG}}` placeholder replacement moved to container with build-time manifest generation (significantly faster initialization)
- Socket mount configuration uses environment variable with fallback: `${CONTAINER_SOCKET_PATH:-/var/run/docker.sock}`
- `initialize.sh` writes socket path to `.env` file instead of modifying YAML directly
- `init-workspace.sh` simplified: removed cross-platform `sed` handling (always runs in Linux)

### Removed

- Deprecated `version` field from all Docker Compose files
- `:Z` SELinux flag from socket mounts (incompatible with macOS socket files)
- `docker-compose.override.yml` (replaced by `project.yaml` and `local.yaml`)
- `docker-compose.sidecar.yaml` (merged into main `docker-compose.yml`)

### Fixed

- Test failures from lingering containers between test phases
(now detected and reported before test run; added `PYTEST_SKIP_CONTAINER_CHECK` environment variable)
- Improved error messages for devcontainer startup failures
- SSH commit signing: Changed `user.signingkey` from file path to email identifier to support SSH agent forwarding.
  Git now uses the SSH agent for signing by looking up the email in allowed-signers and matching with the agent key.
- Fixed `gpg.ssh.allowedSignersFile` path to use container path instead of host path after copying git configuration.
- Automatically add git user email to allowed-signers file during setup to ensure commits can be signed and verified.
- macOS Podman socket mounting errors caused by SELinux `:Z` flag on socket files
- Socket detection during tests now matches runtime behavior (Podman-first)

## [0.1](https://github.com/vig-os/devcontainer/releases/tag/v0.1) - 2025-12-10

### Core Image

- Development container image based on Python 3.12 (Debian Trixie)
- Multi-architecture support (AMD64, ARM64)
- System tools: git, gh (GitHub CLI), curl, openssh-client, ca-certificates
- Python tools: uv, pre-commit, ruff
- Pre-configured development environment with minimal overhead

### Devcontainer Integration

- VS Code devcontainer template with init-workspace script setting organization and project name
- Docker Compose orchestration for flexible container management
- Support for mounting additional folders via docker-compose.override.yml
- Container lifecycle scripts `post-create.sh`, `initialize.sh` and `post-attach.sh` for seamless development setup
- Automatic Git configuration synchronization from host machine
- SSH commit signing support with signature verification
- Focused `.devcontainer/README.md` with version tracking, lifecycle documentation, and workspace configuration guide
- User-specific `workspace.code-workspace.example` for multi-root VS Code workspaces (actual file is gitignored)

### Testing Infrastructure

- Three-tiered test suite: image tests, integration tests, and registry tests
- Automated testing with pytest and testinfra
- Registry tests with optimized minimal Containerfile (10-20s builds)
- Session-scoped fixtures for efficient test execution
- Comprehensive validation of push/pull/clean workflows
- Tests verify devcontainer README version in pushed images
- Helper function tests for README update utilities

### Automation and Tooling

- Justfile with build, test, push, pull, and clean recipes
- Automated version management and git tagging
- Automatic README.md updates with version and image size during releases
- Push script with multi-architecture builds and registry validation
- Setup script for development environment initialization
- `update_readme.py` helper script for patching README metadata (version, size, development reset)
- Automatic devcontainer README version updates during releases

### Documentation and Templates

- GitHub issue templates (bug report, feature request, task)
- Pull request template with comprehensive checklist
- Complete project documentation (README.md, CONTRIBUTE.md, TESTING.md)
- Detailed testing strategy and workflow documentation
- Push script updates README files in both project and assets
