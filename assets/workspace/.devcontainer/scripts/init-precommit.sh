#!/bin/bash
set -euo pipefail

# Run only if pre-commit hooks are not already installed
if [ -f "/workspace/.pre-commit-cache" ]; then
	echo "Pre-commit hooks already installed, skipping"
	exit 0
fi

if [ -f "/workspace/.pre-commit-config.yaml" ]; then
    echo "Setting up pre-commit hooks (this may take a few minutes)..."
    cd /workspace
    pre-commit install-hooks || {
        echo "⚠️  Pre-commit install failed"
        echo "    You can manually run 'pre-commit install-hooks' later"
        return 1
    }
    echo "Pre-commit hooks installed successfully"
else
    echo "No .pre-commit-config.yaml found, skipping"
fi
