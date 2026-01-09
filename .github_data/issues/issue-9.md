---
type: issue
state: closed
created: 2025-12-10T08:39:42Z
updated: 2025-12-15T08:42:46Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/9
comments: 5
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-09T16:17:36.775Z
---

# [Issue 9]: [Freeze image version in docker-compose.yml instead of using 'dev' tag](https://github.com/vig-os/devcontainer/issues/9)

## Issue

The `.devcontainer/docker-compose.yml` currently uses the `dev` tag:

```yaml
image: ghcr.io/vig-os/devcontainer:dev
```

## Question

After deployment of the devcontainer to a project, should the image version be frozen/pinned instead of using `dev`?

### Considerations:
- **`:dev`** - Currently used, but this tag is for development builds and may change unexpectedly
- **`:latest`** - Points to the most recent stable release, but still not frozen
- **Pinned version (e.g., `:1.0`)** - Would provide stability and reproducibility

## Context

The `dev` tag is used by `make build` for local development builds. For production use or when deploying to other projects, a frozen version would:
1. Ensure reproducible builds
2. Prevent unexpected breaking changes
3. Allow controlled upgrades

## Discussion Points
- Should this file use a pinned version, `latest`, or keep `dev`?
- If a pinned version is preferred, should the `{{IMAGE_TAG}}` placeholder system be extended to cover the `.devcontainer/docker-compose.yml` as well?

cc @c-vigo
---

# [Comment #1]() by [c-vigo]()

_Posted on December 10, 2025 at 08:55 AM_

The file does use a pinned version, but only at release stage

This way you guarantee that if you use a dev version, it reflects that

Release 0.1 coming soon, then you can verify and close

---

# [Comment #2]() by [c-vigo]()

_Posted on December 12, 2025 at 01:58 PM_

@gerchowl may we close this issue?

---

# [Comment #3]() by [gerchowl]()

_Posted on December 12, 2025 at 05:33 PM_

Lemme test in a test repo that it unpacks for me with renaming

---

# [Comment #4]() by [gerchowl]()

_Posted on December 15, 2025 at 08:19 AM_

works

---

# [Comment #5]() by [c-vigo]()

_Posted on December 15, 2025 at 08:42 AM_

Fixed in #11 

