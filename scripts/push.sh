#!/usr/bin/env bash
# Push container image to registry
# Usage: push.sh <version> [REPO] [NATIVE_PLATFORM] [PLATFORMS] [NO_TEST] [NATIVE_ARCH_ONLY]

set -e

VERSION="$1"
REPO="${2:-${TEST_REGISTRY:-ghcr.io/vig-os/devcontainer}}"

# Detect native platform
NATIVE_ARCH=$(uname -m)
if [ "$NATIVE_ARCH" = "arm64" ] || [ "$NATIVE_ARCH" = "aarch64" ]; then
	NATIVE_PLATFORM="${3:-linux/arm64}"
else
	NATIVE_PLATFORM="${3:-linux/amd64}"
fi

PLATFORMS="${4:-linux/amd64,linux/arm64}"
NO_TEST="${5:-}"
NATIVE_ARCH_ONLY="${6:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Validate version
if [ -z "$VERSION" ]; then
	echo ""
	echo "❌ ERROR: VERSION is required to push"
	echo ""
	echo "   Usage: push.sh VERSION [REPO] [NATIVE_PLATFORM] [PLATFORMS] [NO_TEST] [NATIVE_ARCH_ONLY]"
	echo "   Example: push.sh 1.0"
	echo ""
	exit 1
fi

if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+$'; then
	echo ""
	echo "❌ ERROR: Invalid version format '$VERSION'"
	echo ""
	echo "   Version must follow the format X.Y (e.g., 1.0, 2.5, 10.3)"
	echo "   Examples of valid versions: 1.0, 2.1, 10.5, 0.9"
	echo "   Examples of invalid versions: 1, 1.0.0, v1.0, 1.0-dev"
	echo ""
	exit 1
fi

echo "Preparing image:$VERSION..."

# Check git tag
GIT_TAG="$VERSION"
echo "Checking if git tag $GIT_TAG already exists..."
if git rev-parse "$GIT_TAG" >/dev/null 2>&1; then
	echo ""
	echo "❌ ERROR: Git tag $GIT_TAG already exists!"
	echo ""
	echo "   Please use a different version number or delete the existing tag:"
	echo "   git tag -d $GIT_TAG"
	echo ""
	exit 1
fi
echo "✓ Git tag $GIT_TAG does not exist"

# Check if version exists on GHCR
echo "Checking if version $VERSION already exists on GHCR..."
if podman manifest inspect "$REPO:$VERSION" >/dev/null 2>&1; then
	echo ""
	echo "❌ ERROR: Version $VERSION already exists on GHCR!"
	echo ""
	echo "   Stable versions are immutable and cannot be overwritten."
	echo "   This prevents accidental corruption of released versions."
	echo ""
	echo "   Options:"
	echo "   1. Use a different version number"
	echo "   2. Manually delete from GHCR if this was intentional:"
	echo "      podman manifest rm $REPO:$VERSION"
	echo ""
	exit 1
fi
echo "✓ Version $VERSION does not exist on GHCR"

# Check latest version tag
echo "Checking latest version tag..."
LATEST_TAG=$(git tag -l | grep -E '^[0-9]+\.[0-9]+$' | sort -t. -k1,1n -k2,2n | tail -1)
if [ -n "$LATEST_TAG" ]; then
	echo "  Latest tag: $LATEST_TAG"
	MAJOR_NEW=$(echo "$VERSION" | cut -d. -f1)
	MINOR_NEW=$(echo "$VERSION" | cut -d. -f2)
	MAJOR_LATEST=$(echo "$LATEST_TAG" | cut -d. -f1)
	MINOR_LATEST=$(echo "$LATEST_TAG" | cut -d. -f2)
	if [ "$MAJOR_NEW" -lt "$MAJOR_LATEST" ] || { [ "$MAJOR_NEW" -eq "$MAJOR_LATEST" ] && [ "$MINOR_NEW" -le "$MINOR_LATEST" ]; }; then
		echo ""
		echo "❌ ERROR: New version $VERSION is not higher than latest version $LATEST_TAG!"
		echo ""
		echo "   The new version must be greater than the latest tagged version."
		echo "   Latest version: $LATEST_TAG"
		echo "   New version: $VERSION"
		echo ""
		exit 1
	fi
	echo "✓ New version $VERSION is higher than latest $LATEST_TAG"
else
	echo "  No previous tags found"
	echo "✓ This will be the first version tag"
fi

# Verify git repository is clean
echo "Verifying git repository is in a clean state..."
if ! git rev-parse --git-dir >/dev/null 2>&1; then
	echo ""
	echo "❌ ERROR: Not in a git repository!"
	echo ""
	exit 1
fi
if ! git diff --quiet HEAD; then
	echo ""
	echo "❌ ERROR: Repository has uncommitted changes!"
	echo ""
	echo "   All changes must be committed before creating a versioned release."
	echo "   This ensures the git tag points to the exact code that was built."
	echo ""
	echo "   Please commit or stash your changes and try again."
	echo ""
	git status --short
	echo ""
	exit 1
fi
if ! git diff --cached --quiet; then
	echo ""
	echo "❌ ERROR: Repository has staged but uncommitted changes!"
	echo ""
	echo "   All changes must be committed before creating a versioned release."
	echo ""
	git status --short
	echo ""
	exit 1
fi
echo "✓ Repository is clean"

# Backup and replace template
echo "Backing up and replacing template with version $VERSION..."
"$SCRIPT_DIR/backup_template.sh" "$VERSION"

# Capture build metadata
echo "Capturing build metadata (before any commits)..."
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
echo "  BUILD_DATE: $BUILD_DATE"
echo "  VCS_REF: $VCS_REF"
echo "  IMAGE_TAG: $VERSION"

# Build and test if needed
if [ -z "$NO_TEST" ]; then
	echo "Building versioned image:$VERSION (single arch for testing)..."
	if ! podman build --platform "$NATIVE_PLATFORM" \
		--build-arg BUILD_DATE="$BUILD_DATE" \
		--build-arg VCS_REF="$VCS_REF" \
		--build-arg IMAGE_TAG="$VERSION" \
		-t "$REPO:$VERSION" -f Containerfile .; then
		echo "❌ Build failed"
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi

	echo "Testing versioned image:$VERSION..."
	if ! "$SCRIPT_DIR/run_tests.sh" "$VERSION"; then
		echo "❌ Tests failed"
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi
else
	echo "⚠️  Skipping tests (NO_TEST=1)"
fi

# Build for target platforms
if [ -n "$NATIVE_ARCH_ONLY" ]; then
	PLATFORM_LIST="$NATIVE_PLATFORM"
	echo "Building single-arch image for native platform: $NATIVE_PLATFORM"
else
	PLATFORM_LIST="$PLATFORMS"
	echo "Building multi-arch images for: $PLATFORMS"
	echo "  Using same build metadata for all platforms"
fi

BUILT_PLATFORMS=""
for platform in $(echo "$PLATFORM_LIST" | tr ',' ' '); do
	platform=$(echo "$platform" | xargs)
	arch=$(echo "$platform" | cut -d'/' -f2)
	echo "Building for $platform..."
	if ! podman build \
		--platform "$platform" \
		--build-arg BUILD_DATE="$BUILD_DATE" \
		--build-arg VCS_REF="$VCS_REF" \
		--build-arg IMAGE_TAG="$VERSION" \
		--tag "$REPO:$VERSION-$arch" \
		-f Containerfile .; then
		echo "❌ Error: $platform build failed"
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi
	if echo "$REPO" | grep -q "^localhost:"; then
		echo "Pushing $platform image to local registry..."
		if ! podman push --tls-verify=false "$REPO:$VERSION-$arch"; then
			echo "❌ Error: Pushing $platform image failed"
			"$SCRIPT_DIR/restore_template.sh"
			exit 1
		fi
	fi
	BUILT_PLATFORMS="$BUILT_PLATFORMS $REPO:$VERSION-$arch"
done

# Create manifests
echo "Creating :latest manifest list..."
echo "Removing any existing local tags/manifests for :latest..."
podman manifest rm "$REPO:latest" 2>/dev/null || true
podman rmi -f "$REPO:latest" 2>/dev/null || true

if echo "$REPO" | grep -q "^localhost:"; then
	PODMAN_TLS_VERIFY="--tls-verify=false"
else
	PODMAN_TLS_VERIFY=""
fi

if ! podman manifest create "$REPO:latest"; then
	echo "❌ Error: Manifest creation failed"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
fi

for img_tag in $BUILT_PLATFORMS; do
	if ! podman manifest add "$REPO:latest" "$img_tag"; then
		echo "❌ Error: Adding $img_tag to manifest failed"
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi
done

echo "Creating :$VERSION manifest list..."
echo "Removing any existing local tags/manifests for $VERSION..."
podman manifest rm "$REPO:$VERSION" 2>/dev/null || true
podman rmi -f "$REPO:$VERSION" 2>/dev/null || true

if ! podman manifest create "$REPO:$VERSION"; then
	echo "❌ Error: Version manifest creation failed"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
fi

for img_tag in $BUILT_PLATFORMS; do
	if ! podman manifest add "$REPO:$VERSION" "$img_tag"; then
		echo "❌ Error: Adding $img_tag to version manifest failed"
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi
done

# Push manifests
echo "Pushing manifests to registry..."
if ! podman manifest push $PODMAN_TLS_VERIFY "$REPO:latest"; then
	echo "❌ Error: :latest manifest push failed"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
fi

if ! podman manifest push $PODMAN_TLS_VERIFY "$REPO:$VERSION"; then
	echo "❌ Error: :$VERSION manifest push failed"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
fi

if [ -n "$NATIVE_ARCH_ONLY" ]; then
	echo "✓ Successfully pushed $REPO:latest and $REPO:$VERSION ($NATIVE_PLATFORM)"
else
	echo "✓ Successfully pushed $REPO:latest and $REPO:$VERSION (multi-arch)"
fi

# Update README.md
echo "Updating README.md with latest version..."
if [ -f README.md ]; then
	if ! sed -i.tmp "s/- \*\*Latest version\*\*: .*/- **Latest version**: $VERSION/" README.md; then
		echo "❌ Failed to update README.md"
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi
	rm -f README.md.tmp 2>/dev/null || true
	echo "✓ Updated README.md with version $VERSION"
else
	echo "⚠️  README.md not found, skipping version update"
fi

# Commit changes
echo "Committing changes..."
git add Containerfile template README.md 2>/dev/null || true
if git diff --cached --quiet; then
	echo "❌ Error! No changes to commit in Containerfile, template, or README.md"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
else
	if ! git commit -m "Release $VERSION"; then
		echo "❌ Failed to commit changes"
		git reset HEAD Containerfile template README.md 2>/dev/null || true
		"$SCRIPT_DIR/restore_template.sh"
		exit 1
	fi
	echo "✓ Committed changes"
fi

# Create git tag
echo "Creating git tag $VERSION (for image:$VERSION)..."
if ! git tag "$VERSION"; then
	echo "❌ Failed to create git tag"
	"$SCRIPT_DIR/restore_template.sh"
	exit 1
fi
echo "✓ Created git tag $VERSION"

# Restore template
echo "Restoring template folder..."
"$SCRIPT_DIR/restore_template.sh"

echo ""
echo "✓ Successfully tagged and pushed:$VERSION"
if [ -n "$NATIVE_ARCH_ONLY" ]; then
	echo "  Image: $REPO:$VERSION ($NATIVE_PLATFORM)"
	echo "  Image: $REPO:latest ($NATIVE_PLATFORM)"
else
	echo "  Image: $REPO:$VERSION (multi-arch)"
	echo "  Image: $REPO:latest (multi-arch)"
fi
echo "  Git tag: $VERSION"
