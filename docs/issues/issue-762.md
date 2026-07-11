---
type: issue
state: closed
created: 2026-06-30T08:34:14Z
updated: 2026-06-30T12:07:20Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/762
comments: 1
labels: chore, priority:medium, area:ci, effort:medium, security
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:50.679Z
---

# [Issue 762]: [[CHORE] Per-CVE rationale + shorter expiry for .vulnixignore Class-2 entries](https://github.com/vig-os/devkit/issues/762)

## Chore Type

Configuration change (security)

## Description

PR #670 review (larger nit). `.vulnixignore` covers 22 HIGH/CRITICAL CVEs
(including CRITICAL openssl) under a single blanket "Class-2" rationale with a
long expiry. Replace the blanket rationale with per-CVE notes and shorter
expiries so each suppression is justified and revisited.

## Acceptance Criteria

- [ ] Each of the 22 HIGH/CRITICAL entries has a per-CVE rationale note
- [ ] Expiries shortened from the blanket value to per-CVE appropriate windows
- [ ] CRITICAL openssl entry explicitly justified or removed

## Implementation Notes

Security-sensitive: blanket suppression of CRITICAL CVEs hides real exposure.

## Files

- `.vulnixignore`

## Related Issues

Parent: #625. From PR #670 review (Comment 2, larger nits).

**Priority:** Medium · **Changelog Category:** Security

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 12:07 PM_

Landed on the migration branch via #771.

