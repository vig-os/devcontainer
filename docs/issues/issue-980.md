---
type: issue
state: open
created: 2026-07-11T12:19:18Z
updated: 2026-07-11T12:19:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/980
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:14.280Z
---

# [Issue 980]: [sync-issues: cache miss triggers full epoch re-sync, exhausting API rate limit](https://github.com/vig-os/devkit/issues/980)

## Problem

The scaffolded `sync-issues.yml` keys its incremental-state cache by `${{ github.repository }}` and passes `updated-since: ''` to `vig-os/sync-issues-action` when no state is restored. On any **cache miss** the action then re-syncs the **entire** issue/PR history from epoch.

For a repo with a large archive (devkit: 359 issues + 361 PRs = **720 items**, several API calls each), that full sync exceeds the app installation's **5,000 req/hr** GitHub API rate limit mid-run and fails **before saving state** — so every subsequent run repeats the full sync and fails again (never self-heals).

**Triggers a cache miss:**
- A **repository rename** (the cache key changes; old cache orphaned) — hit during `vig-os/devcontainer` → `vig-os/devkit` (#781).
- The routine **7-day cache eviction** for any repo idle that long.

Observed: `API rate limit exceeded for installation ID …` after syncing a few hundred items; `no cache is being saved`.

## Fix (in the scaffolded workflow)

On a cache miss, pass a **bounded look-back** `updated-since` instead of epoch, so the sync stays small and completes under the rate limit, then saves state and self-heals to incremental. `force-update` still forces a full rebuild. Lands in the scaffold template + this repo's root copy so all consumers get it.

Deeper defense-in-depth (rate-limit-aware checkpointing) belongs in `vig-os/sync-issues-action` — separate, lower priority.

Refs: #781
