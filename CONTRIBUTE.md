
<!-- Auto-generated from docs/templates/CONTRIBUTE.md.j2 - DO NOT EDIT DIRECTLY -->
<!-- Run 'just docs' to regenerate -->

# Contributing to vigOS Development Environment

This guide explains how to develop, build, test, and release the vigOS development container image.

## Requirements

| Component            | Version | Purpose |
|----------------------|---------|---------|
| **podman** | >=4.0 | Container runtime, compose, and image building |
| **just** | >=1.40.0 | Command runner for task automation |
| **git** | >=2.34 | Version control and pre-commit hooks |
| **ssh** | latest | GitHub authentication and commit signing |
| **gh** | latest | GitHub CLI for repository and PR/issue management |
| **npm** | latest | Node.js package manager (for DevContainer CLI) |
| **uv** | >=0.8 | Python package and project manager |
| **devcontainer** | 0.80.1 | DevContainer CLI for testing devcontainer functionality |

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install -y podman git openssh-client nodejs npm
# just
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# gh
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install -y gh

```

**macOS (Homebrew):**

```bash
brew install podman just git openssh gh node
```

- For other Linux distributions, use your package manager (e.g., `dnf`, `yum`, `zypper`, `apk`) to install these dependencies.
- Run `./scripts/init.sh` to check dependencies and get OS-specific installation commands.
- Ensure Docker is installed if you plan to use it instead of Podman.

## Setup

Clone this repository and prepare it for container development:

```bash
git clone git@github.com:vig-os/devcontainer.git
cd devcontainer
just init           # Install dependencies and setup development environment
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
   - Build and test locally: `just build && just test`
   - Ensure your code follows the project's style and conventions

4. **Update documentation if necessary**
   - Update templates in `docs/templates/` (not the generated files directly)
   - Run `just docs` to regenerate documentation
   - Update the [CHANGELOG](CHANGELOG.md) with your changes in the `[Unreleased]` section
     - Add entries under appropriate categories (Added, Changed, Fixed, etc.)
     - Use clear, concise descriptions
     - Reference related [issues](https://github.com/vig-os/devcontainer/issues) and [PRs](https://github.com/vig-os/devcontainer/pulls) when applicable
   - Keep documentation in sync with code changes

5. **Verify tests pass**

   ```bash
   # Run all test suites (image, integration, registry)
   just test

   # Or run individual test suites
   just test-image
   just test-integration
   just test-utils
   just test-version-check
   ```

6. **Create a pull request**
   - Create a [pull request](https://github.com/vig-os/devcontainer/pulls) targeting the `dev` branch
   - Link the PR to the related [issue(s)](https://github.com/vig-os/devcontainer/issues)
   - Provide a clear description of your changes

7. **Accepted contributions will be merged into `dev` branch**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, your changes will be merged into `dev`

## Just Recipes

```text
Available recipes:
    [build]
    build no_cache=""              # Build local development image
    clean version="dev"            # Remove image (default: dev)
    clean-artifacts                # Clean build artifacts
    clean-test-containers          # Clean up lingering test containers

    [deps]
    sync                           # Sync dependencies from pyproject.toml
    update                         # Update all dependencies

    [info]
    default                        # Show available commands (default)
    docs                           # Generate documentation from templates
    help                           # Show available commands
    info                           # Show image information
    init *args                     # Install system dependencies and setup development environment
    login                          # Test login to GHCR

    [podman]
    podman-kill name               # Stop and remove a container by name or ID
    podman-kill-all                # Stop and remove all containers (with confirmation)
    podman-kill-project            # Stop and remove project-related containers
    podman-prune                   # Prune unused containers, images, networks, and volumes
    podman-prune-all               # Full cleanup: prune including volumes
    podman-ps *args                # List containers/images (--all for all podman resources)
    podman-rmi image               # Remove an image by name, tag, or ID
    podman-rmi-all                 # Remove all images (with confirmation)
    podman-rmi-dangling            # Remove dangling images (untagged)
    podman-rmi-project             # Remove project-related images

    [quality]
    format                         # Format code
    lint                           # Run all linters
    precommit                      # Run pre-commit hooks on all files

    [release]
    pull version="latest"          # Pull image from registry (default: latest)
    push version                   # Push versioned release to registry (builds, tests, tags, pushes)

    [sidecar]
    sidecar name *args             # just sidecar redis flush
    sidecars                       # List available sidecar containers
    test-sidecar *args             # Convenience alias for test-sidecar (uses generic sidecar recipe)

    [test]
    test version="dev"             # Run all test suites
    test-cov *args                 # Run tests with coverage
    test-image version="dev"       # Run image tests only
    test-integration version="dev" # Run integration tests only
    test-pytest *args              # Run tests with pytest
    test-utils                     # Run utils tests only
    test-version-check             # Run version check tests only

```

## Release Workflow

When releasing a new version of the devcontainer image, follow these steps:

1. **Update documentation**
   - Ensure documentation templates are up to date
   - Run `just docs` to regenerate all documentation
   - Update [CHANGELOG.md](CHANGELOG.md):
     - Move all `[Unreleased]` entries to a new version section (e.g., `[1.0.0]`)
     - Add the release date in YYYY-MM-DD format
     - Update the version links at the bottom of the file
     - Clear the `[Unreleased]` section for future changes
   - Verify all documentation reflects the current state

2. **Run tests**

   ```bash
   # Run all test suites to ensure everything works
   just test
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

4. **Release with `just push` (creates tag)**

   ```bash
   # Replace X.Y.Z with the semantic version (e.g. 1.0.0, 1.1.0, 2.0.0)
   # Version must follow Semantic Versioning format: MAJOR.MINOR.PATCH
   just push X.Y.Z
   ```

   - This will:
     - Build the image for the specified version
     - Run tests (unless `no_test=true` is specified)
     - Push the image to GHCR with both `:latest` and `:X.Y.Z` tags
     - Update [README.md](README.md) with the new version
     - Create a git commit with the README.md update (commit message: "Release X.Y.Z")
     - Create a git tag `vX.Y.Z` pointing to that commit

5. **Create pull request to merge into `main`**
   - After the release is pushed, create a [pull request](https://github.com/vig-os/devcontainer/pulls) from `dev` to `main`
   - The PR should include:
     - Summary of changes in this release
     - Reference to the version tag created
     - Any important notes for users
   - Once merged, `main` will reflect the stable release

## Version Tagging

vigOS Development Environment uses **Semantic Versioning** ([SemVer](https://semver.org/)) to manage both GHCR tags and git tags:

- **Development versions** (`dev`):
  - Only local, without time stamp or git reference
  - Meant for development and testing only
  - Use `just build` and `just test` to build and test

- **Stable versions** (e.g., `1.2.0`, `2.0.0`):
  - Follow Semantic Versioning format: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.2.3`, `2.0.0`)
  - Pushes to GHCR with both `:latest` and `:version` tags
  - Creates git tag `v{version}` (e.g., `v1.2.0`)
  - Use `just push X.Y.Z` where X.Y.Z is the semantic version

This ensures that `:latest` always points to the latest stable release, and git tags provide traceability for all stable container versions.

## Multi-Architecture Support

vigOS Development Environment supports both **AMD64** (x86_64) and **ARM64** (Apple Silicon) architectures:

- **Local builds** (`just build` and `just test`): Automatically builds and tests for your native platform (ARM64 on macOS, AMD64 on Linux)
- **Push to registry** (`just push`): Builds and pushes multi-arch manifests supporting both platforms
- **Pull from registry** (`just pull`): Automatically pulls the correct architecture for your platform

This ensures seamless development across different platforms without manual platform specification.

## Testing

vigOS Development Environment relies on comprehensive tests to verify both container images and devcontainer functionality.
For detailed information about the testing strategy, test structure, and how to develop tests, see the [Testing Guide](TESTING.md).
