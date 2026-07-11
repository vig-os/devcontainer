---
type: issue
state: closed
created: 2026-06-30T12:51:59Z
updated: 2026-06-30T13:15:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/773
comments: 1
labels: priority:high, area:image, effort:small, security
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:50.337Z
---

# [Issue 773]: [[SECURITY] Harden baked nix.conf: drop accept-flake-config=true for explicit substituters + trusted-public-keys](https://github.com/vig-os/devkit/issues/773)

**Source:** PR #670 forward-looking roadmap, thread A — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). Part of the #625 Nix migration; small + security-critical, so landing **on the migration branch before the dev merge** rather than deferring.

## Problem
`accept-flake-config = true` is baked into the image's `/etc/nix/nix.conf` (`flake.nix` ~591). Any in-container `nix run github:attacker/flake` then **silently accepts that flake's `substituters`/`trusted-public-keys`** — the textbook Nix cache-redirection supply-chain attack.

## Fix
- Drop `accept-flake-config = true` from the baked nix.conf.
- Bake **explicit** `substituters` + `trusted-public-keys` (cache.nixos.org + the vig-os cachix key) so normal use still hits the caches.
- Require `--accept-flake-config` per-invocation for anything that genuinely needs a foreign flake's config.

## Acceptance
- Baked nix.conf no longer sets `accept-flake-config = true`; explicit substituters/keys present.
- Image build + dev-shell + CI still resolve from the expected caches (no source-rebuild regression).
- A foreign flake's `nixConfig` is **not** auto-accepted without the explicit flag.

Refs #625, #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 01:15 PM_

Landed on the migration branch via #782.

