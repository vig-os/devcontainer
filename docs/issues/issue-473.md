---
type: issue
state: open
created: 2026-03-27T16:06:03Z
updated: 2026-03-27T16:06:03Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/473
comments: 0
labels: chore, area:ci
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:12.111Z
---

# [Issue 473]: [[CHORE] Authenticate Docker Hub before Buildx in CI to avoid pull rate limits](https://github.com/vig-os/devcontainer/issues/473)

### Chore Type
CI / Build change

### Description
CI **Build Container Image** fails when `docker/setup-buildx-action` pulls `moby/buildkit:buildx-stable-1` from Docker Hub on shared GitHub-hosted runners. Anonymous pulls share an IP; when limits are hit, Hub returns auth-style errors, retries count as failed logins, and jobs fail with `toomanyrequests: too many failed login attempts for username or IP address` (and sometimes `unauthorized: incorrect username or password` first). This is environmental, not application code, but it blocks merges until re-runs land on a cleaner IP.

### Acceptance Criteria
- [ ] CI build path that uses `.github/actions/build-image` can pull Buildx/BuildKit reliably (e.g. optional Docker Hub login before `setup-buildx-action`, or another documented approach that avoids shared anonymous Hub limits).
- [ ] Document required repo/org secrets (if any) and that they are optional vs required for forks.
- [ ] No regression: image still builds and downstream jobs unchanged when Hub is healthy.

### Implementation Notes
- Target: `.github/actions/build-image/action.yml` — add `docker/login-action` for `registry: docker.io` **before** `docker/setup-buildx-action` when secrets are present (e.g. `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`), using `secrets` from the calling workflow; keep behavior unchanged when secrets are absent if feasible, or document that org repos must configure secrets.
- Reference: failed runs pulling `https://registry-1.docker.io/v2/moby/buildkit/manifests/buildx-stable-1`.

### Related Issues
(none identified; complements backlog CI hardening)

### Priority
Medium

### Changelog Category
No changelog needed

### Additional Context
Example failure: [CI run 23655237806](https://github.com/vig-os/devcontainer/actions/runs/23655237806) (PR #472) — `Head "https://registry-1.docker.io/v2/moby/buildkit/manifests/buildx-stable-1": toomanyrequests: too many failed login attempts for username or IP address`. Immediate mitigation: re-run job for a different runner IP.
