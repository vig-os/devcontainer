#!/usr/bin/env bash
set -e

# === Configuration ===
PYTHON_VERSION="3.12.10"
UV_VERSION="0.9.13"

###############################################################################
# setup.sh
#
# EXOMA Containers Project: Setup Script
#
# This script automates the environment setup for EXOMA container development.
# It performs the following actions:
#
#  - Installs uv if missing (Python package and project manager)
#  - Installs Python $PYTHON_VERSION via uv
#  - Creates a local Python virtual environment in the project (`.venv`)
#  - Syncs project dependencies according to the `uv.lock`
#  - Sets up Git hooks for code quality (via pre-commit)
#  - Sets up GitHub Container Registry authentication
#  - Installs DevContainer CLI if missing (for devcontainer testing)
#
# USAGE:
#   ./setup.sh            # Run setup interactively
#   ./setup.sh --help     # Show this help message
#
# Requirements:
#   - Unix-like environment (Linux, macOS)
#   - curl (for installing uv if needed)
#   - git (for Git hooks)
#   - podman or docker (for GitHub Container Registry authentication)
#   - gh (for GitHub CLI)
#   - openssh-client (for SSH authentication)
#   - npm (for installing DevContainer CLI, will be checked/installed automatically)
###############################################################################

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
  # Extract help text from the script's header comment block
  sed -n '/^###############################################################################$/,/^###############################################################################$/p' "$0" | sed '1d;$d'
  exit 0
fi

# Get the project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source utilities
# shellcheck source=scripts/utils.sh
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

# === 1. Install uv if missing ===
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv $UV_VERSION..."
    curl -LsSf https://astral.sh/uv/$UV_VERSION/install.sh | sh

    # Add uv to PATH temporarily for this session
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Using uv version: $(uv --version)"

# === 2. Create virtual environment with specific Python version ===
# uv will download and install Python $PYTHON_VERSION automatically if needed
echo "Creating virtual environment with Python $PYTHON_VERSION in: $PROJECT_ROOT/.venv"
uv venv --python "$PYTHON_VERSION" .venv

# === 3. Sync project dependencies from lockfile ===
echo "Installing project dependencies (including dev dependencies)..."
uv sync --frozen --all-extras

# === 4. Setup Git hooks automatically ===
echo "Setting up Git hooks..."

# Configure custom hooks path and make executable
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

# Install hooks using uv
uv run pre-commit install-hooks

# === 5. Setup Docker/Podman authentication ===
DOCKER_CONFIG="$HOME/.docker/config.json"

# Determine which container runtime to use
if command -v podman >/dev/null 2>&1; then
    CONTAINER_CMD="podman"
elif command -v docker >/dev/null 2>&1; then
    CONTAINER_CMD="docker"
else
    echo "Warning: Neither podman nor docker found. Skipping GHCR authentication."
    echo "Install podman or docker to enable container registry access."
    CONTAINER_CMD=""
    exit 1
fi
echo "Using $CONTAINER_CMD as container runtime and compose"

if [ -n "$CONTAINER_CMD" ]; then
    if [ ! -f "$DOCKER_CONFIG" ]; then
        echo "Container registry config not found. Setting up GitHub Container Registry authentication..."

        # Ensure .docker directory exists
        mkdir -p "$HOME/.docker"

        # Prompt for GitHub credentials
        read -r -p "Enter GitHub Username: " GITHUB_USER
        read -r -s -p "Enter GitHub Token: " GITHUB_TOKEN
        echo

        # Login to GHCR
        echo "$GITHUB_TOKEN" | $CONTAINER_CMD login ghcr.io -u "$GITHUB_USER" --password-stdin

        echo "GitHub Container Registry authentication configured."
    else
        echo "Container registry config exists at $DOCKER_CONFIG. Verifying authentication..."
        if $CONTAINER_CMD login ghcr.io --get-login >/dev/null 2>&1 || \
           run_with_timeout 2 $CONTAINER_CMD login ghcr.io >/dev/null 2>&1; then
            echo "✓ GitHub Container Registry authentication verified."
        else
            echo "⚠ Warning: Could not verify authentication."
            echo "  If you encounter authentication issues, run:"
            echo "    $CONTAINER_CMD login ghcr.io"
        fi
    fi
fi


# === 6. Verify GitHub CLI authentication ===

if ! command -v gh >/dev/null 2>&1; then
    echo "⚠ Warning: GitHub CLI (gh) is not installed."
    echo "  Please install GitHub CLI: https://cli.github.com/"
else
    if ! gh auth status >/dev/null 2>&1; then
        echo "⚠ Warning: GitHub CLI is not authenticated."
        echo "  Run 'gh auth login' to authenticate with GitHub."
    else
        echo "✓ GitHub CLI authentication verified."
    fi
fi


# === 7. Install DevContainer CLI ===

DEVCONTAINER_CLI_VERSION="0.80.1"

if command -v devcontainer >/dev/null 2>&1; then
    DEVCONTAINER_VERSION=$(devcontainer --version 2>/dev/null | head -n1 | sed 's/.*version //' | sed 's/ .*//' || echo "unknown")

    # Check if version matches expected version
    if [ "$DEVCONTAINER_VERSION" != "$DEVCONTAINER_CLI_VERSION" ]; then
        echo "⚠ DevContainer CLI is installed but version mismatch:"
        echo "  Installed: $DEVCONTAINER_VERSION"
        echo "  Expected:  $DEVCONTAINER_CLI_VERSION"
        echo ""
        read -r -p "Would you like to reinstall with version $DEVCONTAINER_CLI_VERSION? (y/N): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Reinstalling DevContainer CLI version $DEVCONTAINER_CLI_VERSION..."
            npm install -g "@devcontainers/cli@$DEVCONTAINER_CLI_VERSION"

            # Verify new version
            NEW_VERSION=$(devcontainer --version 2>/dev/null | head -n1 | sed 's/.*version //' | sed 's/ .*//' || echo "unknown")
            if [ "$NEW_VERSION" = "$DEVCONTAINER_CLI_VERSION" ]; then
                echo "✓ DevContainer CLI reinstalled successfully (version: $NEW_VERSION)"
            else
                echo "⚠ DevContainer CLI reinstalled but version check failed (got: $NEW_VERSION)"
            fi
        else
            echo "Keeping existing DevContainer CLI version $DEVCONTAINER_VERSION"
        fi
    else
        echo "✓ DevContainer CLI is installed (version: $DEVCONTAINER_VERSION)"
    fi
else
    echo "DevContainer CLI not found. Checking for npm..."

    if ! command -v npm >/dev/null 2>&1; then
        echo "❌ npm is not installed."
        echo ""
        echo "Please install Node.js and npm, then rerun this script:"
        echo "  - Ubuntu/Debian: sudo apt install nodejs npm"
        echo "  - macOS: brew install node"
        echo "  - Or download from: https://nodejs.org/"
        echo ""
        exit 1
    fi

    echo "Installing DevContainer CLI version $DEVCONTAINER_CLI_VERSION..."
    npm install -g "@devcontainers/cli@$DEVCONTAINER_CLI_VERSION"

    if command -v devcontainer >/dev/null 2>&1; then
        INSTALLED_VERSION=$(devcontainer --version 2>/dev/null | head -n1 | sed 's/.*version //' | sed 's/ .*//' || echo "unknown")
        echo "✓ DevContainer CLI installed successfully (version: $INSTALLED_VERSION)"
    else
        echo "❌ Failed to install DevContainer CLI."
        echo "  Please install manually with: npm install -g @devcontainers/cli@$DEVCONTAINER_CLI_VERSION"
        exit 1
    fi
fi


# === 8. Done ===
echo ""
echo "✓ Environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Run 'make help' to see the available commands."
