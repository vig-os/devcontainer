#!/usr/bin/env bats
# shellcheck disable=SC2016
# BATS tests for init.sh
#
# Tests the init.sh script which checks and installs development dependencies.
# These tests verify:
# - Command-line flag parsing (--check, --yes, --help, --verbose)
# - OS detection (macOS, Debian/Ubuntu, Fedora, Alpine)
# - YAML parsing of requirements.yaml
# - Dependency checking
# - Installation path detection
# - Error handling
#
# Note: SC2016 disabled because we intentionally use single quotes to search
# for literal shell variable syntax (e.g., '$VAR') in the target scripts.

setup() {
    load test_helper
    INIT_SH="$PROJECT_ROOT/scripts/init.sh"
    REQUIREMENTS_YAML="$PROJECT_ROOT/scripts/requirements.yaml"
}

# ── script structure ──────────────────────────────────────────────────────────

@test "init.sh is executable" {
    run test -x "$INIT_SH"
    assert_success
}

@test "init.sh has shebang" {
    run head -1 "$INIT_SH"
    assert_output "#!/usr/bin/env bash"
}

# ── error handling ────────────────────────────────────────────────────────────

@test "init.sh uses strict error handling (set -euo pipefail)" {
    run grep 'set -euo pipefail' "$INIT_SH"
    assert_success
}

# ── flag parsing ──────────────────────────────────────────────────────────────

@test "init.sh initializes CHECK_ONLY flag as false" {
    run grep 'CHECK_ONLY=false' "$INIT_SH"
    assert_success
}

@test "init.sh initializes AUTO_YES flag as false" {
    run grep 'AUTO_YES=false' "$INIT_SH"
    assert_success
}

@test "init.sh initializes VERBOSE flag as false" {
    run grep 'VERBOSE=false' "$INIT_SH"
    assert_success
}

@test "init.sh supports --check flag" {
    run grep '\-\-check' "$INIT_SH"
    assert_success
}

@test "init.sh supports --yes flag" {
    run grep '\-\-yes' "$INIT_SH"
    assert_success
}

@test "init.sh supports --help flag" {
    run grep '\-\-help' "$INIT_SH"
    assert_success
}

@test "init.sh supports --verbose flag" {
    run grep '\-\-verbose' "$INIT_SH"
    assert_success
}

# ── os detection ──────────────────────────────────────────────────────────────

@test "init.sh defines detect_os function" {
    run grep 'detect_os()' "$INIT_SH"
    assert_success
}

@test "init.sh detects OS using uname -s" {
    run grep 'uname -s' "$INIT_SH"
    assert_success
}

@test "init.sh detects macOS as 'Darwin'" {
    run grep 'Darwin)' "$INIT_SH"
    assert_success
}

@test "init.sh returns 'macos' for macOS" {
    run grep 'os_type="macos"' "$INIT_SH"
    assert_success
}

@test "init.sh detects Linux" {
    run grep 'Linux)' "$INIT_SH"
    assert_success
}

@test "init.sh reads /etc/os-release on Linux" {
    run grep 'os-release' "$INIT_SH"
    assert_success
}

@test "init.sh detects Debian/Ubuntu" {
    run grep 'debian' "$INIT_SH"
    assert_success
}

@test "init.sh detects Fedora/RHEL/CentOS" {
    run grep 'fedora' "$INIT_SH"
    assert_success
}

@test "init.sh detects Alpine Linux" {
    run grep 'alpine)' "$INIT_SH"
    assert_success
}

@test "init.sh detects Arch Linux" {
    run grep 'arch' "$INIT_SH"
    assert_success
}

@test "init.sh returns 'unknown' for unrecognized OS" {
    run grep 'os_type="unknown"' "$INIT_SH"
    assert_success
}

# ── os pretty name ────────────────────────────────────────────────────────────

@test "init.sh defines get_os_pretty_name function" {
    run grep 'get_os_pretty_name()' "$INIT_SH"
    assert_success
}

@test "init.sh gets macOS version via sw_vers" {
    run grep 'sw_vers -productVersion' "$INIT_SH"
    assert_success
}

@test "init.sh reads PRETTY_NAME from /etc/os-release" {
    run grep 'PRETTY_NAME' "$INIT_SH"
    assert_success
}

# ── yaml parsing ──────────────────────────────────────────────────────────────

@test "init.sh defines parse_requirements function" {
    run grep 'parse_requirements()' "$INIT_SH"
    assert_success
}

@test "init.sh skips comment lines in YAML" {
    run grep '# Skip comments' "$INIT_SH"
    assert_success
}

@test "init.sh skips empty lines in YAML" {
    run grep '# Skip.*empty' "$INIT_SH"
    assert_success
}

@test "init.sh detects dependencies section" {
    run grep 'dependencies:' "$INIT_SH"
    assert_success
}

@test "init.sh detects optional section" {
    run grep 'optional:' "$INIT_SH"
    assert_success
}

@test "init.sh parses dependency name" {
    run grep 'name:' "$INIT_SH"
    assert_success
}

@test "init.sh parses dependency version" {
    run grep 'version:' "$INIT_SH"
    assert_success
}

@test "init.sh parses dependency purpose" {
    run grep 'purpose:' "$INIT_SH"
    assert_success
}

@test "init.sh parses dependency required flag" {
    run grep 'required:' "$INIT_SH"
    assert_success
}

@test "init.sh parses check command" {
    run grep 'check:' "$INIT_SH"
    assert_success
}

@test "init.sh parses install commands" {
    run grep 'install:' "$INIT_SH"
    assert_success
}

@test "init.sh supports macOS-specific install" {
    run grep 'macos:' "$INIT_SH"
    assert_success
}

@test "init.sh supports Debian-specific install" {
    run grep 'debian:' "$INIT_SH"
    assert_success
}

@test "init.sh supports Fedora-specific install" {
    run grep 'fedora:' "$INIT_SH"
    assert_success
}

@test "init.sh supports Alpine-specific install" {
    run grep 'alpine:' "$INIT_SH"
    assert_success
}

@test "init.sh supports platform-agnostic install" {
    run grep 'all:' "$INIT_SH"
    assert_success
}

@test "init.sh supports manual install instructions" {
    run grep 'manual:' "$INIT_SH"
    assert_success
}

# ── requirements file ─────────────────────────────────────────────────────────

@test "requirements.yaml exists" {
    run test -f "$REQUIREMENTS_YAML"
    assert_success
}

@test "requirements.yaml is readable" {
    run test -r "$REQUIREMENTS_YAML"
    assert_success
}

@test "requirements.yaml contains dependencies section" {
    run grep '^dependencies:' "$REQUIREMENTS_YAML"
    assert_success
}

@test "requirements.yaml has at least one dependency" {
    run grep '^  - name:' "$REQUIREMENTS_YAML"
    assert_success
}

@test "requirements.yaml dependencies have version" {
    run grep 'version:' "$REQUIREMENTS_YAML"
    assert_success
}

@test "requirements.yaml dependencies have purpose" {
    run grep 'purpose:' "$REQUIREMENTS_YAML"
    assert_success
}

# ── path setup ────────────────────────────────────────────────────────────────

@test "init.sh derives SCRIPT_DIR from script path" {
    run grep 'SCRIPT_DIR=' "$INIT_SH"
    assert_success
}

@test "init.sh derives PROJECT_ROOT as parent of SCRIPT_DIR" {
    run grep 'PROJECT_ROOT=' "$INIT_SH"
    assert_success
}

@test "init.sh sets REQUIREMENTS_FILE path" {
    run grep 'REQUIREMENTS_FILE=' "$INIT_SH"
    assert_success
}

@test "init.sh defines PYTHON_VERSION" {
    run grep 'PYTHON_VERSION=' "$INIT_SH"
    assert_success
}

# ── output functions ─────────────────────────────────────────────────────────

@test "init.sh defines print_header function" {
    run grep 'print_header()' "$INIT_SH"
    assert_success
}

@test "init.sh defines print_section function" {
    run grep 'print_section()' "$INIT_SH"
    assert_success
}

@test "init.sh defines log_info function" {
    run grep 'log_info()' "$INIT_SH"
    assert_success
}

@test "init.sh defines log_success function" {
    run grep 'log_success()' "$INIT_SH"
    assert_success
}

@test "init.sh defines log_warning function" {
    run grep 'log_warning()' "$INIT_SH"
    assert_success
}

@test "init.sh defines log_error function" {
    run grep 'log_error()' "$INIT_SH"
    assert_success
}

@test "init.sh defines log_debug function" {
    run grep 'log_debug()' "$INIT_SH"
    assert_success
}

# ── user interaction ──────────────────────────────────────────────────────────

@test "init.sh defines confirm function" {
    run grep 'confirm()' "$INIT_SH"
    assert_success
}

@test "init.sh confirm function uses AUTO_YES" {
    run grep 'if \$AUTO_YES' "$INIT_SH"
    assert_success
}

@test "init.sh confirm function reads user input" {
    run grep 'read -r response' "$INIT_SH"
    assert_success
}

# ── color support ─────────────────────────────────────────────────────────────

@test "init.sh defines RED color" {
    run grep "RED=" "$INIT_SH"
    assert_success
}

@test "init.sh defines GREEN color" {
    run grep "GREEN=" "$INIT_SH"
    assert_success
}

@test "init.sh defines YELLOW color" {
    run grep "YELLOW=" "$INIT_SH"
    assert_success
}

@test "init.sh defines BLUE color" {
    run grep "BLUE=" "$INIT_SH"
    assert_success
}

@test "init.sh defines CYAN color" {
    run grep "CYAN=" "$INIT_SH"
    assert_success
}

@test "init.sh defines BOLD style" {
    run grep "BOLD=" "$INIT_SH"
    assert_success
}

@test "init.sh defines NC (no color) reset" {
    run grep "NC=" "$INIT_SH"
    assert_success
}

# ── devcontainer local install ───────────────────────────────────────────────

@test "requirements.yaml devcontainer check falls back to node_modules/.bin" {
    run grep 'node_modules/.bin/devcontainer' "$REQUIREMENTS_YAML"
    assert_success
}

@test "requirements.yaml devcontainer does not use npm install -g" {
    run grep 'npm install -g.*devcontainer' "$REQUIREMENTS_YAML"
    assert_failure
}
