---
type: issue
state: closed
created: 2026-07-04T22:14:42Z
updated: 2026-07-04T22:32:33Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/857
comments: 2
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:35.278Z
---

# [Issue 857]: [Smoke-test dispatch failed for 0.4.0-rc3](https://github.com/vig-os/devkit/issues/857)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.4.0-rc3`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `28720740438`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/28720740438
- source_sha: `3b188e47bbcad0870648bb08d1da94316aa6f8c1`
- correlation_id: `vig-os/devcontainer:28720740438:0.4.0-rc3`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28721208567
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/189
- release PR: not created

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `failure`
- ready-release-pr: `skipped`
- trigger-release: `skipped`
- wait-release-pr-ci: `skipped`
- trigger-promote-release: `skipped`
- summary: `failure`

## Manual cleanup guidance
- Inspect deploy/release PRs and workflow logs before retrying.
- If needed, close stale release PRs and delete stale `release/<version>` branch.
- Do not rewrite or delete **published** GitHub Releases (or their linked tags when **immutable releases** are enabled) to retry the same version; bare git tags without a published release are not locked by that feature unless a tag ruleset applies.
- After fixing the root cause upstream, publish a **new** RC tag (or a new final attempt only after branch/tag state matches your release policy), then rely on a fresh dispatch.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 10:16 PM_

**Diagnosis — the #810 PR-body bug, shipped to consumers.** rc3 got the furthest yet: consumer CI green inside the rc3 image (typos fix #856 validated), **deploy PR merged**, downstream release cycle started. The downstream `prepare-release` run then died at `Create draft PR to main` with `GraphQL: Body is too long (maximum is 65536 characters)`.

Root cause: #812 capped the PR body only in **this repo's** `prepare-release.yml`; the **shipped consumer copy** (`assets/workspace/.github/workflows/prepare-release.yml:295-321`) still interpolates the full changelog section uncapped. The smoke-test repo's CHANGELOG is seeded from our `.devcontainer/CHANGELOG.md` (receiver unprepares the 0.4.0 section into Unreleased), so its release PR body is the same ~67k chars that overflowed upstream.

Fix: port the same cap (65,000-char budget, line-boundary truncation, pointer to the release branch's full `CHANGELOG.md`) to the shipped workflow. `release-core.yml` (shipped) has no PR-body refresh step, so this is the only consumer-side site. The deploy sync will carry the fixed workflow to the smoke-test repo on the next candidate.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 10:32 PM_

Fixed by #858 (merged): the shipped consumer `prepare-release.yml` now caps its draft-PR body with the same line-boundary truncation as #812/#830. The deploy sync carries it downstream on the next candidate (rc4).

