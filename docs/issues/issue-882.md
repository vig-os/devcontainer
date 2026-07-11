---
type: issue
state: closed
created: 2026-07-07T09:00:36Z
updated: 2026-07-08T07:54:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/882
comments: 1
labels: docs, priority:medium, area:image, effort:small
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:30.650Z
---

# [Issue 882]: [[DOCS] Formalize the native-build contract — C/C++ toolchains come from the project flake, not the image](https://github.com/vig-os/devkit/issues/882)

### Description

0.4.0 consumer field-validation (#639, EXOMA/hyrr) showed that `uv sync` hard-fails in
`ghcr.io/vig-os/devcontainer:0.4.0` for any dependency without a cp314 wheel (pycatima):
the image ships no C/C++ compiler and the baked CPython sysconfig points CC/CXX at a
nix-store path absent from the runtime image (#879). The *mechanical* half is #879
(sanitize sysconfig so build backends fall back to PATH discovery). This issue is the
*contract* half: document, as official policy, **where native builds belong** so
consumers with native deps (Geant4, ROOT, OCCT, catima, f2py) have a supported target
instead of waiting for a fatter base image.

The contract already half-exists — `docs/MIGRATION.md` § "Adding tools the image does
not ship" states the image is deliberately minimal and points at
`vigos.lib.mkProjectShell { extraPackages = [ … ]; }` — but it is written around CLI
tools (Rust example) and says nothing about **native Python sdist builds**, which is
where consumers actually hit the wall. Formalize:

1. **The tiered contract**, stated explicitly:
   - *Pure-Python / wheel-only repos* — image works as-is; nothing to do.
   - *Repos with native deps (preferred path)* — provide the toolchain via the project
     flake: `mkProjectShell { extraPackages = [ pkgs.stdenv.cc pkgs.cmake pkgs.pkg-config … ]; }`.
     Inside `nix develop`/direnv the stdenv exports working `CC`/`CXX`, so
     scikit-build-core/setuptools/meson-python find a real compiler regardless of the
     baked sysconfig. This is the path EXOMA/talys already validated (#639 consumer 2/2).
   - *Devcontainer-mode repos with native deps (middle path — document it!)* — no full
     direnv migration required: the image ships Nix with flakes enabled, so inside the
     container `nix develop -c just sync` (against the project flake) or ad-hoc
     `nix shell nixpkgs#gcc nixpkgs#cmake -c uv sync` works today. Name this explicitly
     as the interim answer for repos like hyrr while the cp314 wheel ecosystem matures.
2. **A worked example with heavyweight scientific deps** — a devshell adding
   `pkgs.geant4` / `pkgs.root` alongside the compiler, showing that a bare compiler in
   the base image would *not* have sufficed (native builds need headers + libs + build
   config, which only a pinned flake provides reproducibly).
3. **What we will NOT do** — bake gcc/cmake into the published image (breaks the
   minimal-image stance, inflates every consumer, and still fails for anything needing
   third-party headers/libs). Record the reasoning so the request doesn't resurface
   per-consumer.
4. **CI boundary** — running consumer CI inside the project devshell (so the contract
   holds in CI, not just locally) is the nix-direct CI lane, tracked in #854; this issue
   only cross-references it. Until #854 lands, devcontainer-mode CI can use the
   in-container `nix develop -c` form from (1c).

### Documentation Type

Add new documentation

### Target Files

- `docs/MIGRATION.md` — extend § "Adding tools the image does not ship" into the
  explicit native-build contract (tiers, worked Geant4 example, in-container middle
  path, non-goals). Direct file, not template-generated.
- `docs/NIX.md` — cross-reference from the flake-architecture side if needed.

### Related Code Changes

- #879 — sysconfig sanitize (graceful PATH fallback in-image); this issue documents the
  contract that fix degrades into.
- #854 — nix-direct (direnv-mode) CI lane; the CI enforcement of this contract lives
  there, not here.
- #639 — field evidence: talys (direnv-mode, native toolchain from flake) green;
  hyrr (devcontainer-mode, pycatima sdist) blocked.

### Acceptance Criteria

- [ ] MIGRATION.md states the tiered contract (wheel-only / flake-provided toolchain /
      in-container `nix develop` middle path) with copy-pasteable snippets
- [ ] Worked example covering a compiler-only case (`stdenv.cc` + `cmake`) and a
      heavyweight case (`pkgs.geant4`)
- [ ] Explicit non-goal recorded: no C/C++ toolchain in the base image, with rationale
- [ ] Cross-links to #879 (mechanics) and #854 (CI lane) in place

### Changelog Category

Changed

### Additional Context

Field evidence and discussion: #639 (Phase-B downstream validation comments).
`mkProjectShell` is defined in `flake.nix` and already accepts
`extraPackages`; `pkgs.geant4` and `pkgs.root` exist in nixpkgs, so the worked example
is real, not aspirational.

Refs: #879, #854, #639

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

