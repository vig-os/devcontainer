# vigOS Development Environment

This repository provides a standardized development container image.
It serves as a minimal, consistent development environment with essential
tools and configurations for containerized development workflows.

## Requirements

To use this devcontainer image, you need:

- **VS Code** - Visual Studio Code editor
- **Dev Containers extension** - VS Code extension for working with development containers
- **Podman** or **Docker** - Container runtime to run the container image

That's it! All development tools (Python, git, pre-commit, just, etc.) are included in the container image itself.

## Setup

### Podman Socket Setup (Debian/Ubuntu)

If you're using **Podman** on Debian/Ubuntu, you need to enable the Podman socket service to allow the devcontainer to access Podman from inside containers (required for sidecars and container builds).

**Install Podman** (if not already installed):

```bash
sudo apt-get update
sudo apt-get install -y podman
```

**Enable and start the Podman socket service**:

```bash
# Enable the socket service to start automatically on login
systemctl --user enable podman.socket

# Start the socket service now
systemctl --user start podman.socket

# Verify it's running
systemctl --user status podman.socket
```

The socket will be created at `/run/user/$(id -u)/podman/podman.sock` and will automatically start on future logins.

**Note**: The devcontainer's `initialize.sh` script automatically detects and configures the socket path. If you need to manually configure it, create `.devcontainer/.env` with:

```bash
CONTAINER_SOCKET_PATH=/run/user/$(id -u)/podman/podman.sock
```

**Using Docker instead**: If you prefer Docker, the socket is typically at `/var/run/docker.sock`. Make sure your user is in the `docker` group:

```bash
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

The `initialize.sh` script will automatically detect Docker socket if Podman socket is not available.

## Quick Start

1. **Pull the latest image**

   ```bash
   podman pull ghcr.io/vig-os/devcontainer:latest
   # or
   docker pull ghcr.io/vig-os/devcontainer:latest
   ```

2. **Initialize a workspace inside `PATH_TO_PROJECT`**

   ```bash
   podman run -it --rm -v "PATH_TO_PROJECT:/workspace" \
     ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh
   # or with Docker:
   docker run -it --rm -v "PATH_TO_PROJECT:/workspace" \
     ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh
   ```

   The script copies the devcontainer template (`.devcontainer/`), git hooks, README/CHANGELOG, and auth helpers into your project.

3. **Run with `--force` when overwriting or updating an existing project**

   ```bash
   podman run -it --rm -v "PATH_TO_PROJECT:/workspace" \
     ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh --force
   ```

   You will be prompted to confirm before files are replaced.
   **Preserved files**: `docker-compose.project.yaml` and `docker-compose.local.yaml`
   are never overwritten, keeping your customizations intact.

   It is advised to commit all your changes before so that it can be easily reverted.

4. **Open the project in VS Code**

   VS Code will detect `.devcontainer/devcontainer.json` and offer to reopen inside the container automatically.

## Available Commands

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
    init *args                     # Check/install system dependencies (OS-sensitive)
    login                          # Test login to GHCR
    setup                          # Setup Python environment and dev tools

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
    test-registry                  # Run registry tests only (doesn't need image)

```

For detailed command descriptions, run `just --list --unsorted` or `just --help`.

## Image Details

- **Base Image**: `python:3.12-slim-trixie`
- **Registry**: `ghcr.io/vig-os/devcontainer`
- **Architecture**: Multi-platform support (AMD64, ARM64)
- **License**: Apache
- **Version**: 0.1
- **Built**: 2025-12-16T16:30:44
- **Size**: ~920 MB

## Features

### **Base Image**

- **python:3.12-slim-trixie** – Minimal Python base image (Debian Trixie) for lightweight and robust foundation

### **System Tools**

- **curl** – HTTP client for API testing and downloads
- **git** – Version control system
- **gh** – GitHub CLI for interacting with GitHub from the command line and pre-commits
- **openssh-client** – SSH client for secure Git operations and remote access
- **ca-certificates** – SSL/TLS certificate support for secure connections
- **locales** – UTF-8 locale support for internationalization

### **Python Environment**

- **Python 3.12** - Latest stable Python version
- **pip, setuptools, wheel** - Python packaging tools (included with base image)
- **uv** - Fast Python package installer and resolver

### **Development Tools**

- **pre-commit** - Git hook framework for code quality
- **ruff** - Fast Python linter and formatter (replaces Black, isort, flake8, and more)
- **just** - Command runner for task automation
- **precommit alias** - Shortcut command for running pre-commit hooks

## Contributing

If you want to contribute to the development of this devcontainer image, see [CONTRIBUTE.md](CONTRIBUTE.md) for information about:

- Requirements and setup
- Building and testing the image
- Version tagging and release process
- Multi-architecture support
- Testing strategies

## License

This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for details.
