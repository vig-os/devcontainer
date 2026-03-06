"""Tests for scripts/transforms.py — transform classes used by sync_manifest."""

from __future__ import annotations

import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir.parent))


def _load_transforms():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "transforms", scripts_dir / "transforms.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["transforms"] = module
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
