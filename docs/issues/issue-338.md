---
type: issue
state: closed
created: 2026-03-17T12:49:50Z
updated: 2026-03-17T13:07:06Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/338
comments: 0
labels: chore, priority:medium, area:ci, effort:small
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:23.097Z
---

# [Issue 338]: [[CHORE] Align actions/create-github-app-token pin in smoke-test template with v3.0.0](https://github.com/vig-os/devcontainer/issues/338)

### Chore Type

CI / Build change

### Description

Dependabot PR #316 bumped `actions/create-github-app-token` from 2.2.1 to 3.0.0 (`f8d387b68d61c58ab83c6c016672934102569859`) across `.github/workflows/` and `assets/workspace/.github/workflows/`, but missed the smoke-test template at `assets/smoke-test/.github/workflows/repository-dispatch.yml`, which still pins v2.2.1 (`29824e69f54612133e76f7eaac726eef6c875baf`).

Additionally, the `# v2` inline comment on the v3.0.0 SHA is incorrect in every file that was bumped — it should read `# v3`.

### Acceptance Criteria

- [ ] `assets/smoke-test/.github/workflows/repository-dispatch.yml` uses `actions/create-github-app-token@f8d387b68d61c58ab83c6c016672934102569859`
- [ ] All `# v2` comments on the v3.0.0 SHA are corrected to `# v3`
- [ ] No other action pins are affected

### Implementation Notes

Files to update:
- `assets/smoke-test/.github/workflows/repository-dispatch.yml` (2 occurrences — pin + comment)
- `.github/workflows/release.yml` (5 occurrences — comment only)
- `assets/workspace/.github/workflows/sync-issues.yml` (1 occurrence — comment only)
- `assets/workspace/.github/workflows/sync-main-to-dev.yml` (2 occurrences — comment only)

### Related Issues

Follow-up from Dependabot PR #316. Pre-release cleanup for 0.3.1.

### Priority

Medium

### Changelog Category

Changed
