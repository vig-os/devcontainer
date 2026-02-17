#!/bin/bash
# vigOS devcontainer quick install script
#
# Usage:
#   curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh
#   curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- [OPTIONS] [PATH]
#
# Options:
#   --force           Overwrite existing files (for upgrades)
#   --version VER     Use specific version (default: latest)
#   --docker          Force docker (default: auto-detect, prefers podman)
#   --podman          Force podman
#   --name NAME       Override project name (SHORT_NAME)
#   --org ORG         Override organization name (default: vigOS)
#   --dry-run         Show what would be done without executing
#   -h, --help        Show this help message
#
# Examples:
#   curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh
#   curl -sSf ... | sh -s -- ~/Projects/my-project
#   curl -sSf ... | sh -s -- --version 1.0.0 --force ./my-project
#   curl -sSf ... | sh -s -- --org MyOrg ./my-project

set -euo pipefail

# Configuration
REGISTRY="ghcr.io/vig-os/devcontainer"
VERSION="latest"
RUNTIME=""
FORCE=""
DRY_RUN=false
SKIP_PULL=false
PROJECT_PATH=""
PROJECT_NAME=""
ORG_NAME="vigOS"

# Colors (disabled if not a tty)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

err() { echo -e "${RED}error${NC}: $1" >&2; }
info() { echo -e "${BLUE}info${NC}: $1"; }
warn() { echo -e "${YELLOW}warn${NC}: $1"; }
success() { echo -e "${GREEN}success${NC}: $1"; }

usage() {
    cat <<'EOF'
vigOS Devcontainer Install Script

USAGE:
    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh
    curl -sSf ... | sh -s -- [OPTIONS] [PATH]

OPTIONS:
    --force           Overwrite existing files (for upgrades)
    --version VER     Use specific version (default: latest)
    --docker          Force docker runtime
    --podman          Force podman runtime
    --name NAME       Override project name (SHORT_NAME, used for module name)
    --org ORG         Override organization name (default: vigOS)
    --dry-run         Show what would be done
    -h, --help        Show this help

EXAMPLES:
    # Initialize current directory with latest version
    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh

    # Initialize specific directory
    curl -sSf ... | sh -s -- ~/Projects/my-new-project

    # Upgrade existing project
    curl -sSf ... | sh -s -- --force ./my-project

    # Use specific version
    curl -sSf ... | sh -s -- --version 1.0.0 ./my-project

    # Override project name
    curl -sSf ... | sh -s -- --name my_custom_name ./my-project

    # Use custom organization name
    curl -sSf ... | sh -s -- --org MyOrg ./my-project
EOF
}

detect_os() {
    case "$(uname -s)" in
        Darwin*)  echo "macos" ;;
        Linux*)
            if [ -f /etc/os-release ]; then
                # shellcheck source=/dev/null
                . /etc/os-release
                case "$ID" in
                    ubuntu|debian|pop|linuxmint) echo "debian" ;;
                    fedora|rhel|centos|rocky|almalinux) echo "fedora" ;;
                    arch|manjaro|endeavouros) echo "arch" ;;
                    opensuse*|sles) echo "suse" ;;
                    *) echo "linux" ;;
                esac
            else
                echo "linux"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

detect_runtime() {
    if [ -n "$RUNTIME" ]; then
        echo "$RUNTIME"
        return
    fi

    if command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        echo ""
    fi
}

show_install_instructions() {
    local os="$1"

    echo ""
    echo "Please install podman (recommended) or docker:"
    echo ""

    case "$os" in
        macos)
            echo "  ${BLUE}macOS (Homebrew):${NC}"
            echo "    brew install podman"
            echo "    podman machine init"
            echo "    podman machine start"
            echo ""
            echo "  ${BLUE}macOS (Docker Desktop):${NC}"
            echo "    Download from: https://docker.com/products/docker-desktop"
            ;;
        debian)
            echo "  ${BLUE}Ubuntu/Debian:${NC}"
            echo "    sudo apt update"
            echo "    sudo apt install -y podman"
            echo ""
            echo "  ${BLUE}Or Docker:${NC}"
            echo "    curl -fsSL https://get.docker.com | sh"
            echo "    sudo usermod -aG docker \$USER"
            echo "    # Log out and back in for group changes"
            ;;
        fedora)
            echo "  ${BLUE}Fedora/RHEL/CentOS:${NC}"
            echo "    sudo dnf install -y podman"
            echo ""
            echo "  ${BLUE}Or Docker:${NC}"
            echo "    sudo dnf install -y docker-ce docker-ce-cli containerd.io"
            echo "    sudo systemctl enable --now docker"
            echo "    sudo usermod -aG docker \$USER"
            ;;
        arch)
            echo "  ${BLUE}Arch Linux:${NC}"
            echo "    sudo pacman -S podman"
            echo ""
            echo "  ${BLUE}Or Docker:${NC}"
            echo "    sudo pacman -S docker"
            echo "    sudo systemctl enable --now docker"
            echo "    sudo usermod -aG docker \$USER"
            ;;
        suse)
            echo "  ${BLUE}openSUSE/SLES:${NC}"
            echo "    sudo zypper install podman"
            echo ""
            echo "  ${BLUE}Or Docker:${NC}"
            echo "    sudo zypper install docker"
            echo "    sudo systemctl enable --now docker"
            ;;
        windows)
            echo "  ${BLUE}Windows:${NC}"
            echo "    1. Install WSL2: wsl --install"
            echo "    2. Install Docker Desktop: https://docker.com/products/docker-desktop"
            echo "       (Enable WSL2 backend in settings)"
            echo ""
            echo "  ${BLUE}Or Podman Desktop:${NC}"
            echo "    Download from: https://podman-desktop.io"
            ;;
        *)
            echo "  ${BLUE}Generic Linux:${NC}"
            echo "    # Check your distribution's package manager for 'podman' or 'docker'"
            echo ""
            echo "  ${BLUE}Docker (universal):${NC}"
            echo "    curl -fsSL https://get.docker.com | sh"
            echo "    sudo usermod -aG docker \$USER"
            ;;
    esac

    echo ""
    echo "After installation, run this script again."
    echo ""
}

# Sanitize project name: replace hyphens and spaces with underscore; lowercase; remove other special chars
sanitize_name() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[ -]/_/g' | sed 's/[^a-z0-9_]/_/g'
}

# Run copy-host-user-conf.sh from the deployed project (non-fatal)
run_user_conf() {
    local project_path="$1"
    local script="$project_path/.devcontainer/scripts/copy-host-user-conf.sh"

    if [ ! -f "$script" ]; then
        warn "User configuration script not found at $script"
        echo "  Ensure the workspace has been initialized first."
        return 1
    fi

    info "Running user configuration setup (git, ssh, gh)..."
    if bash "$script"; then
        success "User configuration complete"
    else
        warn "User configuration had issues (see warnings above)"
        echo "  You can re-run this step later with:"
        echo "    cd $project_path && bash .devcontainer/scripts/copy-host-user-conf.sh"
        echo "  Or use: bash install.sh --user-conf $project_path"
    fi
}

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --force)
            FORCE="--force"
            shift
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --docker)
            RUNTIME="docker"
            shift
            ;;
        --podman)
            RUNTIME="podman"
            shift
            ;;
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --org)
            ORG_NAME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-pull)
            SKIP_PULL=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            err "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            PROJECT_PATH="$1"
            shift
            ;;
    esac
done

# Validate and set project path
PROJECT_PATH="${PROJECT_PATH:-.}"
if [ ! -d "$PROJECT_PATH" ]; then
    err "Directory does not exist: $PROJECT_PATH"
    exit 1
fi
PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"

# Derive project name from folder if not provided
if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME="$(basename "$PROJECT_PATH")"
fi
PROJECT_NAME=$(sanitize_name "$PROJECT_NAME")

# Detect container runtime
RUNTIME=$(detect_runtime)
if [ -z "$RUNTIME" ]; then
    err "No container runtime found!"
    OS=$(detect_os)
    show_install_instructions "$OS"
    exit 1
fi

# Verify runtime is actually working
if ! $RUNTIME info >/dev/null 2>&1; then
    OS=$(detect_os)
    err "$RUNTIME is installed but not running!"
    echo ""
    case "$OS" in
        macos)
            if [ "$RUNTIME" = "podman" ]; then
                echo "Start the Podman machine:"
                echo "  podman machine start"
                echo ""
                echo "If no machine exists, create one first:"
                echo "  podman machine init"
                echo "  podman machine start"
            else
                echo "Start Docker Desktop from your Applications folder,"
                echo "or run: open -a Docker"
            fi
            ;;
        windows)
            echo "Make sure Docker Desktop or Podman Desktop is running."
            echo "Check the system tray for the container icon."
            ;;
        *)
            if [ "$RUNTIME" = "docker" ]; then
                echo "Start the Docker daemon:"
                echo "  sudo systemctl start docker"
                echo ""
                echo "To enable on boot:"
                echo "  sudo systemctl enable docker"
            else
                echo "Podman should work without a daemon on Linux."
                echo "Try running: podman info"
                echo ""
                echo "If using rootless podman, ensure your user session is set up:"
                echo "  podman system migrate"
            fi
            ;;
    esac
    echo ""
    exit 1
fi

IMAGE="$REGISTRY:$VERSION"

info "Using $RUNTIME with image $IMAGE"
info "Target directory: $PROJECT_PATH"
info "Project name: $PROJECT_NAME"

# Build the command
# Use --rm to cleanup container after run; no -it since we use --no-prompts (non-interactive)
# Pass SHORT_NAME and ORG_NAME as environment variables to the container
CMD="$RUNTIME run --rm -e SHORT_NAME=\"$PROJECT_NAME\" -e ORG_NAME=\"$ORG_NAME\" -v \"$PROJECT_PATH:/workspace\" \"$IMAGE\" /root/assets/init-workspace.sh --no-prompts $FORCE"

if [ "$DRY_RUN" = true ]; then
    info "Would execute:"
    echo "  $CMD"
    exit 0
fi

# Check if terminal is interactive (needed for init-workspace.sh prompts)
# When piped via curl, stdin is the script - use /dev/tty for user input
# Only check this when actually running (not in dry-run mode)
if [ ! -t 0 ]; then
    if [ ! -e /dev/tty ]; then
        err "This script requires an interactive terminal"
        echo ""
        echo "Try running directly instead of piping:"
        echo "  curl -sSf https://vig-os.github.io/devcontainer/install.sh -o install.sh"
        echo "  bash install.sh $PROJECT_PATH"
        exit 1
    fi
fi

# Pull image first (better UX - shows progress separately)
if [ "$SKIP_PULL" = false ]; then
    info "Pulling image $IMAGE..."
    if ! $RUNTIME pull "$IMAGE" >/dev/null 2>&1; then
        err "Failed to pull image $IMAGE"
        echo ""
        echo "Check your internet connection and that the image exists:"
        echo "  $REGISTRY:$VERSION"
        exit 1
    fi
else
    # Verify image exists locally when skipping pull
    if ! $RUNTIME image exists "$IMAGE" 2>/dev/null; then
        err "Image $IMAGE not found locally (--skip-pull was specified)"
        exit 1
    fi
    info "Using local image $IMAGE (skipping pull)"
fi

# Run the initialization
info "Initializing workspace..."
echo ""

# Execute the container
# Since we use --no-prompts, no interactive input is needed.
if ! eval "$CMD"; then
    err "Failed to initialize workspace"
    exit 1
fi

# ── Post-initialization: host-side setup ──────────────────────────────────────

echo ""
info "Running post-initialization setup..."

# 1. Copy host user configuration (git, ssh, gh) into .devcontainer/.conf/
# Non-fatal: warnings about missing SSH keys or GH CLI are expected on CI/fresh machines
run_user_conf "$PROJECT_PATH" || true

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
success "Devcontainer deployed to $PROJECT_PATH"
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_PATH"
echo "  2. Open in VS Code - it will detect .devcontainer/ and offer to reopen in container"
echo ""
