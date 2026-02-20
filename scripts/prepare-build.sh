#!/usr/bin/env bash
# Prepare build directory for container image build
# Usage: prepare-build.sh <version>
#
# This script prepares the build directory:
# - Creates and clears the build directory
# - Copies Containerfile and assets
# - Syncs canonical files into build template (from manifest)
# - Replaces {{IMAGE_TAG}} placeholders in template files

set -e

VERSION="${1:-dev}"
echo "🔍 DEBUG: VERSION='$VERSION'"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
echo "🔍 DEBUG: SCRIPT_DIR='$SCRIPT_DIR'"
echo "🔍 DEBUG: PROJECT_ROOT='$PROJECT_ROOT'"

cd "$PROJECT_ROOT"
echo "🔍 DEBUG: Changed to PROJECT_ROOT"

BUILD_DIR="build"
BUILD_VERSION="$VERSION"
echo "🔍 DEBUG: BUILD_DIR='$BUILD_DIR'"
echo "🔍 DEBUG: BUILD_VERSION='$BUILD_VERSION'"

# Create and clear build folder
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy Containerfile, assets, and vig-utils package to build folder
cp Containerfile "$BUILD_DIR/"
cp -r assets "$BUILD_DIR/"
cp -r packages "$BUILD_DIR/"

# Sync canonical files into build template (from declarative Python manifest)
echo "Syncing canonical files into build template..."
uv run python "$SCRIPT_DIR/sync_manifest.py" sync "$BUILD_DIR/assets/workspace" \
	--project-root "$PROJECT_ROOT"

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
