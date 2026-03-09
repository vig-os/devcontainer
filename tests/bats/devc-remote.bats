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

# ── parse_args: gh: target syntax ────────────────────────────────────────────

@test "parse_args recognizes gh:org/repo as second positional arg" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver gh:vig-os/fd5 2>&1
    # Should get past parse_args (fail at check_ssh, not "Unexpected argument")
    refute_output --partial "Unexpected argument"
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "parse_args recognizes gh:org/repo:branch with branch extraction" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver gh:vig-os/fd5:feature/my-branch 2>&1
    refute_output --partial "Unexpected argument"
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "parse_args accepts host:path combined with gh:org/repo" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver:~/custom/path gh:vig-os/fd5 2>&1
    refute_output --partial "Unexpected argument"
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "parse_args rejects gh: with missing repo" {
    run "$DEVC_REMOTE" --open none myserver gh: 2>&1
    assert_failure
    assert_output --partial "Invalid gh: target"
}

# ── remote_clone_project ─────────────────────────────────────────────────────

@test "remote_clone_project clones repo on fresh target" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "1" ]; then
  echo "CLONE_PATH=/home/user/Projects/fd5"
  echo "CLONE_STATUS=cloned"
elif [ "\$count" = "2" ]; then
  echo "RUNTIME=podman"
  echo "COMPOSE_AVAILABLE=1"
  echo "REPO_PATH_EXISTS=1"
  echo "DEVCONTAINER_EXISTS=1"
  echo "DISK_AVAILABLE_GB=5"
  echo "OS_TYPE=linux"
elif [ "\$count" = "3" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver gh:vig-os/fd5 2>&1
    assert_success
    assert_output --partial "Cloning vig-os/fd5"
    rm -rf "$mock_bin"
}

@test "remote_clone_project fetches existing repo" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "1" ]; then
  echo "CLONE_PATH=/home/user/Projects/fd5"
  echo "CLONE_STATUS=fetched"
elif [ "\$count" = "2" ]; then
  echo "RUNTIME=podman"
  echo "COMPOSE_AVAILABLE=1"
  echo "REPO_PATH_EXISTS=1"
  echo "DEVCONTAINER_EXISTS=1"
  echo "DISK_AVAILABLE_GB=5"
  echo "OS_TYPE=linux"
elif [ "\$count" = "3" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver gh:vig-os/fd5 2>&1
    assert_success
    assert_output --partial "Fetching vig-os/fd5"
    rm -rf "$mock_bin"
}

@test "remote_clone_project checks out specified branch" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "1" ]; then
  echo "CLONE_PATH=/home/user/Projects/fd5"
  echo "CLONE_STATUS=cloned"
  echo "CLONE_BRANCH=feature/my-branch"
elif [ "\$count" = "2" ]; then
  echo "RUNTIME=podman"
  echo "COMPOSE_AVAILABLE=1"
  echo "REPO_PATH_EXISTS=1"
  echo "DEVCONTAINER_EXISTS=1"
  echo "DISK_AVAILABLE_GB=5"
  echo "OS_TYPE=linux"
elif [ "\$count" = "3" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver gh:vig-os/fd5:feature/my-branch 2>&1
    assert_success
    assert_output --partial "Checked out feature/my-branch"
    rm -rf "$mock_bin"
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
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    # Unset TERM_PROGRAM so auto-detect falls through to CLI availability check
    TERM_PROGRAM='' PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" nonexistent-host 2>&1
    # Auto-detect should pick cursor; verify it gets past detect_editor_cli
    assert_output --partial "IDE: cursor"
    rm -rf "$mock_bin"
}

@test "detect_editor_cli uses code when cursor not found" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    echo '#!/bin/sh' > "$mock_bin/code"
    chmod +x "$mock_bin/code"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    # Use env -i to ensure system cursor is not in PATH
    run env -i PATH="$mock_bin" HOME="$HOME" TERM_PROGRAM= /bin/bash "$DEVC_REMOTE" nonexistent-host 2>&1
    assert_output --partial "IDE: code"
    rm -rf "$mock_bin"
}

@test "detect_editor_cli falls back to ssh when neither cursor nor code in PATH" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    # Run via /bin/bash so script execution does not depend on PATH/shebang lookup
    run env -i PATH="$mock_bin" HOME="$HOME" /bin/bash "$DEVC_REMOTE" myserver 2>&1
    # Should not error about missing CLI — falls back to ssh mode
    refute_output --partial "cursor CLI not found"
    refute_output --partial "code CLI not found"
    assert_output --partial "No IDE CLI found, falling back to --open ssh"
    # Fails at check_ssh, not editor detection
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

# ── --open flag ──────────────────────────────────────────────────────────────

@test "--open none skips editor detection" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    # No cursor/code in PATH, but --open none should skip detection
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none myserver 2>&1
    refute_output --partial "cursor CLI not found"
    refute_output --partial "code CLI not found"
    # Should fail at check_ssh, not editor detection
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "--open code fails when code not in PATH" {
    local empty_path
    empty_path="$(mktemp -d)"
    run env -i PATH="$empty_path" HOME="$HOME" /bin/bash "$DEVC_REMOTE" --open code myserver 2>&1
    assert_failure
    assert_output --partial "code CLI not found"
    rm -rf "$empty_path"
}

@test "--open ssh skips editor detection" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open ssh myserver 2>&1
    refute_output --partial "cursor CLI not found"
    refute_output --partial "code CLI not found"
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "--open auto detects cursor from TERM_PROGRAM" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    TERM_PROGRAM=cursor PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" myserver 2>&1
    assert_output --partial "IDE: cursor"
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "--open auto falls back to ssh for WezTerm TERM_PROGRAM" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    TERM_PROGRAM=WezTerm PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" myserver 2>&1
    refute_output --partial "cursor CLI not found"
    assert_output --partial "Mode: SSH"
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

@test "--open invalid value rejected" {
    run "$DEVC_REMOTE" --open vim myserver 2>&1
    assert_failure
    assert_output --partial "must be auto, cursor, code, ssh, or none"
}

# ── --yes flag ──────────────────────────────────────────────────────────────

@test "--yes flag is accepted" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    printf '%s\n' '#!/bin/sh' 'exit 1' > "$mock_bin/ssh"
    chmod +x "$mock_bin/ssh"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --yes --open cursor myserver 2>&1
    # Should fail at check_ssh, not argument parsing
    assert_output --partial "Cannot connect to"
    rm -rf "$mock_bin"
}

# ── inject_tailscale_key ────────────────────────────────────────────────────

@test "wait_for_tailscale defines function" {
    run grep 'wait_for_tailscale()' "$DEVC_REMOTE"
    assert_success
}

@test "read_workspace_folder defines function" {
    run grep 'read_workspace_folder()' "$DEVC_REMOTE"
    assert_success
}

# ── inject_claude_auth ─────────────────────────────────────────────────────

@test "inject_claude_auth defines function" {
    run grep 'inject_claude_auth()' "$DEVC_REMOTE"
    assert_success
}

@test "inject_claude_auth is called in main" {
    run grep 'inject_claude_auth' "$DEVC_REMOTE"
    assert_success
    # Should appear at least twice: definition + call
    local count
    count=$(grep -c 'inject_claude_auth' "$DEVC_REMOTE")
    [ "$count" -ge 2 ]
}

@test "inject_claude_auth skips when CLAUDE_CODE_OAUTH_TOKEN unset" {
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
    # Run WITHOUT CLAUDE_CODE_OAUTH_TOKEN — inject_claude_auth should not mention Claude
    PATH="$mock_bin:$PATH" run env -u CLAUDE_CODE_OAUTH_TOKEN "$DEVC_REMOTE" --open none host 2>&1
    assert_success
    refute_output --partial "Claude"
    rm -rf "$mock_bin"
}

# ── inject_tailscale_key ────────────────────────────────────────────────────

@test "inject_tailscale_key defines function" {
    run grep 'inject_tailscale_key()' "$DEVC_REMOTE"
    assert_success
}

@test "inject_tailscale_key is called in main" {
    run grep 'inject_tailscale_key' "$DEVC_REMOTE"
    assert_success
    # Should appear at least twice: definition + call
    local count
    count=$(grep -c 'inject_tailscale_key' "$DEVC_REMOTE")
    [ "$count" -ge 2 ]
}

@test "inject_tailscale_key skips when TS_CLIENT_ID unset" {
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
elif [ "\$count" = "4" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'echo "vscode-remote://test"' 'exit 0' > "$mock_bin/python3"
    chmod +x "$mock_bin/python3"
    printf '%s\n' '#!/bin/sh' '[ "$1" = "--folder-uri" ] && [ -n "$2" ] && exit 0' 'exit 1' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    # Run WITHOUT TS_CLIENT_ID — inject_tailscale_key should not mention Tailscale
    # Use --open none to avoid ssh mode triggering wait_for_tailscale output
    PATH="$mock_bin:$PATH" run env -u TS_CLIENT_ID -u TS_CLIENT_SECRET "$DEVC_REMOTE" --open none host 2>&1
    assert_success
    refute_output --partial "Tailscale"
    rm -rf "$mock_bin"
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
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none anyhost 2>&1
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
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none badhost 2>&1
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
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none host 2>&1
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
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none host 2>&1
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
elif [ "\$count" = "4" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'echo "vscode-remote://test"' 'exit 0' > "$mock_bin/python3"
    chmod +x "$mock_bin/python3"
    printf '%s\n' '#!/bin/sh' '[ "$1" = "--folder-uri" ] && [ -n "$2" ] && exit 0' 'exit 1' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open cursor host 2>&1
    assert_success
    assert_output --partial "Devcontainer already running"
    rm -rf "$mock_bin"
}

# ── main: step-level progress logging ────────────────────────────────────────

@test "main logs progress for each pipeline step" {
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
elif [ "\$count" = "4" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'echo "vscode-remote://test"' 'exit 0' > "$mock_bin/python3"
    chmod +x "$mock_bin/python3"
    printf '%s\n' '#!/bin/sh' '[ "$1" = "--folder-uri" ] && [ -n "$2" ] && exit 0' 'exit 1' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open cursor host 2>&1
    assert_success
    assert_output --partial "IDE:"
    assert_output --partial "SSH"
    assert_output --partial "pre-flight"
    rm -rf "$mock_bin"
}

# ── remote_compose_up ────────────────────────────────────────────────────────

# ── lifecycle functions (Unit 2) ──────────────────────────────────────────────

@test "run_container_lifecycle defines function" {
    run grep 'run_container_lifecycle()' "$DEVC_REMOTE"
    assert_success
}

@test "run_container_lifecycle is called in main" {
    run grep 'run_container_lifecycle' "$DEVC_REMOTE"
    assert_success
    local count
    count=$(grep -c 'run_container_lifecycle' "$DEVC_REMOTE")
    [ "$count" -ge 2 ]
}

@test "prepare_remote defines function" {
    run grep 'prepare_remote()' "$DEVC_REMOTE"
    assert_success
}

@test "read_compose_files defines function" {
    run grep 'read_compose_files()' "$DEVC_REMOTE"
    assert_success
}

@test "compose_cmd_with_files defines function" {
    run grep 'compose_cmd_with_files()' "$DEVC_REMOTE"
    assert_success
}


# ── --bootstrap flag parsing ──────────────────────────────────────────────

@test "--bootstrap requires ssh-host argument" {
    run "$DEVC_REMOTE" --bootstrap
    assert_failure
    assert_output --partial "Missing required argument"
}

@test "--bootstrap sets BOOTSTRAP_MODE" {
    run grep 'BOOTSTRAP_MODE=' "$DEVC_REMOTE"
    assert_success
}

@test "--bootstrap defines bootstrap_remote function" {
    run grep 'bootstrap_remote()' "$DEVC_REMOTE"
    assert_success
}

@test "--bootstrap with host runs bootstrap flow" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
# check_ssh
if [ "\$count" = "0" ]; then
  exit 0
fi
# bootstrap_check_config: config does not exist
if [ "\$count" = "1" ]; then
  echo "CONFIG_EXISTS=0"
  exit 0
fi
# bootstrap_write_config
if [ "\$count" = "2" ]; then
  exit 0
fi
# bootstrap_forward_ghcr_auth
if [ "\$count" = "3" ]; then
  exit 0
fi
# bootstrap_clone_and_build
if [ "\$count" = "4" ]; then
  exit 0
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    # Provide scp mock (for GHCR auth forwarding)
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/scp"
    chmod +x "$mock_bin/scp"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --bootstrap --yes myserver 2>&1
    assert_success
    assert_output --partial "Bootstrap"
    rm -rf "$mock_bin"
}

@test "--bootstrap first-run creates config on remote" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
# check_ssh
if [ "\$count" = "0" ]; then exit 0; fi
# bootstrap_check_config: no config
if [ "\$count" = "1" ]; then
  echo "CONFIG_EXISTS=0"
  exit 0
fi
# write config
if [ "\$count" = "2" ]; then exit 0; fi
# clone/build
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/scp"
    chmod +x "$mock_bin/scp"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --bootstrap --yes myserver 2>&1
    assert_success
    assert_output --partial "Config written"
    rm -rf "$mock_bin"
}

@test "--bootstrap re-run reads existing config without re-prompting" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
# check_ssh
if [ "\$count" = "0" ]; then exit 0; fi
# bootstrap_check_config: config exists
if [ "\$count" = "1" ]; then
  echo "CONFIG_EXISTS=1"
  echo "PROJECTS_DIR=~/Projects"
  echo "DEVCONTAINER_REPO=vig-os/devcontainer"
  echo "DEVCONTAINER_PATH=~/Projects/devcontainer"
  echo "IMAGE_TAG=dev"
  echo "REGISTRY=ghcr.io/vig-os/devcontainer"
  exit 0
fi
# pull + rebuild
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/scp"
    chmod +x "$mock_bin/scp"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --bootstrap myserver 2>&1
    assert_success
    assert_output --partial "existing, not modified"
    rm -rf "$mock_bin"
}

@test "--bootstrap forwards GHCR auth to remote" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    # Create fake local auth file
    local fake_home
    fake_home="$(mktemp -d)"
    mkdir -p "$fake_home/.config/containers"
    echo '{"auths":{}}' > "$fake_home/.config/containers/auth.json"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "0" ]; then exit 0; fi
if [ "\$count" = "1" ]; then
  echo "CONFIG_EXISTS=0"
  exit 0
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    # scp mock that records what was copied
    cat > "$mock_bin/scp" << SCPEOF
#!/bin/sh
echo "SCP_CALLED: \$@" >> "${mock_bin}/scp_log"
exit 0
SCPEOF
    chmod +x "$mock_bin/scp"
    HOME="$fake_home" PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --bootstrap --yes myserver 2>&1
    assert_success
    assert_output --partial "GHCR auth"
    rm -rf "$mock_bin" "$fake_home"
}

@test "--bootstrap builds devcontainer image on remote" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
counter="${mock_bin}/ssh_counter"
count=\$(cat "\$counter" 2>/dev/null || echo 0)
echo \$((count + 1)) > "\$counter"
if [ "\$count" = "0" ]; then exit 0; fi
if [ "\$count" = "1" ]; then
  echo "CONFIG_EXISTS=0"
  exit 0
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/scp"
    chmod +x "$mock_bin/scp"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --bootstrap --yes myserver 2>&1
    assert_success
    assert_output --partial "Building devcontainer image"
    rm -rf "$mock_bin"
}

# ── remote_compose_up ────────────────────────────────────────────────────────

@test "remote_compose_up skips when container running and healthy" {
    local mock_bin
    mock_bin="$(mktemp -d)"
    cat > "$mock_bin/ssh" << SSHEOF
#!/bin/sh
# check_ssh=0, preflight=1, prepare_remote=2+3, compose_ps=4
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
elif [ "\$count" = "4" ]; then
  echo '[{"Service":"devcontainer","State":"running","Health":"healthy"}]'
else
  :
fi
exit 0
SSHEOF
    chmod +x "$mock_bin/ssh"
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$mock_bin/cursor"
    chmod +x "$mock_bin/cursor"
    PATH="$mock_bin:$PATH" run "$DEVC_REMOTE" --open none host 2>&1
    refute_output --partial "compose up"
    rm -rf "$mock_bin"
}
