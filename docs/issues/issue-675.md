---
type: issue
state: open
created: 2026-06-24T10:59:42Z
updated: 2026-06-24T10:59:42Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/675
comments: 0
labels: chore, priority:low, area:image, effort:small, area:testing
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:58.497Z
---

# [Issue 675]: [[CHORE] Smoke-test that nix/direnv work inside the built Nix image](https://github.com/vig-os/devcontainer/issues/675)

### Chore Type

CI / Build change

### Description

The portable testinfra suite verifies that tools are *present* in the image, but
nothing asserts that the baked-in Nix toolchain actually *functions* inside the
built container. The Nix image ships `nix`, `direnv`, and `nix-direnv` live in
the closure (#634); a regression that breaks in-container `nix`/`direnv` would
pass today's presence-only tests.

Add a runtime smoke test in the Nix image lane that exercises the toolchain
inside the image.

### Acceptance Criteria

- [ ] A step/test in `.github/workflows/nix-image.yml` (and/or `tests/`) runs,
      inside the built image: `nix --version`, `direnv version`, and a
      `nix develop -c true` (or `direnv allow` + `direnv exec . true`), asserting
      each succeeds
- [ ] The test runs against the real Nix-built image and fails if in-container
      Nix/direnv is broken
- [ ] TDD compliance (see .claude/skills/tdd/SKILL.md)

### Implementation Notes

Keep workflow edits confined to `nix-image.yml` — the sibling flake quality-gates
issue edits `ci.yml` — so the two follow-up PRs do not conflict on a shared
workflow file.

### Related Issues

Part of #625.

### Priority

Low

### Changelog Category

Added

