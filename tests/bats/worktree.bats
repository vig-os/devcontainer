#!/usr/bin/env bats
# BATS tests for worktree-related scripts
#
# Tests scripts/resolve-branch.sh which extracts a branch name from
# the tab-separated output of `gh issue develop --list`.

setup() {
    load test_helper
    RESOLVE_BRANCH="$PROJECT_ROOT/scripts/resolve-branch.sh"
}

# ── resolve-branch.sh ────────────────────────────────────────────────────────

@test "resolve-branch.sh is executable" {
    assert_file_exists "$RESOLVE_BRANCH"
    run test -x "$RESOLVE_BRANCH"
    assert_success
}

@test "extracts branch from tab-separated output" {
    run bash -c 'printf "feature/103-enhancements\thttps://github.com/org/repo/tree/feature/103-enhancements\n" | "$1"' _ "$RESOLVE_BRANCH"
    assert_success
    assert_output "feature/103-enhancements"
}

@test "handles output with no tab (branch name only)" {
    run bash -c 'printf "feature/103-enhancements\n" | "$1"' _ "$RESOLVE_BRANCH"
    assert_success
    assert_output "feature/103-enhancements"
}

@test "picks first line when multiple branches returned" {
    run bash -c 'printf "feature/103-first\thttps://example.com\nbugfix/99-second\thttps://example.com\n" | "$1"' _ "$RESOLVE_BRANCH"
    assert_success
    assert_output "feature/103-first"
}

@test "returns empty on empty input" {
    run bash -c 'printf "" | "$1"' _ "$RESOLVE_BRANCH"
    assert_success
    assert_output ""
}
