---
type: issue
state: closed
created: 2026-07-06T10:57:31Z
updated: 2026-07-06T13:01:50Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/870
comments: 1
labels: bug
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:33.326Z
---

# [Issue 870]: [Self-host NVD feed mirror so vulnix CVE scans survive nvd.nist.gov outages](https://github.com/vig-os/devkit/issues/870)

## Problem

The vulnix CVE gate (nightly \`security-scan.yml\` + release \`release.yml\`) fails **slowly** on NVD feed downloads whenever \`nvd.nist.gov\` is throttled/degraded (upstream nix-community/vulnix#171, still open). Verified 2026-07-06: a cold run failed all 3 retry attempts over **53 min** (\`ReadTimeoutError\` / \`IncompleteRead\`). A warm-cache run on \`dev\` succeeded the same day (only the small \`modified\` feed needed), proving the cold **year-feed crawl** is the failure surface.

Compounding factors:
- The combined \`actions/cache\` **skips save on job failure**, so partial NVD downloads are discarded and re-dispatches do not converge.
- The cache is **branch-scoped**: \`release/*\` and \`main\` cannot read \`dev\`'s warm cache.

## Proposed solution

Self-host the NVD 2.0 data feeds so scans never depend on \`nvd.nist.gov\` at runtime.

1. **New \`nvd-mirror-refresh.yml\`** — the only NVD-facing job. Scheduled + \`workflow_dispatch\`. Downloads the 7 files vulnix needs (\`nvdcve-2.0-{6 years}.json.gz\` + \`nvdcve-2.0-modified.json.gz\`) from NVD with resumable retry (\`curl -C - --retry\`), validates (\`gzip -t\`), and — only if all succeed — publishes them as assets on a dedicated \`nvd-mirror\` release (\`gh release upload --clobber\`). Non-blocking; needs to succeed only occasionally.
2. **Point scans at the mirror** — add \`--mirror https://github.com/vig-os/devcontainer/releases/download/nvd-mirror/\` to the \`nix run .#vulnix\` invocations in \`security-scan.yml\` and \`release.yml\` (\`vulnix-gate\`). Scans then fetch from GitHub's CDN, not NVD.
3. **Concentrate resilience in the refresh job** — the retry/partial-progress logic belongs in the mirror refresh; scan jobs simplify to the mirror flag (+ optional light retry).

## Why (verified facts)

- Pinned vulnix uses \`https://nvd.nist.gov/feeds/json/cve/2.0/\` (2.0 feeds; the repo's \"1.1\" comment is stale). No firm feed-retirement date (extended \"until further notice\"); vulnix has no API-migration plan and chose NIST-direct as of Oct 2025.
- The mirror is an abstraction layer: if NVD ever changes/retires the feeds, only the refresh job's source changes — vulnix keeps consuming identical files.
- vulnix stays because it is the only scanner that reads the Nix store closure (Trivy is dark there).

## Acceptance criteria

- [ ] \`nvd-mirror-refresh.yml\` publishes 7 valid gzip feed assets to the \`nvd-mirror\` release.
- [ ] \`security-scan.yml\` and \`release.yml\` vulnix runs use \`--mirror\` and do not contact \`nvd.nist.gov\` (grep the log).
- [ ] A scan completes fast even while \`nvd.nist.gov\` is degraded.
- [ ] Docs updated (\`docs/CONTAINER_SECURITY.md\` / \`docs/NIX.md\`); CHANGELOG \`## Unreleased\`.
---

# [Comment #1]() by [c-vigo]()

_Posted on July 6, 2026 at 01:01 PM_

Resolved. ✅

A dedicated public mirror — [`vig-os/nvd-mirror`](https://github.com/vig-os/nvd-mirror) — serves the 7 NVD 2.0 feeds (`nvdcve-2.0-{2021..2026}.json.gz` + `modified`) via GitHub Pages at https://vig-os.github.io/nvd-mirror/, refreshed every 6 h. `security-scan.yml` and the release `vulnix-gate` now fetch via `vulnix --mirror https://vig-os.github.io/nvd-mirror/`, so `nvd.nist.gov` outages can no longer fail a scan or block a release.

- #871 landed the initial approach (release assets); #872 corrected it to the dedicated Pages host after GitHub **immutable releases** blocked release-asset hosting (assets can't be clobbered; tag gets poisoned).
- Verified end-to-end: a mirror-backed scan on the `release/0.4.0` branch passed in **~97 s** ([run 28792515788](https://github.com/vig-os/devcontainer/actions/runs/28792515788)) while cold `nvd.nist.gov` runs today failed after **53–68 min**.

Both merged into `release/0.4.0`; the nightly path is correct for `main` once the cutover lands.

