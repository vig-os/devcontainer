#!/usr/bin/env bash
# Build container image
# Usage: build.sh <version> [REPO] [NATIVE_PLATFORM]

set -e

echo "🔍 DEBUG: Script started"
echo "🔍 DEBUG: Raw arguments: $*"

# Optional flag: --no-cache (must be first arg to keep positional semantics)
NO_CACHE=0
if [ "${1:-}" = "--no-cache" ]; then
	NO_CACHE=1
	shift
	echo "🔍 DEBUG: --no-cache flag detected"
fi

VERSION="${1:-dev}"
REPO="${2:-${TEST_REGISTRY:-ghcr.io/vig-os/devcontainer}}"
echo "🔍 DEBUG: VERSION='$VERSION'"
echo "🔍 DEBUG: REPO (before cleanup)='$REPO'"

# Remove trailing slash from REPO to avoid invalid tag format (e.g., localhost:5000/test/:tag)
REPO="${REPO%/}"
echo "🔍 DEBUG: REPO (after cleanup)='$REPO'"

# Detect native platform
NATIVE_ARCH=$(uname -m)
echo "🔍 DEBUG: Detected architecture: $NATIVE_ARCH"

if [ "$NATIVE_ARCH" = "arm64" ] || [ "$NATIVE_ARCH" = "aarch64" ]; then
	NATIVE_PLATFORM="${3:-linux/arm64}"
else
	NATIVE_PLATFORM="${3:-linux/amd64}"
fi
echo "🔍 DEBUG: NATIVE_PLATFORM='$NATIVE_PLATFORM'"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "🔍 DEBUG: SCRIPT_DIR='$SCRIPT_DIR'"
echo "🔍 DEBUG: PROJECT_ROOT='$PROJECT_ROOT'"

# Source utilities
# shellcheck source=scripts/utils.sh
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"
echo "🔍 DEBUG: Changed to PROJECT_ROOT"

BUILD_DIR="build"
BUILD_VERSION="$VERSION"
BUILD_DATE=""
VCS_REF=""
echo "🔍 DEBUG: BUILD_DIR='$BUILD_DIR'"
echo "🔍 DEBUG: BUILD_VERSION='$BUILD_VERSION'"
echo "🔍 DEBUG: BUILD_DATE='$BUILD_DATE'"
echo "🔍 DEBUG: VCS_REF='$VCS_REF'"

echo "Building $REPO:$VERSION..."

# Create and clear build folder
echo "Preparing build folder..."
echo "🔍 DEBUG: Removing existing build directory..."
rm -rf "$BUILD_DIR"
echo "🔍 DEBUG: Creating build directory..."
mkdir -p "$BUILD_DIR"
echo "🔍 DEBUG: Build directory created"

# Copy Containerfile and assets to build folder
echo "Copying Containerfile and assets to build folder..."
echo "🔍 DEBUG: Copying Containerfile..."
cp Containerfile "$BUILD_DIR/"
echo "🔍 DEBUG: Copying assets directory..."
cp -r assets "$BUILD_DIR/"
echo "🔍 DEBUG: Files copied successfully"

# Modify assets if needed (replace version placeholders)
if [ -d "$BUILD_DIR/assets/workspace" ]; then
	echo "Replacing {{IMAGE_TAG}} with $BUILD_VERSION in template files..."
	echo "🔍 DEBUG: Searching for files in $BUILD_DIR/assets/workspace..."
	echo "🔍 DEBUG: Using $(get_sed_type) sed syntax"

	find "$BUILD_DIR/assets/workspace" -type f -print0 | while IFS= read -r -d '' file; do
		sed_inplace "s|{{IMAGE_TAG}}|$BUILD_VERSION|g" "$file"
	done

	echo "🔍 DEBUG: Template replacement completed"
	echo "🔍 DEBUG: Verifying replacements..."
	if grep -r "{{IMAGE_TAG}}" "$BUILD_DIR/assets/workspace" 2>/dev/null; then
		echo "⚠️  WARNING: Some {{IMAGE_TAG}} placeholders were not replaced!"
	else
		echo "🔍 DEBUG: All {{IMAGE_TAG}} placeholders successfully replaced"
	fi
else
	echo "🔍 DEBUG: $BUILD_DIR/assets/workspace does not exist, skipping template replacement"
fi

# Build the image from build folder
echo "Building image from build folder..."
echo "🔍 DEBUG: Running podman build with:"
echo "🔍 DEBUG:   Platform: $NATIVE_PLATFORM"
echo "🔍 DEBUG:   BUILD_DATE: $BUILD_DATE"
echo "🔍 DEBUG:   VCS_REF: $VCS_REF"
echo "🔍 DEBUG:   IMAGE_TAG: $BUILD_VERSION"
echo "🔍 DEBUG:   Tag: $REPO:$BUILD_VERSION"
echo "🔍 DEBUG:   Containerfile: $BUILD_DIR/Containerfile"
echo "🔍 DEBUG:   Build context: $BUILD_DIR"
if [ "$NO_CACHE" -eq 1 ]; then
	echo "🔍 DEBUG:   No cache: enabled"
fi

BUILD_CACHE_ARGS=()
if [ "$NO_CACHE" -eq 1 ]; then
	BUILD_CACHE_ARGS+=(--no-cache)
fi

if ! podman build --platform "$NATIVE_PLATFORM" \
	"${BUILD_CACHE_ARGS[@]}" \
	--build-arg BUILD_DATE="$BUILD_DATE" \
	--build-arg VCS_REF="$VCS_REF" \
	--build-arg IMAGE_TAG="$BUILD_VERSION" \
	-t "$REPO:$BUILD_VERSION" \
	-f "$BUILD_DIR/Containerfile" \
	"$BUILD_DIR"; then
	BUILD_EXIT_CODE=$?
	echo "❌ Build failed"
	echo "🔍 DEBUG: Podman build command failed with exit code $BUILD_EXIT_CODE"
	exit 1
fi

echo "🔍 DEBUG: Podman build completed successfully"
echo "✓ Built local development image $REPO:$BUILD_VERSION ($NATIVE_PLATFORM)"
