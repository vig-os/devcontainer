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
    [ "${CI:-}" = "true" ] && skip "tmux integration tests require interactive TTY"
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

    env WORKTREE_ATTACH_RESTART_CMD="sleep 5" timeout 3 just worktree-attach "$ISSUE" 2>/dev/null &
    sleep 2
    run tmux has-session -t "$SESSION" 2>/dev/null
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    rm -rf "$WT_DIR"
    rmdir "$WT_BASE" 2>/dev/null || true

    assert_success
}

@test "send-keys 'a' approves agent trust prompt in tmux session" {
    [ "${CI:-}" = "true" ] && skip "tmux integration tests require interactive TTY"
    command -v tmux >/dev/null 2>&1 || skip "tmux not installed"
    command -v agent >/dev/null 2>&1 || skip "cursor-agent not installed"

    SESSION="wt-test-trust-$$"
    TESTDIR="/tmp/bats-trust-$$"
    mkdir -p "$TESTDIR"

    tmux new-session -d -s "$SESSION" -c "$TESTDIR" \
        "agent chat --yolo --approve-mcps 'say hello'"
    sleep 5
    tmux send-keys -t "$SESSION" "a" 2>/dev/null || true
    sleep 5

    run tmux capture-pane -t "$SESSION" -p
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    rm -rf "$TESTDIR"

    assert_success
    assert_output --partial "Cursor Agent"
}

@test "worktree-start detects branch already checked out via worktree list" {
    # Validates the detection pattern used in worktree-start's guard:
    # git worktree list --porcelain | grep "branch refs/heads/$BRANCH"
    TMPDIR_TEST="$(mktemp -d)"
    git init "$TMPDIR_TEST/repo" >/dev/null 2>&1
    git -C "$TMPDIR_TEST/repo" config user.email "test@test.local"
    git -C "$TMPDIR_TEST/repo" config user.name "Test"
    git -C "$TMPDIR_TEST/repo" commit --allow-empty -m "init" >/dev/null 2>&1
    git -C "$TMPDIR_TEST/repo" checkout -b "feature/999997-test-branch" >/dev/null 2>&1

    # The current checkout should appear in worktree list
    run bash -c "git -C '$TMPDIR_TEST/repo' worktree list --porcelain | grep 'branch refs/heads/feature/999997-test-branch'"
    assert_success

    # A non-existent branch should NOT appear
    run bash -c "git -C '$TMPDIR_TEST/repo' worktree list --porcelain | grep 'branch refs/heads/feature/000000-nonexistent'"
    assert_failure

    rm -rf "$TMPDIR_TEST"
}

# ── derive-branch-summary.sh (#154) ───────────────────────────────────────────

@test "derive-branch-summary.sh outputs summary when BRANCH_SUMMARY_CMD succeeds" {
    DERIVE_SCRIPT="$PROJECT_ROOT/scripts/derive-branch-summary.sh"
    assert_file_exists "$DERIVE_SCRIPT"
    run test -x "$DERIVE_SCRIPT"
    assert_success

    run env BRANCH_SUMMARY_CMD="echo fix-login-bug" "$DERIVE_SCRIPT" "Fix login bug"
    assert_success
    assert_output "fix-login-bug"
}

@test "derive-branch-summary.sh times out when mock hangs" {
    DERIVE_SCRIPT="$PROJECT_ROOT/scripts/derive-branch-summary.sh"
    run env BRANCH_SUMMARY_CMD="sleep 5" DERIVE_BRANCH_TIMEOUT=2 "$DERIVE_SCRIPT" "Some title" 2>&1
    assert_failure
    assert_output --partial "[ERROR]"
    assert_output --partial "Failed to derive branch summary"
}

@test "derive-branch-summary.sh prints error with workaround when mock fails" {
    DERIVE_SCRIPT="$PROJECT_ROOT/scripts/derive-branch-summary.sh"
    run env BRANCH_SUMMARY_CMD="false" "$DERIVE_SCRIPT" "Some title" 2>&1
    assert_failure
    assert_output --partial "[ERROR]"
    assert_output --partial "Create one manually"
    assert_output --partial "gh issue develop"
}

# ── worktree-attach ───────────────────────────────────────────────────────────

@test "worktree-attach errors when neither worktree dir nor session exists" {
    [ "${CI:-}" = "true" ] && skip "tmux integration tests require interactive TTY"
    command -v tmux >/dev/null 2>&1 || skip "tmux not installed"
    command -v just >/dev/null 2>&1 || skip "just not installed"

    run just worktree-attach 999998 2>&1
    assert_failure
    assert_output --partial "[ERROR]"
    assert_output --partial "No tmux session"
}
