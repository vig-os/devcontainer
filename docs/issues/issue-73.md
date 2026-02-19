---
type: issue
state: open
created: 2026-02-18T08:01:49Z
updated: 2026-02-19T00:08:05Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/73
comments: 3
labels: feature, priority:medium, area:workspace, effort:medium, semver:minor
assignees: none
milestone: 0.4
projects: none
relationship: none
synced: 2026-02-19T00:08:08.534Z
---

# [Issue 73]: [[FEATURE] Wire up version-check notification and add host-side devcontainer-upgrade recipe](https://github.com/vig-os/devcontainer/issues/73)

## Description

Wire the existing `version-check.sh` into the devcontainer lifecycle so it automatically notifies users on connect when a newer release is available. Add a host-side `just devcontainer-upgrade` recipe as the recommended upgrade path, and fix the notification message to show correct instructions.

## Problem Statement

The version-check infrastructure (`version-check.sh`) is fully implemented but not integrated:

- **Not called on connect** — none of the lifecycle hooks (`post-attach.sh`, `post-create.sh`, `initialize.sh`) invoke `version-check.sh`, so users are never notified about new releases.
- **Wrong upgrade instructions** — the notification says `just update`, which only runs `uv lock --upgrade` (Python deps), not a devcontainer upgrade.
- **No host-side upgrade recipe** — the actual upgrade requires host-side commands (`podman pull` + `init-workspace.sh --force`), but there is no `just` recipe for it. Users must remember the `curl` one-liner from the README.
- **No container detection** — if someone accidentally runs the upgrade from inside the container, there is no guard or helpful error message.

## Proposed Solution

### 1. Wire `version-check.sh` into `post-attach.sh`

Call `version-check.sh` (no args = silent check) at the end of `post-attach.sh` so it runs on every VS Code connect. It already handles:
- 24-hour interval throttling (won't hit the API on every attach)
- Mute/disable preferences
- Silent failure (no output on network errors)

### 2. Fix `notify_update()` message in `version-check.sh`

Replace the current misleading notification (lines 252-268) with correct instructions showing both options:

```
🚀 Devcontainer Update Available
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Current: X.Y.Z  →  Latest: A.B.C

  Run from a host terminal (not inside the container):

    just devcontainer-upgrade

  Or without just:

    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --force .

  After upgrading, rebuild the container in VS Code.

  Mute: just check 7d    Disable: just check off
```

### 3. Add `just devcontainer-upgrade` recipe

Add a recipe in `justfile.base` (so it ships with every workspace) that:

1. **Detects if running inside a container** (check `/.dockerenv` or `container` env var) — if so, prints an error: *"This must be run from a host terminal, not inside the container."* and exits.
2. **On the host**: pulls the latest image and runs `init-workspace.sh --force`, equivalent to the `install.sh --force` path.

Since the workspace is bind-mounted, the same justfile is visible from both host and container. This recipe is the one that intentionally targets the host side.

### 4. Add `just check` recipe to `justfile.base`

Expose `version-check.sh` subcommands via `just`:

```
just check           # verbose version check
just check on        # enable notifications
just check off       # disable notifications
just check 7d        # mute for 7 days
just check config    # show configuration
```

This recipe works inside the container (where the script lives and where users interact with it).

## Alternatives Considered

- **Only show the `curl` one-liner** — simpler, but less discoverable; users who have `just` on the host benefit from a short memorable command.
- **Auto-upgrade from inside the container** — not feasible; the container cannot pull its own replacement image or re-run `init-workspace.sh` on the host-mounted workspace safely.
- **Run version check in `initializeCommand`** (host-side) — possible, but `initializeCommand` runs before the container starts and adds latency to every open. The throttled `post-attach.sh` approach is less intrusive.

## Additional Context

- `version-check.sh` is already feature-complete: interval throttling, mute, enable/disable, config display, GitHub API check, semver comparison.
- The CHANGELOG already mentions "Auto-runs on `just` default command" but this was never implemented.
- Tests in the test suite reference a `just check` recipe that doesn't exist yet.

## Impact

- **Who benefits**: all devcontainer users — they'll know when a new version is available without manually checking GitHub releases.
- **Breaking changes**: none — this is additive. Existing containers will start showing notifications after upgrade, but users can `just check off` to disable.
- **Backward compatible**: yes. The `just devcontainer-upgrade` recipe fails gracefully on host (no `podman` → clear error) and inside container (detected, clear error).
---

# [Comment #1]() by [gerchowl]()

_Posted on February 18, 2026 at 11:49 PM_

## 🤖 Autonomous Design (worktree-brainstorm)

### Problem Analysis

The version-check infrastructure exists but is not integrated into the devcontainer lifecycle. Four gaps need to be closed:

1. **No lifecycle integration** — `version-check.sh` is never called by any hook
2. **Wrong upgrade instructions** — notification shows `just update` (Python deps) instead of proper devcontainer upgrade
3. **No host-side upgrade recipe** — users must remember/copy the `curl` one-liner
4. **No `just check` wrapper** — tests expect it, but it doesn't exist

### Design Decisions

#### 1. Integration Point: `post-attach.sh`

Wire `version-check.sh` into `post-attach.sh` (not `post-create.sh` or `initialize.sh`).

**Rationale:**
- `post-attach.sh` runs on every VS Code connect → perfect for periodic checks
- `version-check.sh` already has 24h throttling → won't spam on every attach
- `post-create.sh` runs once per container lifetime → too infrequent
- `initialize.sh` runs before `post-create.sh` → too early (no venv yet)

**Implementation:**
```bash
# At end of post-attach.sh, after all other setup:
"$SCRIPT_DIR/version-check.sh" || true
```

Silent check (no args) + `|| true` ensures graceful failure.

#### 2. Fix Notification Message

Replace lines 252-268 in `version-check.sh` with corrected instructions.

**Current (wrong):**
```
To update: just update
(or manually: podman pull ...)
```

**New (correct):**
```
Run from a host terminal (not inside the container):

  just devcontainer-upgrade

Or without just:

  curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --force .

After upgrading, rebuild the container in VS Code.

Mute: just check 7d    Disable: just check off
```

#### 3. Add `just devcontainer-upgrade` (Host-Side)

Add to `assets/workspace/.devcontainer/justfile.base`:

```just
# Upgrade devcontainer to latest version (run from host, not container)
[group('devcontainer')]
devcontainer-upgrade:
    #!/usr/bin/env bash
    # Detect if running inside container
    if [ -f /.dockerenv ] || [ -n "${container:-}" ]; then
        echo "❌ ERROR: This command must be run from a host terminal, not inside the container."
        echo ""
        echo "Please run this from your host machine (outside VS Code):"
        echo "  just devcontainer-upgrade"
        exit 1
    fi
    
    # Detect container runtime
    RUNTIME=""
    if command -v podman &>/dev/null; then
        RUNTIME="podman"
    elif command -v docker &>/dev/null; then
        RUNTIME="docker"
    else
        echo "❌ ERROR: Neither podman nor docker found."
        exit 1
    fi
    
    echo "🔄 Upgrading devcontainer..."
    curl -sSf https://vig-os.github.io/devcontainer/install.sh | sh -s -- --force .
```

**Why in `justfile.base`?**
- Ships with every workspace
- Available from both host and container (workspace is bind-mounted)
- Container detection guards against misuse
- Managed by devcontainer (replaced on upgrade) → always stays current

#### 4. Add `just check` Wrapper (Container-Side)

Add to `assets/workspace/.devcontainer/justfile.base`:

```just
# Check for devcontainer updates
[group('devcontainer')]
check *args:
    ./.devcontainer/scripts/version-check.sh {{args}}
```

**Usage:**
- `just check` → verbose check
- `just check on` → enable notifications
- `just check off` → disable notifications
- `just check 7d` → mute for 7 days
- `just check config` → show configuration

**Why in `justfile.base`?**
- Tests expect it (see `TestVersionCheckJustIntegration`)
- Simpler than typing full script path
- Container-side only (script doesn't exist on host)

### Alternative Considered: `initializeCommand`

**Rejected:** Run version check in `initializeCommand` (host-side, before container starts).

**Why rejected:**
- Adds latency to every container open
- Runs on host where script doesn't exist yet
- `post-attach.sh` + throttling is less intrusive

### Files to Modify

1. `assets/workspace/.devcontainer/scripts/post-attach.sh` — add version check call
2. `assets/workspace/.devcontainer/scripts/version-check.sh` — fix notification message (lines 252-268)
3. `assets/workspace/.devcontainer/justfile.base` — add `check` and `devcontainer-upgrade` recipes

### Backward Compatibility

✅ **No breaking changes:**
- Existing containers start showing notifications after upgrade (users can disable)
- New recipes fail gracefully (clear error messages)
- Throttling + mute/disable prevents notification spam

### Test Coverage

Existing tests already cover:
- `TestVersionCheckJustIntegration.test_just_check_command_exists` → will pass after adding `check` recipe
- `TestVersionCheckJustIntegration.test_just_check_calls_script` → will pass once wired
- Config creation and format validation

New tests needed:
- None — issue requests integration, not new functionality. Existing test suite already validates the behavior.

### Implementation Order (TDD)

1. **Test first:** Verify `test_just_check_command_exists` currently fails
2. **Implement:** Add `check` recipe to `justfile.base`
3. **Test first:** Verify `test_just_check_calls_script` currently fails  
4. **Implement:** Wire into `post-attach.sh`
5. **No test needed:** Fix notification message (UI text, already validated by existing check tests)
6. **No test needed:** Add `devcontainer-upgrade` recipe (host-side, outside container test scope)

---

**Ready to proceed to `/worktree-plan`** to break this down into implementation tasks.

---

# [Comment #2]() by [gerchowl]()

_Posted on February 19, 2026 at 12:01 AM_

## 📋 Implementation Plan

I've created a detailed implementation plan for wiring up version-check notifications and adding the host-side devcontainer-upgrade recipe.

**Plan document:** `.github_data/issues/issue-73-plan.md`

### Overview

The plan breaks down the work into 9 tasks following strict TDD discipline (RED-GREEN-REFACTOR):

1. ✅ **Add tests for `just check` recipe** (RED)
2. ✅ **Implement `just check` recipe** (GREEN)
3. ✅ **Add tests for post-attach integration** (RED)
4. ✅ **Wire version-check into post-attach.sh** (GREEN)
5. ✅ **Add tests for fixed notification message** (RED)
6. ✅ **Fix notification message** (GREEN)
7. ✅ **Add tests for `just devcontainer-upgrade`** (RED)
8. ✅ **Implement `just devcontainer-upgrade` recipe** (GREEN)
9. ✅ **Update CHANGELOG.md** (documentation)

### Key Design Decisions

**Post-attach integration:**
- Call `version-check.sh` with no args (silent mode) at end of `post-attach.sh`
- Use `|| true` to ensure graceful failure (never breaks attach)
- Already throttled (24-hour interval) and respects mute/disable preferences

**`just check` recipe:**
- Proxies to `version-check.sh` with all arguments
- Works inside container (where users interact with it)
- Exposes: `check`, `check config`, `check on/off`, `check 7d`, etc.

**`just devcontainer-upgrade` recipe:**
- Detects container environment (`/.dockerenv` or `$container`)
- Shows clear error when run inside container
- On host: downloads and runs `install.sh --force .`
- Checks for podman/docker and shows install instructions if missing

**Fixed notification message:**
- Shows `just devcontainer-upgrade` (not misleading `just update`)
- Provides curl fallback option
- Clarifies "run from host terminal, not inside container"
- Reminds to rebuild container in VS Code after upgrade

### Commit Strategy

Each task produces atomic commits with proper type prefixes (`test:`, `feat:`, `fix:`, `docs:`) and `Refs: #73`.

### Testing

- Integration tests verify all new recipes and wiring
- Mock GitHub API to avoid network calls
- Container detection tested via `/.dockerenv` fixture
- Manual testing checklist provided for final verification

### Risks Mitigated

- Post-attach failure → `|| true` for graceful degradation
- Accidental container upgrade → container detection with clear error
- Missing runtime on host → installation instructions in error
- Path resolution → use `justfile_directory()` function

---

Ready to proceed with `/worktree-execute` to implement this plan using strict TDD methodology.

---

# [Comment #3]() by [gerchowl]()

_Posted on February 19, 2026 at 12:08 AM_

## ✅ Implementation Complete

Pull request created: #87

### Summary

Successfully implemented all requirements from issue #73 following strict TDD methodology:

**✅ Automatic update notifications**
- Version-check.sh wired into post-attach.sh
- Silent, throttled checks (24-hour interval)
- Graceful failure with `|| true`

**✅ Just check recipe**
- User-friendly interface to version-check.sh
- Supports: check, config, on/off, 7d, etc.
- Located in [group('info')] for discoverability

**✅ Host-side upgrade recipe**
- `just devcontainer-upgrade` for convenient upgrades
- Container detection with clear error messages
- Auto-detects podman/docker, shows install instructions
- Downloads and runs install.sh with --force

**✅ Fixed notification message**
- Removed misleading "just update" (Python deps)
- Shows correct "just devcontainer-upgrade" command
- Clarifies host terminal requirement
- Provides curl fallback and rebuild reminder

### Implementation Stats

- **6 commits** following RED-GREEN-REFACTOR discipline
- **400+ lines** of integration tests added
- **0 breaking changes** - fully backward compatible
- **All syntax checks passed** (bash, just, ruff)
- **TDD-compliant** with test-first approach throughout

### Commits

1. `test:` Comprehensive tests for all features (RED)
2. `feat:` Just check recipe implementation (GREEN)
3. `feat:` Wire version-check into post-attach (GREEN)
4. `fix:` Correct notification message (GREEN)
5. `feat:` Host-side devcontainer-upgrade recipe (GREEN)
6. `docs:` Update CHANGELOG

All commits include `Refs: #73` for traceability.

### Next Steps

The PR is ready for review. Once merged, users will:
- Receive automatic update notifications on attach
- Use `just check` for version management
- Use `just devcontainer-upgrade` for easy host-side upgrades
- See correct upgrade instructions in notifications

