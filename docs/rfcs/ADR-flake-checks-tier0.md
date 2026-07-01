---
rfc: ADR-flake-checks-tier0
date: 2026-07-01
title: Flake checks as CI Tier 0 (nix-fast-build), effectful jobs GH-orchestrated
status: accepted
authors:
  - Carlos Vigo (c-vigo)
---

# ADR: Flake checks as CI Tier 0

**Decision (TL;DR):** Make the flake's `checks.<system>` the **Tier-0** CI gate and
run them with **`nix-fast-build`** (parallel, eval-cached) instead of a serial
`nix flake check`. Keep every **effectful** job — image testinfra, integration,
the vulnix CVE-DB scan, multi-arch build, publish/cosign/SBOM/Cachix, and the
**impure pre-commit hooks and pytest units** — **GitHub-Actions-orchestrated** in
their own jobs. Adopt **`nix-fast-build` on the existing runners now**; keep
**garnix** (hosted, zero-YAML) as a documented future option and defer any
Tier-1 self-hosted builder (Hydra/Buildkite) as a separate, later decision.

## Problem statement

Post-migration the flake already exposes a growing set of pure quality gates —
`formatting` (treefmt: nixfmt + ruff-format + taplo, #777), `deadnix`/`statix`
(#777), `devShell`/`devShellTools` (#674), and `pre-commit` (the sandbox-pure hook
subset via git-hooks.nix + prek, #778). CI ran them with a single serial
`nix flake check --accept-flake-config`. As the check set grows, serial evaluation
and building is the bottleneck, and there was no articulated boundary between
"checks that are pure functions of the source" (reproducible, cacheable, portable)
and "checks that need the world" (a built image, a running container, the CVE
database, the network, the project venv). This ADR draws that line.

## The tiering

### Tier 0 — pure, in `checks.<system>`, driven by nix-fast-build

Run by `nix run .#nix-fast-build -- --skip-cached --no-nom --flake .#checks.<system>`
in the `project-checks` job. These are pure functions of the flake source and the
pinned `nixpkgs`, so they are reproducible, binary-cacheable (Cachix), and could
move to a hosted evaluator unchanged:

- `formatting` — the tree is treefmt-clean.
- `deadnix`, `statix` — the authored `flake.nix` is dead-code- and anti-pattern-free.
- `devShell` — the dev-shell closure builds.
- `devShellTools` — the parity-test SSoT evaluates non-empty.
- `pre-commit` — the **sandbox-pure** hook subset (treefmt, ruff, shellcheck,
  yamllint, typos, taplo-lint, the `pre-commit-hooks` meta hooks, and the
  `vig-utils`/`bandit` hooks wired to hermetic Nix binaries), via git-hooks.nix
  driven by prek (#778).

`nix-fast-build` evaluates through `nix-eval-jobs`, so eval/type errors still fail
the gate; it builds the derivations in parallel with an eval cache. It is exposed
as `packages.<system>.nix-fast-build` (a passthrough of the pinned nixpkgs build),
**not** added to `devTools` — so CI invokes it reproducibly via `nix run` without
baking a CI-only tool into the dev-shell or the image closure (it also has no
top-level `--version`, which would trip the dev-shell parity check).

The flake **output schema** that `nix-fast-build` does not exercise (it only builds
`checks`) — the treefmt `formatter`, the `checks` attr names, the `install` app,
the `nixos`/`homeManager` modules — is validated cheaply by
`tests/test_flake_checks.py` (minus its slow `nix flake check` build, now covered
by nix-fast-build).

### GH-orchestrated — effectful, stays in dedicated jobs

Deliberately **not** flake checks, because a Nix sandbox has no network, no
recursive Nix, no built image, no running container, and no project venv:

- **Image testinfra** (`test-image`) and **integration** (`test-integration`) —
  need the built OCI image loaded into podman and a running devcontainer.
- **Dev-shell ↔ image parity** (`test_flake_devshell.py`) — runs `nix develop`
  recursively; a sandboxed check cannot.
- **vulnix CVE scan** (`security-scan.yml`, `release.yml`) — needs the live CVE
  database; intentionally impure and time-varying.
- **Multi-arch build, publish, cosign, SBOM, Cachix push** — registry/OIDC/network.
- **Impure pre-commit hooks** — `generate-docs`, `sync-manifest`, `pip-licenses`,
  `pymarkdown`, `no-commit-to-branch`, `check-agent-identity`, and the
  `commit-msg`/`prepare-commit-msg`-stage hooks. These need the repo tree, the
  project venv, git state, or a tool absent from nixpkgs, so they run via the
  runner's `prek`/`pre-commit run --all-files` step, not the sandbox check.
- **Pytest units** (`tests/test_utils.py`, `packages/vig-utils/tests/…`) — several
  read repo files (`docs/`, `CHANGELOG.md`) or exercise git/GitHub-shaped code
  (`test_gh_issues`, `test_renovate_changelog_pr`, `check_action_pins`), so the
  suite is **not** cleanly sandbox-pure. Wrapping the genuinely-pure subset as a
  `checks.vigUtilsTests` derivation is a reasonable **future** extension; it is
  deliberately **out of scope here** rather than forced, to avoid a flaky check.

## Driver decision: nix-fast-build now, garnix later

- **`nix-fast-build` on existing GitHub runners (chosen).** No new hosted
  dependency, no new secrets, reuses the Cachix cache already provisioned. Zero
  onboarding cost; parallelism + eval cache today. It is a drop-in for the serial
  `nix flake check` build step.
- **garnix (documented alternative).** Hosted, zero-YAML, builds every flake
  output on push and reports per-output status. Attractive when the pure-check set
  grows large or we want the checks off the GitHub-runner minutes budget; costs a
  third-party app install + trust. Revisit if Tier 0 build time becomes material.
- **Tier 1 — self-hosted (Hydra / Buildkite).** Out of scope; a separate, later
  decision if we ever need a persistent builder farm.

## Consequences

- CI builds the pure checks in parallel with an eval cache; adding a new pure
  check (a new `checks.<system>.*`) automatically joins the Tier-0 gate with no
  workflow edit.
- The pure/effectful boundary is explicit, so contributors know where a new gate
  belongs: pure and source-only → a flake check; needs the world → a GH job.
- `nix flake check`'s incidental output-schema validation is preserved by the
  `test_flake_checks.py` step rather than lost.

## Reconsider if

- The pure-check build time on GitHub runners becomes material → evaluate garnix.
- A genuinely-pure pytest subset is factored out → wrap it as `checks.vigUtilsTests`.
- We need a persistent builder or cross-arch check farm → revisit Tier 1.

Refs: #779, #674, #777, #778.
