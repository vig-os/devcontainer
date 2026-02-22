"""Tests for scripts/devc_remote_uri.py — Cursor URI construction for remote devcontainers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
devc_spec = importlib.util.spec_from_file_location(
    "devc_remote_uri", scripts_dir / "devc_remote_uri.py"
)
devc_remote_uri = importlib.util.module_from_spec(devc_spec)
devc_spec.loader.exec_module(devc_remote_uri)


class TestHexEncode:
    """Test hex_encode function."""

    def test_hex_encode_simple_string(self):
        """Known input produces exact hex output."""
        assert devc_remote_uri.hex_encode("a") == "61"

    def test_hex_encode_empty_string(self):
        """Empty string produces empty hex."""
        assert devc_remote_uri.hex_encode("") == ""

    def test_hex_encode_unicode(self):
        """Unicode string is UTF-8 encoded then hexed."""
        assert devc_remote_uri.hex_encode("é") == "c3a9"
