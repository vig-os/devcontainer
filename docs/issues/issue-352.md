---
type: issue
state: open
created: 2026-03-17T20:28:29Z
updated: 2026-03-17T20:28:56Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/352
comments: 0
labels: bug, priority:high, area:ci, area:workflow, effort:small, semver:patch
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-18T04:29:20.825Z
---

# [Issue 352]: [[BUG] repository_dispatch smoke-test deploy fails with workspace Permission denied after installer](https://github.com/vig-os/devcontainer/issues/352)

### Description
`Repository Dispatch Listener` fails in the deploy job after running installer from dispatch tag. The installer reports successful workspace initialization, but subsequent host-side file operations fail with `Permission denied`.

### Steps to Reproduce
1. Trigger `repository_dispatch` event `smoke-test-trigger` in `vig-os/devcontainer-smoke-test` with tag `0.3.1-rc2`.
2. Observe job `Deploy tag and open PR to dev`, step `Run installer from dispatch tag`.
3. Workflow runs:
   - `curl -sSf "https://raw.githubusercontent.com/vig-os/devcontainer/${TAG}/install.sh" | bash -s -- --version "${TAG}" --smoke-test --force --docker .`
   - `cp ".devcontainer/CHANGELOG.md" "CHANGELOG.md"`
4. Step fails with `Permission denied`.

### Expected Behavior
After installer execution, workspace files remain writable by the GitHub Actions runner so metadata copy, commit, and PR steps can continue.

### Actual Behavior
Post-install, workspace writes fail:
- `mkdir: cannot create directory .../.devcontainer/.conf: Permission denied`
- `cp: cannot create regular file 'CHANGELOG.md': Permission denied`
Deploy job exits with code 1, downstream release/publish is skipped.

### Environment
- **OS**: GitHub-hosted Ubuntu 22.04 runner
- **Container Runtime**: Docker (`--docker`)
- **Image Version/Tag**: `ghcr.io/vig-os/devcontainer:0.3.1-rc2`
- **Architecture**: AMD64 (GitHub-hosted runner)

### Additional Context
- Failing run: https://github.com/vig-os/devcontainer-smoke-test/actions/runs/23206472689/job/67443185534#step:6:361
- Suspected root cause: containerized initialization writes bind-mounted workspace with ownership/permissions not writable by runner user.
- Related to #330

#### Acceptance Criteria
- [ ] Dispatch flow for RC tag completes deploy job without permission errors.
- [ ] `Run installer from dispatch tag` can write `.devcontainer/.conf` and copy `.devcontainer/CHANGELOG.md` to root `CHANGELOG.md`.
- [ ] Deploy branch and deploy PR creation steps run successfully.
- [ ] TDD compliance (see `.cursor/rules/tdd.mdc`)

### Possible Solution
Prefer installer-side ownership normalization for bind-mounted files (host UID/GID), or workflow-side ownership fix immediately after installer (e.g. `chown -R "$(id -u):$(id -g)" .`) before host writes.

### Changelog Category
Fixed
