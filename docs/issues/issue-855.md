---
type: issue
state: closed
created: 2026-07-04T21:20:58Z
updated: 2026-07-04T21:39:05Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/855
comments: 2
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:35.670Z
---

# [Issue 855]: [Smoke-test dispatch failed for 0.4.0-rc2](https://github.com/vig-os/devkit/issues/855)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `0.4.0-rc2`
- release_kind: `candidate`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `28719441697`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/28719441697
- source_sha: `cbd2b712559f742e146c243d6f493733ad0e8ccf`
- correlation_id: `vig-os/devcontainer:28719441697:0.4.0-rc2`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/28719938097
- deploy PR: https://github.com/vig-os/devcontainer-smoke-test/pull/188
- release PR: not created

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `failure`
- cleanup-release: `skipped`
- trigger-prepare-release: `skipped`
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

_Posted on July 4, 2026 at 09:23 PM_

**Diagnosis — the #853 pin fix works end-to-end; the remaining failure is a missing `.typos.toml` in the scaffold.**

rc2 deploy PR ([devcontainer-smoke-test#188](https://github.com/vig-os/devcontainer-smoke-test/pull/188)): `.vig-os` correctly pins `0.4.0-rc2`, the Lint job runs inside the rc2 image, and the **entire prek suite executes** — every hook passes except `typos` (exit 2), which flags false positives in scaffolded content:

- `Nd` — the duration placeholder in `version-check.sh` help text and the synced `.devcontainer/CHANGELOG.md`
- `unexcepted` — the #637 CVE-policy term of art in the synced changelog prose

Both are already excepted in this repo's `.typos.toml` (`[default.extend-words]`), but the scaffold ships the `typos` hook in `.pre-commit-config.yaml` **without shipping `.typos.toml`** — so every consumer lints scaffold-shipped files with zero exceptions and fails out of the box.

Fix: add `.typos.toml` to `scripts/manifest.toml` so the sync-manifest hook ships it with the scaffold, same as `.yamllint`/`.pymarkdown` (single source of truth, kept in sync automatically). The Tests job passed inside the rc2 image, so this is the last consumer-CI blocker visible in the smoke test.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 09:39 PM_

Fixed by #856 (merged): `.typos.toml` now ships with the workspace scaffold via `scripts/manifest.toml`. rc3 will verify end-to-end. Note rc2 already validated everything else downstream: `.vig-os` pin (#853), prek suite inside the image, Tests job green.

