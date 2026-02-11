#!/usr/bin/env bash
# Build container image
# Usage: build.sh <version> [REPO] [NATIVE_PLATFORM]
#
# This script builds a container image:
# - Creates and clears the build directory
# - Copies Containerfile and assets
# - Replaces {{IMAGE_TAG}} placeholders in template files
# - Builds the container image using podman

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
REPO="ghcr.io/vig-os/devcontainer"
echo "🔍 DEBUG: VERSION='$VERSION'"
echo "🔍 DEBUG: REPO='$REPO'"

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

# Prepare build directory for container image build
echo "Preparing build directory..."

# Create and clear build folder
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy Containerfile and assets to build folder
cp Containerfile "$BUILD_DIR/"
cp -r assets "$BUILD_DIR/"

# Replace {{IMAGE_TAG}} placeholders in template files
if [ -d "$BUILD_DIR/assets/workspace" ]; then
	echo "Replacing {{IMAGE_TAG}} with $BUILD_VERSION in template files..."

	find "$BUILD_DIR/assets/workspace" -type f -print0 | while IFS= read -r -d '' file; do
		uv run python "$SCRIPT_DIR/utils.py" sed "s|{{IMAGE_TAG}}|$BUILD_VERSION|g" "$file"
	done

	# Verify replacements
	if grep -r "{{IMAGE_TAG}}" "$BUILD_DIR/assets/workspace" 2>/dev/null; then
		echo "❌ Some {{IMAGE_TAG}} placeholders were not replaced!"
		exit 1
	fi
	echo "✓ All {{IMAGE_TAG}} placeholders replaced"
fi

# Update devcontainer README with version (if script exists and file exists)
BUILD_DEVCONTAINER_README="$BUILD_DIR/assets/workspace/.devcontainer/README.md"
if [ -f "$BUILD_DEVCONTAINER_README" ] && [ -f "scripts/update_readme.py" ] && [ "$BUILD_VERSION" != "dev" ]; then
	RELEASE_DATE="$(date -u +%Y-%m-%d)"
	RELEASE_URL=""
	# Only update README if RELEASE_URL is provided (indicates a versioned release, not dev build)
	if [ -n "$RELEASE_URL" ]; then
		echo "Updating devcontainer README with version $BUILD_VERSION..."
		if uv run python "$SCRIPT_DIR/utils.py" version "$BUILD_DEVCONTAINER_README" "$BUILD_VERSION" "$RELEASE_URL" "$RELEASE_DATE"; then
			echo "✓ Updated devcontainer README with version $BUILD_VERSION"
		else
			echo "❌ Failed to update devcontainer README..."
			exit 1
		fi
	fi
fi

echo "✓ Build directory prepared: $BUILD_DIR"

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
