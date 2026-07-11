---
type: issue
state: closed
created: 2026-06-23T06:54:13Z
updated: 2026-07-01T11:19:16Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/638
comments: 1
labels: area:ci, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:11.922Z
---

# [Issue 638]: [T3.2 — Renovate `nix` manager for `flake.lock`](https://github.com/vig-os/devkit/issues/638)

Tracking: #625



## Context

Once the toolchain comes from the flake, the Renovate `dockerfile` base-digest loop is
replaced by maintenance of `flake.lock`. Renovate's `nix` manager + `lockFileMaintenance`
can bump the flake inputs through the normal PR/CI gate. The remaining `pep621`, `npm`, and
`github-actions` managers stay.

## Scope

**In:**
- Add the `nix` manager + `lockFileMaintenance` in `renovate.json`.
- Document the compensating control: include a `vulnix` before/after diff in each
  nixpkgs-bump PR (the `nix` manager won't name *which* CVE a rev bump fixes).

**Out:**
- The vulnix scanner setup itself (#637).

## Tasks

- [ ] Add the `nix` manager + `lockFileMaintenance` config
- [ ] Keep `pep621` / `npm` / `github-actions` managers
- [ ] Document the vulnix-diff compensating control in security docs

## Acceptance criteria

- Renovate opens `flake.lock` PRs through the normal CI gate.

## Dependencies

- **Depends-on:** #631.
- **Blocks:** none.

## Files

- `renovate.json`
- `CONTRIBUTE.md` / security docs

## Test notes

- Validate the Renovate config (`npx renovate-config-validator`) as part of the existing
  `test-renovate` recipe.

## Related issues

- **#604** (consolidate Trivy scan categories) — replacing the `dockerfile` base-digest update
  loop with `flake.lock` maintenance changes what Renovate produces; keep the scan-config SSoT
  documentation in #604 consistent with the new manager set.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30). `renovate.json` `enabledManagers` now includes `nix` + `lockFileMaintenance` for `flake.lock`, retaining pep621/npm/github-actions. Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

