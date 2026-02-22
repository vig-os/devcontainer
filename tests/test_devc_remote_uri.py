"""Tests for scripts/devc_remote_uri.py — Cursor URI construction for remote devcontainers."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
script_path = scripts_dir / "devc_remote_uri.py"


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run devc_remote_uri.py with given args."""
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
    )


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


class TestBuildUri:
    """Test build_uri function."""

    def test_build_uri_matches_cursor_format(self):
        """Known inputs produce exact URI matching Cursor docs."""
        uri = devc_remote_uri.build_uri(
            workspace_path="/home/user/repo",
            devcontainer_path="/home/user/repo/.devcontainer/devcontainer.json",
            ssh_host="loginnode",
            container_workspace="/workspace",
        )
        expected = (
            "vscode-remote://dev-container+"
            "7b2273657474696e6754797065223a22636f6e666967222c22776f726b737061636550617468223a222f686f6d652f757365722f7265706f222c22646576636f6e7461696e657250617468223a222f686f6d652f757365722f7265706f2f2e646576636f6e7461696e65722f646576636f6e7461696e65722e6a736f6e227d"
            "@ssh-remote+loginnode/workspace"
        )
        assert uri == expected

    def test_build_uri_container_workspace_without_leading_slash(self):
        """container_workspace without leading slash is normalized."""
        uri = devc_remote_uri.build_uri(
            workspace_path="/repo",
            devcontainer_path="/repo/.devcontainer/devcontainer.json",
            ssh_host="host",
            container_workspace="workspace",
        )
        assert uri.endswith("/workspace")
        assert "@ssh-remote+host" in uri


class TestCli:
    """Test CLI interface."""

    def test_cli_prints_uri_to_stdout(self):
        """CLI with valid args prints URI to stdout."""
        result = _run_cli("/repo", "host", "/workspace")
        assert result.returncode == 0
        assert result.stdout.startswith("vscode-remote://dev-container+")
        assert "@ssh-remote+host" in result.stdout
        assert result.stderr == ""

    def test_cli_with_devcontainer_path_arg(self):
        """CLI accepts optional devcontainer path."""
        result = _run_cli(
            "/repo",
            "host",
            "/workspace",
            "--devcontainer-path",
            "/custom/devcontainer.json",
        )
        assert result.returncode == 0
        assert result.stdout.startswith("vscode-remote://dev-container+")
        assert "@ssh-remote+host" in result.stdout

    def test_cli_missing_args_exits_nonzero(self):
        """CLI with missing args exits with code 2."""
        result = _run_cli("/repo")
        assert result.returncode == 2
        assert "usage" in result.stderr.lower() or "error" in result.stderr.lower()
