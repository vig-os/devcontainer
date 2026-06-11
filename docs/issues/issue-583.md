---
type: issue
state: closed
created: 2026-06-10T11:20:44Z
updated: 2026-06-10T12:44:27Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/583
comments: 2
labels: bug, priority:high, area:ci, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-11T06:57:22.898Z
---

# [Issue 583]: [RC artifacts never pruned from GHCR: promote-release cleanup 404s silently](https://github.com/vig-os/devcontainer/issues/583)

## Summary
The `Cleanup RC artifacts` job in `promote-release.yml` reports success on every release but never actually deletes RC images from the `devcontainer` GHCR package. Leftover tags accumulate (`0.3.5-rc1`, `0.3.5-rc1-arm64`, `0.3.5-rc1-amd64`, `0.3.4-rc1*`, ...): https://github.com/vig-os/devcontainer/pkgs/container/devcontainer/versions

## Root cause
In the promote run for 0.3.5 (job `Cleanup RC artifacts`), every GHCR delete failed:

    gh: Package not found. (HTTP 404)
    {"message":"Package not found.",...,"status":"404"}
    ERROR: Command failed after 3 attempts: gh api -X DELETE /orgs/vig-os/packages/container/devcontainer/versions/<id>
    WARN: delete failed for id=<id>

The same token lists versions fine (GET works), and the git-tag delete (`0.3.5-rc1`) succeeded. Deleting an org container package version requires **admin on the package** (delete:packages / admin), not read/write; when the identity lacks it, GitHub returns a misleading **404 instead of 403**. The `RELEASE_APP` token used for the deletes can read but not delete the package.
Refs: https://docs.github.com/en/rest/packages/packages , https://github.com/dataaxiom/ghcr-cleanup-action/issues/74

## Why it has gone unnoticed (recurring)
- Failures are swallowed: `gh api -X DELETE ... || echo "WARN: delete failed"`.
- The job is `continue-on-error: true` with no post-verification, so it is always green.

## Second bug (masked by the 404s)
The "orphaned sha256-only" rule deletes **every** `sha256-*` tagged version. Those are cosign signature/attestation objects, including the signatures of the live 0.3.5/0.3.4/0.3.3 releases (e.g. `sha256-44f8742...` is the signature for the current `0.3.5`/`latest` digest). If permissions are fixed without changing this logic, promote-release would start deleting published release signatures.

## Impact
- GHCR fills with stale RC images and orphaned signatures.
- A future permission fix alone would delete live release signatures (cosign verification breakage).

## Proposed fix
See first comment.
---

# [Comment #1]() by [c-vigo]()

_Posted on June 10, 2026 at 11:20 AM_

## Proposed fix

### 1. Permission (root blocker)
Grant Admin on the `devcontainer` GHCR package to the deleting identity:
- Package -> Settings -> "Manage Actions access" -> add repo `vig-os/devcontainer` with role **Admin**, then switch the deletes in the cleanup job to `GITHUB_TOKEN` (the job already declares `packages: write`); or
- Grant the `RELEASE_APP` GitHub App Admin on the package and keep using the App token.

Without this, no code change can delete anything (GET works, DELETE 404s).

### 2. Scope the signature/attestation deletion safely
Replace the blanket "all tags are sha256-*" rule with digest-aware pruning:
- Resolve each RC tag being deleted to its manifest digest.
- Delete only `sha256-<rc-digest>*` signature/attestation objects.
- Never delete a `sha256-*` object whose digest is referenced by a current tag (especially the just-published `${VERSION}` / `latest`).

### 3. Make failures loud / idempotent
- On a delete 404, re-GET the version: if gone, treat as success (idempotent); if still present, it is a permission failure -> record it.
- Track failures; after the pass, re-list the package and assert no `${VERSION}-rc*` tags remain. On leftovers, surface it (fail the step, or open/append a tracking issue since cleanup runs post-merge) instead of exiting 0.

### Backfill
After the permission fix, manually prune the existing leftovers (`0.3.5-rc1*`, `0.3.4-rc1*`) and any orphaned RC signatures.

---

# [Comment #2]() by [c-vigo]()

_Posted on June 10, 2026 at 12:44 PM_

Fixed in #584 — GHCR RC cleanup now uses GITHUB_TOKEN with package Admin, digest-aware selection, and loud verification.

