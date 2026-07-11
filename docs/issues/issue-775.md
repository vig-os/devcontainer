---
type: issue
state: closed
created: 2026-06-30T12:52:04Z
updated: 2026-07-01T11:20:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/775
comments: 1
labels: chore, priority:medium, area:image, effort:large
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:49.581Z
---

# [Issue 775]: [[CHORE] Scope uv2nix/pyproject-nix to dissolve the FHS/manylinux scar tissue](https://github.com/vig-os/devkit/issues/775)

**Source:** PR #670 roadmap, thread A — [roadmap comment](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834503378). **Deferred / sequenced** (large; not for #670).

The FHS/manylinux/loader scar tissue (#683/#697/#698/#703/#728/#735/#736/#740) shares one root cause: uv's generic-ELF wheels vs a no-FHS Nix store. **`uv2nix` / `pyproject-nix`** would dissolve most of it and make `pythonEnv` a real hermetic venv.

Scope this as a spike: evaluate adopting uv2nix/pyproject-nix, what it eliminates vs **relocates**, and the migration cost. Even if not adopted, capture the decision. Refs #670.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:20 AM_

Resolved on `dev` by PR #788 (`docs(rfc): record uv2nix/pyproject-nix evaluation and decision`). The scoping was completed as an ADR with a **defer** verdict (uv2nix/pyproject-nix not adopted now; rationale + revisit triggers recorded). Deliverable landed. Refs #625.

