---
type: issue
state: closed
created: 2026-06-26T08:14:06Z
updated: 2026-07-03T07:46:38Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/718
comments: 1
labels: priority:low, area:workspace
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:59.744Z
---

# [Issue 718]: [perf: bake the build-time placeholder manifest into the Nix image](https://github.com/vig-os/devkit/issues/718)

## Context

Follow-up from #625 / PR #670. `init-workspace.sh` substitutes template placeholders using a build-time manifest (`.placeholder-manifest.txt` at `SCRIPT_DIR`) when present, else falls back to a runtime `find`+`grep` search ("Warning: Manifest not found, searching at runtime (slower)"). The fast baked manifest the comment promises is never generated for the Nix image, so workspace init always takes the slow path.

## Proposed work

- Generate `.placeholder-manifest.txt` during the Nix image build (`flake.nix` `buildLayeredImage`) so `init-workspace.sh` uses the fast path.
- Functional-only optimization; the runtime fallback already produces correct output.

Refs: #625
---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 07:46 AM_

Resolved by #802 (merged to `dev`). The Nix image build now bakes `.placeholder-manifest.txt` into the bootstrap layer (deterministic `grep -rl` + sort), so `init-workspace.sh` takes the fast substitution path instead of the slow runtime find+grep. Guarded by a new `test_placeholder_manifest_baked` image test.

