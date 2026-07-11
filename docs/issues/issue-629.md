---
type: issue
state: closed
created: 2026-06-23T06:53:58Z
updated: 2026-07-01T11:19:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/629
comments: 1
labels: chore, area:workspace, area:workflow
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:15.356Z
---

# [Issue 629]: [C4 — Migrate templates & editor glue off Cursor](https://github.com/vig-os/devkit/issues/629)

Tracking: #625



## Context

`assets/workspace/.cursor/` mirrors the root `.cursor/` for new workspaces; template scripts
reference Cursor remote-SSH sockets; and docs say "VS Code / Cursor". A Claude-native setup
needs the template and editor glue cleaned up.

## Scope

**Decision:** VS Code only — Cursor **editor** support is dropped (not just `cursor-agent`).

**In:**
- `assets/workspace/.cursor/` → `.claude/`.
- Update `scripts/manifest.toml` entries accordingly.
- Drop `/tmp/cursor-remote-ssh-*.sock` handling in
  `assets/workspace/.devcontainer/scripts/{verify-auth,setup-git-conf}.sh`.
- Drop the `command -v cursor` fallback in `justfile.devc`.
- `COMMIT_MESSAGE_STANDARD.md`: "VS Code / Cursor" → "VS Code".
- Remove any other Cursor-editor glue (Cursor-URI / `cursor-remote` paths); VS Code only.

**Out:**
- Root `.cursor/` (#626).

## Tasks

- [ ] Move template `.cursor/` → `.claude/`
- [ ] Update `manifest.toml` sync entries
- [ ] Remove Cursor remote-SSH socket handling from the two scripts
- [ ] Remove the `command -v cursor` fallback in `justfile.devc`
- [ ] Update `COMMIT_MESSAGE_STANDARD.md`

## Acceptance criteria

- New workspaces scaffold `.claude/`, not `.cursor/`.
- No Cursor editor glue remains in templates.

## Dependencies

- **Depends-on:** #626.
- **Blocks:** none.

## Files

- `assets/workspace/**`
- `scripts/manifest.toml`
- `assets/workspace/docs/COMMIT_MESSAGE_STANDARD.md`

## Test notes

- Extend `init-workspace.bats` / `test_integration.py` to assert `.claude/` is scaffolded and
  `.cursor/` is not.

## Related issues

- **#231 / #153** (IDE-agnostic remote wrappers / `devc_remote_uri.py`) — **scope resolved:
  VS Code only.** Cursor **editor** support is dropped along with `cursor-agent`. #629 therefore
  removes all Cursor editor glue (remote-SSH sockets, any `cursor-remote`/Cursor-URI path).
  **Recommend closing #153 and de-scoping #231 to `code-remote` only** (VS Code `vscode-remote://`
  URI), since the Cursor half is no longer wanted.
- **#546** (slim Claude OAuth forwarding) — removes `setup-claude.sh` + the non-root `claude`
  user; overlaps with the editor/auth scripts this issue touches. Coordinate.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30). `assets/workspace/.cursor/` → `.claude/`; cursor remote-SSH socket handling and `command -v cursor` fallbacks removed. Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

