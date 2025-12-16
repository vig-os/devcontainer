#!/bin/bash

# Post-create script - runs when container is created for the first time
# This script is called from postCreateCommand in devcontainer.json

set -euo pipefail

echo "Running post-create setup..."

# Auto-login to GitHub Container Registry (ghcr.io) using GitHub token
# This enables pushing/pulling images without manual authentication
GH_HOSTS_FILE="$HOME/.config/gh/hosts.yml"
if [ -f "$GH_HOSTS_FILE" ]; then
    echo "Authenticating to ghcr.io using GitHub token..."

    # Extract token from hosts.yml (format: oauth_token: gho_xxx)
    TOKEN=$(grep -E "^\s*oauth_token:" "$GH_HOSTS_FILE" | head -1 | awk '{print $2}')

    if [ -n "$TOKEN" ]; then
        # Extract username from hosts.yml
        USERNAME=$(grep -E "^\s*user:" "$GH_HOSTS_FILE" | head -1 | awk '{print $2}')

        if [ -n "$USERNAME" ]; then
            # Login to GitHub Container Registry
            if echo "$TOKEN" | podman login ghcr.io -u "$USERNAME" --password-stdin 2>/dev/null; then
                echo "✅ Successfully logged in to ghcr.io as $USERNAME"
            else
                echo "⚠️  Failed to login to ghcr.io (socket may not be available yet)"
                echo "   You can manually login later with: podman login ghcr.io"
            fi
        else
            echo "⚠️  No username found in $GH_HOSTS_FILE"
        fi
    else
        echo "⚠️  No GitHub token found in $GH_HOSTS_FILE"
    fi
else
    echo "⚠️  GitHub CLI config not found at $GH_HOSTS_FILE"
    echo "   Run 'gh auth login' or add token manually to login to ghcr.io"
fi


# User specific setup
# Add your custom setup commands here to install any dependencies or tools needed for your project

echo "Installing make..."
apt-get update && apt-get install -y make podman docker-compose


echo "Post-create setup complete"
