#!/usr/bin/env bats
# BATS tests for justfile alias resolution
#
# Verifies that short aliases (pdm-*, wt-*, gh-*) resolve to their
# target recipes regardless of which justfile defines them.

setup() {
    load test_helper
}

# ── podman aliases ───────────────────────────────────────────────────────────

@test "pdm-ps alias resolves to podman-ps" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-ps 2>&1
    assert_success
}

@test "pdm-kill alias resolves to podman-kill" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-kill 2>&1
    assert_success
}

@test "pdm-kill-all alias resolves to podman-kill-all" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-kill-all 2>&1
    assert_success
}

@test "pdm-kill-project alias resolves to podman-kill-project" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-kill-project 2>&1
    assert_success
}

@test "pdm-rmi alias resolves to podman-rmi" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-rmi 2>&1
    assert_success
}

@test "pdm-rmi-all alias resolves to podman-rmi-all" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-rmi-all 2>&1
    assert_success
}

@test "pdm-rmi-project alias resolves to podman-rmi-project" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-rmi-project 2>&1
    assert_success
}

@test "pdm-rmi-dangling alias resolves to podman-rmi-dangling" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-rmi-dangling 2>&1
    assert_success
}

@test "pdm-prune alias resolves to podman-prune" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-prune 2>&1
    assert_success
}

@test "pdm-prune-all alias resolves to podman-prune-all" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show pdm-prune-all 2>&1
    assert_success
}

# ── worktree aliases ─────────────────────────────────────────────────────────

@test "wt-start alias resolves to worktree-start" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show wt-start 2>&1
    assert_success
}

@test "wt-list alias resolves to worktree-list" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show wt-list 2>&1
    assert_success
}

@test "wt-attach alias resolves to worktree-attach" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show wt-attach 2>&1
    assert_success
}

@test "wt-stop alias resolves to worktree-stop" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show wt-stop 2>&1
    assert_success
}

@test "wt-clean alias resolves to worktree-clean" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show wt-clean 2>&1
    assert_success
}

# ── github aliases ───────────────────────────────────────────────────────────

@test "gh-i alias resolves to gh-issues" {
    command -v just >/dev/null 2>&1 || skip "just not installed"
    run just --show gh-i 2>&1
    assert_success
}
