---
type: issue
state: closed
created: 2026-06-30T08:33:59Z
updated: 2026-06-30T11:50:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/756
comments: 1
labels: chore, priority:low, area:ci, effort:small
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:52.969Z
---

# [Issue 756]: [[CHORE] M3 — Scope the 'setup-env provisions every job' claim](https://github.com/vig-os/devkit/issues/756)

## Chore Type

CI / Build change

## Description

PR #670 review (M3). The PR-body claim that `setup-env` "provisions every job"
is false. `provision-via-flake: 'true'` is passed only in composite actions
(`build-image`/`test-image`/`test-integration`/`test-project`). The jobs
`python-security` (`ci.yml:225`), `security-scan` (`ci.yml:287`),
`dependency-review` (`ci.yml:351`), and release `validate`/`publish`
(`release.yml:87`, `:835`) call `setup-env` without it.

## Acceptance Criteria

- [ ] Either make provisioning consistent **or** scope the claim
- [ ] Recommended: scope the PR-body sentence to "every job that needs flake tooling"
- [ ] Add `provision-via-flake: 'true'` only where a job actually consumes flake-provided tools (minimal diff, no false universality)

## Implementation Notes

Recommended minimal-diff path: correct the PR #670 body wording and add the flag
only where genuinely needed.

## Files

- PR #670 body
- `.github/workflows/ci.yml` / `release.yml` (only where genuinely needed)

## Related Issues

Parent: #625. From PR #670 review (Comment 2, M3).

**Priority:** Low · **Changelog Category:** No changelog needed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:50 AM_

Audit verdict: **no code change needed** — every CI/release job that actually consumes flake tooling (image build/test jobs + the `vulnix-gate`) already provisions via flake; jobs that only run `uv`-managed project console scripts (`check-expirations`, `prepare-changelog`, etc.) or GitHub-native actions correctly use the lighter ad-hoc setup. The only inaccuracy was the PR #670 body claim, now scoped to "every job that actually consumes it."

