#!/bin/bash

# Initialize script - runs on host before container starts
# This script is called from initializeCommand in devcontainer.json

set -euo pipefail

echo "Initializing devcontainer setup..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/copy-host-user-conf.sh"

echo "Initialization complete"
