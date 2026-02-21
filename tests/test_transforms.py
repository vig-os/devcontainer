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
        ).apply(tmp_path)

        assert f.read_text() == "just test\nline2"

    def test_remove_lines_transform_removes_matching_lines(self, tmp_path):
        """RemoveLines transform removes lines matching pattern."""
        transforms = _load_transforms()
        f = tmp_path / "test.txt"
        f.write_text("keep\nremove me\nkeep\n")

        transforms.RemoveLines(pattern=r"remove me").apply(tmp_path)

        assert f.read_text() == "keep\nkeep\n"
