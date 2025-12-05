#!/bin/bash

# Post-attach script - runs when container is attached
# This script is called from postAttachCommand in devcontainer.json

set -euo pipefail

echo "Running post-attach setup..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/workspace/{{SHORT_NAME}}"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "Error: Project directory $PROJECT_ROOT does not exist"
    exit 1
fi

"$SCRIPT_DIR/init-git.sh"
"$SCRIPT_DIR/setup-git-conf.sh"
"$SCRIPT_DIR/init-precommit.sh"

echo "Post-attach setup complete"
