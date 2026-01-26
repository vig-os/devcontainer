#!/usr/bin/env bash
###############################################################################
# init.sh - Development Environment Initializer
#
# Checks and installs development dependencies from requirements.yaml.
# Provides OS-sensitive installation with interactive confirmations.
#
# USAGE:
#   ./scripts/init.sh              # Interactive mode
#   ./scripts/init.sh --check      # Check only, don't install
#   ./scripts/init.sh --yes        # Auto-confirm all installations
#   ./scripts/init.sh --help       # Show this help
#
# REQUIREMENTS FILE:
#   scripts/requirements.yaml      # Single source of truth for dependencies
#
# SUPPORTED PLATFORMS:
#   - macOS (Homebrew)
#   - Debian/Ubuntu (apt)
#   - Fedora/RHEL (dnf)
#   - Alpine (apk)
###############################################################################

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.yaml"
PYTHON_VERSION="3.12.10"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Flags
CHECK_ONLY=false
AUTO_YES=false
VERBOSE=false

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

print_header() {
    echo -e "\n${BOLD}${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_section() {
    echo -e "\n${BOLD}${CYAN}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}───────────────────────────────────────────────────────────────${NC}\n"
}

log_info() {
    echo -e "${BLUE}ℹ${NC}  $1"
}

log_success() {
    echo -e "${GREEN}✓${NC}  $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

log_error() {
    echo -e "${RED}✗${NC}  $1"
}

log_debug() {
    if $VERBOSE; then
        echo -e "${CYAN}…${NC}  $1"
    fi
}

# Prompt for yes/no confirmation
# Usage: confirm "Question?" && do_something
confirm() {
    if $AUTO_YES; then
        return 0
    fi

    local prompt="$1 [y/N]: "
    local response

    echo -en "${YELLOW}?${NC}  ${prompt}"
    read -r response

    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════════════
# OS DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

detect_os() {
    local os_type=""
    local os_id=""

    case "$(uname -s)" in
        Darwin)
            os_type="macos"
            ;;
        Linux)
            if [ -f /etc/os-release ]; then
                # shellcheck source=/dev/null
                . /etc/os-release
                os_id="${ID:-unknown}"

                case "$os_id" in
                    debian|ubuntu|pop|linuxmint|elementary)
                        os_type="debian"
                        ;;
                    fedora|rhel|centos|rocky|alma)
                        os_type="fedora"
                        ;;
                    alpine)
                        os_type="alpine"
                        ;;
                    arch|manjaro)
                        os_type="arch"
                        ;;
                    *)
                        os_type="linux"
                        ;;
                esac
            else
                os_type="linux"
            fi
            ;;
        *)
            os_type="unknown"
            ;;
    esac

    echo "$os_type"
}

get_os_pretty_name() {
    case "$(uname -s)" in
        Darwin)
            echo "macOS $(sw_vers -productVersion 2>/dev/null || echo '')"
            ;;
        Linux)
            if [ -f /etc/os-release ]; then
                # shellcheck source=/dev/null
                . /etc/os-release
                echo "${PRETTY_NAME:-Linux}"
            else
                echo "Linux"
            fi
            ;;
        *)
            echo "Unknown OS"
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════════════
# YAML PARSING (Pure Bash - no external dependencies)
# ═══════════════════════════════════════════════════════════════════════════════

# Simple YAML parser for our requirements.yaml format
# Extracts dependency information into associative arrays
parse_requirements() {
    local yaml_file="$1"
    local in_dependencies=false
    local in_optional=false
    local current_section=""

    # Reset global arrays
    DEPS_NAMES=()
    DEPS_VERSIONS=()
    DEPS_PURPOSES=()
    DEPS_REQUIRED=()
    DEPS_CHECK_CMDS=()
    DEPS_INSTALL_MACOS=()
    DEPS_INSTALL_DEBIAN=()
    DEPS_INSTALL_FEDORA=()
    DEPS_INSTALL_ALPINE=()
    DEPS_INSTALL_ALL=()
    DEPS_INSTALL_MANUAL=()

    local current_name=""
    local current_version=""
    local current_purpose=""
    local current_required="true"
    local current_check_cmd=""
    local current_install_macos=""
    local current_install_debian=""
    local current_install_fedora=""
    local current_install_alpine=""
    local current_install_all=""
    local current_install_manual=""

    while IFS= read -r line || [ -n "$line" ]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// /}" ]] && continue

        # Detect section starts
        if [[ "$line" =~ ^dependencies: ]]; then
            in_dependencies=true
            in_optional=false
            continue
        elif [[ "$line" =~ ^optional: ]]; then
            in_dependencies=false
            in_optional=true
            continue
        fi

        # Process dependencies
        if $in_dependencies || $in_optional; then
            # New dependency entry (starts with "  - name:")
            if [[ "$line" =~ ^[[:space:]]{2}-[[:space:]]name:[[:space:]]*(.+) ]]; then
                # Save previous dependency if exists
                if [ -n "$current_name" ]; then
                    DEPS_NAMES+=("$current_name")
                    DEPS_VERSIONS+=("$current_version")
                    DEPS_PURPOSES+=("$current_purpose")
                    DEPS_REQUIRED+=("$current_required")
                    DEPS_CHECK_CMDS+=("$current_check_cmd")
                    DEPS_INSTALL_MACOS+=("$current_install_macos")
                    DEPS_INSTALL_DEBIAN+=("$current_install_debian")
                    DEPS_INSTALL_FEDORA+=("$current_install_fedora")
                    DEPS_INSTALL_ALPINE+=("$current_install_alpine")
                    DEPS_INSTALL_ALL+=("$current_install_all")
                    DEPS_INSTALL_MANUAL+=("$current_install_manual")
                fi

                # Reset for new dependency
                current_name="${BASH_REMATCH[1]}"
                current_version=""
                current_purpose=""
                current_required="$($in_optional && echo "false" || echo "true")"
                current_check_cmd=""
                current_install_macos=""
                current_install_debian=""
                current_install_fedora=""
                current_install_alpine=""
                current_install_all=""
                current_install_manual=""
                current_section=""
                continue
            fi

            # Parse dependency fields
            if [[ "$line" =~ ^[[:space:]]{4}version:[[:space:]]*[\"\']?([^\"\']*)[\"\']? ]]; then
                current_version="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{4}purpose:[[:space:]]*(.+) ]]; then
                current_purpose="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{4}required:[[:space:]]*(true|false) ]]; then
                current_required="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{4}check: ]]; then
                current_section="check"
            elif [[ "$line" =~ ^[[:space:]]{4}install: ]]; then
                current_section="install"
            elif [[ "$line" =~ ^[[:space:]]{6}command:[[:space:]]*(.+) ]] && [ "$current_section" = "check" ]; then
                current_check_cmd="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{6}macos:[[:space:]]*(.+) ]] && [ "$current_section" = "install" ]; then
                current_install_macos="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{6}debian:[[:space:]]*(.+) ]] && [ "$current_section" = "install" ]; then
                current_install_debian="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{6}fedora:[[:space:]]*(.+) ]] && [ "$current_section" = "install" ]; then
                current_install_fedora="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{6}alpine:[[:space:]]*(.+) ]] && [ "$current_section" = "install" ]; then
                current_install_alpine="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{6}all:[[:space:]]*(.+) ]] && [ "$current_section" = "install" ]; then
                current_install_all="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^[[:space:]]{6}manual:[[:space:]]*(.+) ]] && [ "$current_section" = "install" ]; then
                current_install_manual="${BASH_REMATCH[1]}"
            fi
        fi
    done < "$yaml_file"

    # Save last dependency
    if [ -n "$current_name" ]; then
        DEPS_NAMES+=("$current_name")
        DEPS_VERSIONS+=("$current_version")
        DEPS_PURPOSES+=("$current_purpose")
        DEPS_REQUIRED+=("$current_required")
        DEPS_CHECK_CMDS+=("$current_check_cmd")
        DEPS_INSTALL_MACOS+=("$current_install_macos")
        DEPS_INSTALL_DEBIAN+=("$current_install_debian")
        DEPS_INSTALL_FEDORA+=("$current_install_fedora")
        DEPS_INSTALL_ALPINE+=("$current_install_alpine")
        DEPS_INSTALL_ALL+=("$current_install_all")
        DEPS_INSTALL_MANUAL+=("$current_install_manual")
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# DEPENDENCY CHECKING & INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════════

check_dependency() {
    local check_cmd="$1"

    if [ -z "$check_cmd" ]; then
        return 1
    fi

    # Execute check command in subshell
    if bash -c "$check_cmd" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

get_install_command() {
    local os_type="$1"
    local idx="$2"

    local install_cmd=""

    # Check for 'all' platforms first
    if [ -n "${DEPS_INSTALL_ALL[$idx]:-}" ]; then
        install_cmd="${DEPS_INSTALL_ALL[$idx]}"
    else
        case "$os_type" in
            macos)
                install_cmd="${DEPS_INSTALL_MACOS[$idx]:-}"
                ;;
            debian)
                install_cmd="${DEPS_INSTALL_DEBIAN[$idx]:-}"
                ;;
            fedora)
                install_cmd="${DEPS_INSTALL_FEDORA[$idx]:-}"
                ;;
            alpine)
                install_cmd="${DEPS_INSTALL_ALPINE[$idx]:-}"
                ;;
        esac
    fi

    # Substitute {{version}} placeholder with actual version
    if [ -n "$install_cmd" ] && [ -n "${DEPS_VERSIONS[$idx]:-}" ]; then
        install_cmd="${install_cmd//\{\{version\}\}/${DEPS_VERSIONS[$idx]}}"
    fi

    echo "$install_cmd"
}

install_dependency() {
    local name="$1"
    local install_cmd="$2"
    local manual_url="${3:-}"

    if [ -z "$install_cmd" ]; then
        log_error "No installation command available for $name on this platform"
        if [ -n "$manual_url" ]; then
            log_info "Manual installation: $manual_url"
        fi
        return 1
    fi

    log_info "Installing $name..."
    log_debug "Command: $install_cmd"

    # Execute installation
    if bash -c "$install_cmd"; then
        log_success "$name installed successfully"
        return 0
    else
        log_error "Failed to install $name"
        if [ -n "$manual_url" ]; then
            log_info "Try manual installation: $manual_url"
        fi
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

show_help() {
    sed -n '/^###############################################################################$/,/^###############################################################################$/p' "$0" | sed '1d;$d'
    exit 0
}

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --check|-c)
                CHECK_ONLY=true
                shift
                ;;
            --yes|-y)
                AUTO_YES=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    print_header "Development Environment Initializer"

    # Check requirements file exists
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_error "Requirements file not found: $REQUIREMENTS_FILE"
        exit 1
    fi

    # Detect OS
    local os_type
    os_type=$(detect_os)
    local os_name
    os_name=$(get_os_pretty_name)

    log_info "Detected OS: ${BOLD}$os_name${NC} (type: $os_type)"

    if [ "$os_type" = "unknown" ]; then
        log_warning "Unknown OS type. Installation commands may not work."
    fi

    # Parse requirements
    log_info "Reading requirements from: $REQUIREMENTS_FILE"
    parse_requirements "$REQUIREMENTS_FILE"

    local total_deps=${#DEPS_NAMES[@]}
    log_info "Found $total_deps dependencies to check"

    # Check each dependency
    print_section "Checking Dependencies"

    local missing_deps=()
    local missing_indices=()
    local installed_count=0

    for i in "${!DEPS_NAMES[@]}"; do
        local name="${DEPS_NAMES[$i]}"
        local version="${DEPS_VERSIONS[$i]}"
        local purpose="${DEPS_PURPOSES[$i]}"
        local required="${DEPS_REQUIRED[$i]}"
        local check_cmd="${DEPS_CHECK_CMDS[$i]}"

        local status_prefix=""
        if [ "$required" = "false" ]; then
            status_prefix="(optional) "
        fi

        if check_dependency "$check_cmd"; then
            log_success "${status_prefix}${BOLD}$name${NC} $version - installed"
            installed_count=$((installed_count + 1))
        else
            log_error "${status_prefix}${BOLD}$name${NC} $version - ${RED}not installed${NC}"
            log_info "  └─ $purpose"
            missing_deps+=("$name")
            missing_indices+=("$i")
        fi
    done

    # Summary
    print_section "Summary"

    echo -e "  ${GREEN}Installed:${NC}      $installed_count"
    echo -e "  ${RED}Missing:${NC}        ${#missing_deps[@]}"

    # Check-only mode
    if $CHECK_ONLY; then
        echo ""
        log_warning "Missing dependencies: ${missing_deps[*]}"
        log_info "Run without --check to install them"
        exit 1
    fi

    # Offer to install missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_section "Install Missing Dependencies"
    fi

    local install_count=0
    local failed_count=0

    for idx in "${missing_indices[@]}"; do
        local name="${DEPS_NAMES[$idx]}"
        local version="${DEPS_VERSIONS[$idx]}"
        local required="${DEPS_REQUIRED[$idx]}"
        local manual="${DEPS_INSTALL_MANUAL[$idx]:-}"

        local install_cmd
        install_cmd=$(get_install_command "$os_type" "$idx")

        echo ""
        echo -e "  ${BOLD}$name${NC} ($version)"
        echo -e "  ${CYAN}Purpose:${NC} ${DEPS_PURPOSES[$idx]}"

        if [ -z "$install_cmd" ]; then
            log_warning "No automatic installation available for this platform"
            if [ -n "$manual" ]; then
                log_info "Manual installation: $manual"
            fi
            failed_count=$((failed_count + 1))
            continue
        fi

        echo -e "  ${CYAN}Command:${NC} $install_cmd"

        if confirm "Install $name?"; then
            if install_dependency "$name" "$install_cmd" "$manual"; then
                install_count=$((install_count + 1))
            else
                failed_count=$((failed_count + 1))
            fi
        else
            log_info "Skipped $name"
            if [ "$required" = "true" ]; then
                failed_count=$((failed_count + 1))
            fi
        fi
    done

    # Summary
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_section "Installation Complete"

        echo -e "  ${GREEN}Installed:${NC}  $install_count"
        echo -e "  ${RED}Failed:${NC}     $failed_count"

        if [ $failed_count -gt 0 ]; then
            echo ""
            log_warning "Some dependencies could not be installed."
            log_info "You may need to install them manually before running ${BOLD}just setup${NC}"
            exit 1
        fi
    fi

    echo ""
    log_success "All dependencies installed!"

    # Environment Setup
    cd "$PROJECT_ROOT"
    print_section "Environment Setup"

    # Create virtual environment with specific Python version
    log_info "Creating virtual environment with Python $PYTHON_VERSION in: $PROJECT_ROOT/.venv"
    if uv venv --python "$PYTHON_VERSION" .venv; then
        log_success "Virtual environment created"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi

    # Sync project dependencies from lockfile
    log_info "Installing project dependencies (including dev dependencies)..."
    if uv sync --frozen --all-extras; then
        log_success "Project dependencies installed"
    else
        log_error "Failed to install project dependencies"
        exit 1
    fi

    # Setup hooks
    log_info "Setting up hooks..."
    if git config core.hooksPath .githooks && chmod +x .githooks/pre-commit 2>/dev/null; then
        log_success "Git hooks path configured"
    else
        log_warning "Could not configure Git hooks path (may not exist yet)"
    fi

    if uv run pre-commit install-hooks 2>/dev/null; then
        log_success "Pre-commit hooks installed"
    else
        log_warning "Pre-commit hooks installation failed (may not be in dependencies)"
    fi

    # Docker/Podman authentication
    print_section "Container Registry Authentication"

    local DOCKER_CONFIG="$HOME/.docker/config.json"
    if [ ! -f "$DOCKER_CONFIG" ]; then
        log_info "Container registry config not found. Setting up GitHub Container Registry authentication..."

        mkdir -p "$HOME/.docker"

        if [ -t 0 ]; then
            # Interactive mode
            read -r -p "Enter GitHub Username: " GITHUB_USER
            read -r -s -p "Enter GitHub Token: " GITHUB_TOKEN
            echo

            if echo "$GITHUB_TOKEN" | podman login ghcr.io -u "$GITHUB_USER" --password-stdin; then
                log_success "GitHub Container Registry authentication configured"
            else
                log_error "Failed to authenticate with GitHub Container Registry"
            fi
        else
            log_warning "Non-interactive mode: Skipping GHCR authentication"
            log_info "Run manually: podman login ghcr.io"
        fi
    else
        log_info "Container registry config exists at $DOCKER_CONFIG"
        if podman login ghcr.io --get-login >/dev/null 2>&1; then
            log_success "GitHub Container Registry authentication verified"
        else
            log_warning "Could not verify authentication"
            log_info "If you encounter authentication issues, run: podman login ghcr.io"
        fi
    fi

    # Verify GitHub CLI authentication
    if gh auth status >/dev/null 2>&1; then
        log_success "GitHub CLI authentication verified"
    else
        log_warning "GitHub CLI is not authenticated."
        log_info "Run 'gh auth login' to authenticate with GitHub."
    fi

    # Done
    echo ""
    print_section "Setup Complete"
    log_success "Environment setup complete!"
    echo ""
    log_info "Run ${BOLD}just${NC} to see available commands."

}

# Run main function
main "$@"
