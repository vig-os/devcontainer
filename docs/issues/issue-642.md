---
type: issue
state: closed
created: 2026-06-23T06:54:20Z
updated: 2026-07-08T07:54:38Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/642
comments: 1
labels: chore, priority:low, area:image, effort:small
assignees: none
milestone: 0.4.1
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:10.455Z
---

# [Issue 642]: [T4.4 — Decommission the Debian path](https://github.com/vig-os/devkit/issues/642)

Tracking: #625



## Context

After a full release cycle of green Nix builds and the #637 CVE gate met, the Debian
fallback can be removed. This closes the migration and leaves a single, Nix-based build path.

## Scope

**In:**
- Delete the Debian `Containerfile` + the `type=gha` Docker cache wiring.
- Drop dead CVE-strategy remnants left from the Debian/apt era.

**Out:**
- None.

## Tasks

- [ ] Remove `Containerfile` and `build/Containerfile`
- [ ] Remove `type=gha` Docker cache wiring from workflows
- [ ] Prune dead Debian/apt CVE-strategy remnants from docs

## Acceptance criteria

- Only the Nix build path remains.
- CI is green.
- The master issue is closeable.

## Dependencies

- **Depends-on:** #639 + one green release cycle.
- **Blocks:** none.

## Files

- `Containerfile`
- `build/Containerfile`
- `.github/workflows/*`
- `docs/*`

## Test notes

- Confirm the full suite (testinfra + bats + renovate validation) is green on the Nix-only
  build before closing.

## Related issues

- **#602 / #521** (nightly HIGH/CRITICAL gate issues) — these track the Debian/apt image's CVE
  surface; once the Debian path is gone they no longer apply. Close them as the Nix-only scan
  takes over (with #637).
- **#604** (stale Trivy alerts) — removing the Debian build retires the apt-based scan
  categories referenced there; ensure the dead categories are dismissed as part of cleanup.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

