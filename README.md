# vigOS Development Environment

This repository provides a standardized development container image.
It serves as a minimal, consistent development environment with essential
tools and configurations for containerized development workflows.

## Requirements

To use this devcontainer image, you need:

- **VS Code** - Visual Studio Code editor
- **Dev Containers extension** - VS Code extension for working with development containers
- **Podman** or **Docker** - Container runtime to run the container image

That's it! All development tools (Python, git, pre-commit, etc.) are included in the container image itself.

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
   It is advised to commit all your changes before so that it can be easily reverted.

4. **Open the project in VS Code**

   VS Code will detect `.devcontainer/devcontainer.json` and offer to reopen inside the container automatically.

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
- **precommit alias** - Shortcut command for running pre-commit hooks

## **VS Code Integration**

The container includes a template that configures recommended VS Code
integration when you initialize a project with `init-workspace`.

### Deployment into a project

To deploy the devcontainer into your project, run the `init-workspace` script
from your host terminal:

```bash
podman run -it --rm -v "./:/workspace" ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh
```

This script:
- Copies the devcontainer asset files (`.devcontainer/` directory, a README...) to your workspace
- Prompts for a project short name and replaces placeholders throughout the assets
- Sets up executable permissions on scripts and git hooks
- Initializes a git repository if one doesn't exist

The template includes:
- `devcontainer.json` - VS Code devcontainer configuration
- Pre-configured scripts for git setup, authentication, and pre-commit hooks
- Git hooks for commit signing and verification
- Project template files: README and CHANGELOG

### Mounting Additional Folders

The devcontainer supports mounting additional folders/projects using Docker Compose override files. This is useful for:

- Multi-project development (monorepos, microservices)
- Shared libraries or resources
- Reference documentation

To mount additional folders:

1. Copy the example file:

   ```bash
   cp .devcontainer/docker-compose.override.yml.example \
      .devcontainer/docker-compose.override.yml
   ```

2. Add your mounts to `docker-compose.override.yml`:

```yaml
   version: '3.8'

   services:
     devcontainer:
       volumes:
         - ../other-project:/workspace/other-project:cached
         - ~/shared-libs:/workspace/shared:cached
   ```

1. Rebuild the devcontainer

The override file is gitignored, so each developer can have their own local mounts.
See `.devcontainer/MOUNTS.md` for detailed documentation and examples.

### Multi-root VS Code workspace

Multi-root workspaces allow to **browse/edit the mounted folders from VS Code** —for
runtime-only usage, mounting through `docker-compose.override.yml` is enough.

1. Copy the template once per machine:
   `cp .devcontainer/workspace.code-workspace.example .devcontainer/workspace.code-workspace`
2. Customize the `folders` array with additional projects mounted via `docker-compose.override.yml`.
3. VS Code will automatically offer the `Open Workspace` option.

Your personal `workspace.code-workspace` stays gitignored and therefore only local.
If you want to share new defaults, update `.devcontainer/workspace.code-workspace.example`
and teammates can recopy or merge the changes locally.

### Authentication

GitHub authentication is handled automatically when the devcontainer starts:

1. **GitHub CLI**: The container copies your host's GitHub CLI configuration
   (from `~/.config/gh/`) into the container on startup
2. **Token-based auth**: If a GitHub token is placed in
   `.devcontainer/.conf/.gh_token`, it will be used to authenticate the GitHub CLI
   and then automatically removed for security
3. **SSH Agent**: SSH agent forwarding is configured automatically for git operations
   and commit signing

The authentication setup runs via the `postAttachCommand` hook, which executes
`.devcontainer/scripts/post-attach.sh` when VS Code attaches to the container.

### Git configuration

Git configuration is synchronized from the host to ensure consistency:

1. **Git config**: Your host's git configuration (user.name, user.email, etc.) is
   copied from `.devcontainer/.conf/.gitconfig` into the container
2. **Commit signing**: SSH public key for commit signing is copied from
   `.devcontainer/.conf/id_ed25519_github.pub` and configured automatically
3. **Signature verification**: The `allowed-signers` file is set up for git
   signature verification
4. **Git hooks**: Pre-commit hooks are installed and configured automatically

To set up these files on the host, run `.devcontainer/scripts/copy-host-user-conf.sh`
from your project root before starting the devcontainer.

### Extensions

The following VS Code extensions are automatically installed and configured:

- **ms-python.python** - Python language support
- **charliermarsh.ruff** - Ruff linter and formatter for Python
- **ms-vscode.vscode-json** - JSON language support
- **redhat.vscode-yaml** - YAML language support
- **GitHub.vscode-pull-request-github** - GitHub Pull Request integration

These extensions are configured in the `.devcontainer/devcontainer.json`
template, not installed in the container image itself. VS Code settings are
also pre-configured for development with format-on-save and automatic
import organization.

## Image Details

- **Base Image**: `python:3.12-slim-trixie`
- **Registry**: `ghcr.io/vig-os/devcontainer`
- **Architecture**: Multi-platform support (AMD64, ARM64)
- **License**: MIT
- **Version**: [99.9204](https://github.com/vig-os/devcontainer/releases/tag/v99.9204), 2025-12-03
- **Size**: ~140 MB

## Contributing

If you want to contribute to the development of this devcontainer image, see [CONTRIBUTE.md](CONTRIBUTE.md) for information about:

- Requirements and setup
- Building and testing the image
- Version tagging and release process
- Multi-architecture support
- Testing strategies

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
