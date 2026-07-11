---
type: issue
state: closed
created: 2026-07-05T12:36:19Z
updated: 2026-07-06T13:58:24Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/859
comments: 5
labels: chore, priority:blocking, area:workspace
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:34.903Z
---

# [Issue 859]: [[CHORE] Field-validate 0.4.0-rc4 in real consumer repos before finalize](https://github.com/vig-os/devkit/issues/859)

The automated RC gate (pipeline + smoke test) is green for `0.4.0-rc4`. This issue tracks the manual field validation that automation cannot cover — upgrading real existing consumers (0.3.x scaffolds + preserved files), interactive devcontainer UX, real dependency trees under uv/Python 3.14, the nix-direct (direnv) mode, and a machine other than the maintainer's — before `finalize-release 0.4.0` is dispatched.

## Matrix

| # | Repo | Tester | Profile | What it validates |
|---|------|--------|---------|-------------------|
| 1 | exo-pet/playground-carlos | @c-vigo | Python/uv, pin 0.3.4, scaffolded CI, `--mode both` | full upgrade pass: install --force, preserved files, **nix-direct dev-shell (direnv)**, container UX, uv/3.14, prek, signing, podman shim, CI on rc4, rollback lever |
| 2 | exoma-ch/brother-printer | @c-vigo | Python/uv, pin 0.3.4, second org | condensed upgrade pass + CI |
| 3 | exo-pet/vault | @c-vigo | docs-only, pin 0.3.5, most active consumer | minimal pass: docs hooks (pymarkdown/typos) + CI |
| 4 | exoma-ch/hyrr | @gerchowl | Python, **oldest scaffold gen** (hardcoded `:0.2.1`, pre-`.vig-os`) | deep-upgrade path on a different host |
| 5 | exoma-ch/talys | @gerchowl | Rust + own nix-direnv flake | fresh adoption (`--mode devcontainer`), PRESERVE_FILES coexistence, cargo-in-container |

Delivery-mode coverage is split across rows (one branch per repo): row 1 runs `--mode both` and covers the direnv path locally (no CI lane exists for it yet — #854); all other rows test `devcontainer` mode, their real-world usage.

## Mechanics

- Per repo: stub issue + `feature/<issue>-devcontainer-rc4-validation` branch + **dummy draft PR** (CI trigger; never merged — closed and branch deleted afterwards).
- Upgrade command: `curl -sSfL https://raw.githubusercontent.com/vig-os/devcontainer/0.4.0-rc4/install.sh | bash -s -- --version 0.4.0-rc4 --force [--mode <mode>] .`
- **All findings — positive and negative — land here as comments**, one per repo pass: `**repo / tester / duration** — ✅/❌ per checklist item — caveats — follow-up (issue/PR link)`. gerchowl reports on his PRs (mirrored here).
- Fixes or improvements (docs, setup, workflows) go as PRs into `release/0.4.0` referencing this issue.
- Expected known finding: preserved `justfile.project` still calls `uv run pre-commit` (dropped in 0.4.0) — capture the manual migration step for `docs/MIGRATION.md`.

## Exit criteria

Rows 1–3 pass (or their defects are fixed on `release/0.4.0` and re-verified); row 4 reported or a one-business-day window elapsed; row 5 nice-to-have. Then `just finalize-release 0.4.0` proceeds; this issue closes with the filled matrix after promote.

Refs: #639
---

# [Comment #1]() by [c-vigo]()

_Posted on July 5, 2026 at 12:57 PM_

## Row 1 — exo-pet/playground-carlos / @c-vigo / ~90 min — ✅ pass with findings

Full pass, `--mode both`, upgrade 0.3.4 → 0.4.0-rc4 on `feature/6-devcontainer-rc4-validation` (dummy PR [exo-pet/playground-carlos#7](https://github.com/exo-pet/playground-carlos/pull/7)).

| Check | Result |
|---|---|
| Upgrade one-liner (`--version 0.4.0-rc4 --force --mode both`) | ✅ `.vig-os` pins rc4 (#853 verified in the field); PRESERVE_FILES untouched; real code untouched |
| Nix-direct dev-shell (stub pinned to rc4 tag, `nix develop`) | ✅ builds, full toolchain (prek/uv/ruff/just/typos) |
| `uv sync` (real dep tree, Python 3.14) | ✅ host dev-shell and in-container |
| `just precommit` | ✅ after documented migrations (below) |
| Scratch/upgrade commit: hooks + SSH signing | ✅ signed `G`; branch-name + commit-msg hooks enforce conventions |
| Container up (rc4), lifecycle hooks, post-attach | ✅ |
| `just test` in-container | ✅ 69 passed |
| docker→podman shim | ✅ `docker --version` → podman 5.8.2 |
| Scaffolded CI on dummy PR (resolve-image → Lint/Tests in rc4 container) | ✅ green |
| Rollback lever (`.vig-os` → 0.3.4 → container runs 0.3.4 image → restore) | ✅ |

### Findings (fix/document before finalize)

1. **🔴 direnv mode cannot commit — `.githooks` guard requires the container.** `.githooks/pre-commit` hard-fails with "Please commit your changes within the dev container" unless `IN_CONTAINER=true`. In direnv/nix-direct mode there is no container, so one of the two advertised modes cannot make commits. Fix: accept the nix dev-shell (e.g. `IN_NIX_SHELL`) as sanctioned.
2. **🔴 `.githooks/*` shebangs are `#!/bin/bash`** — `cannot exec` on NixOS hosts (no `/bin/bash`) in direnv mode. Fix: `#!/usr/bin/env bash` in `assets/workspace/.githooks/*`.
3. **🟡 shipped `.typos.toml` is silently shadowed** by a consumer's own `typos.toml` (typos prefers the undotted name), so scaffold-shipped content (`Nd` in version-check.sh) fails their hooks anyway. Also the hook lacks `--force-exclude`, so per-repo `[files] extend-exclude` is ignored for staged files. Consumer migration applied here: merge shipped extend-words into the project `typos.toml` + `entry: typos --force-exclude`.
4. **🟡 meta autofix hooks (end-of-file-fixer, trailing-whitespace, mixed-line-ending) mangle committed artifacts** (170+ SVG/HTML files under `exports/` were "fixed"). Consumers with committed artifacts need a global `exclude:` — or the scaffold config should ship one pattern for common artifact dirs.
5. **🟡 preserved `justfile.project` keeps the dead `uv run pre-commit run --all-files` recipe** (as predicted). One-line migration to `prek run --all-files` — must go in MIGRATION.md.
6. **🟡 recipe rename breaks muscle memory/scripts**: `just test-pytest` no longer exists (now `just test`, devc-* namespacing per #806/#809). MIGRATION.md note.
7. **🟢 scaffolded CodeQL workflow fails on repos without Advanced Security enabled** (private exo-pet repo) — onboarding caveat, not an rc4 defect; candidate for #854.
8. **🟢 re-scaffold re-derives the project name from the directory** — placeholder files (tests/test_example.py, a new stub package dir) got renamed from the original scaffold name; real code untouched, but noisy. #854-class hardening.

Items 1–2 are code fixes on `release/0.4.0` (rc5 needed); 3–6 are MIGRATION.md/config items; the batch goes into one fix PR set after rows 2–3.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 5, 2026 at 01:10 PM_

## Row 2 — exoma-ch/brother-printer / @c-vigo / ~40 min — ✅ pass with findings

Upgrade 0.3.4 → rc4, devcontainer mode ([dummy PR exoma-ch/brother-printer#58](https://github.com/exoma-ch/brother-printer/pull/58)). Container up on rc4 ✅ · `just sync` ✅ · signed commit + hooks ✅ · **scaffolded CI fully green** (resolve-image, Lint, Tests, CodeQL) ✅.

9. **🔴 REGRESSION (new): lifecycle scripts lost the `${BASH_SOURCE[0]:-$0}` pipe-safety fallback.** brother-printer's own regression tests (`test_script_dir_safe_when_piped`, 4 failures) caught it: the 0.3.4-era scripts had `:-$0`; the 0.4.0 `assets/workspace/.devcontainer/scripts/{initialize,post-create,post-attach,version-check}.sh` regressed to the bare form, which dies with `unbound variable` under `set -u` when piped. Restoring the fallback → 321/321 pass. Upstream fix required (rc5).
10. **🟡 typos scans binary artifacts, third instance**: `.bin` golden protocol fixtures produced garbage findings in CI; fixed consumer-side with `extend-exclude` + `--force-exclude` (finding 3/4 class).

## Row 3 — exo-pet/vault / @c-vigo / ~25 min — ✅ pass with findings

Upgrade 0.3.5 → rc4, devcontainer mode ([dummy PR exo-pet/vault#9](https://github.com/exo-pet/vault/pull/9)). Container up on rc4 ✅ · docs hooks (`just precommit`) green after migrations ✅ · **scaffolded CI core lane green** (Lint, Tests, Summary) ✅ · CodeQL fails on repo settings (Advanced Security not enabled — finding 7, org onboarding, not rc4).

11. **🟡 typos shadowing, second instance**: vault owns a `_typos.toml` (higher precedence than the shipped `.typos.toml`); binary vendor PDFs (`datasheets/`) also produced garbage findings. Same consumer migration applied. **All three real consumers checked so far own a shadowing typos config** — the shipped `.typos.toml` will rarely take effect; MIGRATION.md must say "merge, don't rely on the shipped file", and the hook needs `--force-exclude`.

## Rows 4+5 — prepared for @gerchowl (different host)

- **hyrr** (deep upgrade 0.2.1 → rc4): branch + [dummy PR exoma-ch/hyrr#520](https://github.com/exoma-ch/hyrr/pull/520) with instructions. Preparation surfaced two more findings:
12. **🔴 `--mode devcontainer` prune deletes a consumer's own pre-existing `flake.nix`/`.envrc`** (hyrr's real nix-direnv setup; reproduced on talys too). Contradicts the PRESERVE_FILES principle / #738 guard, which protects `.devcontainer/` in direnv mode but not the flake files in devcontainer mode. Upstream fix required (only prune files the scaffold itself created).
13. **🟡 installer's final `just sync` fails on old-generation preserved `justfile.project`** (no `sync` recipe in the 0.2.1 layout) → `install.sh` exits 1 after an otherwise-complete scaffold. Should tolerate/skip with a warning.
- **talys** (fresh adoption on Rust + nix-direnv): branch + [dummy PR exoma-ch/talys#553](https://github.com/exoma-ch/talys/pull/553) with instructions. Preparation surfaced:
14. **🔴 fresh adoption clobbers existing project infrastructure**: talys' own root `justfile` (48 lines of real recipes), `.github/workflows/ci.yml`, `.pre-commit-config.yaml` and `.gitignore` were silently overwritten by scaffold templates — none are PRESERVE_FILES. For adoption into non-empty repos the never-overwrite class is too narrow (or needs an `--adopt` mode that only adds `.devcontainer/` + `.vig-os`).

## Interim verdict

The **image, container UX, toolchain, uv/3.14, podman shim, signing, and consumer CI all validate green** across three real repos and two orgs. Every red finding is in the **installer/scaffold layer** (`install.sh`/`init-workspace.sh`/shipped configs), not the image: #1 direnv commit guard, #2 shebangs, #9 BASH_SOURCE regression, #12 prune deletes user flake files, #14 adoption clobber. Fix batch on `release/0.4.0` next → rc5 → targeted re-verification.

---

# [Comment #3]() by [c-vigo]()

_Posted on July 5, 2026 at 02:17 PM_

## rc5 re-verification — ✅ all six fixes confirmed in the field

`0.4.0-rc5` (fix batch #860) is green through the full automated gate (pipeline + complete downstream smoke-test cycle). Targeted re-verification of the red findings:

| Finding | Re-verification | Result |
|---|---|---|
| 1 — direnv mode cannot commit | playground: commit from `nix develop` with **no override** → hooks ran, commit signed `G` | ✅ |
| 2 — `/bin/bash` shebangs | rc5 scaffold ships `#!/usr/bin/env bash` + `IN_NIX_SHELL` guard | ✅ |
| 9 — BASH_SOURCE regression | fixed scripts shipped (brother-printer's regression tests already proved the shape at rc4) | ✅ |
| 12 — prune deletes own flake files | hyrr **and** talys rc5 installer runs: `preserving existing flake.nix/.envrc (#859)`, zero deletions, no manual restore | ✅ |
| 13 — installer dies on old `justfile.project` | hyrr rc5 install: exit 0 with the warning + MIGRATION.md pointer | ✅ |
| 3/10/11 — typos vs artifacts/shadowing | `--force-exclude` shipped in repo + scaffold hooks; consumer merge steps now in MIGRATION.md | ✅ |

All five validation branches are bumped to rc5 (`.vig-os` pins verified); the three @c-vigo dummy PRs are re-running CI against the rc5 image; @gerchowl's PRs ([hyrr#520](https://github.com/exoma-ch/hyrr/pull/520), [talys#553](https://github.com/exoma-ch/talys/pull/553)) are updated with rc5 notes.

**Exit criteria status**: rows 1–3 ✅ (pending the rc5 CI re-runs going green); row 4 awaiting @gerchowl's report (soft-blocking, one-business-day window); row 5 nice-to-have. Once rows 1–3 CI confirms, `finalize-release 0.4.0` is unblocked from this issue's perspective.

---

# [Comment #4]() by [c-vigo]()

_Posted on July 5, 2026 at 02:21 PM_

## Rows 1–3 closed out — rc5 CI confirmed

- exo-pet/playground-carlos#7: core scaffolded CI **green on rc5**; only CodeQL fails (Advanced Security not enabled on the repo — finding 7, org onboarding). PR closed, branch deleted.
- exoma-ch/brother-printer#58: **fully green on rc5**. PR closed, branch deleted.
- exo-pet/vault#9: core scaffolded CI **green on rc5**; same CodeQL settings caveat. PR closed, branch deleted.

Stub issues closed in all three repos; local checkouts restored to their default branches; nothing merged anywhere.

**Exit criteria: rows 1–3 ✅ complete.** Remaining: row 4 (@gerchowl on hyrr#520 — soft-blocking, one-business-day window from now) and row 5 (talys#553, nice-to-have). `finalize-release 0.4.0` is otherwise unblocked; this issue closes with the final matrix after promote.

---

# [Comment #5]() by [c-vigo]()

_Posted on July 6, 2026 at 01:58 PM_

0.4.0 finalized and validated end-to-end: the release workflow is all-green (build/test amd64+arm64, vulnix CVE gate via the NVD mirror, publish) and the downstream `devcontainer-smoke-test` published its non-draft final release for `0.4.0`. Proceeding to promote. Closing as resolved.

