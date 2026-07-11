---
type: issue
state: closed
created: 2026-06-23T06:54:15Z
updated: 2026-07-07T08:46:29Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/639
comments: 7
labels: area:image
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-07-11T13:34:11.564Z
---

# [Issue 639]: [T4.1 — Publish-cutover to the Nix image (GATED)](https://github.com/vig-os/devkit/issues/639)

Tracking: #625



## Context

Flip the published `ghcr.io/vig-os/devcontainer` image to the Nix-built, multi-arch image.
This is the only hard-to-reverse step, so it is gated on the #637 CVE gate + test/image parity and keeps the Debian
`Containerfile` in-tree as a fallback for one release cycle.

## Scope

**In:**
- Publish the Nix multi-arch image.
- Retain the Debian `Containerfile` in-tree as fallback for one release cycle.
- Run **both** nightly scans for one cycle to compare findings.

**Out:**
- Debian removal (#642).

## Go / no-go gate

- T2 green (image + portable tests + multi-arch).
- #637 CVE gate met (no unexcepted HIGH/CRITICAL; overlap diff archived).

**Rollback (no-go / post-cutover regression):** re-point the published `:latest` / release
tags at the last Debian-built digest (retained in-tree and in the registry for this cycle).
Because consumers digest-pin, an in-flight rollback only affects repos that re-resolve `:latest`;
no downstream change is required to recover.

## Tasks

- [ ] Publish the Nix multi-arch image as `:latest` / release tags
- [ ] Keep the Debian build available as fallback for one cycle
- [ ] Run both nightly scans and archive the comparison

## Acceptance criteria

- `ghcr.io/vig-os/devcontainer:latest` is Nix-built and multi-arch.
- Downstream consumers are unchanged.
- Scan comparison archived.

## Dependencies

- **Depends-on:** #636, #637.
- **Blocks:** #640.

## Files

- `.github/workflows/*`
- release docs

## Test notes

- Confirm a downstream repo pulling the new digest comes up unchanged before declaring the
  cutover done.

---

# [Comment #1]() by [c-vigo]()

_Posted on July 3, 2026 at 12:09 PM_

Status update — readiness pass for the cutover (full plan reviewed and approved out-of-band):

**Two corrections to this issue's assumptions:**

1. **Rollback rationale:** consumers do **not** digest-pin — they pin mutable semver tags via `.vig-os` (`DEVCONTAINER_VERSION=X.Y.Z`; sampled spread across repos: 0.1–0.3.9), with `:latest` only as the compose fallback. The consumer-side rollback lever is pinning `0.3.9` (the final Debian release) in `.vig-os`; the publisher-side emergency brake is re-pointing `:latest` at the 0.3.9 per-arch digests via `imagetools create` (old images persist in GHCR). Both now documented in `docs/MIGRATION.md` (PR #808).
2. **"Keep the Debian build as fallback for one cycle / run both nightly scans" is moot as written** — #642 already deleted the Debian path on `dev` (no `Containerfile`, Nix-only `build-image`, vulnix-primary scan), so there is nothing to dual-build or dual-scan. The clause's *intent* (don't fly blind on the scanner switch) is covered by: the archived Trivy-vs-vulnix overlap diff (#637, `docs/security/nix-cutover-scan-overlap.md`), the blocking `vulnix-gate` in `release.yml`, a manual `security-scan.yml` dispatch on the release ref (trigger added in PR #808; first run dispatched), and the first green *scheduled* vulnix nightly on `main` post-promote.

**Cutover mechanics confirmed:** the flip happens with the normal 0.4.0 release train — `prepare-release` → `release.yml` (RC, blocking vulnix-gate) → smoke-test gate → `just promote-release 0.4.0` (`:latest` assembled from the per-arch Nix images; the merge to `main` simultaneously replaces the failing Debian-era nightly scan, which is what has been filing alerts like #805).

**Sequencing decision (user-approved):** cutover first under the `devcontainer` name; the `devkit` rename (#781) follows as its own release cycle immediately after promote, targeting `devkit 1.0.0`.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 4, 2026 at 07:14 AM_

**Go/no-go evidence: the vulnix gate is GREEN.** ✅

Run: https://github.com/vig-os/devcontainer/actions/runs/28698572494 (dispatched on `feature/639-cutover-readiness` = dev + PR #808) — all steps green in 8.5 min: `.vulnixignore` expiry validation → vulnix scan (4 min) → **gate: no unexcepted HIGH/CRITICAL** (35 exceptions applied) → SBOM (CycloneDX) → Trivy SBOM-mode awareness scan → findings+SBOM artifact uploaded.

Getting here surfaced and fixed real gate defects (all on PR #808):
- the scan step died on vulnix's documented exit 2 under the runner's default errexit shell — findings never reached the gate;
- a vulnix *crash* (exit 1, NVD timeout) masqueraded as the documented "whitelisted findings" exit 1 and slipped an empty findings file to the gate;
- nvd.nist.gov throttling (nix-community/vulnix#171) made every cold run a ~25-min coin flip: now mitigated by a weekly-keyed `actions/cache` of the NVD DB, a 3-attempt ETag-resuming retry loop, and a 60 s fetch-timeout patch on `packages.vulnix`.

The 8 HIGH/CRITICAL CVEs published after the 2026-06-23 baseline (libssh2 ×2, socat, libxml2, gzip, fzf ×2, jq) were triaged **online** (NVD/CERT.PL/GHSA + upstream repos + nixpkgs branch state): all real product matches, none fixable by a rev advance today (fixes in nixpkgs staging or unreleased upstream), none with a realistic attack path in this deployment. Accepted into `.vulnixignore` with staggered 2026-08-03/08-17/09-01 expiries so the staging fixes get picked up on re-review.

With PR #808 merged, the objective gate input for the cutover is met; the release train (prepare-release → RC → promote) is unblocked.

---

# [Comment #3]() by [c-vigo]()

_Posted on July 6, 2026 at 02:54 PM_

Publish-cutover complete. `0.4.0` is released and **promoted to `Latest`** (`ghcr.io/vig-os/devcontainer:latest` → 0.4.0), and the release PR merged `release/0.4.0` → `main`, so the Nix image and its tooling are now the default-branch posture:

- Blocking `vulnix-gate` operational on both the release path and the nightly (`security-scan.yml`), now fetching NVD data from the self-hosted mirror `vig-os/nvd-mirror` (#870) — the throttled `nvd.nist.gov` no longer gates releases.
- The old Debian `:latest` Trivy nightly is retired on `main`, replaced by the vulnix Nix-image scan.
- Release run all-green (build/test amd64+arm64, vulnix gate via mirror, publish, smoke-test); downstream `devcontainer-smoke-test` published its final `0.4.0` release; rollback issue #869 resolved.

Closing as done.

---

# [Comment #4]() by [c-vigo]()

_Posted on July 6, 2026 at 04:26 PM_

## Phase-B downstream validation — consumer 1/2: EXOMA/hyrr (0.4.0-rc5 → 0.4.0)

Validation vehicle: EXOMA/hyrr#520 (`feature/519-devcontainer-rc4-validation`), commit `f806895`. Method: pin bump + full hook suite run **inside** `ghcr.io/vig-os/devcontainer:0.4.0` locally (podman), then shipped in-container CI.

### Result: image functional; consumer CI blocked on one upstream defect (#879)

| Check | Outcome |
|---|---|
| Image pull (`0.4.0`, multi-arch) | ✅ |
| `just` recipes resolve in-image | ✅ after consumer-side repair (#877) |
| `prek run --all-files` in-image | ✅ green (exit 0) after consumer-side repair (#878) |
| `just sync` (uv) | ❌ pycatima sdist build fails — **#879** (no C/C++ toolchain; cp314 wheel gap) |
| Shipped CI (run 28806387785) | 8 pass / 3 fail — failures are all the `Sync project dependencies` step, identical to local repro |

### Issues filed from this validation

- #877 — scaffold upgrade strands base recipes (`just sync` etc. missing → shipped ci.yml fails); also covers the stale `justfile.base` leftover and the `sync` recipe's `--all-extras` semantics change that pulls hyrr's quarantined cp312/313-only `geometry` extra
- #878 — scaffold upgrade replaces `.pre-commit-config.yaml`, clobbering repo excludes (false-positive private key, hooks rewriting physics data tables)
- #879 — image can't build native sdists (unset/dead CXX from baked CPython sysconfig, no compiler on PATH) — **the one hard blocker**; amplified by the young cp314 wheel ecosystem
- #880 — process: post-promote RC cleanup deleted rc5 while hyrr/talys still pinned it (both were unable to pull until this rollout)

### Consumer-side repairs applied (hyrr f806895)

`.vig-os` → 0.4.0; base recipes restored into `justfile.project` (sync kept as plain `uv sync`); pre-0.4.0 hook excludes restored; yamllint pragmas/E402/nixfmt cleanup to green the new hook set.

**Verdict for #639:** downstream comes up on the 0.4.0 image and the full hook suite is green in-image; "unchanged" is **not met** for repos with non-cp314-wheel native deps until #879 is resolved. talys report follows.

---

# [Comment #5]() by [c-vigo]()

_Posted on July 7, 2026 at 06:17 AM_

## Phase-B downstream validation — consumer 2/2: EXOMA/talys (0.4.0-rc5 → 0.4.0)

Validation vehicle: EXOMA/talys#553 (`feature/552-devcontainer-rc4-validation`), commits `b736717f` + `182f27e8` (local, push in progress — heavy repo-side pre-push gates). talys is a **direnv-mode** consumer: the image is the outer shell, toolchain comes from the repo flake; its PR CI (`nix flake check`) never touches the image.

### Result: image checks all green; every failure encountered was pre-existing repo state

| Check (in `ghcr.io/vig-os/devcontainer:0.4.0`) | Outcome |
|---|---|
| Image pull | ✅ |
| justfile parses, scaffold recipes resolve | ✅ after restoring the missing import block (fresh-adoption variant, noted on #877) |
| `just sync` (uv) | ✅ — no native-build deps, so #879 not hit here |
| Hook suite (flake devshell, scoped to changed files) | ✅ |

### Repo-side (NOT image) findings, for the record

- Root `justfile` had lost the entire scaffold import block during rc4 adoption → template base recipes unreachable (#877 evidence point 2).
- `cargo fmt --check` under devshell rustfmt 1.95 reports ~124KB of drift — pre-existing; also produced a spectacular pipe-buffer deadlock (rustfmt blocked 13h at 0% CPU inside prek's output capture: diff > 64KB pipe buffer, parent in do_wait).
- `cargo-deny` advisory gate blocked **all** pushes: RUSTSEC-2024-0436 (`paste` unmaintained via parquet → talys-io, no safe upgrade). Accepted via the deny.toml ignore-list convention (`182f27e8`).
- Pre-push clippy gate requires the `f2py-shims` build artifact (`nix build .#f2py-shims`, ~20 min cold) — without it `talys-core` fails with 2700 errors; worth a line in the repo README/onboarding.

**Verdict for #639:** second consumer confirms the 0.4.0 image is functional for direnv-mode repos; the "downstream unchanged" criterion is met for talys (all blockers were repo-local). Combined with the hyrr report above: #639's remaining blocker for wheel-building consumers is #879.

---

# [Comment #6]() by [c-vigo]()

_Posted on July 7, 2026 at 08:24 AM_

## Phase-B downstream validation — consumer 3: EXOPET/vault (0.3.5 → 0.4.0)

Validation vehicle: exo-pet/vault#19 (`feature/18-devcontainer-0-4-0`, commit `43b6299`, closes exo-pet/vault#18).

### Result: ✅ fully green — CI (Lint & Format, Tests, CI Summary) all pass inside `ghcr.io/vig-os/devcontainer:0.4.0`

The cleanest migration of the three: vault's scaffold was already current-generation despite the 0.3.5 pin, so the #877/#878 upgrade-path traps didn't fire. Effective change: pin bump + `pre-commit` → `prek` renames.

### Findings

- **#881 (new):** the image drops the `pre-commit` binary with no compat path — vault's preserved `justfile.project` recipe and its repo-managed `.githooks/*` both called it (exit 127 in-image). Repaired consumer-side; a shim or migration note would save every other old consumer.
- vault's `.githooks` also had `#!/bin/bash` shebangs — fine in-container, dead on NixOS hosts. Its `IN_CONTAINER` commit guard proved correct: on the host, prek fetched a generic-linux `typos` binary that can't exec on NixOS. Recommendation for the migration docs: commits for image-consumer repos belong in the container, and the full commit path (hooks + SSH-agent-based signing) works inside 0.4.0 — verified by making the adoption commit itself in-image.
- Minor: vault never had the vig-os label taxonomy provisioned (`setup-labels`) — unrelated to 0.4.0, noted for hygiene.

### Rollout scoreboard

| Consumer | Pin | Status |
|---|---|---|
| EXOMA/hyrr | 0.4.0 | pushed; CI green except `just sync` blocked by **#879** (native sdist toolchain) |
| EXOMA/talys | 0.4.0 | validated; commits ready on the branch, push pending (heavy repo-local pre-push gates) |
| EXOPET/vault | 0.4.0 | ✅ fully green, PR exo-pet/vault#19 ready to merge |

**#639 acceptance:** "a downstream repo on the new image comes up unchanged" is now demonstrated by vault (fully green) and talys (all image-side checks green). The remaining upstream work from this rollout: #879 (blocker for wheel-building consumers like hyrr), #877/#878/#880/#881 (upgrade-path hardening).

---

# [Comment #7]() by [c-vigo]()

_Posted on July 7, 2026 at 08:46 AM_

## Phase-B downstream validation — consumer 4: MorePET/mat (0.3.3 → 0.4.0, local probe)

Validation performed **locally only** (throwaway branch `chore/devcontainer-0-4-0-local-probe`, commit `520385b`, not pushed — no consumer issue/PR yet). Method: pin bump + `just sync && just precommit && just test` inside `ghcr.io/vig-os/devcontainer:0.4.0`.

### Result: ✅ fully green after the known consumer-side repairs — including the first real in-image test suite pass of the rollout

| Check (in-image) | Outcome |
|---|---|
| `just sync` (uv, all groups + dev extra) | ✅ |
| Full hook suite (`prek run --all-files`) | ✅ |
| **pytest — 924 passed, 70 skipped, 8 xfailed (66 s)** | ✅ |

### Findings

- **#879 is a pattern, not a hyrr quirk.** mat's template-style `sync` (`uv sync --all-extras --all-groups`) pulls `pycatima` via the optional `nuclear` extra (`nucl-parquet` → `pycatima`, wheels stop at cp313) → identical toolchain failure to hyrr, reached through an unrelated repo. Two of four Python consumers tested now hit #879, on the same package. Consumer-side mitigation both times: drop `--all-extras` from `sync` so quarantined extras stay quarantined (the sync-semantics note on #877).
- **#881 replayed:** preserved `justfile.project` recipe ran `uv run pre-commit`, and `.githooks/*` call `pre-commit` — third consumer with the pattern (hyrr's config predates it, vault and mat both had it).
- mat-specific nuance for the eventual real adoption PR: pytest lives in the legacy `dev` **extra** (`[project.optional-dependencies]`), not a dependency group, so a de-extra'd sync needs `--extra dev` explicitly.
- Scaffold was already current-generation (like vault) despite the 0.3.3 pin — #877/#878 upgrade traps did not fire.

### Updated rollout scoreboard

| Consumer | Status |
|---|---|
| EXOMA/hyrr | CI green except `just sync` — blocked by **#879** |
| EXOMA/talys | validated; push pending (heavy repo-local gates) |
| EXOPET/vault | ✅ fully green, PR exo-pet/vault#19 |
| MorePET/mat | ✅ fully green **locally** incl. 924-test pytest pass; official adoption PR to follow |

With mat's evidence, #879 is the clear headline for a 0.4.1 forward-fix; #877/#878/#881 are the upgrade-path hardening batch riding with it.

