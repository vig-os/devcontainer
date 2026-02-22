#!/usr/bin/env bash
###############################################################################
# devc-remote.sh - Remote devcontainer orchestrator
#
# Starts a devcontainer on a remote host via SSH and opens Cursor/VS Code.
# Handles SSH connectivity, pre-flight checks, container state detection,
# and compose lifecycle. URI construction delegated to Python helper.
#
# USAGE:
#   ./scripts/devc-remote.sh <ssh-host> [--path <remote-path>]
#   ./scripts/devc-remote.sh --help
#
# Part of #70. See issue #152 for design.
###############################################################################

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# shellcheck disable=SC2034
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING (matches init.sh patterns)
# ═══════════════════════════════════════════════════════════════════════════════

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

show_help() {
    sed -n '/^###############################################################################$/,/^###############################################################################$/p' "$0" | sed '1d;$d'
    exit 0
}

parse_args() {
    SSH_HOST=""
    REMOTE_PATH="$HOME"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_help
                ;;
            --path)
                if [[ $# -lt 2 ]]; then
                    log_error "Missing value for --path"
                    exit 1
                fi
                # shellcheck disable=SC2034
                REMOTE_PATH="$2"
                shift 2
                ;;
            -*)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
            *)
                if [[ -n "$SSH_HOST" ]]; then
                    log_error "Unexpected argument: $1"
                    exit 1
                fi
                SSH_HOST="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$SSH_HOST" ]]; then
        log_error "Missing required argument: <ssh-host>"
        echo "Use --help for usage information"
        exit 1
    fi
}

detect_editor_cli() {
    if command -v cursor &>/dev/null; then
        # shellcheck disable=SC2034
        EDITOR_CLI="cursor"
    elif command -v code &>/dev/null; then
        # shellcheck disable=SC2034
        EDITOR_CLI="code"
    else
        log_error "Neither cursor nor code CLI found. Install Cursor or VS Code and enable the shell command."
        exit 1
    fi
}

check_ssh() {
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$SSH_HOST" true 2>/dev/null; then
        log_error "Cannot connect to $SSH_HOST. Check your SSH config and network."
        exit 1
    fi
}

remote_preflight() {
    :
}

remote_compose_up() {
    :
}

open_editor() {
    :
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    parse_args "$@"
    detect_editor_cli
    check_ssh
    remote_preflight
    remote_compose_up
    open_editor
}

main "$@"
