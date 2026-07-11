---
type: issue
state: closed
created: 2026-07-07T09:12:21Z
updated: 2026-07-08T07:41:13Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/884
comments: 1
labels: feature, priority:medium, area:workspace, effort:large, semver:minor
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:29.855Z
---

# [Issue 884]: [feat(flake): modular capability shells — opt-in vigos capability modules (native, geant4, rust, …) on top of mkProjectShell](https://github.com/vig-os/devkit/issues/884)

### Description

Implement the modular capability layer that ADR-nix-devenv-strategy already
anticipates ("future modular `vigos.devShells.{cpp,geant4,…}` as the org grows
language stacks"): a battery of opt-in **capability modules** shipped by this
flake, composing onto the existing `mkProjectShell` builder, so a consumer
declares *capabilities* instead of hand-picking packages.

A pure-Python repo enables nothing and stays exactly as thin as today. A
scientific repo enables e.g. `native` and gets the full toolchain
(compiler **and** the build tools native sdist builds actually need)
from the same pinned nixpkgs, reproducibly, in direnv-mode — without any change
to the published base image.

Consumer surface (v1 — simple string list; per-module option attrsets can come
later without breaking this):

    devShells.default = inputs.devcontainer.lib.mkProjectShell {
      inherit pkgs;
      modules = [ "native" ];            # opt-in capability modules
      extraPackages = [ pkgs.my-extra ]; # existing escape hatch, unchanged
    };

### Problem Statement

0.4.0 downstream validation (#639) showed the real native-build story: the base
image deliberately ships no C/C++ toolchain, and a bare compiler would not be
enough anyway — consumers need compiler + headers + libs (catima, OCCT, Geant4,
ROOT, f2py). The sanctioned path is "provide toolchains via the project flake in
direnv-mode" (#882; cf. #879 fix + #854), but today each consumer hand-rolls
that flake content. `mkProjectShell` offers only a flat `extraPackages`, so:

- every native-deps repo re-derives the same package sets (DRY violation; the
  org maintains N copies of "how to get a working C++/Geant4 devshell");
- there is no curated, tested, Renovate-tracked definition of a capability —
  quality varies per repo;
- "I do not want C++ in my pure-Python project" is only guaranteed by omission,
  not by an explicit, named contract.

The builder-level questions are settled and are **not** reopened here:
ADR-nix-devenv-strategy (accepted) keeps plain `pkgs.mkShell` via
`mkProjectShell`, rejects `cachix/devenv` / `numtide/devshell` as the shared
builder, and settles services on process-compose + services-flake (#795).
git-hooks.nix is already the hooks substrate (#778, extended consumer-side by
#883). This issue implements the modular layer *on top of* those decisions.

### Proposed Solution

1. **Design the module contract** (small design note or ADR addendum in
   `docs/rfcs/`, following the conventions of the in-flight home-modules ADR
   work): v1 shape is a string list (`modules = [ "native" … ]`); a module
   contributes **packages, env vars, and shellHook fragments only** in v1
   (hooks-contribution — e.g. `native` bringing `clang-format` into the #883
   hook set — is recorded as an open design-note question, not v1 scope);
   composition rules with `extraPackages`/`shellHook`; migration path to
   per-module option attrsets (e.g. geant4 dataset selection) when needed.
2. **Implement the composition seam in `mkProjectShell`** (flake.nix): accept
   `modules`, merge module contributions, keep the zero-module path
   byte-identical to today (parity test `tests/test_flake_devshell.py` must be
   unaffected — the image continues to bake `devTools` only).
3. **Ship the `native` module first** — `stdenv.cc`, `cmake`, `gnumake`,
   `pkg-config` (+ sane CC/CXX): the generic sdist-building capability and
   #879's long-term answer, with demonstrated need (hyrr/pycatima, #639).
   Named candidates gated on a concrete consumer ask (YAGNI): `geant4`
   (fast-follow once an EXOMA/EXOPET repo asks), `rust`, `fortran`/`f2py`,
   `root`.
4. **Document** in MIGRATION.md / NIX.md: how a consumer enables modules, the
   explicit statement that the published image stays base-only and modules are
   a direnv-mode/devshell feature, and a worked hyrr-style example.
5. **Tests**: flake check evaluating each shipped module on both systems; a
   smoke test that the `native` module can build a trivial C-extension sdist
   with uv.

#### Acceptance criteria

- [ ] Module contract designed and recorded (docs/rfcs addendum or design note)
- [ ] `mkProjectShell` composes modules; no-module path unchanged (parity test green)
- [ ] `native` module ships and a uv sdist build (e.g. pycatima-class) succeeds in its devshell
- [ ] Candidate modules (`geant4`, `rust`, `fortran`, `root`) named in docs with the ask-driven gate; when a module ships, its devshell smoke check ships with it (e.g. `geant4-config` resolves)
- [ ] Consumer docs + example updated (MIGRATION.md / NIX.md)
- [ ] Published image contents unchanged (base only)

### Alternatives Considered

- **`cachix/devenv` (`languages.*.enable`)** — the off-the-shelf version of
  this model; **rejected as the shared builder by ADR-nix-devenv-strategy**
  (accepted): interposes a framework between the `devTools` SSoT and PATH,
  breaks the dev-shell↔image parity approach, own substituter; org rejected it
  before (#27). Note for the record: devenv 2.x (2026) reworked eval
  performance (incremental eval cache) so the ADR's measured ~165s IFD figure
  is stale for 2.x — but 2.x is *more* framework (own CLI as primary
  interface, C FFI backend, built-in process manager superseding
  process-compose), so the architectural objections stand. If someone wants to
  re-litigate, that is an ADR revision with new org-level facts, not this
  issue.
- **`numtide/devshell`** — ergonomics layer only; rejected in the same ADR
  (no capability we lack; `just --list` is the verb menu).
- **Status quo (`extraPackages` only)** — works today (talys proves it) but
  keeps N hand-rolled copies of each capability across consumers; no curated,
  tested definition. This issue is exactly the DRY consolidation of that.
- **Baking toolchains into the published image** — rejected in #879/#882:
  inflates every consumer's image and still lacks the per-project libraries
  (Geant4/OCCT/ROOT) native builds need.
- **Per-module option attrsets in v1** — deferred: the string list covers all
  shipped v1 modules; attrset options (e.g. geant4 datasets) come with the
  first module that needs them, additively.

### Additional Context

Origin: 0.4.0 Phase-B downstream validation (#639) — hyrr blocked on native
sdist builds (#879), talys green via its own flake in direnv-mode. The module
battery generalizes talys's working pattern into shipped, reusable capability
definitions. #882 documents the contract this implements the ergonomic layer
for.

Relates to the planned declarative `.vig-os` manifest work: a future
`DEVKIT_MODULES=…` key can drive scaffold-level module enablement; the
flake-level contract from this issue is the foundation it would map onto.

### Impact

Consumers with native/scientific dependencies get curated, pinned, tested
capability shells instead of hand-rolled flake content; pure-Python consumers
are untouched (explicitly zero-cost). Image size and contents unchanged.
Semver: **minor** (new lib surface, additive).

### Changelog Category

Added

Refs: #882, #879, #854, #639, #778, #795, #883

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:41 AM_

Delivered by #901 (merged to `dev` on 2026-07-07). Closing as complete for milestone 0.5.

