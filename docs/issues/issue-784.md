---
type: issue
state: closed
created: 2026-06-30T13:43:24Z
updated: 2026-06-30T13:59:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/784
comments: 1
labels: bug, priority:high, area:ci, effort:small, area:testing
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:33:46.967Z
---

# [Issue 784]: [[BUG] CodeQL: incomplete-url-substring-sanitization in test_image.py nix.conf assertions](https://github.com/vig-os/devkit/issues/784)

**Source:** CodeQL (PR #670 merge ref) flagged two high-severity `py/incomplete-url-substring-sanitization` alerts at `tests/test_image.py:1118` and `:1121`, introduced by the #773 nix.conf assertions.

## Problem
`test_nix_conf_bakes_explicit_substituters` asserts `"https://cache.nixos.org" in sub_line` (substring-in-string). CodeQL heuristically treats a URL checked as a substring of another string as bypassable host validation → high-severity alert. Harmless in a test assertion, but a real new alert on the PR.

## Fix
Split the `substituters` (and, for consistency, `trusted-public-keys`) line into whitespace tokens and assert **exact membership** in the token list instead of substring-in-line. Clears the CodeQL alert and is a stricter assertion (the URL/key must be a whole token, not an accidental substring).

Refs #625, #773.

---

# [Comment #1]() by [c-vigo]()

_Posted on June 30, 2026 at 01:59 PM_

Landed on the migration branch via #785.

