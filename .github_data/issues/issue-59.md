---
type: issue
state: closed
created: 2026-02-17T18:57:15Z
updated: 2026-02-18T16:36:59Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/59
comments: 2
labels: discussion, priority:low, area:ci
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T16:37:21.143Z
---

# [Issue 59]: [Local build (just build) vs. CI build (build-image action): intended parity?](https://github.com/vig-os/devcontainer/issues/59)

cc @c-vigo

## Context

Reviewing PR #56 and the release workflows, I noticed that the local `just build` path and the CI `build-image` composite action use fundamentally different build pipelines.

## Current state

| Aspect | Local (`just build`) | CI (`build-image` action) |
|---|---|---|
| **Engine** | podman | Docker Buildx (`docker/build-push-action`) |
| **Output** | local podman image | tar file or registry push |
| **OCI labels** | none | full OCI metadata via `docker/metadata-action` |
| **Caching** | podman layer cache | `type=gha` (GitHub Actions cache) |
| **Build args** | `BUILD_DATE=""`, `VCS_REF=""` | fully populated from workflow context |
| **Prepare step** | `scripts/prepare-build.sh` | same `scripts/prepare-build.sh` |
| **Test flow** | `just test-image` -> pytest directly | build tar -> load into podman -> pytest |

The `scripts/prepare-build.sh` and the Containerfile are shared, so the image **content** is likely identical. But the build tooling, metadata, and test flow differ.

## Questions

1. **Is build-tool divergence intentional?** The local path uses podman directly while CI uses Docker Buildx. Is this a deliberate choice (podman for local dev, Buildx for multi-arch CI), or should local builds eventually also use Buildx (or podman's buildx equivalent)?

2. **Should local builds populate OCI labels?** CI images get full `org.opencontainers.image.*` labels. Local dev images get none (`BUILD_DATE=""`, `VCS_REF=""`). Is this fine for dev builds, or should `just build` populate at least basic metadata (e.g., `VCS_REF=$(git rev-parse HEAD)`)?

3. **Should there be a `just build-ci` recipe?** A recipe that mirrors the CI flow locally (build to tar, load, test with same env vars) would let developers catch CI-specific failures before pushing. Is this worth the complexity?

4. **Test-flow parity:** CI tests go through tar-export -> podman-load -> pytest, while local tests run pytest directly against the podman image. Should there be a `just test-ci` that replicates the CI test flow for pre-push validation?

## Why it matters

If CI builds are the only path to production, divergence is manageable — developers build locally for fast iteration and trust CI for the final artifact. But if a developer needs to debug a CI-only failure, there's currently no local way to reproduce the CI build/test flow.

Not necessarily requesting changes — just want to understand the intended long-term workflow.
---

# [Comment #1]() by [c-vigo]()

_Posted on February 18, 2026 at 02:28 PM_

> 1. **Is build-tool divergence intentional?** The local path uses podman directly while CI uses Docker Buildx. Is this a deliberate choice (podman for local dev, Buildx for multi-arch CI), or should local builds eventually also use Buildx (or podman's buildx equivalent)?

Not intentional, but probably harmless. Docker ecosystem in GitHub actions is much more developed. Podman was the first choice for local builds, and we require users to have podman to run the container anyway.

> 2. **Should local builds populate OCI labels?** CI images get full `org.opencontainers.image.*` labels. Local dev images get none (`BUILD_DATE=""`, `VCS_REF=""`). Is this fine for dev builds, or should `just build` populate at least basic metadata (e.g., `VCS_REF=$(git rev-parse HEAD)`)?

I'd argue they should not, since they are a development version and there is no guarantee there are uncommitted files.

> 3. **Should there be a `just build-ci` recipe?** A recipe that mirrors the CI flow locally (build to tar, load, test with same env vars) would let developers catch CI-specific failures before pushing. Is this worth the complexity?

Opinion: not worth it, the CI pipeline can eventually only be tested in CI.

> 4. **Test-flow parity:** CI tests go through tar-export -> podman-load -> pytest, while local tests run pytest directly against the podman image. Should there be a `just test-ci` that replicates the CI test flow for pre-push validation?

Same as 3.


---

# [Comment #2]() by [gerchowl]()

_Posted on February 18, 2026 at 04:36 PM_

Thanks for clarification.

