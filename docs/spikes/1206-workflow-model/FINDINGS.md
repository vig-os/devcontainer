<!-- Spike artifact — not a managed file. -->

# Spike #1206 — `DEVKIT_WORKFLOW` (gitflow | trunk) de-risk

Epic #1205. Verdict and evidence for the scaffold-render approach to the
per-consumer workflow-model knob. **No production wiring** was done (that is
#1207/#1208); this is a de-risk plus a red/green test skeleton.

## Verdict: GO

Both de-risked assumptions hold. `trunk` is realizable entirely at scaffold time
as an anchored `dev -> main` rewrite plus one copy-exclude, with no
resolve-toolchain runtime wiring and no workflow twin. Rendered trunk workflows
are `actionlint`-clean, carry zero residual `heads/dev`, and preserve the #991
invariants. The gitflow (default) render is a provable byte-for-byte no-op.

## Artifacts

| File | What it proves |
|------|----------------|
| `simulate_trunk_release.sh` | D1 — trunk release topology (local git sim) |
| `render_workflow_model.sh` | D2 — `render_workflow_model()` prototype *(removed #1208)* |
| `verify_render.sh` | D2 — drives the render + all shape/lint assertions *(removed #1208)* |
| `../../../tests/test_workflow_model.py` | D3 — red/green pytest skeleton |

Run inside the dev shell: `direnv exec . docs/spikes/1206-workflow-model/<script>`.

> **Post-port note (#1208):** `render_workflow_model.sh` and its driver
> `verify_render.sh` have been removed — the render is now the single source of
> truth inside `assets/init-workspace.sh` (`render_workflow_model()`, a sibling
> of `render_codeql_matrix()`), and `tests/test_workflow_model.py` drives the
> real `init-workspace.sh` end-to-end. `simulate_trunk_release.sh` is kept: it
> de-risks the release *topology*, which has no production counterpart to
> supersede it.

## Deliverable 1 — trunk release topology

A release cut from `main` and merged back to `main`, with **no `dev` branch**,
holds. The simulation replays the real workflow core against base `main` using
the actual `prepare-changelog` tool, then asserts: tag `1.0.0` exists and is an
ancestor of `main`; `## Unreleased` is preserved on `main` (#590); no `dev`
branch is ever created; the dated `[1.0.0]` section carries the frozen content;
the fresh `Unreleased` no longer carries it (moved, not copied).

No topology surprise. Two prior-fix behaviors survive the retarget unchanged:

- **#617 advance guard** — the "wait for base to advance past the pre-freeze
  SHA before branching" loop is base-agnostic: it compares two SHAs of the same
  base ref. Retargeting `dev -> main` changes only which ref is read, not the
  comparison. Logic is identical.
- **#590 Unreleased preservation** — the release branch keeps the empty
  `## Unreleased`, so `main` retains it above the dated release. In trunk there
  is no main/dev sync merge to worry about, so the invariant is strictly easier.

`promote-release.yml` already merges `release/* -> main` (`:458-466`) — no change
needed there. Its only `dev` mentions are comments about `sync-main-to-dev`,
which in trunk simply never triggers (the workflow file is excluded, and it
fires on a push to `main`).

## Deliverable 2 — scaffold render prototype

`actionlint` exit 0 on all four rendered workflows
(`prepare-release`/`ci`/`codeql`/`sync-issues`); zero residual `heads/dev`; base
confirmed `main`; #991 invariants intact (no `ghcr.io/vig-os/devcontainer:` pin,
no `resolve-image`, uses `setup-devkit-toolchain`). Gitflow render byte-identical
to the committed template (confirmed by `diff -r`).

All eight `prepare-release.yml` edits are **clean literal swaps**: `ref: dev` x2,
`heads/dev` x4 (both `git/ref/heads/dev` and `refs/heads/dev`), and one
`from dev` step name.

### Where the render is trickier than a blind swap

- **`prepare-release.yml` has `dev`-adjacent tokens that MUST be left alone** —
  the anchoring is load-bearing, not incidental:
  - `/dev/null` (lines ~90/104/108/…) — device paths; a naive `s/dev/main/`
    would corrupt them.
  - `dev_sha:` job output (`:167`) and `DEV_SHA` shell var (`:256`) — behavior
    is unaffected by their name; leaving them avoids churn.
  - cosmetic step names still say dev: `Checkout dev branch` (`:177`), `Capture
    pre-prepare dev SHA` (`:189`), `Commit prepared CHANGELOG to dev via API`
    (`:228`), `Commit CHANGELOG rollback to dev via API` (`:496`), plus the
    `#617` explanatory comments. These are **inert** (only the branch literals
    drive behavior) but a reader may find "Checkout dev branch" checking out
    `main` confusing. **#1208 should decide** whether to also rewrite these
    step-name/comment strings; the locked spec only mandates `ref:`, `heads/dev`,
    and `from dev`, which is what the prototype does.
  Anchors used: `heads/dev\b` (word boundary — cannot hit `heads/development`;
  also protects `devkit`/`devcontainer`), `^\s*ref: dev$` and `from dev$`
  (end-anchored). Verified: no `development`/`devcontainer`/`devkit` token is
  collaterally rewritten anywhere in the tree.
- **`ci.yml` / `codeql.yml`** — the `- dev` deletion is a bare `/^      - dev$/d`.
  In today's templates there is exactly one such line per file (the PR
  `branches:` list). #1208 should scope the delete to the
  `on.pull_request.branches` block if a future template grows a second 6-space
  `- dev` elsewhere.
- **`sync-issues.yml` description** (`:26`, `e.g., dev, release/x.y.z`) is left
  as an illustrative example of a valid arbitrary value; only the `default:`
  (`:28`) and the two `|| 'dev'` fallbacks (`:103`/`:186`) are behavioral and are
  swapped.

## Deliverable 3 — red/green test skeleton

`tests/test_workflow_model.py`: **9 passed, 2 xfailed**. The 9 green tests drive
the prototype `render_workflow_model()` against a copied template tree
(executed-bash style, mirroring `test_ci_runner.py`) and assert the full trunk
shape plus the gitflow byte-identical guard. The 2 `xfail(strict=True)` tests
name the production seams so they stay visible and auto-flip to red when wired:

- **#1207 seam** — `test_vig_os_declares_workflow_key`: `.vig-os` must ship
  `DEVKIT_WORKFLOW=` (manifest key, default gitflow), exactly like the existing
  `DEVKIT_CI_RUNNER=` key. Resolve it in `init-workspace.sh` alongside the other
  `read_manifest_value` calls (`:290-297`).
- **#1208 seam** — `test_init_workspace_invokes_render_workflow_model`: port
  `render_workflow_model()` into `init-workspace.sh` as a sibling of
  `render_codeql_matrix()` (`:857`), invoke it after the rsync copy (near the
  `render_codeql_matrix` call at `:1418`), and add the trunk
  `--exclude=/.github/workflows/sync-main-to-dev.yml` to `EXCLUDE_ARGS`
  (`:1140-1163`) so a trunk workspace never receives the file.

## Notes for the follow-up sub-issues

- The design assumption "every `dev` in `prepare-release.yml` is a plain branch
  literal" is **confirmed** — all eight are literals; the render is an anchored
  retarget, not a structural rewrite.
- `promote-release.yml` needs **no** render (already main-targeted). Only the two
  comment lines mentioning `sync-main-to-dev` are stale in trunk; cosmetic.
- Decide (#1208) the policy on cosmetic `dev` step names / comments in
  `prepare-release.yml` — inert but potentially confusing.
