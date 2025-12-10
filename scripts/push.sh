#!/usr/bin/env bash
# Push container image to registry
# Usage: push.sh <version> [REPO] [NATIVE_PLATFORM] [PLATFORMS] [REGISTRY_TEST]

set -e

VERSION="$1"
REPO="${2:-${TEST_REGISTRY:-ghcr.io/vig-os/devcontainer}}"
# Remove trailing slash from REPO to avoid invalid tag format (e.g., localhost:5000/test/:tag)
REPO="${REPO%/}"

# Detect native platform
NATIVE_ARCH=$(uname -m)
if [ "$NATIVE_ARCH" = "arm64" ] || [ "$NATIVE_ARCH" = "aarch64" ]; then
	NATIVE_PLATFORM="${3:-linux/arm64}"
	NATIVE_ARCH="arm64"
else
	NATIVE_PLATFORM="${3:-linux/amd64}"
	NATIVE_ARCH="amd64"
fi

PLATFORMS="${4:-linux/amd64,linux/arm64}"
export PLATFORMS
REGISTRY_TEST=${5:-0}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source utilities
# shellcheck source=scripts/utils.sh
source "$SCRIPT_DIR/utils.sh"

cd "$PROJECT_ROOT"

# Validate version
if [ -z "$VERSION" ]; then
	echo ""
	echo "❌ ERROR: VERSION is required to push"
	echo ""
	echo "   Usage: push.sh VERSION [REPO] [NATIVE_PLATFORM] [PLATFORMS] [REGISTRY_TEST]"
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
GIT_TAG="v$VERSION"
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
LATEST_TAG=$(git tag -l | grep -E '^v[0-9]+\.[0-9]+$' | sed 's/^v//' | sort -t. -k1,1n -k2,2n | tail -1)
if [ -n "$LATEST_TAG" ]; then
	echo "  Latest tag: v$LATEST_TAG"
	MAJOR_NEW=$(echo "$VERSION" | cut -d. -f1)
	MINOR_NEW=$(echo "$VERSION" | cut -d. -f2)
	MAJOR_LATEST=$(echo "$LATEST_TAG" | cut -d. -f1)
	MINOR_LATEST=$(echo "$LATEST_TAG" | cut -d. -f2)
	if [ "$MAJOR_NEW" -lt "$MAJOR_LATEST" ] || { [ "$MAJOR_NEW" -eq "$MAJOR_LATEST" ] && [ "$MINOR_NEW" -le "$MINOR_LATEST" ]; }; then
		echo ""
		echo "❌ ERROR: New version $VERSION is not higher than latest version v$LATEST_TAG!"
		echo ""
		echo "   The new version must be greater than the latest tagged version."
		echo "   Latest version: v$LATEST_TAG"
		echo "   New version: $VERSION"
		echo ""
		exit 1
	fi
	echo "✓ New version $VERSION is higher than latest v$LATEST_TAG"
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

# Capture build metadata
echo "Capturing build metadata (before any commits)..."
BUILD_DATE=$(get_iso_date)
VCS_REF=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
echo "  BUILD_DATE: $BUILD_DATE"
echo "  VCS_REF: $VCS_REF"
echo "  IMAGE_TAG: $VERSION"

# Prepare build folder
BUILD_DIR="build"
echo "Preparing build folder..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Use minimal Containerfile for registry tests (faster builds)
if [ "$REGISTRY_TEST" -eq 1 ]; then
	echo "Using minimal Containerfile for registry testing (REGISTRY_TEST=1)"
	cat > "$BUILD_DIR/Containerfile" << 'EOF'
# Minimal Containerfile for registry testing
FROM python:3.12-slim-trixie

# Keep basic structure to test asset copying
COPY assets /root/assets

# Minimal metadata
ARG BUILD_DATE
ARG VCS_REF
ARG IMAGE_TAG=dev
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.version="${IMAGE_TAG}"
EOF
else
	cp Containerfile "$BUILD_DIR/"
fi

# Copy assets to build folder
cp -r assets "$BUILD_DIR/"
if [ -d "$BUILD_DIR/assets/workspace" ]; then
	echo "Replacing {{IMAGE_TAG}} with $VERSION in build folder template files..."

	find "$BUILD_DIR/assets/workspace" -type f -print0 | while IFS= read -r -d '' file; do
		sed_inplace "s|{{IMAGE_TAG}}|$VERSION|g" "$file"
	done

	# Update devcontainer README in build folder with version and date
	BUILD_DEVCONTAINER_README="$BUILD_DIR/assets/workspace/.devcontainer/README.md"
	if [ -f "$BUILD_DEVCONTAINER_README" ]; then
		RELEASE_DATE="${BUILD_DATE%%T*}"
		RELEASE_URL="https://github.com/vig-os/devcontainer/releases/tag/v$VERSION"
		echo "Updating devcontainer README in build folder with version $VERSION..."
		if ! python3 scripts/update_readme.py version "$BUILD_DEVCONTAINER_README" "$VERSION" "$RELEASE_URL" "$RELEASE_DATE"; then
			echo "❌ Failed to update devcontainer README version metadata in build folder"
			exit 1
		fi
		echo "✓ Updated devcontainer README in build folder with version $VERSION"
	fi
fi

# Build native platform image
echo "Building native platform image $VERSION..."
if ! podman build --platform "$NATIVE_PLATFORM" \
	--build-arg BUILD_DATE="$BUILD_DATE" \
	--build-arg VCS_REF="$VCS_REF" \
	--build-arg IMAGE_TAG="$VERSION" \
	--tag "$REPO:$VERSION-$NATIVE_ARCH" \
	--file "$BUILD_DIR/Containerfile" \
	"$BUILD_DIR"; then
	echo "❌ Error: Native platform build failed"
	exit 1
fi
echo "✓ Built native platform image $VERSION-$NATIVE_ARCH"

# Run tests on native platform image
if [ "$REGISTRY_TEST" -eq 1 ]; then
	echo "Skipping image testing (this is a registry test run))"
else
	echo "Testing versioned image:$VERSION..."

	# Tag native image without arch so devcontainer tests can pull it
	podman tag "$REPO:$VERSION-$NATIVE_ARCH" "$REPO:$VERSION"
	if ! ( make test-image VERSION="$VERSION" \
		&& make test-integration VERSION="$VERSION" ); then
			echo "❌ Tests failed"

			# Clean tag to avoid leaving stray tag if tests fail
			podman rmi -f "$REPO:$VERSION" >/dev/null 2>&1 || true
			exit 1
		fi

	# Clean the temporary arch-less tag after tests
	podman rmi -f "$REPO:$VERSION" >/dev/null 2>&1 || true
fi

# Add native platform to list of built platforms
BUILT_PLATFORMS=("$REPO:$VERSION-$NATIVE_ARCH")

# Build for target platforms
echo "Building multi-arch images for: $PLATFORMS"
for platform in $(echo "$PLATFORMS" | tr ',' ' '); do
	# Skip native platform, it was built above
	if [ "$platform" = "$NATIVE_PLATFORM" ]; then
		continue
	fi

	# Normalize platform format
	platform=$(echo "$platform" | xargs)
	arch=$(echo "$platform" | cut -d'/' -f2)

	# Build image for platform
	echo "Building for $platform..."
	if ! podman build \
		--platform "$platform" \
		--build-arg BUILD_DATE="$BUILD_DATE" \
		--build-arg VCS_REF="$VCS_REF" \
		--build-arg IMAGE_TAG="$VERSION" \
		--tag "$REPO:$VERSION-$arch" \
		--file "$BUILD_DIR/Containerfile" \
		"$BUILD_DIR"; then
		echo "❌ Error: $platform build failed"
		exit 1
	fi
	BUILT_PLATFORMS+=("$REPO:$VERSION-$arch")
done

# TLS verify for localhost registries
if [ "$REGISTRY_TEST" -eq 1 ]; then
	PODMAN_TLS_VERIFY="--tls-verify=false"
else
	PODMAN_TLS_VERIFY=""
fi

# Push individual images to registry (needed for manifest creation)
echo "Pushing individual images to registry..."
for img_tag in "${BUILT_PLATFORMS[@]}"; do
	echo "Pushing $img_tag..."
	if ! podman push $PODMAN_TLS_VERIFY "$img_tag"; then
		echo "❌ Error: Pushing $img_tag failed"
		exit 1
	fi
done

# Create LATEST manifest
echo "Creating :latest manifest list..."
echo "Removing any existing local tags/manifests for :latest..."
podman manifest rm "$REPO:latest" 2>/dev/null || true
podman rmi -f "$REPO:latest" 2>/dev/null || true


if ! podman manifest create "$REPO:latest"; then
	echo "❌ Error: Manifest creation failed"
	exit 1
fi

for img_tag in "${BUILT_PLATFORMS[@]}"; do
	# Images are now in registry, so we can use regular registry references
	if ! podman manifest add "$REPO:latest" "$img_tag"; then
		echo "❌ Error: Adding $img_tag to manifest failed"
		exit 1
	fi
done

# Create VERSION manifest
echo "Creating :$VERSION manifest list..."
echo "Removing any existing local tags/manifests for $VERSION..."
podman manifest rm "$REPO:$VERSION" 2>/dev/null || true
podman rmi -f "$REPO:$VERSION" 2>/dev/null || true

if ! podman manifest create "$REPO:$VERSION"; then
	echo "❌ Error: Version manifest creation failed"
	exit 1
fi

for img_tag in "${BUILT_PLATFORMS[@]}"; do
	# Images are now in registry, so we can use regular registry references
	if ! podman manifest add "$REPO:$VERSION" "$img_tag"; then
		echo "❌ Error: Adding $img_tag to version manifest failed"
		exit 1
	fi
done

# Push manifests
echo "Pushing manifests to registry..."
if ! podman manifest push $PODMAN_TLS_VERIFY --all "$REPO:latest"; then
	echo "❌ Error: :latest manifest push failed"
	exit 1
fi
if ! podman manifest push $PODMAN_TLS_VERIFY --all "$REPO:$VERSION"; then
	echo "❌ Error: :$VERSION manifest push failed"
	exit 1
fi
echo "✓ Successfully pushed latest and $VERSION (multi-arch)"

# Update README.md
echo "Updating README.md with latest version and size..."
RELEASE_DATE="${BUILD_DATE%%T*}"
RELEASE_URL="https://github.com/vig-os/devcontainer/releases/tag/v$VERSION"
if [ -f README.md ]; then
	if ! python3 scripts/update_readme.py version README.md "$VERSION" "$RELEASE_URL" "$RELEASE_DATE"; then
		echo "❌ Failed to update README.md version"
		exit 1
	fi

	# Get image size and round to nearest 10MB
	# Note: Inspect architecture-specific image, not the manifest
	echo "Calculating image size..."
	NATIVE_ARCH=$(uname -m)
	if [ "$NATIVE_ARCH" = "arm64" ] || [ "$NATIVE_ARCH" = "aarch64" ]; then
		INSPECT_ARCH="arm64"
	else
		INSPECT_ARCH="amd64"
	fi
	IMAGE_SIZE_BYTES=$(podman image inspect --format='{{.Size}}' "$REPO:$VERSION-$INSPECT_ARCH" 2>/dev/null || echo "0")
	if [ "$IMAGE_SIZE_BYTES" -gt 0 ]; then
		# Convert to MB and round to nearest 10MB
		IMAGE_SIZE_MB=$(( (IMAGE_SIZE_BYTES / 1024 / 1024 + 5) / 10 * 10 ))
		if ! python3 scripts/update_readme.py size README.md "$IMAGE_SIZE_MB"; then
			echo "⚠️  Failed to update README.md size, continuing..."
		else
			echo "✓ Updated README.md with size ~${IMAGE_SIZE_MB} MB"
		fi
	else
		echo "⚠️  Could not determine image size, skipping size update"
		IMAGE_SIZE_MB=""
	fi

	if [ -n "$IMAGE_SIZE_MB" ]; then
		echo "✓ Updated README.md with version $VERSION and size ~${IMAGE_SIZE_MB} MB"
	else
		echo "✓ Updated README.md with version $VERSION (size update skipped)"
	fi

else
	echo "⚠️  README.md not found, skipping updates"
fi

# Commit changes to README.md
echo "Committing changes..."
# Check if README.md has any changes (staged or unstaged)
if git diff --quiet README.md && git diff --cached --quiet README.md; then
	echo "⚠️  WARNING: README.md has no changes to commit"
	echo ""
	echo "   This may happen if README.md was already at version $VERSION."
	echo "   Current README.md version line:"
	grep "\*\*Version\*\*" README.md || echo "   (Version line not found)"
	echo ""
	echo "   Continuing without committing README.md changes..."
else
	git add README.md 2>/dev/null || true
	if ! git commit -m "Release $VERSION"; then
		echo "❌ Failed to commit changes"
		git reset HEAD README.md 2>/dev/null || true
		exit 1
	fi
	echo "✓ Committed changes"
fi

# Create git tag
echo "Creating git tag $GIT_TAG (for image:$VERSION)..."
# Disable GPG signing for tags to avoid interactive prompts in automated environments
if ! git -c tag.gpgsign=false tag -a "$GIT_TAG" -m "Release $VERSION"; then
	echo "❌ Failed to create git tag"
	exit 1
fi
echo "✓ Created git tag $GIT_TAG"

echo ""
echo "✓ Successfully tagged and pushed:$VERSION"
if [ "$REGISTRY_TEST" -eq 1 ]; then
	echo "  Image: $REPO:$VERSION (dummy image)"
	echo "  Image: $REPO:latest (dummy image)"
else
	echo "  Image: $REPO:$VERSION (multi-arch)"
	echo "  Image: $REPO:latest (multi-arch)"
fi
echo "  Git tag: $GIT_TAG"
