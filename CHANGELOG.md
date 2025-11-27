# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses a simplified versioning scheme (X.Y format, e.g., 1.0, 1.1, 2.0).

## Unreleased

### Added

#### Core Image
- Development container image based on Python 3.12 (Debian Trixie)
- Multi-architecture support (AMD64, ARM64)
- System tools: git, gh (GitHub CLI), curl, openssh-client, ca-certificates
- Python tools: uv (fast package manager), pre-commit, ruff
- Pre-configured development environment with minimal overhead

#### Devcontainer Integration
- VS Code devcontainer template with init-workspace script
- Docker Compose orchestration for flexible container management
- Support for mounting additional folders via docker-compose.override.yml
- Post-attach automation for seamless development setup
- Automatic Git configuration synchronization from host machine
- SSH commit signing support with signature verification
- Focused `.devcontainer/README.md` with version tracking, lifecycle documentation, and workspace configuration guide
- User-specific `workspace.code-workspace.example` for multi-root VS Code workspaces (actual file is gitignored)

#### Testing Infrastructure
- Three-tiered test suite: image tests, integration tests, and registry tests
- Automated testing with pytest and testinfra
- Registry tests with optimized minimal Containerfile (10-20s builds)
- Session-scoped fixtures for efficient test execution
- Comprehensive validation of push/pull/clean workflows
- Tests verify devcontainer README version in pushed images
- Helper function tests for README update utilities

#### Automation & Tooling
- Makefile with build, test, push, pull, and clean targets
- Automated version management and git tagging
- Automatic README.md updates with version and image size during releases
- Push script with multi-architecture builds and registry validation
- Setup script for development environment initialization
- `update_readme.py` helper script for patching README metadata (version, size, development reset)
- Automatic devcontainer README version updates during releases

#### Documentation & Templates
- GitHub issue templates (bug report, feature request, task)
- Pull request template with comprehensive checklist
- Complete project documentation (README.md, CONTRIBUTE.md, TESTING.md)
- Detailed testing strategy and workflow documentation
- Push script now updates README files in build folder instead of source files (keeps source clean)
- Simplified push parameters: single `REGISTRY_TEST=1` flag replaces `NO_TEST` and `NATIVE_ARCH_ONLY` flags
- Workspace configuration (`workspace.code-workspace`) is now user-specific (gitignored, users copy from example)
- Registry test mode now skips full test suite (minimal test image doesn't need comprehensive tests)
- Push script commit logic handles cases where README.md already has the target version

### Changed

### Deprecated

### Removed

### Fixed

### Security
