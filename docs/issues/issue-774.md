---
type: issue
state: closed
created: 2026-06-30T12:52:01Z
updated: 2026-06-30T13:33:56Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/774
comments: 1
labels: chore, priority:medium, area:image, effort:small
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:49.918Z
---

# [Issue 774]: [[CHORE] Flake cheap-fix batch: darwin guard, overlay eval hoist, uv downloads URL drift + Renovate, nixfmt glob](https://github.com/vig-os/devkit/issues/774)

**Source:** PR #670 roadmap, thread A — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). Bundles the "cheap fixes" the reviewer flagged; all touch `flake.nix`, so batched into one PR (Nits-batch precedent #759). Lands on the migration branch before dev merge.

## Items
1. **darwin guard** — `eachDefaultSystem` advertises the Linux-only image on darwin, breaking `nix flake check --all-systems` on a Mac. Guard the image/Linux-only attrs to Linux systems.
2. **hoist `import nixpkgs-unstable`** out of the overlay closure so it doesn't re-evaluate per attribute access.
3. **`uvPythonDownloadsJsonUrl` drift** (`flake.nix` ~146) — pinned to a literal uv version in a raw-githubusercontent URL while `uv` floats from nixpkgs. Derive the URL from `pkgs.uv.version`.
4. **Renovate regex-manager** rule for the `pip-licenses` wheel hash (`flake.nix` ~276-281).
5. **`nixfmt --check` glob** all `*.nix` (today only `flake.nix`).

## Acceptance
- `nix flake check` (host system) green; `--all-systems` no longer errors on darwin eval.
- `uvPythonDownloadsJsonUrl` derives from `pkgs.uv.version` (no literal version drift).
- Renovate config validates; nixfmt check covers all `*.nix`.

Refs #625, #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 01:33 PM_

Landed on the migration branch via #783.

