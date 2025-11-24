#!/bin/bash

# Initialize script - runs on host before container starts
# This script is called from initializeCommand

# Set error handling, fail on any error during script execution
set -euo pipefail

echo "Initializing devcontainer setup..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call copy-host-user-conf.sh from the same directory
"$SCRIPT_DIR/scripts/copy-host-user-conf.sh"

echo "Initialization complete"
