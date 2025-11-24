#!/usr/bin/env bash
# Build container image
# Usage: build.sh <version> [REPO] [NATIVE_PLATFORM]

set -e

VERSION="${1:-dev}"
REPO="${2:-${TEST_REGISTRY:-ghcr.io/vig-os/devcontainer}}"
# Remove trailing slash from REPO to avoid invalid tag format (e.g., localhost:5000/test/:tag)
REPO="${REPO%/}"

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

BUILD_DIR="build"
BUILD_VERSION="$VERSION"
BUILD_DATE=""
VCS_REF=""

echo "Building $REPO:$VERSION..."

# Create and clear build folder
echo "Preparing build folder..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy Containerfile and assets to build folder
echo "Copying Containerfile and assets to build folder..."
cp Containerfile "$BUILD_DIR/"
cp -r assets "$BUILD_DIR/"

# Modify assets if needed (replace version placeholders)
if [ -d "$BUILD_DIR/assets/workspace" ]; then
	echo "Replacing {{IMAGE_TAG}} with $BUILD_VERSION in template files..."
	find "$BUILD_DIR/assets/workspace" -type f -exec sed -i "s|{{IMAGE_TAG}}|$BUILD_VERSION|g" {} \; 2>/dev/null || true
fi

# Build the image from build folder
echo "Building image from build folder..."
if ! podman build --platform "$NATIVE_PLATFORM" \
	--build-arg BUILD_DATE="$BUILD_DATE" \
	--build-arg VCS_REF="$VCS_REF" \
	--build-arg IMAGE_TAG="$BUILD_VERSION" \
	-t "$REPO:$BUILD_VERSION" \
	-f "$BUILD_DIR/Containerfile" \
	"$BUILD_DIR"; then
	echo "❌ Build failed"
	exit 1
fi

echo "✓ Built local development image $REPO:$BUILD_VERSION ($NATIVE_PLATFORM)"
