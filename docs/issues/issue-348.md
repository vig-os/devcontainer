---
type: issue
state: closed
created: 2026-03-17T15:47:26Z
updated: 2026-03-17T16:47:41Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/348
comments: 0
labels: area:ci
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:21.393Z
---

# [Issue 348]: [[CI] Migrate release workflow from actions/attest-sbom to actions/attest](https://github.com/vig-os/devcontainer/issues/348)

## Context
Release workflow run [#23201577188](https://github.com/vig-os/devcontainer/actions/runs/23201577188) shows these publish-job warnings tied to SBOM attestation:
- actions/attest-sbom has been deprecated, please use actions/attest instead
- Please check that the \"artifact-metadata:write\" permission has been included
- Failed to create storage record: no artifacts found

## Goal
Migrate from `actions/attest-sbom` to `actions/attest` in `.github/workflows/release.yml` and validate warning behavior.

## Scope
- Replace `actions/attest-sbom` step with equivalent `actions/attest` usage.
- Keep existing subject and SBOM inputs equivalent.
- Re-run release workflow (or targeted validation) and confirm warnings 4/5/6 are resolved or reduced to expected behavior.

## Acceptance Criteria
- `release.yml` no longer uses `actions/attest-sbom`.
- Migration preserves SBOM attestation behavior (push to registry remains enabled).
- Run notes document whether additional permissions are required after migration.
