---
type: issue
state: open
created: 2026-06-24T10:59:38Z
updated: 2026-06-24T10:59:38Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/673
comments: 0
labels: docs, priority:high, area:docs
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:59.155Z
---

# [Issue 673]: [[DOCS] README advertises the decommissioned Debian python:3.12-slim base image](https://github.com/vig-os/devcontainer/issues/673)

### Description

The shipped devcontainer image is now built entirely by Nix
(`dockerTools.buildLayeredImage` in `flake.nix`, #634/#642) — there is no Debian
base image anymore. The flagship docs, however, still advertise a Debian base:

- `README.md:198` — "**Base Image**: `python:3.12-slim-trixie`"
- `README.md:209` — "**python:3.12-slim-trixie** – Minimal Python base image (Debian Trixie) …"
- `README.md:224` — "pip, setuptools, wheel … (included with base image)"

The editable source is `docs/templates/README.md.j2` (≈line 143); `README.md` is
generated from it via `docs/generate.py` (`just docs`). This is a user-facing
contradiction in the project's primary document and must describe the Nix-built
image instead.

### Documentation Type

Fix incorrect or outdated content

### Target Files

- `docs/templates/README.md.j2` (source template — edit here)
- `README.md` (regenerated via `just docs`, do not edit directly)

### Related Code Changes

Follows the Nix image build (#634) and Debian decommission (#642).

### Acceptance Criteria

- [ ] Template no longer claims a Debian `python:3.12-slim-trixie` base image; it
      describes the Nix-built (`buildLayeredImage`) image with the pinned
      `nixpkgs`/CPython instead
- [ ] `just docs` regenerates `README.md` with no residual Debian-base wording
      (`grep -ri "slim-trixie\|Debian.*base" README.md docs/templates/README.md.j2` is clean)
- [ ] `just docs` is diff-clean (generated file matches template)

### Changelog Category

Changed

### Additional Context

Part of the Nix migration epic #625.

