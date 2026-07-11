---
type: issue
state: closed
created: 2026-06-23T06:53:57Z
updated: 2026-07-01T11:19:24Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/628
comments: 1
labels: area:image, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:15.750Z
---

# [Issue 628]: [C3 — Remove `cursor-agent` install from the image](https://github.com/vig-os/devkit/issues/628)

Tracking: #625



## Context

`Containerfile` (~lines 166–182) curl-installs `cursor-agent` unpinned from an external CDN,
and `.trivyignore` carries `CVE-2026-55388` (piscina) on its behalf. `cursor-agent` is the
only tool **not** available in nixpkgs, so removing it leaves an all-nixpkgs toolchain and
materially simplifies the Nix migration (precedes #634).

## Scope

**In:**
- Delete the `cursor-agent` install block and its `/root/.local/bin` PATH note.
- Drop the piscina CVE (`CVE-2026-55388`) from `.trivyignore`.

**Out:**
- The broader Nix rebuild of the image (#634).

## Tasks

- [ ] Remove the install block from `Containerfile` and `build/Containerfile`
- [ ] Prune the related PATH note
- [ ] Remove the `CVE-2026-55388` entry from `.trivyignore`
- [ ] Changelog entry

## Acceptance criteria

- Image builds without `cursor-agent`.
- Trivy run is clean without the previously ignored CVE.

## Dependencies

- **Depends-on:** #627.
- **Blocks:** (precedes) #634.

## Files

- `Containerfile`
- `build/Containerfile`
- `.trivyignore`

## Test notes

- #630 removes the corresponding `test_cursor_agent_installed` image test.

## Related issues

- **#545** (bake agent-CLI toolkit + Claude Code into image) — as `cursor-agent` is removed,
  `claude` becomes the baked agent CLI. The install *mechanism* in #545 (apt/curl) is replaced
  by the Nix `devTools` path (#631/#634); its `IS_SANDBOX=1` + `cc`/`cld` aliases carry into
  #634. Coordinate so cursor-agent removal and claude bake-in are consistent.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30) (commit 065bb665). The `cursor-agent` install block is gone; the toolchain is all-nixpkgs with `claude-code` in `devTools`. Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

