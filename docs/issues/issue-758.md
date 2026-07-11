---
type: issue
state: closed
created: 2026-06-30T08:34:04Z
updated: 2026-06-30T11:55:25Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/758
comments: 2
labels: docs, priority:medium, effort:small, area:docs
assignees: c-vigo
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:52.184Z
---

# [Issue 758]: [[DOCS] M5 — Resync security-gate docs to blocking](https://github.com/vig-os/devkit/issues/758)

## Description

PR #670 review (M5). Docs and a workflow summary still describe the security
gate as non-blocking / in a discovery phase; it is now **blocking** (#639).

## Documentation Type

Fix incorrect or outdated content

## Target Files

- `docs/NIX.md:210-214` — drop "discovery phase / non-blocking / `continue-on-error`" wording and the stale `builder: debian|nix` selector reference (selector no longer exists); state the gate is **blocking**.
- `docs/CONTAINER_SECURITY.md:58-59` — flip "non-blocking (`continue-on-error`)" to blocking. (Its Debian-decommission line at `:8` is current — leave it.)
- `.github/workflows/security-scan.yml:137` — stale "non-blocking during discovery" summary string leftover; align with the now-blocking gate.

## Acceptance Criteria

- [ ] `docs/NIX.md` states the gate is blocking; no `builder: debian|nix` selector reference remains
- [ ] `docs/CONTAINER_SECURITY.md` describes the gate as blocking
- [ ] `security-scan.yml` summary string aligned with the blocking gate
- [ ] `grep -n "non-blocking\|discovery\|builder:" docs/` returns nothing stale

## Related Code Changes

Follows the blocking gate work under #639.

## Related Issues

Parent: #625. From PR #670 review (Comment 2, M5).

**Changelog Category:** Changed

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 11:54 AM_

Landed on the migration branch via #770.

---

# [Comment #2]() by [c-vigo]()

_Posted on June 30, 2026 at 11:55 AM_

Landed on the migration branch via #770.

