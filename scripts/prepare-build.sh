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

# Sync canonical files into build template (from manifest)
echo "Syncing canonical files into build template..."
sync_manifest_files() {
	local dest_base="$1"
	local manifest="$SCRIPT_DIR/sync-manifest.txt"
	local failed=0

	if [[ ! -f "$manifest" ]]; then
		echo "Error: Manifest not found at $manifest" >&2
		exit 1
	fi

	if [[ ! -d "$dest_base" ]]; then
		echo "Error: Target directory $dest_base does not exist" >&2
		exit 1
	fi

	while IFS= read -r line || [[ -n "$line" ]]; do
		# Skip blank lines and comments
		[[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
		# Parse line: "source -> destination" or just "source" (dest defaults to source)
		local src dest
		if [[ "$line" == *" -> "* ]]; then
			src="$(echo "$line" | sed 's/ *->.*$//' | xargs)"
			dest="$(echo "$line" | sed 's/^.*-> *//' | xargs)"
		else
			src="$(echo "$line" | xargs)"
			dest=""
		fi
		if [[ -z "$src" ]]; then
			echo "Warning: Skipping malformed manifest line: $line" >&2
			continue
		fi
		# Default destination to source path if omitted
		if [[ -z "$dest" ]]; then
			dest="$src"
		fi

		local src_path="$PROJECT_ROOT/$src"
		local dest_path="$dest_base/$dest"

		# Check if source exists (file or directory)
		if [[ ! -e "$src_path" ]]; then
			echo "  [MISSING] Source not found: $src" >&2
			failed=1
			continue
		fi

		# Handle directories
		if [[ -d "$src_path" ]]; then
			mkdir -p "$(dirname "$dest_path")"
			cp -r "$src_path" "$dest_path"
			echo "  [SYNCED]  $src/ -> assets/workspace/$dest/"
		# Handle files
		elif [[ -f "$src_path" ]]; then
			mkdir -p "$(dirname "$dest_path")"
			cp "$src_path" "$dest_path"
			echo "  [SYNCED]  $src -> assets/workspace/$dest"
		else
			echo "  [UNKNOWN] Source is neither file nor directory: $src" >&2
			failed=1
		fi
	done < "$manifest"

	if [[ $failed -ne 0 ]]; then
		echo "Error: Some files could not be synced" >&2
		exit 1
	fi
	echo "All manifest files synced successfully."
}

sync_manifest_files "$BUILD_DIR/assets/workspace"

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
