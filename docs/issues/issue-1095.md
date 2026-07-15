---
type: issue
state: closed
created: 2026-07-15T07:18:02Z
updated: 2026-07-15T07:33:28Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1095
comments: 1
labels: bug, area:ci, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-15T11:04:53.298Z
---

# [Issue 1095]: [[BUG] Candidate release fails draft/approval gate — release-core.yml template missing #902 guard](https://github.com/vig-os/devkit/issues/1095)

## Description

The scaffolded release template `assets/workspace/.github/workflows/release-core.yml` applies the **draft + approval gate to every release kind**, including release **candidates**. Candidates are supposed to gate on **CI only** (per #902), so a candidate dispatch fails against a still-draft PR with `ERROR: PR #<n> is still in draft`.

This is a **template drift** bug: #902's fix landed in the devkit's *own* `.github/workflows/release.yml` (`release.yml:354-380`, guarding the draft/approval checks behind `RELEASE_KIND = final`) but was never mirrored into the scaffolded `release-core.yml` that consumer repos receive. The devkit dogfoods the fixed copy, so the regression went unnoticed until a downstream repo ran a candidate.

## Steps to Reproduce

1. Deploy the devkit release workflows to a consumer repo (e.g. `vig-os/commit-action`).
2. Open the release PR from `release/X.Y.Z` → `main` and leave it as a **draft** (the intended state during candidate iteration).
3. Dispatch **Release Core** with `release_kind=candidate`.
4. The `validate` job fails at **"Find and verify PR"**.

Observed: https://github.com/vig-os/commit-action/actions/runs/29396249943/job/87290340861

## Expected Behavior

A `release_kind=candidate` dispatch passes validation against a draft, not-yet-approved PR, gating on CI only. The draft + approval gate is enforced for `release_kind=final` only — consistent with `RELEASE_CYCLE.md` (candidate gate vs. final gate) and the devkit's own `release.yml`.

## Actual Behavior

```
ERROR: PR #78 is still in draft
##[error]Process completed with exit code 1.
```

The candidate run is rejected because `release-core.yml`'s "Find and verify PR" step (lines 307-327) checks `isDraft` and `reviewDecision` with **no `release_kind` guard**.

## Environment

- **Repo**: `vig-os/commit-action` (consumer of the scaffolded devkit release workflows)
- **Workflow**: `release-core.yml` (Release Core / Validate Release Core)
- **Release kind**: `candidate`
- **Devkit template source**: `assets/workspace/.github/workflows/release-core.yml`

## Additional Context

Documented intent this violates:
- `RELEASE_CYCLE.md:135` — approvals are "the final-release gate, not the candidate gate"
- `RELEASE_CYCLE.md:274` — "Candidate dispatch gates on CI only — the PR may stay a draft and need not be approved yet (#902)"
- `RELEASE_CYCLE.md:347` — draft/approval prerequisites are "enforced for the final release only"

## Possible Solution

Port the guard from `release.yml:347-380` into `release-core.yml`'s "Find and verify PR" step: wrap the draft (307-310) and approval (311-327) checks in `if [ "$RELEASE_KIND" = "final" ]; then ... else <defer message> fi`, keep the existing CI-failure check unconditional, and add `RELEASE_KIND: ${{ steps.vars.outputs.release_kind }}` to the step env. After merge, redeploy the template to consumer repos (commit-action) and re-run the 0.3.0 candidate.

## Changelog Category

Fixed

---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 07:33 AM_

Fixed by #1097 (merged to `dev` as `7306f231`). The scaffolded `release-core.yml` draft + approval gate is now guarded behind `release_kind=final`; candidates gate on CI only. Auto-close did not fire because the PR merged into `dev`, not the default branch. Ships to consumers on the next devkit release; `vig-os/commit-action` needs a template redeploy before re-running its 0.3.0 candidate.

