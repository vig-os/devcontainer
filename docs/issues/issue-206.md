---
type: issue
state: closed
created: 2026-02-26T10:58:12Z
updated: 2026-02-26T11:44:58Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/206
comments: 0
labels: bug, area:image, area:workspace, effort:small, semver:patch
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-27T04:19:05.619Z
---

# [Issue 206]: [[BUG] Cursor Agent shell fails with forkpty(3) in devcontainer — missing terminal.integrated.defaultProfile.linux override](https://github.com/vig-os/devcontainer/issues/206)

## Description

When a user's Cursor/VS Code settings configure `terminal.integrated.defaultProfile.linux` to a shell not present in the container image (e.g. `zsh`), the Agent chat shell fails with `forkpty(3) failed` and the extension host times out. This is because `init-workspace.sh` does not set a `terminal.integrated.defaultProfile.linux` override in the generated `devcontainer.json`, so the user's host-side preference leaks into the container.

The container image ships `bash` but not `zsh`. Users with `"terminal.integrated.defaultProfile.linux": "zsh"` in their global settings hit this silently.

## Steps to Reproduce

1. Set `"terminal.integrated.defaultProfile.linux": "zsh"` in Cursor user settings (common for macOS users)
2. Open any project using the devcontainer image (`ghcr.io/vig-os/devcontainer:dev`)
3. Open Agent chat and run any shell command (e.g. `pwd`)

## Expected Behavior

Agent shell executes commands and displays output.

## Actual Behavior

- `The terminal process failed to launch: A native exception occurred during launch (forkpty(3) failed.)`
- `The agent execution provider did not respond within 30 seconds.`
- Regular terminal may also fail or fall back silently
- `agent` CLI inside the container works (it spawns bash directly)

## Environment

- Cursor 2.5.25 (Stable, macOS arm64)
- Container image: `ghcr.io/vig-os/devcontainer:dev` (Debian-based, bash only)
- Reproduces both locally and over remote SSH

## Proposed Fix

Two complementary changes:

1. **`init-workspace.sh`** — add `"terminal.integrated.defaultProfile.linux": "bash"` to the generated `devcontainer.json` settings, so the container always overrides the user's host shell preference.
2. **Container image** (optional) — install `zsh` so users with that preference don't break. Adds ~2MB.

## Changelog Category

Fixed
