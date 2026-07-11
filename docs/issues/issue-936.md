---
type: issue
state: closed
created: 2026-07-08T13:49:58Z
updated: 2026-07-08T14:14:37Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/936
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:21.413Z
---

# [Issue 936]: [Autochangelog: Renovate PR table not parsed (Unicode → arrow), entries silently skipped](https://github.com/vig-os/devkit/issues/936)

## Problem

`vig_utils.renovate_changelog_pr._parse_change_cell` only matches the ASCII arrow `->` (regex at renovate_changelog_pr.py:23,27), but Renovate PR bodies use the Unicode arrow `→` (U+2192), e.g. `` `v4.2.0` → `v4.4.0` ``. So `_parse_table_updates` returns `[]` for every real Renovate PR. A changelog entry only appears when the *title* fallback matches (digest bumps, single `update X to Y`); grouped PRs (#866) and pins (#861) silently get no entry.

The existing tests never caught this because their fixtures use ASCII `->` (14×) with 0 Unicode arrows.

## Repro
```python
from vig_utils.renovate_changelog_pr import _parse_table_updates
row = '| [docker/login-action](x) | action | minor | `v4.2.0` → `v4.4.0` |'
_parse_table_updates(row)  # → []  (should parse docker/login-action v4.2.0→v4.4.0)
```

## Fix
- Widen the change-cell regex to accept both `→` and `->`.
- Add tests using the real Unicode arrow (quoted + unquoted/digest cells).

Discovered while verifying autochangelog behaviour on recreated #862/#866.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 02:14 PM_

Resolved by #937 (merged to `dev`, commit b87a7816). `renovate-changelog-pr` now parses change cells with the Unicode arrow `→` (and ASCII `->`), so grouped Renovate PRs get a changelog entry. Verified end-to-end against the real #866 body (all three updates parsed) and with the full vig-utils suite.

