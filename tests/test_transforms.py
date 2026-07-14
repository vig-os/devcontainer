"""Tests for scripts/transforms.py — transform classes used by sync_manifest."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
project_root = scripts_dir.parent
sys.path.insert(0, str(project_root))


def _load_transforms():
    spec = importlib.util.spec_from_file_location(
        "transforms", scripts_dir / "transforms.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["transforms"] = module
    spec.loader.exec_module(module)
    return module


def _load_sync_manifest():
    spec = importlib.util.spec_from_file_location(
        "sync_manifest", scripts_dir / "sync_manifest.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["sync_manifest"] = module
    spec.loader.exec_module(module)
    return module


class TestTransformsModule:
    """Test that transforms module exists and exports transform classes."""

    def test_sed_transform_applies_regex_substitution(self, tmp_path):
        """Sed transform applies regex substitution to file content."""
        transforms = _load_transforms()
        f = tmp_path / "test.txt"
        f.write_text("just test-image\nline2")

        transforms.Sed(
            pattern=r"just test-image", replace="just test", target=""
        ).apply(f)

        assert f.read_text() == "just test\nline2"

    def test_remove_lines_transform_removes_matching_lines(self, tmp_path):
        """RemoveLines transform removes lines matching pattern."""
        transforms = _load_transforms()
        f = tmp_path / "test.txt"
        f.write_text("keep\nremove me\nkeep\n")

        transforms.RemoveLines(pattern=r"remove me").apply(f)

        assert f.read_text() == "keep\nkeep\n"


class TestWorkspaceInterpreterPath:
    """The synced workspace settings must point at the workspace venv."""

    def test_synced_settings_uses_workspace_relative_venv(self, tmp_path):
        """Syncing must leave the python interpreter workspace-relative, never /opt/venv."""
        sync_manifest = _load_sync_manifest()
        sync_manifest.sync(project_root, tmp_path)

        settings = json.loads((tmp_path / ".vscode" / "settings.json").read_text())
        interpreter = settings["python.defaultInterpreterPath"]

        assert interpreter == "${workspaceFolder}/.venv/bin/python3"
        assert "/opt/venv" not in interpreter


class TestRenovateChangelogTemplateNoMirrorLeak:
    """Synced renovate-changelog workflows must not leak the upstream-only mirror (#914).

    The devcontainer repo keeps assets/workspace/.devcontainer/CHANGELOG.md in
    lockstep with the root CHANGELOG.md, but consumers of the template have no
    assets/workspace/ tree. Under ``set -euo pipefail`` the mirror copies hard-fail
    on every consumer Renovate changelog run, so they must be stripped from the
    template while the consumer-facing logic is preserved.

    ``renovate-changelog-build.yml`` is de-coupled from the sync manifest (#996):
    the root workflow runs host+Nix via ``setup-env`` while the scaffold copy is
    the mode-aware ``resolve-toolchain`` variant, authored directly under
    ``assets/workspace/``. The no-mirror-leak guard therefore reads the committed
    scaffold file rather than a freshly-synced copy.
    """

    def test_build_workflow_drops_workspace_mirror(self):
        """The committed scaffold build.yml must not reference assets/workspace."""
        build = (
            project_root
            / "assets"
            / "workspace"
            / ".github"
            / "workflows"
            / "renovate-changelog-build.yml"
        ).read_text()

        # The upstream-only mirror tree must not leak into the consumer template.
        assert "assets/workspace" not in build
        # Consumer-facing artifact copy and metadata logic must survive.
        assert "cp CHANGELOG.md changelog-artifact/" in build
        assert "metadata.env" in build
        assert "renovate-changelog-pr" in build

    def test_commit_workflow_only_commits_consumer_changelog(self, tmp_path):
        """commit.yml FILE_PATHS must list only the consumer's own CHANGELOG.md."""
        sync_manifest = _load_sync_manifest()
        sync_manifest.sync(project_root, tmp_path)

        commit = (
            tmp_path / ".github" / "workflows" / "renovate-changelog-commit.yml"
        ).read_text()

        assert "assets/workspace" not in commit
        assert "FILE_PATHS: CHANGELOG.md\n" in commit


class TestBannerTransform:
    """The Banner transform stamps the generated provenance banner (#1036).

    Two byte-stable, version-free variants (managed vs preserved) are derived
    from ``PRESERVE_FILES``; the transform inserts them at the correct position
    for the file's comment style and is idempotent.
    """

    def test_managed_hash_inserts_two_comment_lines_at_top(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "ci.yml"
        f.write_text("# CI Workflow\non: push\n")

        transforms.Banner(preserved=False, style="hash").apply(f)

        lines = f.read_text().splitlines()
        assert lines[0] == "# " + transforms.MANAGED_BANNER[0]
        assert lines[1] == "# " + transforms.MANAGED_BANNER[1]
        assert lines[2] == ""
        assert "# CI Workflow" in lines
        assert "on: push" in f.read_text()

    def test_preserved_hash_uses_preserved_text(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "justfile.project"
        f.write_text("# PROJECT RECIPES\n")

        transforms.Banner(preserved=True, style="hash").apply(f)

        text = f.read_text()
        assert "# " + transforms.PRESERVED_BANNER[0] in text
        assert "# " + transforms.PRESERVED_BANNER[1] in text
        # The managed variant must not leak into a preserved file.
        assert transforms.MANAGED_BANNER[0] not in text

    def test_banner_carries_no_version_string(self):
        transforms = _load_transforms()
        import re

        for variant in (transforms.MANAGED_BANNER, transforms.PRESERVED_BANNER):
            for line in variant:
                assert not re.search(r"\d+\.\d+", line), (
                    f"banner must stay byte-stable across releases: {line!r}"
                )
            # A pointer to where issues go, not a policy restatement.
            assert any("github.com/vig-os/devkit/issues" in line for line in variant)

    def test_html_variant_inserts_after_front_matter(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "SKILL.md"
        f.write_text("---\nname: tdd\ndescription: x\n---\n\n# TDD\n\nbody\n")

        transforms.Banner(preserved=False, style="html").apply(f)

        lines = f.read_text().splitlines()
        # Front matter must stay first.
        assert lines[0] == "---"
        assert lines[3] == "---"
        assert lines[4] == "<!-- " + transforms.MANAGED_BANNER[0] + " -->"
        assert lines[5] == "<!-- " + transforms.MANAGED_BANNER[1] + " -->"
        assert "# TDD" in f.read_text()

    def test_html_variant_no_front_matter_goes_to_top(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "README.md"
        f.write_text("# Title\n\nbody\n")

        transforms.Banner(preserved=True, style="html").apply(f)

        lines = f.read_text().splitlines()
        assert lines[0] == "<!-- " + transforms.PRESERVED_BANNER[0] + " -->"
        assert lines[1] == "<!-- " + transforms.PRESERVED_BANNER[1] + " -->"
        assert lines[2] == ""
        assert lines[3] == "# Title"

    def test_banner_inserts_after_shebang(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "post-create.sh"
        f.write_text("#!/bin/bash\n\n# real comment\necho hi\n")

        transforms.Banner(preserved=False, style="hash").apply(f)

        lines = f.read_text().splitlines()
        assert lines[0] == "#!/bin/bash"
        assert lines[1] == "# " + transforms.MANAGED_BANNER[0]
        assert lines[2] == "# " + transforms.MANAGED_BANNER[1]
        assert "# real comment" in lines

    def test_banner_inserts_after_yaml_document_start(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "docker-compose.yml"
        f.write_text("---\nservices:\n  a: {}\n")

        transforms.Banner(preserved=True, style="hash").apply(f)

        lines = f.read_text().splitlines()
        assert lines[0] == "---"
        assert lines[1] == "# " + transforms.PRESERVED_BANNER[0]
        assert lines[2] == "# " + transforms.PRESERVED_BANNER[1]
        assert "services:" in lines

    def test_banner_is_idempotent(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "ci.yml"
        f.write_text("# CI Workflow\non: push\n")

        transforms.Banner(preserved=False, style="hash").apply(f)
        once = f.read_text()
        transforms.Banner(preserved=False, style="hash").apply(f)
        twice = f.read_text()

        assert once == twice

    def test_banner_replaces_stale_variant(self, tmp_path):
        transforms = _load_transforms()
        f = tmp_path / "ci.yml"
        f.write_text("# CI Workflow\non: push\n")

        transforms.Banner(preserved=True, style="hash").apply(f)
        transforms.Banner(preserved=False, style="hash").apply(f)

        text = f.read_text()
        assert "# " + transforms.MANAGED_BANNER[0] in text
        # The old preserved banner must be gone, not stacked.
        assert transforms.PRESERVED_BANNER[0] not in text
        assert text.count("vig-os/devkit/issues") == 1


class TestRemovePrecommitHooks:
    """Tests for RemovePrecommitHooks transform."""

    def test_preserves_section_comment_after_removed_repo(self, tmp_path):
        """Section comment preceding a kept repo must survive removal of the prior repo."""
        transforms = _load_transforms()
        f = tmp_path / ".pre-commit-config.yaml"
        f.write_text(
            "repos:\n"
            "  # Section A\n"
            "  - repo: https://example.com/a\n"
            "    rev: abc123\n"
            "    hooks:\n"
            "      - id: remove-me\n"
            "        name: remove-me\n"
            "\n"
            "  # Section B (must survive)\n"
            "  - repo: https://example.com/b\n"
            "    rev: def456\n"
            "    hooks:\n"
            "      - id: keep-me\n"
        )

        transforms.RemovePrecommitHooks(hook_ids=["remove-me"]).apply(f)

        result = f.read_text()
        assert "# Section B (must survive)" in result
        assert "keep-me" in result
        assert "# Section A" not in result
        assert "remove-me" not in result


class TestPreserveFilesSource:
    """PRESERVE_FILES (init-workspace.sh) is the banner-variant SSoT (#1036)."""

    def test_load_preserve_files_reads_the_array(self):
        sync_manifest = _load_sync_manifest()
        preserve = sync_manifest.load_preserve_files(
            project_root / "assets" / "init-workspace.sh"
        )
        assert "justfile.project" in preserve
        assert "renovate.json" in preserve
        assert ".envrc" in preserve
        assert ".typos.toml" in preserve
        # Interleaved comment lines are not mistaken for array entries.
        assert not any(entry.startswith("#") for entry in preserve)


class TestBannerApplication:
    """apply_banners walks the synced tree and stamps the right variant (#1036)."""

    def test_stamps_managed_and_preserved_variants(self, tmp_path):
        sync_manifest = _load_sync_manifest()
        transforms = _load_transforms()
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        managed = tmp_path / ".github" / "workflows" / "ci.yml"
        managed.write_text("# CI\non: push\n")
        preserved = tmp_path / "justfile.project"
        preserved.write_text("# recipes\n")

        sync_manifest.apply_banners(tmp_path, {"justfile.project"})

        assert ("# " + transforms.MANAGED_BANNER[0]) in managed.read_text()
        assert ("# " + transforms.PRESERVED_BANNER[0]) in preserved.read_text()

    def test_skips_strict_json_and_generated_configs(self, tmp_path):
        sync_manifest = _load_sync_manifest()
        renovate = tmp_path / "renovate.json"
        renovate.write_text('{\n  "x": 1\n}\n')
        (tmp_path / ".claude").mkdir()
        worktrees = tmp_path / ".claude" / "worktrees.json"
        worktrees.write_text('{\n  "y": 2\n}\n')
        precommit = tmp_path / ".pre-commit-config.yaml"
        precommit.write_text("repos: []\n")
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("# Changelog\n")

        sync_manifest.apply_banners(tmp_path, {"renovate.json"})

        assert renovate.read_text() == '{\n  "x": 1\n}\n'
        assert worktrees.read_text() == '{\n  "y": 2\n}\n'
        assert "vigOS devkit" not in precommit.read_text()
        assert "vigOS devkit" not in changelog.read_text()

    def test_skips_contradictory_justfile_local(self, tmp_path):
        sync_manifest = _load_sync_manifest()
        local = tmp_path / "justfile.local"
        local.write_text("# LOCAL RECIPES\n")

        sync_manifest.apply_banners(tmp_path, set())

        assert "vigOS devkit" not in local.read_text()

    def test_apply_banners_is_idempotent(self, tmp_path):
        sync_manifest = _load_sync_manifest()
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        wf = tmp_path / ".github" / "workflows" / "ci.yml"
        wf.write_text("# CI\non: push\n")

        sync_manifest.apply_banners(tmp_path, set())
        once = wf.read_text()
        sync_manifest.apply_banners(tmp_path, set())
        assert wf.read_text() == once

    def test_restores_a_deleted_banner(self, tmp_path):
        """A missing banner is regenerated exactly, so the hook flags the drift."""
        sync_manifest = _load_sync_manifest()
        wf = tmp_path / "scorecard.yml"
        wf.write_text("# Scorecard\non: push\n")
        sync_manifest.apply_banners(tmp_path, set())
        clean = wf.read_text()

        # Consumer deletes the banner block entirely.
        wf.write_text("# Scorecard\non: push\n")
        assert wf.read_text() != clean

        sync_manifest.apply_banners(tmp_path, set())
        assert wf.read_text() == clean

    def test_detects_a_hand_edited_banner(self, tmp_path):
        """A hand-edited banner re-emerges canonically, so re-sync differs from it."""
        sync_manifest = _load_sync_manifest()
        transforms = _load_transforms()
        wf = tmp_path / "scorecard.yml"
        wf.write_text("# Scorecard\non: push\n")
        sync_manifest.apply_banners(tmp_path, set())

        tampered = wf.read_text().replace(transforms.MANAGED_BANNER[0], "hand edited")
        wf.write_text(tampered)

        sync_manifest.apply_banners(tmp_path, set())
        result = wf.read_text()
        # The canonical banner is re-stamped at the top and the drift is visible.
        assert result != tampered
        assert result.splitlines()[0] == "# " + transforms.MANAGED_BANNER[0]
        assert result.splitlines()[1] == "# " + transforms.MANAGED_BANNER[1]


class TestSyncBannerIntegration:
    """The full sync applies banners and converges (#1036)."""

    def test_sync_stamps_banner_on_synced_assets(self, tmp_path):
        sync_manifest = _load_sync_manifest()
        transforms = _load_transforms()
        sync_manifest.sync(project_root, tmp_path)

        # .typos.toml is a preserved file (PRESERVE_FILES) -> preserved variant.
        typos = (tmp_path / ".typos.toml").read_text()
        assert ("# " + transforms.PRESERVED_BANNER[0]) in typos
        # A synced workflow is managed.
        scorecard = (tmp_path / ".github" / "workflows" / "scorecard.yml").read_text()
        assert ("# " + transforms.MANAGED_BANNER[0]) in scorecard

    def test_sync_converges_on_second_run(self, tmp_path):
        sync_manifest = _load_sync_manifest()
        sync_manifest.sync(project_root, tmp_path)
        first = {
            p.relative_to(tmp_path).as_posix(): p.read_text()
            for p in tmp_path.rglob("*")
            if p.is_file()
        }
        sync_manifest.sync(project_root, tmp_path)
        second = {
            p.relative_to(tmp_path).as_posix(): p.read_text()
            for p in tmp_path.rglob("*")
            if p.is_file()
        }
        assert first == second


class TestJustfileDevcBanner:
    """The stale justfile.devc banner is corrected to point at justfile.project (#1036)."""

    def test_devc_banner_points_at_justfile_project(self):
        transforms = _load_transforms()
        devc = (
            project_root / "assets" / "workspace" / ".devcontainer" / "justfile.devc"
        ).read_text()

        lines = devc.splitlines()
        assert lines[0] == "# " + transforms.MANAGED_BANNER[0]
        assert lines[1] == "# " + transforms.MANAGED_BANNER[1]
        assert "justfile.project" in lines[1]
        # The stale, actively-wrong banner is gone.
        assert "DEVCONTAINER RECIPES - DO NOT EDIT" not in devc
        assert "Managed by vigOS devcontainer" not in devc
