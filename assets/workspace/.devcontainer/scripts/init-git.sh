#!/bin/bash
set -euo pipefail

echo "Checking git repository status..."

# Check if we're already in a git repository
if [ -d ".git" ]; then
    echo "Git repository already initialized"
else
    echo "No git repository found, initializing..."
    git init
    git checkout -b main 2>/dev/null || git branch -M main
    echo "Git repository initialized with main branch"
fi
