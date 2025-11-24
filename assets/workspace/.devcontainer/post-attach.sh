#!/bin/bash

# Post-attach script - runs when container is attached
# This script is called from postAttachCommand

# Set error handling, fail on any error during script execution
set -euo pipefail

echo "Running post-attach setup..."

SCRIPTS_DIR="/workspace/.devcontainer/scripts"

# Initialize git repository if needed
"$SCRIPTS_DIR/init-git.sh"

# Set up git configuration (includes GitHub CLI config and authentication)
"$SCRIPTS_DIR/setup-git-conf.sh"

# Install pre-commit hooks
"$SCRIPTS_DIR/init-precommit.sh"

echo "Post-attach setup complete"
