#!/usr/bin/env bash
###############################################################################
# devc-remote.sh - Remote devcontainer orchestrator
#
# Starts a devcontainer on a remote host via SSH and optionally opens an IDE.
# Handles SSH connectivity, pre-flight checks, container state detection,
# compose lifecycle, and optional Tailscale auth key injection.
#
# USAGE:
#   ./scripts/devc-remote.sh [options] <ssh-host>[:<remote-path>]
#   ./scripts/devc-remote.sh --help
#
# Options:
#   --yes, -y         Auto-accept prompts (reuse running containers)
#   --open <mode>     How to connect after compose up:
#                       cursor  - open Cursor via devcontainer protocol (default)
#                       code    - open VS Code via devcontainer protocol
#                       ssh     - wait for Tailscale, print hostname (for SSH clients)
#                       none    - infra only, no IDE
#
# Tailscale key injection (opt-in):
#   When TS_CLIENT_ID and TS_CLIENT_SECRET are set in the local environment,
#   generates an ephemeral auth key via the Tailscale API and injects it
#   into the remote docker-compose.local.yaml before compose up.
#
# Examples:
#   ./scripts/devc-remote.sh myserver
#   ./scripts/devc-remote.sh --open none myserver:/home/user/repo
#   ./scripts/devc-remote.sh --open ssh myserver
#   ./scripts/devc-remote.sh --yes --open code user@host:/opt/projects/myrepo
#
# Part of #70. See issues #152, #230, #231 for design.
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
    REMOTE_PATH="~"
    YES_MODE=0
    OPEN_MODE="cursor"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_help
                ;;
            --yes|-y)
                # shellcheck disable=SC2034
                YES_MODE=1
                shift
                ;;
            --open)
                shift
                OPEN_MODE="${1:-cursor}"
                if [[ "$OPEN_MODE" != "cursor" && "$OPEN_MODE" != "code" && "$OPEN_MODE" != "ssh" && "$OPEN_MODE" != "none" ]]; then
                    log_error "--open must be cursor, code, ssh, or none"
                    exit 1
                fi
                shift
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
                # Parse SSH-style format: user@host:path or host:path
                if [[ "$1" =~ ^([^:]+):(.+)$ ]]; then
                    SSH_HOST="${BASH_REMATCH[1]}"
                    REMOTE_PATH="${BASH_REMATCH[2]}"
                else
                    SSH_HOST="$1"
                    # Default to ~ (expanded by remote shell) if no path specified
                    REMOTE_PATH="~"
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$SSH_HOST" ]]; then
        log_error "Missing required argument: <ssh-host>[:<remote-path>]"
        echo "Use --help for usage information"
        exit 1
    fi
}

detect_editor_cli() {
    if [[ "$OPEN_MODE" == "none" || "$OPEN_MODE" == "ssh" ]]; then
        EDITOR_CLI=""
        return
    fi

    if [[ "$OPEN_MODE" == "cursor" ]]; then
        if command -v cursor &>/dev/null; then
            EDITOR_CLI="cursor"
        else
            log_error "cursor CLI not found. Install Cursor and enable the shell command, or use --open code|ssh|none."
            exit 1
        fi
    elif [[ "$OPEN_MODE" == "code" ]]; then
        if command -v code &>/dev/null; then
            EDITOR_CLI="code"
        else
            log_error "code CLI not found. Install VS Code and enable the shell command, or use --open cursor|ssh|none."
            exit 1
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# TAILSCALE KEY INJECTION (opt-in via TS_CLIENT_ID + TS_CLIENT_SECRET)
# ═══════════════════════════════════════════════════════════════════════════════

inject_tailscale_key() {
    # Skip if no OAuth credentials
    if [[ -z "${TS_CLIENT_ID:-}" || -z "${TS_CLIENT_SECRET:-}" ]]; then
        return 0
    fi

    # Check if key already set on remote
    # shellcheck disable=SC2029
    if ssh "$SSH_HOST" "grep -q 'TAILSCALE_AUTHKEY' '$REMOTE_PATH/.devcontainer/docker-compose.local.yaml' 2>/dev/null"; then
        log_info "Tailscale: auth key already configured on remote"
        return 0
    fi

    # Verify local prerequisites
    if ! command -v curl &>/dev/null || ! command -v jq &>/dev/null; then
        log_warning "Tailscale: curl and jq required for key generation, skipping"
        return 0
    fi

    log_info "Tailscale: generating ephemeral auth key..."

    # Get OAuth access token
    local token_response token
    token_response=$(curl -s -f \
        -d "client_id=$TS_CLIENT_ID" \
        -d "client_secret=$TS_CLIENT_SECRET" \
        "https://api.tailscale.com/api/v2/oauth/token" 2>&1) || {
        log_warning "Tailscale: failed to get OAuth token, skipping"
        return 0
    }
    token=$(echo "$token_response" | jq -r '.access_token // empty')
    if [[ -z "$token" ]]; then
        log_warning "Tailscale: empty access token, skipping"
        return 0
    fi

    # Create ephemeral, non-reusable auth key
    local key_response auth_key
    key_response=$(curl -s -f -X POST \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d '{
            "capabilities": {
                "devices": {
                    "create": {
                        "reusable": false,
                        "ephemeral": true,
                        "tags": ["tag:devcontainer"]
                    }
                }
            }
        }' \
        "https://api.tailscale.com/api/v2/tailnet/-/keys" 2>&1) || {
        log_warning "Tailscale: failed to create auth key, skipping"
        return 0
    }
    auth_key=$(echo "$key_response" | jq -r '.key // empty')
    if [[ -z "$auth_key" ]]; then
        local err_msg
        err_msg=$(echo "$key_response" | jq -r '.message // empty')
        log_warning "Tailscale: API error: ${err_msg:-unknown}, skipping"
        return 0
    fi

    # Inject into remote docker-compose.local.yaml
    # shellcheck disable=SC2029
    ssh "$SSH_HOST" "bash -s" "$REMOTE_PATH" "$auth_key" << 'INJECT_EOF'
REPO_PATH="$1"
AUTH_KEY="$2"
LOCAL_YAML="$REPO_PATH/.devcontainer/docker-compose.local.yaml"

# Create if missing
if [ ! -f "$LOCAL_YAML" ]; then
    cat > "$LOCAL_YAML" << 'YAML'
services:
  devcontainer:
    environment:
      - TAILSCALE_AUTHKEY=PLACEHOLDER
YAML
fi

# If file has 'services: {}' (empty), replace with proper structure
if grep -q 'services: {}' "$LOCAL_YAML"; then
    cat > "$LOCAL_YAML" << YAML
services:
  devcontainer:
    environment:
      - TAILSCALE_AUTHKEY=${AUTH_KEY}
YAML
elif grep -q 'TAILSCALE_AUTHKEY' "$LOCAL_YAML"; then
    sed -i "s|TAILSCALE_AUTHKEY=.*|TAILSCALE_AUTHKEY=${AUTH_KEY}|" "$LOCAL_YAML"
elif grep -q 'environment:' "$LOCAL_YAML"; then
    sed -i "/environment:/a\\      - TAILSCALE_AUTHKEY=${AUTH_KEY}" "$LOCAL_YAML"
elif grep -q 'devcontainer:' "$LOCAL_YAML"; then
    sed -i "/devcontainer:/a\\    environment:\\n      - TAILSCALE_AUTHKEY=${AUTH_KEY}" "$LOCAL_YAML"
else
    cat > "$LOCAL_YAML" << YAML
services:
  devcontainer:
    environment:
      - TAILSCALE_AUTHKEY=${AUTH_KEY}
YAML
fi
INJECT_EOF

    log_success "Tailscale: ephemeral auth key injected into remote compose"
}

check_ssh() {
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$SSH_HOST" true 2>/dev/null; then
        log_error "Cannot connect to $SSH_HOST. Check your SSH config and network."
        exit 1
    fi
}

remote_preflight() {
    local preflight_output
    # shellcheck disable=SC2029
    preflight_output=$(ssh "$SSH_HOST" "bash -s" "$REMOTE_PATH" << 'REMOTEEOF'
REPO_PATH="${1:-$HOME}"
if command -v podman &>/dev/null; then
    echo "RUNTIME=podman"
elif command -v docker &>/dev/null; then
    echo "RUNTIME=docker"
else
    echo "RUNTIME="
fi
if (command -v podman &>/dev/null && podman compose version &>/dev/null) || \
   (command -v docker &>/dev/null && docker compose version &>/dev/null); then
    echo "COMPOSE_AVAILABLE=1"
else
    echo "COMPOSE_AVAILABLE=0"
fi
if [ -d "$REPO_PATH" ]; then
    echo "REPO_PATH_EXISTS=1"
else
    echo "REPO_PATH_EXISTS=0"
fi
if [ -d "$REPO_PATH/.devcontainer" ]; then
    echo "DEVCONTAINER_EXISTS=1"
else
    echo "DEVCONTAINER_EXISTS=0"
fi
AVAIL_GB=$(df -BG "$REPO_PATH" 2>/dev/null | awk 'NR==2 {gsub(/G/,""); print $4}')
echo "DISK_AVAILABLE_GB=${AVAIL_GB:-0}"
if [ "$(uname -s)" = "Darwin" ]; then
    echo "OS_TYPE=macos"
else
    echo "OS_TYPE=linux"
fi
REMOTEEOF
    )

    while IFS= read -r line; do
        [[ "$line" =~ ^([A-Z_]+)=(.*)$ ]] || continue
        case "${BASH_REMATCH[1]}" in
            RUNTIME) RUNTIME="${BASH_REMATCH[2]}" ;;
            COMPOSE_AVAILABLE) COMPOSE_AVAILABLE="${BASH_REMATCH[2]}" ;;
            REPO_PATH_EXISTS) REPO_PATH_EXISTS="${BASH_REMATCH[2]}" ;;
            DEVCONTAINER_EXISTS) DEVCONTAINER_EXISTS="${BASH_REMATCH[2]}" ;;
            DISK_AVAILABLE_GB) DISK_AVAILABLE_GB="${BASH_REMATCH[2]}" ;;
            OS_TYPE) OS_TYPE="${BASH_REMATCH[2]}" ;;
        esac
    done <<< "$preflight_output"

    if [[ -z "${RUNTIME:-}" ]]; then
        log_error "No container runtime found on $SSH_HOST. Install podman or docker."
        exit 1
    fi
    if [[ "$RUNTIME" == "podman" ]]; then
        COMPOSE_CMD="podman compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    if [[ "${COMPOSE_AVAILABLE:-0}" != "1" ]]; then
        log_error "Compose not available on $SSH_HOST. Install docker-compose or podman-compose."
        exit 1
    fi
    if [[ "${REPO_PATH_EXISTS:-0}" != "1" ]]; then
        log_error "Repository not found at $REMOTE_PATH on $SSH_HOST."
        exit 1
    fi
    if [[ "${DEVCONTAINER_EXISTS:-0}" != "1" ]]; then
        log_error "No .devcontainer/ found in $REMOTE_PATH. Is this a devcontainer-enabled project?"
        exit 1
    fi
    if [[ "${DISK_AVAILABLE_GB:-0}" -lt 2 ]] 2>/dev/null; then
        log_warning "Low disk space on $SSH_HOST (${DISK_AVAILABLE_GB:-0}GB). At least 2GB recommended."
    fi
    if [[ "${OS_TYPE:-}" == "macos" ]]; then
        log_warning "Remote host is macOS. Devcontainer support may be limited."
    fi
}

remote_compose_up() {
    local ps_output state health
    # shellcheck disable=SC2029
    ps_output=$(ssh "$SSH_HOST" "cd $REMOTE_PATH && $COMPOSE_CMD ps --format json 2>/dev/null" || true)
    state=$(echo "$ps_output" | grep -o '"State":"[^"]*"' | head -1 | cut -d'"' -f4)
    health=$(echo "$ps_output" | grep -o '"Health":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [[ "$state" == "running" && "${health:-}" == "healthy" ]]; then
        log_success "Devcontainer already running on $SSH_HOST. Opening..."
    else
        log_info "Starting devcontainer on $SSH_HOST..."
        # shellcheck disable=SC2029
        if ! ssh "$SSH_HOST" "cd $REMOTE_PATH && $COMPOSE_CMD up -d"; then
            log_error "Failed to start devcontainer on $SSH_HOST."
            log_error "Debug with: ssh $SSH_HOST 'cd $REMOTE_PATH && $COMPOSE_CMD logs'"
            exit 1
        fi
        sleep 2
    fi
}

read_workspace_folder() {
    # Read workspaceFolder from devcontainer.json on remote host
    local folder
    # shellcheck disable=SC2029
    folder=$(ssh "$SSH_HOST" \
        "grep -o '\"workspaceFolder\"[[:space:]]*:[[:space:]]*\"[^\"]*\"' \
         ${REMOTE_PATH}/.devcontainer/devcontainer.json 2>/dev/null" \
        | sed 's/.*: *"//;s/"//' || echo "/workspace")
    echo "${folder:-/workspace}"
}

open_editor() {
    local container_workspace uri
    container_workspace=$(read_workspace_folder)

    # Build URI using Python helper
    uri=$(python3 "$SCRIPT_DIR/devc_remote_uri.py" \
        "$REMOTE_PATH" \
        "$SSH_HOST" \
        "$container_workspace")

    "$EDITOR_CLI" --folder-uri "$uri"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TAILSCALE WAIT + SSH OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

wait_for_tailscale() {
    if ! command -v tailscale &>/dev/null; then
        log_error "tailscale CLI not found locally. Install Tailscale to use --open ssh."
        exit 1
    fi

    # Derive expected hostname pattern from devcontainer.json name field
    local devc_name
    # shellcheck disable=SC2029
    devc_name=$(ssh "$SSH_HOST" \
        "python3 -c \"import json,sys; print(json.load(sys.stdin).get('name',''))\" \
         < ${REMOTE_PATH}/.devcontainer/devcontainer.json 2>/dev/null" || true)
    devc_name="${devc_name:-devc}"

    log_info "Tailscale: waiting for container to join tailnet (pattern: *${devc_name}*)..."

    local ip hostname
    for _ in $(seq 1 30); do
        # Query local tailscale for peers matching the devc hostname pattern
        local ts_status
        ts_status=$(tailscale status --json 2>/dev/null || true)
        if [[ -n "$ts_status" ]]; then
            # Find an online peer whose hostname contains the devc name
            local match
            match=$(echo "$ts_status" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for peer in (data.get('Peer') or {}).values():
    if peer.get('Online') and '${devc_name}' in peer.get('HostName', ''):
        ips = peer.get('TailscaleIPs', [])
        print(peer['HostName'] + ' ' + (ips[0] if ips else ''))
        break
" 2>/dev/null || true)

            if [[ -n "$match" ]]; then
                hostname="${match%% *}"
                ip="${match#* }"
                log_success "Tailscale: container online as ${hostname} (${ip})"
                # Output connection info to stdout (for scripting)
                echo ""
                echo "Connect via:"
                echo "  ssh root@${hostname}"
                echo "  ssh root@${ip}"
                echo ""
                echo "Cursor:  cursor --remote ssh-remote+root@${hostname} $(read_workspace_folder)"
                echo "VS Code: code --remote ssh-remote+root@${hostname} $(read_workspace_folder)"
                return 0
            fi
        fi
        sleep 2
    done

    log_warning "Tailscale: container did not appear on tailnet within 60s"
    log_warning "Check that TAILSCALE_AUTHKEY is set and Tailscale ACLs allow SSH"
    return 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    parse_args "$@"

    detect_editor_cli
    case "$OPEN_MODE" in
        cursor|code) log_success "IDE: $EDITOR_CLI" ;;
        ssh)         log_info "Mode: SSH (wait for Tailscale, print connection info)" ;;
        none)        log_info "Mode: infra only (no IDE)" ;;
    esac

    log_info "Checking SSH connectivity to $SSH_HOST..."
    check_ssh
    log_success "SSH connection OK"

    log_info "Running pre-flight checks on $SSH_HOST..."
    remote_preflight
    log_success "Pre-flight OK (runtime: $RUNTIME)"

    inject_tailscale_key

    remote_compose_up

    case "$OPEN_MODE" in
        cursor|code)
            open_editor
            log_success "Done — opened $EDITOR_CLI for $SSH_HOST:$REMOTE_PATH"
            ;;
        ssh)
            wait_for_tailscale
            ;;
        none)
            log_success "Done — devcontainer running on $SSH_HOST:$REMOTE_PATH"
            ;;
    esac
}

main "$@"
