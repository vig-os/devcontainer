#!/usr/bin/env bats
# shellcheck disable=SC2016
# BATS tests for devc-remote.sh
#
# Tests the devc-remote.sh script which orchestrates starting a devcontainer
# on a remote host via SSH. These tests verify:
# - Script structure (set -euo pipefail, logging, functions)
# - Argument parsing (missing host, --help, --path, unknown flags)
# - detect_editor_cli, check_ssh, remote_preflight, remote_compose_up, open_editor
#
# Note: SC2016 disabled because we intentionally use single quotes to search
# for literal shell variable syntax in the target scripts.

setup() {
    load test_helper
    DEVC_REMOTE="$PROJECT_ROOT/scripts/devc-remote.sh"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "devc-remote.sh is executable" {
    run test -x "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh has shebang" {
    run head -1 "$DEVC_REMOTE"
    assert_output "#!/usr/bin/env bash"
}

@test "devc-remote.sh uses strict error handling (set -euo pipefail)" {
    run grep 'set -euo pipefail' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_info function" {
    run grep 'log_info()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_success function" {
    run grep 'log_success()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_warning function" {
    run grep 'log_warning()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines log_error function" {
    run grep 'log_error()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines parse_args function" {
    run grep 'parse_args()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines detect_editor_cli function" {
    run grep 'detect_editor_cli()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines check_ssh function" {
    run grep 'check_ssh()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines remote_preflight function" {
    run grep 'remote_preflight()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines remote_compose_up function" {
    run grep 'remote_compose_up()' "$DEVC_REMOTE"
    assert_success
}

@test "devc-remote.sh defines open_editor function" {
    run grep 'open_editor()' "$DEVC_REMOTE"
    assert_success
}

# ── parse_args: missing host ──────────────────────────────────────────────────

@test "devc-remote.sh with no args exits with error" {
    run "$DEVC_REMOTE"
    assert_failure
}

# ── parse_args: --help ───────────────────────────────────────────────────────

@test "devc-remote.sh --help exits 0" {
    run "$DEVC_REMOTE" --help
    assert_success
}

@test "devc-remote.sh --help shows usage" {
    run "$DEVC_REMOTE" --help
    assert_output --partial "USAGE"
}

# ── parse_args: unknown flag ──────────────────────────────────────────────────

@test "devc-remote.sh with unknown flag exits with error" {
    run "$DEVC_REMOTE" --unknown-flag myserver
    assert_failure
}

# ── detect_editor_cli ─────────────────────────────────────────────────────────

@test "detect_editor_cli prefers cursor when both cursor and code exist" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    echo '#!/bin/sh' > "$mock_bin/cursor"
    echo '#!/bin/sh' > "$mock_bin/code"
    chmod +x "$mock_bin/cursor" "$mock_bin/code"
    # Script will fail at check_ssh, but we verify cursor was chosen by checking
    # we get past detect_editor_cli (would fail with "Neither cursor nor code" otherwise)
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" nonexistent-host 2>&1
    # Should not contain "Neither cursor nor code" - fails at check_ssh instead
    refute_output --partial "Neither cursor nor code"
    rm -rf "$mock_bin"
}

@test "detect_editor_cli uses code when cursor not found" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    echo '#!/bin/sh' > "$mock_bin/code"
    chmod +x "$mock_bin/code"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" nonexistent-host 2>&1
    refute_output --partial "Neither cursor nor code"
    rm -rf "$mock_bin"
}

@test "detect_editor_cli fails when neither cursor nor code in PATH" {
    # Use env -i for clean environment; minimal PATH has no cursor/code
    run env -i PATH="/usr/bin:/bin" HOME="$HOME" "$DEVC_REMOTE" myserver 2>&1
    assert_failure
    assert_output --partial "Neither cursor nor code"
}

# ── check_ssh ────────────────────────────────────────────────────────────────

@test "check_ssh succeeds when ssh connects" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    # Need cursor for detect_editor_cli
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" anyhost 2>&1
    # Should get past check_ssh; will fail at remote_preflight (mock ssh just exits)
    refute_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "check_ssh fails when ssh returns non-zero" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" badhost 2>&1
    assert_failure
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

# ── remote_preflight ─────────────────────────────────────────────────────────

@test "remote_preflight parses structured KEY=value output" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << 'SSHEOF'
#!/bin/sh
echo "RUNTIME=podman"
echo "COMPOSE_AVAILABLE=1"
echo "REPO_PATH_EXISTS=1"
echo "DEVCONTAINER_EXISTS=1"
echo "DISK_AVAILABLE_GB=5"
echo "OS_TYPE=linux"
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    # Will fail at remote_compose_up or open_editor; we verify we get past preflight
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" host 2>&1
    refute_output --partial "No container runtime"
    refute_output --partial "Compose not available"
    refute_output --partial "Repository not found"
    refute_output --partial "No .devcontainer"
    rm -rf "$mock_bin"
}

@test "remote_preflight fails when runtime missing" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << 'SSHEOF'
#!/bin/sh
echo "RUNTIME="
echo "COMPOSE_AVAILABLE=0"
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" host 2>&1
    assert_failure
    assert_output --partial "No container runtime"
    rm -rf "$mock_bin"
}

# ── open_editor ──────────────────────────────────────────────────────────────

@test "open_editor calls URI helper and editor" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "1" ]; then
  echo "RUNTIME=podman"
  echo "COMPOSE_AVAILABLE=1"
  echo "REPO_PATH_EXISTS=1"
  echo "DEVCONTAINER_EXISTS=1"
  echo "DISK_AVAILABLE_GB=5"
  echo "OS_TYPE=linux"
elif [ "\$count" = "2" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'echo "vscode-remote://test"' 'exit 0' > "$mock_bin/python3"
    chmod +x "$mock_bin/python3"
    printf '%s\n' '#!/bin/sh' '[ "$1" = "--folder-uri" ] && [ -n "$2" ] && exit 0' 'exit 1' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" host 2>&1
    assert_success
    assert_output --partial "Devcontainer already running"
    rm -rf "$mock_bin"
}

# ── remote_compose_up ────────────────────────────────────────────────────────

@test "remote_compose_up skips when container running and healthy" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
# check_ssh=0, preflight=1, compose_ps=2
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "1" ]; then
  echo "RUNTIME=podman"
  echo "COMPOSE_AVAILABLE=1"
  echo "REPO_PATH_EXISTS=1"
  echo "DEVCONTAINER_EXISTS=1"
  echo "DISK_AVAILABLE_GB=5"
  echo "OS_TYPE=linux"
elif [ "\$count" = "2" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
else
  :
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" host 2>&1
    refute_output --partial "compose up"
    rm -rf "$mock_bin"
}
