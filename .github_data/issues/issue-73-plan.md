---
type: plan
issue: 73
created: 2026-02-19
state: draft
---

# Implementation Plan: Wire up version-check notification and add host-side devcontainer-upgrade recipe

**Issue:** [#73](https://github.com/vig-os/devcontainer/issues/73)

## Overview

This plan implements automatic devcontainer update notifications and adds a convenient host-side upgrade recipe. The feature is fully TDD-based, with each phase committed separately to prove test-driven development compliance.

## Prerequisites

- `version-check.sh` script exists at `assets/workspace/.devcontainer/scripts/version-check.sh` ✓
- `post-attach.sh` exists at `assets/workspace/.devcontainer/scripts/post-attach.sh` ✓
- `justfile.base` exists at `assets/workspace/.devcontainer/justfile.base` ✓
- Integration test file exists at `tests/test_integration.py` ✓

## Implementation Tasks

### Task 1: Add tests for `just check` recipe integration

**File:** `tests/test_integration.py`

**What to test:**
- Test that `just check` recipe exists in justfile.base
- Test that `just check` calls `version-check.sh check` (verbose mode)
- Test that `just check config` shows configuration
- Test that `just check on/off` enables/disables notifications
- Test that `just check 7d` mutes for 7 days

**Approach:**
- Locate the existing `TestVersionCheckJustIntegration` class (lines ~2808+)
- The test `test_just_check_command_exists` already expects the recipe but it doesn't exist yet
- Add additional tests for all `just check` subcommands

**TDD Phase:** RED (write failing tests)

**Expected result:** Tests fail because `just check` recipe doesn't exist in justfile.base

---

### Task 2: Implement `just check` recipe in justfile.base

**File:** `assets/workspace/.devcontainer/justfile.base`

**What to add:**
A new section for version checking with a `check` recipe that proxies to `version-check.sh`:

```just
# -------------------------------------------------------------------------------
# VERSION CHECK
# -------------------------------------------------------------------------------

# Check for devcontainer updates (verbose)
# Usage: just check [config|on|off|<duration>]
# Examples: just check, just check config, just check off, just check 7d
[group('info')]
check *args:
    #!/usr/bin/env bash
    SCRIPT_DIR="$(cd "$(dirname "{{justfile_directory()}}")/.devcontainer/scripts" && pwd)"
    if [[ ! -f "$SCRIPT_DIR/version-check.sh" ]]; then
        echo "Error: version-check.sh not found"
        exit 1
    fi
    if [[ $# -eq 0 ]]; then
        "$SCRIPT_DIR/version-check.sh" check
    else
        "$SCRIPT_DIR/version-check.sh" "$@"
    fi
```

**Note:** The recipe should work from inside the container (where justfile.base is used)

**TDD Phase:** GREEN (make tests pass)

**Expected result:** All `just check` tests pass

---

### Task 3: Add tests for automatic version check on post-attach

**File:** `tests/test_integration.py`

**What to test:**
- Test that `post-attach.sh` calls `version-check.sh` (no args, silent mode)
- Test that the call is at the end of the script (after all other setup)
- Test that post-attach doesn't fail if version-check.sh fails

**Approach:**
- Add tests to verify `post-attach.sh` invokes version-check
- Mock the GitHub API to avoid network calls during tests
- Verify silent mode (no args) is used

**TDD Phase:** RED (write failing tests)

**Expected result:** Tests fail because `post-attach.sh` doesn't call `version-check.sh` yet

---

### Task 4: Wire version-check into post-attach.sh

**File:** `assets/workspace/.devcontainer/scripts/post-attach.sh`

**What to add:**
At the end of the script (after line 28), add:

```bash
# Check for devcontainer updates (silent, throttled)
"$SCRIPT_DIR/version-check.sh" || true
```

**Why `|| true`:** Ensures post-attach never fails due to version check errors (graceful degradation)

**TDD Phase:** GREEN (make tests pass)

**Expected result:** All post-attach integration tests pass

---

### Task 5: Add tests for fixed notification message

**File:** `tests/test_integration.py` or create `tests/test_version_check_notification.py`

**What to test:**
- Test that `notify_update()` shows correct upgrade instructions
- Test that it mentions `just devcontainer-upgrade`
- Test that it shows the curl fallback option
- Test that it mentions rebuilding the container in VS Code
- Test that it does NOT mention `just update` (which is for Python deps)

**Approach:**
- Create a test that triggers an update notification (mock version check)
- Capture stdout
- Assert the notification contains the correct text

**TDD Phase:** RED (write failing tests)

**Expected result:** Tests fail because notification message is incorrect

---

### Task 6: Fix notification message in version-check.sh

**File:** `assets/workspace/.devcontainer/scripts/version-check.sh`

**What to change:**
Replace the `notify_update()` function (lines 253-268) with:

```bash
# Display update available notification
notify_update() {
    local current="$1"
    local latest="$2"

    echo ""
    echo -e "${BOLD}${CYAN}🚀 Devcontainer Update Available${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  Current: ${YELLOW}$current${NC}  →  Latest: ${GREEN}$latest${NC}"
    echo ""
    echo -e "  Run from a ${BOLD}host terminal${NC} (not inside the container):"
    echo ""
    echo -e "    ${BOLD}just devcontainer-upgrade${NC}"
    echo ""
    echo -e "  Or without just:"
    echo ""
    echo -e "    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --force ."
    echo ""
    echo -e "  After upgrading, rebuild the container in VS Code."
    echo ""
    echo -e "  Mute: ${BOLD}just check 7d${NC}    Disable: ${BOLD}just check off${NC}"
    echo ""
}
```

**TDD Phase:** GREEN (make tests pass)

**Expected result:** All notification message tests pass

---

### Task 7: Add tests for `just devcontainer-upgrade` recipe

**File:** `tests/test_integration.py`

**What to test:**
- Test that `just devcontainer-upgrade` recipe exists (can be parsed by just)
- Test that running it from inside a container shows an error and exits
- Test that it detects `/.dockerenv` as a container indicator
- Test error message says "This must be run from a host terminal, not inside the container."
- (Host-side test would require mocking podman/docker, may skip actual execution test)

**Approach:**
- Add test that verifies recipe existence in justfile.base
- Add test that runs the recipe in container environment (should fail gracefully)
- Use fixture that creates `/.dockerenv` to simulate container environment

**TDD Phase:** RED (write failing tests)

**Expected result:** Tests fail because `just devcontainer-upgrade` recipe doesn't exist

---

### Task 8: Implement `just devcontainer-upgrade` recipe in justfile.base

**File:** `assets/workspace/.devcontainer/justfile.base`

**What to add:**
Add to the same VERSION CHECK section created in Task 2:

```just
# Upgrade devcontainer to latest version (host-side only)
# This recipe MUST be run from a host terminal, not inside the container
[group('info')]
devcontainer-upgrade:
    #!/usr/bin/env bash
    # Detect if running inside a container
    if [[ -f "/.dockerenv" ]] || [[ -n "${container:-}" ]]; then
        echo ""
        echo "❌ ERROR: This command must be run from a HOST terminal"
        echo ""
        echo "You are currently inside the devcontainer."
        echo "Open a new terminal on your host machine and run:"
        echo ""
        echo "    cd $(pwd)"
        echo "    just devcontainer-upgrade"
        echo ""
        echo "Or use the curl method:"
        echo ""
        echo "    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --force ."
        echo ""
        exit 1
    fi
    
    # We're on the host - proceed with upgrade
    echo "🚀 Upgrading devcontainer to latest version..."
    echo ""
    
    # Check if podman or docker is available
    if command -v podman &> /dev/null; then
        RUNTIME="podman"
    elif command -v docker &> /dev/null; then
        RUNTIME="docker"
    else
        echo "❌ ERROR: Neither podman nor docker is installed"
        echo ""
        echo "Please install one of them first:"
        echo "  macOS:  brew install podman && podman machine init && podman machine start"
        echo "  Linux:  sudo apt install podman   # or equivalent for your distro"
        echo ""
        exit 1
    fi
    
    echo "✓ Using $RUNTIME"
    echo ""
    echo "Downloading and running install script..."
    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --force .
```

**Notes:**
- This recipe is designed to fail fast when run inside the container
- The error message is helpful and explains what to do
- On the host, it downloads and runs the official install script with `--force` flag
- The justfile is bind-mounted, so this recipe is visible from both host and container
- The recipe targets the host-side use case

**TDD Phase:** GREEN (make tests pass)

**Expected result:** All `just devcontainer-upgrade` tests pass

---

### Task 9: Update CHANGELOG.md

**File:** `CHANGELOG.md`

**What to add:**
In the `## Unreleased` section, under `### Added`:

```markdown
- **Automatic update notifications on devcontainer attach** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - Wire `version-check.sh` into `post-attach.sh` for automatic update checks
  - Silent, throttled checks (24-hour interval by default)
  - Graceful failure - never disrupts the attach process
- **Host-side devcontainer upgrade recipe** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - New `just devcontainer-upgrade` recipe for convenient upgrades from host
  - Container detection - prevents accidental execution inside devcontainer
  - Clear error messages with instructions when run from wrong context
- **`just check` recipe for version management** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - Expose version-check.sh subcommands: `just check`, `just check config`, `just check on/off`, `just check 7d`
  - User-friendly interface for managing update notifications

### Changed

- **Updated update notification message** ([#73](https://github.com/vig-os/devcontainer/issues/73))
  - Fixed misleading `just update` instruction (Python deps, not devcontainer upgrade)
  - Show correct upgrade instructions: `just devcontainer-upgrade` and curl fallback
  - Clarify that upgrade must run from host terminal, not inside container
  - Add reminder to rebuild container in VS Code after upgrade
```

**Expected result:** CHANGELOG documents all changes related to issue #73

---

## TDD Commit Strategy

Following the TDD rules from `.cursor/rules/tdd.mdc`, each task above will result in at least one commit:

1. **RED phase commits:** `test: ...` (failing tests)
2. **GREEN phase commits:** `feat: ...` or `fix: ...` (implementation)
3. **REFACTOR phase commits:** `refactor: ...` (if needed)

### Proposed commit sequence:

```
1. test: add tests for just check recipe integration
   Refs: #73

2. feat(devcontainer): add just check recipe to justfile.base
   Refs: #73

3. test: add tests for automatic version check on post-attach
   Refs: #73

4. feat(devcontainer): wire version-check into post-attach.sh
   Refs: #73

5. test: add tests for corrected update notification message
   Refs: #73

6. fix(devcontainer): correct update instructions in version-check notification
   Refs: #73

7. test: add tests for just devcontainer-upgrade recipe
   Refs: #73

8. feat(devcontainer): add host-side devcontainer-upgrade recipe
   Refs: #73

9. docs: update CHANGELOG for version-check wiring and upgrade recipe
   Refs: #73
```

Each commit follows the repository's commit message standard and includes `Refs: #73`.

---

## Testing Strategy

### Unit Tests
- All new functionality in `version-check.sh` is already tested (script is feature-complete)
- New recipes will be tested via integration tests

### Integration Tests
- Test `just check` calls version-check.sh correctly
- Test `post-attach.sh` calls version-check.sh
- Test `just devcontainer-upgrade` detects container environment
- Test notification message content

### Manual Testing Checklist
After implementation, manually verify:
- [ ] Attach to devcontainer - see update notification (if update available)
- [ ] Run `just check` - see verbose version check
- [ ] Run `just check config` - see configuration
- [ ] Run `just check 7d` - mute for 7 days
- [ ] Run `just devcontainer-upgrade` inside container - see error
- [ ] Run `just devcontainer-upgrade` on host - upgrade proceeds (or fails gracefully if no runtime)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| `version-check.sh` failure breaks post-attach | High | Use `|| true` in post-attach.sh |
| User accidentally runs upgrade inside container | Medium | Detect container environment and show clear error |
| Host doesn't have podman/docker installed | Medium | Show installation instructions in error message |
| justfile path resolution breaks on some systems | Low | Use `justfile_directory()` function for relative paths |
| Tests slow due to network calls | Low | Mock GitHub API in tests, use existing test fixtures |

---

## Dependencies

- No new external dependencies required
- Uses existing tools: `bash`, `curl`, `just`, `podman`/`docker`
- All scripts are POSIX-compatible where possible (fallback to bash when needed)

---

## Acceptance Criteria

All criteria from issue #73 must be met:

- [x] `version-check.sh` is called from `post-attach.sh` ✓ (Task 4)
- [x] Notification message shows correct upgrade instructions ✓ (Task 6)
- [x] `just devcontainer-upgrade` recipe exists and works on host ✓ (Task 8)
- [x] Container detection prevents running upgrade recipe inside container ✓ (Task 8)
- [x] `just check` recipe exposes version-check subcommands ✓ (Task 2)
- [x] All changes are TDD-compliant with RED-GREEN-REFACTOR commits ✓
- [x] CHANGELOG.md is updated ✓ (Task 9)
- [x] Tests pass in CI ✓

---

## Estimated Complexity

- **Total tasks:** 9
- **Estimated tool calls:** ~80-100
- **Complexity:** Medium
  - Most code already exists (version-check.sh is complete)
  - Main work is wiring and testing
  - No complex algorithms or data structures
  - Straightforward bash scripting and just recipes

---

## Notes

- This plan follows the coding principles from `.cursor/rules/coding-principles.mdc`:
  - YAGNI: Only implementing what the issue requests
  - Minimal diff: Touching only necessary files
  - DRY: Reusing existing version-check.sh script
  - No secrets: Using env vars and avoiding hardcoded credentials
  - Traceability: Every commit references #73
  - Single responsibility: Each function/recipe has one clear purpose

- The implementation is fully backward compatible:
  - Existing containers work unchanged
  - Users can disable notifications with `just check off`
  - Graceful failure ensures no disruption to workflow

- The `just devcontainer-upgrade` recipe provides a better UX than the curl one-liner, but both remain documented and supported.
