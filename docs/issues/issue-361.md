---
type: issue
state: closed
created: 2026-03-19T06:40:20Z
updated: 2026-03-19T07:02:03Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/361
comments: 0
labels: chore, priority:high, area:ci, area:image, security
assignees: c-vigo
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-20T04:20:27.726Z
---

# [Issue 361]: [[CHORE] Resolve Trivy-blocking CVE-2026-33186 in CI image scan](https://github.com/vig-os/devcontainer/issues/361)

### Chore Type
Dependency update

### Description
PR #360 fails CI in `Security Scan` because Trivy reports a fixed CRITICAL vulnerability in the container image scan gate (`exit-code: 1`, `severity: HIGH,CRITICAL`, `ignore-unfixed: true`).

Blocking finding:
- Library: `google.golang.org/grpc`
- CVE: `CVE-2026-33186`
- Severity: `CRITICAL`
- Installed: `v1.79.2`
- Fixed: `1.79.3`

Run/job reference:
- [CI run 23282697478](https://github.com/vig-os/devcontainer/actions/runs/23282697478)
- [Security Scan job 67699627300](https://github.com/vig-os/devcontainer/actions/runs/23282697478/job/67699627300?pr=360)

### Acceptance Criteria
- [ ] Identify which packaged binary/dependency in the image pulls `google.golang.org/grpc v1.79.2`
- [ ] Update that dependency path so Trivy no longer reports `CVE-2026-33186` as fixed+critical
- [ ] Keep the blocking policy in CI (`HIGH,CRITICAL` with `exit-code: 1`)
- [ ] Re-run CI and confirm `Security Scan` passes on the affected branch/PR
- [ ] If immediate upgrade is impossible, add a time-bounded temporary exception with explicit risk rationale and tracking

### Implementation Notes
- Investigate image contents and dependency provenance from `/tmp/image.tar` scan target.
- Prioritize remediation over ignore rules.
- Node 20 deprecation warning in the same job is non-blocking and should be tracked separately (already covered by open issue #349).

### Related Issues
Related to #358, PR #360  
Potentially related: #349 (Node.js 20 action deprecation warning)

### Priority
High

### Changelog Category
Security

### Additional Context
`Test Summary` fails as a consequence of `Security Scan` failing.
