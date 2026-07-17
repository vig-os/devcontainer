"""Workflow-shape tests: the DEVKIT_WORKFLOW knob (gitflow default | trunk).

Spike #1206 (epic #1205). This is a RED/GREEN SKELETON, not the finished suite.

The locked design realizes `trunk` entirely at scaffold time (mirroring the
`DEVKIT_MODE` structural precedent): a scaffolded workspace is rewritten from the
gitflow shape (long-lived ``dev`` + ``main`` + ``sync-main-to-dev.yml``) to the
trunk shape (``main`` only). No resolve-toolchain runtime wiring, no workflow
twin — every dev reference in ``prepare-release.yml`` is a plain branch literal,
so the trunk render is an anchored ``dev -> main`` rewrite.

Production wiring does not exist yet. Until it lands the tests drive the spike's
``render_workflow_model()`` prototype (docs/spikes/1206-workflow-model/) against
a COPY of the scaffold template — the same executed-bash style as
``tests/test_ci_runner.py`` runs the real ``resolve-toolchain`` script. The two
tests that assert not-yet-built production wiring are ``xfail(strict=True)`` and
name their seam:

  * #1207 — the ``.vig-os`` manifest ships a ``DEVKIT_WORKFLOW`` key.
  * #1208 — ``init-workspace.sh`` calls ``render_workflow_model`` (+ the trunk
            ``sync-main-to-dev.yml`` copy-exclude) in its scaffold flow.

When either lands, the strict xfail flips to a failure, forcing removal of the
marker — so the suite is green today but the seams stay visible.

Refs: #1206
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

# Repository root (tests/ -> repo root).
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = REPO_ROOT / "assets" / "workspace"
WORKFLOWS = WORKSPACE / ".github" / "workflows"

# SPIKE prototype seam (#1208 replaces this with a bash function inside
# init-workspace.sh, invoked from the scaffold flow like render_codeql_matrix).
SPIKE_DIR = REPO_ROOT / "docs" / "spikes" / "1206-workflow-model"
RENDER_SCRIPT = SPIKE_DIR / "render_workflow_model.sh"


def _render(tmp_path: Path, model: str) -> Path:
    """Copy the scaffold template and run the render prototype against it.

    Returns the rendered workspace root. ``model`` is ``gitflow`` (no-op) or
    ``trunk``. Mirrors test_ci_runner.py's pattern of executing the real
    ``run:`` bash, except the seam here is the spike script, not production
    (that is #1208).
    """
    dest = tmp_path / model
    shutil.copytree(WORKSPACE, dest)
    subprocess.run(
        ["bash", str(RENDER_SCRIPT), str(dest), model],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest


def _wf(rendered: Path, name: str) -> str:
    return (rendered / ".github" / "workflows" / name).read_text(encoding="utf-8")


# ── gitflow no-op guard ──────────────────────────────────────────────────────


def test_gitflow_render_is_byte_identical(tmp_path: Path) -> None:
    """gitflow is the default: rendering must change zero bytes vs the template."""
    rendered = _render(tmp_path, "gitflow")
    diff = subprocess.run(
        ["diff", "-r", str(WORKSPACE), str(rendered)],
        capture_output=True,
        text=True,
    )
    assert diff.returncode == 0, f"gitflow render changed bytes:\n{diff.stdout}"


# ── trunk shape ──────────────────────────────────────────────────────────────


def test_trunk_removes_sync_main_to_dev(tmp_path: Path) -> None:
    """A trunk workspace has no sync-main-to-dev.yml (copy-exclude in prod)."""
    rendered = _render(tmp_path, "trunk")
    assert not (rendered / ".github" / "workflows" / "sync-main-to-dev.yml").exists()


def test_trunk_prepare_release_forks_from_main(tmp_path: Path) -> None:
    """prepare-release retargets its release base dev -> main, zero heads/dev."""
    text = _wf(_render(tmp_path, "trunk"), "prepare-release.yml")
    assert "heads/dev" not in text
    assert "refs/heads/main" in text
    assert text.count("\n          ref: main\n") == 2  # both checkout jobs
    assert "Create release branch from main" in text


def test_trunk_ci_pr_filter_excludes_dev(tmp_path: Path) -> None:
    """ci.yml drops `- dev` from the PR branch filter; commit-gate TRUNK=main."""
    text = _wf(_render(tmp_path, "trunk"), "ci.yml")
    assert "\n      - dev\n" not in text
    assert 'TRUNK="main"' in text
    assert 'TRUNK="dev"' not in text


def test_trunk_codeql_pr_filter_excludes_dev(tmp_path: Path) -> None:
    """codeql.yml drops `- dev` from the PR filter; the main leg survives."""
    text = _wf(_render(tmp_path, "trunk"), "codeql.yml")
    assert "\n      - dev\n" not in text
    assert "\n      - main\n" in text


def test_trunk_sync_issues_default_main(tmp_path: Path) -> None:
    """sync-issues default target-branch dev -> main; no `|| 'dev'` fallback."""
    text = _wf(_render(tmp_path, "trunk"), "sync-issues.yml")
    assert "default: 'main'" in text
    assert "|| 'dev'" not in text
    assert "|| 'main'" in text


def test_trunk_skill_base_branch_main(tmp_path: Path) -> None:
    """branch-naming SKILL base default dev -> main; example branch untouched."""
    rendered = _render(tmp_path, "trunk")
    text = (rendered / ".claude" / "skills" / "branch-naming" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "fall back to `main`" in text
    assert "use `main` as" in text
    # The `chore/sync-main-to-dev` illustration is a branch NAME, not a base
    # default — anchoring must leave it intact.
    assert "chore/sync-main-to-dev" in text


def test_trunk_precommit_drops_dev_clause(tmp_path: Path) -> None:
    """.pre-commit-config drops the `(?!dev$)` protect-clause; main stays."""
    rendered = _render(tmp_path, "trunk")
    text = (rendered / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "(?!dev$)" not in text
    assert "(?!main$)" in text


def test_anchoring_preserves_dev_prefixed_and_device_tokens(tmp_path: Path) -> None:
    """Anchoring must not touch /dev/null, dev_sha, or development/devkit tokens.

    The render's word-boundary/end anchors exist precisely so these behaviorally
    or lexically dev-adjacent tokens survive. /dev/null in particular would be a
    catastrophic corruption if rewritten.
    """
    text = _wf(_render(tmp_path, "trunk"), "prepare-release.yml")
    assert "/dev/null" in text  # device path, not a branch ref
    assert "dev_sha:" in text  # workflow output variable name preserved


# ── production wiring seams (RED until the follow-up sub-issues land) ─────────


@pytest.mark.xfail(strict=True, reason="awaits #1207: DEVKIT_WORKFLOW manifest key")
def test_vig_os_declares_workflow_key() -> None:
    """#1207 seam: the scaffold manifest ships the opt-in key (default gitflow).

    Mirrors test_ci_runner.py::test_vig_os_declares_ci_runner_key. Fails today
    (key absent); flips to xpass -> strict failure when #1207 adds it.
    """
    text = (WORKSPACE / ".vig-os").read_text(encoding="utf-8")
    assert "DEVKIT_WORKFLOW=" in text


@pytest.mark.xfail(
    strict=True, reason="awaits #1208: render wiring in init-workspace.sh"
)
def test_init_workspace_invokes_render_workflow_model() -> None:
    """#1208 seam: init-workspace.sh calls render_workflow_model in scaffold flow.

    Today the logic lives only in the spike prototype
    (docs/spikes/1206-workflow-model/render_workflow_model.sh). When #1208 ports
    it into init-workspace.sh (sibling to render_codeql_matrix) and invokes it
    after the rsync copy, this passes and the strict marker must be removed.
    """
    init = (REPO_ROOT / "assets" / "init-workspace.sh").read_text(encoding="utf-8")
    assert "render_workflow_model" in init
