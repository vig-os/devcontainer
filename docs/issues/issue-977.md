---
type: issue
state: closed
created: 2026-07-10T15:42:10Z
updated: 2026-07-10T16:08:26Z
author: vig-os-release-app[bot]
author_url: https://github.com/vig-os-release-app[bot]
url: https://github.com/vig-os/devkit/issues/977
comments: 2
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:14.698Z
---

# [Issue 977]: [Smoke-test dispatch failed for 1.0.0](https://github.com/vig-os/devkit/issues/977)

Smoke-test dispatch failed while orchestrating downstream release validation.

## Dispatch metadata
- tag: `1.0.0`
- release_kind: `final`
- source_repo: `vig-os/devcontainer`
- source_workflow: `Release`
- source_run_id: `29102698645`
- source_run_url: https://github.com/vig-os/devcontainer/actions/runs/29102698645
- source_sha: `3aeb01ae074a1125ee5b49426c2a7f1fa3b81421`
- correlation_id: `vig-os/devcontainer:29102698645:1.0.0`

## Workflow context
- downstream workflow run: https://github.com/vig-os/devkit-smoke-test/actions/runs/29104036245
- deploy PR: https://github.com/vig-os/devkit-smoke-test/pull/229
- release PR: https://github.com/vig-os/devkit-smoke-test/pull/230

## Job results
- validate: `success`
- deploy: `success`
- wait-deploy-merge: `success`
- cleanup-release: `success`
- trigger-prepare-release: `success`
- ready-release-pr: `success`
- trigger-release: `failure`
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

_Posted on July 10, 2026 at 03:45 PM_

**Triage (automated):** Not a defect in the 1.0.0 artifacts. The **upstream** 1.0.0 is finalized — `ghcr.io/vig-os/devcontainer:1.0.0` published, draft GitHub Release `1.0.0` created. The failure is downstream on `devkit-smoke-test`: its `release-core` finalize step **"Wait for sync-issues completion" timed out (~2m)** while the repo's `sync-issues` workflow was still running (first final-release path since the repo was renamed; the run ran long). The downstream release rolled back cleanly — no partial `1.0.0` release.

`promote-release` is **held** (its gate requires a published-final downstream 1.0.0 release). Attempting **one** bounded retry of the downstream final cycle once `sync-issues` completes; if the timeout recurs, this is a real config issue (wait-timeout vs. sync-issues duration on the renamed repo) and it will be left for a human.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 10, 2026 at 04:08 PM_

**Resolved.** Confirmed transient: the failed run's `sync-issues` spiked to **441s** vs its normal **60–80s** (last 5 runs: 60/74/80/65/65s), overrunning the ~2min wait. A single re-dispatch of the downstream final cycle passed cleanly (`sync-issues` back to normal), the downstream published its final 1.0.0 Release, and `promote-release 1.0.0` then completed: `:latest` → 1.0.0, GitHub Release undrafted, PR #975 merged to `main`. No config change needed. Closing.

