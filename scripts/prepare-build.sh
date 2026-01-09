#!/usr/bin/env bash
# Prepare build directory for container image build
# Usage: prepare-build.sh <version> [BUILD_DIR] [RELEASE_DATE] [RELEASE_URL]
#
# This script prepares the build directory by:
# - Creating and clearing the build directory
# - Copying Containerfile and assets
# - Replacing {{IMAGE_TAG}} placeholders in template files
# - Updating devcontainer README with version metadata (optional)

set -e

VERSION="${1:-dev}"
BUILD_DIR="${2:-build}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "Preparing build directory..."

# Create and clear build folder
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy Containerfile and assets to build folder
cp Containerfile "$BUILD_DIR/"
cp -r assets "$BUILD_DIR/"

# Replace {{IMAGE_TAG}} placeholders in template files
if [ -d "$BUILD_DIR/assets/workspace" ]; then
	echo "Replacing {{IMAGE_TAG}} with $VERSION in template files..."

	find "$BUILD_DIR/assets/workspace" -type f -print0 | while IFS= read -r -d '' file; do
		python3 "$SCRIPT_DIR/utils.py" sed "s|{{IMAGE_TAG}}|$VERSION|g" "$file"
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
if [ -f "$BUILD_DEVCONTAINER_README" ] && [ -f "scripts/update_readme.py" ] && [ "$VERSION" != "dev" ]; then
	RELEASE_DATE="${3:-$(date -u +%Y-%m-%d)}"
	RELEASE_URL="${4:-}"
	# Only update README if RELEASE_URL is provided (indicates a versioned release, not dev build)
	if [ -n "$RELEASE_URL" ]; then
		echo "Updating devcontainer README with version $VERSION..."
		if python3 "$SCRIPT_DIR/utils.py" version "$BUILD_DEVCONTAINER_README" "$VERSION" "$RELEASE_URL" "$RELEASE_DATE"; then
			echo "✓ Updated devcontainer README with version $VERSION"
		else
			echo "❌ Failed to update devcontainer README..."
			exit 1
		fi
	fi
fi

echo "✓ Build directory prepared: $BUILD_DIR"
