#!/bin/bash

# Post-create script - runs when container is created for the first time
# This script is called from postCreateCommand in devcontainer.json

set -euo pipefail

echo "Running post-create setup..."

# Set venv prompt
sed -i 's/template-project/{{SHORT_NAME}}/g' /root/assets/workspace/.venv/bin/activate

# Sync Python dependencies (fast if nothing changed from pre-built venv)
# Use --no-install-project since new projects may not have source code yet
if [[ -f "pyproject.toml" ]]; then
    echo "Syncing Python dependencies..."
    uv sync --all-extras --no-install-project
fi

# User specific setup
# Add your custom setup commands here to install any dependencies or tools needed for your project

echo "Post-create setup complete"
