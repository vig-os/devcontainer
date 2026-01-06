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

# Sync Python dependencies if pyproject.toml changed (fast, only installs missing deps)
# Use --no-install-project since new projects may not have source code yet
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    uv sync --all-extras --no-install-project --quiet
fi

echo "Post-attach setup complete"
