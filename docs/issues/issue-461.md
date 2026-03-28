---
type: issue
state: open
created: 2026-03-27T08:53:12Z
updated: 2026-03-27T08:53:12Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/461
comments: 0
labels: chore, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:13.694Z
---

# [Issue 461]: [[CHORE] Add nightly CI and upgrade scheduled security scan](https://github.com/vig-os/devcontainer/issues/461)

### Chore Type

CI / Build change

### Description

Currently, CI only runs on PRs and manual dispatch, and the scheduled security scan runs weekly against `dev` only. This leaves two gaps:

1. **Upstream breakage goes undetected between PRs** — new apt package versions, base image updates, or Python dependency changes can silently break the build.
2. **Newly published CVEs against the production image are only caught weekly**, and the released image on `main` is never scanned on a schedule.

#### Proposed changes

1. **Nightly CI on `dev`**: Add a `schedule` trigger to [`ci.yml`](.github/workflows/ci.yml). On schedule events, check out `dev` explicitly. This runs the full suite nightly: build, image tests, integration tests, project checks, Python security (Bandit + Safety), and Trivy scan. The `dependency-review` job already auto-skips on non-PR events.

2. **Upgrade [`security-scan.yml`](.github/workflows/security-scan.yml) from weekly to nightly**: Change the cron from Monday 06:00 to nightly. Add a new job that pulls the **latest published image from GHCR** (`ghcr.io/vig-os/devcontainer:latest`) and runs Trivy + SBOM against it — covering `main` without rebuilding.

### Acceptance Criteria

- [ ] `ci.yml` runs nightly against `dev` (build + all test suites + Python security + Trivy)
- [ ] `security-scan.yml` runs nightly instead of weekly
- [ ] `security-scan.yml` scans both `dev` (freshly built) and `main` (latest from GHCR, no rebuild)
- [ ] Existing PR-triggered and manual-dispatch behavior is unchanged
- [ ] SARIF uploads use distinct categories to avoid overwriting each other

### Implementation Notes

- `ci.yml`: add `schedule` cron trigger; in the checkout step, use `ref: dev` when `github.event_name == 'schedule'`
- `security-scan.yml`: add a `scan-latest` job that does `docker pull ghcr.io/vig-os/devcontainer:latest`, saves to tar, then runs the same Trivy steps with a separate SARIF category (`container-image-latest`)
- Suggested cron times: CI at ~04:00 UTC, security-scan at ~05:00 UTC (stagger to reduce runner contention with existing CodeQL at 02:15)

### Related Issues

None

### Priority

Medium

### Changelog Category

No changelog needed

