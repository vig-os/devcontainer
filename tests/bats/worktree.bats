#!/usr/bin/env bats
# BATS tests for worktree justfile recipes
#
# Tests the branch resolution parsing used in justfile.worktree.
# gh issue develop --list returns tab-separated output: branch<TAB>URL
# The parsing must extract only the branch name (first field).

setup() {
    load test_helper
    WORKTREE_JUSTFILE="$PROJECT_ROOT/justfile.worktree"
}

# ── branch resolution parsing ────────────────────────────────────────────────

@test "justfile.worktree exists" {
    assert_file_exists "$WORKTREE_JUSTFILE"
}

@test "branch resolution extracts branch from tab-separated gh output" {
    local gh_output=$'feature/103-worktree-workflow-enhancements\thttps://github.com/vig-os/devcontainer/tree/feature/103-worktree-workflow-enhancements'
    local result
    result=$(echo "$gh_output" | head -1 | cut -f1)
    assert_equal "$result" "feature/103-worktree-workflow-enhancements"
}

@test "branch resolution handles single-field output (no tab)" {
    local gh_output='feature/103-worktree-workflow-enhancements'
    local result
    result=$(echo "$gh_output" | head -1 | cut -f1)
    assert_equal "$result" "feature/103-worktree-workflow-enhancements"
}

@test "branch resolution handles multi-line output (picks first)" {
    local gh_output=$'feature/103-enhancements\thttps://example.com\nbugfix/99-hotfix\thttps://example.com'
    local result
    result=$(echo "$gh_output" | head -1 | cut -f1)
    assert_equal "$result" "feature/103-enhancements"
}

@test "justfile.worktree uses cut -f1 for issue branch resolution" {
    run grep -E 'BRANCH=.*gh issue develop --list.*cut -f1' "$WORKTREE_JUSTFILE"
    assert_success
}

@test "justfile.worktree uses cut -f1 for parent branch resolution" {
    run grep -E 'BASE=.*gh issue develop --list.*cut -f1' "$WORKTREE_JUSTFILE"
    assert_success
}
