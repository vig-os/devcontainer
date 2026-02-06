# ═══════════════════════════════════════════════════════════════════════════════
# vigOS Devcontainer - Just Recipes
# Build automation for devcontainer image development
# ═══════════════════════════════════════════════════════════════════════════════
# Import standard dev recipes

import 'justfile.base'

# ═══════════════════════════════════════════════════════════════════════════════
# VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════
# Allow TEST_REGISTRY to override REPO for testing (e.g., localhost:5000/test/)

repo := env_var_or_default("TEST_REGISTRY", "ghcr.io/vig-os/devcontainer")

# Multi-arch support: build for both AMD64 and ARM64

platforms := "linux/amd64,linux/arm64"

# ═══════════════════════════════════════════════════════════════════════════════
# INFO
# ═══════════════════════════════════════════════════════════════════════════════

# Show available commands (default)
[group('info')]
default:
    @just --list --unsorted

# Show available commands
[group('info')]
help:
    @just --list

# Show image information
[group('info')]
info:
    #!/usr/bin/env bash
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        NATIVE_ARCH="linux/arm64"
    else
        NATIVE_ARCH="linux/amd64"
    fi
    echo "Image: {{ repo }}"
    echo "Containerfile: Containerfile"
    echo "Native arch: $NATIVE_ARCH"

# Install system dependencies and setup development environment
[group('info')]
init *args:
    ./scripts/init.sh {{ args }}

# Generate documentation from templates
[group('info')]
docs:
    uv run python docs/generate.py

# Test login to GHCR
[group('info')]
login:
    #!/usr/bin/env bash
    echo "Logging in to GitHub Container Registry..."
    podman login ghcr.io

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════════════════════

# Build local development image
[group('build')]
build no_cache="":
    #!/usr/bin/env bash
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        NATIVE_ARCH="linux/arm64"
    else
        NATIVE_ARCH="linux/amd64"
    fi
    if [ -n "{{ no_cache }}" ]; then
        ./scripts/build.sh --no-cache dev "{{ repo }}" "$NATIVE_ARCH"
    else
        ./scripts/build.sh dev "{{ repo }}" "$NATIVE_ARCH"
    fi

# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

# Helper to ensure dev image exists before running image/integration tests
[private]
_ensure-dev-image version="dev":
    #!/usr/bin/env bash
    if ! podman image exists "{{ repo }}:{{ version }}"; then
        if [ "{{ version }}" = "dev" ]; then
            echo "Building dev image..."
            just build
        else
            echo "❌ Image {{ repo }}:{{ version }} not found. Please build it first."
            exit 1
        fi
    fi

# Run image tests only
[group('test')]
test-image version="dev":
    @just _ensure-dev-image {{ version }}
    #!/usr/bin/env bash
    TEST_CONTAINER_TAG={{ version }} uv run pytest tests/test_image.py -v --tb=short

# Run integration tests only
[group('test')]
test-integration version="dev":
    @just _ensure-dev-image {{ version }}
    #!/usr/bin/env bash
    TEST_CONTAINER_TAG={{ version }} uv run pytest tests/test_integration.py -v --tb=short

# Run utils tests only
[group('test')]
test-utils:
    #!/usr/bin/env bash
    uv run pytest tests/test_utils.py -v -s --tb=short

# Run version check tests only
[group('test')]
test-version-check:
    #!/usr/bin/env bash
    uv run pytest tests/test_version_check.py -v -s --tb=short

# Run validate commit msg tests only
[group('test')]
test-validate-commit-msg:
    #!/usr/bin/env bash
    uv run pytest tests/test_validate_commit_msg.py -v -s --tb=short

# Clean up lingering containers before running tests
[private]
_test-cleanup-check:
    #!/usr/bin/env bash
    if podman ps -a --filter "name=workspace-devcontainer" -q 2>/dev/null | grep -q .; then
        echo "⚠️  Lingering test containers found, cleaning up..."
        just clean-test-containers
    fi

# Run all test suites
[group('test')]
test version="dev":
    @just _test-cleanup-check
    @just _ensure-dev-image {{ version }}
    #!/usr/bin/env bash
    TEST_CONTAINER_TAG={{ version }}  uv run pytest tests -v -s --tb=short

# ═══════════════════════════════════════════════════════════════════════════════
# RELEASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
# Release process is now handled by GitHub Actions workflow.
# Pushing a semantic version tag (e.g., v1.2.3) triggers the CI/CD pipeline:
#   .github/workflows/publish-container-image.yml
#
# Manual release process:
#   1. Ensure on dev branch and up to date
#   2. Run tests: just test
#   3. Update CHANGELOG.md (move Unreleased to version section)
#   4. Commit changes
#   5. Create and push tag: git tag -a vX.Y.Z -m "Release X.Y.Z" && git push origin vX.Y.Z
#   6. GitHub Actions will build, test, and publish the image
#   7. Create PR from dev to main after release completes
#
# Planned automation (issue #48):
#   - just create-release X.Y.Z  (automates steps 1-5)
#   - just finalize-release X.Y.Z (automates step 7)
#   - just test-release X.Y.Z (test build without publishing)
# ═══════════════════════════════════════════════════════════════════════════════

# Pull image from registry (default: latest)
[group('release')]
pull version="latest":
    #!/usr/bin/env bash
    echo "Pulling image {{ repo }}:{{ version }}..."
    TLS_FLAG=""
    if [ "${REGISTRY_TEST:-}" = "1" ]; then
        TLS_FLAG="--tls-verify=false"
    fi
    podman pull $TLS_FLAG "{{ repo }}:{{ version }}" || echo "⚠️  Failed to pull {{ repo }}:{{ version }}"

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD / CLEAN
# ═══════════════════════════════════════════════════════════════════════════════

# Remove image (default: dev)
[group('build')]
clean version="dev":
    #!/usr/bin/env bash
    # Use TEST_REGISTRY from environment if set, otherwise use repo variable
    # This allows tests to override the repo via TEST_REGISTRY at runtime
    export TEST_REGISTRY
    REPO="${TEST_REGISTRY:-{{ repo }}}"
    # If TEST_REGISTRY was used and doesn't contain a path, append /test
    # This handles cases where TEST_REGISTRY=localhost:PORT instead of localhost:PORT/test
    if [[ -n "$TEST_REGISTRY" && "$REPO" == "$TEST_REGISTRY" && "$REPO" != *"/"* ]]; then
        REPO="${REPO}/test"
    fi
    ./scripts/clean.sh "{{ version }}" "$REPO"

# Clean up lingering test containers
[group('build')]
clean-test-containers:
    #!/usr/bin/env bash
    echo "🧹 Cleaning up lingering test containers..."
    FMT=$(printf '\x7b\x7b.ID\x7d\x7d')
    DEVCONTAINERS=$(podman ps -a --filter "name=workspace-devcontainer" --format "$FMT" 2>/dev/null)
    SIDECARS=$(podman ps -a --filter "name=test-sidecar" --format "$FMT" 2>/dev/null)
    if [ -n "$DEVCONTAINERS" ] || [ -n "$SIDECARS" ]; then
        if [ -n "$DEVCONTAINERS" ]; then
            echo "  Removing workspace devcontainers..."
            echo "$DEVCONTAINERS" | xargs -r podman rm -f
        fi
        if [ -n "$SIDECARS" ]; then
            echo "  Removing test sidecars..."
            echo "$SIDECARS" | xargs -r podman rm -f
        fi
        echo "✅ Cleanup complete"
    else
        echo "✨ No lingering test containers found"
    fi

# ═══════════════════════════════════════════════════════════════════════════════
# SIDECAR
# ═══════════════════════════════════════════════════════════════════════════════

# Convenience alias for test-sidecar (uses generic sidecar recipe)
[group('sidecar')]
test-sidecar *args:
    @just sidecar test-sidecar {{ args }}

# ═══════════════════════════════════════════════════════════════════════════════
# PODMAN
# ═══════════════════════════════════════════════════════════════════════════════
# Podman container & image management recipes

import 'justfile.podman'
