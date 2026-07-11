---
type: issue
state: closed
created: 2026-07-07T15:31:58Z
updated: 2026-07-08T07:54:28Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/913
comments: 1
labels: bug, priority:high, area:workspace, effort:small, semver:patch
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:25.770Z
---

# [Issue 913]: [fix(workspace): scaffold upgrade clobbers a customized .typos.toml (dual-config corruption)](https://github.com/vig-os/devkit/issues/913)

Found during 0.4.1-rc1 consumer-upgrade testing (follow-up to #878, same class of bug).

## Problem

`init-workspace.sh --force` overwrites the consumer's `.typos.toml` with the generic template one, because `.typos.toml` is **not** in `PRESERVE_FILES`. Two failure modes were reproduced:

- **Customized config lost (mat, 0.4.0 → rc1):** a 69-line material-science `.typos.toml` (element symbols, `Macor`, `metalness`, `LSO`, fixture typos) was replaced by the 10-line generic template. The `typos` hook then "corrected" real content across the repo — `metalness`→`metallicity`, `LSO`→`ALSO`, and renamed `docs/catalog/ceramics/macor.md`→`macro.md`.
- **Dual-config corruption (vault, 0.3.5 → rc1):** vault carries a legacy-named `_typos.toml`; the upgrade dropped a new `.typos.toml` alongside it. `typos` honours both, and the template `.typos.toml` lacks the `Nd` exemption, so the hook corrupted `Nd`→`And` inside the scaffold's own `.devcontainer/scripts/version-check.sh` — `prek run --all-files` then fails out of the box on a fresh upgrade.

## Proposed fix

- Add `.typos.toml` to `PRESERVE_FILES` (it is already the pattern for `.pre-commit-config.yaml` / `justfile.project`), and print the preserved-vs-template diff like #878.
- Handle the legacy `_typos.toml` case so the upgrade never leaves two active typos configs (migrate `_typos.toml`→`.typos.toml`, or skip shipping the template `.typos.toml` when the consumer already has `_typos.toml`).

Refs: #878
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

