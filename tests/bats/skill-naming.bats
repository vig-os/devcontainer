#!/usr/bin/env bats
# BATS tests for scripts/check-skill-names.sh
#
# Validates that the skill naming checker correctly accepts valid names
# (lowercase letters, digits, hyphens, underscores) and rejects invalid
# names (colons, dots, uppercase, spaces, etc.).

setup() {
    load test_helper
    CHECK_SCRIPT="$PROJECT_ROOT/scripts/check-skill-names.sh"
}

# ── script basics ─────────────────────────────────────────────────────────────

@test "check-skill-names.sh exists and is executable" {
    assert_file_exists "$CHECK_SCRIPT"
    run test -x "$CHECK_SCRIPT"
    assert_success
}

# ── valid names ───────────────────────────────────────────────────────────────

@test "accepts underscore-separated names (ci_check)" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/ci_check"
    touch "$dir/ci_check/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_success
    rm -rf "$dir"
}

@test "accepts hyphenated names (pr_post-merge)" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/pr_post-merge"
    touch "$dir/pr_post-merge/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_success
    rm -rf "$dir"
}

@test "accepts multiple valid skill directories" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/ci_check" "$dir/code_tdd" "$dir/worktree_solve-and-pr"
    touch "$dir/ci_check/SKILL.md" "$dir/code_tdd/SKILL.md" "$dir/worktree_solve-and-pr/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_success
    rm -rf "$dir"
}

@test "accepts empty skills directory (no subdirs)" {
    local dir
    dir="$(mktemp -d)"
    run "$CHECK_SCRIPT" "$dir"
    assert_success
    rm -rf "$dir"
}

# ── invalid names ─────────────────────────────────────────────────────────────

@test "rejects colon-separated names (ci:check)" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/ci:check"
    touch "$dir/ci:check/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_failure
    assert_output --partial "ci:check"
    rm -rf "$dir"
}

@test "rejects names with dots (ci.check)" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/ci.check"
    touch "$dir/ci.check/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_failure
    assert_output --partial "ci.check"
    rm -rf "$dir"
}

@test "rejects names with uppercase (CI_Check)" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/CI_Check"
    touch "$dir/CI_Check/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_failure
    assert_output --partial "CI_Check"
    rm -rf "$dir"
}

@test "rejects names with spaces" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/ci check"
    touch "$dir/ci check/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_failure
    assert_output --partial "ci check"
    rm -rf "$dir"
}

@test "reports all invalid names when multiple exist" {
    local dir
    dir="$(mktemp -d)"
    mkdir -p "$dir/ci:check" "$dir/code_tdd" "$dir/Design:Plan"
    touch "$dir/ci:check/SKILL.md" "$dir/code_tdd/SKILL.md" "$dir/Design:Plan/SKILL.md"
    run "$CHECK_SCRIPT" "$dir"
    assert_failure
    assert_output --partial "ci:check"
    assert_output --partial "Design:Plan"
    rm -rf "$dir"
}

# ── real repo validation ──────────────────────────────────────────────────────

@test "all skills in .cursor/skills/ have valid names" {
    run "$CHECK_SCRIPT" "$PROJECT_ROOT/.cursor/skills"
    assert_success
}

@test "canary: injecting a bad name into real skills dir is caught and cleaned up" {
    local canary="$PROJECT_ROOT/.cursor/skills/bad:canary"
    mkdir -p "$canary"
    touch "$canary/SKILL.md"

    run "$CHECK_SCRIPT" "$PROJECT_ROOT/.cursor/skills"
    rm -rf "$canary"

    assert_failure
    assert_output --partial "bad:canary"
}
