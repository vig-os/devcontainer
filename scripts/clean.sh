#!/usr/bin/env bash
# Clean (remove) container image
# Usage: clean.sh [version] [REPO]

set -e

VERSION="${1:-dev}"
REPO="${2:-${TEST_REGISTRY:-ghcr.io/vig-os/devcontainer}}"
# Strip trailing slash if present
REPO="${REPO%/}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

IMAGE_NAME="$REPO:$VERSION"

if podman images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}$"; then
	echo "Removing image $IMAGE_NAME..."
	if ! podman rmi -f "$IMAGE_NAME" 2>/dev/null; then
		echo "⚠️  Failed to remove $IMAGE_NAME"
		exit 1
	fi
	echo "✓ Removed image $IMAGE_NAME"
else
	echo "⚠️  Image $IMAGE_NAME does not exist"
fi
