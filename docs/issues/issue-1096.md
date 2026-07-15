---
type: issue
state: closed
created: 2026-07-15T07:22:33Z
updated: 2026-07-15T08:30:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1096
comments: 1
labels: priority:high, area:workspace
assignees: none
milestone: none
projects: none
parent: none
children: 1092, 1093, 1099
synced: 2026-07-15T11:04:52.859Z
---

# [Issue 1096]: [[EPIC] Managed-file upgrades have no durable consumer seam and no scaffold↔flake lockstep (root cause of #1092 + #1093)](https://github.com/vig-os/devkit/issues/1096)

## Summary

Two `priority:high` bugs — #1092 and #1093 — surfaced from the **same event**
(the `commit-action` pilot upgrade 1.1.0 → 1.2.0) and reduce to **one
architectural gap in the managed-file upgrade model**. Fixing them
independently patches two symptoms and leaves the pattern to recur on the next
managed file / next coupled concern. This epic tracks the root cause and its
wider blast radius.

The devkit's core promise is *"we manage these files and upgrade them for you."*
That promise has exactly two seam categories today, and a real consumer that
diverges from the default shape falls between them:

- **`PRESERVE_FILES`** (16 files) — whole-file consumer ownership; never
  overwritten if present (`justfile.project`, `flake.nix`, `.pre-commit-config.yaml`,
  `.typos.toml`, …).
- **Fully-managed** (~90 files) — overwritten on every `install.sh --force`
  (*"regenerated on upgrade; local edits are lost"*).

There is **no third category** for a managed file that legitimately needs
*consumer-specific additions it cannot relocate to a preserved sibling* — and
no mechanism keeping concerns that ship from **two version vehicles** (scaffold
image vs `vigos` flake input) in lockstep. #1092 is the first gap; #1093 is the
second. Below is the deep evaluation of where else each recurs.

---

## Root-cause class A — managed full-overwrite files with no durable consumer seam (#1092)

A managed file is whole-file overwritten, but the consumer legitimately needs to
add repo-specific content to it, and that content **cannot** live in a preserved
sibling — most acutely for **repo-root paths**, since git only honors a root
ignore from the root `.gitignore`, which devkit overwrites. The managed file's
own advice (*"put repo-specific ignores in a committed file your team owns"*) has
no valid form for that case. Worse, `assets/workspace/flake.nix:68` **instructs**
the flake-hooks opt-in consumer to add `.pre-commit-config.yaml` to `.gitignore`
— an edit the next upgrade destroys.

Precedent for the fix already exists but was applied one file at a time:
`.pre-commit-config.yaml` (#878) and `.typos.toml` (#913) were **promoted to
`PRESERVE_FILES`** precisely because a template overwrite silently destroyed
repo-specific `exclude:`/exception content. The same reasoning was never applied
systematically.

### Deep-eval: other at-risk managed files (same class)

| File | Managed? | Consumer additions it invites | Seam today | Risk |
|------|----------|-------------------------------|------------|------|
| `.gitignore` (root) | yes | repo-root ignores (`.pre-commit-config.yaml` store symlink, `dist/src/` byproducts) | none (devkit-owned `gitignore.d/` language fragments only) | **REPORTED #1092** |
| `.yamllint` | yes | per-repo `ignore:` globs, rule relaxations | none — **not** in `PRESERVE_FILES` | **High** — same shape as `.typos.toml`/`.pre-commit-config.yaml`, which *were* promoted |
| `.pymarkdown.config.md` | yes | per-repo rule disables for domain docs | none | **High** — identical class to `.yamllint` |
| `.vscode/settings.json` | yes | repo editor settings, `files.exclude` | none | Medium (editor-only) — **also** a #1093 JSONC file → double-exposed |
| `.devcontainer/devcontainer.json` | yes | VS Code extensions, features, mounts | `docker-compose.project.yaml` covers compose, **not** devcontainer.json | Medium — no seam for the extensions/features list |
| `SECURITY.md` | yes | repo-specific security contact | none — **asymmetric**: README/CHANGELOG/LICENSE are preserved, SECURITY.md is not | Low–Medium |
| `.github/label-taxonomy.toml`, `.github/agent-blocklist.toml`, `.claude/agent-models.toml`, `.github/ISSUE_TEMPLATE/config.yml` | yes | repo-specific labels / model map / blocklist / contact links | none | Low frequency, same class |

**Structural direction:** adopt a **uniform "managed base + preserved consumer
fragment"** convention with a form valid for root-level paths (the
`.gitignore.local`-append or consumer `gitignore.d/` slot proposed in #1092),
then audit every managed lint/config file above and either **promote to
`PRESERVE_FILES`** (the `.typos.toml` path) or **give it a fragment slot**. Stop
managed files from instructing edits they then destroy (`flake.nix:68`).

---

## Root-cause class B — coupled concerns split across scaffold image vs flake input, no lockstep (#1093)

Two halves of one change ship from **different vehicles** that version
independently, and nothing detects skew:

- the **scaffold** (`init-workspace.sh`, keyed to `.vig-os` `DEVKIT_VERSION`)
  writes files, while
- the **`vigos` flake input** (`nix/hooks.nix`) delivers the hook behavior that
  acts on those files.

A consumer who pins `vigos.url = "…?ref=1.1.0"` and bumps only the scaffold to
1.2.0 gets the #1053 JSONC banner **without** its `check-json` exclude → every
commit fails, no warning.

### Deep-eval: this is systemic, not one JSONC exclude

`nix/hooks.nix` hard-codes **its entire exclude set to scaffold-delivered
paths**. Any future scaffold path that needs a hook exclude reproduces the skew:

| Flake-side exclude (`nix/hooks.nix`) | Scaffold-delivered target |
|--------------------------------------|---------------------------|
| `checkJsonExclude` (L64) | `.devcontainer/devcontainer.json`, `.vscode/settings.json`, `workspace.code-workspace.example` — **REPORTED** |
| `shellcheckExclude` (L59) | `.envrc` (direnv scaffold file) |
| `yamlExclude` (L34) | `.github_data/`, `docs/issues/`, `docs/pull-requests/` (sync-issues scaffold dirs) |
| markdownlint excludes (L415) | `README.md`, `CONTRIBUTE.md`, `TESTING.md` |

There are **three version sources**, of which one is an orphan:

1. `.vig-os` `DEVKIT_VERSION` — scaffold **and** (via `resolve-toolchain`) the CI
   image tag.
2. Container image tag — derived from (1), already unified.
3. `vigos.url` flake `ref` pin — **independent; drifts silently.**

The `mkProjectShell` `vigos.*` module options are a second flake↔scaffold
coupling (the scaffold `flake.nix` stub references option *definitions* that ship
in the flake). And the lockstep invariant is **undocumented** — `MIGRATION.md`
covers the repo rename hand-update and RC-pin migration, but never states that
`DEVKIT_VERSION` and the flake `ref` must move together.

**Structural direction:** make `install.sh` **own or verify** the flake pin
against `DEVKIT_VERSION` — at minimum **detect and warn** on skew (cheap, high
value), ideally rewrite the pinned `ref` when set (the `vigos.url` line is a
managed concern). Document the lockstep invariant where the pin is set.

---

## Why now

The pilot did its job: it found the *class* of defect that only appears when a
real consumer diverges from the default shape. **cad2gdml (#1040) is the next
external consumer** — direnv mode, being onboarded now — and will hit the same
two classes the moment it needs a non-default ignore or pins the flake. Landing
the seam convention + skew warning **before** Phase 2 onboarding is cheaper than
re-living the pilot's red-tree debugging on someone else's repo. Also worth a
release-cycle decision: whether the cheap halves (skew warning + durable
`.gitignore` slot) warrant a **1.2.1** before that onboarding.

## Sub-issues

- [ ] #1092 — managed `.gitignore` drops consumer-required ignores; no durable root-level extension point (class A)
- [ ] #1093 — `DEVKIT_VERSION`/flake-pin skew ships the #1053 banner without its `check-json` exclude (class B)

## Follow-on work this epic scopes (file as sub-issues once triaged)

- Audit `.yamllint` / `.pymarkdown.config.md` → promote to `PRESERVE_FILES` or add a fragment slot (class A).
- Decide the general "managed base + preserved consumer fragment" convention (class A).
- Resolve the `flake.nix:68` self-contradiction — stop instructing an edit the upgrade destroys (class A).
- `install.sh` skew detect/warn between `DEVKIT_VERSION` and the pinned flake `ref` + document the invariant (class B).

Refs: #1092

---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 08:30 AM_

Resolved. All three tracked sub-issues are fixed and merged to `dev` (ship in the next release):

- **Class A — no durable consumer seam:** #1092 → #1100 (`9a3aa179`) adds the preserved `.gitignore.project` seam for repo-root ignores; #1099 → #1102 (`23dd89a7`) generalizes the promote-to-`PRESERVE_FILES` pattern to the `.pymarkdown` / `.yamllint` / `.pymarkdown.config.md` lint configs (the `.typos.toml`/#913 precedent).
- **Class B — scaffold↔flake lockstep:** #1093 → #1101 (`04016b0e`) adds warn-on-skew detection in `install.sh --force` plus the lockstep invariant in `MIGRATION.md`.

Not filed (YAGNI — documented observations only, no consumer has hit them): the milder editor/config instances of Class A — `.vscode/settings.json`, `.devcontainer/devcontainer.json` (extensions/features), and the `SECURITY.md` preserve-asymmetry. They remain in this epic's write-up as future work to file if/when a consumer is actually affected. Closing the epic since its concrete scope is complete.

