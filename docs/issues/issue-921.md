---
type: issue
state: closed
created: 2026-07-07T15:54:39Z
updated: 2026-07-08T11:56:07Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/921
comments: 1
labels: bug, priority:low, area:image, semver:patch
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:23.777Z
---

# [Issue 921]: [fix(image): bake an authoritative built-tag version record for init-workspace .vig-os stamping](https://github.com/vig-os/devkit/issues/921)

Split out from #916 (F5) during 0.4.1-rc1 hardening — cannot be fixed runtime-only.

## Problem

On a bare `podman run … /root/assets/init-workspace.sh` upgrade (no `install.sh`), the scaffolded `.vig-os` is left pinned to whatever the **baked template** `.vig-os` says — currently `DEVCONTAINER_VERSION=0.4.0` — not the image's actual tag. `init-workspace.sh` only rewrites the pin when `VIG_OS_VERSION` is set, which `install.sh` forwards but a raw `docker run` does not. The image exposes no independent record of its own built tag: no VERSION file, no version env var, no OCI version label. The only in-image version string is the template `.vig-os`, seeded from the repo-root pin at build time (`flake.nix` `{{IMAGE_TAG}}` sed from `./.vig-os`), so reading it back to "stamp" is a no-op and stays stale for RC images.

## Proposed fix (build-side)

Bake the true built tag (RCs included) into the image as an authoritative record distinct from the repo-root pin — e.g. a `VIG_OS_VERSION` env var or a dedicated `/root/assets/VERSION` file set from the real build tag. `init-workspace.sh` already has the stamping path (a NOTE was added there); it should read this record when `VIG_OS_VERSION` is unset.

Consumer impact today is limited (the `install.sh` path is correct), so this is low priority and may slip to 0.5 if 0.4.1 finalizes first.

Refs: #916
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 11:56 AM_

Closed by #926 

