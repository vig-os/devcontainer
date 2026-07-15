---
type: issue
state: closed
created: 2026-07-15T06:36:06Z
updated: 2026-07-15T08:29:48Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1092
comments: 2
labels: bug, priority:high
assignees: none
milestone: none
projects: none
parent: 1096
children: none
synced: 2026-07-15T11:04:54.514Z
---

# [Issue 1092]: [[BUG] Managed .gitignore rewrite (#1024) drops consumer-required ignores with no durable committed extension point for repo-root paths](https://github.com/vig-os/devkit/issues/1092)

## Summary

The 1.2.0 language-aware managed `.gitignore` (#1024) drops ignores that certain consumers require, and the managed file's own advice — *"Put repo-specific ignores in a committed file your team owns instead"* — has **no valid form for a repo-root path**, because git only honors a root ignore from the root `.gitignore`, which devkit overwrites on every upgrade.

Surfaced upgrading the `commit-action` pilot (direnv mode, Node, flake-generated hooks) from 1.1.0 → 1.2.0.

## Two concrete losses on upgrade

1. **`.pre-commit-config.yaml` (flake-hooks opt-in).** A consumer that opts into flake-generated hooks (`hooks = { }` in `flake.nix`, a documented, supported option) gets `.pre-commit-config.yaml` installed as a **`/nix/store` symlink**. It must be gitignored — committing it pushes a machine-local, broken symlink. The 1.1.0 managed `.gitignore` ignored it; the 1.2.0 rewrite dropped it. There is **no committed extension point** for this root-level path other than the managed root `.gitignore`, so the consumer must re-edit a file stamped *"regenerated on upgrade; local edits are lost."*

2. **`dist/src/` byproducts (Node/JS Action).** The Node fragment correctly drops the blanket `dist/` ignore so `dist/index.js` stays tracked (#1024), but it also drops any handling of the `tsc`/`ncc` declaration byproducts under `dist/src/` (`.d.ts`, `.d.ts.map`). Those `.d.ts.map` files embed absolute `file://` paths (regenerated per checkout), so a whole-tree `git status`-based dist gate fails on them after `just bundle`. (This one *does* have a workaround — a nested `dist/.gitignore` — so it is the milder half.)

## Impact

After a clean, supported `install.sh --force` upgrade, a flake-hooks Node consumer's **pre-commit suite and dist gate are red** until they hand-restore ignores the upgrade silently removed — with no warning and, for the root-level case, no durable place to put them.

## Suggested fix (one or more)

- Have `init-workspace.sh` **append a consumer-owned `.gitignore` fragment** (e.g. `.gitignore.local`, or an `assets/gitignore.d/`-style consumer slot) that the managed regeneration preserves and re-includes — giving root-level paths a durable committed home.
- When the flake-hooks opt-in is detected (`hooks = { }` / a `.pre-commit-config.yaml` symlink into the store), **seed the `.pre-commit-config.yaml` ignore automatically**.
- For Node consumers, re-add a **byproduct ignore** (`dist/**` except the committed bundle entrypoints, or `dist/*.tsbuildinfo` + `dist/src/`) so `dist/src/` declaration output is ignored while `dist/index.js`/`dist/package.json` stay tracked.

## Interim workaround (applied in commit-action)

Nested `dist/.gitignore` (`/src/`) for the byproducts (durable), and re-added the `.pre-commit-config.yaml` line to the managed root `.gitignore` (not durable — will need re-adding on the next upgrade until this is fixed).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 07:30 AM_

Scope note (from #1096 triage): the durable consumer-owned root ignore slot introduced here should also resolve the self-contradiction at `assets/workspace/flake.nix:68`, which currently instructs the flake-hooks opt-in consumer to add `.pre-commit-config.yaml` to the managed root `.gitignore` — an edit the next upgrade destroys. Redirect that instruction to the new durable slot (or seed the ignore automatically) as part of this fix.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 15, 2026 at 08:29 AM_

Fixed by #1100 (merged to `dev`, commit `9a3aa179`; ships in the next release). Shipped: a preserved, consumer-owned **`.gitignore.project`** (mirroring `justfile.project`) whose contents `init-workspace.sh` appends to the regenerated root `.gitignore` on every upgrade — the durable committed home for repo-root ignores; the flake-hooks `/nix/store`-symlink `.pre-commit-config.yaml` ignore is now auto-seeded (gated on the symlink, so a hand-managed file is untouched); the Node fragment ignores `dist/src/` byproducts while keeping the committed bundle tracked; and `flake.nix` no longer instructs the doomed edit to the managed `.gitignore`. Part of #1096.

