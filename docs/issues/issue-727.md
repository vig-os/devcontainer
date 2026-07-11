---
type: issue
state: closed
created: 2026-06-29T07:55:54Z
updated: 2026-06-30T07:42:22Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/727
comments: 1
labels: bug, priority:high, area:image, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:58.226Z
---

# [Issue 727]: [[BUG] Nix image lacks /usr/bin/env — breaks #!/usr/bin/env shebangs for all consumers](https://github.com/vig-os/devkit/issues/727)

## Description

The Nix-built devcontainer image (`dockerTools.buildLayeredImage`, `flake.nix` `packages.devcontainerImage`) does **not** provide `/usr/bin/env` — in fact `/usr/bin` does not exist at all. `env` is only available at `/bin/env`.

The canonical portable shebang `#!/usr/bin/env <interp>` (used by virtually every Node, Python, Ruby, etc. CLI) therefore fails inside the image. This blocks essentially **every** Node/TypeScript (and many other) downstream consumers running in devcontainer/image mode.

Discovered while live-testing the migration against the `commit-action` consumer.

## Steps to Reproduce

1. `just build` (loads `ghcr.io/vig-os/devcontainer:dev`).
2. Run a Node/TS project in the image, e.g.:
   ```
   podman run --rm -v <commit-action>:/workspace/commit_action -w /workspace/commit_action \
     ghcr.io/vig-os/devcontainer:dev bash -lc 'npm ci && npm run build'
   ```
3. Observe `tsc` (and any local `node_modules/.bin/*`) fail.

## Expected Behavior

`/usr/bin/env` exists, so `#!/usr/bin/env node` (and other interpreters) resolve and locally-installed CLIs run.

## Actual Behavior

```
sh: /workspace/commit_action/node_modules/.bin/tsc: /usr/bin/env: bad interpreter: No such file or directory
```

```
$ ls -l /usr/bin/env   # No such file or directory   (/usr/bin does not exist)
$ ls -l /bin/env       # /bin/env -> coreutils
```

**Confirmed fix in-container:** after `mkdir -p /usr/bin && ln -sf /bin/env /usr/bin/env`, `npm run build` succeeds and the full `commit-action` Jest suite passes (80/80).

## Environment

- **OS**: NixOS (host); image is hermetic Nix (no base distro)
- **Container Runtime**: Podman 5.8.2
- **Image Version/Tag**: `dev` (locally built from `feature/625-nix-claude-migration` via `just build`)
- **Architecture**: AMD64

## Additional Context

Part of the Nix migration master issue #625 / image task #634. Likely a hard blocker for the publish-cutover (#639). Distinct from #687 (which is about `#!/bin/bash` in **host** scripts).

## Possible Solution

Add the standard `/usr/bin/env` (and `/usr/bin`, `/bin/sh`) symlinks in the image. nixpkgs `dockerTools` provides helpers exactly for this — include `pkgs.dockerTools.usrBinEnv` (and `binSh`) in the image contents, or add an `extraCommands`/fakeRootCommands step that symlinks `usr/bin/env -> /bin/env`.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 07:42 AM_

Resolved by #730 (f5679cd) on the Nix-migration branch (epic #625, PR #670). Closing as part of post-merge backlog hygiene (#677).

