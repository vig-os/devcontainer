---
type: issue
state: closed
created: 2026-07-17T20:27:20Z
updated: 2026-07-20T10:47:18Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1210
comments: 1
labels: chore, priority:medium, effort:medium, area:testing
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-20T14:51:04.150Z
---

# [Issue 1210]: [workflow-model: tests (test_workflow_model.py + bats + parametrize dev-assuming suites)](https://github.com/vig-os/devkit/issues/1210)

Part of #1205. Test-first alongside sub-2/3; finalize here.

- **New `tests/test_workflow_model.py`**: scaffold a trunk workspace → assert no `sync-main-to-dev.yml`; `prepare-release.yml` forks from main (grep `ref: main`/`heads/main`, **zero residual `heads/dev`**); ci/codeql `on:` filters exclude dev; sync-issues default main; SKILL base main; pre-commit no `(?!dev$)`. Gitflow scaffold asserts the inverse + **byte-identical to today** (default regression guard).
- **New bats** (`tests/bats/init-workspace.bats`): trunk drops sync-main-to-dev.yml; trunk `prepare-release.yml` satisfies the #991 invariants (no ghcr pin, no resolve-image, uses setup-devkit-toolchain); `--force`/`--preview` DELETIONS on gitflow→trunk; contradiction guard refuses `--workflow trunk` vs persisted gitflow. #991 managed-set assertions (:2648-2738) read TEMPLATE_DIR (always gitflow) → unchanged.
- **Parametrize** dev-assuming suites (gitflow rows unchanged): `test_install_script.py:363-380`, `bats/install.bats:296-317`+`:400-456`, `test_workflow_sync_checkout.py`, `test_scaffold_lint.py:280-300`, `test_workflow_prepare_extension.py`, `test_release_core_sync_dispatch.py:48,62`. **Do NOT touch** the `"dev"`-as-image-tag sentinel in `test_utils.py`/`conftest.py`/`docs/generate.py`.

Refs: #1205
---

# [Comment #1]() by [c-vigo]()

_Posted on July 20, 2026 at 10:47 AM_

Implemented via PR #1212, shipped in 1.4.0 via unfreeze PR #1215.

