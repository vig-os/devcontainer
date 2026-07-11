---
type: issue
state: closed
created: 2026-07-07T09:04:46Z
updated: 2026-07-08T07:41:11Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/883
comments: 1
labels: feature, priority:medium, area:workspace, effort:large, semver:minor
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:30.276Z
---

# [Issue 883]: [feat(workspace): generate .pre-commit-config.yaml from the flake (git-hooks.nix) — composable base hooks, consumer-extensible in the project flake](https://github.com/vig-os/devkit/issues/883)

### Description

Make the flake the **generator** of `.pre-commit-config.yaml` instead of a parallel
verification artifact, and expose the hook set as a composable module consumers
extend from their own (preserved) `flake.nix`: enable/disable base hooks, add
custom hooks, and set global + per-hook `excludes` — without ever editing a
managed file.

This builds on infrastructure that already exists — it is **not** a new-framework
adoption:

- `cachix/git-hooks.nix` is already a flake input and already declares the
  sandbox-pure hook subset as Nix (`preCommitCheck`, `flake.nix` ~421–547, with
  `package = pkgs.prek`; Refs #778).
- The scaffold already ships a consumer flake (`assets/workspace/flake.nix`)
  consuming `vigos` as an input via `vigos.lib.mkProjectShell` + `extraPackages`
  (scaffold-once, never overwritten) — the natural home for consumer hook config.
- The `vigos.*` home-manager modules (ADR-home-environment-modules) already
  establish the "shared base module + consumer opt-in" pattern this follows.

What changes is the direction of truth: today the committed YAML is the
hand-maintained runner SSoT and `checks.pre-commit` mirrors a subset of it
(the "two-artifact model", `docs/NIX.md` "Evaluator and pre-commit decisions"),
with a `sync-manifest` transform (`scripts/manifest.toml`) deriving the scaffold
copy. That is three hand-synchronized representations of one hook set.

### Problem Statement

Field validation of 0.4.0 (Refs #639) showed the scaffold's wholesale replacement
of `.pre-commit-config.yaml` silently destroys consumer customization — global
`exclude:` blocks and per-hook excludes (Refs #878: physics data tables rewritten,
false-positive `detect-private-key`). The interim fix preserves the file, but that
recreates the inverse problem (Refs #877): preserved files never receive upstream
hook updates, so consumer hook sets will drift stale.

The root cause is that one YAML file holds two owners' content: **our** base hook
set (should be managed/current) and **the consumer's** customization (must be
preserved). A generated config with consumer config expressed in their own flake
separates the owners cleanly:

- base hooks live in a shared module we ship → always current on toolchain bump;
- consumer hooks/excludes live in the consumer's preserved flake → never clobbered.

It also collapses the maintenance triangle in this repo: committed YAML,
`preCommitCheck` mirror, and manifest transforms are kept in agreement by hand
today (e.g. the `check-yaml --allow-multiple-documents` fidelity note, the
duplicated shellcheck/yamllint args). One Nix definition should render all of it.

### Proposed Solution

**1. Shared hooks module (this repo).** Refactor `preCommitCheck`'s hook
definitions into a reusable module (e.g. `nix/hooks.nix`) parameterized like the
existing lib surface, and expose it as a **`hooks` argument on
`mkProjectShell`** (single consumer entry point; the config refreshes naturally
on shell entry):

```nix
# consumer flake.nix — preserved, consumer-owned
vigos.lib.mkProjectShell {
  inherit pkgs;
  hooks = {
    pymarkdown.enable = false;                       # toggle a base hook
    detect-private-keys.excludes = [ "worker/src/index\\.ts" ];
    my-data-check = {                                # fully custom hook
      enable = true;
      entry = "./scripts/check-dat.sh";
      files = "\\.dat$";
      language = "system";
    };
  };
  hooksExcludes = [ "^data/stopping/" "\\.dat$" ];    # global excludes
}
```

`git-hooks.nix` supports all of this today (custom hooks with the full
pre-commit schema, global `excludes`, per-hook `excludes`, `language: system`
entries, `package = pkgs.prek`), and its `run` result exposes the rendered
config (`configFile`) plus a `shellHook` that installs `.pre-commit-config.yaml`
into the repo. Base-hook options should include the knobs consumers plausibly
need — e.g. `no-commit-to-branch`'s protected-branch pattern as a module option.

**2. Generation & delivery per mode.**

- **direnv-mode:** the hooks module is wired into `mkProjectShell`'s `shellHook`
  — entering the shell installs/refreshes the generated config.
  `.pre-commit-config.yaml` becomes a gitignored generated artifact
  (git-hooks.nix's own recommended model).
- **devcontainer-mode:** the image ships `nix`, `direnv` and `prek`, and the
  scaffold ships the consumer flake, so the same generation works in-container;
  decide the trigger (postCreate/postStart hook vs a `just hooks-sync` recipe).
- **CI:** the shipped `ci.yml` must generate before `prek run --all-files`
  (e.g. run inside the devshell — same seam as #854).

**3. Committed vs gitignored — decided: gitignored + regenerated.** The
generated file embeds `/nix/store` paths for nix-resolved hooks, so it is
**gitignored and regenerated** on shell entry (upstream's recommended model;
avoids the nixpkgs-bump churn that `docs/NIX.md` cites as the reason generation
was rejected before). Fallback if a committed config ever proves necessary:
render a PATH-portable variant (bare-name `language: system` entries only — the
pattern the committed config already uses for ruff/typos/shellcheck/nixfmt).
Record the decision in `docs/NIX.md` and retire the "two-artifact model"
section.

**4. This repo dogfoods first.** Replace the hand-maintained root
`.pre-commit-config.yaml` and the `RemovePrecommitHooks`/`ReplaceBlock`
transforms in `scripts/manifest.toml` with the module (upstream-only hooks
become module options the scaffold profile disables). `checks.pre-commit` stops
being a mirror and becomes the same module evaluated in sandbox-pure profile —
drift between gate and runner becomes impossible by construction.

**5. Escape hatch (freedom guarantee).** A consumer may opt out of generation
and hand-manage a raw `.pre-commit-config.yaml`: if the file exists and is not
the generated artifact (or an explicit marker/manifest flag says so), the
scaffold and shellHook leave it alone (it stays preserved per #878). Nobody is
forced through Nix to configure hooks.

#### Tasks

- [ ] Extract `preCommitCheck` hook definitions into a shared, profile-aware hooks module; expose as a `hooks` arg on `mkProjectShell` (incl. base-hook options such as the `no-commit-to-branch` branch pattern)
- [ ] Record the gitignored-generated decision in `docs/NIX.md`; supersede the two-artifact model section (document the committed-portable render as fallback)
- [ ] Wire generation into direnv-mode (`shellHook`) and devcontainer-mode (postCreate/postStart or `just` recipe)
- [ ] Update scaffold: consumer flake example with hooks block; drop the pre-commit entries from `scripts/manifest.toml`; gitignore handling
- [ ] Escape-hatch detection (raw-YAML opt-out) in `init-workspace.sh` + shellHook
- [ ] Shipped `ci.yml`: generate config before `prek run` (coordinate with #854)
- [ ] Dogfood in this repo: root config generated; `checks.pre-commit` consumes the same module
- [ ] `docs/MIGRATION.md`: how consumers port existing YAML excludes to the flake block; note the YAML→Nix interface change
- [ ] Integration test: scaffold a consumer, customize hooks + excludes, upgrade the scaffold, assert customization survives and base hooks updated

### Alternatives Considered

- **Merge logic in the installer** (splice consumer `exclude:` keys onto the
  freshly-synced YAML): fragile YAML surgery, still one file with two owners,
  and throwaway once generation lands. Rejected.
- **Keep the file preserved forever** (#878 stopgap as end-state): consumer hook
  sets go stale; every base-hook change becomes a manual MIGRATION step. Rejected
  as end-state; fine as the interim.
- **devenv's hooks integration:** devenv is already rejected as the shared shell
  builder by the accepted `ADR-nix-devenv-strategy` (parity-test constraint, IFD
  cold-eval tax); its hooks layer is git-hooks.nix underneath anyway — use the
  source directly.
- **Separate `vigos.lib.mkProjectHooks` entry point:** viable, but a second lib
  surface for consumers to discover; the `hooks` arg on the existing
  `mkProjectShell` keeps one entry point and ties config refresh to shell entry.
  Can be split out later if a consumer needs hooks without the shared shell.

### Additional Context

- Refs #878 (supersedes its preserve-file stopgap), #877 (same
  managed-vs-preserved root cause, justfile side), #854 (ci.yml/devshell seam),
  #778 (git-hooks.nix + prek adoption this builds on), #639 (field validation
  that surfaced the defect class), #882 (native-build contract — same
  "capabilities come from the project flake" direction).
- Planned sibling issues (numbers TBD at filing time): *modular capability
  shells* (opt-in `vigos` modules on `mkProjectShell`), *declarative `.vig-os`
  manifest* (mode/modules SSoT — the hooks opt-out flag should live there),
  *upgrade preflight guard* (clean-branch requirement for scaffold upgrades).
- `docs/NIX.md` "Two hook artifacts, kept in agreement" documents why generation
  was previously rejected: (a) the scaffold "has no flake" — no longer true, the
  scaffold ships a vigos-input flake in both modes; (b) store-path churn — solved
  by gitignoring the artifact. Both objections are addressed above rather than
  ignored.

### Impact

- **Who benefits:** every scaffold consumer (hook updates flow automatically;
  customization survives upgrades — the #878 class of data loss becomes
  structurally impossible); this repo (three hand-synced hook representations
  collapse to one).
- **Compatibility:** backward compatible via the escape hatch; consumers opt in
  by adding the hooks block to their preserved flake. The editing interface for
  hook customization moves YAML→Nix for opted-in repos (called out in
  MIGRATION.md). Semver: **minor** (new lib surface + scaffold behavior).

### Changelog Category

Added

Refs: #878, #877, #854, #778, #639, #882

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:41 AM_

Delivered by #908 (merged to `dev` on 2026-07-07). Closing as complete for milestone 0.5.

