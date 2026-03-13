#!/usr/bin/env bats
# shellcheck disable=SC2016
# BATS tests for build.sh
#
# Tests the build.sh script which prepares and builds a container image.
# These tests verify:
# - Argument parsing (version, repo, platform)
# - --no-cache flag handling
# - Architecture detection
# - Integration with prepare-build.sh
# - Error handling
#
# Note: SC2016 disabled because we intentionally use single quotes to search
# for literal shell variable syntax (e.g., '$VAR') in the target scripts.

setup() {
    load test_helper
    BUILD_SH="$PROJECT_ROOT/scripts/build.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "build.sh is executable" {
    run test -x "$BUILD_SH"
    assert_success
}

@test "build.sh has shebang" {
    run head -1 "$BUILD_SH"
    assert_output "#!/usr/bin/env bash"
}

# ── argument parsing & defaults ───────────────────────────────────────────────

@test "build.sh defines VERSION variable with default 'dev'" {
    run grep 'VERSION="\${1:-dev}"' "$BUILD_SH"
    assert_success
}

@test "build.sh defines REPO variable with default registry" {
    run grep 'REPO="\${2:-ghcr.io/vig-os/devcontainer}"' "$BUILD_SH"
    assert_success
}

@test "build.sh accepts --no-cache as first flag" {
    run grep 'if \[ "\${1:-}" = "--no-cache" \]' "$BUILD_SH"
    assert_success
}

# ── architecture detection ────────────────────────────────────────────────────

@test "build.sh detects architecture using uname" {
    run grep 'NATIVE_ARCH=\$(uname -m)' "$BUILD_SH"
    assert_success
}

@test "build.sh handles arm64 architecture" {
    run grep 'arm64' "$BUILD_SH"
    assert_success
}

@test "build.sh handles aarch64 architecture" {
    run grep 'aarch64' "$BUILD_SH"
    assert_success
}

@test "build.sh defaults to linux/amd64 for standard x86" {
    run grep 'NATIVE_PLATFORM="\${3:-linux/amd64}"' "$BUILD_SH"
    assert_success
}

@test "build.sh defaults to linux/arm64 for arm architectures" {
    run grep 'NATIVE_PLATFORM="\${3:-linux/arm64}"' "$BUILD_SH"
    assert_success
}

# ── build directory preparation ───────────────────────────────────────────────

@test "build.sh calls prepare-build.sh" {
    run grep '"\$SCRIPT_DIR/prepare-build.sh"' "$BUILD_SH"
    assert_success
}

@test "build.sh passes version to prepare-build.sh" {
    run grep 'prepare-build.sh.*VERSION' "$BUILD_SH"
    assert_success
}

# ── podman build invocation ───────────────────────────────────────────────────

@test "build.sh invokes podman build" {
    run grep 'podman build' "$BUILD_SH"
    assert_success
}

@test "build.sh passes --platform to podman build" {
    run grep 'podman build --platform' "$BUILD_SH"
    assert_success
}

@test "build.sh supports --no-cache flag for podman" {
    run grep 'BUILD_CACHE_ARGS' "$BUILD_SH"
    assert_success
}

@test "build.sh tags image with repository and version" {
    run grep -- '-t "\$REPO:\$BUILD_VERSION"' "$BUILD_SH"
    assert_success
}

@test "build.sh uses Containerfile from build directory" {
    run grep -- '-f "\$BUILD_DIR/Containerfile"' "$BUILD_SH"
    assert_success
}

# ── error handling ────────────────────────────────────────────────────────────

@test "build.sh uses strict mode (set -e)" {
    run grep 'set -e' "$BUILD_SH"
    assert_success
}

@test "build.sh captures podman build exit code" {
    run grep 'BUILD_EXIT_CODE=' "$BUILD_SH"
    assert_success
}

@test "build.sh exits with error on build failure" {
    run grep 'exit 1' "$BUILD_SH"
    assert_success
}

# ── output messages ───────────────────────────────────────────────────────────

@test "build.sh outputs success message with platform info" {
    run grep '✓ Built local development image' "$BUILD_SH"
    assert_success
}

@test "build.sh outputs error message on failure" {
    run grep '❌ Build failed' "$BUILD_SH"
    assert_success
}

# ── directory management ──────────────────────────────────────────────────────

@test "build.sh derives SCRIPT_DIR from script path" {
    run grep 'SCRIPT_DIR=' "$BUILD_SH"
    assert_success
}

@test "build.sh derives PROJECT_ROOT as parent of SCRIPT_DIR" {
    run grep 'PROJECT_ROOT=' "$BUILD_SH"
    assert_success
}

@test "build.sh changes to PROJECT_ROOT" {
    run grep 'cd "\$PROJECT_ROOT"' "$BUILD_SH"
    assert_success
}
