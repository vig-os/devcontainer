#!/usr/bin/env bats
# BATS tests for setup-tailscale.sh
#
# Tests script structure, opt-in behavior, and subcommand handling.
# No live Tailscale tests — we only verify the opt-in gate logic.

setup() {
    load test_helper
    SETUP_TAILSCALE="$PROJECT_ROOT/assets/workspace/.devcontainer/scripts/setup-tailscale.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "setup-tailscale.sh is executable" {
    run test -x "$SETUP_TAILSCALE"
    assert_success
}

@test "setup-tailscale.sh has shebang" {
    run head -1 "$SETUP_TAILSCALE"
    assert_output "#!/bin/bash"
}

@test "setup-tailscale.sh uses strict error handling (set -euo pipefail)" {
    run grep 'set -euo pipefail' "$SETUP_TAILSCALE"
    assert_success
}

# ── no subcommand / invalid subcommand ────────────────────────────────────────

@test "setup-tailscale.sh with no arguments exits with error" {
    run "$SETUP_TAILSCALE"
    assert_failure
    assert_output --partial "Usage:"
}

@test "setup-tailscale.sh with invalid subcommand exits with error" {
    run "$SETUP_TAILSCALE" bogus
    assert_failure
    assert_output --partial "Usage:"
}

# ── install subcommand: opt-in gate ──────────────────────────────────────────

@test "install is a no-op when TAILSCALE_AUTHKEY is unset" {
    unset TAILSCALE_AUTHKEY
    run "$SETUP_TAILSCALE" install
    assert_success
    assert_output --partial "TAILSCALE_AUTHKEY not set"
}

@test "install is a no-op when TAILSCALE_AUTHKEY is empty" {
    TAILSCALE_AUTHKEY="" run "$SETUP_TAILSCALE" install
    assert_success
    assert_output --partial "TAILSCALE_AUTHKEY not set"
}

# ── start subcommand: opt-in gate ────────────────────────────────────────────

@test "start is a no-op when TAILSCALE_AUTHKEY is unset" {
    unset TAILSCALE_AUTHKEY
    run "$SETUP_TAILSCALE" start
    assert_success
    assert_output --partial "TAILSCALE_AUTHKEY not set"
}

@test "start is a no-op when TAILSCALE_AUTHKEY is empty" {
    TAILSCALE_AUTHKEY="" run "$SETUP_TAILSCALE" start
    assert_success
    assert_output --partial "TAILSCALE_AUTHKEY not set"
}
