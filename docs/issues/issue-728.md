---
type: issue
state: closed
created: 2026-06-29T07:55:55Z
updated: 2026-06-30T07:42:24Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/728
comments: 1
labels: bug, priority:medium, area:image, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:57.852Z
---

# [Issue 728]: [[BUG] npm global prefix points at off-PATH Nix store — `npm install -g` silently invisible](https://github.com/vig-os/devkit/issues/728)

## Description

In the Nix-built image, npm's global prefix is the Node nix-store path (`/nix/store/...-nodejs-slim-<ver>`), and that prefix's `bin/` directory is **not** on `PATH` (`PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`).

As a result, `npm install -g <tool>` reports success but the installed binary is invisible — it lands in `/nix/store/.../bin/<tool>`, which nothing on `PATH` can see.

## Steps to Reproduce

1. `just build` → run image.
2. `npm install -g tsx`  → prints `changed 3 packages`, exit 0.
3. `command -v tsx`  → not found (exit 1).
4. `npm config get prefix` → `/nix/store/...-nodejs-slim-24.16.0`; `ls $(npm config get prefix)/bin` shows `tsx`, but that dir is not on `PATH`.

## Expected Behavior

Globally-installed npm CLIs are on `PATH` and runnable, and the global prefix is a writable, non-store location.

## Actual Behavior

Global install "succeeds" silently into an off-`PATH` (and store-managed) location; the tool is unusable. This bit `commit-action`'s `post-create.sh` (`npm install -g tsx`), which only appeared to work because it swallows errors.

## Environment

- **OS**: NixOS (host)
- **Container Runtime**: Podman 5.8.2
- **Image Version/Tag**: `dev` (built from `feature/625-nix-claude-migration`)
- **Architecture**: AMD64

## Additional Context

Found live-testing the migration vs `commit-action` (#625 / #634).

## Possible Solution

Set a sane, writable global npm prefix that is on `PATH` (e.g. `npm config set prefix /usr/local` baked into the image, with `/usr/local/bin` already on `PATH`), or document for consumers: prefer `npx` / local devDeps over `npm install -g`.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #734 (c984c29) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

