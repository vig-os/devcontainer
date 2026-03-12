#!/usr/bin/env bats
# BATS tests for justfile
#
# Tests the justfile recipes and configuration.
# These tests verify:
# - Default recipe lists available commands

setup() {
    load test_helper
}

@test "just without arguments lists available recipes" {
    run just
    assert_success
    assert_output --partial "Available recipes"
}

@test "prepare-release dispatches workflow from dev ref" {
    run bash -lc "awk '/^prepare-release version ref=\"\" \\*flags:/{flag=1; next} /^$/{if(flag){exit}} flag' justfile | grep -Fq -- 'REF=\"dev\"'"
    assert_success
}

@test "finalize-release dispatches workflow from release branch ref" {
    run bash -lc "awk '/^finalize-release version ref=\"\" \\*flags:/{flag=1; next} /^$/{if(flag){exit}} flag' justfile | grep -Fq -- 'REF=\"release/{{ version }}\"'"
    assert_success
}

@test "publish-candidate dispatches workflow from release branch ref" {
    run bash -lc "awk '/^publish-candidate version ref=\"\" \\*flags:/{flag=1; next} /^$/{if(flag){exit}} flag' justfile | grep -Fq -- 'REF=\"release/{{ version }}\"'"
    assert_success
}
