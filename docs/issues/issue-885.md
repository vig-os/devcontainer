---
type: issue
state: closed
created: 2026-07-07T09:14:21Z
updated: 2026-07-08T07:41:16Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/885
comments: 1
labels: feature, priority:medium, area:workspace, effort:large, semver:minor
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:29.481Z
---

# [Issue 885]: [feat(workspace): persist delivery mode, identity, and modules in .vig-os — declarative manifest with a new "bare" mode](https://github.com/vig-os/devkit/issues/885)

### Description

Promote `.vig-os` from a single-purpose version pin into the project's declarative manifest: persist the **delivery mode** (`devcontainer` | `direnv` | `both` | new **`bare`**), the **project identity** (short name, org, GitHub repo), and — later — enabled capability **modules**, so `init-workspace.sh` reads the project's shape on every (re)scaffold instead of asking again. Add a `bare` mode for projects that want the standards (hooks, recipes, CI, conventions) without any container or flake machinery — no `.devcontainer/` directory that only brings confusion.

### Problem Statement

Today `.vig-os` holds exactly one key (`DEVCONTAINER_VERSION`, `assets/workspace/.vig-os`), while every other install-time choice is transient:

1. **Mode is not persisted.** `--mode devcontainer|direnv|both` exists only as an install flag (`install.sh` ~317, `init-workspace.sh` ~79–102). On a `--force` upgrade the mode must be re-supplied; omitted, it defaults to `both`, so a direnv-mode repo silently gets a template `.devcontainer/` re-added. The #738/#859 pre-existence guards paper over symptoms of exactly this non-persistence.
2. **Identity is not persisted.** `SHORT_NAME` / `ORG_NAME` / `GITHUB_REPOSITORY` are substituted once into the scaffold (`init-workspace.sh` ~407–437) and forgotten. Upgrades re-copy managed files containing `{{SHORT_NAME}}`-style placeholders, so the user must re-enter the same identity every upgrade — a typo drifts compose project names, renovate presets, and src/ layout.
3. **No thin deployment exists.** The thinnest mode today (`direnv`) still assumes a Nix flake. A pure-standards repo (host-native `uv`, no container, no flake) has no supported shape; 0.4.0 field-validation showed `.devcontainer/` confuses repos that never use it.
4. **Modules need a home.** The capability-module work (#883 hooks, #884 capability shells) needs a per-project declaration of enabled modules; `.vig-os` is the natural SSoT.

### Proposed Solution

**1. Extend `.vig-os` with new keys (format unchanged: flat `KEY=VALUE`, `#` comments):**

```sh
# vig-os devcontainer configuration
DEVCONTAINER_VERSION=0.4.0
DEVKIT_MODE=direnv                 # devcontainer | direnv | both | bare
DEVKIT_PROJECT=my_proj             # persisted SHORT_NAME
DEVKIT_ORG=EXOMA                   # persisted ORG_NAME
DEVKIT_REPO=exoma-ch/my-proj       # persisted GITHUB_REPOSITORY
DEVKIT_MODULES=""                  # reserved: space-separated capability modules (#884)
```

This is backward-safe by construction: all three existing parsers (`.github/actions/resolve-image/action.yml` ~31–51, `.devcontainer/scripts/initialize.sh` ~26–44, `.devcontainer/scripts/version-check.sh` ~204+) are line-based `case DEVCONTAINER_VERSION=*` matchers that skip unknown keys; nothing `source`s the file; docker-compose consumes the version only via the `.env` bridge. `DEVCONTAINER_VERSION` itself is **not** renamed here (it is sed-rewritten by `release.yml` ~532–539 and sparse-checked-out by several workflows) — key renames ride the #781 devkit rename with a read-both shim. New keys are named `DEVKIT_*` from the start so #781 does not have to touch them. All modes — including `bare` — keep writing `DEVCONTAINER_VERSION` (scaffold-version provenance, one code path).

**2. Make `init-workspace.sh` read the manifest before prompting.** Precedence: explicit flag/env > `.vig-os` value > prompt/default. Write back whatever was resolved (same `sed`/append pattern as the #852 version pin, `init-workspace.sh` ~398–405). Upgrades of a manifest-bearing repo become non-interactive and shape-preserving by default.

**3. Add `bare` mode.** Ships: root `justfile` + managed recipe file, `justfile.project`/`justfile.local`, `.pre-commit-config.yaml`, `.github/` CI, `pyproject.toml` scaffolding, `.vig-os`. Prunes: `.devcontainer/`, `flake.nix`, `.envrc` (with the same pre-existence guards as #738/#859). Requires a **host-native variant of the shipped `ci.yml`**: the current template is container-based (resolve-image → jobs run inside the image), which is meaningless without an image — the bare variant runs on the runner with `uv` set up directly.

**4. Migration/inference for existing consumers (no `DEVKIT_MODE` yet):** infer conservatively on upgrade — populated `.devcontainer/` + scaffold-stub flake ⇒ `both`; `.devcontainer/` only ⇒ `devcontainer`; flake/envrc only ⇒ `direnv`. Ambiguous combinations (e.g. `.devcontainer/` + consumer-authored flake, the #859 case) resolve to the *wider* mode and print what was inferred; interactive runs confirm. Never reshape a repo based on inference alone. On first upgrade, append the inferred/resolved keys to the legacy file so it self-documents from then on.

**5. Mode *switching* is destructive** (e.g. `both` → `bare` deletes `.devcontainer/`): out of scope here — the upgrade-guard issue (dedicated clean branch + diff preview) owns that; this issue only requires that a mode change never happens implicitly.

### Alternatives Considered

- **TOML/JSON manifest** — structured, but breaks the three tolerant line parsers and the `release.yml` sed, and adds a parser dependency to host-side shell (`initialize.sh` runs on the host before any container exists). Flat KV keeps every current consumer working; revisit only if `DEVKIT_MODULES` outgrows a quoted space-separated list.
- **Persisting mode in `devcontainer.json` or `flake.nix`** — circular: those files only exist in *some* modes; the manifest must exist in all of them.
- **Keeping mode as an install flag + better docs** — does not fix upgrade drift or enable non-interactive shape-preserving upgrades.
- **Naming new keys `VIG_OS_*` or unprefixed** — would need renaming again at #781; `DEVKIT_*` is stable across the rename.

### Additional Context

- Depends on **#877**: `direnv`/`bare` viability requires the CI-contract recipes (`sync`, `precommit`, `test`, …) to live in a **managed file outside `.devcontainer/`** — today the managed imports are all `.devcontainer/justfile.*` (root `justfile` template), so a no-`.devcontainer/` repo has only the preserved `justfile.project`. #877's relocation decision should be made with `bare` in mind.
- Coordinates **#781** (devcontainer → devkit rename): `DEVCONTAINER_VERSION` alias/shim and any future `.vig-os` → `.devkit` file rename land there, reading the old name when the new one is absent.
- Relates to **#883** (flake-generated hooks — its raw-YAML opt-out flag should live in this manifest) and **#884** (capability shells — `DEVKIT_MODULES` is reserved as their scaffold-level declaration) and the planned **upgrade-guard** issue (owns destructive mode switches).
- Prior art in-repo: #852 (write-back of the version pin post-scaffold), #738/#859 (mode-prune pre-existence guards — symptoms of non-persisted mode).

#### Tasks

- [ ] Define the `.vig-os` key set (`DEVKIT_MODE`, `DEVKIT_PROJECT`, `DEVKIT_ORG`, `DEVKIT_REPO`, `DEVKIT_MODULES` reserved) and document it in `docs/MIGRATION.md` + template comments
- [ ] `init-workspace.sh`: read-manifest-before-prompt precedence; write back resolved values; never change persisted mode implicitly
- [ ] `install.sh`: forward/read the same keys; drop the requirement to re-pass `--mode` on upgrade
- [ ] Mode inference for legacy consumers (conservative, transparent, confirm when interactive); append inferred keys on first upgrade
- [ ] Implement `bare` mode: template prune set + pre-existence guards
- [ ] Host-native `ci.yml` variant for `bare` (no resolve-image/container jobs)
- [ ] Tests: scaffold/upgrade matrix across all four modes × (fresh | legacy-no-manifest | manifest-bearing); parser tolerance test (unknown keys ignored)
- [ ] Changelog entry

#### Acceptance criteria

- A repo scaffolded in any mode upgrades with `--force` and **no mode/identity flags** and keeps its shape and names.
- Legacy consumers (version-only `.vig-os`) upgrade without breakage; inferred mode is printed and persisted.
- `bare` mode produces no `.devcontainer/`, no `flake.nix`/`.envrc`, and green CI on the host-native workflow.
- Existing CI consumers of `.vig-os` (resolve-image, initialize.sh, version-check.sh) are byte-for-byte unaffected by the new keys.

### Impact

- **Who benefits:** every consumer repo (shape-preserving upgrades), pure-Python/standards-only repos (`bare`), and the module work (declaration point).
- **Compatibility:** backward compatible (`semver:minor`) — new keys are additive; all existing parsers ignore them; `DEVCONTAINER_VERSION` semantics unchanged.

### Changelog Category

Added

Refs: #877, #781, #883, #884

---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:41 AM_

Delivered by #911 (merged to `dev` on 2026-07-07). Closing as complete for milestone 0.5.

