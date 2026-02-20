---
type: issue
state: closed
created: 2026-02-20T10:59:01Z
updated: 2026-02-20T13:19:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/111
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-20T15:25:35.197Z
---

# [Issue 111]: [[BUG] just init fails to install devcontainer CLI — npm global install permission denied](https://github.com/vig-os/devcontainer/issues/111)

## Description

`just init` fails to install the `devcontainer` CLI on Linux because `npm install -g` requires write access to `/usr/local/lib/node_modules`, which is owned by root.

## Steps to Reproduce

1. Run `just init` on a Linux machine where `devcontainer` CLI is not installed
2. When prompted to install `devcontainer`, accept with `y`

## Expected Behavior

The `devcontainer` CLI should install successfully without requiring `sudo` or manual intervention.

## Actual Behavior

The installation fails with `EACCES: permission denied`:

```
  devcontainer (0.81.1)
  Purpose: DevContainer CLI for testing devcontainer functionality
  Command: npm install -g @devcontainers/cli@0.81.1
?  Install devcontainer? [y/N]: y
ℹ  Installing devcontainer...
npm ERR! code EACCES
npm ERR! syscall mkdir
npm ERR! path /usr/local/lib/node_modules
npm ERR! errno -13
npm ERR! Error: EACCES: permission denied, mkdir '/usr/local/lib/node_modules'
✗  Failed to install devcontainer
```

## Environment

- **OS**: Ubuntu 24.04 (Linux 6.17.0-14-generic)
- **npm**: system npm with default global prefix (`/usr/local/lib/node_modules`)
- **Node**: system Node.js

## Additional Context

`@devcontainers/cli@0.81.1` is already declared as a local dependency in `package.json`. The `bats` dependency already uses the correct pattern — local `npm install` with a `node_modules/.bin/` check fallback. The `devcontainer` entry should follow the same approach instead of requiring a global install.

## Possible Solution

Change the `devcontainer` entry in `scripts/requirements.yaml` to:
- Use `npm install` (local) instead of `npm install -g` (global)
- Check `node_modules/.bin/devcontainer` in addition to `command -v devcontainer`
- Use `npx devcontainer --version` for version checking

This matches the existing `bats` pattern and avoids permission issues entirely.

## Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on February 20, 2026 at 10:59 AM_

## Implementation Plan

### Root Cause

The `devcontainer` entry in `scripts/requirements.yaml` uses `npm install -g @devcontainers/cli@{{version}}` which requires root permissions on Linux. Meanwhile, `@devcontainers/cli@0.81.1` is already declared in `package.json` as a local dependency.

### Fix

Follow the same pattern already used by `bats` in `requirements.yaml`:

**Before:**
```yaml
  # DevContainer CLI (auto-installed by setup.sh)
  - name: devcontainer
    version: "0.81.1"
    check:
      command: command -v devcontainer
      version_command: devcontainer --version
      version_regex: '(\d+\.\d+\.\d+)'
    install:
      all: npm install -g @devcontainers/cli@{{version}}
      manual: https://github.com/devcontainers/cli
```

**After:**
```yaml
  # DevContainer CLI (auto-installed by npm install)
  - name: devcontainer
    version: "0.81.1"
    check:
      command: command -v devcontainer || test -x node_modules/.bin/devcontainer
      version_command: npx devcontainer --version
      version_regex: '(\d+\.\d+\.\d+)'
    install:
      all: npm install
      manual: https://github.com/devcontainers/cli
```

### Files Changed

- `scripts/requirements.yaml` — update devcontainer entry (check command, version command, install command, comment)

### What Does NOT Change

- `package.json` — already has the dependency at the correct version
- `.github/actions/setup-env/action.yml` — CI runs with proper permissions, no change needed
- `tests/bats/init.bats` — existing tests are structural grep checks, unaffected

### TDD Steps

1. **RED:** Add test asserting `requirements.yaml` uses `node_modules/.bin/devcontainer` check pattern → fails
2. **GREEN:** Update `requirements.yaml` → test passes
3. **Verify:** `just init --check` confirms devcontainer is detected via local path

