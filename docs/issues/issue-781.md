---
type: issue
state: open
created: 2026-06-30T12:52:12Z
updated: 2026-07-10T22:58:56Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/781
comments: 8
labels: chore, priority:high, area:image, effort:medium, semver:major
assignees: none
milestone: 1.0
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:47.311Z
---

# [Issue 781]: [[CHORE] Rename devcontainer → devkit (after publish-cutover #639)](https://github.com/vig-os/devkit/issues/781)

## Rename `devcontainer` → `devkit`, ship as **devkit 1.0.0**

> **This issue is the source of truth for the rename program.** The body below is a living
> plan-of-record (checklist auto-tracks as PRs merge); a dated status timeline lives in the
> comments. Sequenced AFTER the gated publish-cutover #639 — consumer-facing, `semver:major`.

**Origin:** PR #670 roadmap, thread E + [rename note](https://github.com/vig-os/devcontainer/pull/670#issuecomment-4834414012). Refs #639, #670.

---

### Confirmed decisions (approved 2026-07-10)

- **Brand spelling:** `devkit` (one word) — matches all existing `DEVKIT_*` manifest keys.
- **Version target:** **1.0.0** — the rename milestone; declares the contract stable. (Breaking surface is now small: **image ref unchanged**; pin-key + install-source changes are soft.)
- **Pin-key migration:** `DEVCONTAINER_VERSION` → `DEVKIT_VERSION` via a **dual-key parser** — read
  `DEVKIT_VERSION` first, fall back to legacy `DEVCONTAINER_VERSION`. Soft cutover; un-migrated
  consumers keep working until an `install.sh --force` re-scaffold.
- **Both repos rename:** `vig-os/devcontainer` → `vig-os/devkit` **and**
  `vig-os/devcontainer-smoke-test` → `vig-os/devkit-smoke-test`.
- **Image name UNCHANGED** — stays `ghcr.io/vig-os/devcontainer` (the artifact is a dev container; `devkit` is the project/repo that ships it). No new package, no consumer image migration. *(Course-correction 2026-07-10, #974 — supersedes the earlier "new devkit package" plan.)*

**Rollback levers:** pin `DEVKIT_VERSION`/`DEVCONTAINER_VERSION=0.5.1` (last pre-rename release) or
`0.3.9` (final Debian). Pre-promote failures auto-reset `release/1.0.0` (never delete tags).

---

### Stage checklist

#### Stage 0 — Pre-flight (manual / human-gated)
- [~] ~~GHCR `ghcr.io/vig-os/devkit` seeded~~ — **now unused** (image stays `devcontainer`, #974); delete the seeded package (needs `delete:packages`/UI)
- [x] Rename smoke-test repo `devcontainer-smoke-test` → `devkit-smoke-test` ✅ **done** (remote updated; old name redirects)
- [x] Smoke-test dispatch listener verified `active` post-rename (a real test dispatch is deferred to the 1.0.0 candidate — it runs the full cycle)

#### Stage 1 — Code rename on `dev` (PRs, all `Refs: #781`)
- [x] **PR 1** — dual-key version parser (`DEVKIT_VERSION` → legacy fallback) — resolve-image action, scaffold scripts, flake — #968 ✅ **merged**
- [x] **PR 3** — internal package identity (`pyproject.toml`, `package.json`, lockfiles) — #969 ✅ **merged**
- [x] **PR 4** — pre-rename curl `-L` hardening (docs/install one-liners) — #970 ✅ **merged**
- [x] **PR 5** — flip *written* pin key to `DEVKIT_VERSION` (template, `init-workspace.sh`, `release.yml`, `devc-upgrade`) — #971 ✅ **merged**
- [x] **PR 2** — image ref → `ghcr.io/vig-os/devkit` + flake-attr rename (`devkitImage*`) — #973 merged; **image-ref portion reverted by #974** (flake attrs `devkitImage*` kept)
- [x] **PR 2b** — smoke-test dispatch targets → `vig-os/devkit-smoke-test` (release/promote workflows) — #972 *(in review)*

> **Scope adjustments (from execution):** the flake **attribute** rename moved from
> PR 3 into **PR 2** (same workflow files, shared nix-build verification). Repo-URL
> and image-ref **doc** canonicalization deferred out of PR 4 to Stage 3 / PR 2
> (flipping them early 404s until the repo rename). PR 4 also caught a missed pin
> **reader** — `devc-upgrade`'s `awk` — now dual-keyed in PR 5.

#### Stage 2 — Release train → devkit 1.0.0 (human-gated dispatches)
- [x] `just prepare-release 1.0.0` ✅
- [x] `just publish-candidate 1.0.0` → 1.0.0-rc1 green ✅
- [x] ready + approved (#975) → `just finalize-release 1.0.0` ✅
- [x] Downstream gate: `devkit-smoke-test` published final 1.0.0 (after 1 retry of a transient sync-issues timeout) ✅
- [x] `just promote-release 1.0.0` ✅ — :latest, Release undrafted, #975 merged to main

#### Stage 3 — Rename source repo (one-way; after promote)
- [x] Renamed `vig-os/devcontainer` → `vig-os/devkit`; remotes updated; Stage-3 PR **#979** (cosign identity + OCI label + source-repo URLs) ✅
- [x] Lockstep PR **#235** in `devkit-smoke-test` (install URL, notify target, self/source refs) ✅
- [x] Triggers: scheduled Security Scan verified `active` post-rename (fully re-registers on #979 merge to main)

#### Stage 4 — Consumer rollout & close-out
- [ ] Re-scaffold active consumers (`install.sh --force`): vault, talys, hyrr, cad2gdml, scitadel, …
- [ ] Announce 1.0.0 as the rename boundary (old package frozen at 0.5.1)
- [ ] First green scheduled vulnix nightly on `main` under the new package → **close this issue**

---

*Working scratch copy of the full plan (verification steps, per-file line refs, testing/reporting
strategy) is maintained alongside the executor; canonical status is this issue + its comments.*

---

# [Comment #1]() by [c-vigo]()

_Posted on July 10, 2026 at 10:56 AM_

## 📌 Plan approved — starting Stage 1 (2026-07-10)

`0.5.1` has landed, so the rename cycle is now unblocked. The plan-of-record (decisions +
stage checklist) is in the issue body above; this comment thread will carry the dated status
timeline, one entry per stage boundary — mirroring how #639 tracked the cutover.

**Now:** beginning **Stage 1 · PR 1 — dual-key version parser**, the load-bearing first slice.
It makes `.vig-os` resolution accept `DEVKIT_VERSION` (preferred) with a legacy
`DEVCONTAINER_VERSION` fallback, so every later rename step is non-breaking for consumers.
TDD: failing test for dual-key precedence + legacy fallback first, then the minimal parser
change across the three sites (`resolve-image` action, `install.sh`, scaffolder writeback).

Stages 0/2/3 (GHCR bootstrap, release dispatches, repo renames) are human-gated and will be
driven separately; Stage 1 code PRs land on `dev` under `Refs: #781`.


---

# [Comment #2]() by [c-vigo]()

_Posted on July 10, 2026 at 11:36 AM_

## 📋 Concrete plan — PR 2 (image-ref cutover + flake-attr rename)

Posting the executable plan for the last, most-coupled Stage-1 slice. PRs 1/3/4/5 handle
the pin key, package identity, and hardening; **PR 2 flips the image itself** to
`ghcr.io/vig-os/devkit` and renames the flake attributes.

### The chicken-and-egg, and how it's resolved

After #971, the repo pins `DEVKIT_VERSION=0.5.1`. Flipping the ref to `ghcr.io/vig-os/devkit`
means anything that *pulls the pinned tag* wants `ghcr.io/vig-os/devkit:0.5.1`, which won't
exist (0.5.1 lives on the old package).

- **The repo's own PR CI is safe as-is.** `ci.yml` is *build-and-use*: the `build-image`
  job builds `.#devkitImage` locally and `test-image` / `project-checks` consume the built
  artifact — **no registry pull of the pinned tag**. So PR 2's checks go green without the
  new package existing.
- **What still needs the package:** the `resolve-image` **validate** step (`docker manifest
  inspect`) and the scheduled/dispatch workflows that run it after merge (`sync-main-to-dev`,
  `sync-issues`, `renovate-changelog-build`), plus real consumers pinned to the new ref.

**Resolution — seed the new package at Stage 0 (recommended).** One-time, before PR 2 merges:
```
docker buildx imagetools create --tag ghcr.io/vig-os/devkit:0.5.1  ghcr.io/vig-os/devcontainer:0.5.1
docker buildx imagetools create --tag ghcr.io/vig-os/devkit:latest ghcr.io/vig-os/devcontainer:latest
```
This copies the existing multi-arch manifest so `devkit:0.5.1`/`:latest` are immediately
pullable — the ref swap becomes **gap-free** and the rollback lever (pin `0.5.1`) works on
both packages. 1.0.0 is still the first *native* devkit release; 0.5.1 is a continuity seed.
*(Alternative if we want the package to start clean at 1.0.0: land PR 2 last and merge it
into the release train so `devkit:1.0.0-rc` is the first tag the pinned ref resolves — more
ordering-fragile; seeding is preferred.)*

### Edit inventory

**A. Flake attribute rename** (`devcontainerImage`→`devkitImage`, `devcontainerImageEnv`→
`devkitImageEnv`, `devcontainer-bootstrap`→`devkit-bootstrap`) — CI-safe (local builds):
- `flake.nix` — attr defs (~796, ~1152) + `runCommand` name (~845) + comments.
- Call sites: `.github/workflows/nix-image.yml:104`, `.github/actions/build-image/action.yml:56,121`,
  `.github/workflows/security-scan.yml:92,145`, `.github/workflows/release.yml:875`,
  `justfile:56,94,95`.
- **Test anchors** (TDD RED→GREEN): `tests/test_flake_services.py:175-176` asserts the exposed
  attr set; `tests/test_workflow_cachix.py:99` asserts the pushed closure name. Flip both.

**B. Image ref `ghcr.io/vig-os/devcontainer` → `ghcr.io/vig-os/devkit`** — single flake source
+ ~10 duplicated literals:
- `flake.nix:1033` (image `name`) + OCI source label (~1138).
- Actions/workflows: `resolve-image/action.yml:81` (both root + `assets/workspace/` copies),
  `build-image/action.yml`, `nix-image.yml:58`, `release.yml` (REPO literals ~1058/1091/1115/1171),
  `promote-release.yml:114,147,329`, `security-scan.yml`, `sync-*`, `renovate-changelog-build.yml`.
- Tooling/tests: `justfile:10`, `justfile.gh:108`, `justfile.podman` filters, `install.sh:33`,
  `tests/docker-compose.test.yml`, `tests/test_integration.py:553` (+ resolve-image validate text).
- **Scaffold template** (`assets/workspace/`): `docker-compose.yml:4`, `.github/workflows/*.yml`
  image refs, `resolve-image/action.yml:81`, `flake.nix` input URL — *these ship to consumers,*
  so this is where the compose `.env`/`${DEVCONTAINER_VERSION}` **interpolation var** can finally
  rename too (deferred from #971), since the compose file and its writer move together here.
- **Docs image refs** (`podman pull ghcr.io/vig-os/devkit…`): `docs/templates/README.md.j2`,
  `docs/*.md`. (Repo *URL* canonicalization still waits for Stage 3.)

**C. Verify, don't assume — cosign identity.** `promote-release.yml`'s
`--certificate-identity-regexp` encodes the **workflow OIDC identity** (repo-path-based). If it
includes `vig-os/devcontainer`, it flips at the **Stage 3 repo rename**, *not* here; if it only
matches `…/release.yml@refs/heads/release/`, it's repo-agnostic. Confirm before touching.

### Sequencing & testing

1. **Stage 0 prerequisite:** bootstrap `ghcr.io/vig-os/devkit` (public, repo-linked, Actions
   r/w + package Admin) and seed `:0.5.1`/`:latest` (above).
2. Branch `feature/781-image-ref-cutover` off `dev`. Two commits: (A) flake-attr rename, (B) ref flip.
3. **Tests:** `nix build .#devkitImage` + `.#devkitImageEnv` build locally; `just test`
   (flake-services/cachix attr assertions flipped, RED→GREEN); `nix flake check ./assets/workspace
   --override-input vigos "path:$PWD"`; `just precommit` full suite green.
4. **Post-merge smoke:** confirm the scheduled `resolve-image` workflows resolve `devkit:0.5.1`
   against the seeded package (green), and `docker pull ghcr.io/vig-os/devkit:latest` works.
5. **Reporting:** status comment here on merge; the nightly `security-scan` vulnix run should go
   green against `.#devkitImageEnv` on `dev`.

**Not in PR 2:** repo-URL doc canonicalization + smoke-test dispatch targets (PR 2b) + the actual
repo renames — those are Stage 3. PR 2 is purely the image/attr identity.


---

# [Comment #3]() by [c-vigo]()

_Posted on July 10, 2026 at 12:31 PM_

## 🔧 Stage 0 partially done + PR 2b up (2026-07-10)

- **Smoke-test repo renamed** `vig-os/devcontainer-smoke-test` → **`vig-os/devkit-smoke-test`** ✅
  (old name redirects; `Repository Dispatch Listener` verified `active` post-rename; sibling
  clone's remote updated). A real test dispatch is deferred to the 1.0.0 candidate since it runs
  the full downstream cycle.
- **#972** (`ci(release)`) — release/promote dispatch targets, scoped app tokens, downstream gate,
  the `assets/smoke-test/` mirror, and release docs now point at `devkit-smoke-test`. *In review.*
- **Still needs a human** — the GHCR seed requires a `write:packages` token (the automation token
  only has `admin:org`/`repo`/`workflow`):
  ```
  gh auth refresh -h github.com -s write:packages
  gh auth token | docker login ghcr.io -u c-vigo --password-stdin
  docker buildx imagetools create --tag ghcr.io/vig-os/devkit:0.5.1  ghcr.io/vig-os/devcontainer:0.5.1
  docker buildx imagetools create --tag ghcr.io/vig-os/devkit:latest ghcr.io/vig-os/devcontainer:latest
  ```
  then set the package **Public** + link + Actions access. Once seeded, **PR 2** (image ref +
  flake-attr rename) can go — it's the last Stage-1 slice.


---

# [Comment #4]() by [c-vigo]()

_Posted on July 10, 2026 at 01:08 PM_

## ✅ Stage 0 complete + Stage 1 code fully authored (2026-07-10)

**Stage 0 (bootstrap) — done:**
- `ghcr.io/vig-os/devkit` seeded (`0.5.1` + `latest`, multi-arch), **public**, `devcontainer` repo has package Admin.
- Smoke-test repo renamed → `vig-os/devkit-smoke-test`; RELEASE_APP install verified.

**Stage 1 (code rename) — all six PRs authored:** #968, #969, #970, #971, #972 merged; **#973** (image-ref cutover + flake-attr rename) in review — the final slice.

Once #973 merges, `dev` fully speaks devkit (pin key, image ref, flake attrs, dispatch targets), with the old package/repo names deliberately retained only where they must follow the **Stage 3** repository rename (OCI source label, cosign identity, source-repo URLs) or are immutable history.

**Next: Stage 2 — the `1.0.0` release train** (human-gated): `just prepare-release 1.0.0` → `publish-candidate` → `finalize-release` → downstream gate → `promote-release`. This is where the first *native* `devkit:1.0.0` image is built, signed, and published.


---

# [Comment #5]() by [c-vigo]()

_Posted on July 10, 2026 at 01:46 PM_

## ✅ Stage 1 complete — `dev` fully speaks devkit (2026-07-10)

#973 merged. All six Stage-1 PRs (#968/#969/#970/#971/#972/#973) are in `dev`, which now uses the renamed identity end-to-end:

- **Pin key** `DEVKIT_VERSION` (readers accept legacy `DEVCONTAINER_VERSION`)
- **Image** `ghcr.io/vig-os/devkit` (old package frozen at `0.5.1`, still pullable)
- **Flake attrs** `devkitImage` / `devkitImageEnv`
- **Dispatch targets** `vig-os/devkit-smoke-test`
- **Package identity** (`pyproject`/`package.json`) + curl `-L` hardening

Deliberately still on the old names until **Stage 3** (repo rename): OCI `source` label, cosign identity-regexp, source-repo URLs — plus immutable CHANGELOG/ADR history and the `MIGRATION.md` "old package remains pullable" note. The docker-compose `${DEVCONTAINER_VERSION}` interpolation var is a deferred cosmetic cleanup.

**Next → Stage 2: the `1.0.0` release train** (human-gated): `just prepare-release 1.0.0` → `publish-candidate` (iterate to green incl. the blocking vulnix gate) → `finalize-release` → downstream gate on `devkit-smoke-test` → `promote-release`. This builds/signs/publishes the first **native `devkit:1.0.0`**.


---

# [Comment #6]() by [c-vigo]()

_Posted on July 10, 2026 at 02:07 PM_

## 🔄 Course-correction: image keeps the name `ghcr.io/vig-os/devcontainer` (2026-07-10)

Revisited the package-rename decision. **The project/repository becomes `devkit`, but the published container image stays `ghcr.io/vig-os/devcontainer`.** The artifact *is* a dev container; `devkit` names the project/repo that builds and ships it (image + installer + scaffold + flake templates). Repo-name ≠ artifact-name, and keeping the descriptive image name means:

- **Consumers never change their image ref** — no new GHCR package, no `--force` re-scaffold to move registries, no two-package / "frozen old package" complexity.
- The `${DEVCONTAINER_VERSION}` compose var is now **consistent by default** (no rename needed).
- **1.0.0's breaking surface shrinks** to soft-only changes (pin key `DEVKIT_VERSION` with legacy fallback; `install.sh` source URL on re-scaffold). Still a fair "declare the contract stable" milestone.

**#974** reverts the image-ref flip from #973 while **keeping** the internal `devkitImage`/`devkitImageEnv` flake attrs and the `DEVKIT_VERSION` pin key. `nix eval .#devkitImage.imageName` → `ghcr.io/vig-os/devcontainer`.

**Still devkit:** repo (Stage 3), `pyproject`/`package.json`, `DEVKIT_*` manifest keys, installer branding, `devkit-smoke-test` dispatch targets.

**Cleanup:** the seeded `ghcr.io/vig-os/devkit` package is now unused → delete it. Stage 0 seeding turned out unnecessary (the `devcontainer` package already has every tag).


---

# [Comment #7]() by [c-vigo]()

_Posted on July 10, 2026 at 04:08 PM_

## 🎉 devkit 1.0.0 released (2026-07-10)

Stage 2 complete. `1.0.0` is published and on `main`:
- `ghcr.io/vig-os/devcontainer:1.0.0` (multi-arch) + `:latest` → 1.0.0 (digests match), cosign/SLSA/SBOM attested.
- GitHub Release `1.0.0` published (undrafted); **PR #975 merged to `main`**; RC artifacts pruned.
- Downstream `devkit-smoke-test` published its final 1.0.0 Release (the promote gate).

**One transient hiccup, auto-recovered:** the downstream final cycle first failed when that repo's `sync-issues` spiked to 441s (vs its normal 60–80s) and overran the ~2min wait; a single re-dispatch passed cleanly. No config change needed (#977 closed).

**The corrected model shipped and is validated end-to-end:** image name unchanged (`ghcr.io/vig-os/devcontainer`), `DEVKIT_VERSION` pin (legacy accepted), `devkitImage` flake attr, dispatch to the renamed `devkit-smoke-test`.

### Next — Stage 3 (repository rename), human-gated, do now that promote is done:
1. Rename `vig-os/devcontainer` → `vig-os/devkit`; update remotes.
2. PR: flip cosign `--certificate-identity-regexp` + OCI `source` label → `…/devkit` + canonicalize source-repo doc URLs. **Must merge before the next release (1.0.1+)**, else its promote cosign-verify breaks.
3. Lockstep PR in `devkit-smoke-test`: flip its source-repo back-refs (install.sh raw URL, notify-failure) — the moment the source repo is renamed.
4. Re-register triggers; verify scheduled `security-scan.yml` cron is enabled.
Then Stage 4: announce; consumers re-scaffold at leisure (no image migration); close this issue after the first green scheduled vulnix nightly on `main`.


---

# [Comment #8]() by [c-vigo]()

_Posted on July 10, 2026 at 10:58 PM_

## 🔤 Stage 3 — repository renamed (2026-07-11)

`vig-os/devcontainer` → **`vig-os/devkit`** and `vig-os/devcontainer-smoke-test` → **`vig-os/devkit-smoke-test`** (done; GitHub redirects old URLs; local remotes updated; scheduled Security Scan verified `active`).

- **#979** (source repo) — flips all source-repo references to `vig-os/devkit`: clone/raw/API URLs, install one-liners, `devc-upgrade`, docs, **cosign `--certificate-identity-regexp`**, and the image **OCI `source` label**. ⚠️ Must merge **before the next release (1.0.1+)** or its promote cosign-verify fails.
- **#235** (`devkit-smoke-test`) — lockstep: flips its back-refs (dispatch `INSTALL_URL`, `notify-failure --repo`, version-check API, self/source links).

**Image name deliberately unchanged** — `ghcr.io/vig-os/devcontainer` (no `ghcr.io` ref touched in either PR). Immutable released CHANGELOG + `docs/issues`/`docs/pull-requests` archives keep old links (redirect).

### Remaining
- Merge #979 + #235. After #979 lands on `main`, re-confirm the scheduled Security Scan shows a next run.
- **Stage 4:** announce; consumers re-scaffold at leisure (no image migration); close this issue after the first green scheduled vulnix nightly on `main` under the renamed repo.


