#!/bin/bash

# Post-attach script - runs each time a tool attaches to the container.
# This script is called from postAttachCommand in devcontainer.json.
#
# Only lightweight checks belong here (no file copies, no installs):
#   - Verify SSH agent has the signing key
#   - Verify GitHub CLI is authenticated

set -euo pipefail

echo "Running post-attach checks..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/verify-auth.sh"

echo "Post-attach checks complete"
