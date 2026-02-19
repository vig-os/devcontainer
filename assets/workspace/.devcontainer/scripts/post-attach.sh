#!/bin/bash

# Post-attach script - runs each time a tool attaches to the container.
# This script is called from postAttachCommand in devcontainer.json.
#
# Lightweight checks and dependency sync:
#   - Verify SSH agent has the signing key
#   - Verify GitHub CLI is authenticated
#   - Sync dependencies (fast no-op if nothing changed)

set -euo pipefail

echo "Running post-attach checks..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/workspace/{{SHORT_NAME}}"

"$SCRIPT_DIR/verify-auth.sh"

# Sync dependencies (fast no-op if nothing changed)
echo "Syncing dependencies..."
just --justfile "$PROJECT_ROOT/justfile" --working-directory "$PROJECT_ROOT" sync

echo "Post-attach checks complete"
