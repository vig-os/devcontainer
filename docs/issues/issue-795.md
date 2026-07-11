---
type: issue
state: closed
created: 2026-07-01T08:25:41Z
updated: 2026-07-03T12:03:07Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/795
comments: 2
labels: feature, area:workspace, effort:medium, semver:minor
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:45.363Z
---

# [Issue 795]: [feat(flake): mkProjectServices — process-compose + services-flake helper for local dev services](https://github.com/vig-os/devkit/issues/795)

**Source:** ADR `docs/rfcs/ADR-nix-devenv-strategy.md` (#794), local-services axis. The ADR *adopts* `process-compose` + `services-flake` as the org default for local dev services; this issue *implements* the shared helper.

## Context

Dropping `cachix/devenv` (the org direction — see #794, exo-fleet#76) removes the one capability plain `pkgs.mkShell` lacks: `devenv up`-style orchestration of local services (MinIO, Postgres, …) for development. The ADR picks the nix-native replacement — `process-compose` (daemon-free single-binary process runner) + `juspay/services-flake` (NixOS-like service modules) — because it keeps service versions in the same nixpkgs lock/SSoT, is GC-rooted with the flake, needs no container daemon, and carries no IFD cold-eval cost.

## Goal

Provide a shared `mkProjectServices` helper (alongside `mkProjectShell` in `flake.nix`) that a consuming repo can wire into its flake to expose `nix run .#services` (or a `just up` verb) booting a declared set of local services from a plain `pkgs.mkShell`, with **no container runtime** required.

## Scope

- Add `mkProjectServices` to the flake and export it via `self.lib` (as `mkProjectShell` is).
- A minimal validating PoC: daemon-free **MinIO + Postgres** brought up from a plain mkShell, versions from the pinned nixpkgs, GC-rooted, teardown clean.
- Wire an optional `services`/`up` verb into the `assets/workspace/` scaffold + `justfile`, off by default (repos opt in).
- Resolve the `flake-parts` question: `services-flake` is idiomatically flake-parts, but the toolchain flake is `flake-utils`/`eachSystem`. Decide adopt-flake-parts vs manual `process-compose` wiring; record the cost.

## Non-goals

- No repo is forced to adopt services. This is opt-in tooling.
- Not adopting `devenv` (explicitly rejected in #794).

## Acceptance criteria

- [ ] `mkProjectServices` exported and documented in `docs/NIX.md`.
- [ ] PoC: `nix run .#services` boots MinIO + Postgres with no Docker/Podman daemon; a short eval-cost/timing note captured.
- [ ] Service versions come from the pinned nixpkgs (no out-of-lock image tags).
- [ ] Scaffold gains an opt-in `up` verb; existing consumers unaffected.
- [ ] The flake-parts-vs-manual decision is recorded.

Refs #794

---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 11:41 AM_

## PoC S3 service: SeaweedFS instead of MinIO

Heads-up for the acceptance criteria: the PoC boots **SeaweedFS + Postgres**, not MinIO + Postgres as originally written.

While implementing, `nix build` refused the pinned `pkgs.minio`: nixpkgs marks MinIO with `knownVulnerabilities` on **both** the stable (nixos-26.05) and unstable channels — six unfixed CVEs (unauthenticated object write via unsigned-trailer uploads ×2, JWT algorithm confusion in OIDC, LDAP login brute-force, SSE metadata injection, S3 Select DoS) plus the blanket note:

> minio has been abandoned by upstream and security issues won't be fixed. Users should migrate to alternatives such as Garage, SeaweedFS, or Ceph.

Building it would require a `permittedInsecurePackages` exception, which is the wrong default for the org's blessed services PoC. `services-flake` ships a first-class **seaweedfs** module (maintained, S3-compatible gateway with health probes), so the PoC uses that; MinIO remains reachable via `mkProjectServices` for repos that consciously opt into the insecure-package exception (documented in `docs/NIX.md`).

cc @gerchowl — flagging since you may be working with S3 buckets elsewhere: anything provisioning MinIO (devenv `services.minio`, exo-fleet, etc.) is on an upstream-abandoned server with unfixed CVEs; SeaweedFS/Garage are the nixpkgs-recommended migration targets.

Refs #794

---

# [Comment #2]() by [c-vigo]()

_Posted on July 3, 2026 at 12:03 PM_

Closed in #807 

