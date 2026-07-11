---
type: issue
state: closed
created: 2026-07-04T15:50:55Z
updated: 2026-07-08T13:07:51Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/814
comments: 2
labels: feature
assignees: none
milestone: none
projects: none
parent: none
children: 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828
synced: 2026-07-11T13:33:43.185Z
---

# [Issue 814]: [[MASTER] Terminal home environment as devkit home-manager modules](https://github.com/vig-os/devkit/issues/814)

## Context

The repo already delivers the org toolchain as a dev-shell (`mkProjectShell` +
nix-direnv), a Nix-built devcontainer image, and thin package-only
`homeManagerModules.default` / `nixosModules.default` (#777). What it does not
deliver is the *user-environment* layer: shell/tmux/sesh/editor/git/`~/.claude`
configuration with org defaults and per-user overrides — today that exists only
as single-user, hand-maintained personal configuration outside the org.

This epic ports that seed into **parameterized `homeManagerModules.*`** (option
namespace `vigos.*`) shipped from this repo as a **second product** — its own CI
matrix, docs, and API policy, sharing the `devTools` SSoT, lockfile, and release
train. Consumers: the org's private NixOS server fleet (HM as NixOS module,
per-user opt-in), and standalone home-manager on personal
machines (aarch64-darwin first-class; x86_64-darwin best-effort). The
devcontainer image is **not** integrated.

Design authority: `docs/rfcs/ADR-home-environment-modules.md` (E1 below).

## Confirmed decisions (from the ADR)

- **Artifact:** home-manager modules with options; `homeConfigurations.demo` as
  onboarding sugar only. **Placement:** this repo (parity SSoT; extraction later
  is a URL change).
- **Inputs:** `home-manager` is the **only** new flake input. No nixvim (editor
  module = `programs.neovim` + nixpkgs `vimPlugins.claudecode-nvim`). No
  third-party claude-code flake — keep the `fastMovers` overlay on
  `nixpkgs-unstable`, kept fresh by a scheduled lock bump.
- **Image:** not integrated (HM activation can't run in `dockerTools` builds;
  closure/CVE-gate/startup-time costs; container never *needs* the home env).
- **`~/.claude`:** `~/.claude.json` + `settings.local.json` never managed;
  `settings.json` seeded copy-if-absent (seed updates announced in changelog,
  re-seed = delete + re-activate); hooks + an org CLAUDE.md *fragment*
  (`~/.claude/vigos.md`) copied via `home.activation` (checksum-overwrite
  with `.bak` of local edits) — **no symlinks of any kind in `.claude/`**;
  top-level `~/.claude/CLAUDE.md` stays user-owned (Claude Code writes to it)
  and is seeded with a single `@vigos.md` import line; org defaults
  pre-authorize nothing; `DISABLE_AUTOUPDATER=1` via `home.sessionVariables`;
  no home-level skills (repos stay the skills SSoT).
- **CLAUDE.md hierarchy:** templates + guidelines, not managed files; optional
  off-by-default symlink option with user-declared paths.
- **Optionality invariant:** none → direnv → devcontainer → home env, strictly
  additive; nothing work-required depends on the home env.
- **Platforms:** bash **and** zsh; platform guards
  (`pkgs.stdenv.hostPlatform.isLinux`, per-package availability);
  aarch64-darwin CI build + Cachix push must exist **before** first colleague
  onboarding; x86_64-darwin = eval-only best-effort, EOL at nixpkgs 26.05 EOL
  (2026-12-31), fallback = amd64 devcontainer image.
- **Credentials:** resident per-user secrets on servers for persistent
  sessions (no SSH agent forwarding); canonical interface
  `~/.config/vigos/secrets/<NAME>` (0600) + opt-in shell env export;
  deployment out of scope (sops-nix backing on servers, hand-placed or
  OS-native on laptops); interactive auth must keep working without it.
  Hygiene: scoped/revocable only — fine-grained expiring PATs, Claude
  `setup-token`, Cachix not per-user; **SSH keys (auth + signing) minted per
  user × host, never copied** — signatures identify the originating machine.
- **Sandboxing:** working agreement (autonomous runs in container), not a
  security boundary; bwrap wrapper = tracked backlog, out of scope here.
- **Release:** modules ride existing release tags; consumers pin
  `github:vig-os/devcontainer/<tag>`; option renames get a
  `mkRenamedOptionModule` shim for one release + changelog *modules* entry.
  The workspace scaffold's untagged `vigos.url` gets aligned with the policy
  in E2. Dogfood exception: the maintainer's config tracks `dev` as
  pre-release canary until the first module-bearing tag ships.
- **One HM mode per user per host** (central XOR standalone; never both).

## Scope

**In:**
- Tracking only — links the sub-issues below; holds decisions + dependency graph.

**Out:**
- Image integration (rejected; revisit-trigger in ADR).
- nixvim editor flake (personal / future).
- bwrap sandbox wrapper (backlog issue, linked, not in this epic).
- Server-fleet adoption (private infrastructure repo's change; devkit only
  keeps modules cleanly importable).
- nix-darwin, macOS Intel investment, home-level skills, atuin sync server.

## Sub-issues

- **Track E — Policy & substrate first:**
  - E1 (#815) — Accept and merge `ADR-home-environment-modules` (flip
    `status: proposed` → `accepted`).
  - E2 (#816) — Module release/versioning/changelog policy in `docs/NIX.md` +
    `CHANGELOG.md` *modules* subcategory + align the workspace scaffold's
    untagged `vigos.url` with the pin-tags policy.
  - E3 (#817) — Scheduled `nix flake update nixpkgs-unstable` workflow (claude-code
    freshness), full CI as merge gate.
- **Track A — Library core + CI substrate:**
  - A1 (#818) — `vigos.*` option namespace + module skeleton; `programs.vigos-devtools`
    → `mkRenamedOptionModule`; package module becomes
    `homeManagerModules.packages`; `.default` becomes the all-modules umbrella
    (each disabled by default); modules resolve packages from devkit's locked
    nixpkgs + overlay (self-pkgs, per the #777 overlay constraint); export
    `homeModules.*` aliases.
  - A2 (#819) — `home-manager` flake input + per-system flake checks building the
    homeConfigurations matrix: `minimal` (only `vigos.shell`) and `full`
    (every module) for synthetic user `ci` (`/home/ci`; `/Users/ci` on
    darwin; pinned `stateVersion`). x86_64-linux legs join the Tier-0 gate
    (#778/#779, via PR #791); aarch64-linux legs on arm runners; darwin legs
    build in A3 only.
  - A3 (#820) — `aarch64-darwin` CI job (macos runner) building the matrix + Cachix
    darwin push.
  - A4 (#821) — Wave-1 modules: `vigos.shell` (bash+zsh, starship, atuin, opt-in
    `secretsEnv` export hook per the ADR spec), `vigos.multiplexer` (tmux),
    `vigos.cli` (modern-unix *configuration only* — packages ship solely via
    `homeManagerModules.packages`, never duplicated), `vigos.direnv`,
    `vigos.git` (identity options; `signingKeyPath` default-null, signing
    activates only when set — key minting/forge registration are C2 runbook
    steps; gh, lazygit, delta).
- **Track B — Dogfood migration (maintainer's personal config consumes devkit):**
  - B1 (#822) — Wave 1 consumption (may close per-module; wave complete when all
    private copies are deleted); acceptance = no package changes in
    `nvd diff` **and** `home-files` tree diff limited to the sub-issue's
    expected-diff allowlist.
  - B2 (#823) — Wave 2: `vigos.claude` (settings-seeding policy, fragment/hooks
    copy management, agent runtime deps, the optional off-by-default
    workspace-CLAUDE.md management option); devcontainer consumes the
    canonical secrets dir via env-file/mount (compose scaffolding only,
    image untouched) — the slim token path of #546.
  - B3 (#824) — Wave 3: `vigos.sesh` (projects option API replacing hardcoded paths),
    `vigos.ghdash` (parameterized filters/paths), `vigos.editor`
    (`programs.neovim` + `claudecode-nvim`, no nixvim).
- **Track C — Onboarding & docs:**
  - C1 (#825) — `docs/home/` bootstrap guide: Determinate installer, macOS
    `trusted-users`/Cachix trap, `home-manager switch --flake`, dotfile-collision
    adoption path (`-b backup`).
  - C2 (#826) — Override cookbook + rollback one-pager (HM generations /
    `nixos-rebuild --rollback` / image-tag pin) + the spelled-out operational
    meaning of best-effort Intel + credential-hygiene one-pager (PAT
    scoping/expiry, per-user×host SSH keys, rotation/offboarding runbook).
  - C3 (#827) — `templates.personal` starter flake (20-line personal flake importing
    the modules) + `homeConfigurations.demo` (synthetic `demo` user, `full`
    profile, all matrix systems).
  - C4 (#828) — CLAUDE.md template hierarchy (org/workspace/user) + directory-layout
    convention docs (the workspace-CLAUDE.md management option itself lands
    with `vigos.claude` in B2 — C4 stays docs-only).

## Dependency graph & parallelism

```
  start in parallel:  E1   E2   E3
  E1 ─► A1 ─► A2 ─► A3 ─┐
         └──► A4 ────────┤
                         ├─► B1 ─► B2 ─► B3
  A2 ─────────► C3       │
  A3 + A4 ────────────►  C1 ─► C2
  E1 ─────────► C4   (independent of A/B)
```

- **Critical path (MVP):** `E1 → A1 → A2 → A3 → (A4) → B1 → C1`.
- **MVP slice** (proves the architecture end-to-end): one wave-1 module with
  `vigos.*` options + matrix checks + darwin CI/Cachix + the maintainer's
  personal configuration consuming it with zero diff + a bootstrap doc the
  arm-Mac colleague follows unaided.
- **Conservative early-exit:** stopping after B1 + C1 still delivers a usable,
  documented wave-1 environment on servers and the arm Mac; taking it means
  explicitly re-scoping B2/B3/C4 into follow-up issues so the epic can close
  against its criteria.
- **Sequencing vs. open work:** `release/0.4.0` is in flight (cutover #639
  still open and gated); the release-branch cut predates all epic code, so epic PRs
  merge to `dev` freely and ship no earlier than the next release. Library/CI
  tracks are rename-proof and may start now; the C-track doc surge ideally
  lands after the #781 rename (or uses org-level URLs); nothing here touches
  #639/#642 (image cutover) — by design.

## Acceptance criteria

- All sub-issues closed; ADR status `accepted`.
- `nix flake check` builds the homeConfigurations matrix; aarch64-darwin CI
  green and its closures on Cachix **before** first colleague onboarding.
- The maintainer's personal configuration imports every module landed by this
  epic (no private duplicates); each wave passed the generation-diff bar (no
  package changes; `home-files` diff within the wave's allowlist).
- A tier-"none" user is unaffected: dev-shell, devcontainer, CI, pre-commit all
  work with no home-env dependency (optionality invariant holds).
- Claude Code resolves to the same pinned version via the one `fastMovers`
  overlay across dev-shell, image, and home modules (store paths differ per
  system); the home modules set `DISABLE_AUTOUPDATER` via
  `home.sessionVariables` (dev-shell/image counterpart = linked follow-up
  chore, not this epic).
- Onboarding test: colleague reaches `home-manager switch` on the arm Mac with
  zero live help, using C1–C3 alone.

## Related existing issues

| Issue | Relation | Verdict |
|-------|----------|---------|
| **#777** flake polish (module outputs, treefmt, install app) | Introduced the package-only `homeManagerModules.default`/`nixosModules.default` this epic parameterizes (A1). | **Extended** — cross-link. |
| **#781** rename `devcontainer` → `devkit` | Namespace `vigos.*` chosen rename-proof; C-track docs sequence after it where practical. | **Related** — cross-link; no gate. |
| **#546** slim Claude Code OAuth-token forwarding | Resolved by the canonical secrets-dir convention: container env-file/mounts `~/.config/vigos/secrets/` (B2). | **Absorbed** — implement via B2, close pointing there. |
| **#779** flake checks as CI Tier 0 (closed via PR #791) | A2's matrix checks join the landed Tier-0 gate. | **Landed substrate** — extend. |
| **#795** `mkProjectServices` helper (closed) | Same "second product" flake-growth pattern; no dependency. | **Independent** — precedent landed. |
| **#639 / #642** image cutover / Debian decommission | Untouched — image integration rejected by ADR Axis 4. | **Independent by design.** |
| **#545** agent-CLI toolkit (closed) | Precedent: agent tooling as product; its host-side counterpart is B2. | **Historical.** |
| **#625** Nix migration master (open, tracking) | Structural template for this epic; scope disjoint. | **Sibling epic.** |

Refs: #625

---

# [Comment #1]() by [c-vigo]()

_Posted on July 4, 2026 at 04:32 PM_

MVP night complete — all tracks landed on `feature/814-home-environment-modules`; full ledger, evidence, and the morning handoff list live in draft PR #833. B2 (#823) / B3 (#824) remain for the follow-up wave.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 01:07 PM_

## Closing — epic complete, all sub-issues closed

Tracking-only master; acceptance is "all sub-issues closed", now met. Every
track is done:

- **Track E — policy & substrate:** #815 (ADR accepted), #816 (release/versioning policy), #817 (nixpkgs-unstable lock bump)
- **Track A — library core + CI:** #818 (`vigos.*` namespace + skeleton), #819 (home-manager input + matrix checks), #820 (aarch64 CI + Cachix), #821 (wave-1 modules)
- **Track B — dogfood:** #822 (wave 1), #823 (wave 2: `vigos.claude` + secrets dir), #824 (wave 3: `vigos.{sesh,ghdash,editor}`)
- **Track C — docs:** #825 (bootstrap), #826 (override/rollback/credential-hygiene cookbook), #827 (`templates.personal` + `homeConfigurations.demo`), #828 (CLAUDE.md hierarchy)

The terminal home environment now ships from `vig-os/devcontainer` as
parameterized `homeManagerModules.*` under the `vigos.*` namespace, consumed by
the maintainer's personal config (dogfooded through waves 1–3, #822 evidence
shows a zero-package-regression switch on the live host).

Follow-on work (server-fleet adoption, bwrap sandbox wrapper, nix-darwin) is
out-of-scope per the ADR and tracked separately.

