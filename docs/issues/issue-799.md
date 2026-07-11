---
type: issue
state: closed
created: 2026-07-02T12:47:30Z
updated: 2026-07-03T07:46:43Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/799
comments: 1
labels: chore, area:image, area:workspace, effort:medium, semver:minor
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:44.964Z
---

# [Issue 799]: [[CHORE] Drop the sidecar / multi-container capability entirely](https://github.com/vig-os/devkit/issues/799)

## Context

The devcontainer shipped a **sidecar** capability: run secondary containers alongside the primary devcontainer via docker-compose (`docker-compose.project.yaml`), a `just sidecar <name> <recipe>` exec-into-container pattern, and a build-in-a-sidecar workflow (tested by `tests/fixtures/sidecar.Containerfile`). After the Nix migration (#625) this no longer earns its keep:

- **Toolchains** (compilers, Geant4, analysis libs) belong in Nix devShells (`vigos.lib.mkProjectShell` + the future modular `vigos.devShells.{cpp,geant4,dataAnalysis}`), on PATH — not a container you `podman exec` into. This obsoletes the build-isolation sidecar.
- **Local software services** (Postgres, Redis, MinIO, …) are handled by `process-compose` + `services-flake` per ADR #794, implemented in #795 (`mkProjectServices`) — daemon-free, same nixpkgs lock, no container runtime.
- The only residual case (opaque/vendor images, prod-parity, hardware sims) does not justify maintaining a bespoke sidecar exec framework plus its tests/fixtures and the lone `hadolint` dependency.

**Decision: remove the sidecar / multi-container capability entirely.** Supersedes #719 (hadolint + sidecar-fixture fate).

## Scope

- Delete pure sidecar fixtures: `tests/fixtures/sidecar.Containerfile`, `tests/fixtures/test-build.sh`, `tests/fixtures/justfile`.
- Remove the `test-sidecar` service from `tests/docker-compose.test.yml` (keep `init-workspace`/`workspace-inspector`).
- Remove sidecar fixtures/tests from `tests/conftest.py` (`sidecar_image`, `devcontainer_with_sidecar`) and `tests/test_integration.py` (`TestSidecarConnectivity`).
- Remove sidecar recipes: `assets/workspace/.devcontainer/justfile.devc` (SIDECAR group), `justfile`, `justfile.podman`, `assets/workspace/justfile.project`.
- Remove sidecar test invocation/cleanup in `.github/actions/test-integration/action.yml`.
- Drop `hadolint` from the flake `devTools` (its only lint target was the sidecar Containerfile) and its assertions in `tests/test_image.py`.
- De-sidecar the scaffold compose docs (`docker-compose.yml`, `docker-compose.project.yaml`) — keep the DooD socket (still needed for container builds), drop the sidecar framing.
- Docs: `docs/templates/TESTING.md.j2`, `docs/templates/CONTRIBUTE.md.j2`, `tests/README.md` (regenerate `TESTING.md`/`CONTRIBUTE.md`).
- ADR #794: record the containers-vs-devShell-vs-services-flake boundary (why sidecars are removed).
- CHANGELOG: **Removed** entry (semver:minor — downstream capability removed) + migration note (devShells / services-flake #795).

## Acceptance criteria

- [ ] No `sidecar` / `test-sidecar` / build-in-sidecar references remain in source (excluding historical `docs/issues`/`docs/pull-requests` mirrors).
- [ ] `just`, integration tests, `prek run --all-files`, and flake eval green; `hadolint` gone from `devTools` with no dangling assertion.
- [ ] `TESTING.md`/`CONTRIBUTE.md` regenerated; `sync-manifest` + `generate-docs` pass.
- [ ] ADR #794 amended; CHANGELOG **Removed** entry + downstream migration note.
- [ ] #719 closed as subsumed.

Refs: #625, #719, #794, #795
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 07:46 AM_

Resolved by #800 (merged to `dev`). The sidecar / multi-container capability (recipes, compose examples, fixtures, CI wiring) has been removed.

