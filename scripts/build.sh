#!/usr/bin/env bash
# Build container image
# Usage: build.sh <version> [REPO] [NATIVE_PLATFORM]

set -e

VERSION="${1:-dev}"
REPO="${2:-${TEST_REGISTRY:-ghcr.io/vig-os/devcontainer}}"

# Detect native platform
NATIVE_ARCH=$(uname -m)
if [ "$NATIVE_ARCH" = "arm64" ] || [ "$NATIVE_ARCH" = "aarch64" ]; then
	NATIVE_PLATFORM="${3:-linux/arm64}"
else
	NATIVE_PLATFORM="${3:-linux/amd64}"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Building $REPO:$VERSION..."

# Backup and replace template
"$SCRIPT_DIR/backup_template.sh" "$VERSION"

BUILD_VERSION="$VERSION"
BUILD_DATE=""
VCS_REF=""

# Build the image
if ! podman build --platform "$NATIVE_PLATFORM" \
	--build-arg BUILD_DATE="$BUILD_DATE" \
	--build-arg VCS_REF="$VCS_REF" \
	--build-arg IMAGE_TAG="$BUILD_VERSION" \
	-t "$REPO:$BUILD_VERSION" -f Containerfile .; then
	echo "❌ Build failed"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
fi

# Restore template
"$SCRIPT_DIR/restore_template.sh"

echo "✓ Built local development image $REPO:$BUILD_VERSION ($NATIVE_PLATFORM)"
