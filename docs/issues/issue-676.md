---
type: issue
state: open
created: 2026-06-24T10:59:44Z
updated: 2026-06-24T10:59:44Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/676
comments: 0
labels: docs, priority:medium
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:58.167Z
---

# [Issue 676]: [[DOCS] Reconcile the CHANGELOG ## Unreleased section to the Nix end-state](https://github.com/vig-os/devcontainer/issues/676)

### Description

The `## Unreleased` section of `CHANGELOG.md` was written incrementally as the
Nix epic (#625) progressed and now contains internally contradictory,
point-in-time bullets that describe intermediate states rather than the end
state:

- The #632 entry states: "The Debian image is still built unchanged and the
  Docker `type=gha` build cache stays intact" — no longer true after #642.
- The #639 entry states: "Added a `builder: debian|nix` selector … (**default
  `debian`**)" — the selector was removed by #642; `release.yml`, `ci.yml`, and
  the `build-image` action are now Nix-only.

Before release, reconcile the Unreleased section so it reads as a single coherent
Nix end-state. Released entries (below `## Unreleased`) must not be touched.

### Documentation Type

Fix incorrect or outdated content

### Target Files

- `CHANGELOG.md` (`## Unreleased` section only)

### Related Code Changes

Cleans up after #632, #639, #642 (all under the same Unreleased block).

### Acceptance Criteria

- [ ] No Unreleased bullet claims a surviving Debian build path or a
      `builder: debian|nix` selector
- [ ] The Unreleased section is internally consistent and describes the Nix
      end-state (flake SSoT, Nix-only build, staged cutover)
- [ ] No entries below `## Unreleased` are modified

### Changelog Category

No changelog needed

### Additional Context

Part of the Nix migration epic #625. Should be done last, after the sibling
follow-up PRs have landed their own Unreleased entries.

