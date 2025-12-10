#!/bin/bash

# Post-create script - runs when container is created for the first time
# This script is called from postCreateCommand in devcontainer.json

set -euo pipefail

echo "Running post-create setup..."

# User specific setup
# Add your custom setup commands here to install any dependencies or tools needed for your project

echo "Post-create setup complete"
