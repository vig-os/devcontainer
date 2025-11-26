# Contributing to vigOS Development Environment

This guide explains how to develop, build, test, and release the vigOS development container image.

## Requirements

| Component            | Version | Purpose |
|----------------------|---------|---------|
| **Podman**           | v4.0+   | Container runtime, compose, and linting |
| **make**             | GNU     | Build automation and management         |
| **uv**               | v0.8+   | Python package and project manager      |
| **git**              | >2.34.0 | Version control and pre-commit tools    |
| **ssh**              | Latest  | GitHub sign in and commit signing       |
| **gh**               | Latest  | GitHub CLI for repository and PR/issue management |
| **npm**              | Latest  | Node.js package manager (for DevContainer CLI) |
| **devcontainer CLI** | v0.80.1 | DevContainer CLI for testing devcontainer functionality |

> **Note:** You do **not** need to manually install `uv` or `devcontainer CLI`.
They will be installed automatically when running `./scripts/setup.sh` or `make setup`.

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install -y podman git openssh-client gh nodejs npm
```

To build images for multiple architectures (e.g., AMD64 and ARM64), install QEMU user static binaries:

```bash
sudo apt install -y qemu-user-static
sudo podman run --privileged --rm docker.io/tonistiigi/binfmt --install all
```

Verify the installation by checking that `cat /proc/sys/fs/binfmt_misc/qemu-aarch64` shows output (not an error).

**macOS (Homebrew):**

```bash
brew install podman git openssh gh node
```

- For other Linux distributions, use your package manager (e.g., `dnf`, `yum`, `zypper`, `apk`) to install these dependencies.
- `uv` and `devcontainer CLI` will be set up automatically; no need to install them manually.
- Ensure Docker is installed if you plan to use it instead of Podman.

## Setup

Clone this repository and prepare it for container development:

```bash
git clone git@github.com:vig-os/devcontainer.git
cd devcontainer
make setup
```

## Development Workflow

When contributing to this project, follow this workflow:

1. **Create an issue** to report a bug or request a feature
   - Use [GitHub Issues](https://github.com/vig-os/devcontainer/issues) to document the problem or feature request
   - This helps track work and provides context for reviewers

2. **Create a branch from `dev` branch**

   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Work on the issue or feature**
   - Make your changes
   - Commit often and descriptively
   - Add tests
   - Build and test locally: `make build && make test`
   - Ensure your code follows the project's style and conventions

4. **Update documentation if necessary**
   - Update [README.md](README.md), [CONTRIBUTE.md](CONTRIBUTE.md), or other relevant docs
   - Update the [CHANGELOG](CHANGELOG.md) with your changes in the `[Unreleased]` section
     - Add entries under appropriate categories (Added, Changed, Fixed, etc.)
     - Use clear, concise descriptions
     - Reference related [issues](https://github.com/vig-os/devcontainer/issues) and [PRs](https://github.com/vig-os/devcontainer/pulls) when applicable
   - Keep documentation in sync with code changes

5. **Verify tests pass**

   ```bash
   # Run all test suites (image, integration, registry)
   make test

   # Or run individual test suites
   make test-image
   make test-integration
   make test-registry
   ```

6. **Create a pull request**
   - Create a [pull request](https://github.com/vig-os/devcontainer/pulls) targeting the `dev` branch
   - Link the PR to the related [issue(s)](https://github.com/vig-os/devcontainer/issues)
   - Provide a clear description of your changes

7. **Accepted contributions will be merged into `dev` branch**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, your changes will be merged into `dev`

## Make Targets

- **help**: Show a list of all available make targets
- **info**: Show information about the image
- **setup**: Setup this repository for container development
- **login**: Test authentication to GitHub Container Registry
- **build**: Build local development image (`dev` tag)
- **test**: Run image and integration tests (not registry tests)
- **test-image**: Run image tests only
- **test-integration**: Run integration tests only
- **test-registry**: Run registry tests only
- **push VERSION=X.Y**: Build, test, commit, push & tag image:X.Y
- **push VERSION=X.Y NO_TEST=1**: Build, commit, push & tag image:X.Y (skip tests)
- **push VERSION=X.Y NATIVE_ARCH_ONLY=1**: Build only for native architecture
- **pull VERSION={VER}**: Pull image:{VER} (default: latest)
- **clean VERSION={VER}**: Remove image:{VER} (default: dev)

## Release Workflow

When releasing a new version of the devcontainer image, follow these steps:

1. **Update documentation**
   - Ensure [README.md](README.md), [CONTRIBUTE.md](CONTRIBUTE.md), and other docs are up to date
   - Update [CHANGELOG.md](CHANGELOG.md):
     - Move all `[Unreleased]` entries to a new version section (e.g., `[1.0]`)
     - Add the release date in YYYY-MM-DD format
     - Update the version links at the bottom of the file
     - Clear the `[Unreleased]` section for future changes
   - Verify all documentation reflects the current state

2. **Run tests**

   ```bash
   # Run all test suites to ensure everything works
   make test
   ```

3. **Ensure clean git state**

   ```bash
   # Make sure you are on the dev branch
   git checkout dev
   git pull origin dev

   # Ensure no uncommitted changes
   git status
   # All changes should be committed before releasing
   ```

4. **Release with `make push` (creates tag)**

   ```bash
   # Replace X.Y with the version number (e.g. 1.0, 1.1, 2.0)
   make push VERSION=X.Y
   ```

   - This will:
     - Build the image for the specified version
     - Run tests (unless `NO_TEST=1` is specified)
     - Push the image to GHCR with both `:latest` and `:X.Y` tags
     - Update [README.md](README.md) with the new version
     - Create a git commit with the README.md update (commit message: "Release X.Y")
     - Create a git tag `vX.Y` pointing to that commit

5. **Create pull request to merge into `main`**
   - After the release is pushed, create a [pull request](https://github.com/vig-os/devcontainer/pulls) from `dev` to `main`
   - The PR should include:
     - Summary of changes in this release
     - Reference to the version tag created
     - Any important notes for users
   - Once merged, `main` will reflect the stable release

## Version Tagging

vigOS Development Environment uses **smart version detection** to manage both GHCR tags and git tags:

- **Development versions** (`dev`):
  - Only local, without time stamp or git reference
  - Meant for development and testing only
  - Use `make build` and `make test` to build and test

- **Stable versions** (e.g., `1.2`, `2.0`):
  - Pushes to GHCR with both `:latest` and `:version` tags
  - Creates git tag `v{version}` (e.g., `v1.2`)
  - Use `make push VERSION=X.Y`

This ensures that `:latest` always points to the latest stable release, and git tags provide traceability for all stable container versions.

## Multi-Architecture Support

vigOS Development Environment supports both **AMD64** (x86_64) and **ARM64** (Apple Silicon) architectures:

- **Local builds** (`make build` and `make test`): Automatically builds and tests for your native platform (ARM64 on macOS, AMD64 on Linux)
- **Push to registry** (`make push`): Builds and pushes multi-arch manifests supporting both platforms
- **Pull from registry** (`make pull`): Automatically pulls the correct architecture for your platform

This ensures seamless development across different platforms without manual platform specification.

## Testing

vigOS Development Environment relies on comprehensive tests to verify both container images and devcontainer functionality.
For detailed information about the testing strategy, test structure, and how to develop tests, see the [Testing Guide](TESTING.md).
