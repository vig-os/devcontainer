#!/usr/bin/env bats
# BATS tests for init-workspace.sh
#
# Tests script structure (executable, shebang, strict mode).

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

# ── devcontainer.json template ───────────────────────────────────────────────

@test "devcontainer.json template sets terminal.integrated.defaultProfile.linux to bash" {
    DEVCONTAINER_JSON="$PROJECT_ROOT/assets/workspace/.devcontainer/devcontainer.json"
    run python3 -c "
import json, sys
with open('$DEVCONTAINER_JSON') as f:
    data = json.load(f)
settings = data.get('customizations', {}).get('vscode', {}).get('settings', {})
profile = settings.get('terminal.integrated.defaultProfile.linux')
if profile == 'bash':
    print('bash')
    sys.exit(0)
else:
    print(f'expected bash, got {profile!r}')
    sys.exit(1)
"
    assert_success
    assert_output "bash"
}

# ── idempotent rename guard (#197) ───────────────────────────────────────────

@test "init-workspace.sh guards against nested template_project on re-run" {
    run grep -A4 'if \[\[ -d.*src/template_project' "$INIT_WORKSPACE_SH"
    assert_success
    # shellcheck disable=SC2016
    assert_output --partial 'src/${SHORT_NAME}'
    assert_output --partial 'rm -rf'
}

@test "init-workspace.sh uses rsync without fallback" {
    run grep 'rsync -av' "$INIT_WORKSPACE_SH"
    assert_success

    run grep 'if command -v rsync' "$INIT_WORKSPACE_SH"
    assert_failure
}

@test "init-workspace.sh excludes preserved files only when they exist" {
    # shellcheck disable=SC2016
    run grep -A3 'for preserved in "${PRESERVE_FILES\[@\]}"' "$INIT_WORKSPACE_SH"
    assert_success
    # shellcheck disable=SC2016
    assert_output --partial 'if [[ -e "$WORKSPACE_DIR/$preserved" ]]; then'
    # shellcheck disable=SC2016
    assert_output --partial 'EXCLUDE_ARGS+=("--exclude=$preserved")'
}
