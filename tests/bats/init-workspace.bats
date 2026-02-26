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
