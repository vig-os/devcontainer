#!/usr/bin/env bats
# shellcheck disable=SC2016
# BATS tests for devc-remote.sh
#
# Tests the devc-remote.sh script which orchestrates starting a devcontainer
# on a remote host via SSH. These tests verify:
# - Script structure (set -euo pipefail, logging, functions)
# - Argument parsing (missing host, --help, --path, unknown flags)
# - detect_editor_cli, check_ssh, remote_preflight, remote_compose_up, open_editor
#
# Note: SC2016 disabled because we intentionally use single quotes to search
# for literal shell variable syntax in the target scripts.

setup() {
    load test_helper
    DEVC_REMOTE="$PROJECT_ROOT/scripts/devc-remote.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "devc-remote.sh is executable" {
    run test -x "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh has shebang" {
    run head -1 "$DEVC_REMOTE"
    assert_output "#!/usr/bin/env bash"
}

@test "devc-remote.sh uses strict error handling (set -euo pipefail)" {
    run grep 'set -euo pipefail' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_info function" {
    run grep 'log_info()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_success function" {
    run grep 'log_success()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_warning function" {
    run grep 'log_warning()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_error function" {
    run grep 'log_error()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines parse_args function" {
    run grep 'parse_args()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines detect_editor_cli function" {
    run grep 'detect_editor_cli()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines check_ssh function" {
    run grep 'check_ssh()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines remote_preflight function" {
    run grep 'remote_preflight()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines remote_compose_up function" {
    run grep 'remote_compose_up()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines open_editor function" {
    run grep 'open_editor()' "$DEVC_REMOTE"
    assert_success
}

# ── parse_args: missing host ──────────────────────────────────────────────────

@test "devc-remote.sh with no args exits with error" {
    run "$DEVC_REMOTE"
    assert_failure
}

# ── parse_args: --help ───────────────────────────────────────────────────────

@test "devc-remote.sh --help exits 0" {
    run "$DEVC_REMOTE" --help
    assert_success
}

@test "devc-remote.sh --help shows usage" {
    run "$DEVC_REMOTE" --help
    assert_output --partial "USAGE"
}

# ── parse_args: unknown flag ──────────────────────────────────────────────────

@test "devc-remote.sh with unknown flag exits with error" {
    run "$DEVC_REMOTE" --unknown-flag myserver
    assert_failure
}
