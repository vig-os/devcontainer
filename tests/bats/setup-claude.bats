#!/usr/bin/env bats
# BATS tests for setup-claude.sh
#
# Tests script structure, opt-in behavior, and subcommand handling.
# No live install tests — we only verify the opt-in gate logic.

setup() {
    load test_helper
    SETUP_CLAUDE="$PROJECT_ROOT/assets/workspace/.devcontainer/scripts/setup-claude.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "setup-claude.sh is executable" {
    run test -x "$SETUP_CLAUDE"
    assert_success
}

@test "setup-claude.sh has shebang" {
    run head -1 "$SETUP_CLAUDE"
    assert_output "#!/bin/bash"
}

@test "setup-claude.sh uses strict error handling (set -euo pipefail)" {
    run grep 'set -euo pipefail' "$SETUP_CLAUDE"
    assert_success
}

# ── no subcommand / invalid subcommand ────────────────────────────────────────

@test "setup-claude.sh with no arguments exits with error" {
    run "$SETUP_CLAUDE"
    assert_failure
    assert_output --partial "Usage:"
}

@test "setup-claude.sh with invalid subcommand exits with error" {
    run "$SETUP_CLAUDE" bogus
    assert_failure
    assert_output --partial "Usage:"
}

# ── install subcommand: opt-in gate ──────────────────────────────────────────

@test "install is a no-op when CLAUDE_CODE_OAUTH_TOKEN is unset" {
    unset CLAUDE_CODE_OAUTH_TOKEN
    run "$SETUP_CLAUDE" install
    assert_success
    assert_output --partial "CLAUDE_CODE_OAUTH_TOKEN not set"
}

@test "install is a no-op when CLAUDE_CODE_OAUTH_TOKEN is empty" {
    CLAUDE_CODE_OAUTH_TOKEN="" run "$SETUP_CLAUDE" install
    assert_success
    assert_output --partial "CLAUDE_CODE_OAUTH_TOKEN not set"
}

# ── start subcommand: opt-in gate ────────────────────────────────────────────

@test "start is a no-op when CLAUDE_CODE_OAUTH_TOKEN is unset" {
    unset CLAUDE_CODE_OAUTH_TOKEN
    run "$SETUP_CLAUDE" start
    assert_success
    assert_output --partial "CLAUDE_CODE_OAUTH_TOKEN not set"
}

@test "start is a no-op when CLAUDE_CODE_OAUTH_TOKEN is empty" {
    CLAUDE_CODE_OAUTH_TOKEN="" run "$SETUP_CLAUDE" start
    assert_success
    assert_output --partial "CLAUDE_CODE_OAUTH_TOKEN not set"
}
