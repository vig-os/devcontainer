---
type: issue
state: closed
created: 2026-06-30T08:33:57Z
updated: 2026-06-30T09:40:05Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/755
comments: 1
labels: bug, priority:high, area:ci, effort:small, security
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:53.354Z
---

# [Issue 755]: [[BUG] M2 — vulnix_gate fail-loud on unscored CVEs and scanner crashes](https://github.com/vig-os/devkit/issues/755)

## Description

PR #670 review (M2). `vulnix_gate.py` silently skips unscored CVEs and the scan
capture swallows scanner crashes, so a crash or an unscored CRITICAL looks clean.

`packages/vig-utils/src/vig_utils/vulnix_gate.py:68-70` —
`if score is None or score < threshold: continue` (unscored CVE = non-blocking).
`security-scan.yml:82-83` runs vulnix with `|| true` (scanner crash → `[]`,
indistinguishable from a clean scan).

## Steps to Reproduce

1. Feed the gate a CVE with `score is None` → it is skipped, not blocked.
2. Make the vulnix scan crash → `|| true` yields `[]` → job passes as "clean".

## Expected Behavior

`score is None` is treated as fail-loud (block, or surfaced separately); a
scanner crash fails the job.

## Actual Behavior

Unscored CVEs silently skipped; scanner crash indistinguishable from clean.

## Fix

Treat `score is None` as fail-loud (block, or surface separately), not silently
skipped; drop `|| true` on the scan capture so a crash fails the job. Update
`test_vulnix_gate` accordingly.

## Acceptance Criteria

- [ ] `score is None` blocks (or is surfaced as a distinct non-clean state), not silently skipped
- [ ] `security-scan.yml` scan capture no longer masks a scanner crash with `|| true`
- [ ] `test_vulnix_gate` covers the `score is None` case and asserts it blocks
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

## Files

- `packages/vig-utils/src/vig_utils/vulnix_gate.py`
- `.github/workflows/security-scan.yml`
- vulnix-gate tests

## Related Issues

Parent: #625. From PR #670 review (Comment 2, M2).

**Changelog Category:** Security

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 09:40 AM_

Landed on the migration branch via #765 (merge `7087347`).

