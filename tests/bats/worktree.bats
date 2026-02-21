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

# ── worktree-attach restart logic (#132) ───────────────────────────────────────
# Tests that worktree-attach restarts a stopped tmux session when the worktree
# directory exists. Uses WORKTREE_ATTACH_RESTART_CMD to avoid agent dependency.

@test "worktree-attach restarts stopped session when worktree dir exists" {
    command -v tmux >/dev/null 2>&1 || skip "tmux not installed"
    command -v just >/dev/null 2>&1 || skip "just not installed"

    ISSUE=999999
    REPO=$(basename "$(cd "$PROJECT_ROOT" && git rev-parse --show-toplevel)")
    WT_BASE="$(dirname "$PROJECT_ROOT")/${REPO}-worktrees"
    WT_DIR="${WT_BASE}/${ISSUE}"
    SESSION="wt-${ISSUE}"

    mkdir -p "$WT_DIR"
    tmux new-session -d -s "$SESSION" -c "$WT_DIR" "true"
    sleep 1
    if tmux has-session -t "$SESSION" 2>/dev/null; then
        tmux kill-session -t "$SESSION" 2>/dev/null || true
        skip "tmux session did not exit after 'true' (timing)"
    fi

    env WORKTREE_ATTACH_RESTART_CMD="sleep 5" timeout 2 just worktree-attach "$ISSUE" 2>/dev/null &
    sleep 1.5
    run tmux has-session -t "$SESSION" 2>/dev/null
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    rm -rf "$WT_DIR"
    rmdir "$WT_BASE" 2>/dev/null || true

    assert_success
}

@test "worktree-attach errors when neither worktree dir nor session exists" {
    command -v tmux >/dev/null 2>&1 || skip "tmux not installed"
    command -v just >/dev/null 2>&1 || skip "just not installed"

    run just worktree-attach 999998 2>&1
    assert_failure
    assert_output --partial "[ERROR]"
    assert_output --partial "No tmux session"
}
