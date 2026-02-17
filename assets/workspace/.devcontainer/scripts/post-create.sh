#!/bin/bash

# Post-create script - runs once when container is created for the first time.
# This script is called from postCreateCommand in devcontainer.json.
#
# All one-time setup belongs here:
#   - Git repo init, config, hooks
#   - SSH key + allowed-signers placement
#   - GitHub CLI config + authentication
#   - Pre-commit hook installation
#   - Python dependency sync

set -euo pipefail

echo "Running post-create setup..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/workspace/{{SHORT_NAME}}"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "Error: Project directory $PROJECT_ROOT does not exist"
    exit 1
fi

# Set venv prompt
sed -i 's/template-project/{{SHORT_NAME}}/g' /root/assets/workspace/.venv/bin/activate

# One-time setup: git repo, config, hooks, gh auth
"$SCRIPT_DIR/init-git.sh"
"$SCRIPT_DIR/setup-git-conf.sh"
"$SCRIPT_DIR/init-precommit.sh"

# Sync Python dependencies (fast if nothing changed from pre-built venv)
# Use --no-install-project since new projects may not have source code yet
if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    echo "Syncing Python dependencies..."
    uv sync --all-extras --no-install-project
fi

# User specific setup
# Add your custom setup commands here to install any dependencies or tools needed for your project

echo "Post-create setup complete"
