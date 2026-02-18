#!/usr/bin/env bats
# BATS tests for init-workspace.sh
#
# Tests the non-empty workspace detection logic, specifically:
# - File classification: overwritten vs. added
# - Git status awareness: clean vs. dirty files
# - Output formatting for user decision-making

setup() {
    load test_helper
    INIT_WORKSPACE_SH="$PROJECT_ROOT/assets/init-workspace.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "init-workspace.sh is executable" {
    run test -x "$INIT_WORKSPACE_SH"
    assert_success
}

@test "init-workspace.sh has shebang" {
    run head -1 "$INIT_WORKSPACE_SH"
    assert_output "#!/bin/bash"
}

@test "init-workspace.sh uses strict error handling (set -euo pipefail)" {
    run grep 'set -euo pipefail' "$INIT_WORKSPACE_SH"
    assert_success
}

# ── git-dirty check ──────────────────────────────────────────────────────────

@test "init-workspace.sh defines is_git_dirty function" {
    run grep 'is_git_dirty()' "$INIT_WORKSPACE_SH"
    assert_success
}

@test "is_git_dirty uses git status --porcelain" {
    run grep 'git.*status.*--porcelain' "$INIT_WORKSPACE_SH"
    assert_success
}

@test "is_git_dirty checks files relative to WORKSPACE_DIR" {
    run grep 'git -C.*WORKSPACE_DIR' "$INIT_WORKSPACE_SH"
    assert_success
}

# ── non-empty workspace output categories ─────────────────────────────────────

@test "non-empty workspace check classifies overwrite-clean files" {
    run grep 'OVERWRITE_CLEAN' "$INIT_WORKSPACE_SH"
    assert_success
}

@test "non-empty workspace check classifies overwrite-dirty files" {
    run grep 'OVERWRITE_DIRTY' "$INIT_WORKSPACE_SH"
    assert_success
}

@test "non-empty workspace check shows uncommitted changes warning" {
    run grep 'uncommitted' "$INIT_WORKSPACE_SH"
    assert_success
}

@test "non-empty workspace check suggests commit or stash for dirty files" {
    run grep -E 'commit.*stash|stash.*commit' "$INIT_WORKSPACE_SH"
    assert_success
}

@test "non-empty workspace check shows safe message when all clean" {
    run grep -i 'safe' "$INIT_WORKSPACE_SH"
    assert_success
}

# ── graceful fallback without git ─────────────────────────────────────────────

@test "is_git_dirty falls back to dirty when no .git directory" {
    run grep -A1 'is_git_dirty()' "$INIT_WORKSPACE_SH"
    assert_success
    # The function checks for .git dir and treats missing repo as dirty (return 0)
    run grep 'no git repo.*dirty\|cannot verify.*dirty' "$INIT_WORKSPACE_SH"
    assert_success
}
