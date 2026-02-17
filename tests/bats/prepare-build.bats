#!/usr/bin/env bats
# shellcheck disable=SC2016
# BATS tests for prepare-build.sh
#
# Tests the prepare-build.sh script which prepares the build directory.
# These tests verify:
# - Build directory creation and cleanup
# - File copying (Containerfile, assets, packages)
# - Manifest file syncing
# - Template placeholder replacement ({{IMAGE_TAG}})
# - Version handling
#
# Note: SC2016 disabled because we intentionally use single quotes to search
# for literal shell variable syntax (e.g., '$VAR') in the target scripts.

setup() {
    load test_helper
    PREPARE_BUILD_SH="$PROJECT_ROOT/scripts/prepare-build.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "prepare-build.sh is executable" {
    run test -x "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh has shebang" {
    run head -1 "$PREPARE_BUILD_SH"
    assert_output "#!/usr/bin/env bash"
}

# ── argument handling ─────────────────────────────────────────────────────────

@test "prepare-build.sh accepts version as first argument" {
    run grep 'VERSION="\${1:-dev}"' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh defaults version to 'dev'" {
    run grep 'BUILD_VERSION="\$VERSION"' "$PREPARE_BUILD_SH"
    assert_success
}

# ── error handling ────────────────────────────────────────────────────────────

@test "prepare-build.sh uses strict mode (set -e)" {
    run grep 'set -e' "$PREPARE_BUILD_SH"
    assert_success
}

# ── directory setup ───────────────────────────────────────────────────────────

@test "prepare-build.sh derives SCRIPT_DIR from script path" {
    run grep 'SCRIPT_DIR=' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh derives PROJECT_ROOT as parent of SCRIPT_DIR" {
    run grep 'PROJECT_ROOT=' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh changes to PROJECT_ROOT" {
    run grep 'cd "\$PROJECT_ROOT"' "$PREPARE_BUILD_SH"
    assert_success
}

# ── build directory operations ────────────────────────────────────────────────

@test "prepare-build.sh removes existing build directory" {
    run grep 'rm -rf "\$BUILD_DIR"' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh creates fresh build directory" {
    run grep 'mkdir -p "\$BUILD_DIR"' "$PREPARE_BUILD_SH"
    assert_success
}

# ── file copying ──────────────────────────────────────────────────────────────

@test "prepare-build.sh copies Containerfile" {
    run grep 'cp Containerfile' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh copies assets directory recursively" {
    run grep 'cp -r assets' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh copies packages directory recursively" {
    run grep 'cp -r packages' "$PREPARE_BUILD_SH"
    assert_success
}

# ── manifest file syncing ─────────────────────────────────────────────────────

@test "prepare-build.sh defines sync_manifest_files function" {
    run grep 'sync_manifest_files()' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh reads manifest from sync-manifest.txt" {
    run grep 'manifest="\$SCRIPT_DIR/sync-manifest.txt"' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh validates manifest file exists" {
    run grep 'if \[\[ ! -f "\$manifest" \]\]' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh validates destination directory exists" {
    run grep 'if \[\[ ! -d "\$dest_base" \]\]' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh skips blank lines in manifest" {
    run grep 'Skip blank lines' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh skips comment lines in manifest" {
    run grep 'Skip.*comment' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh parses source and destination from manifest" {
    run grep 'if \[\[ "\$line" == \*" -> "\* \]\]' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh handles directory entries in manifest" {
    run grep 'if \[\[ -d "\$src_path" \]\]' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh handles file entries in manifest" {
    run grep 'elif \[\[ -f "\$src_path" \]\]' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh reports missing source files" {
    run grep 'MISSING' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh reports synced files" {
    run grep 'SYNCED' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh calls sync_manifest_files for workspace" {
    run grep 'sync_manifest_files "\$BUILD_DIR/assets/workspace"' "$PREPARE_BUILD_SH"
    assert_success
}

# ── template placeholder replacement ──────────────────────────────────────────

@test "prepare-build.sh checks for assets/workspace directory" {
    run grep 'if \[ -d "\$BUILD_DIR/assets/workspace" \]' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh replaces {{IMAGE_TAG}} placeholders" {
    run grep '{{IMAGE_TAG}}' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh uses python utils.py for replacements" {
    run grep 'uv run python "\$SCRIPT_DIR/utils.py"' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh verifies placeholders were replaced" {
    run grep 'grep -r "{{IMAGE_TAG}}"' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh exits if replacements fail" {
    run grep 'exit 1' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh outputs success for replacements" {
    run grep '✓ All {{IMAGE_TAG}} placeholders replaced' "$PREPARE_BUILD_SH"
    assert_success
}

# ── version and readme updates ────────────────────────────────────────────────

@test "prepare-build.sh checks for devcontainer README" {
    run grep 'BUILD_DEVCONTAINER_README=' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh skips README update for dev builds" {
    run grep 'BUILD_VERSION.*!=.*"dev"' "$PREPARE_BUILD_SH"
    assert_success
}

@test "prepare-build.sh outputs final success message" {
    run grep '✓ Build directory prepared' "$PREPARE_BUILD_SH"
    assert_success
}

# ── error handling and validation ─────────────────────────────────────────────

@test "prepare-build.sh validates manifest sync results" {
    run grep 'if \[\[ \$failed -ne 0 \]\]' "$PREPARE_BUILD_SH"
    assert_success
}
