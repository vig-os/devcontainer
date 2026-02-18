---
type: issue
state: open
created: 2026-02-18T08:01:49Z
updated: 2026-02-18T08:01:49Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/73
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:02:09.061Z
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
